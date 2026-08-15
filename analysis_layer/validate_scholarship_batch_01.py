from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "staging"
    / "152_7c_batch_01_verified.csv"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7c_batch_01_validation.json"
)


ALIASES = {
    "name": [
        "scholarship_name",
        "name",
        "scholarship_title",
        "title",
    ],
    "country": [
        "country_id",
        "country_code",
        "country",
    ],
    "source": [
        "official_source_url",
        "source_url",
        "official_url",
        "url",
    ],
    "verification": [
        "verification_status",
        "data_quality_status",
        "verified",
    ],
    "cycle": [
        "application_cycle",
        "cycle",
        "academic_year",
    ],
}


PLACEHOLDER_VALUES = {
    "todo",
    "tbd",
    "test",
    "dummy",
    "sample",
    "placeholder",
    "fill later",
}


def clean(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def find_value(row: dict, aliases: list[str]) -> str:
    for key in aliases:
        if key in row:
            value = clean(row.get(key))
            if value:
                return value
    return ""


def is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)

        return (
            parsed.scheme == "https"
            and bool(parsed.netloc)
        )
    except Exception:
        return False


def contains_placeholder(value: str) -> bool:
    normalised = value.strip().lower()

    return normalised in PLACEHOLDER_VALUES


def validate_row(
    row_number: int,
    row: dict
) -> dict:

    errors = []
    warnings = []

    name = find_value(
        row,
        ALIASES["name"]
    )

    country = find_value(
        row,
        ALIASES["country"]
    )

    source = find_value(
        row,
        ALIASES["source"]
    )

    cycle = find_value(
        row,
        ALIASES["cycle"]
    )

    verification = find_value(
        row,
        ALIASES["verification"]
    )

    if not name:
        errors.append(
            "Scholarship name is missing."
        )

    if not country:
        errors.append(
            "Country identifier is missing."
        )

    if not source:
        errors.append(
            "Official source URL is missing."
        )

    elif not is_valid_url(source):
        errors.append(
            "Official source URL must be a valid HTTPS URL."
        )

    if cycle == "":
        warnings.append(
            "Application cycle is not available."
        )

    if verification:
        valid_statuses = {
            "verified",
            "pending",
            "current",
            "reviewed",
        }

        if verification.lower() not in valid_statuses:
            warnings.append(
                f"Unrecognised verification status: {verification}"
            )

    for key, value in row.items():

        value = clean(value)

        if contains_placeholder(value):
            errors.append(
                f"Placeholder value found in '{key}': {value}"
            )

    status = "PASS" if not errors else "FAIL"

    return {
        "row": row_number,
        "scholarship": name,
        "country": country,
        "official_source_url": source,
        "status": status,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:

    print("=" * 90)
    print(
        "EduPath - Step 152.7C-1 "
        "Official Scholarship Batch Validation"
    )
    print("=" * 90)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Batch file does not exist:\n{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(
                "CSV header could not be detected."
            )

        rows = list(reader)

    print()
    print(f"Records loaded : {len(rows)}")

    if len(rows) != 6:
        print()
        print(
            "WARNING: Step 152.7C-1 "
            "expects exactly 6 records."
        )

    results = []

    for index, row in enumerate(
        rows,
        start=1
    ):

        result = validate_row(
            index,
            row
        )

        results.append(result)

    passed = sum(
        1
        for result in results
        if result["status"] == "PASS"
    )

    failed = len(results) - passed

    print()
    print("=" * 90)
    print("VALIDATION RESULTS")
    print("=" * 90)

    for result in results:

        print()
        print(
            f"{result['row']}. "
            f"{result['scholarship'] or '<NO NAME>'}"
        )

        print(
            f"   Country : "
            f"{result['country'] or '<MISSING>'}"
        )

        print(
            f"   Status  : "
            f"{result['status']}"
        )

        for error in result["errors"]:
            print(
                f"   ERROR   : {error}"
            )

        for warning in result["warnings"]:
            print(
                f"   WARNING : {warning}"
            )

    overall_status = (
        "PASS"
        if failed == 0
        and len(rows) == 6
        else "FAIL"
    )

    report = {
        "step": "152.7C-1",
        "generated_at": datetime.now().isoformat(),
        "records_checked": len(rows),
        "records_passed": passed,
        "records_failed": failed,
        "overall_status": overall_status,
        "mongodb_modified": False,
        "records": results,
    }

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with REPORT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 90)

    print(
        f"Records checked : {len(rows)}"
    )

    print(
        f"Records passed  : {passed}"
    )

    print(
        f"Records failed  : {failed}"
    )

    print(
        f"Overall status  : {overall_status}"
    )

    print()
    print(
        f"JSON report     : {REPORT_FILE}"
    )

    print(
        "MongoDB modified: NO"
    )

    print("=" * 90)

    if overall_status == "PASS":

        print(
            "STEP 152.7C-1 FIRST VERIFIED "
            "SCHOLARSHIP BATCH: COMPLETED"
        )

    else:

        print(
            "STEP 152.7C-1 NOT COMPLETE."
        )

        print(
            "Fix failed records before continuing."
        )

    print("=" * 90)


if __name__ == "__main__":
    main()