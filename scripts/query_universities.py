from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# ---------------------------------------------------------
# Project configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)

COLLECTION_NAME = "universities"


def print_json(data: Any) -> None:
    """Print MongoDB data in a readable JSON-style format."""

    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


def main() -> None:
    """Run basic university queries against MongoDB Atlas."""

    print("=" * 60)
    print("EduPath University Query Test")
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

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:
        client.admin.command("ping")

        database = client[DATABASE_NAME]
        collection = database[COLLECTION_NAME]

        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {COLLECTION_NAME}")
        print("MongoDB connection: SUCCESS")

        # -------------------------------------------------
        # Query 1: Count all university documents
        # -------------------------------------------------

        total_documents = collection.count_documents({})

        print("\n1. Total university documents")
        print("-" * 60)
        print(f"Total universities: {total_documents}")

        # -------------------------------------------------
        # Query 2: Find one university by university_id
        # -------------------------------------------------

        university = collection.find_one(
            {"university_id": "uni_jp_001"},
            {"_id": 0},
        )

        print("\n2. Find university by university_id")
        print("-" * 60)

        if university is None:
            print("University not found.")
        else:
            print_json(university)

        # -------------------------------------------------
        # Query 3: Find universities from Japan
        # -------------------------------------------------

        japan_cursor = collection.find(
            {"country_id": "country_jp"},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
                "country_id": 1,
                "city": 1,
            },
        )

        japan_universities = list(japan_cursor)

        print("\n3. Universities in Japan")
        print("-" * 60)
        print(f"Matching records: {len(japan_universities)}")
        print_json(japan_universities)

        # -------------------------------------------------
        # Query 4: Find universities with scholarships
        # -------------------------------------------------

        scholarship_cursor = collection.find(
            {"scholarship_available": True},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
                "scholarship_available": 1,
                "degree_levels": 1,
            },
        )

        scholarship_universities = list(
            scholarship_cursor
        )

        print("\n4. Universities with scholarships")
        print("-" * 60)
        print(
            "Matching records: "
            f"{len(scholarship_universities)}"
        )
        print_json(scholarship_universities)

        # -------------------------------------------------
        # Query 5: Find universities offering Master level
        # -------------------------------------------------

        master_cursor = collection.find(
            {"degree_levels": "Master"},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
                "degree_levels": 1,
            },
        )

        master_universities = list(master_cursor)

        print("\n5. Universities offering Master programmes")
        print("-" * 60)
        print(f"Matching records: {len(master_universities)}")
        print_json(master_universities)

        print("\nAll MongoDB queries completed successfully.")

    except PyMongoError as error:
        raise RuntimeError(
            "A MongoDB query failed.\n"
            "Check your internet connection, Atlas IP access, "
            "database user, and connection string."
        ) from error

    finally:
        client.close()
        print("MongoDB connection closed safely.")


if __name__ == "__main__":
    main()