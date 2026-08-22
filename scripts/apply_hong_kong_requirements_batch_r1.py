import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "16_hong_kong_program_requirements_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2as"
)

VERIFIED_AT = "2026-08-21"


R1_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(1, 16)
]


def official_url(host, path):
    return "https://" + host + path


HKU_SOURCE = official_url(
    "admissions.hku.hk",
    "/apply/international-qualifications/"
    "english-language-requirement",
)

CUHK_SOURCE = official_url(
    "admission.cuhk.edu.hk",
    "/application/overseas-other-qualifications-"
    "non-local-international-team/requirements/",
)

HKUST_SOURCE = official_url(
    "join.hkust.edu.hk",
    "/oas/elar.pdf",
)

POLYU_SOURCE = official_url(
    "www.polyu.edu.hk",
    "/study/ug/admissions/"
    "international-other-qualifications/"
    "international-other-qualifications-english",
)

CITYU_SOURCE = official_url(
    "www.cityu.edu.hk",
    "/admo/faq",
)


UNIVERSITY_REQUIREMENTS = {
    "uni_hk_001": {
        "ielts": "6.5",
        "toefl": "93",
        "source_name": (
            "HKU International Qualifications - "
            "English Language Requirement"
        ),
        "source_url": HKU_SOURCE,
        "gpa_status": (
            "No universal numeric GPA minimum verified; "
            "academic entrance thresholds depend on the "
            "applicant's qualification or country."
        ),
        "english_status": (
            "University-wide international undergraduate "
            "English minimum verified."
        ),
        "accepted_tests": (
            "IELTS Academic; TOEFL iBT"
        ),
        "numeric_minimum_status": (
            "IELTS 6.5 and TOEFL iBT 93 verified; "
            "universal GPA minimum not stored."
        ),
        "reason": (
            "HKU official international admissions requirements "
            "specify IELTS Academic 6.5 and TOEFL iBT 93. "
            "Academic lower boundaries vary by qualification, "
            "so a universal GPA value is not stored."
        ),
    },

    "uni_hk_002": {
        "ielts": "6.0",
        "toefl": "80",
        "source_name": (
            "CUHK International Students Admissions "
            "Requirements"
        ),
        "source_url": CUHK_SOURCE,
        "gpa_status": (
            "No universal numeric GPA minimum verified; "
            "general academic requirements are "
            "qualification-specific."
        ),
        "english_status": (
            "University-wide international undergraduate "
            "English minimum verified."
        ),
        "accepted_tests": (
            "IELTS Academic; TOEFL iBT"
        ),
        "numeric_minimum_status": (
            "IELTS 6.0 verified. TOEFL 80 on the "
            "0-120 reporting scale is retained; official "
            "2026 requirements also document the new "
            "TOEFL reporting scale."
        ),
        "reason": (
            "CUHK official international admission requirements "
            "specify IELTS Academic 6.0. For 2026 entry the "
            "official TOEFL requirement documents 80 on the "
            "0-120 scale together with the newer reporting "
            "scale. Academic admission thresholds vary by "
            "qualification, so no universal GPA is stored."
        ),
    },

    "uni_hk_003": {
        "ielts": "6.0",
        "toefl": "",
        "source_name": (
            "HKUST University's English Language "
            "Admissions Requirement"
        ),
        "source_url": HKUST_SOURCE,
        "gpa_status": (
            "No universal numeric GPA minimum verified; "
            "academic requirements depend on qualification "
            "and school/program-specific criteria."
        ),
        "english_status": (
            "IELTS requirement verified. TOEFL requirement "
            "verified but uses different official score scales "
            "depending on test date."
        ),
        "accepted_tests": (
            "IELTS Academic; TOEFL iBT"
        ),
        "numeric_minimum_status": (
            "IELTS 6.0 stored. TOEFL numeric field intentionally "
            "left blank because HKUST specifies 80 before "
            "21 January 2026 and 4.5 from 21 January 2026, "
            "while the current EduPath schema has no TOEFL "
            "score-scale field."
        ),
        "reason": (
            "HKUST official undergraduate English requirements "
            "specify IELTS Academic 6.0. TOEFL iBT uses a "
            "test-date-dependent score scale in 2026, so one "
            "numeric TOEFL value would be ambiguous in the "
            "current schema. No universal GPA is stored."
        ),
    },

    "uni_hk_004": {
        "ielts": "6.0",
        "toefl": "80",
        "source_name": (
            "PolyU International / Other Qualifications - "
            "English Language Requirements"
        ),
        "source_url": POLYU_SOURCE,
        "gpa_status": (
            "No universal numeric GPA minimum verified; "
            "general entrance requirements vary by "
            "international qualification."
        ),
        "english_status": (
            "General non-local undergraduate English "
            "minimum verified; no higher English cutoff "
            "identified for these R1 programmes."
        ),
        "accepted_tests": (
            "IELTS Academic; TOEFL iBT"
        ),
        "numeric_minimum_status": (
            "IELTS 6.0 and TOEFL iBT 80 verified; "
            "universal GPA minimum not stored."
        ),
        "reason": (
            "PolyU official non-local undergraduate requirements "
            "specify IELTS Academic 6.0 and TOEFL iBT 80 unless "
            "an individual programme specifies otherwise. "
            "No separate higher English cutoff was identified "
            "for the three R1 PolyU programmes."
        ),
    },

    "uni_hk_005": {
        "ielts": "6.5",
        "toefl": "79",
        "source_name": (
            "CityUHK Undergraduate Admissions FAQ"
        ),
        "source_url": CITYU_SOURCE,
        "gpa_status": (
            "No universal numeric GPA minimum verified; "
            "academic entry requirements depend on the "
            "qualification and admission route."
        ),
        "english_status": (
            "General undergraduate English minimum "
            "verified."
        ),
        "accepted_tests": (
            "IELTS; TOEFL iBT"
        ),
        "numeric_minimum_status": (
            "IELTS 6.5 and TOEFL iBT 79 verified; "
            "universal GPA minimum not stored."
        ),
        "reason": (
            "CityUHK official undergraduate admissions FAQ "
            "specifies IELTS overall 6.5 or TOEFL iBT 79 "
            "for applicants whose entrance qualification "
            "was obtained in a language other than English. "
            "No universal GPA is stored."
        ),
    },
}


EXPECTED_UNIVERSITIES = {
    "prog_hk_001": "uni_hk_001",
    "prog_hk_002": "uni_hk_001",
    "prog_hk_003": "uni_hk_001",

    "prog_hk_004": "uni_hk_002",
    "prog_hk_005": "uni_hk_002",
    "prog_hk_006": "uni_hk_002",

    "prog_hk_007": "uni_hk_003",
    "prog_hk_008": "uni_hk_003",
    "prog_hk_009": "uni_hk_003",

    "prog_hk_010": "uni_hk_004",
    "prog_hk_011": "uni_hk_004",
    "prog_hk_012": "uni_hk_004",

    "prog_hk_013": "uni_hk_005",
    "prog_hk_014": "uni_hk_005",
    "prog_hk_015": "uni_hk_005",
}


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def main():
    print("=" * 96)
    print(
        "STEP 169.2AS.2 - APPLY HONG KONG "
        "REQUIREMENTS BATCH R1"
    )
    print("=" * 96)

    if not QUEUE_PATH.exists():
        raise FileNotFoundError(
            f"Requirements queue not found: {QUEUE_PATH}"
        )

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

    missing_ids = [
        program_id
        for program_id in R1_IDS
        if program_id not in row_by_id
    ]

    if missing_ids:
        raise ValueError(
            "Missing R1 IDs: "
            + ", ".join(missing_ids)
        )

    # ---------------------------------------------
    # Safety validation before modifying anything
    # ---------------------------------------------

    for program_id in R1_IDS:
        row = row_by_id[program_id]

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
                f"{program_id}: expected PENDING "
                f"before R1 update, found {status!r}."
            )

        for field in [
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
        ]:
            if clean(row[field]):
                raise ValueError(
                    f"{program_id}: field {field} "
                    "was unexpectedly prefilled."
                )

    # ---------------------------------------------
    # Backup immediately before the write
    # ---------------------------------------------

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = BACKUP_DIR / (
        "hong_kong_program_requirements_queue_"
        f"before_r1_apply_{timestamp}.csv"
    )

    shutil.copy2(
        QUEUE_PATH,
        backup_path,
    )

    print(
        "Backup:",
        backup_path,
    )

    # ---------------------------------------------
    # Apply verified R1 evidence
    # ---------------------------------------------

    updated = 0

    for program_id in R1_IDS:
        row = row_by_id[program_id]

        university_id = clean(
            row["university_id"]
        )

        requirement = (
            UNIVERSITY_REQUIREMENTS[
                university_id
            ]
        )

        # GPA intentionally remains blank because
        # no universal numeric GPA was verified.
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

    # ---------------------------------------------
    # Save queue
    # ---------------------------------------------

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
        writer.writerows(rows)

    # ---------------------------------------------
    # Post-write verification
    # ---------------------------------------------

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
        saved_by_id[program_id]
        for program_id in R1_IDS
    ]

    r2_r3 = [
        row
        for row in saved_rows
        if row["program_id"]
        not in set(R1_IDS)
    ]

    verified_count = sum(
        clean(
            row[
                "requirements_research_status"
            ]
        )
        == "VERIFIED"
        for row in r1
    )

    pending_remaining = sum(
        clean(
            row[
                "requirements_research_status"
            ]
        )
        == "PENDING"
        for row in r2_r3
    )

    blank_source = sum(
        not clean(
            row["requirements_source_url"]
        )
        for row in r1
    )

    blank_reason = sum(
        not clean(
            row["requirements_reason"]
        )
        for row in r1
    )

    blank_verified_at = sum(
        not clean(
            row["verified_at"]
        )
        for row in r1
    )

    gpa_values_stored = sum(
        bool(clean(row["minimum_gpa"]))
        or bool(clean(row["gpa_scale"]))
        for row in r1
    )

    ielts_stored = sum(
        bool(
            clean(
                row["ielts_requirement"]
            )
        )
        for row in r1
    )

    toefl_stored = sum(
        bool(
            clean(
                row["toefl_requirement"]
            )
        )
        for row in r1
    )

    print()
    print(
        "R1 rows updated                 :",
        updated,
    )

    print(
        "R1 VERIFIED                     :",
        verified_count,
    )

    print(
        "R2/R3 PENDING                   :",
        pending_remaining,
    )

    print(
        "R1 blank source URL             :",
        blank_source,
    )

    print(
        "R1 blank evidence reason        :",
        blank_reason,
    )

    print(
        "R1 blank verified_at            :",
        blank_verified_at,
    )

    print(
        "R1 numeric GPA values stored    :",
        gpa_values_stored,
    )

    print(
        "R1 IELTS numeric values stored  :",
        ielts_stored,
    )

    print(
        "R1 TOEFL numeric values stored  :",
        toefl_stored,
    )

    if verified_count != 15:
        raise ValueError(
            "R1 verification count is not 15."
        )

    if pending_remaining != 30:
        raise ValueError(
            "R2/R3 must remain 30 PENDING rows."
        )

    if (
        blank_source
        or blank_reason
        or blank_verified_at
    ):
        raise ValueError(
            "R1 evidence metadata is incomplete."
        )

    if gpa_values_stored != 0:
        raise ValueError(
            "R1 unexpectedly contains universal "
            "numeric GPA values."
        )

    if ielts_stored != 15:
        raise ValueError(
            "Expected IELTS numeric evidence "
            "for all 15 R1 rows."
        )

    # HKUST 007-009 intentionally have no single
    # TOEFL numeric value due the 2026 scale change.
    if toefl_stored != 12:
        raise ValueError(
            "Expected exactly 12 stored TOEFL "
            "numeric values in R1."
        )

    print()
    print("=" * 96)
    print(
        "STEP 169.2AS.2 REQUIREMENTS "
        "BATCH R1 APPLY: PASS"
    )
    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )
    print("=" * 96)


if __name__ == "__main__":
    main()
