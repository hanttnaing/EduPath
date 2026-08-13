from __future__ import annotations

import csv
from pathlib import Path


VERIFIED_DATE = "2026-08-12T00:00:00"


# ======================================================
# OFFICIAL SOURCES
# ======================================================

OSAKA_SOURCE = (
    "https://www.ist.osaka-u.ac.jp/files/"
    "examinees/admission/2026/15_a_EN2026.pdf"
)

UTOKYO_SOURCE = (
    "https://www.i.u-tokyo.ac.jp/edu/"
    "entra/2026_admission-g_m_e.pdf"
)

TOHOKU_SOURCE = (
    "https://www.is.tohoku.ac.jp/media/files/"
    "entrance/summary/first202604_20251010_1_1_en.pdf"
)

WASEDA_SOURCE = (
    "https://www.waseda.jp/inst/admission/"
    "assets/uploads/2025/06/"
    "Masters-Professional-Expenses-AY2026.pdf"
)


# ======================================================
# VERIFIED UNIVERSITY CONTEXT
# ======================================================

VERIFIED_UNIVERSITIES = {
    "Osaka University": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate School of Information "
                "Science and Technology - Master's"
            ),
        "tuition_source_url":
            OSAKA_SOURCE,
        "tuition_note":
            (
                "Annual tuition for the Graduate "
                "School of Information Science and "
                "Technology. Admission fee is separate."
            ),
    },

    "The University of Tokyo": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate School of Information "
                "Science and Technology - Master's"
            ),
        "tuition_source_url":
            UTOKYO_SOURCE,
        "tuition_note":
            (
                "AY2026 Master's annual tuition. "
                "Admission fee is separate."
            ),
    },

    "Tohoku University": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate School of Information "
                "Sciences - Master's"
            ),
        "tuition_source_url":
            TOHOKU_SOURCE,
        "tuition_note":
            (
                "AY2026 annual tuition for the "
                "Graduate School of Information "
                "Sciences. Amount may change if "
                "university tuition is revised."
            ),
    },

    "Waseda University": {
        "expected_fee": "991000",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate School of Fundamental "
                "Science and Engineering - Master's"
            ),
        "tuition_source_url":
            WASEDA_SOURCE,
        "tuition_note":
            (
                "AY2026 tuition fee only. "
                "Admission fee, seminar/laboratory "
                "fees and other charges are separate."
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
        "Batch 03"
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
        / "27_japan_program_tuition_context_batch02_verified.csv"
    )

    output_file = (
        project_root
        / "planning"
        / "28_japan_program_tuition_context_batch03_verified.csv"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Batch 02 file not found:\n{input_file}"
        )

    # --------------------------------------------------
    # Load Batch 02
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
        "Rows loaded from Batch 02:",
        len(rows),
    )

    # --------------------------------------------------
    # Apply Batch 03 verification
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

        # ----------------------------------------------
        # Safety check
        # ----------------------------------------------

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
    # Each target university must exist
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
            "in the dataset:\n"
            + "\n".join(
                universities_not_found
            )
        )

    # --------------------------------------------------
    # Count total context
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
    # Write Batch 03 result
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
        "Batch 03 tuition verification complete."
    )

    print()
    print(
        "Programs verified in Batch 03:",
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
        "Batch 03 breakdown:"
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
        "validated against official sources."
    )

    print("=" * 88)


if __name__ == "__main__":
    main()