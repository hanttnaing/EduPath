import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "18_hong_kong_program_intake_deadline_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2bm"
)

VERIFIED_AT = "2026-08-21"


I3_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(31, 46)
]


EXPECTED_UNIVERSITY = {
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


RULES = {

    "uni_hk_011": {
        "source_name": (
            "HSUHK International Qualifications - "
            "Important Dates"
        ),
        "source_url": (
            "https://admission.hsu.edu.hk/"
            "undergraduate-admissions/year-1-entry/"
            "international-qualification/important-dates/"
        ),
        "route": (
            "Year 1 Entry - International Qualifications"
        ),
        "evidence": (
            "HSUHK's current official important-dates page "
            "publishes September intake for 2026 admissions. "
            "Applications opened 15 Nov 2025 and the "
            "non-local deadline was 10 Jun 2026, with "
            "Semester 1 beginning in Sep 2026. "
            "No exact 2027/28 schedule was published on "
            "the reviewed official source."
        ),
    },


    "uni_hk_012": {
        "source_name": (
            "Hong Kong Chu Hai College - "
            "International Qualifications"
        ),
        "source_url": (
            "https://chuhai.edu.hk/en/"
            "overseas-candidates"
        ),
        "route": (
            "Undergraduate - Non-local - "
            "International Qualifications"
        ),
        "evidence": (
            "Chu Hai's current official international "
            "qualifications page publishes the 2026/27 "
            "admission cycle. Non-local applications run "
            "from 20 Oct 2025 to 26 Jun 2026. "
            "No verified exact 2027/28 application period "
            "was published on the reviewed official page."
        ),
    },


    "uni_hk_013": {
        "source_name": (
            "Saint Francis University Admissions"
        ),
        "source_url": (
            "https://www.sfu.edu.hk/en/"
            "admission/admission/"
        ),
        "route": (
            "International Qualifications - "
            "Non-local Applicants"
        ),
        "evidence": (
            "Saint Francis University's official admissions "
            "page currently identifies the 2026/27 September "
            "intake and states that non-local applications "
            "for the AY2026/27 September cohort closed on "
            "31 Jul 2026. A verified exact 2027/28 "
            "application deadline was not yet published "
            "on the reviewed official page."
        ),
    },


    "uni_hk_014": {
        "source_name": (
            "THEi International Undergraduate Leaflet"
        ),
        "source_url": (
            "https://www.thei.edu.hk/wp-content/uploads/"
            "2026/02/"
            "THEi_Intl-leaflet-20260202_compressed_V2.pdf"
        ),
        "route": (
            "International Student - "
            "Bachelor Year 1 Entry"
        ),
        "evidence": (
            "THEi's official international undergraduate "
            "leaflet for the current cycle gives a "
            "tentative Bachelor's application deadline "
            "of mid-July 2026 and indicates registration "
            "and orientation in late August. "
            "The reviewed official material does not "
            "publish an exact 2027/28 application deadline."
        ),
    },


    "uni_hk_015": {
        "source_name": (
            "Tung Wah College - "
            "Admission for Non-local Applicants"
        ),
        "source_url": (
            "https://www.twc.edu.hk/en/"
            "Administration_Units/reg/our_service/"
            "prospective_students/non-local_admission"
        ),
        "route": (
            "Non-local Undergraduate Admission"
        ),
        "evidence": (
            "Tung Wah College's current non-local "
            "admission and prospectus materials remain "
            "for 2026/27 entry. The general admissions "
            "FAQ states that online applications normally "
            "start from mid-October, but an exact "
            "2027/28 non-local programme deadline for "
            "these records was not yet safely verified."
        ),
    },
}


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 100)
    print(
        "STEP 169.2BM - APPLY HONG KONG "
        "INTAKE/DEADLINE BATCH I3"
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
    # Preserve I1 + I2 closed state
    # -------------------------------------------------

    for i in range(1, 31):

        program_id = f"prog_hk_{i:03d}"

        if clean(
            by_id[program_id][
                "schedule_research_status"
            ]
        ) != "REVIEWED_UNRESOLVED":

            raise ValueError(
                f"{program_id}: prior closed state changed."
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
    # I3 safety audit
    # -------------------------------------------------

    for program_id in I3_IDS:

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
                f"{program_id}: university_id mismatch."
            )

        for field in research_fields:

            if clean(row[field]):

                raise ValueError(
                    f"{program_id}: {field} "
                    "unexpectedly prefilled."
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
        f"before_i3_apply_{timestamp}.csv"
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
    # Apply evidence closure
    # -------------------------------------------------

    for program_id in I3_IDS:

        row = by_id[program_id]

        university_id = clean(
            row["university_id"]
        )

        rule = RULES[
            university_id
        ]

        # Never reinterpret 2026 dates as 2027.
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
            "The target master record is for the "
            "2027/28 admission cycle. Current official "
            "material still reflects the previous/current "
            "cycle or does not provide a safely "
            "attributable exact 2027/28 deadline. "
            "No prior-cycle date is stored as a "
            "2027 intake or application deadline."
        )

        row["verified_at"] = VERIFIED_AT


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
        writer.writerows(rows)


    # -------------------------------------------------
    # Post-write audit
    # -------------------------------------------------

    with QUEUE_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        saved = list(
            csv.DictReader(file)
        )


    saved_by_id = {
        clean(row["program_id"]): row
        for row in saved
    }


    prior = [
        saved_by_id[f"prog_hk_{i:03d}"]
        for i in range(1, 31)
    ]

    i3 = [
        saved_by_id[f"prog_hk_{i:03d}"]
        for i in range(31, 46)
    ]


    prior_preserved = sum(
        clean(row["schedule_research_status"])
        == "REVIEWED_UNRESOLVED"
        for row in prior
    )

    i3_unresolved = sum(
        clean(row["schedule_research_status"])
        == "REVIEWED_UNRESOLVED"
        for row in i3
    )

    intakes = sum(
        bool(clean(row["intake"]))
        for row in i3
    )

    deadlines = sum(
        bool(
            clean(
                row["application_deadline"]
            )
        )
        for row in i3
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
        for row in i3
    )


    print()

    print(
        "I3 rows updated                 :",
        len(i3),
    )

    print(
        "I1/I2 closed state preserved    :",
        prior_preserved,
    )

    print(
        "I3 REVIEWED_UNRESOLVED          :",
        i3_unresolved,
    )

    print(
        "I3 intake values stored         :",
        intakes,
    )

    print(
        "I3 deadline values stored       :",
        deadlines,
    )

    print(
        "I3 evidence-complete rows       :",
        evidence_complete,
    )


    if prior_preserved != 30:
        raise ValueError(
            "I1/I2 closed state changed."
        )

    if i3_unresolved != 15:
        raise ValueError(
            "Expected 15 I3 unresolved rows."
        )

    if intakes != 0:
        raise ValueError(
            "Unverified 2027 intake was stored."
        )

    if deadlines != 0:
        raise ValueError(
            "Unverified 2027 deadline was stored."
        )

    if evidence_complete != 15:
        raise ValueError(
            "I3 evidence metadata is incomplete."
        )


    print()
    print("=" * 100)

    print(
        "STEP 169.2BM INTAKE/DEADLINE "
        "BATCH I3 APPLY: PASS"
    )

    print(
        "ALL 45 PROGRAMMES ARE NOW "
        "SCHEDULE-RESEARCH CLOSED"
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
