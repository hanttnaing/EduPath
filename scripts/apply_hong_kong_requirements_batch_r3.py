import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "16_hong_kong_program_requirements_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2au"
)

VERIFIED_AT = "2026-08-21"


R3_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(31, 46)
]


UNIVERSITY_REQUIREMENTS = {

    # -------------------------------------------------
    # HSUHK
    # prog_hk_031 - prog_hk_033
    # -------------------------------------------------

    "uni_hk_011": {
        "ielts": "5.5",
        "toefl": "70",

        "source_name": (
            "HSUHK International Qualifications - "
            "Year 1 Entrance Requirements"
        ),

        "source_url": (
            "https://admission.hsu.edu.hk/"
            "undergraduate-admissions/year-1-entry/"
            "international-qualification/"
            "entrance-requirements/"
        ),

        "gpa_status": (
            "No universal numeric GPA minimum verified "
            "for Year 1 international admission. "
            "Academic entry requirements depend on the "
            "applicant's qualification."
        ),

        "english_status": (
            "General English requirement for overseas "
            "Year 1 applicants verified."
        ),

        "accepted_tests": (
            "IELTS Academic; TOEFL iBT; TOEFL PBT; "
            "other recognised qualification-specific "
            "English results"
        ),

        "numeric_minimum_status": (
            "IELTS Academic 5.5 and TOEFL iBT 70 "
            "verified. No universal GPA value stored."
        ),

        "reason": (
            "HSUHK official Year 1 international "
            "qualification requirements specify IELTS "
            "Academic overall 5.5 or TOEFL iBT 70. "
            "Academic requirements vary by qualification, "
            "so no universal numeric GPA is stored."
        ),
    },


    # -------------------------------------------------
    # Hong Kong Chu Hai College
    # prog_hk_034 - prog_hk_036
    # -------------------------------------------------

    "uni_hk_012": {
        "ielts": "5.5",
        "toefl": "",

        "source_name": (
            "Hong Kong Chu Hai College - "
            "International Qualifications"
        ),

        "source_url": (
            "https://chuhai.edu.hk/en/"
            "overseas-candidates"
        ),

        "gpa_status": (
            "No universal numeric GPA minimum verified. "
            "Academic entry requirements are based on "
            "the applicant's international qualification."
        ),

        "english_status": (
            "IELTS and TOEFL requirements verified. "
            "TOEFL uses different official score scales "
            "depending on the test-result date."
        ),

        "accepted_tests": (
            "IELTS; TOEFL; ACT; AP; GCE/IAL; "
            "GCSE/IGCSE; IB; SAT; SPM/STPM; UEC"
        ),

        "numeric_minimum_status": (
            "IELTS overall 5.5 stored. TOEFL numeric "
            "field intentionally blank because the "
            "official requirement is 70 on the older "
            "iBT scale or 3.5 for results obtained "
            "after 21 January 2026."
        ),

        "reason": (
            "Hong Kong Chu Hai College official "
            "international undergraduate requirements "
            "specify IELTS 5.5. TOEFL has a "
            "test-date-dependent score scale, which "
            "cannot be represented safely by EduPath's "
            "single numeric TOEFL field. No universal "
            "GPA value is stored."
        ),
    },


    # -------------------------------------------------
    # Saint Francis University
    # prog_hk_037 - prog_hk_039
    # -------------------------------------------------

    "uni_hk_013": {
        "ielts": "5.5",
        "toefl": "",

        "source_name": (
            "Saint Francis University - "
            "International Qualifications "
            "(Non-local Applicants)"
        ),

        "source_url": (
            "https://www.sfu.edu.hk/en/admission/"
            "admission/international-qualifications/"
            "index.html"
        ),

        "gpa_status": (
            "No universal numeric GPA minimum verified "
            "for international Year 1 undergraduate "
            "admission. Entry is qualification-based."
        ),

        "english_status": (
            "General international undergraduate "
            "English requirement verified. TOEFL uses "
            "different official score scales according "
            "to test date."
        ),

        "accepted_tests": (
            "IELTS; TOEFL; GCE; GCSE/IGCSE; "
            "IB; TOEIC; SAT; equivalent qualifications"
        ),

        "numeric_minimum_status": (
            "IELTS overall 5.5 stored. TOEFL numeric "
            "field intentionally blank because the "
            "official undergraduate requirement is "
            "70 before 21 January 2026 or 3.5 from "
            "21 January 2026 onwards."
        ),

        "reason": (
            "SFU official international qualification "
            "requirements specify IELTS 5.5 for "
            "undergraduate applicants and a "
            "date-dependent TOEFL scale. The current "
            "EduPath schema cannot safely represent both "
            "TOEFL scales with one numeric field. "
            "No universal GPA is stored."
        ),
    },


    # -------------------------------------------------
    # THEi
    # prog_hk_040 - prog_hk_042
    # -------------------------------------------------

    "uni_hk_014": {
        "ielts": "5.5",
        "toefl": "79",

        "source_name": (
            "THEi International Student - "
            "Entry Requirements and Fee"
        ),

        "source_url": (
            "https://thei.edu.hk/admission/"
            "international-student-fee/"
            "entry-requirements-fee/"
        ),

        "gpa_status": (
            "No universal numeric GPA minimum verified. "
            "Non-local academic qualifications are "
            "assessed individually by the departments."
        ),

        "english_status": (
            "English requirement for non-local degree "
            "applicants verified."
        ),

        "accepted_tests": (
            "IELTS Academic; TOEFL; GCSE/IGCSE/GCE; "
            "IB; SAT; ACT; equivalent qualifications"
        ),

        "numeric_minimum_status": (
            "IELTS Academic 5.5 and TOEFL iBT 79 "
            "verified. No universal GPA value stored."
        ),

        "reason": (
            "THEi official non-local entry requirements "
            "specify IELTS Academic overall 5.5 and "
            "TOEFL iBT 79 for degree programmes. "
            "Non-local academic qualifications are "
            "assessed individually, so no universal "
            "numeric GPA is stored."
        ),
    },


    # -------------------------------------------------
    # Tung Wah College
    # prog_hk_043 - prog_hk_045
    # -------------------------------------------------

    "uni_hk_015": {
        "ielts": "5.5",
        "toefl": "",

        "source_name": (
            "Tung Wah College - Admission Requirements "
            "for Non-local Bachelor's Degree Applicants"
        ),

        "source_url": (
            "https://www.twc.edu.hk/en/"
            "Administration_Units/reg/our_service/"
            "prospective_students/non-local_admission"
        ),

        "gpa_status": (
            "No universal numeric GPA minimum verified "
            "for Year 1 non-local bachelor admission. "
            "Academic admission depends on the "
            "applicant's qualification."
        ),

        "english_status": (
            "Non-local bachelor's degree English "
            "requirement verified. TOEFL uses "
            "date-dependent score scales."
        ),

        "accepted_tests": (
            "IELTS Academic; TOEFL; GCE; GCSE/IGCSE; "
            "SAT; recognised international "
            "English qualifications"
        ),

        "numeric_minimum_status": (
            "IELTS Academic 5.5 stored. TOEFL numeric "
            "field intentionally blank because the "
            "official requirement is 70 before "
            "21 January 2026 or 4 from "
            "21 January 2026 onwards."
        ),

        "reason": (
            "Tung Wah College official non-local "
            "bachelor admission requirements specify "
            "IELTS Academic 5.5. TOEFL uses different "
            "score scales depending on test date, so "
            "one TOEFL numeric value is not stored. "
            "No universal GPA value is stored."
        ),
    },
}


EXPECTED_UNIVERSITIES = {
    "prog_hk_031": "uni_hk_011",
    "prog_hk_032": "uni_hk_011",
    "prog_hk_033": "uni_hk_011",

    "prog_hk_034": "uni_hk_012",
    "prog_hk_035": "uni_hk_012",
    "prog_hk_036": "uni_hk_012",

    "prog_hk_037": "uni_hk_013",
    "prog_hk_038": "uni_hk_013",
    "prog_hk_039": "uni_hk_013",

    "prog_hk_040": "uni_hk_014",
    "prog_hk_041": "uni_hk_014",
    "prog_hk_042": "uni_hk_014",

    "prog_hk_043": "uni_hk_015",
    "prog_hk_044": "uni_hk_015",
    "prog_hk_045": "uni_hk_015",
}


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 96)
    print(
        "STEP 169.2AU.2 - APPLY HONG KONG "
        "REQUIREMENTS BATCH R3"
    )
    print("=" * 96)

    if not QUEUE_PATH.exists():
        raise FileNotFoundError(
            f"Requirements queue not found: {QUEUE_PATH}"
        )


    # -------------------------------------------------
    # Read queue
    # -------------------------------------------------

    with QUEUE_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        headers = reader.fieldnames

        rows = list(reader)


    if headers is None:
        raise ValueError(
            "Requirements queue has no headers."
        )

    if len(rows) != 45:
        raise ValueError(
            f"Expected 45 queue rows, found {len(rows)}."
        )


    row_by_id = {
        clean(row["program_id"]): row
        for row in rows
    }


    # -------------------------------------------------
    # Verify completed R1 + R2
    # -------------------------------------------------

    for i in range(1, 31):

        program_id = (
            f"prog_hk_{i:03d}"
        )

        if clean(
            row_by_id[
                program_id
            ][
                "requirements_research_status"
            ]
        ) != "VERIFIED":

            raise ValueError(
                f"{program_id}: R1/R2 is no longer "
                "VERIFIED."
            )


    # -------------------------------------------------
    # R3 safety audit
    # -------------------------------------------------

    research_fields = [
        "minimum_gpa",
        "gpa_scale",
        "ielts_requirement",
        "toefl_requirement",
        "gpa_status",
        "english_status",
        "accepted_tests",
        "numeric_minimum_status",
        "requirements_source_name",
        "requirements_source_url",
        "requirements_reason",
        "verified_at",
    ]


    for program_id in R3_IDS:

        if program_id not in row_by_id:
            raise ValueError(
                f"Missing R3 programme: {program_id}"
            )

        row = row_by_id[
            program_id
        ]

        expected_university = (
            EXPECTED_UNIVERSITIES[
                program_id
            ]
        )

        actual_university = clean(
            row["university_id"]
        )

        if actual_university != expected_university:
            raise ValueError(
                f"{program_id}: expected "
                f"{expected_university}, found "
                f"{actual_university}."
            )

        status = clean(
            row[
                "requirements_research_status"
            ]
        )

        if status != "PENDING":
            raise ValueError(
                f"{program_id}: expected PENDING, "
                f"found {status!r}."
            )

        for field in research_fields:

            if clean(row[field]):

                raise ValueError(
                    f"{program_id}: {field} was "
                    "unexpectedly prefilled."
                )


    # -------------------------------------------------
    # Backup immediately before write
    # -------------------------------------------------

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = BACKUP_DIR / (
        "hong_kong_program_requirements_queue_"
        f"before_r3_apply_{timestamp}.csv"
    )

    shutil.copy2(
        QUEUE_PATH,
        backup_path,
    )

    print(
        "Backup:",
        backup_path,
    )


    # -------------------------------------------------
    # Apply verified R3 requirements
    # -------------------------------------------------

    updated = 0

    for program_id in R3_IDS:

        row = row_by_id[
            program_id
        ]

        university_id = clean(
            row["university_id"]
        )

        requirement = (
            UNIVERSITY_REQUIREMENTS[
                university_id
            ]
        )

        # No universal Year-1 GPA verified.
        row["minimum_gpa"] = ""
        row["gpa_scale"] = ""

        row["ielts_requirement"] = (
            requirement["ielts"]
        )

        row["toefl_requirement"] = (
            requirement["toefl"]
        )

        row[
            "requirements_research_status"
        ] = "VERIFIED"

        row["gpa_status"] = (
            requirement["gpa_status"]
        )

        row["english_status"] = (
            requirement["english_status"]
        )

        row["accepted_tests"] = (
            requirement["accepted_tests"]
        )

        row["numeric_minimum_status"] = (
            requirement[
                "numeric_minimum_status"
            ]
        )

        row["requirements_source_name"] = (
            requirement["source_name"]
        )

        row["requirements_source_url"] = (
            requirement["source_url"]
        )

        row["requirements_reason"] = (
            requirement["reason"]
        )

        row["verified_at"] = VERIFIED_AT

        updated += 1


    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    with QUEUE_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=headers,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    # -------------------------------------------------
    # Re-read and verify
    # -------------------------------------------------

    with QUEUE_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        saved_rows = list(
            csv.DictReader(file)
        )


    saved_by_id = {
        clean(row["program_id"]): row
        for row in saved_rows
    }


    all_verified = sum(
        clean(
            row[
                "requirements_research_status"
            ]
        )
        == "VERIFIED"
        for row in saved_rows
    )


    r3 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(31, 46)
    ]


    r3_verified = sum(
        clean(
            row[
                "requirements_research_status"
            ]
        )
        == "VERIFIED"
        for row in r3
    )


    blank_source = sum(
        not clean(
            row[
                "requirements_source_url"
            ]
        )
        for row in r3
    )


    blank_reason = sum(
        not clean(
            row[
                "requirements_reason"
            ]
        )
        for row in r3
    )


    blank_verified_at = sum(
        not clean(
            row["verified_at"]
        )
        for row in r3
    )


    numeric_gpa_stored = sum(
        bool(clean(row["minimum_gpa"]))
        or bool(clean(row["gpa_scale"]))
        for row in r3
    )


    ielts_stored = sum(
        bool(
            clean(
                row["ielts_requirement"]
            )
        )
        for row in r3
    )


    toefl_stored = sum(
        bool(
            clean(
                row["toefl_requirement"]
            )
        )
        for row in r3
    )


    print()

    print(
        "R3 rows updated                 :",
        updated,
    )

    print(
        "R3 VERIFIED                     :",
        r3_verified,
    )

    print(
        "Total VERIFIED                  :",
        all_verified,
    )

    print(
        "R3 blank source URL             :",
        blank_source,
    )

    print(
        "R3 blank evidence reason        :",
        blank_reason,
    )

    print(
        "R3 blank verified_at            :",
        blank_verified_at,
    )

    print(
        "R3 numeric GPA values stored    :",
        numeric_gpa_stored,
    )

    print(
        "R3 IELTS numeric values stored  :",
        ielts_stored,
    )

    print(
        "R3 TOEFL numeric values stored  :",
        toefl_stored,
    )


    # -------------------------------------------------
    # Assertions
    # -------------------------------------------------

    if updated != 15:
        raise ValueError(
            "Expected exactly 15 R3 updates."
        )

    if r3_verified != 15:
        raise ValueError(
            "Expected 15 R3 VERIFIED rows."
        )

    if all_verified != 45:
        raise ValueError(
            "All 45 requirements rows must now "
            "be VERIFIED."
        )

    if (
        blank_source
        or blank_reason
        or blank_verified_at
    ):
        raise ValueError(
            "R3 evidence metadata is incomplete."
        )

    if numeric_gpa_stored != 0:
        raise ValueError(
            "Unexpected universal numeric GPA "
            "values were stored."
        )

    if ielts_stored != 15:
        raise ValueError(
            "Expected IELTS numeric values for "
            "all 15 R3 rows."
        )

    # Only HSUHK 3 + THEi 3 have a single,
    # safely representable current TOEFL number.
    if toefl_stored != 6:
        raise ValueError(
            "Expected exactly 6 R3 TOEFL "
            "numeric values."
        )


    print()
    print("=" * 96)

    print(
        "STEP 169.2AU.2 REQUIREMENTS "
        "BATCH R3 APPLY: PASS"
    )

    print(
        "ALL 45 REQUIREMENTS RESEARCH "
        "ROWS ARE VERIFIED"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 96)


if __name__ == "__main__":
    main()
