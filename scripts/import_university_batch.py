from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import UpdateOne


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import get_database

REQUIRED_FIELDS = [
    "university_id",
    "university_name",
    "country_id",
    "city",
    "official_website",
    "source_url",
]


def clean_text(value: Any) -> str:
    return " ".join(
        str(value or "").strip().split()
    )


def validate_records(
    records: list[dict[str, Any]],
    database: Any,
) -> list[dict[str, Any]]:

    errors: list[str] = []

    valid_country_ids = {
        item["country_id"]
        for item in database["countries"].find(
            {},
            {
                "_id": 0,
                "country_id": 1,
            },
        )
    }

    seen_ids: set[str] = set()
    seen_names: set[tuple[str, str]] = set()

    cleaned_records: list[dict[str, Any]] = []

    for position, raw in enumerate(
        records,
        start=1,
    ):
        record = dict(raw)

        for field in REQUIRED_FIELDS:
            value = record.get(field)

            if value is None or clean_text(value) == "":
                errors.append(
                    f"Row {position}: missing {field}"
                )

        university_id = clean_text(
            record.get("university_id")
        )

        university_name = clean_text(
            record.get("university_name")
        )

        country_id = clean_text(
            record.get("country_id")
        )

        city = clean_text(
            record.get("city")
        )

        official_website = clean_text(
            record.get("official_website")
        )

        source_url = clean_text(
            record.get("source_url")
        )

        if (
            university_id
            and university_id in seen_ids
        ):
            errors.append(
                f"Row {position}: duplicate "
                f"university_id {university_id}"
            )

        seen_ids.add(university_id)

        name_key = (
            country_id,
            university_name.lower(),
        )

        if (
            university_name
            and name_key in seen_names
        ):
            errors.append(
                f"Row {position}: duplicate "
                f"country/name {university_name}"
            )

        seen_names.add(name_key)

        if (
            country_id
            and country_id not in valid_country_ids
        ):
            errors.append(
                f"Row {position}: unknown "
                f"country_id {country_id}"
            )

        if (
            official_website
            and not official_website.startswith(
                ("http://", "https://")
            )
        ):
            errors.append(
                f"Row {position}: invalid "
                "official_website"
            )

        if (
            source_url
            and not source_url.startswith(
                ("http://", "https://")
            )
        ):
            errors.append(
                f"Row {position}: invalid source_url"
            )

        cleaned = {
            **record,
            "university_id": university_id,
            "university_name": university_name,
            "country_id": country_id,
            "city": city,
            "official_website": official_website,
            "source_url": source_url,
        }

        cleaned_records.append(cleaned)

    if errors:
        print()
        print("=" * 72)
        print("VALIDATION ERRORS")
        print("=" * 72)

        for error in errors:
            print("-", error)

        raise SystemExit(
            f"Validation failed with "
            f"{len(errors)} error(s)."
        )

    return cleaned_records


def check_database_conflicts(
    records: list[dict[str, Any]],
    database: Any,
) -> None:

    batch_ids = [
        record["university_id"]
        for record in records
    ]

    existing_by_id = {
        item["university_id"]: item
        for item in database[
            "universities"
        ].find(
            {
                "university_id": {
                    "$in": batch_ids,
                }
            },
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
                "country_id": 1,
            },
        )
    }

    conflicts = []

    for record in records:
        existing = existing_by_id.get(
            record["university_id"]
        )

        if existing is None:
            continue

        if (
            clean_text(
                existing.get("university_name")
            ).lower()
            != record[
                "university_name"
            ].lower()
            or existing.get("country_id")
            != record["country_id"]
        ):
            conflicts.append(
                (
                    record["university_id"],
                    existing.get(
                        "university_name"
                    ),
                    record[
                        "university_name"
                    ],
                )
            )

    if conflicts:
        print()
        print("=" * 72)
        print("DATABASE ID CONFLICTS")
        print("=" * 72)

        for item in conflicts:
            print(item)

        raise SystemExit(
            "Existing university_id conflict "
            "detected. Import cancelled."
        )


def import_records(
    records: list[dict[str, Any]],
    database: Any,
    dry_run: bool,
) -> None:

    check_database_conflicts(
        records,
        database,
    )

    if dry_run:
        print()
        print(
            "DRY RUN: database was not modified."
        )

        print(
            "Validated records:",
            len(records),
        )

        return

    now = datetime.now(
        timezone.utc
    )

    operations = []

    for record in records:

        document = {
            **record,
            "last_verified_at": now,
            "freshness_status": "current",
        }

        operations.append(
            UpdateOne(
                {
                    "university_id":
                        record["university_id"],
                },
                {
                    "$set": document,
                    "$setOnInsert": {
                        "collected_at": now,
                    },
                },
                upsert=True,
            )
        )

    result = database[
        "universities"
    ].bulk_write(
        operations
    )

    print()
    print("=" * 72)
    print("UNIVERSITY BULK IMPORT RESULT")
    print("=" * 72)

    print(
        "Input records:",
        len(records),
    )

    print(
        "Matched:",
        result.matched_count,
    )

    print(
        "Modified:",
        result.modified_count,
    )

    print(
        "Inserted:",
        len(result.upserted_ids),
    )


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "json_file",
        help=(
            "JSON file containing university "
            "records."
        ),
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Write validated records to MongoDB. "
            "Without this flag the script performs "
            "a dry run."
        ),
    )

    args = parser.parse_args()

    path = Path(args.json_file)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        raise SystemExit(
            f"File not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise SystemExit(
            "JSON root must be a list."
        )

    database = get_database()

    cleaned_records = validate_records(
        records,
        database,
    )

    print("=" * 72)
    print("UNIVERSITY BATCH VALIDATION")
    print("=" * 72)

    print(
        "Records:",
        len(cleaned_records),
    )

    print(
        "Countries:",
        len(
            {
                item["country_id"]
                for item in cleaned_records
            }
        ),
    )

    print(
        "Validation: PASS"
    )

    import_records(
        records=cleaned_records,
        database=database,
        dry_run=not args.apply,
    )


if __name__ == "__main__":
    main()
