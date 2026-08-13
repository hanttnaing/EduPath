from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path


# ======================================================
# PROJECT ROOT
# ======================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# ======================================================
# EXISTING DATABASE CONNECTION
# ======================================================

from backend.app.database import (
    get_database,
    ping_database,
)


# ======================================================
# CONFIG
# ======================================================

COLLECTION_NAME = "programs"

EXPECTED_PROGRAM_COUNT = 36

EXPECTED_CHANGED_IDS = {
    "prog_jp_025",
    "prog_jp_026",
    "prog_jp_027",
}

MODIFIED_FIELDS = [
    "tuition_fee",
    "tuition_currency",
    "tuition_period",
    "tuition_academic_year",
    "tuition_student_scope",
    "tuition_source_url",
    "tuition_last_verified_at",
    "tuition_note",
]


# ======================================================
# HELPERS
# ======================================================

def clean_text(value) -> str:
    return str(
        value or ""
    ).strip()


def parse_int(value) -> int:
    text = clean_text(value)

    text = text.replace(
        ",",
        "",
    )

    if not text:
        raise ValueError(
            "Blank numeric value."
        )

    return int(
        float(text)
    )


def parse_datetime(value: str) -> datetime:
    text = clean_text(value)

    if not text:
        raise ValueError(
            "Blank datetime value."
        )

    parsed = datetime.fromisoformat(
        text.replace(
            "Z",
            "+00:00",
        )
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed


def normalize_mongo_datetime(
    value,
):
    if value is None:
        return None

    if not isinstance(
        value,
        datetime,
    ):
        return value

    # PyMongo commonly returns
    # naive UTC datetimes.
    if value.tzinfo is None:
        value = value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        timezone.utc
    ).replace(
        microsecond=0
    )


# ======================================================
# MAIN
# ======================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Apply verified Japan program "
            "tuition updates to MongoDB."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Actually modify MongoDB. "
            "Without this flag the script stops."
        ),
    )

    args = parser.parse_args()

    print("=" * 94)

    print(
        "EduPath - Controlled Program "
        "Tuition MongoDB Update"
    )

    print("=" * 94)

    if not args.apply:
        print()
        print(
            "UPDATE NOT STARTED."
        )

        print(
            "This script requires the "
            "--apply flag."
        )

        print()
        print(
            "Run:"
        )

        print(
            "python scripts\\"
            "apply_program_tuition_mongodb_update.py "
            "--apply"
        )

        print()
        print(
            "No MongoDB records were modified."
        )

        return

    # --------------------------------------------------
    # Verified CSV
    # --------------------------------------------------

    csv_file = (
        PROJECT_ROOT
        / "planning"
        / "29_japan_program_tuition_context_all_verified.csv"
    )

    if not csv_file.exists():
        raise FileNotFoundError(
            f"Verified CSV not found:\n"
            f"{csv_file}"
        )

    # --------------------------------------------------
    # Load CSV
    # --------------------------------------------------

    with csv_file.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        rows = list(reader)

    if len(rows) != EXPECTED_PROGRAM_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_PROGRAM_COUNT} "
            f"rows but found {len(rows)}."
        )

    program_ids = [
        clean_text(
            row.get("program_id")
        )
        for row in rows
    ]

    if len(
        set(program_ids)
    ) != EXPECTED_PROGRAM_COUNT:
        raise RuntimeError(
            "Program IDs are not unique."
        )

    # --------------------------------------------------
    # Connect
    # --------------------------------------------------

    print()
    print(
        "Connecting to MongoDB..."
    )

    ping_database()

    database = get_database()

    print(
        "MongoDB connection: OK"
    )

    print(
        "Database:",
        database.name,
    )

    collection_names = (
        database.list_collection_names()
    )

    if COLLECTION_NAME not in collection_names:
        raise RuntimeError(
            f'Collection "{COLLECTION_NAME}" '
            "does not exist."
        )

    collection = database[
        COLLECTION_NAME
    ]

    # ==================================================
    # PRE-WRITE SAFETY CHECK
    # ==================================================

    print()
    print(
        "Running final pre-write checks..."
    )

    snapshots = {}

    expected_updates = {}

    changed_ids = set()

    for row in rows:
        program_id = clean_text(
            row.get(
                "program_id"
            )
        )

        document = collection.find_one(
            {
                "program_id":
                    program_id
            }
        )

        if document is None:
            raise RuntimeError(
                f"{program_id} not found "
                "in MongoDB."
            )

        previous_fee = parse_int(
            row.get(
                "previous_tuition_fee"
            )
        )

        mongo_fee = parse_int(
            document.get(
                "tuition_fee"
            )
        )

        if mongo_fee != previous_fee:
            raise RuntimeError(
                f"{program_id}: MongoDB "
                f"tuition is {mongo_fee}, "
                f"expected baseline "
                f"{previous_fee}."
            )

        change_required = (
            clean_text(
                row.get(
                    "tuition_change_required"
                )
            )
            .upper()
        )

        verified_fee = parse_int(
            row.get(
                "current_tuition_fee"
            )
        )

        if change_required == "YES":
            changed_ids.add(
                program_id
            )

        elif change_required == "NO":
            if verified_fee != previous_fee:
                raise RuntimeError(
                    f"{program_id}: tuition "
                    "changed even though "
                    "change_required=NO."
                )

        else:
            raise RuntimeError(
                f"{program_id}: invalid "
                "tuition_change_required."
            )

        # ----------------------------------------------
        # Preserve exact old field state
        # for possible rollback
        # ----------------------------------------------

        snapshots[
            program_id
        ] = {
            field: {
                "exists":
                    field in document,

                "value":
                    document.get(
                        field
                    ),
            }
            for field in MODIFIED_FIELDS
        }

        # ----------------------------------------------
        # Build verified update
        # ----------------------------------------------

        expected_updates[
            program_id
        ] = {
            "tuition_fee":
                verified_fee,

            "tuition_currency":
                clean_text(
                    row.get(
                        "current_tuition_currency"
                    )
                ),

            "tuition_period":
                clean_text(
                    row.get(
                        "current_tuition_period"
                    )
                ),

            "tuition_academic_year":
                parse_int(
                    row.get(
                        "tuition_academic_year"
                    )
                ),

            "tuition_student_scope":
                clean_text(
                    row.get(
                        "tuition_student_scope"
                    )
                ),

            "tuition_source_url":
                clean_text(
                    row.get(
                        "tuition_source_url"
                    )
                ),

            "tuition_last_verified_at":
                parse_datetime(
                    row.get(
                        "tuition_last_verified_at"
                    )
                ),

            "tuition_note":
                clean_text(
                    row.get(
                        "tuition_note"
                    )
                ),
        }

    if changed_ids != EXPECTED_CHANGED_IDS:
        raise RuntimeError(
            "Expected tuition-change IDs "
            "do not match.\n"
            f"Expected: "
            f"{sorted(EXPECTED_CHANGED_IDS)}\n"
            f"Found: "
            f"{sorted(changed_ids)}"
        )

    print(
        "Pre-write validation: PASSED"
    )

    print(
        "Programs ready:",
        len(expected_updates),
    )

    print(
        "Actual tuition changes:",
        len(changed_ids),
    )

    # ==================================================
    # IMMEDIATE BACKUP OF MODIFIED FIELDS
    # ==================================================

    backup_folder = (
        PROJECT_ROOT
        / "planning"
        / "backups"
    )

    backup_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    snapshot_file = (
        backup_folder
        / (
            "program_tuition_fields_"
            f"before_update_{timestamp}.csv"
        )
    )

    snapshot_fields = [
        "program_id",
        *MODIFIED_FIELDS,
    ]

    with snapshot_file.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=snapshot_fields,
        )

        writer.writeheader()

        for program_id in program_ids:
            old_state = snapshots[
                program_id
            ]

            output_row = {
                "program_id":
                    program_id
            }

            for field in MODIFIED_FIELDS:
                if old_state[
                    field
                ][
                    "exists"
                ]:
                    output_row[
                        field
                    ] = old_state[
                        field
                    ][
                        "value"
                    ]

                else:
                    output_row[
                        field
                    ] = (
                        "<FIELD_NOT_PRESENT>"
                    )

            writer.writerow(
                output_row
            )

    print()
    print(
        "Immediate backup created:"
    )

    print(
        snapshot_file
    )

    # ==================================================
    # APPLY UPDATES
    # ==================================================

    print()
    print(
        "Applying controlled updates..."
    )

    processed_ids = []

    matched_total = 0
    modified_total = 0

    try:
        for program_id in program_ids:
            update_data = (
                expected_updates[
                    program_id
                ]
            )

            result = collection.update_one(
                {
                    "program_id":
                        program_id
                },
                {
                    "$set":
                        update_data
                },
            )

            if result.matched_count != 1:
                raise RuntimeError(
                    f"{program_id}: "
                    "matched_count "
                    f"was {result.matched_count}."
                )

            matched_total += (
                result.matched_count
            )

            modified_total += (
                result.modified_count
            )

            processed_ids.append(
                program_id
            )

        # ==============================================
        # POST-WRITE VERIFICATION
        # ==============================================

        print()
        print(
            "Verifying updated records..."
        )

        verification_errors = []

        for program_id in program_ids:
            document = (
                collection.find_one(
                    {
                        "program_id":
                            program_id
                    },
                    {
                        "_id": 0,
                        **{
                            field: 1
                            for field
                            in MODIFIED_FIELDS
                        },
                    },
                )
            )

            if document is None:
                verification_errors.append(
                    f"{program_id}: missing "
                    "after update."
                )

                continue

            expected = (
                expected_updates[
                    program_id
                ]
            )

            for (
                field,
                expected_value,
            ) in expected.items():

                actual_value = (
                    document.get(
                        field
                    )
                )

                if field == (
                    "tuition_last_verified_at"
                ):
                    actual_value = (
                        normalize_mongo_datetime(
                            actual_value
                        )
                    )

                    expected_value = (
                        normalize_mongo_datetime(
                            expected_value
                        )
                    )

                if (
                    actual_value
                    != expected_value
                ):
                    verification_errors.append(
                        f"{program_id}: "
                        f"{field} mismatch. "
                        f"Expected "
                        f"{expected_value!r}, "
                        f"found "
                        f"{actual_value!r}."
                    )

        if verification_errors:
            raise RuntimeError(
                "Post-write verification "
                "failed:\n"
                + "\n".join(
                    verification_errors
                )
            )

    except Exception as error:
        # ==============================================
        # AUTOMATIC ROLLBACK
        # ==============================================

        print()
        print(
            "ERROR DURING UPDATE:"
        )

        print(
            error
        )

        print()
        print(
            "Starting automatic rollback..."
        )

        for program_id in processed_ids:
            old_state = (
                snapshots[
                    program_id
                ]
            )

            set_fields = {}

            unset_fields = {}

            for field in MODIFIED_FIELDS:
                state = old_state[
                    field
                ]

                if state[
                    "exists"
                ]:
                    set_fields[
                        field
                    ] = state[
                        "value"
                    ]

                else:
                    unset_fields[
                        field
                    ] = ""

            update_operation = {}

            if set_fields:
                update_operation[
                    "$set"
                ] = set_fields

            if unset_fields:
                update_operation[
                    "$unset"
                ] = unset_fields

            collection.update_one(
                {
                    "program_id":
                        program_id
                },
                update_operation,
            )

        print(
            "Rollback complete."
        )

        print(
            "Database was restored to "
            "the captured pre-update state."
        )

        raise

    # ==================================================
    # SUCCESS
    # ==================================================

    print()
    print("=" * 94)

    print(
        "CONTROLLED MONGODB UPDATE: PASSED"
    )

    print("=" * 94)

    print()
    print(
        "Programs matched:",
        matched_total,
    )

    print(
        "Programs modified:",
        modified_total,
    )

    print(
        "Programs verified after write:",
        len(program_ids),
    )

    print()

    print(
        "Tuition amount changes:"
    )

    print(
        " - prog_jp_025: "
        "535,800 -> 608,800 JPY"
    )

    print(
        " - prog_jp_026: "
        "535,800 -> 608,800 JPY"
    )

    print(
        " - prog_jp_027: "
        "535,800 -> 608,800 JPY"
    )

    print()
    print(
        "Tuition context fields added "
        "for all 36 programs."
    )

    print()
    print(
        "Immediate pre-update backup:"
    )

    print(
        snapshot_file
    )

    print()
    print(
        "MongoDB update and "
        "post-write verification "
        "completed successfully."
    )

    print("=" * 94)


if __name__ == "__main__":
    main()