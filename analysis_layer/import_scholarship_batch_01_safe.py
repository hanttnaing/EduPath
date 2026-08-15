from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from pymongo import MongoClient


# ============================================================
# EduPath - Step 152.7C-4
# Safe MongoDB Scholarship Import
#
# DEFAULT:
#   DRY RUN ONLY
#
# ACTUAL WRITE:
#   python import_scholarship_batch_01_safe.py --apply
#
# SAFETY:
# - Never modifies Step 151.10 baseline
# - Creates live MongoDB backup before insert
# - Insert-only
# - Duplicate ID protection
# - Duplicate scholarship name protection
# - Country validation
# - Post-import count validation
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BASELINE_DIR = PROJECT_ROOT / "backups" / "baseline_151_10"
STAGING_DIR = PROJECT_ROOT / "data" / "staging"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"

BASELINE_SCHOLARSHIPS = BASELINE_DIR / "scholarships.json"
BASELINE_COUNTRIES = BASELINE_DIR / "countries.json"

PREIMPORT_CSV = (
    STAGING_DIR / "152_7c_batch_01_preimport.csv"
)

EXPECTED_EXISTING_COUNT = 12
EXPECTED_NEW_COUNT = 6
EXPECTED_FINAL_COUNT = 18

COLLECTION_NAME = "scholarships"


# ------------------------------------------------------------
# Environment loader
# ------------------------------------------------------------

def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as f:

        for line in f:
            line = line.strip()

            if (
                not line
                or line.startswith("#")
                or "=" not in line
            ):
                continue

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip()

            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in ("'", '"')
            ):
                value = value[1:-1]

            os.environ.setdefault(
                key,
                value,
            )


def load_project_environment() -> None:

    candidates = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "backend" / ".env",
        PROJECT_ROOT / "backend" / "app" / ".env",
    ]

    for path in candidates:
        load_env_file(path)


def first_env(*names: str) -> str | None:

    for name in names:
        value = os.getenv(name)

        if value and value.strip():
            return value.strip()

    return None


# ------------------------------------------------------------
# File utilities
# ------------------------------------------------------------

def load_json_records(path: Path) -> list[dict]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required file does not exist: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "items",
            "records",
            "data",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return value

    raise ValueError(
        f"Cannot detect JSON record list: {path}"
    )


def load_csv_records(
    path: Path,
) -> list[dict]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required CSV does not exist: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError(
                "CSV header could not be detected."
            )

        return list(reader)


def json_safe(value):

    if isinstance(value, dict):
        return {
            key: json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            json_safe(item)
            for item in value
        ]

    # ObjectId / datetime / etc.
    if type(value).__module__ != "builtins":
        return str(value)

    return value


def save_json(
    path: Path,
    data,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            json_safe(data),
            f,
            indent=2,
            ensure_ascii=False,
        )


# ------------------------------------------------------------
# Normalisation
# ------------------------------------------------------------

def clean_text(value) -> str:

    if value is None:
        return ""

    return str(value).strip()


def normalise_name(value) -> str:

    return re.sub(
        r"\s+",
        " ",
        clean_text(value).lower(),
    )


LIST_FIELDS = {
    "degree_levels",
    "eligible_nationalities",
    "fields_of_study",
    "required_documents",
}


def parse_list_value(value):

    text = clean_text(value)

    if not text:
        return []

    if text.startswith("["):

        try:
            result = json.loads(text)

            if isinstance(result, list):
                return result

        except Exception:
            pass

    if "|" in text:
        return [
            item.strip()
            for item in text.split("|")
            if item.strip()
        ]

    if ";" in text:
        return [
            item.strip()
            for item in text.split(";")
            if item.strip()
        ]

    return [text]


def convert_using_example(
    field: str,
    value,
    example,
):

    text = clean_text(value)

    if not text:
        return None

    if field in LIST_FIELDS:
        return parse_list_value(text)

    if isinstance(example, bool):

        return text.lower() in {
            "true",
            "1",
            "yes",
            "y",
        }

    if isinstance(example, int) and not isinstance(
        example,
        bool,
    ):

        try:
            return int(float(text))
        except Exception:
            return text

    if isinstance(example, float):

        try:
            return float(text)
        except Exception:
            return text

    if isinstance(example, list):
        return parse_list_value(text)

    return text


# ------------------------------------------------------------
# Production schema
# ------------------------------------------------------------

def build_schema_examples(
    baseline: list[dict],
) -> dict:

    examples = {}

    for record in baseline:

        for key, value in record.items():

            if key == "_id":
                continue

            if (
                key not in examples
                and value is not None
                and value != ""
            ):
                examples[key] = value

    return examples


def build_production_document(
    source: dict,
    schema_examples: dict,
) -> dict:

    document = {}

    # Only fields belonging to existing
    # production scholarship schema.
    for field, example in schema_examples.items():

        if field == "_id":
            continue

        if field not in source:
            continue

        converted = convert_using_example(
            field,
            source.get(field),
            example,
        )

        if converted is not None:
            document[field] = converted

    # Essential fields must always survive
    for essential in (
        "scholarship_id",
        "scholarship_name",
        "country_id",
    ):

        value = clean_text(
            source.get(essential)
        )

        if value:
            document[essential] = value

    return document


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually insert records into MongoDB",
    )

    args = parser.parse_args()

    apply_mode = args.apply

    print("=" * 92)
    print(
        "EduPath - Step 152.7C-4 "
        "Safe MongoDB Scholarship Import"
    )
    print("=" * 92)

    print()

    if apply_mode:
        print("MODE: APPLY")
        print(
            "MongoDB may be modified after "
            "all safety checks pass."
        )
    else:
        print("MODE: DRY RUN")
        print("MongoDB will NOT be modified.")

    print()

    # --------------------------------------------------------
    # Load environment
    # --------------------------------------------------------

    load_project_environment()

    mongo_uri = first_env(
        "MONGODB_URI",
        "MONGO_URI",
        "MONGO_URL",
        "DATABASE_URL",
    )

    db_name = first_env(
        "MONGODB_DB",
        "MONGO_DB",
        "DB_NAME",
        "DATABASE_NAME",
    )

    if not mongo_uri:
        raise RuntimeError(
            "MongoDB URI was not found in project "
            "environment variables.\n"
            "Expected one of: MONGODB_URI, "
            "MONGO_URI, MONGO_URL, DATABASE_URL"
        )

    # --------------------------------------------------------
    # Load trusted project files
    # --------------------------------------------------------

    baseline = load_json_records(
        BASELINE_SCHOLARSHIPS
    )

    countries = load_json_records(
        BASELINE_COUNTRIES
    )

    preimport = load_csv_records(
        PREIMPORT_CSV
    )

    print("=" * 92)
    print("SOURCE DATA")
    print("=" * 92)

    print(
        f"Step 151.10 baseline : {len(baseline)}"
    )

    print(
        f"Pre-import Batch 01  : {len(preimport)}"
    )

    if len(baseline) != EXPECTED_EXISTING_COUNT:
        raise RuntimeError(
            "Step 151.10 scholarship baseline "
            f"should contain {EXPECTED_EXISTING_COUNT} "
            f"records, but found {len(baseline)}."
        )

    if len(preimport) != EXPECTED_NEW_COUNT:
        raise RuntimeError(
            "Batch 01 should contain "
            f"{EXPECTED_NEW_COUNT} records, "
            f"but found {len(preimport)}."
        )

    # --------------------------------------------------------
    # Country validation
    # --------------------------------------------------------

    valid_country_ids = {
        clean_text(row.get("country_id"))
        for row in countries
        if clean_text(row.get("country_id"))
    }

    for row in preimport:

        country_id = clean_text(
            row.get("country_id")
        )

        if country_id not in valid_country_ids:

            raise RuntimeError(
                "Invalid country_id detected: "
                f"{country_id}"
            )

    print("Country validation    : PASS")

    # --------------------------------------------------------
    # Prepare production documents
    # --------------------------------------------------------

    schema_examples = build_schema_examples(
        baseline
    )

    new_documents = [
        build_production_document(
            row,
            schema_examples,
        )
        for row in preimport
    ]

    for index, doc in enumerate(
        new_documents,
        start=1,
    ):

        for field in (
            "scholarship_id",
            "scholarship_name",
            "country_id",
        ):

            if not clean_text(
                doc.get(field)
            ):
                raise RuntimeError(
                    f"Record {index} is missing "
                    f"required field: {field}"
                )

    # --------------------------------------------------------
    # Connect MongoDB
    # --------------------------------------------------------

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000,
    )

    client.admin.command("ping")

    print("MongoDB connection    : PASS")

    if db_name:
        db = client[db_name]

    else:
        try:
            db = client.get_default_database()

        except Exception as exc:

            raise RuntimeError(
                "Database name could not be detected. "
                "Add DB_NAME or MONGODB_DB "
                "to your .env file."
            ) from exc

    collection = db[COLLECTION_NAME]

    live_count = collection.count_documents({})

    print(
        f"Live scholarship count: {live_count}"
    )

    # --------------------------------------------------------
    # Critical baseline lock
    # --------------------------------------------------------

    if live_count != EXPECTED_EXISTING_COUNT:

        raise RuntimeError(
            "\nSAFETY STOP\n"
            "Live MongoDB scholarship count does "
            "not match Step 151.10 baseline.\n"
            f"Expected: {EXPECTED_EXISTING_COUNT}\n"
            f"Actual:   {live_count}\n"
            "Nothing was inserted."
        )

    print("Baseline count lock    : PASS")

    # --------------------------------------------------------
    # Duplicate checks
    # --------------------------------------------------------

    live_records = list(
        collection.find({})
    )

    live_ids = {
        clean_text(
            row.get("scholarship_id")
        )
        for row in live_records
        if clean_text(
            row.get("scholarship_id")
        )
    }

    live_names = {
        normalise_name(
            row.get("scholarship_name")
        )
        for row in live_records
        if normalise_name(
            row.get("scholarship_name")
        )
    }

    new_ids = []
    new_names = []

    for doc in new_documents:

        scholarship_id = clean_text(
            doc["scholarship_id"]
        )

        scholarship_name = clean_text(
            doc["scholarship_name"]
        )

        if scholarship_id in live_ids:
            raise RuntimeError(
                "Duplicate scholarship_id found: "
                f"{scholarship_id}"
            )

        if (
            normalise_name(scholarship_name)
            in live_names
        ):
            raise RuntimeError(
                "Duplicate scholarship_name found: "
                f"{scholarship_name}"
            )

        if scholarship_id in new_ids:
            raise RuntimeError(
                "Duplicate ID inside Batch 01: "
                f"{scholarship_id}"
            )

        if (
            normalise_name(scholarship_name)
            in new_names
        ):
            raise RuntimeError(
                "Duplicate name inside Batch 01: "
                f"{scholarship_name}"
            )

        new_ids.append(scholarship_id)

        new_names.append(
            normalise_name(
                scholarship_name
            )
        )

    print("Duplicate ID check     : PASS")
    print("Duplicate name check   : PASS")

    print()
    print("=" * 92)
    print("RECORDS READY FOR INSERT")
    print("=" * 92)

    for index, doc in enumerate(
        new_documents,
        start=1,
    ):

        print(
            f"{index}. "
            f"{doc['scholarship_id']} | "
            f"{doc['country_id']} | "
            f"{doc['scholarship_name']}"
        )

    print()
    print(
        f"Existing : {live_count}"
    )

    print(
        f"New      : {len(new_documents)}"
    )

    print(
        f"Projected: "
        f"{live_count + len(new_documents)}"
    )

    # --------------------------------------------------------
    # DRY RUN STOP
    # --------------------------------------------------------

    if not apply_mode:

        print()
        print("=" * 92)
        print(
            "STEP 152.7C-4 DRY RUN: PASS"
        )
        print("=" * 92)

        print(
            "MongoDB modified: NO"
        )

        print()
        print(
            "Next command, only after reviewing "
            "this output:"
        )

        print(
            ".\\.venv\\Scripts\\python.exe "
            ".\\analysis_layer\\"
            "import_scholarship_batch_01_safe.py "
            "--apply"
        )

        client.close()
        return

    # --------------------------------------------------------
    # APPLY MODE - backup first
    # --------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_dir = (
        PROJECT_ROOT
        / "backups"
        / f"pre_152_7c4_{timestamp}"
    )

    backup_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    live_backup_path = (
        backup_dir
        / "scholarships_before_import.json"
    )

    rollback_path = (
        backup_dir
        / "rollback_inserted_ids.json"
    )

    report_path = (
        ANALYSIS_DIR
        / "152_7c4_mongodb_import_report.json"
    )

    save_json(
        live_backup_path,
        live_records,
    )

    save_json(
        rollback_path,
        {
            "step": "152.7C-4",
            "created_at": (
                datetime.now().isoformat()
            ),
            "inserted_scholarship_ids": (
                new_ids
            ),
        },
    )

    print()
    print("=" * 92)
    print("LIVE DATABASE BACKUP")
    print("=" * 92)

    print(
        f"Backup directory : {backup_dir}"
    )

    print(
        f"Backup records   : "
        f"{len(live_records)}"
    )

    print("Backup status    : PASS")

    # --------------------------------------------------------
    # INSERT ONLY
    # --------------------------------------------------------

    print()
    print("=" * 92)
    print("MONGODB INSERT")
    print("=" * 92)

    try:

        result = collection.insert_many(
            new_documents,
            ordered=True,
        )

        inserted_count = len(
            result.inserted_ids
        )

    except Exception:

        # Safety rollback:
        # only delete IDs belonging to this new batch.
        collection.delete_many(
            {
                "scholarship_id": {
                    "$in": new_ids
                }
            }
        )

        client.close()

        raise RuntimeError(
            "MongoDB insert failed. "
            "Automatic rollback attempted."
        )

    print(
        f"Inserted records: {inserted_count}"
    )

    if inserted_count != EXPECTED_NEW_COUNT:

        collection.delete_many(
            {
                "scholarship_id": {
                    "$in": new_ids
                }
            }
        )

        client.close()

        raise RuntimeError(
            "Unexpected inserted record count. "
            "Automatic rollback completed."
        )

    # --------------------------------------------------------
    # POST IMPORT VALIDATION
    # --------------------------------------------------------

    final_count = collection.count_documents(
        {}
    )

    found_new_count = collection.count_documents(
        {
            "scholarship_id": {
                "$in": new_ids
            }
        }
    )

    print()
    print("=" * 92)
    print("POST-IMPORT VALIDATION")
    print("=" * 92)

    print(
        f"Final MongoDB count : "
        f"{final_count}"
    )

    print(
        f"New IDs found       : "
        f"{found_new_count}"
    )

    if (
        final_count != EXPECTED_FINAL_COUNT
        or found_new_count
        != EXPECTED_NEW_COUNT
    ):

        print(
            "Post-validation failed."
        )

        print(
            "Rolling back Batch 01..."
        )

        collection.delete_many(
            {
                "scholarship_id": {
                    "$in": new_ids
                }
            }
        )

        rolled_back_count = (
            collection.count_documents({})
        )

        print(
            f"Count after rollback: "
            f"{rolled_back_count}"
        )

        client.close()

        raise RuntimeError(
            "Post-import validation failed. "
            "Batch 01 was rolled back."
        )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    report = {
        "step": "152.7C-4",
        "status": "PASS",
        "timestamp": (
            datetime.now().isoformat()
        ),
        "mongodb_modified": True,
        "collection": COLLECTION_NAME,
        "before_count": live_count,
        "inserted_count": inserted_count,
        "after_count": final_count,
        "inserted_ids": new_ids,
        "backup_file": str(
            live_backup_path
        ),
        "rollback_file": str(
            rollback_path
        ),
    }

    save_json(
        report_path,
        report,
    )

    client.close()

    print("Count validation    : PASS")
    print("Inserted ID check   : PASS")

    print()
    print("=" * 92)
    print(
        "STEP 152.7C-4 SAFE MONGODB IMPORT: PASS"
    )
    print("=" * 92)

    print()
    print(
        f"Before : {live_count}"
    )

    print(
        f"Added  : {inserted_count}"
    )

    print(
        f"After  : {final_count}"
    )

    print()
    print(
        f"Backup : {live_backup_path}"
    )

    print(
        f"Report : {report_path}"
    )

    print()
    print(
        "Next step: Step 152.7C-5 "
        "Post-Import Dataset Synchronisation "
        "& API Validation."
    )


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print()
        print("=" * 92)
        print("STEP 152.7C-4: FAILED")
        print("=" * 92)

        print(exc)

        sys.exit(1)