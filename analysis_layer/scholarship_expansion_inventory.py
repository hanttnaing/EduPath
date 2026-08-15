from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# ============================================================
# EduPath - Step 152.7A
# Scholarship Expansion Schema & Coverage Inventory
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
STAGING_DIR = PROJECT_ROOT / "data" / "staging"
PLANNING_DIR = PROJECT_ROOT / "planning"

JSON_REPORT = (
    ANALYSIS_DIR
    / "152_7a_scholarship_expansion_inventory.json"
)

CSV_REPORT = (
    PLANNING_DIR
    / "40_scholarship_field_inventory.csv"
)

STAGING_TEMPLATE = (
    STAGING_DIR
    / "152_7b_scholarship_expansion_template.csv"
)

DEFAULT_DATABASE_NAME = "edupath_db"

MINIMUM_TARGET = 30
RECOMMENDED_TARGET = 50


# Fields useful for the final recommendation system.
# We DO NOT automatically add these to MongoDB.
# They are only compared against the current schema.

RECOMMENDATION_FIELDS = [
    "scholarship_id",
    "name",
    "country_id",
    "university_id",
    "funding_type",
    "degree_levels",
    "fields_of_study",
    "minimum_gpa",
    "english_requirement",
    "eligible_nationalities",
    "age_limit",
    "application_opening_date",
    "application_deadline",
    "application_cycle",
    "scholarship_status",
    "official_source_url",
    "source_url",
    "last_verified_at",
    "freshness_status",
    "data_quality_status",
]


def separator() -> None:
    print("=" * 90)


def load_environment() -> None:
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    else:
        load_dotenv()


def get_mongodb_uri() -> str:
    possible_keys = [
        "MONGODB_URI",
        "MONGO_URI",
        "MONGODB_URL",
        "DATABASE_URL",
    ]

    for key in possible_keys:
        value = os.getenv(key)

        if value and value.strip():
            return value.strip()

    raise RuntimeError(
        "MongoDB connection URI was not found in environment variables."
    )


def get_database_name() -> str:
    possible_keys = [
        "MONGODB_DB",
        "MONGO_DB",
        "DATABASE_NAME",
        "DB_NAME",
    ]

    for key in possible_keys:
        value = os.getenv(key)

        if value and value.strip():
            return value.strip()

    return DEFAULT_DATABASE_NAME


def value_type_name(value: Any) -> str:
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "bool"

    if isinstance(value, list):
        return "list"

    if isinstance(value, dict):
        return "dict"

    if isinstance(value, datetime):
        return "datetime"

    if isinstance(value, int):
        return "int"

    if isinstance(value, float):
        return "float"

    if isinstance(value, str):
        return "str"

    return type(value).__name__


def is_populated(value: Any) -> bool:
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (list, dict)):
        return len(value) > 0

    return True


def safe_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            safe_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: safe_value(item)
            for key, item in value.items()
        }

    return value


def main() -> None:
    separator()

    print(
        "EduPath - Step 152.7A "
        "Scholarship Expansion Schema & Coverage Inventory"
    )

    separator()
    print()

    load_environment()

    client: MongoClient | None = None

    try:
        mongodb_uri = get_mongodb_uri()
        database_name = get_database_name()

        print("Connecting to MongoDB Atlas...")

        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=10000,
        )

        client.admin.command("ping")

        print("MongoDB Atlas connection: SUCCESS")
        print(f"Database: {database_name}")

        database = client[database_name]

        if "scholarships" not in database.list_collection_names():
            raise RuntimeError(
                "The 'scholarships' collection does not exist."
            )

        scholarship_collection = database["scholarships"]

        scholarships = list(
            scholarship_collection.find({})
        )

        total_records = len(scholarships)

        print()
        separator()
        print("CURRENT SCHOLARSHIP DATASET")
        separator()

        print()
        print(f"Current scholarships       : {total_records}")
        print(f"Minimum target             : {MINIMUM_TARGET}")
        print(f"Recommended target         : {RECOMMENDED_TARGET}")
        print(
            f"Minimum records still needed: "
            f"{max(MINIMUM_TARGET - total_records, 0)}"
        )
        print(
            f"Recommended records needed  : "
            f"{max(RECOMMENDED_TARGET - total_records, 0)}"
        )

        # ----------------------------------------------------
        # Discover actual MongoDB field names
        # ----------------------------------------------------

        field_occurrence = Counter()
        field_populated = Counter()

        field_types: dict[str, Counter] = defaultdict(Counter)

        all_fields: set[str] = set()

        for record in scholarships:
            for field, value in record.items():

                if field == "_id":
                    continue

                all_fields.add(field)

                field_occurrence[field] += 1

                if is_populated(value):
                    field_populated[field] += 1

                field_types[field][
                    value_type_name(value)
                ] += 1

        sorted_fields = sorted(all_fields)

        print()
        separator()
        print("DISCOVERED SCHOLARSHIP FIELDS")
        separator()
        print()

        inventory_rows: list[dict[str, Any]] = []

        for field in sorted_fields:
            present_count = field_occurrence[field]
            populated_count = field_populated[field]

            coverage = (
                (populated_count / total_records) * 100
                if total_records
                else 0
            )

            types_found = ", ".join(
                f"{data_type}:{count}"
                for data_type, count
                in field_types[field].most_common()
            )

            row = {
                "field": field,
                "present_records": present_count,
                "populated_records": populated_count,
                "total_records": total_records,
                "coverage_percent": round(
                    coverage,
                    2,
                ),
                "types_found": types_found,
            }

            inventory_rows.append(row)

            print(
                f"{field:<32} "
                f"{populated_count:>3}/{total_records:<3} "
                f"{coverage:>7.2f}%   "
                f"{types_found}"
            )

        # ----------------------------------------------------
        # Compare schema with recommendation needs
        # ----------------------------------------------------

        print()
        separator()
        print("RECOMMENDATION FIELD GAP CHECK")
        separator()
        print()

        existing_lower = {
            field.lower(): field
            for field in sorted_fields
        }

        found_recommendation_fields = []
        missing_recommendation_fields = []

        for recommended_field in RECOMMENDATION_FIELDS:

            if recommended_field.lower() in existing_lower:
                found_recommendation_fields.append(
                    recommended_field
                )

            else:
                missing_recommendation_fields.append(
                    recommended_field
                )

        print("Fields currently present:")
        for field in found_recommendation_fields:
            print(f"  + {field}")

        print()

        print(
            "Potential recommendation fields "
            "not found under these exact names:"
        )

        if missing_recommendation_fields:
            for field in missing_recommendation_fields:
                print(f"  - {field}")
        else:
            print("  None")

        print()
        print(
            "NOTE: Missing exact names do NOT automatically "
            "mean the information is absent."
        )
        print(
            "The current schema may use a different field name. "
            "We will map fields before importing new data."
        )

        # ----------------------------------------------------
        # First 3 sanitized records for schema inspection
        # ----------------------------------------------------

        samples = []

        for record in scholarships[:3]:

            clean_record = {}

            for key, value in record.items():

                if key == "_id":
                    clean_record["_id"] = str(value)
                else:
                    clean_record[key] = safe_value(
                        value
                    )

            samples.append(clean_record)

        # ----------------------------------------------------
        # Save JSON report
        # ----------------------------------------------------

        ANALYSIS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        PLANNING_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        STAGING_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = {
            "project": "EduPath Analytics",
            "step": "152.7A",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "database": database_name,
            "collection": "scholarships",
            "current_count": total_records,
            "minimum_target": MINIMUM_TARGET,
            "recommended_target": RECOMMENDED_TARGET,
            "minimum_records_needed": max(
                MINIMUM_TARGET - total_records,
                0,
            ),
            "recommended_records_needed": max(
                RECOMMENDED_TARGET - total_records,
                0,
            ),
            "discovered_fields": sorted_fields,
            "field_inventory": inventory_rows,
            "recommendation_fields_found": (
                found_recommendation_fields
            ),
            "recommendation_fields_missing_exact_name": (
                missing_recommendation_fields
            ),
            "sample_records": samples,
            "mongodb_records_modified": False,
        }

        with JSON_REPORT.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=2,
                ensure_ascii=False,
            )

        # ----------------------------------------------------
        # Save CSV field inventory
        # ----------------------------------------------------

        with CSV_REPORT.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "field",
                    "present_records",
                    "populated_records",
                    "total_records",
                    "coverage_percent",
                    "types_found",
                ],
            )

            writer.writeheader()
            writer.writerows(
                inventory_rows
            )

        # ----------------------------------------------------
        # Create EMPTY expansion staging template
        # using ACTUAL current field names only.
        # ----------------------------------------------------

        with STAGING_TEMPLATE.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                sorted_fields
            )

        print()
        separator()

        print(
            "STEP 152.7A SCHOLARSHIP "
            "EXPANSION INVENTORY: COMPLETED"
        )

        separator()

        print()

        print("JSON report:")
        print(JSON_REPORT)

        print()

        print("Field inventory CSV:")
        print(CSV_REPORT)

        print()

        print("Expansion staging template:")
        print(STAGING_TEMPLATE)

        print()

        print("MongoDB records modified: NO")

    except PyMongoError as error:

        print()
        print("MongoDB error:")
        print(error)

        sys.exit(1)

    except Exception as error:

        print()
        print(
            f"Error: {type(error).__name__}: "
            f"{error}"
        )

        sys.exit(1)

    finally:

        if client is not None:
            client.close()

            print()
            print(
                "MongoDB connection closed safely."
            )


if __name__ == "__main__":
    main()