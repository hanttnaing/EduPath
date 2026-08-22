import csv
import shutil
from datetime import datetime
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "18_hong_kong_program_intake_deadline_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2bi"
)

VERIFIED_AT = "2026-08-21"


I1_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(1, 16)
]


UNIVERSITY_RULES = {

    "uni_hk_001": {
        "source_name": (
            "HKU International / Non-JUPAS Admissions"
        ),
        "source_url": (
            "https://admissions.hku.hk/"
            "apply/international-qualifications"
        ),
        "route": (
            "International / Non-JUPAS Admissions Scheme"
        ),
        "evidence": (
            "As of 2026-08-21, HKU's official international "
            "admissions page still publishes the 2026-entry "
            "cycle: applications opened 24 Sep 2025, "
            "first-round evaluation deadline was "
            "26 Nov 2025, later applications were reviewed "
            "on a rolling basis, and the cycle closes "
            "21 Aug 2026. A 2027/28 exact intake/deadline "
            "schedule was not published on the reviewed page."
        ),
    },

    "uni_hk_002": {
        "source_name": (
            "CUHK Undergraduate Admissions - "
            "International Important Dates"
        ),
        "source_url": (
            "https://admission.cuhk.edu.hk/application/"
            "overseas-other-qualifications-non-local-"
            "international-team/important-dates/"
        ),
        "route": (
            "Non-local / International Qualifications"
        ),
        "evidence": (
            "CUHK's current official important-dates page "
            "publishes the 2026 Admissions Exercise: "
            "advance deadline 13 Nov 2025, regular deadline "
            "8 Jan 2026, extended deadline 29 May 2026, "
            "with the first teaching term commencing in "
            "early Sep 2026. A 2027/28 exact schedule was "
            "not published on the reviewed page."
        ),
    },

    "uni_hk_003": {
        "source_name": (
            "HKUST International Qualifications"
        ),
        "source_url": (
            "https://join.hkust.edu.hk/"
            "admissions/international-qualifications"
        ),
        "route": (
            "International Qualifications"
        ),
        "evidence": (
            "HKUST's current official international page "
            "publishes the 2026-entry cycle: application "
            "opens 3 Oct 2025, early-round deadline "
            "20 Nov 2025, main-round deadline 8 Jan 2026 "
            "and late-round deadline 30 Jun 2026. "
            "A 2027/28 exact schedule was not published "
            "on the reviewed page."
        ),
    },

    "uni_hk_004": {
        "source_name": (
            "PolyU International / Other Qualifications"
        ),
        "source_url": (
            "https://www.polyu.edu.hk/study/ug/"
            "admissions/international-other-qualifications"
        ),
        "route": (
            "International / Other Qualifications"
        ),
        "evidence": (
            "PolyU's current undergraduate international "
            "admissions listings primarily show Sept 2026 "
            "entry and 2026 programme application deadlines. "
            "A verified 2027/28 application deadline for "
            "these three I1 programmes was not yet published "
            "on the reviewed official admissions listing."
        ),
    },

    "uni_hk_005": {
        "source_name": (
            "CityUHK International Admission"
        ),
        "source_url": (
            "https://www.cityu.edu.hk/admo/"
            "admissions/international-admissions"
        ),
        "route": (
            "International Admission - Bachelor's Degree"
        ),
        "evidence": (
            "CityUHK's current official international "
            "admissions page publishes the 2026-entry "
            "cycle: application opens 25 Sep 2025, "
            "early deadline 15 Nov 2025, main deadline "
            "15 Jan 2026 and provisional Semester A "
            "start on 31 Aug 2026. A 2027-entry exact "
            "application schedule was not published on "
            "the reviewed page."
        ),
    },
}


EXPECTED_UNIVERSITY = {
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
    return str(value or "").strip()


def main():

    print("=" * 100)
    print(
        "STEP 169.2BI - APPLY HONG KONG "
        "INTAKE/DEADLINE BATCH I1"
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
            "Research queue has no headers."
        )

    if len(rows) != 45:
        raise ValueError(
            f"Expected 45 rows, found {len(rows)}."
        )

    by_id = {
        clean(row["program_id"]): row
        for row in rows
    }


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
    # I1 safety audit
    # -------------------------------------------------

    for program_id in I1_IDS:

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
                f"{program_id}: unexpected university_id."
            )

        for field in research_fields:

            if clean(row[field]):
                raise ValueError(
                    f"{program_id}: {field} "
                    "unexpectedly prefilled."
                )


    # I2/I3 must remain untouched.
    for i in range(16, 46):

        program_id = f"prog_hk_{i:03d}"

        if clean(
            by_id[program_id][
                "schedule_research_status"
            ]
        ) != "PENDING":
            raise ValueError(
                f"{program_id}: later batch "
                "is not PENDING."
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
        f"before_i1_apply_{timestamp}.csv"
    )

    shutil.copy2(
        QUEUE_PATH,
        backup_path,
    )

    print("Backup:", backup_path)


    # -------------------------------------------------
    # Apply I1 evidence closure
    # -------------------------------------------------

    for program_id in I1_IDS:

        row = by_id[program_id]

        university_id = clean(
            row["university_id"]
        )

        rule = UNIVERSITY_RULES[
            university_id
        ]

        # Do NOT copy 2026 deadlines into 2027.
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
            "Target admission cycle not yet "
            "published on reviewed official source"
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
            "The target is 2027/28 admission, but the "
            "reviewed official source still publishes "
            "the previous/current admission cycle. "
            "No 2026 intake or deadline is copied into "
            "the master record as if it were a 2027 "
            "schedule."
        )

        row["verified_at"] = VERIFIED_AT


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

    i1 = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(1, 16)
    ]

    later = [
        saved_by_id[
            f"prog_hk_{i:03d}"
        ]
        for i in range(16, 46)
    ]


    unresolved = sum(
        clean(
            row["schedule_research_status"]
        ) == "REVIEWED_UNRESOLVED"
        for row in i1
    )

    intake_stored = sum(
        bool(clean(row["intake"]))
        for row in i1
    )

    deadline_stored = sum(
        bool(
            clean(
                row["application_deadline"]
            )
        )
        for row in i1
    )

    evidence_complete = sum(
        all(
            clean(row[field])
            for field in [
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
        )
        for row in i1
    )

    later_pending = sum(
        clean(
            row["schedule_research_status"]
        ) == "PENDING"
        for row in later
    )


    print()

    print(
        "I1 rows updated                 :",
        len(i1),
    )

    print(
        "I1 REVIEWED_UNRESOLVED          :",
        unresolved,
    )

    print(
        "I1 intake values stored         :",
        intake_stored,
    )

    print(
        "I1 deadline values stored       :",
        deadline_stored,
    )

    print(
        "I1 evidence-complete rows       :",
        evidence_complete,
    )

    print(
        "I2/I3 PENDING preserved         :",
        later_pending,
    )


    if unresolved != 15:
        raise ValueError(
            "Expected 15 I1 unresolved rows."
        )

    if intake_stored != 0:
        raise ValueError(
            "No unverified 2027 intake "
            "should be stored."
        )

    if deadline_stored != 0:
        raise ValueError(
            "No unverified 2027 deadline "
            "should be stored."
        )

    if evidence_complete != 15:
        raise ValueError(
            "I1 evidence metadata is incomplete."
        )

    if later_pending != 30:
        raise ValueError(
            "I2/I3 must remain PENDING."
        )


    print()
    print("=" * 100)

    print(
        "STEP 169.2BI INTAKE/DEADLINE "
        "BATCH I1 APPLY: PASS"
    )

    print(
        "2026 DATES WERE NOT MISREPRESENTED "
        "AS 2027 DATES"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
