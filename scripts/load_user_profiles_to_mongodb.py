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
    / "user_profiles.json"
)

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)

USER_PROFILES_COLLECTION = "user_profiles"
COUNTRIES_COLLECTION = "countries"
UNIVERSITIES_COLLECTION = "universities"
SCHOLARSHIPS_COLLECTION = "scholarships"


# These fields can later be changed by users inside the app.
# The ETL loader must not overwrite them every time it runs.
RUNTIME_FIELDS = {
    "saved_universities",
    "saved_scholarships",
    "recommendation_history",
}


# ---------------------------------------------------------
# JSON loading
# ---------------------------------------------------------

def load_json_records() -> list[dict[str, Any]]:
    """Read user profiles from the cleaned JSON file."""

    if not INPUT_JSON.exists():
        raise FileNotFoundError(
            "The cleaned user profiles JSON file was not found.\n"
            f"Expected location: {INPUT_JSON}"
        )

    with INPUT_JSON.open(
        mode="r",
        encoding="utf-8",
    ) as input_file:
        records = json.load(input_file)

    if not isinstance(records, list):
        raise ValueError(
            "user_profiles.json must contain a list of records."
        )

    if not records:
        raise ValueError(
            "user_profiles.json does not contain any records."
        )

    for record in records:
        if not isinstance(record, dict):
            raise ValueError(
                "Every user profile must be a JSON object."
            )

    return records


# ---------------------------------------------------------
# Data preparation
# ---------------------------------------------------------

def calculate_content_hash(
    record: dict[str, Any],
) -> str:
    """
    Calculate a stable hash for profile preference fields.

    Runtime fields such as saved items and recommendation
    history are excluded so that rerunning this loader does
    not overwrite application-generated data.
    """

    source_profile = {
        key: value
        for key, value in record.items()
        if key not in RUNTIME_FIELDS
    }

    normalised_content = json.dumps(
        source_profile,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        normalised_content.encode("utf-8")
    ).hexdigest()


def prepare_document(
    raw_record: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[Any]]]:
    """
    Separate source profile fields from runtime fields.

    Source fields can be updated by ETL.
    Runtime fields are initialized only when the profile
    is first inserted.
    """

    source_document = {
        key: value
        for key, value in raw_record.items()
        if key not in RUNTIME_FIELDS
    }

    runtime_defaults: dict[str, list[Any]] = {}

    for field_name in RUNTIME_FIELDS:
        field_value = raw_record.get(field_name, [])

        if not isinstance(field_value, list):
            raise ValueError(
                f"Field '{field_name}' must contain a list."
            )

        runtime_defaults[field_name] = field_value

    source_document["content_hash"] = (
        calculate_content_hash(raw_record)
    )

    return source_document, runtime_defaults


# ---------------------------------------------------------
# Relationship validation
# ---------------------------------------------------------

def validate_preferred_countries(
    preferred_countries: Any,
    countries_collection: Any,
) -> None:
    """Verify all preferred country names exist in MongoDB."""

    if not isinstance(preferred_countries, list):
        raise ValueError(
            "Field 'preferred_countries' must contain a list."
        )

    if not preferred_countries:
        raise ValueError(
            "Field 'preferred_countries' cannot be empty."
        )

    country_documents = countries_collection.find(
        {
            "country_name": {
                "$in": preferred_countries
            }
        },
        {
            "_id": 0,
            "country_name": 1,
        },
    )

    existing_country_names = {
        document["country_name"]
        for document in country_documents
    }

    missing_country_names = (
        set(preferred_countries)
        - existing_country_names
    )

    if missing_country_names:
        raise ValueError(
            "The following preferred countries do not exist "
            "in the MongoDB countries collection:\n"
            + "\n".join(
                f"- {country_name}"
                for country_name in sorted(
                    missing_country_names
                )
            )
        )


def validate_saved_universities(
    university_ids: list[Any],
    universities_collection: Any,
) -> None:
    """Verify initial saved university IDs when provided."""

    if not university_ids:
        return

    university_documents = universities_collection.find(
        {
            "university_id": {
                "$in": university_ids
            }
        },
        {
            "_id": 0,
            "university_id": 1,
        },
    )

    existing_ids = {
        document["university_id"]
        for document in university_documents
    }

    missing_ids = set(university_ids) - existing_ids

    if missing_ids:
        raise ValueError(
            "The following saved university IDs do not exist:\n"
            + "\n".join(
                f"- {university_id}"
                for university_id in sorted(missing_ids)
            )
        )


def validate_saved_scholarships(
    scholarship_ids: list[Any],
    scholarships_collection: Any,
) -> None:
    """Verify initial saved scholarship IDs when provided."""

    if not scholarship_ids:
        return

    scholarship_documents = scholarships_collection.find(
        {
            "scholarship_id": {
                "$in": scholarship_ids
            }
        },
        {
            "_id": 0,
            "scholarship_id": 1,
        },
    )

    existing_ids = {
        document["scholarship_id"]
        for document in scholarship_documents
    }

    missing_ids = set(scholarship_ids) - existing_ids

    if missing_ids:
        raise ValueError(
            "The following saved scholarship IDs "
            "do not exist:\n"
            + "\n".join(
                f"- {scholarship_id}"
                for scholarship_id in sorted(missing_ids)
            )
        )


# ---------------------------------------------------------
# Main loader
# ---------------------------------------------------------

def main() -> None:
    """Load cleaned user profiles into MongoDB Atlas."""

    print("=" * 60)
    print("EduPath MongoDB User Profile Loader")
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
    print(f"Collection: {USER_PROFILES_COLLECTION}")
    print("Connecting to MongoDB Atlas...")

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:
        # Verify MongoDB connectivity.
        client.admin.command("ping")

        database = client[DATABASE_NAME]

        profiles_collection = database[
            USER_PROFILES_COLLECTION
        ]

        countries_collection = database[
            COUNTRIES_COLLECTION
        ]

        universities_collection = database[
            UNIVERSITIES_COLLECTION
        ]

        scholarships_collection = database[
            SCHOLARSHIPS_COLLECTION
        ]

        # -------------------------------------------------
        # Create indexes
        # -------------------------------------------------

        user_id_index = profiles_collection.create_index(
            [("user_id", ASCENDING)],
            unique=True,
            name="unique_user_id",
        )

        target_degree_index = (
            profiles_collection.create_index(
                [("target_degree_level", ASCENDING)],
                name="profile_target_degree_level",
            )
        )

        preferred_major_index = (
            profiles_collection.create_index(
                [("preferred_major", ASCENDING)],
                name="profile_preferred_major",
            )
        )

        preferred_country_index = (
            profiles_collection.create_index(
                [("preferred_countries", ASCENDING)],
                name="profile_preferred_countries",
            )
        )

        scholarship_required_index = (
            profiles_collection.create_index(
                [("scholarship_required", ASCENDING)],
                name="profile_scholarship_required",
            )
        )

        print(f"Index ready: {user_id_index}")
        print(f"Index ready: {target_degree_index}")
        print(f"Index ready: {preferred_major_index}")
        print(f"Index ready: {preferred_country_index}")
        print(f"Index ready: {scholarship_required_index}")

        inserted_count = 0
        updated_count = 0
        unchanged_count = 0

        # -------------------------------------------------
        # Process user profiles
        # -------------------------------------------------

        for raw_record in raw_records:
            source_document, runtime_defaults = (
                prepare_document(raw_record)
            )

            user_id = source_document.get("user_id")

            if not user_id:
                raise ValueError(
                    "Every user profile must contain a user_id."
                )

            validate_preferred_countries(
                preferred_countries=source_document.get(
                    "preferred_countries"
                ),
                countries_collection=countries_collection,
            )

            validate_saved_universities(
                university_ids=runtime_defaults[
                    "saved_universities"
                ],
                universities_collection=(
                    universities_collection
                ),
            )

            validate_saved_scholarships(
                scholarship_ids=runtime_defaults[
                    "saved_scholarships"
                ],
                scholarships_collection=(
                    scholarships_collection
                ),
            )

            existing_document = profiles_collection.find_one(
                {"user_id": user_id},
                {
                    "_id": 1,
                    "content_hash": 1,
                },
            )

            # Skip the update when source profile data
            # has not changed.
            if (
                existing_document is not None
                and existing_document.get("content_hash")
                == source_document["content_hash"]
            ):
                unchanged_count += 1

                print(
                    f"UNCHANGED: {user_id} - "
                    f"{source_document.get('preferred_major')}"
                )

                continue

            current_time = datetime.now(timezone.utc)

            source_document["database_updated_at"] = (
                current_time
            )

            result = profiles_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": source_document,
                    "$setOnInsert": {
                        "created_at": current_time,
                        "saved_universities": (
                            runtime_defaults[
                                "saved_universities"
                            ]
                        ),
                        "saved_scholarships": (
                            runtime_defaults[
                                "saved_scholarships"
                            ]
                        ),
                        "recommendation_history": (
                            runtime_defaults[
                                "recommendation_history"
                            ]
                        ),
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
                f"{action}: {user_id} - "
                f"{source_document.get('preferred_major')}"
            )

        # -------------------------------------------------
        # Loading summary
        # -------------------------------------------------

        total_documents = (
            profiles_collection.count_documents({})
        )

        print("\nLoading summary")
        print("-" * 60)
        print(f"Records processed: {len(raw_records)}")
        print(f"Inserted: {inserted_count}")
        print(f"Updated: {updated_count}")
        print(f"Unchanged: {unchanged_count}")
        print(
            "Total documents in user_profiles collection: "
            f"{total_documents}"
        )

        first_profile = profiles_collection.find_one(
            {"user_id": "user_test_001"},
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )

        print("\nVerification result")
        print("-" * 60)

        if first_profile is None:
            raise RuntimeError(
                "The pilot user profile could not be found "
                "after loading."
            )

        print(
            json.dumps(
                first_profile,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        print(
            "\nMongoDB user profile loading "
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