import json
import os
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


PROJECT_ROOT = Path(".").resolve()

ENV_PATH = PROJECT_ROOT / ".env"

JSON_PATH = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "programs.json"
)


EXPECTED_TOTAL = 336

EXPECTED_PREFIX_COUNTS = {
    "prog_jp": 36,
    "prog_bn": 12,
    "prog_la": 15,
    "prog_sg": 18,
    "prog_tl": 18,
    "prog_kh": 39,
    "prog_mm": 33,
    "prog_my": 120,
    "prog_hk": 45,
}


def clean(value):
    return str(value or "").strip()


def prefix(program_id):

    parts = program_id.split("_")

    if len(parts) >= 3:
        return "_".join(parts[:2])

    return "unknown"


print("=" * 105)
print(
    "STEP 169.3D - MONGODB "
    "PROGRAMME PRE-LOAD SAFETY AUDIT"
)
print("=" * 105)


# -------------------------------------------------
# 1. Local JSON
# -------------------------------------------------

if not JSON_PATH.exists():
    raise FileNotFoundError(
        f"programs.json not found: {JSON_PATH}"
    )


with JSON_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    records = json.load(file)


if not isinstance(records, list):
    raise ValueError(
        "programs.json must contain a list."
    )


program_ids = [
    clean(row.get("program_id"))
    for row in records
]


if any(not program_id for program_id in program_ids):
    raise ValueError(
        "One or more local programme records "
        "lack program_id."
    )


duplicate_count = (
    len(program_ids)
    - len(set(program_ids))
)


prefix_counts = Counter(
    prefix(program_id)
    for program_id in program_ids
)


hk_records = [
    row
    for row in records
    if clean(
        row.get("program_id")
    ).startswith("prog_hk_")
]


intl_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in hk_records
)


print()
print("LOCAL programs.json")
print("-" * 105)

print(
    "Rows                              :",
    len(records),
)

print(
    "Duplicate IDs                     :",
    duplicate_count,
)

print(
    "Prefix counts                     :",
    dict(prefix_counts),
)

print(
    "Hong Kong rows                    :",
    len(hk_records),
)

print(
    "HK international statuses         :",
    dict(intl_statuses),
)


errors = []


if len(records) != EXPECTED_TOTAL:
    errors.append(
        "Local programs.json must contain 336 rows."
    )

if duplicate_count != 0:
    errors.append(
        "Local programs.json contains duplicate IDs."
    )

if dict(prefix_counts) != EXPECTED_PREFIX_COUNTS:
    errors.append(
        "Local programme prefix counts mismatch."
    )

if len(hk_records) != 45:
    errors.append(
        "Expected exactly 45 Hong Kong records."
    )

if intl_statuses != Counter({
    "verified_yes": 39,
    "unknown": 6,
}):
    errors.append(
        "Hong Kong international eligibility "
        "counts mismatch."
    )


# -------------------------------------------------
# 2. MongoDB connection
# -------------------------------------------------

if not ENV_PATH.exists():
    raise FileNotFoundError(
        f".env not found: {ENV_PATH}"
    )


load_dotenv(
    ENV_PATH
)


mongo_uri = os.getenv(
    "MONGODB_URI"
)


database_name = (
    os.getenv("MONGODB_DB_NAME")
    or os.getenv("MONGODB_DATABASE")
    or "edupath_db"
)


programs_collection_name = (
    os.getenv("PROGRAMS_COLLECTION")
    or "programs"
)


if not mongo_uri:
    raise RuntimeError(
        "MONGODB_URI missing from .env."
    )


client = MongoClient(
    mongo_uri,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=10000,
)


try:

    client.admin.command(
        "ping"
    )

    db = client[
        database_name
    ]

    collection = db[
        programs_collection_name
    ]


    mongo_total = (
        collection.count_documents({})
    )


    mongo_hk = (
        collection.count_documents(
            {
                "program_id": {
                    "$regex": "^prog_hk_"
                }
            }
        )
    )


    mongo_ids = {
        clean(doc.get("program_id"))
        for doc in collection.find(
            {},
            {
                "_id": 0,
                "program_id": 1,
            },
        )
        if clean(doc.get("program_id"))
    }


    local_ids = set(
        program_ids
    )


    mongo_only = sorted(
        mongo_ids - local_ids
    )

    local_only = sorted(
        local_ids - mongo_ids
    )


    print()
    print("CURRENT MONGODB STATE")
    print("-" * 105)

    print(
        "Database                          :",
        database_name,
    )

    print(
        "Collection                        :",
        programs_collection_name,
    )

    print(
        "Current MongoDB programme docs    :",
        mongo_total,
    )

    print(
        "Current MongoDB Hong Kong docs    :",
        mongo_hk,
    )

    print(
        "Local IDs not yet in MongoDB      :",
        len(local_only),
    )

    print(
        "MongoDB-only IDs                  :",
        len(mongo_only),
    )


    if local_only:

        local_only_prefixes = Counter(
            prefix(program_id)
            for program_id in local_only
        )

        print(
            "Local-only prefix counts         :",
            dict(local_only_prefixes),
        )


    if mongo_only:

        print()
        print(
            "MongoDB-only IDs:"
        )

        for program_id in mongo_only[:30]:
            print(
                " ",
                program_id,
            )


finally:

    client.close()


# -------------------------------------------------
# 3. Gate
# -------------------------------------------------

if mongo_only:

    errors.append(
        "MongoDB contains programme IDs not "
        "present in local programs.json."
    )


print()
print("=" * 105)


if errors:

    print(
        "STEP 169.3D MONGODB "
        "PRE-LOAD SAFETY AUDIT: HOLD"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    print()
    print(
        "DO NOT RUN THE MONGODB LOADER."
    )

    raise SystemExit(1)


print(
    "STEP 169.3D MONGODB "
    "PRE-LOAD SAFETY AUDIT: PASS"
)

print(
    "LOCAL 336-PROGRAM DATASET IS "
    "READY FOR MONGODB SYNCHRONIZATION"
)

print(
    "NO MONGODB RECORDS WERE MODIFIED"
)

print("=" * 105)
