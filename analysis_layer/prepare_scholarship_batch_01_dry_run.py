from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BASELINE_FILE = (
    PROJECT_ROOT
    / "backups"
    / "baseline_151_10"
    / "scholarships.json"
)

VERIFIED_BATCH_FILE = (
    PROJECT_ROOT
    / "data"
    / "staging"
    / "152_7c_batch_01_verified.csv"
)

OUTPUT_JSON = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7c_batch_01_integration_dry_run.json"
)

OUTPUT_CSV = (
    PROJECT_ROOT
    / "data"
    / "staging"
    / "152_7c_batch_01_import_ready_dry_run.csv"
)


def clean(value) -> str:
    if value is None:
        return ""

    if isinstance(value, list):
        return "; ".join(str(x).strip() for x in value if str(x).strip())

    return str(value).strip()


def normalise_text(value: str) -> str:
    value = clean(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalise_url(value: str) -> str:
    value = clean(value)

    if not value:
        return ""

    try:
        parsed = urlparse(value)

        domain = parsed.netloc.lower()
        path = parsed.path.rstrip("/").lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return f"{domain}{path}"

    except Exception:
        return value.lower().rstrip("/")


def load_json_records(path: Path) -> list[dict]:
    with path.open(
        "r",
        encoding="utf-8-sig"
    ) as file:
        payload = json.load(file)

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in (
            "items",
            "records",
            "data",
            "scholarships"
        ):
            value = payload.get(key)

            if isinstance(value, list):
                return value

    raise ValueError(
        f"Could not detect record list in:\n{path}"
    )


def load_csv_records(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(
                "Verified batch CSV has no header."
            )

        rows = list(reader)

    return reader.fieldnames, rows


def get_name(record: dict) -> str:
    for field in (
        "scholarship_name",
        "name",
        "title"
    ):
        value = clean(record.get(field))

        if value:
            return value

    return ""


def get_source_url(record: dict) -> str:
    for field in (
        "official_source_url",
        "source_url",
        "official_website",
        "url"
    ):
        value = clean(record.get(field))

        if value:
            return value

    return ""


def get_scholarship_id(record: dict) -> str:
    for field in (
        "scholarship_id",
        "id",
        "_id"
    ):
        value = clean(record.get(field))

        if value:
            return value

    return ""


def get_country_id(record: dict) -> str:
    for field in (
        "country_id",
        "target_country_id",
        "country"
    ):
        value = clean(record.get(field))

        if value:
            return value

    return ""


def duplicate_analysis(
    new_record: dict,
    existing_records: list[dict]
) -> dict:

    new_name = normalise_text(
        get_name(new_record)
    )

    new_url = normalise_url(
        get_source_url(new_record)
    )

    new_country = clean(
        get_country_id(new_record)
    ).lower()

    matches = []

    for existing in existing_records:

        existing_name = normalise_text(
            get_name(existing)
        )

        existing_url = normalise_url(
            get_source_url(existing)
        )

        existing_country = clean(
            get_country_id(existing)
        ).lower()

        reasons = []

        if (
            new_url
            and existing_url
            and new_url == existing_url
        ):
            reasons.append(
                "same_official_url"
            )

        if (
            new_name
            and existing_name
            and new_name == existing_name
        ):
            reasons.append(
                "same_normalised_name"
            )

        if (
            new_name
            and existing_name
            and new_country
            and existing_country
            and new_country == existing_country
            and (
                new_name in existing_name
                or existing_name in new_name
            )
        ):
            reasons.append(
                "similar_name_same_country"
            )

        if reasons:

            matches.append(
                {
                    "existing_scholarship_id":
                        get_scholarship_id(existing),

                    "existing_name":
                        get_name(existing),

                    "reasons":
                        reasons,
                }
            )

    return {
        "duplicate":
            len(matches) > 0,

        "matches":
            matches,
    }


def analyse_id_convention(records: list[dict]) -> dict:

    ids = [
        get_scholarship_id(record)
        for record in records
        if get_scholarship_id(record)
    ]

    numeric_suffixes = []

    for value in ids:

        match = re.search(
            r"(\d+)$",
            value
        )

        if match:
            numeric_suffixes.append(
                int(match.group(1))
            )

    return {
        "existing_ids": ids,

        "records_with_id":
            len(ids),

        "numeric_suffix_detected":
            len(numeric_suffixes) > 0,

        "highest_numeric_suffix":
            (
                max(numeric_suffixes)
                if numeric_suffixes
                else None
            ),
    }


def main() -> None:

    print("=" * 90)
    print(
        "EduPath - Step 152.7C-2 "
        "Scholarship Integration Dry Run"
    )
    print("=" * 90)

    print()
    print(
        f"Baseline file : {BASELINE_FILE}"
    )

    print(
        f"Verified file : {VERIFIED_BATCH_FILE}"
    )

    if not BASELINE_FILE.exists():
        raise FileNotFoundError(
            f"Baseline scholarship file missing:\n"
            f"{BASELINE_FILE}"
        )

    if not VERIFIED_BATCH_FILE.exists():
        raise FileNotFoundError(
            f"Verified batch file missing:\n"
            f"{VERIFIED_BATCH_FILE}"
        )

    existing = load_json_records(
        BASELINE_FILE
    )

    fieldnames, new_records = (
        load_csv_records(
            VERIFIED_BATCH_FILE
        )
    )

    print()
    print("=" * 90)
    print("DATASET COUNTS")
    print("=" * 90)

    print(
        f"Existing scholarships : "
        f"{len(existing)}"
    )

    print(
        f"Verified new records  : "
        f"{len(new_records)}"
    )

    print(
        f"Projected maximum     : "
        f"{len(existing) + len(new_records)}"
    )

    id_info = analyse_id_convention(
        existing
    )

    print()
    print("=" * 90)
    print("EXISTING ID CONVENTION")
    print("=" * 90)

    print(
        f"Records with ID       : "
        f"{id_info['records_with_id']}"
    )

    print(
        f"Numeric suffix found  : "
        f"{id_info['numeric_suffix_detected']}"
    )

    print(
        f"Highest suffix        : "
        f"{id_info['highest_numeric_suffix']}"
    )

    results = []

    duplicate_count = 0

    print()
    print("=" * 90)
    print("DUPLICATE CHECK")
    print("=" * 90)

    for index, record in enumerate(
        new_records,
        start=1
    ):

        duplicate_result = (
            duplicate_analysis(
                record,
                existing
            )
        )

        if duplicate_result["duplicate"]:
            duplicate_count += 1

        name = get_name(record)

        status = (
            "POSSIBLE DUPLICATE"
            if duplicate_result["duplicate"]
            else "NEW"
        )

        print()
        print(
            f"{index}. {name}"
        )

        print(
            f"   Country : "
            f"{get_country_id(record)}"
        )

        print(
            f"   Status  : {status}"
        )

        for match in (
            duplicate_result["matches"]
        ):

            print(
                "   Match   : "
                f"{match['existing_name']}"
            )

            print(
                "   Reason  : "
                + ", ".join(
                    match["reasons"]
                )
            )

        results.append(
            {
                "row": index,
                "scholarship_name": name,
                "country_id":
                    get_country_id(record),

                "source_url":
                    get_source_url(record),

                "duplicate":
                    duplicate_result[
                        "duplicate"
                    ],

                "duplicate_matches":
                    duplicate_result[
                        "matches"
                    ],
            }
        )

    safe_new_count = (
        len(new_records)
        - duplicate_count
    )

    projected_count = (
        len(existing)
        + safe_new_count
    )

    print()
    print("=" * 90)
    print("DRY-RUN SUMMARY")
    print("=" * 90)

    print(
        f"Existing scholarships      : "
        f"{len(existing)}"
    )

    print(
        f"Verified batch records     : "
        f"{len(new_records)}"
    )

    print(
        f"Possible duplicates        : "
        f"{duplicate_count}"
    )

    print(
        f"Safe new records           : "
        f"{safe_new_count}"
    )

    print(
        f"Projected scholarship count: "
        f"{projected_count}"
    )

    overall_status = (
        "PASS"
        if (
            len(new_records) == 6
            and duplicate_count == 0
        )
        else "REVIEW"
    )

    report = {
        "step": "152.7C-2",
        "generated_at":
            datetime.now().isoformat(),

        "mode":
            "DRY_RUN",

        "mongodb_modified":
            False,

        "existing_scholarship_count":
            len(existing),

        "verified_batch_count":
            len(new_records),

        "possible_duplicates":
            duplicate_count,

        "safe_new_records":
            safe_new_count,

        "projected_scholarship_count":
            projected_count,

        "id_convention":
            id_info,

        "records":
            results,

        "overall_status":
            overall_status,
    }

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False
        )

    # Preserve exact verified CSV.
    # This is only a dry-run copy.
    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            new_records
        )

    print()
    print(
        f"JSON report : {OUTPUT_JSON}"
    )

    print(
        f"Dry-run CSV : {OUTPUT_CSV}"
    )

    print()
    print(
        "MongoDB modified: NO"
    )

    print("=" * 90)

    if overall_status == "PASS":

        print(
            "STEP 152.7C-2 DRY RUN: PASS"
        )

        print(
            "No duplicates detected."
        )

    else:

        print(
            "STEP 152.7C-2 DRY RUN: REVIEW REQUIRED"
        )

        print(
            "Review possible duplicates before import."
        )

    print("=" * 90)


if __name__ == "__main__":
    main()