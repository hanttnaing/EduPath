import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "17_hong_kong_program_tuition_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2bc"
)

VERIFIED_AT = "2026-08-21"


T3_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(31, 46)
]


HSUHK_SOURCE = (
    "https://admission.hsu.edu.hk/"
    "undergraduate-admissions/year-1-entry/"
    "international-qualification/fees-and-bursaries/"
)

CHUHAI_SOURCE = (
    "https://chuhai.edu.hk/en/"
    "overseas-candidates"
)

SFU_SOURCE = (
    "https://www.sfu.edu.hk/"
    "filemanager/common/Tuition_Fees_SFU.pdf"
)

TWC_SOURCE = (
    "https://www.twc.edu.hk/en/"
    "Administration_Units/reg/our_service/"
    "prospective_students/non-local_admission/"
    "page/non-local_tuition"
)


CONFIG = {

    # -------------------------------------------------
    # HSUHK
    # -------------------------------------------------

    "prog_hk_031": {
        "status": "VERIFIED",
        "fee": "153820",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local Year-1 undergraduate student"
        ),
        "year": "2026/27",
        "basis": (
            "First-year annual tuition; "
            "SSSDP subsidy not available to non-local students"
        ),
        "source_name": (
            "HSUHK International Qualifications - "
            "Fees and Bursaries"
        ),
        "source_url": HSUHK_SOURCE,
        "reason": (
            "Bachelor of Science (Honours) in Applied "
            "Computing is a 2026/27 SSSDP programme. "
            "HSUHK publishes HKD153,820 as the first-year "
            "full tuition fee for non-local students in "
            "SSSDP programmes other than Art and Design."
        ),
    },

    "prog_hk_032": {
        "status": "VERIFIED",
        "fee": "153820",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local Year-1 undergraduate student"
        ),
        "year": "2026/27",
        "basis": (
            "First-year annual tuition; "
            "SSSDP subsidy not available to non-local students"
        ),
        "source_name": (
            "HSUHK International Qualifications - "
            "Fees and Bursaries"
        ),
        "source_url": HSUHK_SOURCE,
        "reason": (
            "Bachelor of Science (Honours) in Data Science "
            "and Business Intelligence is a 2026/27 SSSDP "
            "programme. HSUHK publishes HKD153,820 as the "
            "first-year full tuition fee for non-local "
            "students in this programme category."
        ),
    },

    "prog_hk_033": {
        "status": "VERIFIED",
        "fee": "153820",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local Year-1 undergraduate student"
        ),
        "year": "2026/27",
        "basis": (
            "First-year annual tuition; "
            "SSSDP subsidy not available to non-local students"
        ),
        "source_name": (
            "HSUHK International Qualifications - "
            "Fees and Bursaries"
        ),
        "source_url": HSUHK_SOURCE,
        "reason": (
            "Bachelor of Science (Honours) in Business "
            "Analytics and Information Management is a "
            "2026/27 SSSDP programme. HSUHK publishes "
            "HKD153,820 as the first-year full tuition "
            "fee for non-local students in this category."
        ),
    },


    # -------------------------------------------------
    # Hong Kong Chu Hai College
    # -------------------------------------------------

    "prog_hk_034": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": (
            "Non-local Year-1 applicability requires "
            "programme-specific re-verification"
        ),
        "year": "2026/27",
        "basis": (
            "No numeric tuition stored"
        ),
        "source_name": (
            "Hong Kong Chu Hai College - "
            "International Qualifications"
        ),
        "source_url": CHUHAI_SOURCE,
        "reason": (
            "Chu Hai publishes HKD104,750 per year for "
            "2026/27 non-local students in four-year degree "
            "programmes generally. However, Computer Science "
            "has programme-specific non-local admission "
            "restriction evidence in official materials. "
            "The generic tuition is therefore not applied "
            "until programme-specific eligibility is "
            "re-verified."
        ),
    },

    "prog_hk_035": {
        "status": "VERIFIED",
        "fee": "104750",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local international undergraduate student"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "Hong Kong Chu Hai College - "
            "International Qualifications"
        ),
        "source_url": CHUHAI_SOURCE,
        "reason": (
            "Chu Hai's current international qualifications "
            "page publishes HKD104,750 per year for non-local "
            "students in 2026/27 four-year degree programmes. "
            "Finance and Information Management is a four-year "
            "undergraduate programme."
        ),
    },

    "prog_hk_036": {
        "status": "VERIFIED",
        "fee": "104750",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local international undergraduate student"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "Hong Kong Chu Hai College - "
            "International Qualifications"
        ),
        "source_url": CHUHAI_SOURCE,
        "reason": (
            "Chu Hai's current international qualifications "
            "page publishes HKD104,750 per year for non-local "
            "students in 2026/27 four-year degree programmes. "
            "Communication and Digital Media is a four-year "
            "undergraduate programme."
        ),
    },


    # -------------------------------------------------
    # Saint Francis University
    # -------------------------------------------------

    "prog_hk_037": {
        "status": "VERIFIED",
        "fee": "100170",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": (
            "Year-1 tuition for 2026/27 entry"
        ),
        "source_name": (
            "Saint Francis University "
            "Tuition Fees 2026-27"
        ),
        "source_url": SFU_SOURCE,
        "reason": (
            "SFU's official 2026/27 tuition schedule "
            "publishes HKD100,170 as the Year-1 non-local "
            "tuition for the full-time Bachelor of Business "
            "Administration (Honours)."
        ),
    },

    "prog_hk_038": {
        "status": "VERIFIED",
        "fee": "100170",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": (
            "Year-1 tuition for 2026/27 entry"
        ),
        "source_name": (
            "Saint Francis University "
            "Tuition Fees 2026-27"
        ),
        "source_url": SFU_SOURCE,
        "reason": (
            "SFU's official 2026/27 tuition schedule "
            "publishes HKD100,170 as the Year-1 non-local "
            "tuition for the full-time Bachelor of Arts "
            "(Honours) in Translation Technology."
        ),
    },

    "prog_hk_039": {
        "status": "VERIFIED",
        "fee": "106670",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": (
            "Year-1 tuition for 2026/27 entry"
        ),
        "source_name": (
            "Saint Francis University "
            "Tuition Fees 2026-27"
        ),
        "source_url": SFU_SOURCE,
        "reason": (
            "SFU's official 2026/27 tuition schedule "
            "publishes HKD106,670 as the Year-1 non-local "
            "tuition for the full-time Bachelor of Science "
            "(Honours) in Artificial Intelligence and "
            "Multimedia Technology."
        ),
    },


    # -------------------------------------------------
    # THEi
    #
    # Official fee is verified, but it is PER CREDIT.
    # Current EduPath tuition_period contract accepts:
    # Annual / Semester / Total only.
    # -------------------------------------------------

    "prog_hk_040": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": (
            "Official fee is HKD4,365 per credit; "
            "current master schema cannot represent "
            "Per Credit safely"
        ),
        "source_name": (
            "THEi Bachelor of Science (Honours) in "
            "Multimedia Technology and Innovation"
        ),
        "source_url": (
            "https://thei.edu.hk/departments/"
            "department-of-digital-innovation-and-technology/"
            "bachelor-of-science-honours-in-"
            "multimedia-technology-and-innovation/"
        ),
        "reason": (
            "THEi officially publishes HKD4,365 per credit "
            "for non-local students in 2026/27. EduPath's "
            "current tuition_period field does not support "
            "Per Credit, so the numeric amount is preserved "
            "in evidence only and is not mislabelled as "
            "Annual, Semester or Total."
        ),
    },

    "prog_hk_041": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": (
            "Official fee is HKD3,635 per credit; "
            "current master schema cannot represent "
            "Per Credit safely"
        ),
        "source_name": (
            "THEi Bachelor of Science (Honours) in "
            "Information and Communications Technology"
        ),
        "source_url": (
            "https://thei.edu.hk/departments/"
            "department-of-digital-innovation-and-technology/"
            "bachelor-of-science-honours-"
            "information-and-communications-technology/"
        ),
        "reason": (
            "THEi officially publishes HKD3,635 per credit "
            "for non-local students in 2026/27. EduPath's "
            "current tuition_period field has no Per Credit "
            "value, so no misleading normalized tuition "
            "amount is stored."
        ),
    },

    "prog_hk_042": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": (
            "Official Year-1 fee is HKD4,520 per credit; "
            "current master schema cannot represent "
            "Per Credit safely"
        ),
        "source_name": (
            "THEi Bachelor of Arts (Honours) "
            "in Fashion Design"
        ),
        "source_url": (
            "https://thei.edu.hk/departments/"
            "department-of-design-and-architecture/"
            "bachelor-of-arts-honours-fashion-design/"
        ),
        "reason": (
            "THEi officially publishes HKD4,520 per credit "
            "for Year-1 non-local students in 2026/27. "
            "The programme also has a different Year-3 "
            "per-credit rate. EduPath's current schema "
            "cannot represent this safely as Annual, "
            "Semester or Total."
        ),
    },


    # -------------------------------------------------
    # Tung Wah College
    # Official page publishes total AND average annual.
    # We store the published average annual value.
    # -------------------------------------------------

    "prog_hk_043": {
        "status": "VERIFIED",
        "fee": "84750",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local first-year-entry undergraduate"
        ),
        "year": "2026/27",
        "basis": (
            "Official published average annual tuition "
            "across the four-year programme"
        ),
        "source_name": (
            "Tung Wah College - Programme and Tuition "
            "Fee for Non-local Applicants 2026/27"
        ),
        "source_url": TWC_SOURCE,
        "reason": (
            "TWC publishes total non-local tuition of "
            "HKD339,000 and average annual tuition of "
            "HKD84,750 for the four-year Bachelor of "
            "Social Science (Honours) in Applied Psychology."
        ),
    },

    "prog_hk_044": {
        "status": "VERIFIED",
        "fee": "86170",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local first-year-entry undergraduate"
        ),
        "year": "2026/27",
        "basis": (
            "Official published average annual tuition "
            "across the four-year programme"
        ),
        "source_name": (
            "Tung Wah College - Programme and Tuition "
            "Fee for Non-local Applicants 2026/27"
        ),
        "source_url": TWC_SOURCE,
        "reason": (
            "TWC publishes total non-local tuition of "
            "HKD344,680 and average annual tuition of "
            "HKD86,170 for the four-year Bachelor of "
            "Management (Honours) in Social and Business "
            "Sustainability."
        ),
    },

    "prog_hk_045": {
        "status": "VERIFIED",
        "fee": "122850",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local first-year-entry undergraduate"
        ),
        "year": "2026/27",
        "basis": (
            "Official published average annual tuition "
            "across the four-year programme"
        ),
        "source_name": (
            "Tung Wah College - Programme and Tuition "
            "Fee for Non-local Applicants 2026/27"
        ),
        "source_url": TWC_SOURCE,
        "reason": (
            "TWC publishes total non-local tuition of "
            "HKD491,400 and average annual tuition of "
            "HKD122,850 for the four-year Bachelor of "
            "Science (Honours) in Biomedical Science."
        ),
    },
}


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 100)
    print(
        "STEP 169.2BC.2 - APPLY HONG KONG "
        "TUITION BATCH T3"
    )
    print("=" * 100)

    if not QUEUE_PATH.exists():
        raise FileNotFoundError(
            f"Tuition queue not found: {QUEUE_PATH}"
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
            "Tuition queue has no headers."
        )

    if len(rows) != 45:
        raise ValueError(
            f"Expected 45 rows, found {len(rows)}."
        )

    if set(CONFIG) != set(T3_IDS):
        raise ValueError(
            "T3 configuration does not match "
            "prog_hk_031 through prog_hk_045."
        )

    row_by_id = {
        clean(row["program_id"]): row
        for row in rows
    }


    # -------------------------------------------------
    # Preserve T1
    # -------------------------------------------------

    for i in range(1, 16):

        program_id = f"prog_hk_{i:03d}"

        if clean(
            row_by_id[program_id][
                "tuition_research_status"
            ]
        ) != "VERIFIED":

            raise ValueError(
                f"{program_id}: T1 is no longer VERIFIED."
            )


    # -------------------------------------------------
    # Preserve closed T2 state
    # -------------------------------------------------

    t2_statuses = [
        clean(
            row_by_id[
                f"prog_hk_{i:03d}"
            ]["tuition_research_status"]
        )
        for i in range(16, 31)
    ]

    if t2_statuses.count("VERIFIED") != 9:
        raise ValueError(
            "T2 VERIFIED count changed."
        )

    if (
        t2_statuses.count(
            "REVIEWED_UNRESOLVED"
        )
        != 6
    ):
        raise ValueError(
            "T2 unresolved count changed."
        )


    # -------------------------------------------------
    # T3 pre-write safety audit
    # -------------------------------------------------

    research_fields = [
        "tuition_fee",
        "tuition_currency",
        "tuition_period",
        "tuition_applicant_scope",
        "tuition_academic_year",
        "tuition_fee_basis",
        "tuition_source_name",
        "tuition_source_url",
        "tuition_reason",
        "verified_at",
    ]

    for program_id in T3_IDS:

        if program_id not in row_by_id:
            raise ValueError(
                f"Missing T3 programme: {program_id}"
            )

        row = row_by_id[
            program_id
        ]

        if clean(
            row["tuition_research_status"]
        ) != "PENDING":

            raise ValueError(
                f"{program_id}: expected PENDING."
            )

        for field in research_fields:

            if clean(row[field]):

                raise ValueError(
                    f"{program_id}: {field} "
                    "unexpectedly prefilled."
                )


    # -------------------------------------------------
    # Backup before write
    # -------------------------------------------------

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = BACKUP_DIR / (
        "hong_kong_program_tuition_queue_"
        f"before_t3_apply_{timestamp}.csv"
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
    # Apply T3
    # -------------------------------------------------

    for program_id in T3_IDS:

        row = row_by_id[
            program_id
        ]

        config = CONFIG[
            program_id
        ]

        row["tuition_fee"] = (
            config["fee"]
        )

        row["tuition_currency"] = (
            config["currency"]
        )

        row["tuition_period"] = (
            config["period"]
        )

        row["tuition_research_status"] = (
            config["status"]
        )

        row["tuition_applicant_scope"] = (
            config["scope"]
        )

        row["tuition_academic_year"] = (
            config["year"]
        )

        row["tuition_fee_basis"] = (
            config["basis"]
        )

        row["tuition_source_name"] = (
            config["source_name"]
        )

        row["tuition_source_url"] = (
            config["source_url"]
        )

        row["tuition_reason"] = (
            config["reason"]
        )

        row["verified_at"] = (
            VERIFIED_AT
        )


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


    # -------------------------------------------------
    # Post-write verification
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


    t3 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(31, 46)
    ]


    verified = sum(
        clean(
            row["tuition_research_status"]
        ) == "VERIFIED"
        for row in t3
    )

    unresolved = sum(
        clean(
            row["tuition_research_status"]
        ) == "REVIEWED_UNRESOLVED"
        for row in t3
    )

    numeric = sum(
        bool(
            clean(
                row["tuition_fee"]
            )
        )
        for row in t3
    )

    unresolved_with_numeric = sum(
        (
            clean(
                row["tuition_research_status"]
            )
            == "REVIEWED_UNRESOLVED"
            and bool(
                clean(
                    row["tuition_fee"]
                )
            )
        )
        for row in t3
    )


    evidence_complete = sum(
        all(
            clean(row[field])
            for field in [
                "tuition_applicant_scope",
                "tuition_academic_year",
                "tuition_fee_basis",
                "tuition_source_name",
                "tuition_source_url",
                "tuition_reason",
                "verified_at",
            ]
        )
        for row in t3
    )


    print()

    print(
        "T3 rows updated                 :",
        len(t3),
    )

    print(
        "T3 VERIFIED                     :",
        verified,
    )

    print(
        "T3 REVIEWED_UNRESOLVED          :",
        unresolved,
    )

    print(
        "T3 numeric tuition rows         :",
        numeric,
    )

    print(
        "Unresolved rows with number     :",
        unresolved_with_numeric,
    )

    print(
        "T3 evidence-complete rows       :",
        evidence_complete,
    )


    print()
    print("T3 TUITION SUMMARY")
    print("-" * 100)

    for row in t3:

        fee = clean(
            row["tuition_fee"]
        )

        if fee:
            tuition = (
                f"HKD {fee} / "
                f"{row['tuition_period']}"
            )
        else:
            tuition = (
                "NO MASTER NUMERIC FEE STORED"
            )

        print(
            row["program_id"],
            "|",
            row["tuition_research_status"],
            "|",
            tuition,
        )


    if verified != 11:
        raise ValueError(
            "Expected exactly 11 T3 VERIFIED rows."
        )

    if unresolved != 4:
        raise ValueError(
            "Expected exactly 4 T3 "
            "REVIEWED_UNRESOLVED rows."
        )

    if numeric != 11:
        raise ValueError(
            "Expected numeric master tuition "
            "for exactly 11 T3 rows."
        )

    if unresolved_with_numeric != 0:
        raise ValueError(
            "An unresolved row contains a "
            "master numeric tuition value."
        )

    if evidence_complete != 15:
        raise ValueError(
            "T3 evidence metadata is incomplete."
        )


    print()
    print("=" * 100)

    print(
        "STEP 169.2BC.2 TUITION "
        "BATCH T3 APPLY: PASS"
    )

    print(
        "NO CLEANED DATASET, WORKBOOK OR "
        "MONGODB DATA WAS MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
