from __future__ import annotations

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
# Project paths and configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

INPUT_JSON = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "universities.json"
)

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)

COLLECTION_NAME = "universities"


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def parse_iso_date(value: Any, field_name: str) -> datetime:
    """
    Convert a YYYY-MM-DD string into a UTC datetime value.

    Example:
    2026-07-29
    """

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Field '{field_name}' must contain a valid date string."
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


def prepare_document(
    record: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepare one cleaned JSON record for MongoDB.

    The JSON date strings are converted into actual
    MongoDB-compatible datetime values.
    """

    document = record.copy()

    document["collected_at"] = parse_iso_date(
        document.get("collected_at"),
        "collected_at",
    )

    last_verified_at = document.get(
        "last_verified_at"
    )

    if last_verified_at is None:
        document["last_verified_at"] = None
    else:
        document["last_verified_at"] = parse_iso_date(
            last_verified_at,
            "last_verified_at",
        )

    # Record when this loader last processed the document.
    document["database_updated_at"] = datetime.now(
        timezone.utc
    )

    return document


def load_json_records() -> list[dict[str, Any]]:
    """Read and validate university records from JSON."""

    if not INPUT_JSON.exists():
        raise FileNotFoundError(
            "The cleaned universities JSON file was not found.\n"
            f"Expected location: {INPUT_JSON}"
        )

    with INPUT_JSON.open(
        mode="r",
        encoding="utf-8",
    ) as input_file:
        records = json.load(input_file)

    if not isinstance(records, list):
        raise ValueError(
            "The universities JSON file must contain a list."
        )

    if not records:
        raise ValueError(
            "The universities JSON file contains no records."
        )

    return records


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------

def main() -> None:
    """Load cleaned university records into MongoDB Atlas."""

    print("=" * 60)
    print("EduPath MongoDB University Loader")
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
    print(f"Collection: {COLLECTION_NAME}")
    print("Connecting to MongoDB Atlas...")

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:
        # Verify that the Atlas connection is working.
        client.admin.command("ping")

        database = client[DATABASE_NAME]
        collection = database[COLLECTION_NAME]

        # Prevent duplicate university_id values.
        index_name = collection.create_index(
            [("university_id", ASCENDING)],
            unique=True,
            name="unique_university_id",
        )

        print(f"Index ready: {index_name}")

        inserted_count = 0
        updated_count = 0
        unchanged_count = 0

        for raw_record in raw_records:
            document = prepare_document(raw_record)

            university_id = document.get("university_id")

            if not university_id:
                raise ValueError(
                    "Every university record must contain "
                    "a university_id."
                )

            result = collection.update_one(
                {"university_id": university_id},
                {"$set": document},
                upsert=True,
            )

            if result.upserted_id is not None:
                inserted_count += 1
                action = "INSERTED"
            elif result.modified_count > 0:
                updated_count += 1
                action = "UPDATED"
            else:
                unchanged_count += 1
                action = "UNCHANGED"

            print(
                f"{action}: "
                f"{university_id} - "
                f"{document.get('university_name')}"
            )

        total_documents = collection.count_documents({})

        print("\nLoading summary")
        print("-" * 60)
        print(f"Records processed: {len(raw_records)}")
        print(f"Inserted: {inserted_count}")
        print(f"Updated: {updated_count}")
        print(f"Unchanged: {unchanged_count}")
        print(
            "Total documents in universities collection: "
            f"{total_documents}"
        )

        first_document = collection.find_one(
            {"university_id": "uni_jp_001"},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
                "country_id": 1,
                "city": 1,
                "degree_levels": 1,
                "scholarship_available": 1,
                "last_verified_at": 1,
                "freshness_status": 1,
            },
        )

        print("\nVerification result")
        print("-" * 60)

        if first_document is None:
            raise RuntimeError(
                "The inserted university could not be found."
            )

        print(
            json.dumps(
                first_document,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        print("\nMongoDB loading completed successfully.")

    except PyMongoError as error:
        raise RuntimeError(
            "A MongoDB operation failed.\n"
            "Check your connection, permissions, "
            "database user, and Atlas IP access list."
        ) from error

    finally:
        client.close()
        print("MongoDB connection closed safely.")


if __name__ == "__main__":
    main()