import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "17_hong_kong_program_tuition_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2az"
)

VERIFIED_AT = "2026-08-21"


T1_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(1, 16)
]


HKU_SOURCE = (
    "https://admissions.hku.hk/"
    "fees-and-scholarships/fees"
)

CUHK_SOURCE = (
    "https://admission.cuhk.edu.hk/"
    "fees-financing-your-studies/fees/"
)

HKUST_SOURCE = (
    "https://join.hkust.edu.hk/"
    "fees-and-scholarships"
)

POLYU_SOURCE = (
    "https://www.polyu.edu.hk/study/ug/"
    "admissions/international-other-qualifications/"
    "international-other-qualifications-tuition-fees"
)

CITYU_SOURCE = (
    "https://www.cityu.edu.hk/"
    "admo/fees-and-scholarships"
)


TUITION = {

    # -------------------------------------------------
    # HKU
    # -------------------------------------------------

    "prog_hk_001": {
        "fee": "249000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student - STEM",
        "year": "2026/27",
        "basis": (
            "Annual tuition including STEM fee"
        ),
        "source_name": (
            "HKU Tuition and Living Expenses"
        ),
        "source_url": HKU_SOURCE,
        "reason": (
            "HKU publishes annual tuition of "
            "HKD249,000 for 2026/27 non-local "
            "students admitted to STEM faculties "
            "and schools. Computing and Data Science "
            "is offered by the School of Computing "
            "and Data Science, which HKU lists in "
            "the STEM tuition category."
        ),
    },

    "prog_hk_002": {
        "fee": "224000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student - non-STEM",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "HKU Tuition and Living Expenses"
        ),
        "source_url": HKU_SOURCE,
        "reason": (
            "HKU publishes annual tuition of "
            "HKD224,000 for 2026/27 non-local "
            "students admitted to non-STEM faculties. "
            "The standard BBA programme is offered by "
            "HKU Business School, which falls under "
            "the non-STEM tuition category. Optional "
            "external dual-degree arrangements are "
            "not represented by this base tuition row."
        ),
    },

    "prog_hk_003": {
        "fee": "249000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student - STEM",
        "year": "2026/27",
        "basis": (
            "Annual tuition including STEM fee"
        ),
        "source_name": (
            "HKU Tuition and Living Expenses"
        ),
        "source_url": HKU_SOURCE,
        "reason": (
            "HKU publishes annual tuition of "
            "HKD249,000 for 2026/27 non-local "
            "students admitted to STEM faculties. "
            "Bachelor of Science is offered by the "
            "Faculty of Science, which HKU explicitly "
            "includes in its STEM tuition category."
        ),
    },


    # -------------------------------------------------
    # CUHK
    # -------------------------------------------------

    "prog_hk_004": {
        "fee": "214000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "CUHK Undergraduate Admissions - Fees"
        ),
        "source_url": CUHK_SOURCE,
        "reason": (
            "CUHK official undergraduate admissions "
            "publishes HKD214,000 annual tuition for "
            "non-local students in 2026/27. The "
            "programme is not identified as a "
            "dual-degree tuition exception."
        ),
    },

    "prog_hk_005": {
        "fee": "214000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "CUHK Undergraduate Admissions - Fees"
        ),
        "source_url": CUHK_SOURCE,
        "reason": (
            "CUHK official undergraduate admissions "
            "publishes HKD214,000 annual tuition for "
            "non-local students in 2026/27. The "
            "programme is not identified as a "
            "dual-degree tuition exception."
        ),
    },

    "prog_hk_006": {
        "fee": "214000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "CUHK Undergraduate Admissions - Fees"
        ),
        "source_url": CUHK_SOURCE,
        "reason": (
            "CUHK official undergraduate admissions "
            "publishes HKD214,000 annual tuition for "
            "non-local students in 2026/27. The "
            "programme is not identified as a "
            "dual-degree tuition exception."
        ),
    },


    # -------------------------------------------------
    # HKUST
    # -------------------------------------------------

    "prog_hk_007": {
        "fee": "215000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "HKUST Undergraduate Admissions - "
            "Fees and Scholarships"
        ),
        "source_url": HKUST_SOURCE,
        "reason": (
            "HKUST publishes HKD215,000 tuition "
            "per academic year for non-local "
            "undergraduate students in 2026/27."
        ),
    },

    "prog_hk_008": {
        "fee": "215000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "HKUST Undergraduate Admissions - "
            "Fees and Scholarships"
        ),
        "source_url": HKUST_SOURCE,
        "reason": (
            "HKUST publishes HKD215,000 tuition "
            "per academic year for non-local "
            "undergraduate students in 2026/27."
        ),
    },

    "prog_hk_009": {
        "fee": "215000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "HKUST Undergraduate Admissions - "
            "Fees and Scholarships"
        ),
        "source_url": HKUST_SOURCE,
        "reason": (
            "HKUST publishes HKD215,000 tuition "
            "per academic year for non-local "
            "undergraduate students in 2026/27."
        ),
    },


    # -------------------------------------------------
    # PolyU
    # -------------------------------------------------

    "prog_hk_010": {
        "fee": "200000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local international student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "PolyU International / Other "
            "Qualifications - Tuition Fees"
        ),
        "source_url": POLYU_SOURCE,
        "reason": (
            "PolyU charges HKD200,000 per academic "
            "year for full-time government-funded "
            "Bachelor programmes in 2026/27. "
            "JS3868 is officially identified as "
            "Government-Funded."
        ),
    },

    "prog_hk_011": {
        "fee": "200000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local international student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "PolyU International / Other "
            "Qualifications - Tuition Fees"
        ),
        "source_url": POLYU_SOURCE,
        "reason": (
            "PolyU charges HKD200,000 per academic "
            "year for full-time government-funded "
            "Bachelor programmes in 2026/27. "
            "The Data Science and AI scheme JS3223 "
            "is officially Government-Funded."
        ),
    },

    "prog_hk_012": {
        "fee": "200000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local international student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "PolyU International / Other "
            "Qualifications - Tuition Fees"
        ),
        "source_url": POLYU_SOURCE,
        "reason": (
            "PolyU charges HKD200,000 per academic "
            "year for full-time government-funded "
            "Bachelor programmes in 2026/27. "
            "Business Administration scheme JS3003 "
            "is officially Government-Funded. "
            "Optional dual-degree pathways are not "
            "represented by this base tuition row."
        ),
    },


    # -------------------------------------------------
    # CityUHK
    # -------------------------------------------------

    "prog_hk_013": {
        "fee": "190000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "CityUHK Fees and Scholarships"
        ),
        "source_url": CITYU_SOURCE,
        "reason": (
            "CityUHK publishes HKD190,000 per "
            "academic year for non-local students "
            "admitted to government-funded Bachelor's "
            "degree programmes in 2026/27. The "
            "Computer Science department also "
            "publishes HKD190,000 for non-local "
            "students entering in 2026."
        ),
    },

    "prog_hk_014": {
        "fee": "190000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "CityUHK Fees and Scholarships"
        ),
        "source_url": CITYU_SOURCE,
        "reason": (
            "CityUHK publishes HKD190,000 annual "
            "tuition for 2026/27 non-local students "
            "in government-funded Bachelor's degree "
            "programmes. The Department of Data "
            "Science identifies JS1071 as UGC-funded."
        ),
    },

    "prog_hk_015": {
        "fee": "190000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "CityUHK Fees and Scholarships"
        ),
        "source_url": CITYU_SOURCE,
        "reason": (
            "CityUHK publishes HKD190,000 annual "
            "tuition for 2026/27 non-local students "
            "in government-funded Bachelor's degree "
            "programmes. CityUHK's official programme "
            "finder identifies BBA Global Business "
            "JS1001 as Government funded. Optional "
            "joint-degree arrangements are not "
            "represented by this base tuition row."
        ),
    },
}


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 100)
    print(
        "STEP 169.2AZ.1 - APPLY HONG KONG "
        "TUITION BATCH T1"
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


    row_by_id = {
        clean(row["program_id"]): row
        for row in rows
    }


    if set(TUITION) != set(T1_IDS):
        raise ValueError(
            "T1 tuition configuration does not "
            "match prog_hk_001 through prog_hk_015."
        )


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


    # -------------------------------------------------
    # Pre-write safety audit
    # -------------------------------------------------

    for program_id in T1_IDS:

        if program_id not in row_by_id:
            raise ValueError(
                f"Missing T1 programme: {program_id}"
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
                    f"{program_id}: {field} is "
                    "unexpectedly prefilled."
                )


    # T2 and T3 must remain completely untouched.
    for i in range(16, 46):

        program_id = (
            f"prog_hk_{i:03d}"
        )

        row = row_by_id[
            program_id
        ]

        if clean(
            row["tuition_research_status"]
        ) != "PENDING":

            raise ValueError(
                f"{program_id}: later batch is "
                "not PENDING."
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
        f"before_t1_apply_{timestamp}.csv"
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
    # Apply T1 official-source tuition
    # -------------------------------------------------

    updated = 0


    for program_id in T1_IDS:

        row = row_by_id[
            program_id
        ]

        config = TUITION[
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

        row[
            "tuition_research_status"
        ] = "VERIFIED"

        row[
            "tuition_applicant_scope"
        ] = config["scope"]

        row[
            "tuition_academic_year"
        ] = config["year"]

        row[
            "tuition_fee_basis"
        ] = config["basis"]

        row[
            "tuition_source_name"
        ] = config["source_name"]

        row[
            "tuition_source_url"
        ] = config["source_url"]

        row[
            "tuition_reason"
        ] = config["reason"]

        row["verified_at"] = (
            VERIFIED_AT
        )

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


    t1 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(1, 16)
    ]

    t2_t3 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(16, 46)
    ]


    verified = sum(
        clean(
            row["tuition_research_status"]
        )
        == "VERIFIED"
        for row in t1
    )


    pending_remaining = sum(
        clean(
            row["tuition_research_status"]
        )
        == "PENDING"
        for row in t2_t3
    )


    fees_stored = sum(
        bool(
            clean(
                row["tuition_fee"]
            )
        )
        for row in t1
    )


    currencies_stored = sum(
        clean(
            row["tuition_currency"]
        )
        == "HKD"
        for row in t1
    )


    annual_periods = sum(
        clean(
            row["tuition_period"]
        )
        == "Annual"
        for row in t1
    )


    complete_evidence = sum(
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
        for row in t1
    )


    print()

    print(
        "T1 rows updated                 :",
        updated,
    )

    print(
        "T1 VERIFIED                     :",
        verified,
    )

    print(
        "T2/T3 PENDING                   :",
        pending_remaining,
    )

    print(
        "T1 tuition fees stored          :",
        fees_stored,
    )

    print(
        "T1 HKD currency stored          :",
        currencies_stored,
    )

    print(
        "T1 Annual periods stored        :",
        annual_periods,
    )

    print(
        "T1 complete evidence rows       :",
        complete_evidence,
    )


    print()
    print("T1 FEE SUMMARY")
    print("-" * 100)


    for row in t1:

        print(
            row["program_id"],
            "|",
            f"HKD {row['tuition_fee']}",
            "|",
            row["tuition_period"],
            "|",
            row["tuition_academic_year"],
        )


    if updated != 15:
        raise ValueError(
            "Expected exactly 15 T1 updates."
        )

    if verified != 15:
        raise ValueError(
            "Expected all 15 T1 rows VERIFIED."
        )

    if pending_remaining != 30:
        raise ValueError(
            "T2/T3 must remain 30 PENDING rows."
        )

    if fees_stored != 15:
        raise ValueError(
            "Expected 15 tuition values."
        )

    if currencies_stored != 15:
        raise ValueError(
            "Every T1 currency must be HKD."
        )

    if annual_periods != 15:
        raise ValueError(
            "Every T1 tuition period must "
            "be Annual."
        )

    if complete_evidence != 15:
        raise ValueError(
            "T1 tuition evidence is incomplete."
        )


    print()
    print("=" * 100)

    print(
        "STEP 169.2AZ.1 TUITION "
        "BATCH T1 APPLY: PASS"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
