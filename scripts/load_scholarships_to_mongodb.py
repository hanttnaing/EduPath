from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# ---------------------------------------------------------
# Project configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

INPUT_JSON = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "scholarships.json"
)

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)

SCHOLARSHIPS_COLLECTION = "scholarships"
COUNTRIES_COLLECTION = "countries"
UNIVERSITIES_COLLECTION = "universities"


# ---------------------------------------------------------
# Date conversion helpers
# ---------------------------------------------------------

def parse_required_date(
    value: Any,
    field_name: str,
) -> datetime:
    """Convert YYYY-MM-DD text into a UTC datetime."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Field '{field_name}' must contain a date."
        )

    try:
        parsed_date = datetime.strptime(
            value.strip(),
            "%Y-%m-%d",
        )
    except ValueError as error:
        raise ValueError(
            f"Field '{field_name}' must use YYYY-MM-DD format."
        ) from error

    return parsed_date.replace(tzinfo=timezone.utc)


def parse_optional_date(
    value: Any,
    field_name: str,
) -> datetime | None:
    """Convert an optional date into a UTC datetime."""

    if value is None:
        return None

    if isinstance(value, str) and not value.strip():
        return None

    return parse_required_date(
        value=value,
        field_name=field_name,
    )


# ---------------------------------------------------------
# Data preparation helpers
# ---------------------------------------------------------

def calculate_content_hash(
    record: dict[str, Any],
) -> str:
    """
    Create a stable hash representing scholarship content.

    Unchanged scholarship data creates the same hash.
    Changed data creates a different hash.
    """

    normalised_content = json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        normalised_content.encode("utf-8")
    ).hexdigest()


def prepare_document(
    raw_record: dict[str, Any],
) -> dict[str, Any]:
    """Prepare one cleaned scholarship for MongoDB."""

    document = raw_record.copy()

    document["application_opening_date"] = (
        parse_optional_date(
            document.get("application_opening_date"),
            "application_opening_date",
        )
    )

    document["application_deadline"] = (
        parse_optional_date(
            document.get("application_deadline"),
            "application_deadline",
        )
    )

    document["collected_at"] = parse_required_date(
        document.get("collected_at"),
        "collected_at",
    )

    document["last_verified_at"] = parse_required_date(
        document.get("last_verified_at"),
        "last_verified_at",
    )

    document["content_hash"] = calculate_content_hash(
        raw_record
    )

    return document


def load_json_records() -> list[dict[str, Any]]:
    """Read scholarship records from cleaned JSON."""

    if not INPUT_JSON.exists():
        raise FileNotFoundError(
            "The cleaned scholarships JSON file was not found.\n"
            f"Expected location: {INPUT_JSON}"
        )

    with INPUT_JSON.open(
        mode="r",
        encoding="utf-8",
    ) as input_file:
        records = json.load(input_file)

    if not isinstance(records, list):
        raise ValueError(
            "scholarships.json must contain a list of records."
        )

    if not records:
        raise ValueError(
            "scholarships.json does not contain any records."
        )

    return records


# ---------------------------------------------------------
# Relationship validation
# ---------------------------------------------------------

def validate_relationships(
    document: dict[str, Any],
    countries_collection: Any,
    universities_collection: Any,
) -> None:
    """
    Verify the scholarship country and host university.

    A host university must exist and belong to the same
    country as the scholarship.
    """

    country_id = document.get("country_id")

    if not country_id:
        raise ValueError(
            "Every scholarship must contain a country_id."
        )

    country_exists = countries_collection.find_one(
        {"country_id": country_id},
        {"_id": 1},
    )

    if country_exists is None:
        raise ValueError(
            f"Country '{country_id}' does not exist "
            "in the MongoDB countries collection."
        )

    host_university_id = document.get(
        "host_university_id"
    )

    if host_university_id is None:
        return

    university = universities_collection.find_one(
        {"university_id": host_university_id},
        {
            "_id": 0,
            "university_id": 1,
            "country_id": 1,
        },
    )

    if university is None:
        raise ValueError(
            f"Host university '{host_university_id}' "
            "does not exist in the MongoDB "
            "universities collection."
        )

    university_country_id = university.get("country_id")

    if university_country_id != country_id:
        raise ValueError(
            f"Host university '{host_university_id}' "
            f"belongs to '{university_country_id}', "
            f"not scholarship country '{country_id}'."
        )


# ---------------------------------------------------------
# Main loader
# ---------------------------------------------------------

def main() -> None:
    """Load cleaned scholarships into MongoDB Atlas."""

    print("=" * 60)
    print("EduPath MongoDB Scholarship Loader")
    print("=" * 60)

    if not ENV_FILE.exists():
        raise FileNotFoundError(
            "The .env file was not found.\n"
            f"Expected location: {ENV_FILE}"
        )

    if not MONGODB_URI:
        raise RuntimeError(
            "MONGODB_URI is missing from the .env file."
        )

    raw_records = load_json_records()

    print(f"Input JSON: {INPUT_JSON}")
    print(f"Records found: {len(raw_records)}")
    print(f"Database: {DATABASE_NAME}")
    print(
        f"Collection: {SCHOLARSHIPS_COLLECTION}"
    )
    print("Connecting to MongoDB Atlas...")

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:
        # Verify MongoDB Atlas connectivity.
        client.admin.command("ping")

        database = client[DATABASE_NAME]

        scholarships_collection = database[
            SCHOLARSHIPS_COLLECTION
        ]

        countries_collection = database[
            COUNTRIES_COLLECTION
        ]

        universities_collection = database[
            UNIVERSITIES_COLLECTION
        ]

        # -------------------------------------------------
        # Create indexes
        # -------------------------------------------------

        scholarship_id_index = (
            scholarships_collection.create_index(
                [("scholarship_id", ASCENDING)],
                unique=True,
                name="unique_scholarship_id",
            )
        )

        country_index = (
            scholarships_collection.create_index(
                [("country_id", ASCENDING)],
                name="scholarship_country_id",
            )
        )

        university_index = (
            scholarships_collection.create_index(
                [("host_university_id", ASCENDING)],
                name="scholarship_host_university_id",
            )
        )

        degree_index = (
            scholarships_collection.create_index(
                [("degree_levels", ASCENDING)],
                name="scholarship_degree_levels",
            )
        )

        funding_index = (
            scholarships_collection.create_index(
                [("funding_type", ASCENDING)],
                name="scholarship_funding_type",
            )
        )

        status_index = (
            scholarships_collection.create_index(
                [("scholarship_status", ASCENDING)],
                name="scholarship_status",
            )
        )

        deadline_index = (
            scholarships_collection.create_index(
                [("application_deadline", ASCENDING)],
                name="scholarship_deadline",
            )
        )

        print(f"Index ready: {scholarship_id_index}")
        print(f"Index ready: {country_index}")
        print(f"Index ready: {university_index}")
        print(f"Index ready: {degree_index}")
        print(f"Index ready: {funding_index}")
        print(f"Index ready: {status_index}")
        print(f"Index ready: {deadline_index}")

        inserted_count = 0
        updated_count = 0
        unchanged_count = 0

        # -------------------------------------------------
        # Process scholarship records
        # -------------------------------------------------

        for raw_record in raw_records:
            document = prepare_document(raw_record)

            scholarship_id = document.get(
                "scholarship_id"
            )

            scholarship_name = document.get(
                "scholarship_name"
            )

            if not scholarship_id:
                raise ValueError(
                    "Every scholarship must contain "
                    "a scholarship_id."
                )

            if not scholarship_name:
                raise ValueError(
                    "Every scholarship must contain "
                    "a scholarship_name."
                )

            validate_relationships(
                document=document,
                countries_collection=countries_collection,
                universities_collection=(
                    universities_collection
                ),
            )

            existing_document = (
                scholarships_collection.find_one(
                    {
                        "scholarship_id": scholarship_id
                    },
                    {
                        "_id": 1,
                        "content_hash": 1,
                    },
                )
            )

            # Skip the write if the scholarship did not change.
            if (
                existing_document is not None
                and existing_document.get("content_hash")
                == document["content_hash"]
            ):
                unchanged_count += 1

                print(
                    f"UNCHANGED: {scholarship_id} - "
                    f"{scholarship_name}"
                )

                continue

            current_time = datetime.now(timezone.utc)

            document["database_updated_at"] = (
                current_time
            )

            result = scholarships_collection.update_one(
                {
                    "scholarship_id": scholarship_id
                },
                {
                    "$set": document,
                    "$setOnInsert": {
                        "created_at": current_time,
                    },
                },
                upsert=True,
            )

            if result.upserted_id is not None:
                inserted_count += 1
                action = "INSERTED"
            else:
                updated_count += 1
                action = "UPDATED"

            print(
                f"{action}: {scholarship_id} - "
                f"{scholarship_name}"
            )

        # -------------------------------------------------
        # Loading summary
        # -------------------------------------------------

        total_documents = (
            scholarships_collection.count_documents({})
        )

        print("\nLoading summary")
        print("-" * 60)
        print(f"Records processed: {len(raw_records)}")
        print(f"Inserted: {inserted_count}")
        print(f"Updated: {updated_count}")
        print(f"Unchanged: {unchanged_count}")
        print(
            "Total documents in scholarships "
            f"collection: {total_documents}"
        )

        first_scholarship = (
            scholarships_collection.find_one(
                {"scholarship_id": "sch_jp_001"},
                {
                    "_id": 0,
                    "scholarship_id": 1,
                    "scholarship_name": 1,
                    "provider_name": 1,
                    "provider_type": 1,
                    "country_id": 1,
                    "host_university_id": 1,
                    "degree_levels": 1,
                    "fields_of_study": 1,
                    "funding_type": 1,
                    "tuition_coverage": 1,
                    "monthly_allowance": 1,
                    "allowance_currency": 1,
                    "application_opening_date": 1,
                    "application_deadline": 1,
                    "scholarship_status": 1,
                    "application_cycle": 1,
                    "freshness_status": 1,
                    "data_quality_status": 1,
                },
            )
        )

        print("\nVerification result")
        print("-" * 60)

        if first_scholarship is None:
            raise RuntimeError(
                "The scholarship could not be found "
                "after loading."
            )

        print(
            json.dumps(
                first_scholarship,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        print(
            "\nMongoDB scholarship loading "
            "completed successfully."
        )

    except PyMongoError as error:
        raise RuntimeError(
            "A MongoDB operation failed.\n"
            "Check the Atlas connection, database user, "
            "IP access list, and permissions."
        ) from error

    finally:
        client.close()
        print("MongoDB connection closed safely.")


if __name__ == "__main__":
    main()