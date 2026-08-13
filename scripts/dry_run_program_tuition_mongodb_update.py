from __future__ import annotations

import csv
import sys
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
# EXISTING PROJECT DATABASE CONNECTION
# ======================================================

from backend.app.database import (
    get_database,
    ping_database,
)


# ======================================================
# CONFIGURATION
# ======================================================

EXPECTED_PROGRAM_COUNT = 36

EXPECTED_TUITION_CHANGE_IDS = {
    "prog_jp_025",
    "prog_jp_026",
    "prog_jp_027",
}

EXPECTED_TSUKUBA_OLD_FEE = 535800
EXPECTED_TSUKUBA_NEW_FEE = 608800

COLLECTION_NAME = "programs"


# ======================================================
# HELPERS
# ======================================================

def clean_text(
    value,
) -> str:
    return str(
        value or ""
    ).strip()


def parse_int(
    value,
) -> int | None:
    text = clean_text(
        value
    )

    if not text:
        return None

    text = text.replace(
        ",",
        "",
    )

    try:
        return int(
            float(text)
        )

    except (
        ValueError,
        TypeError,
    ):
        return None


def normalize_database_fee(
    value,
) -> int | None:
    if value is None:
        return None

    try:
        return int(
            float(value)
        )

    except (
        ValueError,
        TypeError,
    ):
        return None


# ======================================================
# MAIN
# ======================================================

def main() -> None:
    print("=" * 92)

    print(
        "EduPath - Program Tuition "
        "MongoDB Update DRY RUN"
    )

    print("=" * 92)

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
            "Final verified tuition CSV "
            "was not found:\n"
            f"{csv_file}"
        )

    # --------------------------------------------------
    # Connect using existing database.py
    # --------------------------------------------------

    print()
    print(
        "Checking MongoDB connection..."
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

    # --------------------------------------------------
    # Collection safety check
    # --------------------------------------------------

    collection_names = (
        database.list_collection_names()
    )

    print()
    print(
        "MongoDB collections:"
    )

    for name in sorted(
        collection_names
    ):
        print(
            " -",
            name,
        )

    if COLLECTION_NAME not in collection_names:
        print()
        print(
            "ERROR:"
        )

        print(
            f'Collection "{COLLECTION_NAME}" '
            "was not found."
        )

        print(
            "No database changes were made."
        )

        raise SystemExit(1)

    programs_collection = (
        database[
            COLLECTION_NAME
        ]
    )

    # --------------------------------------------------
    # Load verified CSV
    # --------------------------------------------------

    with csv_file.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(
            file
        )

        rows = list(
            reader
        )

    print()
    print(
        "Verified CSV rows:",
        len(rows),
    )

    if (
        len(rows)
        != EXPECTED_PROGRAM_COUNT
    ):
        raise RuntimeError(
            "Expected "
            f"{EXPECTED_PROGRAM_COUNT} "
            "program rows but found "
            f"{len(rows)}."
        )

    # --------------------------------------------------
    # Validation counters
    # --------------------------------------------------

    found_count = 0

    missing_ids = []

    fee_change_ids = []

    context_only_ids = []

    already_matching_ids = []

    unexpected_fee_changes = []

    baseline_mismatches = []

    # --------------------------------------------------
    # Compare CSV to MongoDB
    # --------------------------------------------------

    print()
    print(
        "-" * 92
    )

    print(
        "PROGRAM COMPARISON"
    )

    print(
        "-" * 92
    )

    for row in rows:
        program_id = clean_text(
            row.get(
                "program_id"
            )
        )

        if not program_id:
            raise RuntimeError(
                "Blank program_id "
                "found in CSV."
            )

        document = (
            programs_collection.find_one(
                {
                    "program_id":
                        program_id
                },
                {
                    "_id": 0,

                    "program_id": 1,

                    "program_name": 1,

                    "university_id": 1,

                    "tuition_fee": 1,

                    "tuition_currency": 1,

                    "tuition_period": 1,

                    "tuition_academic_year": 1,

                    "tuition_student_scope": 1,

                    "tuition_source_url": 1,

                    "tuition_last_verified_at": 1,

                    "tuition_note": 1,
                },
            )
        )

        if document is None:
            missing_ids.append(
                program_id
            )

            continue

        found_count += 1

        # ----------------------------------------------
        # Tuition values
        # ----------------------------------------------

        mongo_fee = (
            normalize_database_fee(
                document.get(
                    "tuition_fee"
                )
            )
        )

        previous_csv_fee = (
            parse_int(
                row.get(
                    "previous_tuition_fee"
                )
            )
        )

        verified_csv_fee = (
            parse_int(
                row.get(
                    "current_tuition_fee"
                )
            )
        )

        change_required = (
            clean_text(
                row.get(
                    "tuition_change_required"
                )
            )
            .upper()
        )

        # ----------------------------------------------
        # Baseline safety check
        #
        # MongoDB should still equal the
        # pre-update tuition stored in CSV.
        # ----------------------------------------------

        if (
            mongo_fee
            != previous_csv_fee
        ):
            baseline_mismatches.append(
                {
                    "program_id":
                        program_id,

                    "mongo_fee":
                        mongo_fee,

                    "expected_old_fee":
                        previous_csv_fee,
                }
            )

            continue

        # ----------------------------------------------
        # Expected tuition change
        # ----------------------------------------------

        if change_required == "YES":
            fee_change_ids.append(
                program_id
            )

            if (
                program_id
                not in
                EXPECTED_TUITION_CHANGE_IDS
            ):
                unexpected_fee_changes.append(
                    program_id
                )

            if (
                previous_csv_fee
                == verified_csv_fee
            ):
                unexpected_fee_changes.append(
                    program_id
                )

        elif change_required == "NO":
            if (
                previous_csv_fee
                != verified_csv_fee
            ):
                unexpected_fee_changes.append(
                    program_id
                )

            # ------------------------------------------
            # Check whether tuition context
            # is already present
            # ------------------------------------------

            existing_context = {
                "tuition_academic_year":
                    document.get(
                        "tuition_academic_year"
                    ),

                "tuition_student_scope":
                    document.get(
                        "tuition_student_scope"
                    ),

                "tuition_source_url":
                    document.get(
                        "tuition_source_url"
                    ),

                "tuition_last_verified_at":
                    document.get(
                        "tuition_last_verified_at"
                    ),

                "tuition_note":
                    document.get(
                        "tuition_note"
                    ),
            }

            if any(
                value not in (
                    None,
                    "",
                )
                for value
                in existing_context.values()
            ):
                already_matching_ids.append(
                    program_id
                )

            else:
                context_only_ids.append(
                    program_id
                )

        else:
            unexpected_fee_changes.append(
                program_id
            )

    # ==================================================
    # SUMMARY
    # ==================================================

    print()
    print(
        "=" * 92
    )

    print(
        "DRY RUN SUMMARY"
    )

    print(
        "=" * 92
    )

    print(
        "CSV program records:",
        len(rows),
    )

    print(
        "MongoDB programs found:",
        found_count,
    )

    print(
        "Missing MongoDB program IDs:",
        len(missing_ids),
    )

    print()

    print(
        "Programs requiring "
        "tuition fee change:",
        len(fee_change_ids),
    )

    print(
        "Context-only program updates:",
        len(context_only_ids),
    )

    print(
        "Programs already containing "
        "tuition context:",
        len(already_matching_ids),
    )

    print()

    print(
        "Unexpected tuition changes:",
        len(
            set(
                unexpected_fee_changes
            )
        ),
    )

    print(
        "MongoDB baseline mismatches:",
        len(
            baseline_mismatches
        ),
    )

    # ==================================================
    # EXPECTED TUITION CHANGES
    # ==================================================

    print()
    print(
        "-" * 92
    )

    print(
        "EXPECTED TUITION CHANGES"
    )

    print(
        "-" * 92
    )

    for program_id in sorted(
        fee_change_ids
    ):
        print(
            f"{program_id}: "
            f"{EXPECTED_TSUKUBA_OLD_FEE:,} "
            "-> "
            f"{EXPECTED_TSUKUBA_NEW_FEE:,} "
            "JPY / Annual"
        )

    # ==================================================
    # ERROR DETAILS
    # ==================================================

    errors = []

    if missing_ids:
        errors.append(
            "Missing MongoDB program IDs: "
            + ", ".join(
                sorted(
                    missing_ids
                )
            )
        )

    if baseline_mismatches:
        for mismatch in (
            baseline_mismatches
        ):
            errors.append(
                f"{mismatch['program_id']}: "
                "MongoDB tuition "
                f"{mismatch['mongo_fee']} "
                "does not match expected "
                "pre-update tuition "
                f"{mismatch['expected_old_fee']}."
            )

    unexpected_set = set(
        unexpected_fee_changes
    )

    if unexpected_set:
        errors.append(
            "Unexpected tuition-change "
            "records: "
            + ", ".join(
                sorted(
                    unexpected_set
                )
            )
        )

    if (
        set(fee_change_ids)
        != EXPECTED_TUITION_CHANGE_IDS
    ):
        errors.append(
            "Tuition change IDs do not "
            "match the expected Tsukuba "
            "program set.\n"
            f"Expected: "
            f"{sorted(EXPECTED_TUITION_CHANGE_IDS)}\n"
            f"Found: "
            f"{sorted(set(fee_change_ids))}"
        )

    if len(
        fee_change_ids
    ) != 3:
        errors.append(
            "Expected exactly 3 tuition "
            "fee changes."
        )

    # ==================================================
    # FINAL RESULT
    # ==================================================

    print()
    print(
        "=" * 92
    )

    if errors:
        print(
            "DRY RUN VALIDATION: FAILED"
        )

        print(
            "=" * 92
        )

        print()

        for index, error in enumerate(
            errors,
            start=1,
        ):
            print(
                f"{index}. {error}"
            )

        print()
        print(
            "NO DATABASE RECORDS "
            "WERE MODIFIED."
        )

        raise SystemExit(1)

    print(
        "DRY RUN VALIDATION: PASSED"
    )

    print()

    print(
        "MongoDB currently matches the "
        "expected pre-update dataset."
    )

    print(
        "Exactly 3 verified Tsukuba "
        "tuition changes are ready."
    )

    print(
        "The remaining programs are ready "
        "for tuition-context enrichment."
    )

    print()
    print(
        "NO DATABASE RECORDS "
        "WERE MODIFIED."
    )

    print(
        "=" * 92
    )


if __name__ == "__main__":
    main()