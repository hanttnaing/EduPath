from __future__ import annotations

import csv
from pathlib import Path


VERIFIED_DATE = "2026-08-12T00:00:00"

TSUKUBA_2027_FEE = "608800"

TSUKUBA_SOURCE = (
    "https://eng.ap-graduate.tsukuba.ac.jp/"
    "course/sie/first_all/"
)

TSUKUBA_DOCTORAL_SOURCE = (
    "https://eng.ap-graduate.tsukuba.ac.jp/"
    "course/sie/latter_all/"
)


TARGET_PROGRAMS = {
    "prog_jp_025": {
        "expected_old_fee": "535800",
        "verified_fee": "608800",
        "source_url": TSUKUBA_SOURCE,
        "scope": (
            "International Students with "
            "Student residence status - "
            "AY2027 enrollment"
        ),
        "note": (
            "University of Tsukuba AY2027 "
            "international-student tuition. "
            "Annual tuition is 608,800 JPY "
            "(304,400 JPY per semester). "
            "Admission fee is separate."
        ),
    },

    "prog_jp_026": {
        "expected_old_fee": "535800",
        "verified_fee": "608800",
        "source_url": TSUKUBA_SOURCE,
        "scope": (
            "International Students with "
            "Student residence status - "
            "AY2027 enrollment"
        ),
        "note": (
            "University of Tsukuba AY2027 "
            "international-student tuition. "
            "Annual tuition is 608,800 JPY "
            "(304,400 JPY per semester). "
            "Admission fee is separate."
        ),
    },

    "prog_jp_027": {
        "expected_old_fee": "535800",
        "verified_fee": "608800",
        "source_url": TSUKUBA_DOCTORAL_SOURCE,
        "scope": (
            "International Students with "
            "Student residence status - "
            "AY2027 enrollment"
        ),
        "note": (
            "University of Tsukuba AY2027 "
            "international-student tuition. "
            "Annual tuition is 608,800 JPY "
            "(304,400 JPY per semester). "
            "Admission fee is separate."
        ),
    },
}


def normalize_fee(value: str) -> str:
    value = str(value or "").strip()
    value = value.replace(",", "")

    if value.endswith(".0"):
        value = value[:-2]

    return value


def main() -> None:
    print("=" * 88)
    print(
        "EduPath - Tsukuba AY2027 "
        "International Tuition Verification"
    )
    print("=" * 88)

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    input_file = (
        project_root
        / "planning"
        / "28_japan_program_tuition_context_batch03_verified.csv"
    )

    output_file = (
        project_root
        / "planning"
        / "29_japan_program_tuition_context_all_verified.csv"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Batch 03 file not found:\n{input_file}"
        )

    # --------------------------------------------------
    # Load Batch 03
    # --------------------------------------------------

    with input_file.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        rows = list(reader)
        fieldnames = reader.fieldnames

    if not fieldnames:
        raise RuntimeError(
            "CSV header could not be read."
        )

    print()
    print(
        "Rows loaded from Batch 03:",
        len(rows),
    )

    # --------------------------------------------------
    # Add audit-specific columns
    # --------------------------------------------------

    output_fieldnames = list(fieldnames)

    extra_fields = [
        "previous_tuition_fee",
        "tuition_change_required",
    ]

    for field in extra_fields:
        if field not in output_fieldnames:
            output_fieldnames.append(field)

    corrected_count = 0
    found_ids = set()

    # --------------------------------------------------
    # Process Tsukuba records
    # --------------------------------------------------

    for row in rows:
        program_id = (
            row.get(
                "program_id",
                "",
            )
            .strip()
        )

        context = TARGET_PROGRAMS.get(
            program_id
        )

        if not context:
            continue

        found_ids.add(program_id)

        university_name = (
            row.get(
                "university_name",
                "",
            )
            .strip()
        )

        if university_name != "University of Tsukuba":
            raise RuntimeError(
                "\n"
                "UNIVERSITY MISMATCH\n"
                "-------------------\n"
                f"Program ID : {program_id}\n"
                f"University : {university_name}\n"
                "Expected   : University of Tsukuba"
            )

        old_fee = normalize_fee(
            row.get(
                "current_tuition_fee",
                "",
            )
        )

        expected_old_fee = normalize_fee(
            context[
                "expected_old_fee"
            ]
        )

        if old_fee != expected_old_fee:
            raise RuntimeError(
                "\n"
                "OLD TUITION MISMATCH\n"
                "--------------------\n"
                f"Program ID : {program_id}\n"
                f"Current fee: {old_fee}\n"
                f"Expected old fee: "
                f"{expected_old_fee}\n"
                "Verification stopped."
            )

        # ----------------------------------------------
        # Preserve previous fee for audit trail
        # ----------------------------------------------

        row["previous_tuition_fee"] = old_fee

        # ----------------------------------------------
        # Update verified staging value only
        # MongoDB is NOT modified here.
        # ----------------------------------------------

        row["current_tuition_fee"] = (
            context[
                "verified_fee"
            ]
        )

        row["tuition_academic_year"] = "2027"

        row["tuition_student_scope"] = (
            context[
                "scope"
            ]
        )

        row["tuition_source_url"] = (
            context[
                "source_url"
            ]
        )

        row["tuition_last_verified_at"] = (
            VERIFIED_DATE
        )

        row["tuition_note"] = (
            context[
                "note"
            ]
        )

        row["tuition_change_required"] = "YES"

        corrected_count += 1

    # --------------------------------------------------
    # Safety check
    # --------------------------------------------------

    expected_ids = set(
        TARGET_PROGRAMS.keys()
    )

    missing_ids = (
        expected_ids
        - found_ids
    )

    if missing_ids:
        raise RuntimeError(
            "Expected Tsukuba programs "
            "were not found:\n"
            + "\n".join(
                sorted(missing_ids)
            )
        )

    # --------------------------------------------------
    # Mark unchanged records
    # --------------------------------------------------

    for row in rows:
        if not row.get(
            "tuition_change_required"
        ):
            row[
                "tuition_change_required"
            ] = "NO"

        if not row.get(
            "previous_tuition_fee"
        ):
            row[
                "previous_tuition_fee"
            ] = row.get(
                "current_tuition_fee",
                "",
            )

    # --------------------------------------------------
    # Final completeness check
    # --------------------------------------------------

    context_complete = sum(
        1
        for row in rows
        if (
            row.get(
                "tuition_academic_year"
            )
            and row.get(
                "tuition_student_scope"
            )
            and row.get(
                "tuition_source_url"
            )
            and row.get(
                "tuition_last_verified_at"
            )
        )
    )

    remaining = (
        len(rows)
        - context_complete
    )

    if remaining != 0:
        raise RuntimeError(
            f"{remaining} program(s) still "
            "lack tuition context."
        )

    # --------------------------------------------------
    # Write final verified CSV
    # --------------------------------------------------

    with output_file.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=output_fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    # --------------------------------------------------
    # Report
    # --------------------------------------------------

    print()
    print(
        "Tsukuba verification complete."
    )

    print(
        "Tsukuba programs corrected:",
        corrected_count,
    )

    print(
        "Total programs with tuition context:",
        context_complete,
    )

    print(
        "Programs still awaiting context:",
        remaining,
    )

    print()
    print(
        "Corrected program IDs:"
    )

    for program_id in sorted(
        found_ids
    ):
        print(
            " -",
            program_id,
            "535800 -> 608800 JPY",
        )

    print()
    print(
        "Output file:"
    )

    print(
        output_file
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "MongoDB was NOT modified."
    )

    print(
        "Only the verified staging CSV "
        "was corrected."
    )

    print("=" * 88)


if __name__ == "__main__":
    main()

    