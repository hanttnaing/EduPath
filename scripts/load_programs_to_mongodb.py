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
    / "programs.json"
)

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)

PROGRAMS_COLLECTION = "programs"
UNIVERSITIES_COLLECTION = "universities"


# ---------------------------------------------------------
# Data helper functions
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


def calculate_content_hash(
    record: dict[str, Any],
) -> str:
    """
    Create a stable hash representing the programme content.

    If the programme data does not change, this hash remains
    the same. This allows unchanged records to be skipped.
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
    """Prepare one cleaned programme record for MongoDB."""

    document = raw_record.copy()

    document["collected_at"] = parse_required_date(
        document.get("collected_at"),
        "collected_at",
    )

    document["last_verified_at"] = parse_required_date(
        document.get("last_verified_at"),
        "last_verified_at",
    )

    document["application_deadline"] = parse_optional_date(
        document.get("application_deadline"),
        "application_deadline",
    )

    document["content_hash"] = calculate_content_hash(
        raw_record
    )

    return document


def load_json_records() -> list[dict[str, Any]]:
    """Read programme records from the cleaned JSON file."""

    if not INPUT_JSON.exists():
        raise FileNotFoundError(
            "The cleaned programmes JSON file was not found.\n"
            f"Expected location: {INPUT_JSON}"
        )

    with INPUT_JSON.open(
        mode="r",
        encoding="utf-8",
    ) as input_file:
        records = json.load(input_file)

    if not isinstance(records, list):
        raise ValueError(
            "programs.json must contain a list of records."
        )

    if not records:
        raise ValueError(
            "programs.json does not contain any records."
        )

    return records


# ---------------------------------------------------------
# Main loader
# ---------------------------------------------------------

def main() -> None:
    """Load cleaned programme records into MongoDB Atlas."""

    print("=" * 60)
    print("EduPath MongoDB Programme Loader")
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
    print(f"Collection: {PROGRAMS_COLLECTION}")
    print("Connecting to MongoDB Atlas...")

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:
        # Verify Atlas connectivity.
        client.admin.command("ping")

        database = client[DATABASE_NAME]

        programs_collection = database[
            PROGRAMS_COLLECTION
        ]

        universities_collection = database[
            UNIVERSITIES_COLLECTION
        ]

        # -------------------------------------------------
        # Create indexes
        # -------------------------------------------------

        program_id_index = programs_collection.create_index(
            [("program_id", ASCENDING)],
            unique=True,
            name="unique_program_id",
        )

        university_id_index = (
            programs_collection.create_index(
                [("university_id", ASCENDING)],
                name="program_university_id",
            )
        )

        degree_level_index = (
            programs_collection.create_index(
                [("degree_level", ASCENDING)],
                name="program_degree_level",
            )
        )

        field_index = programs_collection.create_index(
            [("field_of_study", ASCENDING)],
            name="program_field_of_study",
        )

        print(f"Index ready: {program_id_index}")
        print(f"Index ready: {university_id_index}")
        print(f"Index ready: {degree_level_index}")
        print(f"Index ready: {field_index}")

        inserted_count = 0
        updated_count = 0
        unchanged_count = 0

        # -------------------------------------------------
        # Process each programme record
        # -------------------------------------------------

        for raw_record in raw_records:
            document = prepare_document(raw_record)

            program_id = document.get("program_id")
            university_id = document.get("university_id")

            if not program_id:
                raise ValueError(
                    "Every programme must contain a program_id."
                )

            if not university_id:
                raise ValueError(
                    "Every programme must contain "
                    "a university_id."
                )

            # Verify the programme's parent university.
            university_exists = (
                universities_collection.find_one(
                    {"university_id": university_id},
                    {"_id": 1},
                )
            )

            if university_exists is None:
                raise ValueError(
                    f"University '{university_id}' does not "
                    "exist in the MongoDB universities "
                    "collection."
                )

            existing_document = (
                programs_collection.find_one(
                    {"program_id": program_id},
                    {
                        "_id": 1,
                        "content_hash": 1,
                    },
                )
            )

            # Skip the database write when nothing changed.
            if (
                existing_document is not None
                and existing_document.get("content_hash")
                == document["content_hash"]
            ):
                unchanged_count += 1

                print(
                    f"UNCHANGED: {program_id} - "
                    f"{document.get('program_name')}"
                )

                continue

            current_time = datetime.now(timezone.utc)

            document["database_updated_at"] = current_time

            result = programs_collection.update_one(
                {"program_id": program_id},
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
                f"{action}: {program_id} - "
                f"{document.get('program_name')}"
            )

        # -------------------------------------------------
        # Display loading results
        # -------------------------------------------------

        total_documents = (
            programs_collection.count_documents({})
        )

        print("\nLoading summary")
        print("-" * 60)
        print(f"Records processed: {len(raw_records)}")
        print(f"Inserted: {inserted_count}")
        print(f"Updated: {updated_count}")
        print(f"Unchanged: {unchanged_count}")
        print(
            "Total documents in programs collection: "
            f"{total_documents}"
        )

        first_program = programs_collection.find_one(
            {"program_id": "prog_jp_001"},
            {
                "_id": 0,
                "program_id": 1,
                "university_id": 1,
                "program_name": 1,
                "field_of_study": 1,
                "degree_level": 1,
                "language_of_instruction": 1,
                "tuition_fee": 1,
                "tuition_currency": 1,
                "intake": 1,
                "application_deadline": 1,
                "freshness_status": 1,
            },
        )

        print("\nVerification result")
        print("-" * 60)

        if first_program is None:
            raise RuntimeError(
                "The programme could not be found "
                "after loading."
            )

        print(
            json.dumps(
                first_program,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        print(
            "\nMongoDB programme loading "
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