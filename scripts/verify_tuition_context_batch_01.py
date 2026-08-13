from __future__ import annotations

import csv
from pathlib import Path


VERIFIED_DATE = "2026-08-12T00:00:00"


HOKKAIDO_SOURCE = (
    "https://intl-student-handbook.oia.hokudai.ac.jp/"
    "en/campus_life-en/tuition"
)

SCIENCE_TOKYO_SOURCE = (
    "https://admissions.isct.ac.jp/en/013/graduate/"
    "programs/science-and-engineering"
)

KEIO_MASTER_SOURCE = (
    "https://www.keio.ac.jp/files/"
    "92446f38dc587a176fbe87b824d23c53619077cbfe934c78a675c4d4d0e0205c"
)

KEIO_DOCTORAL_SOURCE = (
    "https://www.keio.ac.jp/files/"
    "6816f9eafe807a7f8692e6f74b6571aedb22bee444a04be8184f046af8d3a52c"
)


VERIFIED_CONTEXT = {
    # --------------------------------------------------
    # HOKKAIDO UNIVERSITY
    # --------------------------------------------------

    "prog_jp_019": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            "Graduate Students",
        "tuition_source_url":
            HOKKAIDO_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "Official Hokkaido University "
                "graduate annual tuition. "
                "Admission and examination fees "
                "are separate."
            ),
    },

    "prog_jp_020": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            "Graduate Students",
        "tuition_source_url":
            HOKKAIDO_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "Official Hokkaido University "
                "graduate annual tuition. "
                "Admission and examination fees "
                "are separate."
            ),
    },

    "prog_jp_021": {
        "expected_fee": "535800",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            "Graduate Students",
        "tuition_source_url":
            HOKKAIDO_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "Official Hokkaido University "
                "graduate annual tuition. "
                "Admission and examination fees "
                "are separate."
            ),
    },

    # --------------------------------------------------
    # INSTITUTE OF SCIENCE TOKYO
    # --------------------------------------------------

    "prog_jp_024": {
        "expected_fee": "635400",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate Students - "
                "Science and Engineering"
            ),
        "tuition_source_url":
            SCIENCE_TOKYO_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "Official annual tuition for "
                "Science Tokyo international "
                "graduate programs. Enrollment "
                "and application fees are separate."
            ),
    },

    "prog_jp_022": {
        "expected_fee": "635400",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate Students - "
                "Science and Engineering"
            ),
        "tuition_source_url":
            SCIENCE_TOKYO_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "Official annual tuition for "
                "Science Tokyo international "
                "graduate programs. Enrollment "
                "and application fees are separate."
            ),
    },

    "prog_jp_023": {
        "expected_fee": "635400",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate Students - "
                "Science and Engineering"
            ),
        "tuition_source_url":
            SCIENCE_TOKYO_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "Official annual tuition for "
                "Science Tokyo international "
                "graduate programs. Enrollment "
                "and application fees are separate."
            ),
    },

    # --------------------------------------------------
    # KEIO UNIVERSITY
    # --------------------------------------------------

    "prog_jp_036": {
        "expected_fee": "1160000",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate School of Science "
                "and Technology - Master's"
            ),
        "tuition_source_url":
            KEIO_MASTER_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "AY2026 tuition fee for Keio "
                "Graduate School of Science and "
                "Technology Master's Program. "
                "Registration and other academic "
                "fees are not included."
            ),
    },

    "prog_jp_034": {
        "expected_fee": "1160000",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate School of Science "
                "and Technology - Master's"
            ),
        "tuition_source_url":
            KEIO_MASTER_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "AY2026 tuition fee for Keio "
                "Graduate School of Science and "
                "Technology Master's Program. "
                "Registration and other academic "
                "fees are not included."
            ),
    },

    "prog_jp_035": {
        "expected_fee": "740000",
        "tuition_academic_year": "2026",
        "tuition_student_scope":
            (
                "Graduate School of Science "
                "and Technology - Doctoral"
            ),
        "tuition_source_url":
            KEIO_DOCTORAL_SOURCE,
        "tuition_last_verified_at":
            VERIFIED_DATE,
        "tuition_note":
            (
                "AY2026 tuition fee for Keio "
                "Graduate School of Science and "
                "Technology Doctoral Program. "
                "Registration and other academic "
                "fees are not included."
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
        "Batch 01"
    )
    print("=" * 88)

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    staging_file = (
        project_root
        / "planning"
        / "25_japan_program_tuition_context_staging.csv"
    )

    output_file = (
        project_root
        / "planning"
        / "26_japan_program_tuition_context_batch01_verified.csv"
    )

    if not staging_file.exists():
        raise FileNotFoundError(
            f"Staging CSV not found: {staging_file}"
        )

    # --------------------------------------------------
    # Load staging CSV
    # --------------------------------------------------

    with staging_file.open(
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
        "Staging rows loaded:",
        len(rows),
    )

    # --------------------------------------------------
    # Apply verified context
    # --------------------------------------------------

    verified_count = 0

    found_program_ids = set()

    for row in rows:
        program_id = row.get(
            "program_id",
            "",
        ).strip()

        context = VERIFIED_CONTEXT.get(
            program_id
        )

        if not context:
            continue

        found_program_ids.add(
            program_id
        )

        current_fee = normalize_fee(
            row.get(
                "current_tuition_fee",
                "",
            )
        )

        expected_fee = normalize_fee(
            context["expected_fee"]
        )

        if current_fee != expected_fee:
            raise RuntimeError(
                "\n"
                f"TUITION MISMATCH: {program_id}\n"
                f"Database/staging fee: {current_fee}\n"
                f"Expected verified fee: {expected_fee}\n"
                "Verification stopped. "
                "No output file was written."
            )

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
            context[
                "tuition_last_verified_at"
            ]
        )

        row["tuition_note"] = (
            context[
                "tuition_note"
            ]
        )

        verified_count += 1

    # --------------------------------------------------
    # Safety check
    # --------------------------------------------------

    expected_ids = set(
        VERIFIED_CONTEXT.keys()
    )

    missing_ids = (
        expected_ids
        - found_program_ids
    )

    if missing_ids:
        raise RuntimeError(
            "Some expected program IDs were "
            "not found in the staging CSV:\n"
            + "\n".join(
                sorted(missing_ids)
            )
        )

    # --------------------------------------------------
    # Write verified batch output
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
        "Batch 01 tuition verification complete."
    )

    print(
        "Programs verified:",
        verified_count,
    )

    print(
        "Programs still awaiting context:",
        len(rows) - verified_count,
    )

    print()
    print(
        "Verified program IDs:"
    )

    for program_id in sorted(
        found_program_ids
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
        "Existing tuition fee values were "
        "checked before context was added."
    )

    print("=" * 88)


if __name__ == "__main__":
    main()