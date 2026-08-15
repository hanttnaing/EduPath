from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from datetime import datetime


# ============================================================
# EduPath - Step 152.7C-3
# Scholarship ID Mapping & Pre-Import Package
#
# IMPORTANT:
# - READS existing Step 151.10 baseline
# - READS verified Batch 01
# - DOES NOT modify MongoDB
# - DOES NOT modify baseline JSON
# - Produces new pre-import files only
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BASELINE_DIR = PROJECT_ROOT / "backups" / "baseline_151_10"
STAGING_DIR = PROJECT_ROOT / "data" / "staging"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"

BASELINE_SCHOLARSHIPS = BASELINE_DIR / "scholarships.json"
BASELINE_COUNTRIES = BASELINE_DIR / "countries.json"

VERIFIED_BATCH = STAGING_DIR / "152_7c_batch_01_verified.csv"

OUTPUT_CSV = STAGING_DIR / "152_7c_batch_01_preimport.csv"
OUTPUT_JSON = ANALYSIS_DIR / "152_7c_batch_01_preimport.json"
REPORT_JSON = ANALYSIS_DIR / "152_7c3_preimport_report.json"


EXPECTED_BATCH_SIZE = 6


COUNTRY_PREFIX_MAP = {
    "country_hk": "hk",
    "country_my": "my",
    "country_sg": "sg",
    "country_kr": "kr",
    "country_tw": "tw",
    "country_th": "th",
    "country_jp": "jp",
}


def load_json_records(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Required JSON file not found: {path}")

    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("items", "records", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]

    raise ValueError(
        f"Could not detect record list inside JSON file: {path}"
    )


def load_csv_records(path: Path) -> tuple[list[dict], list[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required CSV file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError(f"CSV header could not be detected: {path}")

        rows = list(reader)
        return rows, list(reader.fieldnames)


def normalise_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalise_name(value) -> str:
    return re.sub(
        r"\s+",
        " ",
        normalise_text(value).lower()
    )


def extract_country_prefix(country_id: str) -> str:
    country_id = normalise_text(country_id)

    if country_id in COUNTRY_PREFIX_MAP:
        return COUNTRY_PREFIX_MAP[country_id]

    if country_id.startswith("country_"):
        suffix = country_id.replace("country_", "", 1).strip()

        if suffix:
            return suffix

    raise ValueError(
        f"Cannot derive scholarship ID prefix from country_id={country_id!r}"
    )


def scholarship_number_for_prefix(
    scholarship_id: str,
    prefix: str,
) -> int | None:

    pattern = rf"^sch_{re.escape(prefix)}_(\d+)$"

    match = re.match(
        pattern,
        normalise_text(scholarship_id),
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return int(match.group(1))


def get_next_number(
    prefix: str,
    existing_ids: set[str],
    newly_assigned_ids: set[str],
) -> int:

    highest = 0

    for scholarship_id in existing_ids | newly_assigned_ids:

        number = scholarship_number_for_prefix(
            scholarship_id,
            prefix,
        )

        if number is not None:
            highest = max(highest, number)

    return highest + 1


def make_new_scholarship_id(
    country_id: str,
    existing_ids: set[str],
    newly_assigned_ids: set[str],
) -> str:

    prefix = extract_country_prefix(country_id)

    next_number = get_next_number(
        prefix,
        existing_ids,
        newly_assigned_ids,
    )

    new_id = f"sch_{prefix}_{next_number:03d}"

    while (
        new_id in existing_ids
        or new_id in newly_assigned_ids
    ):
        next_number += 1
        new_id = f"sch_{prefix}_{next_number:03d}"

    return new_id


def write_csv(
    path: Path,
    rows: list[dict],
    fieldnames: list[str],
) -> None:

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )


def main() -> None:

    print("=" * 88)
    print(
        "EduPath - Step 152.7C-3 "
        "Scholarship ID Mapping & Pre-Import Package"
    )
    print("=" * 88)

    print()
    print(f"Project root       : {PROJECT_ROOT}")
    print(f"Baseline           : {BASELINE_SCHOLARSHIPS}")
    print(f"Verified batch     : {VERIFIED_BATCH}")
    print("MongoDB modification: NO")
    print()

    # --------------------------------------------------------
    # Load source-of-truth datasets
    # --------------------------------------------------------

    baseline_scholarships = load_json_records(
        BASELINE_SCHOLARSHIPS
    )

    countries = load_json_records(
        BASELINE_COUNTRIES
    )

    batch_rows, batch_fields = load_csv_records(
        VERIFIED_BATCH
    )

    print("=" * 88)
    print("SOURCE DATA COUNTS")
    print("=" * 88)

    print(
        f"Existing scholarships : "
        f"{len(baseline_scholarships)}"
    )

    print(
        f"Countries             : "
        f"{len(countries)}"
    )

    print(
        f"Verified Batch 01     : "
        f"{len(batch_rows)}"
    )

    if len(batch_rows) != EXPECTED_BATCH_SIZE:
        raise ValueError(
            f"Batch 01 must contain "
            f"{EXPECTED_BATCH_SIZE} records, "
            f"but found {len(batch_rows)}."
        )

    # --------------------------------------------------------
    # Country validation
    # --------------------------------------------------------

    valid_country_ids = {
        normalise_text(row.get("country_id"))
        for row in countries
        if normalise_text(row.get("country_id"))
    }

    print()
    print("=" * 88)
    print("COUNTRY VALIDATION")
    print("=" * 88)

    country_errors = []

    for index, row in enumerate(batch_rows, start=1):

        country_id = normalise_text(
            row.get("country_id")
            or row.get("target_country_id")
        )

        scholarship_name = normalise_text(
            row.get("scholarship_name")
        )

        if not country_id:
            country_errors.append(
                f"Row {index}: country_id is missing"
            )

            print(
                f"{index}. FAIL - country_id missing"
            )

            continue

        if country_id not in valid_country_ids:
            country_errors.append(
                f"Row {index}: invalid country_id "
                f"{country_id}"
            )

            print(
                f"{index}. FAIL - {country_id}"
            )

            continue

        print(
            f"{index}. PASS - {country_id}"
            f" - {scholarship_name}"
        )

    if country_errors:
        raise ValueError(
            "Country validation failed:\n"
            + "\n".join(country_errors)
        )

    # --------------------------------------------------------
    # Existing scholarship IDs
    # --------------------------------------------------------

    existing_ids = {
        normalise_text(
            row.get("scholarship_id")
        )
        for row in baseline_scholarships
        if normalise_text(
            row.get("scholarship_id")
        )
    }

    existing_names = {
        normalise_name(
            row.get("scholarship_name")
        )
        for row in baseline_scholarships
        if normalise_name(
            row.get("scholarship_name")
        )
    }

    print()
    print("=" * 88)
    print("EXISTING SCHOLARSHIP ID CONVENTION")
    print("=" * 88)

    for scholarship_id in sorted(existing_ids):
        print(scholarship_id)

    # --------------------------------------------------------
    # Duplicate-name safety check
    # --------------------------------------------------------

    print()
    print("=" * 88)
    print("DUPLICATE NAME CHECK")
    print("=" * 88)

    duplicate_names = []

    for index, row in enumerate(batch_rows, start=1):

        scholarship_name = normalise_text(
            row.get("scholarship_name")
        )

        normalised = normalise_name(
            scholarship_name
        )

        if normalised in existing_names:
            duplicate_names.append(
                scholarship_name
            )

            print(
                f"{index}. DUPLICATE: "
                f"{scholarship_name}"
            )

        else:
            print(
                f"{index}. NEW: "
                f"{scholarship_name}"
            )

    if duplicate_names:
        raise ValueError(
            "Possible duplicate scholarship "
            "names detected. Pre-import aborted."
        )

    # --------------------------------------------------------
    # Assign IDs
    # --------------------------------------------------------

    print()
    print("=" * 88)
    print("NEW SCHOLARSHIP ID MAPPING")
    print("=" * 88)

    assigned_ids = set()
    prepared_rows = []

    for index, source_row in enumerate(
        batch_rows,
        start=1,
    ):

        row = dict(source_row)

        country_id = normalise_text(
            row.get("country_id")
            or row.get("target_country_id")
        )

        scholarship_name = normalise_text(
            row.get("scholarship_name")
        )

        current_id = normalise_text(
            row.get("scholarship_id")
        )

        if current_id:
            if current_id in existing_ids:
                raise ValueError(
                    f"Row {index}: scholarship_id "
                    f"{current_id} already exists."
                )

            if current_id in assigned_ids:
                raise ValueError(
                    f"Row {index}: duplicate new ID "
                    f"{current_id}."
                )

            new_id = current_id

        else:
            new_id = make_new_scholarship_id(
                country_id,
                existing_ids,
                assigned_ids,
            )

        row["scholarship_id"] = new_id

        # Keep canonical country_id
        row["country_id"] = country_id

        assigned_ids.add(new_id)
        prepared_rows.append(row)

        print(
            f"{index}. {new_id}"
            f" | {country_id}"
            f" | {scholarship_name}"
        )

    # --------------------------------------------------------
    # Expected result safety check
    # --------------------------------------------------------

    if len(assigned_ids) != EXPECTED_BATCH_SIZE:
        raise ValueError(
            "Generated ID count does not equal "
            "expected Batch 01 size."
        )

    if existing_ids.intersection(assigned_ids):
        raise ValueError(
            "Generated scholarship IDs collide "
            "with baseline IDs."
        )

    # --------------------------------------------------------
    # Preserve CSV schema
    # --------------------------------------------------------

    output_fields = list(batch_fields)

    if "scholarship_id" not in output_fields:
        output_fields.insert(
            0,
            "scholarship_id",
        )

    if "country_id" not in output_fields:
        output_fields.append(
            "country_id"
        )

    # --------------------------------------------------------
    # Create pre-import artifacts
    # --------------------------------------------------------

    write_csv(
        OUTPUT_CSV,
        prepared_rows,
        output_fields,
    )

    write_json(
        OUTPUT_JSON,
        prepared_rows,
    )

    # --------------------------------------------------------
    # Final duplicate validation
    # --------------------------------------------------------

    all_projected_ids = (
        existing_ids | assigned_ids
    )

    projected_count = (
        len(baseline_scholarships)
        + len(prepared_rows)
    )

    id_unique = (
        len(all_projected_ids)
        ==
        len(existing_ids) + len(assigned_ids)
    )

    report = {
        "step": "152.7C-3",
        "title": (
            "Scholarship ID Mapping "
            "& Pre-Import Package"
        ),
        "generated_at": datetime.now().isoformat(),
        "mongodb_modified": False,
        "baseline_scholarships": len(
            baseline_scholarships
        ),
        "verified_batch_records": len(
            prepared_rows
        ),
        "projected_scholarship_count": (
            projected_count
        ),
        "existing_ids": sorted(existing_ids),
        "new_ids": sorted(assigned_ids),
        "country_validation": "PASS",
        "duplicate_name_check": "PASS",
        "duplicate_id_check": (
            "PASS" if id_unique else "FAIL"
        ),
        "output_csv": str(OUTPUT_CSV),
        "output_json": str(OUTPUT_JSON),
    }

    write_json(
        REPORT_JSON,
        report,
    )

    print()
    print("=" * 88)
    print("PRE-IMPORT SUMMARY")
    print("=" * 88)

    print(
        f"Existing scholarships    : "
        f"{len(baseline_scholarships)}"
    )

    print(
        f"New verified scholarships: "
        f"{len(prepared_rows)}"
    )

    print(
        f"Projected total          : "
        f"{projected_count}"
    )

    print(
        f"Unique new IDs           : "
        f"{len(assigned_ids)}"
    )

    print(
        "Duplicate IDs            : "
        "0"
    )

    print(
        "MongoDB modified         : "
        "NO"
    )

    print()
    print(f"Pre-import CSV : {OUTPUT_CSV}")
    print(f"Pre-import JSON: {OUTPUT_JSON}")
    print(f"Report         : {REPORT_JSON}")

    print()
    print("=" * 88)
    print(
        "STEP 152.7C-3 PRE-IMPORT PACKAGE: PASS"
    )
    print("=" * 88)

    print()
    print(
        "IMPORTANT: Nothing has been imported "
        "into MongoDB yet."
    )

    print(
        "Next step: Step 152.7C-4 "
        "Safe MongoDB Scholarship Import."
    )


if __name__ == "__main__":
    main()