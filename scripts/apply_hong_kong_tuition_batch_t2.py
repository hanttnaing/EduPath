import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "17_hong_kong_program_tuition_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2ba"
)

VERIFIED_AT = "2026-08-21"


T2_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(16, 31)
]


HKBU_SOURCE = (
    "https://admissions.hkbu.edu.hk/"
    "fees-and-scholarships.html"
)

LINGNAN_SOURCE = (
    "https://www.ln.edu.hk/"
    "admissions/ug/"
)

EDUHK_SOURCE = (
    "https://www.apply.eduhk.hk/"
    "ug/Fees"
)

HKMU_SOURCE = (
    "https://admissions.hkmu.edu.hk/"
    "ug/overseas/"
)

HKSYU_SOURCE = (
    "https://uao.hksyu.edu/"
    "en/application/FAQ"
)


CONFIG = {

    # -------------------------------------------------
    # HKBU
    # -------------------------------------------------

    "prog_hk_016": {
        "status": "VERIFIED",
        "fee": "190000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "HKBU Undergraduate Admissions - "
            "Fees and Scholarships"
        ),
        "source_url": HKBU_SOURCE,
        "reason": (
            "HKBU officially publishes HKD190,000 "
            "annual tuition for full-time non-local "
            "undergraduate students in 2026/27."
        ),
    },

    "prog_hk_017": {
        "status": "VERIFIED",
        "fee": "190000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "HKBU Undergraduate Admissions - "
            "Fees and Scholarships"
        ),
        "source_url": HKBU_SOURCE,
        "reason": (
            "HKBU officially publishes HKD190,000 "
            "annual tuition for full-time non-local "
            "undergraduate students in 2026/27."
        ),
    },

    "prog_hk_018": {
        "status": "VERIFIED",
        "fee": "190000",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local undergraduate student",
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "HKBU Undergraduate Admissions - "
            "Fees and Scholarships"
        ),
        "source_url": HKBU_SOURCE,
        "reason": (
            "HKBU officially publishes HKD190,000 "
            "annual tuition for full-time non-local "
            "undergraduate students in 2026/27."
        ),
    },


    # -------------------------------------------------
    # Lingnan University
    # -------------------------------------------------

    "prog_hk_019": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": (
            "Non-local tuition amount requires "
            "additional official-source verification"
        ),
        "year": "2026/27",
        "basis": (
            "Numeric tuition intentionally not stored"
        ),
        "source_name": (
            "Lingnan University Undergraduate Admissions"
        ),
        "source_url": LINGNAN_SOURCE,
        "reason": (
            "Official Lingnan admissions sources were "
            "reviewed, but a sufficiently direct current "
            "official source for the 2026/27 non-local "
            "numeric tuition amount was not retrieved "
            "in this verification pass. No amount is "
            "inferred from secondary sources."
        ),
    },

    "prog_hk_020": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": (
            "Non-local tuition amount requires "
            "additional official-source verification"
        ),
        "year": "2026/27",
        "basis": (
            "Numeric tuition intentionally not stored"
        ),
        "source_name": (
            "Lingnan University Undergraduate Admissions"
        ),
        "source_url": LINGNAN_SOURCE,
        "reason": (
            "Official Lingnan admissions sources were "
            "reviewed, but a sufficiently direct current "
            "official source for the 2026/27 non-local "
            "numeric tuition amount was not retrieved "
            "in this verification pass. No amount is "
            "inferred from secondary sources."
        ),
    },

    "prog_hk_021": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": (
            "Non-local tuition amount requires "
            "additional official-source verification"
        ),
        "year": "2026/27",
        "basis": (
            "Numeric tuition intentionally not stored"
        ),
        "source_name": (
            "Lingnan University Undergraduate Admissions"
        ),
        "source_url": LINGNAN_SOURCE,
        "reason": (
            "Official Lingnan admissions sources were "
            "reviewed, but a sufficiently direct current "
            "official source for the 2026/27 non-local "
            "numeric tuition amount was not retrieved "
            "in this verification pass. No amount is "
            "inferred from secondary sources."
        ),
    },


    # -------------------------------------------------
    # EdUHK
    # -------------------------------------------------

    "prog_hk_022": {
        "status": "VERIFIED",
        "fee": "180000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local undergraduate student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "EdUHK Undergraduate Programmes - Fees"
        ),
        "source_url": EDUHK_SOURCE,
        "reason": (
            "EdUHK officially publishes HKD180,000 "
            "per annum for non-local undergraduate "
            "students in government-funded programmes "
            "for 2026/27."
        ),
    },

    "prog_hk_023": {
        "status": "VERIFIED",
        "fee": "180000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local undergraduate student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "EdUHK Undergraduate Programmes - Fees"
        ),
        "source_url": EDUHK_SOURCE,
        "reason": (
            "EdUHK officially publishes HKD180,000 "
            "per annum for non-local undergraduate "
            "students in government-funded programmes "
            "for 2026/27."
        ),
    },

    "prog_hk_024": {
        "status": "VERIFIED",
        "fee": "180000",
        "currency": "HKD",
        "period": "Annual",
        "scope": (
            "Non-local undergraduate student - "
            "government-funded programme"
        ),
        "year": "2026/27",
        "basis": "Annual tuition",
        "source_name": (
            "EdUHK Undergraduate Programmes - Fees"
        ),
        "source_url": EDUHK_SOURCE,
        "reason": (
            "EdUHK officially publishes HKD180,000 "
            "per annum for non-local undergraduate "
            "students in government-funded programmes "
            "for 2026/27."
        ),
    },


    # -------------------------------------------------
    # HKMU
    # -------------------------------------------------

    "prog_hk_025": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": (
            "Direct Admission (Non-local) applicant"
        ),
        "year": "2026/27",
        "basis": (
            "Programme-specific non-local fee "
            "requires further official verification"
        ),
        "source_name": (
            "HKMU Direct Admission (Non-local)"
        ),
        "source_url": HKMU_SOURCE,
        "reason": (
            "HKMU confirms that this programme accepts "
            "Direct Admission (Non-local) applicants, "
            "but the current accessible official page "
            "did not provide a reliably attributable "
            "2026/27 numeric programme fee for this "
            "specific programme. No fee is inferred."
        ),
    },

    "prog_hk_026": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": (
            "Direct Admission (Non-local) applicant"
        ),
        "year": "2026/27",
        "basis": (
            "Programme-specific non-local fee "
            "requires further official verification"
        ),
        "source_name": (
            "HKMU Direct Admission (Non-local)"
        ),
        "source_url": HKMU_SOURCE,
        "reason": (
            "HKMU confirms that this programme accepts "
            "Direct Admission (Non-local) applicants, "
            "but the current accessible official page "
            "did not provide a reliably attributable "
            "2026/27 numeric programme fee for this "
            "specific programme. No fee is inferred."
        ),
    },

    "prog_hk_027": {
        "status": "REVIEWED_UNRESOLVED",
        "fee": "",
        "currency": "",
        "period": "",
        "scope": (
            "Direct Admission (Non-local) applicant"
        ),
        "year": "2026/27",
        "basis": (
            "Programme-specific non-local fee "
            "requires further official verification"
        ),
        "source_name": (
            "HKMU Direct Admission (Non-local)"
        ),
        "source_url": HKMU_SOURCE,
        "reason": (
            "HKMU confirms that this programme accepts "
            "Direct Admission (Non-local) applicants, "
            "but the current accessible official page "
            "did not provide a reliably attributable "
            "2026/27 numeric programme fee for this "
            "specific programme. No fee is inferred."
        ),
    },


    # -------------------------------------------------
    # HKSYU
    # -------------------------------------------------

    "prog_hk_028": {
        "status": "VERIFIED",
        "fee": "125675",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": (
            "Annual programme tuition, "
            "payable in two instalments"
        ),
        "source_name": (
            "HKSYU Undergraduate Admissions FAQ"
        ),
        "source_url": HKSYU_SOURCE,
        "reason": (
            "HKSYU officially publishes HKD125,675 "
            "annual non-local tuition for the "
            "Bachelor of Science with Honours in "
            "Applied Data Science for the 2026/27 cohort."
        ),
    },

    "prog_hk_029": {
        "status": "VERIFIED",
        "fee": "110089",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": (
            "Annual programme tuition, "
            "payable in two instalments"
        ),
        "source_name": (
            "HKSYU Undergraduate Admissions FAQ"
        ),
        "source_url": HKSYU_SOURCE,
        "reason": (
            "HKSYU officially publishes HKD110,089 "
            "annual non-local tuition for the "
            "Bachelor of Commerce (Honours) in "
            "Financial Technology for the 2026/27 cohort."
        ),
    },

    "prog_hk_030": {
        "status": "VERIFIED",
        "fee": "110089",
        "currency": "HKD",
        "period": "Annual",
        "scope": "Non-local student",
        "year": "2026/27",
        "basis": (
            "Annual programme tuition, "
            "payable in two instalments"
        ),
        "source_name": (
            "HKSYU Undergraduate Admissions FAQ"
        ),
        "source_url": HKSYU_SOURCE,
        "reason": (
            "HKSYU publishes HKD110,089 annual "
            "non-local tuition for 'Other undergraduate "
            "programmes' for the 2026/27 cohort. "
            "The standard Psychology programme is not "
            "listed among the higher-fee special "
            "programme categories."
        ),
    },
}


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 100)
    print(
        "STEP 169.2BA - APPLY HONG KONG "
        "TUITION BATCH T2"
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

    if set(CONFIG) != set(T2_IDS):
        raise ValueError(
            "T2 configuration does not match "
            "prog_hk_016 through prog_hk_030."
        )


    # -------------------------------------------------
    # Preserve completed T1
    # -------------------------------------------------

    for i in range(1, 16):

        program_id = f"prog_hk_{i:03d}"

        if clean(
            row_by_id[
                program_id
            ]["tuition_research_status"]
        ) != "VERIFIED":

            raise ValueError(
                f"{program_id}: T1 is no longer VERIFIED."
            )


    # -------------------------------------------------
    # Verify T2 is untouched before write
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

    for program_id in T2_IDS:

        row = row_by_id[program_id]

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


    # T3 remains untouched.
    for i in range(31, 46):

        program_id = f"prog_hk_{i:03d}"

        if clean(
            row_by_id[
                program_id
            ]["tuition_research_status"]
        ) != "PENDING":

            raise ValueError(
                f"{program_id}: T3 is not PENDING."
            )


    # -------------------------------------------------
    # Backup
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
        f"before_t2_apply_{timestamp}.csv"
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
    # Apply T2 evidence
    # -------------------------------------------------

    updated = 0

    for program_id in T2_IDS:

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

        row[
            "tuition_research_status"
        ] = config["status"]

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

        row["verified_at"] = VERIFIED_AT

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
        writer.writerows(rows)


    # -------------------------------------------------
    # Post-write validation
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

    t2 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(16, 31)
    ]

    t3 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(31, 46)
    ]


    verified_t1 = sum(
        clean(row["tuition_research_status"])
        == "VERIFIED"
        for row in t1
    )

    verified_t2 = sum(
        clean(row["tuition_research_status"])
        == "VERIFIED"
        for row in t2
    )

    unresolved_t2 = sum(
        clean(row["tuition_research_status"])
        == "REVIEWED_UNRESOLVED"
        for row in t2
    )

    pending_t3 = sum(
        clean(row["tuition_research_status"])
        == "PENDING"
        for row in t3
    )

    numeric_t2 = sum(
        bool(clean(row["tuition_fee"]))
        for row in t2
    )

    unresolved_with_number = sum(
        (
            clean(row["tuition_research_status"])
            == "REVIEWED_UNRESOLVED"
            and bool(clean(row["tuition_fee"]))
        )
        for row in t2
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
        for row in t2
    )


    print()

    print(
        "T2 rows updated                 :",
        updated,
    )

    print(
        "T1 VERIFIED preserved           :",
        verified_t1,
    )

    print(
        "T2 VERIFIED                     :",
        verified_t2,
    )

    print(
        "T2 REVIEWED_UNRESOLVED          :",
        unresolved_t2,
    )

    print(
        "T3 PENDING                      :",
        pending_t3,
    )

    print(
        "T2 numeric tuition rows         :",
        numeric_t2,
    )

    print(
        "Unresolved rows with number     :",
        unresolved_with_number,
    )

    print(
        "T2 evidence-complete rows       :",
        evidence_complete,
    )


    print()
    print("T2 TUITION SUMMARY")
    print("-" * 100)

    for row in t2:

        fee = clean(
            row["tuition_fee"]
        )

        if fee:
            value = (
                f"HKD {fee} / "
                f"{row['tuition_period']}"
            )
        else:
            value = "NO NUMERIC FEE STORED"

        print(
            row["program_id"],
            "|",
            row["tuition_research_status"],
            "|",
            value,
        )


    if updated != 15:
        raise ValueError(
            "Expected exactly 15 T2 updates."
        )

    if verified_t1 != 15:
        raise ValueError(
            "T1 VERIFIED state changed."
        )

    if verified_t2 != 9:
        raise ValueError(
            "Expected exactly 9 T2 VERIFIED rows."
        )

    if unresolved_t2 != 6:
        raise ValueError(
            "Expected exactly 6 T2 "
            "REVIEWED_UNRESOLVED rows."
        )

    if pending_t3 != 15:
        raise ValueError(
            "T3 must remain 15 PENDING rows."
        )

    if numeric_t2 != 9:
        raise ValueError(
            "Expected numeric tuition for "
            "exactly 9 T2 rows."
        )

    if unresolved_with_number != 0:
        raise ValueError(
            "An unresolved tuition row contains "
            "a numeric amount."
        )

    if evidence_complete != 15:
        raise ValueError(
            "T2 evidence metadata is incomplete."
        )


    print()
    print("=" * 100)

    print(
        "STEP 169.2BA TUITION "
        "BATCH T2 APPLY: PASS"
    )

    print(
        "NO CLEANED DATASET, WORKBOOK OR "
        "MONGODB DATA WAS MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
