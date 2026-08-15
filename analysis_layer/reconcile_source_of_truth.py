from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# EduPath - Step 152.7C-0B
# Baseline Reconciliation & Batch Strategy Lock
#
# PURPOSE
# ------------------------------------------------------------
# 1. Restore missing Step 151.10 baseline records into
#    data/cleaned without deleting newer records.
#
# 2. Preserve the 18-row scholarship source plan.
#
# 3. Split the 18 scholarship slots into three batches:
#       Batch 01 = 6
#       Batch 02 = 6
#       Batch 03 = 6
#
# 4. Keep one scholarship slot per target country per batch.
#
# 5. Create backups BEFORE changing any existing file.
#
# 6. MongoDB is NEVER modified by this script.
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
STAGING_DIR = PROJECT_ROOT / "data" / "staging"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"

BASELINE_DIR = (
    PROJECT_ROOT
    / "backups"
    / "baseline_151_10"
)

SOURCE_PLAN_FILE = (
    STAGING_DIR
    / "152_7b_scholarship_source_collection.csv"
)

CURRENT_BATCH_01_FILE = (
    STAGING_DIR
    / "152_7c_batch_01_verified.csv"
)

BATCH_02_FILE = (
    STAGING_DIR
    / "152_7c_batch_02_pending.csv"
)

BATCH_03_FILE = (
    STAGING_DIR
    / "152_7c_batch_03_pending.csv"
)

REPORT_FILE = (
    ANALYSIS_DIR
    / "152_7c0b_reconciliation_report.json"
)


DATASETS_TO_RECONCILE = {
    "countries": {
        "filename": "countries.json",
        "id_field": "country_id",
    },
    "user_profiles": {
        "filename": "user_profiles.json",
        "id_field": "user_id",
    },
}


EXPECTED_COUNTRIES = [
    "Hong Kong",
    "Malaysia",
    "Singapore",
    "South Korea",
    "Taiwan",
    "Thailand",
]

EXPECTED_TOTAL_SLOTS = 18
EXPECTED_COUNTRIES_PER_BATCH = 6
EXPECTED_BATCH_COUNT = 3


def load_json_list(path: Path) -> list[dict]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required JSON file not found:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected JSON list:\n{path}"
        )

    return data


def write_json_list(
    path: Path,
    data: list[dict],
) -> None:

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )


def load_csv(
    path: Path,
) -> tuple[list[str], list[dict]]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required CSV file not found:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames or []

        rows = list(reader)

    if not fieldnames:
        raise ValueError(
            f"CSV header missing:\n{path}"
        )

    return fieldnames, rows


def write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(rows)


def create_backup_directory() -> Path:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_dir = (
        PROJECT_ROOT
        / "backups"
        / f"pre_152_7c0b_{timestamp}"
    )

    backup_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    return backup_dir


def backup_file(
    source: Path,
    backup_dir: Path,
) -> None:

    if not source.exists():
        return

    target = backup_dir / source.name

    shutil.copy2(
        source,
        target,
    )


def analyse_reconciliation(
    dataset_name: str,
    filename: str,
    id_field: str,
) -> dict:

    cleaned_path = (
        CLEANED_DIR / filename
    )

    baseline_path = (
        BASELINE_DIR / filename
    )

    cleaned = load_json_list(
        cleaned_path
    )

    baseline = load_json_list(
        baseline_path
    )

    cleaned_ids = {
        str(record.get(id_field)).strip()
        for record in cleaned
        if record.get(id_field)
    }

    baseline_ids = {
        str(record.get(id_field)).strip()
        for record in baseline
        if record.get(id_field)
    }

    missing_ids = (
        baseline_ids - cleaned_ids
    )

    extra_ids = (
        cleaned_ids - baseline_ids
    )

    records_to_restore = [
        record
        for record in baseline
        if str(
            record.get(id_field)
        ).strip() in missing_ids
    ]

    return {
        "dataset": dataset_name,
        "filename": filename,
        "id_field": id_field,

        "cleaned_path": cleaned_path,
        "baseline_path": baseline_path,

        "cleaned_data": cleaned,
        "baseline_data": baseline,

        "cleaned_count_before": len(cleaned),
        "baseline_count": len(baseline),

        "missing_ids": sorted(
            missing_ids
        ),

        "extra_ids": sorted(
            extra_ids
        ),

        "records_to_restore": (
            records_to_restore
        ),

        "restore_count": len(
            records_to_restore
        ),
    }


def apply_reconciliation(
    result: dict,
) -> list[dict]:

    cleaned_data = list(
        result["cleaned_data"]
    )

    cleaned_data.extend(
        result["records_to_restore"]
    )

    return cleaned_data


def validate_master_plan(
    fieldnames: list[str],
    rows: list[dict],
) -> None:

    if len(rows) != EXPECTED_TOTAL_SLOTS:
        raise ValueError(
            "Step 152.7B master plan must contain "
            f"{EXPECTED_TOTAL_SLOTS} rows, "
            f"but found {len(rows)}."
        )

    required_columns = {
        "collection_slot",
        "target_country_id",
        "target_country_name",
        "collection_status",
        "verification_status",
    }

    missing_columns = (
        required_columns
        - set(fieldnames)
    )

    if missing_columns:
        raise ValueError(
            "Master plan is missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    grouped = defaultdict(list)

    for row in rows:

        country = (
            row.get(
                "target_country_name"
            )
            or ""
        ).strip()

        grouped[country].append(row)

    actual_countries = set(
        grouped.keys()
    )

    expected_countries = set(
        EXPECTED_COUNTRIES
    )

    if actual_countries != expected_countries:

        raise ValueError(
            "Unexpected target-country distribution.\n"
            f"Expected: {sorted(expected_countries)}\n"
            f"Found   : {sorted(actual_countries)}"
        )

    for country in EXPECTED_COUNTRIES:

        count = len(
            grouped[country]
        )

        if count != 3:
            raise ValueError(
                f"{country} must have exactly "
                f"3 collection slots. "
                f"Found {count}."
            )


def build_balanced_batches(
    rows: list[dict],
) -> list[list[dict]]:

    grouped = defaultdict(list)

    for row in rows:

        country = (
            row.get(
                "target_country_name"
            )
            or ""
        ).strip()

        grouped[country].append(row)

    # Preserve original order within
    # each country's three collection slots.
    batches = []

    for batch_index in range(
        EXPECTED_BATCH_COUNT
    ):

        batch = []

        for country in EXPECTED_COUNTRIES:

            country_rows = grouped[
                country
            ]

            batch.append(
                dict(
                    country_rows[
                        batch_index
                    ]
                )
            )

        batches.append(batch)

    return batches


def batch_summary(
    batch: list[dict],
) -> dict:

    return {
        "record_count": len(batch),

        "slots": [
            (
                row.get("collection_slot")
                or ""
            ).strip()
            for row in batch
        ],

        "countries": [
            (
                row.get(
                    "target_country_name"
                )
                or ""
            ).strip()
            for row in batch
        ],

        "collection_statuses": [
            (
                row.get(
                    "collection_status"
                )
                or ""
            ).strip()
            for row in batch
        ],

        "verification_statuses": [
            (
                row.get(
                    "verification_status"
                )
                or ""
            ).strip()
            for row in batch
        ],
    }


def print_reconciliation_plan(
    reconciliation_results: list[dict],
) -> None:

    print()
    print("=" * 88)
    print("DATASET RECONCILIATION PLAN")
    print("=" * 88)

    for result in reconciliation_results:

        print()
        print(
            f"{result['dataset']}"
        )

        print(
            f"  Cleaned count     : "
            f"{result['cleaned_count_before']}"
        )

        print(
            f"  Baseline count    : "
            f"{result['baseline_count']}"
        )

        print(
            f"  Records to restore: "
            f"{result['restore_count']}"
        )

        if result["missing_ids"]:

            print(
                "  Missing IDs       : "
                + ", ".join(
                    result["missing_ids"]
                )
            )

        if result["extra_ids"]:

            print(
                "  Extra cleaned IDs : "
                + ", ".join(
                    result["extra_ids"]
                )
            )


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "EduPath Step 152.7C-0B "
            "source-of-truth reconciliation."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Apply reconciliation and batch split. "
            "Without this flag, the script performs "
            "a dry run only."
        ),
    )

    args = parser.parse_args()

    print("=" * 88)
    print(
        "EduPath - Step 152.7C-0B "
        "Baseline Reconciliation & Batch Strategy Lock"
    )
    print("=" * 88)

    print()
    print(
        f"Project root : {PROJECT_ROOT}"
    )

    print(
        "Mode         : "
        + (
            "APPLY"
            if args.apply
            else "DRY RUN"
        )
    )

    print(
        "MongoDB      : WILL NOT BE MODIFIED"
    )

    reconciliation_results = []

    for (
        dataset_name,
        config,
    ) in DATASETS_TO_RECONCILE.items():

        result = analyse_reconciliation(
            dataset_name=dataset_name,
            filename=config["filename"],
            id_field=config["id_field"],
        )

        reconciliation_results.append(
            result
        )

    print_reconciliation_plan(
        reconciliation_results
    )

    fieldnames, source_rows = (
        load_csv(
            SOURCE_PLAN_FILE
        )
    )

    validate_master_plan(
        fieldnames,
        source_rows,
    )

    batches = build_balanced_batches(
        source_rows
    )

    print()
    print("=" * 88)
    print("SCHOLARSHIP BATCH STRATEGY")
    print("=" * 88)

    print()
    print(
        f"Master plan records : "
        f"{len(source_rows)}"
    )

    for index, batch in enumerate(
        batches,
        start=1,
    ):

        print()
        print(
            f"Batch {index:02d}"
        )

        print(
            f"  Records : {len(batch)}"
        )

        for row in batch:

            slot = (
                row.get(
                    "collection_slot"
                )
                or ""
            ).strip()

            country = (
                row.get(
                    "target_country_name"
                )
                or ""
            ).strip()

            print(
                f"  {slot:<14} "
                f"{country}"
            )

    # --------------------------------------------------------
    # DRY RUN
    # --------------------------------------------------------

    if not args.apply:

        print()
        print("=" * 88)
        print(
            "STEP 152.7C-0B DRY RUN: PASS"
        )
        print("=" * 88)

        print()
        print(
            "No files were modified."
        )

        print(
            "No MongoDB records were modified."
        )

        print()
        print(
            "If the reconciliation plan above "
            "looks correct, run:"
        )

        print()
        print(
            r".\.venv\Scripts\python.exe "
            r".\analysis_layer\reconcile_source_of_truth.py "
            r"--apply"
        )

        return

    # --------------------------------------------------------
    # APPLY MODE
    # --------------------------------------------------------

    backup_dir = (
        create_backup_directory()
    )

    print()
    print("=" * 88)
    print("CREATING SAFETY BACKUP")
    print("=" * 88)

    print(
        f"Backup directory:\n{backup_dir}"
    )

    for result in reconciliation_results:

        backup_file(
            result["cleaned_path"],
            backup_dir,
        )

    backup_file(
        CURRENT_BATCH_01_FILE,
        backup_dir,
    )

    if BATCH_02_FILE.exists():
        backup_file(
            BATCH_02_FILE,
            backup_dir,
        )

    if BATCH_03_FILE.exists():
        backup_file(
            BATCH_03_FILE,
            backup_dir,
        )

    backup_file(
        SOURCE_PLAN_FILE,
        backup_dir,
    )

    print()
    print("=" * 88)
    print("RECONCILING CLEANED DATA")
    print("=" * 88)

    applied_reconciliations = []

    for result in reconciliation_results:

        merged_data = (
            apply_reconciliation(
                result
            )
        )

        write_json_list(
            result["cleaned_path"],
            merged_data,
        )

        print(
            f"{result['dataset']}: "
            f"{result['cleaned_count_before']} "
            f"→ {len(merged_data)}"
        )

        applied_reconciliations.append(
            {
                "dataset": (
                    result["dataset"]
                ),

                "count_before": (
                    result[
                        "cleaned_count_before"
                    ]
                ),

                "count_after": len(
                    merged_data
                ),

                "restored_ids": (
                    result[
                        "missing_ids"
                    ]
                ),
            }
        )

    print()
    print("=" * 88)
    print("WRITING 6-RECORD BATCHES")
    print("=" * 88)

    batch_01 = batches[0]
    batch_02 = batches[1]
    batch_03 = batches[2]

    # IMPORTANT:
    # Existing 18-row fake "verified" file has already
    # been backed up. It is now replaced with ONLY the
    # six Batch-01 slots expected by the validator.
    #
    # The values remain NOT_COLLECTED / NOT_VERIFIED.
    # Research happens in the NEXT step.
    write_csv(
        CURRENT_BATCH_01_FILE,
        fieldnames,
        batch_01,
    )

    write_csv(
        BATCH_02_FILE,
        fieldnames,
        batch_02,
    )

    write_csv(
        BATCH_03_FILE,
        fieldnames,
        batch_03,
    )

    print(
        f"Batch 01 → "
        f"{CURRENT_BATCH_01_FILE}"
    )

    print(
        f"Batch 02 → "
        f"{BATCH_02_FILE}"
    )

    print(
        f"Batch 03 → "
        f"{BATCH_03_FILE}"
    )

    report = {
        "project": "EduPath Analytics",

        "step": "152.7C-0B",

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "mode": "APPLY",

        "mongodb_modified": False,

        "baseline_source": str(
            BASELINE_DIR
        ),

        "master_source_plan": str(
            SOURCE_PLAN_FILE
        ),

        "backup_directory": str(
            backup_dir
        ),

        "dataset_reconciliation": (
            applied_reconciliations
        ),

        "scholarship_batch_strategy": {
            "master_slots": len(
                source_rows
            ),

            "batch_count": 3,

            "records_per_batch": 6,

            "batch_01": batch_summary(
                batch_01
            ),

            "batch_02": batch_summary(
                batch_02
            ),

            "batch_03": batch_summary(
                batch_03
            ),
        },

        "next_step": (
            "Step 152.7C-1 Research-Assisted "
            "Scholarship Batch 01 Collection"
        ),
    }

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    print()
    print("=" * 88)
    print(
        "STEP 152.7C-0B: COMPLETED"
    )
    print("=" * 88)

    print()
    print(
        "Countries cleaned dataset "
        "has been reconciled safely."
    )

    print(
        "User profiles cleaned dataset "
        "has been reconciled safely."
    )

    print(
        "18 scholarship slots remain intact."
    )

    print(
        "Batch strategy is now 6 + 6 + 6."
    )

    print(
        "MongoDB modified: NO"
    )

    print()
    print(
        f"Report:\n{REPORT_FILE}"
    )

    print()
    print(
        "NEXT:"
    )

    print(
        "Run source_of_truth_audit.py again "
        "to confirm zero dataset drift and "
        "6-row Batch 01 alignment."
    )


if __name__ == "__main__":
    main()