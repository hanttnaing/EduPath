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
    / "countries.json"
)

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)

COLLECTION_NAME = "countries"


# ---------------------------------------------------------
# Helper functions
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


def calculate_content_hash(
    record: dict[str, Any],
) -> str:
    """
    Create a stable hash from the country content.

    Unchanged country data produces the same hash.
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
    """Prepare one cleaned country record for MongoDB."""

    document = raw_record.copy()

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
    """Read country records from countries.json."""

    if not INPUT_JSON.exists():
        raise FileNotFoundError(
            "The cleaned countries JSON file was not found.\n"
            f"Expected location: {INPUT_JSON}"
        )

    with INPUT_JSON.open(
        mode="r",
        encoding="utf-8",
    ) as input_file:
        records = json.load(input_file)

    if not isinstance(records, list):
        raise ValueError(
            "countries.json must contain a list of records."
        )

    if not records:
        raise ValueError(
            "countries.json does not contain any records."
        )

    return records


# ---------------------------------------------------------
# Main loader
# ---------------------------------------------------------

def main() -> None:
    """Load cleaned country records into MongoDB Atlas."""

    print("=" * 60)
    print("EduPath MongoDB Country Loader")
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
        # Verify the connection.
        client.admin.command("ping")

        database = client[DATABASE_NAME]
        collection = database[COLLECTION_NAME]

        # -------------------------------------------------
        # Create indexes
        # -------------------------------------------------

        country_id_index = collection.create_index(
            [("country_id", ASCENDING)],
            unique=True,
            name="unique_country_id",
        )

        country_name_index = collection.create_index(
            [("country_name", ASCENDING)],
            unique=True,
            name="unique_country_name",
        )

        region_index = collection.create_index(
            [("region", ASCENDING)],
            name="country_region",
        )

        currency_index = collection.create_index(
            [("currency_code", ASCENDING)],
            name="country_currency_code",
        )

        print(f"Index ready: {country_id_index}")
        print(f"Index ready: {country_name_index}")
        print(f"Index ready: {region_index}")
        print(f"Index ready: {currency_index}")

        inserted_count = 0
        updated_count = 0
        unchanged_count = 0

        # -------------------------------------------------
        # Process each country record
        # -------------------------------------------------

        for raw_record in raw_records:
            document = prepare_document(raw_record)

            country_id = document.get("country_id")
            country_name = document.get("country_name")

            if not country_id:
                raise ValueError(
                    "Every country must contain a country_id."
                )

            if not country_name:
                raise ValueError(
                    "Every country must contain a country_name."
                )

            existing_document = collection.find_one(
                {"country_id": country_id},
                {
                    "_id": 1,
                    "content_hash": 1,
                },
            )

            if (
                existing_document is not None
                and existing_document.get("content_hash")
                == document["content_hash"]
            ):
                unchanged_count += 1

                print(
                    f"UNCHANGED: {country_id} - "
                    f"{country_name}"
                )

                continue

            current_time = datetime.now(timezone.utc)

            document["database_updated_at"] = current_time

            result = collection.update_one(
                {"country_id": country_id},
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
                f"{action}: {country_id} - "
                f"{country_name}"
            )

        # -------------------------------------------------
        # Loading summary
        # -------------------------------------------------

        total_documents = collection.count_documents({})

        print("\nLoading summary")
        print("-" * 60)
        print(f"Records processed: {len(raw_records)}")
        print(f"Inserted: {inserted_count}")
        print(f"Updated: {updated_count}")
        print(f"Unchanged: {unchanged_count}")
        print(
            "Total documents in countries collection: "
            f"{total_documents}"
        )

        country_ids = [
            document["country_id"]
            for document in collection.find(
                {},
                {
                    "_id": 0,
                    "country_id": 1,
                },
            ).sort("country_id", ASCENDING)
        ]

        expected_country_ids = {
            "country_jp",
            "country_sg",
            "country_my",
        }

        missing_country_ids = (
            expected_country_ids - set(country_ids)
        )

        if missing_country_ids:
            raise RuntimeError(
                "The following expected countries are missing "
                "after loading:\n"
                + "\n".join(
                    f"- {country_id}"
                    for country_id in sorted(
                        missing_country_ids
                    )
                )
            )

        print("\nCountry IDs found")
        print("-" * 60)

        for country_id in country_ids:
            print(f"- {country_id}")

        first_country = collection.find_one(
            {"country_id": "country_jp"},
            {
                "_id": 0,
                "country_id": 1,
                "country_name": 1,
                "region": 1,
                "capital_city": 1,
                "currency_code": 1,
                "main_language": 1,
                "estimated_living_cost": 1,
                "cost_currency": 1,
                "collected_at": 1,
                "last_verified_at": 1,
            },
        )

        print("\nVerification result")
        print("-" * 60)

        if first_country is None:
            raise RuntimeError(
                "Japan could not be found after loading."
            )

        print(
            json.dumps(
                first_country,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        print(
            "\nMongoDB country loading "
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