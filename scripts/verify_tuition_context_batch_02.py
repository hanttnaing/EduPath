from __future__ import annotations

import csv
from pathlib import Path


VERIFIED_DATE = "2026-08-12T00:00:00"


# ======================================================
# OFFICIAL TUITION SOURCES
# ======================================================

KOBE_SOURCE = (
    "https://www.kobe-u.ac.jp/en/"
    "campus-life/tuition/about/"
)

KYOTO_SOURCE = (
    "https://www.kyoto-u.ac.jp/en/current/"
    "how-to/tuition/tuition-and-fees"
)

KYUSHU_SOURCE = (
    "https://www.kyushu-u.ac.jp/en/"
    "admission/fees/expenses/"
)

NAGOYA_SOURCE = (
    "https://life.gmc.nagoya-u.ac.jp/"
    "en/life-at-nu/tuition/"
)


# ======================================================
# VERIFIED UNIVERSITY CONTEXT
# ======================================================

VERIFIED_UNIVERSITIES = {
    "Kobe University": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            "Graduate Students",
        "tuition_source_url":
            KOBE_SOURCE,
        "tuition_note":
            (
                "Official Kobe University annual "
                "graduate tuition. Admission and "
                "entrance examination fees are "
                "separate."
            ),
    },

    "Kyoto University": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            "Graduate Students",
        "tuition_source_url":
            KYOTO_SOURCE,
        "tuition_note":
            (
                "Official Kyoto University annual "
                "graduate tuition. Law School and "
                "other special categories may use "
                "different tuition rates."
            ),
    },

    "Kyushu University": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            "Graduate Students",
        "tuition_source_url":
            KYUSHU_SOURCE,
        "tuition_note":
            (
                "Official Kyushu University annual "
                "graduate tuition. Enrollment and "
                "application fees are separate."
            ),
    },

    "Nagoya University": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            "Degree-Seeking Graduate Students",
        "tuition_source_url":
            NAGOYA_SOURCE,
        "tuition_note":
            (
                "Official Nagoya University annual "
                "tuition for degree-seeking graduate "
                "students. Registration and "
                "application fees are separate."
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
        "EduPath - Tuition Context Verification "
        "Batch 02"
    )
    print("=" * 88)

    # --------------------------------------------------
    # Paths
    # --------------------------------------------------

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    input_file = (
        project_root
        / "planning"
        / "26_japan_program_tuition_context_batch01_verified.csv"
    )

    output_file = (
        project_root
        / "planning"
        / "27_japan_program_tuition_context_batch02_verified.csv"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Batch 01 file not found:\n{input_file}"
        )

    # --------------------------------------------------
    # Load Batch 01 result
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
        "Rows loaded from Batch 01:",
        len(rows),
    )

    # --------------------------------------------------
    # Apply Batch 02 verification
    # --------------------------------------------------

    verified_count = 0

    verified_ids = []

    verified_by_university = {
        university_name: 0
        for university_name
        in VERIFIED_UNIVERSITIES
    }

    for row in rows:
        university_name = (
            row.get(
                "university_name",
                "",
            )
            .strip()
        )

        context = (
            VERIFIED_UNIVERSITIES.get(
                university_name
            )
        )

        if not context:
            continue

        program_id = (
            row.get(
                "program_id",
                "",
            )
            .strip()
        )

        # ----------------------------------------------
        # Safety check: tuition must match official fee
        # ----------------------------------------------

        current_fee = normalize_fee(
            row.get(
                "current_tuition_fee",
                "",
            )
        )

        expected_fee = normalize_fee(
            context[
                "expected_fee"
            ]
        )

        if current_fee != expected_fee:
            raise RuntimeError(
                "\n"
                "TUITION MISMATCH DETECTED\n"
                "-------------------------\n"
                f"Program ID : {program_id}\n"
                f"University : {university_name}\n"
                f"Program    : "
                f"{row.get('program_name')}\n"
                f"Current fee: {current_fee}\n"
                f"Expected   : {expected_fee}\n\n"
                "Verification stopped.\n"
                "No output file was written."
            )

        # ----------------------------------------------
        # Fill tuition context
        # ----------------------------------------------

        row["tuition_academic_year"] = (
            context[
                "tuition_academic_year"
            ]
        )

        row["tuition_student_scope"] = (
            context[
                "tuition_student_scope"
            ]
        )

        row["tuition_source_url"] = (
            context[
                "tuition_source_url"
            ]
        )

        row["tuition_last_verified_at"] = (
            VERIFIED_DATE
        )

        row["tuition_note"] = (
            context[
                "tuition_note"
            ]
        )

        verified_count += 1

        verified_ids.append(
            program_id
        )

        verified_by_university[
            university_name
        ] += 1

    # --------------------------------------------------
    # Safety check:
    # Every target university must exist
    # --------------------------------------------------

    universities_not_found = [
        university_name
        for university_name, count
        in verified_by_university.items()
        if count == 0
    ]

    if universities_not_found:
        raise RuntimeError(
            "Target universities were not found "
            "in the staging dataset:\n"
            + "\n".join(
                universities_not_found
            )
        )

    # --------------------------------------------------
    # Count total rows with tuition context
    # --------------------------------------------------

    total_context_complete = sum(
        1
        for row in rows
        if (
            row.get(
                "tuition_academic_year"
            )
            and row.get(
                "tuition_source_url"
            )
            and row.get(
                "tuition_last_verified_at"
            )
        )
    )

    remaining_context = (
        len(rows)
        - total_context_complete
    )

    # --------------------------------------------------
    # Write Batch 02 output
    # --------------------------------------------------

    with output_file.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(rows)

    # --------------------------------------------------
    # Report
    # --------------------------------------------------

    print()
    print(
        "Batch 02 tuition verification complete."
    )

    print()
    print(
        "Programs verified in Batch 02:",
        verified_count,
    )

    print(
        "Total programs with tuition context:",
        total_context_complete,
    )

    print(
        "Programs still awaiting context:",
        remaining_context,
    )

    print()
    print(
        "Batch 02 breakdown:"
    )

    for (
        university_name,
        count,
    ) in verified_by_university.items():

        print(
            f" - {university_name}: "
            f"{count} program(s)"
        )

    print()
    print(
        "Verified program IDs:"
    )

    for program_id in sorted(
        verified_ids
    ):
        print(
            " -",
            program_id,
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
        "No MongoDB records were modified."
    )

    print(
        "Existing tuition values were "
        "validated before context was added."
    )

    print("=" * 88)


if __name__ == "__main__":
    main()