import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "16_hong_kong_program_requirements_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2at"
)

VERIFIED_AT = "2026-08-21"


R2_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(16, 31)
]


def official_url(host, path):
    return "https://" + host + path


HKBU_SOURCE = official_url(
    "admissions.hkbu.edu.hk",
    "/admissions/international-qualifications.html",
)

LINGNAN_SOURCE = official_url(
    "www.ln.edu.hk",
    "/admissions/ug/apply-now/"
    "overseas-and-mainland-applicants-holding-"
    "international-qualifications",
)

EDUHK_SOURCE = official_url(
    "www.apply.eduhk.hk",
    "/ug/nonlocal",
)

HKMU_SOURCE = official_url(
    "admissions.hkmu.edu.hk",
    "/ug/entry_requirements/",
)

HKSYU_SOURCE = official_url(
    "uao.hksyu.edu",
    "/en/student-admission/non-local_international",
)


UNIVERSITY_REQUIREMENTS = {

    # -------------------------------------------------
    # Hong Kong Baptist University
    # prog_hk_016 - prog_hk_018
    # -------------------------------------------------

    "uni_hk_006": {
        "ielts": "6.0",
        "toefl": "79",

        "source_name": (
            "HKBU Undergraduate Admissions - "
            "International Qualifications"
        ),

        "source_url": HKBU_SOURCE,

        "gpa_status": (
            "No universal numeric GPA minimum verified. "
            "Academic entrance requirements depend on "
            "the applicant's qualification or region."
        ),

        "english_status": (
            "General international undergraduate "
            "English minimum verified."
        ),

        "accepted_tests": (
            "IELTS Academic; TOEFL iBT; "
            "other recognised English qualifications"
        ),

        "numeric_minimum_status": (
            "IELTS Academic 6.0 and TOEFL iBT 79 "
            "verified. No universal GPA value stored."
        ),

        "reason": (
            "HKBU official international admissions "
            "requirements specify IELTS Academic 6.0 "
            "and TOEFL iBT 79. Myanmar academic entry "
            "is qualification-based rather than based "
            "on one universal GPA threshold."
        ),
    },


    # -------------------------------------------------
    # Lingnan University
    # prog_hk_019 - prog_hk_021
    # -------------------------------------------------

    "uni_hk_007": {
        "ielts": "6.0",
        "toefl": "",

        "source_name": (
            "Lingnan Undergraduate Admissions - "
            "International Qualifications"
        ),

        "source_url": LINGNAN_SOURCE,

        "gpa_status": (
            "No universal numeric GPA minimum verified. "
            "Academic thresholds are qualification-specific."
        ),

        "english_status": (
            "IELTS Academic minimum verified. "
            "TOEFL is recognised, but a current numeric "
            "cutoff was not independently verified in this "
            "evidence pass."
        ),

        "accepted_tests": (
            "IELTS Academic; TOEFL; "
            "other recognised English qualifications"
        ),

        "numeric_minimum_status": (
            "IELTS Academic 6.0 stored. TOEFL numeric "
            "field intentionally left blank rather than "
            "inferring a current cutoff."
        ),

        "reason": (
            "Lingnan's official international-qualifications "
            "admissions information confirms IELTS Academic "
            "overall 6.0 and recognises TOEFL. This pass does "
            "not store a TOEFL number without sufficiently "
            "clear current official numeric evidence. "
            "No universal GPA is stored."
        ),
    },


    # -------------------------------------------------
    # Education University of Hong Kong
    # prog_hk_022 - prog_hk_024
    # -------------------------------------------------

    "uni_hk_008": {
        "ielts": "6.0",
        "toefl": "",

        "source_name": (
            "EdUHK International Qualifications - "
            "Entrance Requirements"
        ),

        "source_url": EDUHK_SOURCE,

        "gpa_status": (
            "No universal numeric GPA minimum verified. "
            "General entrance thresholds depend on the "
            "applicant's international qualification."
        ),

        "english_status": (
            "IELTS requirement verified. TOEFL requirement "
            "is verified but uses different score scales "
            "depending on the test date."
        ),

        "accepted_tests": (
            "IELTS Academic; TOEFL iBT; "
            "PTE Academic; other recognised tests"
        ),

        "numeric_minimum_status": (
            "IELTS Academic 6.0 stored. TOEFL numeric field "
            "left blank because EdUHK specifies 80 for tests "
            "before 21 January 2026 and 4 for tests on or "
            "after 21 January 2026."
        ),

        "reason": (
            "EdUHK official international undergraduate "
            "requirements specify IELTS Academic 6.0. "
            "TOEFL uses a test-date-dependent score scale, "
            "which cannot be represented safely by the "
            "current single numeric EduPath TOEFL field. "
            "No universal GPA is stored."
        ),
    },


    # -------------------------------------------------
    # Hong Kong Metropolitan University
    # prog_hk_025 - prog_hk_027
    # -------------------------------------------------

    "uni_hk_009": {
        "ielts": "6.0",
        "toefl": "79",

        "source_name": (
            "HKMU Undergraduate Admissions - "
            "Entry Requirements"
        ),

        "source_url": HKMU_SOURCE,

        "gpa_status": (
            "No universal numeric GPA minimum verified. "
            "General academic entrance requirements vary "
            "by qualification."
        ),

        "english_status": (
            "General full-time undergraduate English "
            "minimum verified."
        ),

        "accepted_tests": (
            "IELTS Academic; TOEFL; "
            "other recognised English qualifications"
        ),

        "numeric_minimum_status": (
            "IELTS Academic 6.0 and TOEFL iBT 79 "
            "verified. No universal GPA value stored."
        ),

        "reason": (
            "HKMU official undergraduate entry requirements "
            "specify IELTS Academic 6.0 and TOEFL iBT 79. "
            "Academic entry requirements are based on the "
            "applicant's qualification, so no universal "
            "GPA threshold is stored."
        ),
    },


    # -------------------------------------------------
    # Hong Kong Shue Yan University
    # prog_hk_028 - prog_hk_030
    # -------------------------------------------------

    "uni_hk_010": {
        "ielts": "5.5",
        "toefl": "79",

        "source_name": (
            "HKSYU University Admissions Office - "
            "Non-Local International Students"
        ),

        "source_url": HKSYU_SOURCE,

        "gpa_status": (
            "No universal numeric GPA minimum verified "
            "for all international undergraduate applicants."
        ),

        "english_status": (
            "Non-local undergraduate English minimum "
            "verified."
        ),

        "accepted_tests": (
            "IELTS; TOEFL iBT; "
            "other recognised international examinations"
        ),

        "numeric_minimum_status": (
            "IELTS 5.5 and TOEFL iBT 79 verified. "
            "No universal GPA value stored."
        ),

        "reason": (
            "HKSYU official international admissions "
            "information states a minimum IELTS score of "
            "5.5 or TOEFL internet-based score of 79 for "
            "non-local applicants. No universal numeric "
            "GPA requirement is stored."
        ),
    },
}


EXPECTED_UNIVERSITIES = {

    "prog_hk_016": "uni_hk_006",
    "prog_hk_017": "uni_hk_006",
    "prog_hk_018": "uni_hk_006",

    "prog_hk_019": "uni_hk_007",
    "prog_hk_020": "uni_hk_007",
    "prog_hk_021": "uni_hk_007",

    "prog_hk_022": "uni_hk_008",
    "prog_hk_023": "uni_hk_008",
    "prog_hk_024": "uni_hk_008",

    "prog_hk_025": "uni_hk_009",
    "prog_hk_026": "uni_hk_009",
    "prog_hk_027": "uni_hk_009",

    "prog_hk_028": "uni_hk_010",
    "prog_hk_029": "uni_hk_010",
    "prog_hk_030": "uni_hk_010",
}


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def main():

    print("=" * 96)
    print(
        "STEP 169.2AT.2 - APPLY HONG KONG "
        "REQUIREMENTS BATCH R2"
    )
    print("=" * 96)

    if not QUEUE_PATH.exists():
        raise FileNotFoundError(
            f"Requirements queue not found: {QUEUE_PATH}"
        )


    # -------------------------------------------------
    # Read current research queue
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
            f"Expected 45 rows, found {len(rows)}."
        )


    row_by_id = {
        clean(row["program_id"]): row
        for row in rows
    }


    # -------------------------------------------------
    # Verify all R2 IDs exist
    # -------------------------------------------------

    missing_ids = [
        program_id
        for program_id in R2_IDS
        if program_id not in row_by_id
    ]

    if missing_ids:
        raise ValueError(
            "Missing R2 IDs: "
            + ", ".join(missing_ids)
        )


    # -------------------------------------------------
    # R2 pre-write safety audit
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


    for program_id in R2_IDS:

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
                f"{expected_university}, "
                f"found {actual_university}."
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
                    f"{program_id}: {field} "
                    "was unexpectedly prefilled."
                )


    # -------------------------------------------------
    # Verify R1 is already closed
    # -------------------------------------------------

    r1_ids = {
        f"prog_hk_{i:03d}"
        for i in range(1, 16)
    }

    for program_id in r1_ids:

        if clean(
            row_by_id[
                program_id
            ][
                "requirements_research_status"
            ]
        ) != "VERIFIED":

            raise ValueError(
                f"{program_id}: R1 is no longer VERIFIED."
            )


    # -------------------------------------------------
    # Backup before modifying queue
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
        f"before_r2_apply_{timestamp}.csv"
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
    # Apply R2 official-source evidence
    # -------------------------------------------------

    updated = 0

    for program_id in R2_IDS:

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


        # No universal GPA has been verified.
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

        row["verified_at"] = (
            VERIFIED_AT
        )

        updated += 1


    # -------------------------------------------------
    # Save queue
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
    # Re-read saved queue
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


    r1 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(1, 16)
    ]

    r2 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(16, 31)
    ]

    r3 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(31, 46)
    ]


    # -------------------------------------------------
    # Post-write validation
    # -------------------------------------------------

    r1_verified = sum(
        clean(
            row[
                "requirements_research_status"
            ]
        )
        == "VERIFIED"
        for row in r1
    )

    r2_verified = sum(
        clean(
            row[
                "requirements_research_status"
            ]
        )
        == "VERIFIED"
        for row in r2
    )

    r3_pending = sum(
        clean(
            row[
                "requirements_research_status"
            ]
        )
        == "PENDING"
        for row in r3
    )


    blank_source = sum(
        not clean(
            row[
                "requirements_source_url"
            ]
        )
        for row in r2
    )

    blank_reason = sum(
        not clean(
            row[
                "requirements_reason"
            ]
        )
        for row in r2
    )

    blank_verified_at = sum(
        not clean(
            row["verified_at"]
        )
        for row in r2
    )


    numeric_gpa_stored = sum(
        bool(
            clean(
                row["minimum_gpa"]
            )
        )
        or bool(
            clean(
                row["gpa_scale"]
            )
        )
        for row in r2
    )


    ielts_stored = sum(
        bool(
            clean(
                row[
                    "ielts_requirement"
                ]
            )
        )
        for row in r2
    )


    toefl_stored = sum(
        bool(
            clean(
                row[
                    "toefl_requirement"
                ]
            )
        )
        for row in r2
    )


    print()

    print(
        "R2 rows updated                 :",
        updated,
    )

    print(
        "R1 VERIFIED preserved           :",
        r1_verified,
    )

    print(
        "R2 VERIFIED                     :",
        r2_verified,
    )

    print(
        "R3 PENDING                      :",
        r3_pending,
    )

    print(
        "R2 blank source URL             :",
        blank_source,
    )

    print(
        "R2 blank evidence reason        :",
        blank_reason,
    )

    print(
        "R2 blank verified_at            :",
        blank_verified_at,
    )

    print(
        "R2 numeric GPA values stored    :",
        numeric_gpa_stored,
    )

    print(
        "R2 IELTS numeric values stored  :",
        ielts_stored,
    )

    print(
        "R2 TOEFL numeric values stored  :",
        toefl_stored,
    )


    # -------------------------------------------------
    # Final assertions
    # -------------------------------------------------

    if updated != 15:
        raise ValueError(
            "Expected exactly 15 R2 updates."
        )

    if r1_verified != 15:
        raise ValueError(
            "R1 VERIFIED state was not preserved."
        )

    if r2_verified != 15:
        raise ValueError(
            "Expected all 15 R2 rows VERIFIED."
        )

    if r3_pending != 15:
        raise ValueError(
            "R3 must remain 15 PENDING rows."
        )

    if (
        blank_source
        or blank_reason
        or blank_verified_at
    ):
        raise ValueError(
            "R2 evidence metadata is incomplete."
        )

    if numeric_gpa_stored != 0:
        raise ValueError(
            "Unexpected universal GPA numeric "
            "values were stored."
        )

    if ielts_stored != 15:
        raise ValueError(
            "Expected 15 R2 IELTS values."
        )

    # Lingnan 3 + EdUHK 3 intentionally blank.
    # Therefore 9 TOEFL numeric values are expected.
    if toefl_stored != 9:
        raise ValueError(
            "Expected exactly 9 R2 TOEFL "
            "numeric values."
        )


    print()
    print("=" * 96)

    print(
        "STEP 169.2AT.2 REQUIREMENTS "
        "BATCH R2 APPLY: PASS"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 96)


if __name__ == "__main__":
    main()
