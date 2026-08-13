from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = PROJECT_ROOT / "scripts"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIRECTORY))


# =========================================================
# DATABASE CONFIG
# =========================================================

try:
    from recommend_scholarships_final import (
        MONGODB_URI,
        DATABASE_NAME,
    )

except ImportError as error:
    raise RuntimeError(
        "Could not import MongoDB configuration from "
        "scripts/recommend_scholarships_final.py"
    ) from error


# =========================================================
# HELPERS
# =========================================================

def clean(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def looks_like_status_field(key: str) -> bool:
    key_lower = key.lower()

    keywords = (
        "status",
        "state",
        "cycle",
        "fresh",
        "open",
        "deadline",
    )

    return any(
        keyword in key_lower
        for keyword in keywords
    )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print("=" * 100)
    print(
        "EduPath - Step 151.2A "
        "Scholarship Status Field Diagnostic"
    )
    print("=" * 100)
    print()

    print("Connecting to MongoDB Atlas...")

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:

        client.admin.command("ping")

        print("MongoDB Atlas connection: SUCCESS")
        print(f"Database: {DATABASE_NAME}")
        print()

        database = client[DATABASE_NAME]

        scholarships = list(
            database["scholarships"].find(
                {},
                {
                    "_id": 0,
                },
            )
        )

        print("=" * 100)
        print("SCHOLARSHIP RECORD COUNT")
        print("=" * 100)

        print(
            f"Scholarships loaded: "
            f"{len(scholarships)}"
        )

        print()

        if not scholarships:
            print("No scholarship records found.")
            return

        # =================================================
        # ALL FIELD NAMES
        # =================================================

        all_keys: set[str] = set()

        for scholarship in scholarships:
            all_keys.update(
                scholarship.keys()
            )

        print("=" * 100)
        print("STATUS-RELATED FIELD NAMES FOUND")
        print("=" * 100)

        status_related_keys = sorted(
            key
            for key in all_keys
            if looks_like_status_field(key)
        )

        if status_related_keys:

            for key in status_related_keys:
                print(f"- {key}")

        else:
            print(
                "No obvious status-related "
                "field names were detected."
            )

        print()

        # =================================================
        # VALUES FOR STATUS-RELATED FIELDS
        # =================================================

        print("=" * 100)
        print("STATUS-RELATED VALUES")
        print("=" * 100)

        for key in status_related_keys:

            values: dict[str, int] = {}

            for scholarship in scholarships:

                raw_value = scholarship.get(key)

                if isinstance(raw_value, list):

                    value = ", ".join(
                        clean(item)
                        for item in raw_value
                        if clean(item)
                    )

                else:
                    value = clean(raw_value)

                if not value:
                    value = "<EMPTY>"

                values[value] = (
                    values.get(value, 0) + 1
                )

            print()
            print(f"[{key}]")

            for value, count in sorted(
                values.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            ):
                print(
                    f"  {value:<40} "
                    f"{count:>3} record(s)"
                )

        print()

        # =================================================
        # FIRST 3 RECORDS
        # =================================================

        print("=" * 100)
        print("FIRST 3 SCHOLARSHIP RECORDS")
        print("=" * 100)

        for index, scholarship in enumerate(
            scholarships[:3],
            start=1,
        ):

            print()
            print(
                f"Scholarship #{index}"
            )

            print("-" * 100)

            scholarship_name = (
                clean(
                    scholarship.get(
                        "scholarship_name"
                    )
                )
                or clean(
                    scholarship.get(
                        "name"
                    )
                )
                or "Unknown Scholarship"
            )

            print(
                f"Name: {scholarship_name}"
            )

            for key in sorted(
                scholarship.keys()
            ):

                if looks_like_status_field(key):

                    print(
                        f"{key}: "
                        f"{scholarship.get(key)!r}"
                    )

        print()
        print("=" * 100)
        print(
            "STEP 151.2A DIAGNOSTIC: COMPLETED"
        )
        print("=" * 100)

        print()
        print(
            "MongoDB records modified: NO"
        )

    except PyMongoError as error:

        raise RuntimeError(
            "MongoDB scholarship status "
            "diagnostic failed."
        ) from error

    finally:

        client.close()

        print()
        print(
            "MongoDB connection closed safely."
        )


if __name__ == "__main__":
    main()