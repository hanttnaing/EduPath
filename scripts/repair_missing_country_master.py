from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

SCRIPTS_DIRECTORY = (
    PROJECT_ROOT
    / "scripts"
)

BACKUP_DIRECTORY = (
    PROJECT_ROOT
    / "planning"
    / "backups"
)

ANALYSIS_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "analysis"
)


if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS_DIRECTORY),
    )


# =========================================================
# EDUPATH DATABASE CONFIG
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
# EXPECTED COUNTRY MASTER RECORDS
# =========================================================
#
# These IDs already exist in university records.
# We are NOT changing university records.
#
# We are restoring the missing referenced country records.
#
# =========================================================

EXPECTED_COUNTRIES: dict[str, dict[str, Any]] = {

    "country_kr": {
        "country_id": "country_kr",
        "country_name": "South Korea",
        "region": "East Asia",
    },

    "country_tw": {
        "country_id": "country_tw",
        "country_name": "Taiwan",
        "region": "East Asia",
    },

    "country_hk": {
        "country_id": "country_hk",
        "country_name": "Hong Kong",
        "region": "East Asia",
    },

    "country_th": {
        "country_id": "country_th",
        "country_name": "Thailand",
        "region": "Southeast Asia",
    },
}


# =========================================================
# HELPERS
# =========================================================

def clean(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(
        value
    ).strip()


def now_iso() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def load_documents(
    database: Any,
    collection_name: str,
) -> list[dict[str, Any]]:

    return list(
        database[
            collection_name
        ].find(
            {},
            {
                "_id": 0,
            },
        )
    )


# =========================================================
# FIND REFERENCED COUNTRY IDS
# =========================================================

def get_referenced_country_ids(
    universities: list[dict[str, Any]],
) -> set[str]:

    referenced: set[str] = set()

    for university in universities:

        country_id = clean(
            university.get(
                "country_id"
            )
        )

        if country_id:
            referenced.add(
                country_id
            )

    return referenced


# =========================================================
# FIND EXISTING COUNTRY IDS
# =========================================================

def get_existing_country_ids(
    countries: list[dict[str, Any]],
) -> set[str]:

    existing: set[str] = set()

    for country in countries:

        country_id = clean(
            country.get(
                "country_id"
            )
        )

        if country_id:
            existing.add(
                country_id
            )

    return existing


# =========================================================
# CREATE BACKUP
# =========================================================

def create_backup(
    countries: list[dict[str, Any]],
) -> Path:

    BACKUP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = (
        BACKUP_DIRECTORY
        / f"countries_before_relationship_repair_{timestamp}.json"
    )

    backup_payload = {
        "created_at": now_iso(),
        "purpose": (
            "Backup countries collection before "
            "Step 151.1C relationship repair"
        ),
        "record_count": len(
            countries
        ),
        "records": countries,
    }

    with backup_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            backup_payload,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    return backup_path


# =========================================================
# WRITE DIAGNOSTIC REPORT
# =========================================================

def write_report(
    mode: str,
    referenced_ids: set[str],
    existing_ids: set[str],
    missing_ids: set[str],
    inserted_ids: list[str],
    status: str,
) -> Path:

    ANALYSIS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        ANALYSIS_DIRECTORY
        / "151_1c_country_master_relationship_repair.json"
    )

    payload = {

        "project":
            "EduPath Analytics",

        "step":
            "151.1C",

        "generated_at":
            now_iso(),

        "mode":
            mode,

        "status":
            status,

        "database":
            DATABASE_NAME,

        "referenced_country_ids":
            sorted(
                referenced_ids
            ),

        "existing_country_ids_before":
            sorted(
                existing_ids
            ),

        "missing_country_ids":
            sorted(
                missing_ids
            ),

        "inserted_country_ids":
            inserted_ids,

        "mongodb_modified":
            mode == "apply"
            and bool(
                inserted_ids
            ),
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return output_path


# =========================================================
# VERIFY AFTER INSERT
# =========================================================

def verify_relationships(
    database: Any,
) -> tuple[
    bool,
    set[str],
]:

    countries = load_documents(
        database,
        "countries",
    )

    universities = load_documents(
        database,
        "universities",
    )

    existing_country_ids = (
        get_existing_country_ids(
            countries
        )
    )

    referenced_country_ids = (
        get_referenced_country_ids(
            universities
        )
    )

    remaining_missing = (
        referenced_country_ids
        - existing_country_ids
    )

    return (
        len(
            remaining_missing
        )
        == 0,

        remaining_missing,
    )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "EduPath Step 151.1C "
            "Country Master Relationship Repair"
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Actually insert verified missing country master records. "
            "Without this flag the script performs a dry run only."
        ),
    )

    args = parser.parse_args()

    mode = (
        "apply"
        if args.apply
        else "dry-run"
    )

    print(
        "=" * 100
    )

    print(
        "EduPath - Step 151.1C "
        "Country Master Relationship Repair"
    )

    print(
        "=" * 100
    )

    print()

    print(
        f"Mode: {mode.upper()}"
    )

    print()

    if not MONGODB_URI:

        raise RuntimeError(
            "MONGODB_URI is unavailable."
        )

    if not DATABASE_NAME:

        raise RuntimeError(
            "DATABASE_NAME is unavailable."
        )

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi(
            "1"
        ),
        serverSelectionTimeoutMS=10000,
    )

    try:

        print(
            "Connecting to MongoDB Atlas..."
        )

        client.admin.command(
            "ping"
        )

        print(
            "MongoDB Atlas connection: SUCCESS"
        )

        print(
            f"Database: {DATABASE_NAME}"
        )

        print()

        database = client[
            DATABASE_NAME
        ]

        countries_collection = database[
            "countries"
        ]

        # =================================================
        # LOAD CURRENT MASTER DATA
        # =================================================

        countries = load_documents(
            database,
            "countries",
        )

        universities = load_documents(
            database,
            "universities",
        )

        print(
            "Current records:"
        )

        print(
            f"Countries   : {len(countries)}"
        )

        print(
            f"Universities: {len(universities)}"
        )

        print()

        # =================================================
        # FIND RELATIONSHIP GAP
        # =================================================

        existing_country_ids = (
            get_existing_country_ids(
                countries
            )
        )

        referenced_country_ids = (
            get_referenced_country_ids(
                universities
            )
        )

        missing_country_ids = (
            referenced_country_ids
            - existing_country_ids
        )

        print(
            "=" * 100
        )

        print(
            "COUNTRY RELATIONSHIP GAP"
        )

        print(
            "=" * 100
        )

        print(
            "Existing country IDs:"
        )

        for country_id in sorted(
            existing_country_ids
        ):

            print(
                f"  - {country_id}"
            )

        print()

        print(
            "Country IDs referenced by universities:"
        )

        for country_id in sorted(
            referenced_country_ids
        ):

            print(
                f"  - {country_id}"
            )

        print()

        print(
            "Missing country master IDs:"
        )

        if missing_country_ids:

            for country_id in sorted(
                missing_country_ids
            ):

                print(
                    f"  - {country_id}"
                )

        else:

            print(
                "  None"
            )

        print()

        # =================================================
        # SAFETY VALIDATION
        # =================================================

        expected_missing_ids = set(
            EXPECTED_COUNTRIES.keys()
        )

        unexpected_missing_ids = (
            missing_country_ids
            - expected_missing_ids
        )

        if unexpected_missing_ids:

            print(
                "=" * 100
            )

            print(
                "SAFETY CHECK: FAILED"
            )

            print(
                "=" * 100
            )

            print(
                "Unexpected missing country IDs were detected:"
            )

            for country_id in sorted(
                unexpected_missing_ids
            ):

                print(
                    f"  - {country_id}"
                )

            print()

            print(
                "No database changes will be made."
            )

            report_path = write_report(
                mode=mode,
                referenced_ids=
                    referenced_country_ids,
                existing_ids=
                    existing_country_ids,
                missing_ids=
                    missing_country_ids,
                inserted_ids=[],
                status=
                    "ABORTED_UNEXPECTED_COUNTRY_IDS",
            )

            print(
                f"Report: {report_path}"
            )

            return

        # =================================================
        # SHOW PROPOSED INSERTS
        # =================================================

        proposed_records: list[
            dict[str, Any]
        ] = []

        for country_id in sorted(
            missing_country_ids
        ):

            proposed_records.append(
                EXPECTED_COUNTRIES[
                    country_id
                ].copy()
            )

        print(
            "=" * 100
        )

        print(
            "PROPOSED COUNTRY MASTER RECORDS"
        )

        print(
            "=" * 100
        )

        if proposed_records:

            for record in proposed_records:

                print(
                    f"{record['country_id']} | "
                    f"{record['country_name']} | "
                    f"{record['region']}"
                )

        else:

            print(
                "No records need to be inserted."
            )

        print()

        # =================================================
        # DRY RUN
        # =================================================

        if not args.apply:

            print(
                "=" * 100
            )

            print(
                "DRY RUN VALIDATION: PASSED"
            )

            print(
                "=" * 100
            )

            print()

            print(
                f"Missing master records: "
                f"{len(missing_country_ids)}"
            )

            print(
                f"Records ready to insert: "
                f"{len(proposed_records)}"
            )

            print()

            print(
                "NO DATABASE RECORDS WERE MODIFIED."
            )

            print()

            print(
                "If the proposed records above are correct, run:"
            )

            print()

            print(
                "python scripts\\repair_missing_country_master.py --apply"
            )

            report_path = write_report(
                mode=
                    "dry-run",

                referenced_ids=
                    referenced_country_ids,

                existing_ids=
                    existing_country_ids,

                missing_ids=
                    missing_country_ids,

                inserted_ids=[],

                status=
                    "DRY_RUN_PASSED",
            )

            print()

            print(
                f"Report: {report_path}"
            )

            return

        # =================================================
        # APPLY MODE
        # =================================================

        print(
            "=" * 100
        )

        print(
            "CONTROLLED APPLY MODE"
        )

        print(
            "=" * 100
        )

        print()

        # -------------------------------------------------
        # Backup first
        # -------------------------------------------------

        backup_path = create_backup(
            countries
        )

        print(
            "Backup created:"
        )

        print(
            backup_path
        )

        print()

        inserted_ids: list[str] = []

        # -------------------------------------------------
        # Insert only genuinely absent master records
        # -------------------------------------------------

        for record in proposed_records:

            country_id = record[
                "country_id"
            ]

            already_exists = (
                countries_collection.find_one(
                    {
                        "country_id":
                            country_id
                    }
                )
            )

            if already_exists:

                print(
                    f"SKIPPED existing: {country_id}"
                )

                continue

            record_to_insert = (
                record.copy()
            )

            record_to_insert[
                "created_at"
            ] = datetime.now(
                timezone.utc
            )

            record_to_insert[
                "last_verified_at"
            ] = datetime.now(
                timezone.utc
            )

            countries_collection.insert_one(
                record_to_insert
            )

            inserted_ids.append(
                country_id
            )

            print(
                f"INSERTED: "
                f"{country_id} "
                f"({record['country_name']})"
            )

        print()

        # =================================================
        # POST-WRITE VERIFICATION
        # =================================================

        verification_passed, remaining_missing = (
            verify_relationships(
                database
            )
        )

        print(
            "=" * 100
        )

        print(
            "POST-WRITE RELATIONSHIP VERIFICATION"
        )

        print(
            "=" * 100
        )

        print(
            f"Inserted records: "
            f"{len(inserted_ids)}"
        )

        print(
            f"Inserted IDs: "
            f"{', '.join(inserted_ids) if inserted_ids else 'None'}"
        )

        print()

        if verification_passed:

            print(
                "Country relationship validation: PASSED"
            )

            print(
                "Remaining missing country IDs: 0"
            )

            final_status = (
                "APPLY_PASSED"
            )

        else:

            print(
                "Country relationship validation: FAILED"
            )

            print(
                "Remaining missing country IDs:"
            )

            for country_id in sorted(
                remaining_missing
            ):

                print(
                    f"  - {country_id}"
                )

            final_status = (
                "APPLY_REVIEW_REQUIRED"
            )

        # =================================================
        # REPORT
        # =================================================

        report_path = write_report(
            mode=
                "apply",

            referenced_ids=
                referenced_country_ids,

            existing_ids=
                existing_country_ids,

            missing_ids=
                missing_country_ids,

            inserted_ids=
                inserted_ids,

            status=
                final_status,
        )

        print()

        print(
            "=" * 100
        )

        print(
            "STEP 151.1C COUNTRY MASTER REPAIR: COMPLETED"
        )

        print(
            "=" * 100
        )

        print(
            f"Status: {final_status}"
        )

        print()

        print(
            f"Backup: {backup_path}"
        )

        print(
            f"Report: {report_path}"
        )

        print()

        print(
            "Next validation command:"
        )

        print(
            "python analysis_layer\\relationship_diagnostic.py"
        )

        print(
            "=" * 100
        )

    except PyMongoError as error:

        raise RuntimeError(
            "MongoDB country master repair failed."
        ) from error

    finally:

        client.close()

        print(
            "MongoDB connection closed safely."
        )


if __name__ == "__main__":
    main()