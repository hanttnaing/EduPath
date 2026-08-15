from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# EduPath - Step 152.7C-0A
# Source-of-Truth Integration Audit
#
# IMPORTANT:
# - READ ONLY
# - Does NOT modify MongoDB
# - Does NOT modify cleaned datasets
# - Does NOT modify staging datasets
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"

BASELINE_DIR = (
    PROJECT_ROOT
    / "backups"
    / "baseline_151_10"
)

STAGING_DIR = PROJECT_ROOT / "data" / "staging"

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"

REPORT_FILE = (
    ANALYSIS_DIR
    / "152_7c0_source_of_truth_audit.json"
)

VALIDATOR_FILE = (
    PROJECT_ROOT
    / "analysis_layer"
    / "validate_scholarship_batch_01.py"
)


DATASETS = {
    "countries": {
        "file": "countries.json",
        "id_field": "country_id",
    },
    "universities": {
        "file": "universities.json",
        "id_field": "university_id",
    },
    "programs": {
        "file": "programs.json",
        "id_field": "program_id",
    },
    "scholarships": {
        "file": "scholarships.json",
        "id_field": "scholarship_id",
    },
    "user_profiles": {
        "file": "user_profiles.json",
        "id_field": "user_id",
    },
}


SOURCE_PLAN_FILE = (
    STAGING_DIR
    / "152_7b_scholarship_source_collection.csv"
)

BATCH_01_FILE = (
    STAGING_DIR
    / "152_7c_batch_01_verified.csv"
)


def load_json_list(path: Path) -> list:
    """
    Load a JSON dataset expected to contain a list.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected JSON list: {path}"
        )

    return data


def load_csv_rows(path: Path) -> tuple[list[str], list[dict]]:
    """
    Read CSV header and rows.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames or []

        rows = list(reader)

    return fieldnames, rows


def compare_dataset(
    dataset_name: str,
    filename: str,
    id_field: str,
) -> dict:
    """
    Compare data/cleaned against Step 151.10 MongoDB baseline backup.
    """

    cleaned_path = CLEANED_DIR / filename
    baseline_path = BASELINE_DIR / filename

    cleaned_data = load_json_list(cleaned_path)
    baseline_data = load_json_list(baseline_path)

    cleaned_ids = {
        str(record.get(id_field)).strip()
        for record in cleaned_data
        if record.get(id_field)
    }

    baseline_ids = {
        str(record.get(id_field)).strip()
        for record in baseline_data
        if record.get(id_field)
    }

    missing_from_cleaned = sorted(
        baseline_ids - cleaned_ids
    )

    extra_in_cleaned = sorted(
        cleaned_ids - baseline_ids
    )

    same_ids = (
        cleaned_ids == baseline_ids
    )

    same_count = (
        len(cleaned_data)
        == len(baseline_data)
    )

    status = (
        "MATCH"
        if same_ids and same_count
        else "DRIFT"
    )

    return {
        "dataset": dataset_name,
        "id_field": id_field,

        "cleaned_count": len(cleaned_data),
        "baseline_count": len(baseline_data),

        "same_count": same_count,
        "same_ids": same_ids,

        "missing_from_cleaned": (
            missing_from_cleaned
        ),

        "extra_in_cleaned": (
            extra_in_cleaned
        ),

        "status": status,
    }


def inspect_source_plan() -> dict:
    """
    Inspect the Step 152.7B scholarship expansion plan.
    """

    fieldnames, rows = load_csv_rows(
        SOURCE_PLAN_FILE
    )

    country_counts = Counter(
        (
            row.get("target_country_name")
            or "<MISSING>"
        ).strip()
        for row in rows
    )

    slots = [
        (
            row.get("collection_slot")
            or ""
        ).strip()
        for row in rows
    ]

    duplicate_slots = sorted(
        slot
        for slot, count
        in Counter(slots).items()
        if slot and count > 1
    )

    status_counts = Counter(
        (
            row.get("collection_status")
            or "<EMPTY>"
        ).strip()
        for row in rows
    )

    verification_counts = Counter(
        (
            row.get("verification_status")
            or "<EMPTY>"
        ).strip()
        for row in rows
    )

    return {
        "file": str(SOURCE_PLAN_FILE),
        "column_count": len(fieldnames),
        "record_count": len(rows),
        "country_distribution": dict(
            sorted(country_counts.items())
        ),
        "collection_status_distribution": dict(
            sorted(status_counts.items())
        ),
        "verification_status_distribution": dict(
            sorted(
                verification_counts.items()
            )
        ),
        "duplicate_slots": duplicate_slots,
    }


def inspect_batch_01() -> dict:
    """
    Inspect the current Step 152.7C Batch 01 staging file.
    """

    fieldnames, rows = load_csv_rows(
        BATCH_01_FILE
    )

    country_counts = Counter(
        (
            row.get("target_country_name")
            or "<MISSING>"
        ).strip()
        for row in rows
    )

    collection_counts = Counter(
        (
            row.get("collection_status")
            or "<EMPTY>"
        ).strip()
        for row in rows
    )

    verification_counts = Counter(
        (
            row.get("verification_status")
            or "<EMPTY>"
        ).strip()
        for row in rows
    )

    scholarship_names_present = sum(
        1
        for row in rows
        if (
            row.get("scholarship_name")
            or ""
        ).strip()
    )

    official_urls_present = sum(
        1
        for row in rows
        if (
            row.get("official_source_url")
            or ""
        ).strip()
    )

    return {
        "file": str(BATCH_01_FILE),
        "column_count": len(fieldnames),
        "record_count": len(rows),

        "country_distribution": dict(
            sorted(country_counts.items())
        ),

        "collection_status_distribution": dict(
            sorted(collection_counts.items())
        ),

        "verification_status_distribution": dict(
            sorted(
                verification_counts.items()
            )
        ),

        "scholarship_names_present": (
            scholarship_names_present
        ),

        "official_source_urls_present": (
            official_urls_present
        ),

        "appears_to_be_placeholder_file": (
            scholarship_names_present == 0
            or official_urls_present == 0
        ),
    }


def detect_validator_expected_count() -> int | None:
    """
    Detect the record count expected by
    validate_scholarship_batch_01.py.

    Example:
        if len(rows) != 6:
    """

    if not VALIDATOR_FILE.exists():
        return None

    text = VALIDATOR_FILE.read_text(
        encoding="utf-8"
    )

    pattern = r"len\s*\(\s*rows\s*\)\s*!=\s*(\d+)"

    match = re.search(
        pattern,
        text,
    )

    if not match:
        return None

    return int(
        match.group(1)
    )


def build_recommendations(
    dataset_results: list[dict],
    source_plan: dict,
    batch_01: dict,
    validator_expected: int | None,
) -> list[str]:

    recommendations = []

    drifted = [
        result
        for result in dataset_results
        if result["status"] == "DRIFT"
    ]

    if drifted:
        names = ", ".join(
            result["dataset"]
            for result in drifted
        )

        recommendations.append(
            "Cleaned datasets and Step 151.10 baseline "
            f"are not fully synchronised: {names}."
        )

    if (
        validator_expected is not None
        and batch_01["record_count"]
        != validator_expected
    ):
        recommendations.append(
            "Batch 01 staging row count does not match "
            "the validator expectation. Do not change "
            "the validator or staging file until the "
            "intended batching strategy is confirmed."
        )

    if batch_01[
        "appears_to_be_placeholder_file"
    ]:
        recommendations.append(
            "152_7c_batch_01_verified.csv is not yet "
            "a genuinely verified scholarship dataset. "
            "It still needs official-source research "
            "before validation/import."
        )

    if (
        source_plan["record_count"]
        == 18
    ):
        recommendations.append(
            "Keep the 18-row Step 152.7B source plan "
            "as the master expansion inventory. "
            "Create verified batches from these slots "
            "rather than replacing the plan."
        )

    recommendations.append(
        "No MongoDB write should occur during "
        "Step 152.7C-0A."
    )

    return recommendations


def print_dataset_table(
    dataset_results: list[dict],
) -> None:

    print()
    print("=" * 90)
    print("CLEANED DATA vs STEP 151.10 BASELINE")
    print("=" * 90)

    print(
        f"{'Dataset':<18}"
        f"{'Cleaned':>10}"
        f"{'Baseline':>12}"
        f"{'Status':>12}"
    )

    print("-" * 90)

    for result in dataset_results:

        print(
            f"{result['dataset']:<18}"
            f"{result['cleaned_count']:>10}"
            f"{result['baseline_count']:>12}"
            f"{result['status']:>12}"
        )

        if result["missing_from_cleaned"]:
            print(
                "   Missing from cleaned: "
                + ", ".join(
                    result[
                        "missing_from_cleaned"
                    ]
                )
            )

        if result["extra_in_cleaned"]:
            print(
                "   Extra in cleaned: "
                + ", ".join(
                    result[
                        "extra_in_cleaned"
                    ]
                )
            )


def main() -> None:

    print("=" * 90)
    print(
        "EduPath - Step 152.7C-0A "
        "Source-of-Truth Integration Audit"
    )
    print("=" * 90)

    print()
    print(f"Project root : {PROJECT_ROOT}")
    print(
        "Mode         : READ ONLY "
        "(no MongoDB/data modification)"
    )

    dataset_results = []

    for dataset_name, config in DATASETS.items():

        result = compare_dataset(
            dataset_name=dataset_name,
            filename=config["file"],
            id_field=config["id_field"],
        )

        dataset_results.append(result)

    print_dataset_table(
        dataset_results
    )

    source_plan = inspect_source_plan()
    batch_01 = inspect_batch_01()

    validator_expected = (
        detect_validator_expected_count()
    )

    print()
    print("=" * 90)
    print("STEP 152.7B SOURCE PLAN")
    print("=" * 90)

    print(
        f"Records             : "
        f"{source_plan['record_count']}"
    )

    print(
        f"Columns             : "
        f"{source_plan['column_count']}"
    )

    print(
        "Country distribution:"
    )

    for country, count in (
        source_plan[
            "country_distribution"
        ].items()
    ):
        print(
            f"  {country:<20} {count}"
        )

    print()
    print("=" * 90)
    print("STEP 152.7C BATCH 01")
    print("=" * 90)

    print(
        f"Records             : "
        f"{batch_01['record_count']}"
    )

    print(
        f"Columns             : "
        f"{batch_01['column_count']}"
    )

    print(
        f"Scholarship names   : "
        f"{batch_01['scholarship_names_present']}"
    )

    print(
        f"Official URLs       : "
        f"{batch_01['official_source_urls_present']}"
    )

    print(
        f"Placeholder state   : "
        f"{batch_01['appears_to_be_placeholder_file']}"
    )

    print()
    print(
        "Validator expected records : "
        f"{validator_expected}"
    )

    batch_alignment = (
        "MATCH"
        if (
            validator_expected is not None
            and batch_01["record_count"]
            == validator_expected
        )
        else "MISMATCH"
    )

    print(
        "Batch / validator alignment: "
        f"{batch_alignment}"
    )

    recommendations = (
        build_recommendations(
            dataset_results,
            source_plan,
            batch_01,
            validator_expected,
        )
    )

    report = {
        "project": "EduPath Analytics",

        "step": "152.7C-0A",

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "mode": "READ_ONLY",

        "mongodb_modified": False,

        "dataset_comparison": (
            dataset_results
        ),

        "scholarship_source_plan": (
            source_plan
        ),

        "scholarship_batch_01": (
            batch_01
        ),

        "validator": {
            "file": str(
                VALIDATOR_FILE
            ),

            "expected_records": (
                validator_expected
            ),

            "current_batch_records": (
                batch_01["record_count"]
            ),

            "status": batch_alignment,
        },

        "recommendations": recommendations,
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
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 90)
    print("AUDIT RECOMMENDATIONS")
    print("=" * 90)

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        print(
            f"{index}. {recommendation}"
        )

    drift_count = sum(
        1
        for result in dataset_results
        if result["status"] == "DRIFT"
    )

    print()
    print("=" * 90)
    print("STEP 152.7C-0A AUDIT: COMPLETED")
    print("=" * 90)

    print(
        f"Datasets with drift : "
        f"{drift_count}"
    )

    print(
        f"Batch alignment     : "
        f"{batch_alignment}"
    )

    print(
        f"MongoDB modified    : NO"
    )

    print()
    print(
        f"JSON report:\n"
        f"{REPORT_FILE}"
    )


if __name__ == "__main__":
    main()