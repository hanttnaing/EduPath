import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "18_hong_kong_program_intake_deadline_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2bk"
)

VERIFIED_AT = "2026-08-21"


I2_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(16, 31)
]


EXPECTED_UNIVERSITY = {
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


RULES = {

    "uni_hk_006": {
        "source_name": (
            "HKBU Undergraduate Admissions - "
            "International Qualifications"
        ),
        "source_url": (
            "https://admissions.hkbu.edu.hk/"
            "admissions/international-qualifications.html"
        ),
        "route": (
            "International Qualifications"
        ),
        "evidence": (
            "As reviewed on 2026-08-21, HKBU's official "
            "international undergraduate admissions page "
            "still presents the 2026 admissions timeline "
            "and related 2025/26 application-cycle "
            "information. A verified exact 2027/28 "
            "application deadline for these programmes "
            "was not yet available on the reviewed source."
        ),
    },


    "uni_hk_007": {
        "source_name": (
            "Lingnan University "
            "Undergraduate Admissions"
        ),
        "source_url": (
            "https://www.ln.edu.hk/"
            "admissions/ug/"
        ),
        "route": (
            "Non-local / International "
            "Undergraduate Admission"
        ),
        "evidence": (
            "Official Lingnan undergraduate admissions "
            "sources were reviewed for the target "
            "2027/28 cycle. A sufficiently direct and "
            "verified exact 2027/28 intake/deadline "
            "schedule for these programmes was not "
            "retrieved in this verification pass. "
            "No prior-cycle deadline is inferred."
        ),
    },


    "uni_hk_008": {
        "source_name": (
            "EdUHK International Qualifications - "
            "Important Dates"
        ),
        "source_url": (
            "https://www.apply.eduhk.hk/"
            "ug/nonlocal_dates"
        ),
        "route": (
            "International Applicants / "
            "Non-local Qualifications"
        ),
        "evidence": (
            "EdUHK's official page currently publishes "
            "the 2026/27 schedule: applications opened "
            "2 Oct 2025, with early, main and late "
            "application rounds continuing through "
            "6 May 2026, and the academic year "
            "commencing in early Sep 2026. "
            "A verified 2027/28 exact schedule was not "
            "published on the reviewed page."
        ),
    },


    "uni_hk_009": {
        "source_name": (
            "HKMU Direct Admission (Non-local)"
        ),
        "source_url": (
            "https://admissions.hkmu.edu.hk/"
            "ug/overseas/"
        ),
        "route": (
            "Direct Admission (Non-local)"
        ),
        "evidence": (
            "HKMU's official non-local undergraduate "
            "page currently publishes the 2026/27 "
            "cycle: applications started 20 Oct 2025, "
            "the first-round deadline was 31 Mar 2026, "
            "the overseas-applicant second-round "
            "deadline was 31 May 2026, and term "
            "commencement was 1 Sep 2026. "
            "A verified 2027/28 exact schedule was not "
            "published on the reviewed page."
        ),
    },


    "uni_hk_010": {
        "source_name": (
            "HKSYU Undergraduate Admissions - "
            "First-Year Entry"
        ),
        "source_url": (
            "https://uao.hksyu.edu/en/"
            "student-admission/first-year"
        ),
        "route": (
            "First-Year Entry - "
            "Other / Overseas Qualifications"
        ),
        "evidence": (
            "HKSYU accepts applicants with overseas "
            "academic qualifications for individual "
            "assessment. Current official undergraduate "
            "admissions materials reviewed on "
            "2026-08-21 remain associated with the "
            "2026/27 entry cycle. A safely attributable "
            "exact 2027/28 deadline for non-local "
            "applicants with overseas qualifications "
            "was not yet verified."
        ),
    },
}


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 100)
    print(
        "STEP 169.2BK - APPLY HONG KONG "
        "INTAKE/DEADLINE BATCH I2"
    )
    print("=" * 100)


    if not QUEUE_PATH.exists():
        raise FileNotFoundError(
            f"Queue not found: {QUEUE_PATH}"
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
            "Queue has no headers."
        )


    if len(rows) != 45:
        raise ValueError(
            f"Expected 45 rows, found {len(rows)}."
        )


    by_id = {
        clean(row["program_id"]): row
        for row in rows
    }


    # -------------------------------------------------
    # Preserve closed I1
    # -------------------------------------------------

    for i in range(1, 16):

        program_id = f"prog_hk_{i:03d}"

        if clean(
            by_id[program_id][
                "schedule_research_status"
            ]
        ) != "REVIEWED_UNRESOLVED":

            raise ValueError(
                f"{program_id}: I1 state changed."
            )


    research_fields = [
        "intake",
        "application_deadline",
        "applicant_scope",
        "admission_route",
        "academic_year",
        "schedule_type",
        "schedule_source_name",
        "schedule_source_url",
        "schedule_evidence",
        "storage_reason",
        "verified_at",
    ]


    # -------------------------------------------------
    # Verify I2 is untouched
    # -------------------------------------------------

    for program_id in I2_IDS:

        row = by_id[program_id]

        if clean(
            row["schedule_research_status"]
        ) != "PENDING":

            raise ValueError(
                f"{program_id}: expected PENDING."
            )

        expected_uni = EXPECTED_UNIVERSITY[
            program_id
        ]

        if clean(
            row["university_id"]
        ) != expected_uni:

            raise ValueError(
                f"{program_id}: unexpected "
                "university_id."
            )

        for field in research_fields:

            if clean(row[field]):

                raise ValueError(
                    f"{program_id}: {field} "
                    "unexpectedly prefilled."
                )


    # I3 must remain untouched.
    for i in range(31, 46):

        program_id = f"prog_hk_{i:03d}"

        if clean(
            by_id[program_id][
                "schedule_research_status"
            ]
        ) != "PENDING":

            raise ValueError(
                f"{program_id}: I3 is not PENDING."
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
        "hong_kong_intake_deadline_queue_"
        f"before_i2_apply_{timestamp}.csv"
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
    # Apply I2 evidence closure
    # -------------------------------------------------

    for program_id in I2_IDS:

        row = by_id[program_id]

        university_id = clean(
            row["university_id"]
        )

        rule = RULES[
            university_id
        ]


        # No 2026 date is copied into 2027.
        row["intake"] = ""
        row["application_deadline"] = ""

        row[
            "schedule_research_status"
        ] = "REVIEWED_UNRESOLVED"

        row[
            "applicant_scope"
        ] = (
            "Non-local / international "
            "undergraduate applicant"
        )

        row[
            "admission_route"
        ] = rule["route"]

        row[
            "academic_year"
        ] = "2027/28"

        row[
            "schedule_type"
        ] = (
            "Target 2027/28 exact schedule "
            "not yet safely verified"
        )

        row[
            "schedule_source_name"
        ] = rule["source_name"]

        row[
            "schedule_source_url"
        ] = rule["source_url"]

        row[
            "schedule_evidence"
        ] = rule["evidence"]

        row[
            "storage_reason"
        ] = (
            "Target admission cycle is 2027/28. "
            "The reviewed official material does not "
            "yet provide a safely attributable exact "
            "2027/28 programme schedule. Previous-cycle "
            "dates are therefore preserved as evidence "
            "only and are not stored in master intake "
            "or application_deadline fields."
        )

        row["verified_at"] = VERIFIED_AT


    # -------------------------------------------------
    # Write
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
    # Post-write audit
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


    i1 = [
        saved_by_id[f"prog_hk_{i:03d}"]
        for i in range(1, 16)
    ]

    i2 = [
        saved_by_id[f"prog_hk_{i:03d}"]
        for i in range(16, 31)
    ]

    i3 = [
        saved_by_id[f"prog_hk_{i:03d}"]
        for i in range(31, 46)
    ]


    i1_preserved = sum(
        clean(row["schedule_research_status"])
        == "REVIEWED_UNRESOLVED"
        for row in i1
    )

    i2_unresolved = sum(
        clean(row["schedule_research_status"])
        == "REVIEWED_UNRESOLVED"
        for row in i2
    )

    i3_pending = sum(
        clean(row["schedule_research_status"])
        == "PENDING"
        for row in i3
    )

    i2_intakes = sum(
        bool(clean(row["intake"]))
        for row in i2
    )

    i2_deadlines = sum(
        bool(
            clean(
                row["application_deadline"]
            )
        )
        for row in i2
    )


    evidence_fields = [
        "applicant_scope",
        "admission_route",
        "academic_year",
        "schedule_type",
        "schedule_source_name",
        "schedule_source_url",
        "schedule_evidence",
        "storage_reason",
        "verified_at",
    ]


    evidence_complete = sum(
        all(
            clean(row[field])
            for field in evidence_fields
        )
        for row in i2
    )


    print()

    print(
        "I2 rows updated                 :",
        len(i2),
    )

    print(
        "I1 unresolved state preserved   :",
        i1_preserved,
    )

    print(
        "I2 REVIEWED_UNRESOLVED          :",
        i2_unresolved,
    )

    print(
        "I3 PENDING preserved            :",
        i3_pending,
    )

    print(
        "I2 intake values stored         :",
        i2_intakes,
    )

    print(
        "I2 deadline values stored       :",
        i2_deadlines,
    )

    print(
        "I2 evidence-complete rows       :",
        evidence_complete,
    )


    if i1_preserved != 15:
        raise ValueError(
            "I1 closed state changed."
        )

    if i2_unresolved != 15:
        raise ValueError(
            "Expected 15 I2 "
            "REVIEWED_UNRESOLVED rows."
        )

    if i3_pending != 15:
        raise ValueError(
            "I3 must remain 15 PENDING rows."
        )

    if i2_intakes != 0:
        raise ValueError(
            "Unverified 2027 intakes were stored."
        )

    if i2_deadlines != 0:
        raise ValueError(
            "Unverified 2027 deadlines were stored."
        )

    if evidence_complete != 15:
        raise ValueError(
            "I2 evidence metadata is incomplete."
        )


    print()
    print("=" * 100)

    print(
        "STEP 169.2BK INTAKE/DEADLINE "
        "BATCH I2 APPLY: PASS"
    )

    print(
        "NO PRIOR-CYCLE DATES WERE "
        "MISREPRESENTED AS 2027 DATES"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
