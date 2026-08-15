from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# ============================================================
# EduPath - Step 152.5
# MongoDB Baseline Dataset Backup
#
# IMPORTANT:
# - READ ONLY
# - This script does NOT modify MongoDB records.
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKUP_DIR = (
    PROJECT_ROOT
    / "backups"
    / "baseline_151_10"
)

ENV_FILE = PROJECT_ROOT / ".env"

DEFAULT_DATABASE_NAME = "edupath_db"

TARGET_COLLECTIONS = [
    "countries",
    "universities",
    "programs",
    "scholarships",
    "user_profiles",
]


def print_separator() -> None:
    print("=" * 78)


def load_environment() -> None:
    """
    Load environment variables from the project root .env file.
    """
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    else:
        load_dotenv()


def get_mongodb_uri() -> str:
    """
    Try commonly used MongoDB environment variable names.
    """

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
        "MongoDB URI was not found.\n"
        "Expected one of these environment variables:\n"
        "  MONGODB_URI\n"
        "  MONGO_URI\n"
        "  MONGODB_URL\n"
        "  DATABASE_URL\n"
    )


def get_database_name() -> str:
    """
    Resolve MongoDB database name.

    Defaults to edupath_db because this is the database
    currently used by EduPath.
    """

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


def json_safe(value: Any) -> Any:
    """
    Convert MongoDB/Python-specific values into JSON-safe values.
    """

    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            json_safe(item)
            for item in value
        ]

    return value


def write_json(
    file_path: Path,
    data: Any,
) -> None:
    """
    Save JSON using UTF-8 and readable formatting.
    """

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            json_safe(data),
            file,
            ensure_ascii=False,
            indent=2,
        )


def backup_collection(
    database,
    collection_name: str,
) -> dict[str, Any]:
    """
    Export one MongoDB collection into a JSON file.
    """

    collection = database[collection_name]

    documents = list(
        collection.find({})
    )

    output_file = (
        BACKUP_DIR
        / f"{collection_name}.json"
    )

    write_json(
        output_file,
        documents,
    )

    return {
        "collection": collection_name,
        "records": len(documents),
        "file": str(output_file),
        "status": "BACKED_UP",
    }


def main() -> None:
    print_separator()

    print(
        "EduPath - Step 152.5 "
        "MongoDB Baseline Dataset Backup"
    )

    print_separator()
    print()

    print(
        f"Project root : {PROJECT_ROOT}"
    )

    print(
        f"Backup folder: {BACKUP_DIR}"
    )

    print()

    load_environment()

    try:
        mongodb_uri = get_mongodb_uri()
        database_name = get_database_name()

    except RuntimeError as error:
        print("CONFIGURATION ERROR")
        print(error)
        sys.exit(1)

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    client: MongoClient | None = None

    try:
        print("Connecting to MongoDB Atlas...")

        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=10000,
        )

        client.admin.command("ping")

        print(
            "MongoDB Atlas connection: SUCCESS"
        )

        print(
            f"Database: {database_name}"
        )

        print()

        database = client[database_name]

        existing_collections = set(
            database.list_collection_names()
        )

        print_separator()
        print("COLLECTION BACKUP")
        print_separator()

        results: list[dict[str, Any]] = []

        total_records = 0

        for collection_name in TARGET_COLLECTIONS:

            if collection_name not in existing_collections:
                print(
                    f"{collection_name:<20}"
                    f": SKIPPED "
                    "(collection does not exist)"
                )

                results.append(
                    {
                        "collection": collection_name,
                        "records": 0,
                        "file": None,
                        "status": "SKIPPED_NOT_FOUND",
                    }
                )

                continue

            result = backup_collection(
                database,
                collection_name,
            )

            results.append(result)

            total_records += result["records"]

            print(
                f"{collection_name:<20}"
                f": {result['records']} record(s)"
            )

        print()

        # ----------------------------------------------------
        # Backup summary
        # ----------------------------------------------------

        summary = {
            "project": "EduPath Analytics",
            "step": "152.5",
            "baseline": "Step 151.10",
            "backup_type": "MongoDB JSON baseline backup",
            "database": database_name,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "mongodb_records_modified": False,
            "total_records_backed_up": total_records,
            "collections": results,
        }

        summary_file = (
            BACKUP_DIR
            / "backup_summary.json"
        )

        write_json(
            summary_file,
            summary,
        )

        print_separator()
        print("BACKUP SUMMARY")
        print_separator()

        for result in results:
            print(
                f"{result['collection']:<20}"
                f": {result['records']}"
            )

        print()
        print(
            f"Total records backed up: "
            f"{total_records}"
        )

        print()
        print(
            f"Summary report:\n"
            f"{summary_file}"
        )

        print()
        print(
            "MongoDB records modified: NO"
        )

        print()

        print_separator()
        print(
            "STEP 152.5 BASELINE BACKUP: COMPLETED"
        )
        print_separator()

    except PyMongoError as error:

        print()
        print_separator()
        print("MONGODB ERROR")
        print_separator()

        print(error)

        sys.exit(1)

    except Exception as error:

        print()
        print_separator()
        print("UNEXPECTED ERROR")
        print_separator()

        print(
            f"{type(error).__name__}: "
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