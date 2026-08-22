import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.server_api import ServerApi


load_dotenv(Path(".env"))


URI = os.getenv("MONGODB_URI")

DB_NAME = (
    os.getenv("MONGODB_DB_NAME")
    or os.getenv("MONGODB_DATABASE")
    or "edupath_db"
)

COLLECTION_NAME = (
    os.getenv("PROGRAMS_COLLECTION")
    or "programs"
)

FIELD = "international_applicants_last_verified_at"

BACKUP_DIR = Path(
    "data/backups/step_169_3f"
)


def clean(value):
    return str(value or "").strip()


def parse_date(value):

    value = clean(value)

    if not value:
        raise ValueError(
            "Blank international verification date."
        )

    # Date only, e.g. 2026-08-21
    if (
        len(value) == 10
        and value[4] == "-"
        and value[7] == "-"
    ):
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        )

    # ISO datetime fallback
    parsed = datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )

    if parsed.tzinfo is not None:
        parsed = (
            parsed
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

    return parsed


print("=" * 100)
print(
    "STEP 169.3F.2 - HONG KONG "
    "INTERNATIONAL DATE TYPE REPAIR"
)
print("=" * 100)


if not URI:
    raise RuntimeError(
        "MONGODB_URI is missing from .env."
    )


client = MongoClient(
    URI,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=10000,
)


try:

    client.admin.command("ping")

    collection = client[
        DB_NAME
    ][
        COLLECTION_NAME
    ]


    hk_docs = list(
        collection.find(
            {
                "program_id": {
                    "$regex": "^prog_hk_"
                }
            },
            {
                "_id": 0,
                "program_id": 1,
                FIELD: 1,
            },
        )
    )


    if len(hk_docs) != 45:
        raise ValueError(
            f"Expected 45 HK documents, "
            f"found {len(hk_docs)}."
        )


    before_types = Counter(
        type(
            doc.get(FIELD)
        ).__name__
        for doc in hk_docs
    )


    print(
        "Hong Kong documents             :",
        len(hk_docs),
    )

    print(
        "Date types before               :",
        dict(before_types),
    )


    converted = {}


    for doc in hk_docs:

        program_id = clean(
            doc["program_id"]
        )

        value = doc.get(FIELD)


        if isinstance(value, datetime):

            converted[
                program_id
            ] = value

        elif isinstance(value, str):

            converted[
                program_id
            ] = parse_date(
                value
            )

        else:

            raise ValueError(
                f"{program_id}: unexpected "
                f"{FIELD} type "
                f"{type(value).__name__}"
            )


    # --------------------------------------------
    # Backup original values before DB write
    # --------------------------------------------

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


    backup_path = BACKUP_DIR / (
        "hong_kong_international_dates_"
        f"before_type_repair_{timestamp}.json"
    )


    backup_rows = []


    for doc in hk_docs:

        value = doc.get(FIELD)

        backup_rows.append(
            {
                "program_id": clean(
                    doc["program_id"]
                ),
                "original_type": (
                    type(value).__name__
                ),
                "original_value": (
                    value.isoformat()
                    if isinstance(
                        value,
                        datetime,
                    )
                    else value
                ),
            }
        )


    with backup_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            backup_rows,
            file,
            ensure_ascii=False,
            indent=2,
        )


    print(
        "Backup                          :",
        backup_path,
    )


    # --------------------------------------------
    # Update ONLY records still stored as strings
    # --------------------------------------------

    operations = []


    for doc in hk_docs:

        old_value = doc.get(FIELD)

        if isinstance(
            old_value,
            datetime,
        ):
            continue


        program_id = clean(
            doc["program_id"]
        )


        operations.append(
            UpdateOne(
                {
                    "program_id": program_id,
                    FIELD: old_value,
                },
                {
                    "$set": {
                        FIELD: converted[
                            program_id
                        ]
                    }
                },
            )
        )


    print(
        "Documents requiring repair      :",
        len(operations),
    )


    if operations:

        result = collection.bulk_write(
            operations,
            ordered=True,
        )

        print(
            "Matched documents              :",
            result.matched_count,
        )

        print(
            "Modified documents             :",
            result.modified_count,
        )


        if (
            result.matched_count
            != len(operations)
        ):
            raise ValueError(
                "Not every targeted HK document matched."
            )


    # --------------------------------------------
    # Immediate verification
    # --------------------------------------------

    after_docs = list(
        collection.find(
            {
                "program_id": {
                    "$regex": "^prog_hk_"
                }
            },
            {
                "_id": 0,
                "program_id": 1,
                FIELD: 1,
            },
        )
    )


    after_types = Counter(
        type(
            doc.get(FIELD)
        ).__name__
        for doc in after_docs
    )


    print(
        "Date types after                :",
        dict(after_types),
    )


    if after_types != Counter({
        "datetime": 45
    }):
        raise ValueError(
            "Expected exactly 45 datetime values "
            "after repair."
        )


finally:

    client.close()


print()
print("=" * 100)

print(
    "STEP 169.3F.2 HK INTERNATIONAL "
    "DATE TYPE REPAIR: PASS"
)

print(
    "ONLY international_applicants_last_verified_at "
    "WAS TYPE-NORMALIZED"
)

print("=" * 100)
