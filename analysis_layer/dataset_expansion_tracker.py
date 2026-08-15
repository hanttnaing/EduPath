from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# ============================================================
# EduPath - Step 152.6
# Dataset Expansion Master Plan & Target Tracker
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis"

OUTPUT_JSON = (
    OUTPUT_DIR
    / "152_6_dataset_expansion_tracker.json"
)

DEFAULT_DATABASE_NAME = "edupath_db"


# ------------------------------------------------------------
# Dataset expansion targets
# ------------------------------------------------------------

TARGETS = {
    "countries": {
        "minimum": 7,
        "recommended": 7,
        "priority": 5,
    },
    "universities": {
        "minimum": 60,
        "recommended": 80,
        "priority": 4,
    },
    "programs": {
        "minimum": 60,
        "recommended": 100,
        "priority": 2,
    },
    "scholarships": {
        "minimum": 30,
        "recommended": 50,
        "priority": 1,
    },
    "user_profiles": {
        "minimum": 20,
        "recommended": 30,
        "priority": 3,
    },
}


def separator() -> None:
    print("=" * 82)


def load_environment() -> None:
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    else:
        load_dotenv()


def get_mongodb_uri() -> str:

    keys = [
        "MONGODB_URI",
        "MONGO_URI",
        "MONGODB_URL",
        "DATABASE_URL",
    ]

    for key in keys:
        value = os.getenv(key)

        if value and value.strip():
            return value.strip()

    raise RuntimeError(
        "MongoDB connection URI was not found."
    )


def get_database_name() -> str:

    keys = [
        "MONGODB_DB",
        "MONGO_DB",
        "DATABASE_NAME",
        "DB_NAME",
    ]

    for key in keys:
        value = os.getenv(key)

        if value and value.strip():
            return value.strip()

    return DEFAULT_DATABASE_NAME


def calculate_status(
    current: int,
    minimum: int,
    recommended: int,
) -> str:

    if current >= recommended:
        return "RECOMMENDED_TARGET_REACHED"

    if current >= minimum:
        return "MINIMUM_TARGET_REACHED"

    return "EXPANSION_REQUIRED"


def percentage(
    current: int,
    target: int,
) -> float:

    if target <= 0:
        return 100.0

    value = (current / target) * 100

    return round(
        min(value, 100.0),
        2,
    )


def main() -> None:

    separator()

    print(
        "EduPath - Step 152.6 "
        "Dataset Expansion Master Plan & Target Tracker"
    )

    separator()

    print()

    load_environment()

    try:
        mongodb_uri = get_mongodb_uri()
        database_name = get_database_name()

    except RuntimeError as error:

        print(
            f"Configuration error: {error}"
        )

        sys.exit(1)

    client: MongoClient | None = None

    try:

        print(
            "Connecting to MongoDB Atlas..."
        )

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

        database = client[database_name]

        existing_collections = set(
            database.list_collection_names()
        )

        results: list[dict[str, Any]] = []

        separator()

        print(
            "CURRENT DATASET VS EXPANSION TARGETS"
        )

        separator()

        print()

        for collection_name, target in TARGETS.items():

            if collection_name in existing_collections:

                current_count = (
                    database[collection_name]
                    .count_documents({})
                )

            else:
                current_count = 0

            minimum = target["minimum"]
            recommended = target["recommended"]

            minimum_remaining = max(
                minimum - current_count,
                0,
            )

            recommended_remaining = max(
                recommended - current_count,
                0,
            )

            status = calculate_status(
                current_count,
                minimum,
                recommended,
            )

            result = {
                "collection": collection_name,
                "current": current_count,
                "minimum_target": minimum,
                "recommended_target": recommended,
                "minimum_remaining": minimum_remaining,
                "recommended_remaining": recommended_remaining,
                "minimum_progress_percent": percentage(
                    current_count,
                    minimum,
                ),
                "recommended_progress_percent": percentage(
                    current_count,
                    recommended,
                ),
                "priority": target["priority"],
                "status": status,
            }

            results.append(result)

            print(
                f"{collection_name:<18} "
                f"Current: {current_count:<4} "
                f"Minimum: {minimum:<4} "
                f"Recommended: {recommended:<4} "
                f"Status: {status}"
            )

        # ----------------------------------------------------
        # Expansion priority
        # ----------------------------------------------------

        expansion_required = [
            item
            for item in results
            if item["status"]
            == "EXPANSION_REQUIRED"
        ]

        expansion_required.sort(
            key=lambda item: item["priority"]
        )

        print()
        separator()
        print(
            "DATA EXPANSION PRIORITY"
        )
        separator()

        print()

        if not expansion_required:

            print(
                "All minimum dataset targets "
                "have been reached."
            )

        else:

            for index, item in enumerate(
                expansion_required,
                start=1,
            ):

                print(
                    f"{index}. "
                    f"{item['collection']}"
                )

                print(
                    f"   Current             : "
                    f"{item['current']}"
                )

                print(
                    f"   Minimum target      : "
                    f"{item['minimum_target']}"
                )

                print(
                    f"   Records still needed: "
                    f"{item['minimum_remaining']}"
                )

                print()

        # ----------------------------------------------------
        # Recommended expansion plan
        # ----------------------------------------------------

        plan = [
            {
                "phase": "152-A",
                "dataset": "scholarships",
                "objective": (
                    "Expand verified scholarship records "
                    "with eligibility and application fields."
                ),
            },
            {
                "phase": "152-B",
                "dataset": "programs",
                "objective": (
                    "Expand academic programs across "
                    "currently supported universities and countries."
                ),
            },
            {
                "phase": "152-C",
                "dataset": "user_profiles",
                "objective": (
                    "Create diverse synthetic test profiles "
                    "for recommendation evaluation."
                ),
            },
            {
                "phase": "152-D",
                "dataset": "universities",
                "objective": (
                    "Increase university coverage only where "
                    "additional program depth is useful."
                ),
            },
        ]

        report = {
            "project": "EduPath Analytics",
            "step": "152.6",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "database": database_name,
            "mongodb_records_modified": False,
            "targets": TARGETS,
            "results": results,
            "expansion_plan": plan,
        }

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        with OUTPUT_JSON.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=2,
                ensure_ascii=False,
            )

        print()
        separator()

        print(
            "STEP 152.6 DATASET EXPANSION "
            "TRACKER: COMPLETED"
        )

        separator()

        print()

        print(
            f"JSON report:\n{OUTPUT_JSON}"
        )

        print()

        print(
            "MongoDB records modified: NO"
        )

    except PyMongoError as error:

        print()
        print(
            "MongoDB error:"
        )

        print(error)

        sys.exit(1)

    except Exception as error:

        print()
        print(
            f"Unexpected error: "
            f"{type(error).__name__}: {error}"
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