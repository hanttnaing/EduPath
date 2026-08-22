import csv
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path


QUEUE = Path(
    "planning/20_macau_program_research_queue.csv"
)

EVIDENCE = Path(
    "planning/21_macau_program_detail_evidence.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_170_2c"
)

VERIFIED_AT = datetime.now().date().isoformat()


def detail(
    duration,
    mode,
    language,
    tuition,
    currency,
    period,
    detail_source,
    tuition_source,
    note,
):
    return {
        "duration_years": duration,
        "study_mode": mode,
        "language_of_instruction": language,
        "tuition_fee": tuition,
        "tuition_currency": currency,
        "tuition_period": period,
        "detail_source": detail_source,
        "tuition_source": tuition_source,
        "note": note,
    }


DETAILS = {

    # ========================================================
    # University of Macau
    # 2026/27 non-local 4-year Bachelor full tuition:
    # MOP 490,400
    # ========================================================

    "prog_mo_001": detail(
        "4",
        "Full-time",
        "English",
        "490400",
        "MOP",
        "Total",
        "https://www.cis.um.edu.mo/bsc_computer_science.html",
        "https://reg.um.edu.mo/admissions/general-information/fees/",
        "Current official programme/accreditation and fee evidence "
        "supports a 4-year English Bachelor programme and the "
        "non-local full-programme tuition. Future 2027/28 intake "
        "and deadline are not stored without a published schedule.",
    ),

    "prog_mo_002": detail(
        "4",
        "Full-time",
        "English",
        "490400",
        "MOP",
        "Total",
        "https://www.fst.um.edu.mo/academics/programs/",
        "https://reg.um.edu.mo/admissions/general-information/fees/",
        "Current UM engineering programme and non-local fee "
        "evidence verified. Future schedule fields remain blank.",
    ),

    "prog_mo_003": detail(
        "4",
        "Full-time",
        "English",
        "490400",
        "MOP",
        "Total",
        "https://www.fst.um.edu.mo/cee/degrees/bachelor/",
        "https://reg.um.edu.mo/admissions/general-information/fees/",
        "Current UM civil engineering and non-local fee evidence "
        "verified. Future schedule fields remain blank.",
    ),


    # ========================================================
    # Macao Polytechnic University
    # Official mode wording = daytime.
    # Do NOT force-map daytime -> Full-time.
    # Other overseas undergraduate full tuition = MOP 480,000.
    # ========================================================

    "prog_mo_004": detail(
        "4",
        "",
        "English",
        "480000",
        "MOP",
        "Total",
        "https://mpusite.mpu.edu.mo/admission_overseas/en/undergraduate.php",
        "https://mpusite.mpu.edu.mo/admission_overseas/en/fees_scholarships.php",
        "Official MPU source reports 4 years, daytime and English. "
        "Daytime is preserved as evidence but is not force-mapped "
        "to the canonical study_mode enum.",
    ),

    "prog_mo_005": detail(
        "4",
        "",
        "English",
        "480000",
        "MOP",
        "Total",
        "https://mpusite.mpu.edu.mo/admission_overseas/en/undergraduate.php",
        "https://mpusite.mpu.edu.mo/admission_overseas/en/fees_scholarships.php",
        "Official MPU source reports 4 years, daytime and English. "
        "Canonical study_mode remains unresolved.",
    ),

    "prog_mo_006": detail(
        "4",
        "",
        "English",
        "480000",
        "MOP",
        "Total",
        "https://mpusite.mpu.edu.mo/admission_overseas/en/undergraduate.php",
        "https://mpusite.mpu.edu.mo/admission_overseas/en/fees_scholarships.php",
        "For the overseas/current route, MPU lists Bachelor of "
        "Management as a 4-year daytime English programme. "
        "The separate evening Chinese version is not mixed into "
        "this selected programme record.",
    ),


    # ========================================================
    # Macau University of Science and Technology
    # 2026/27 non-Macao first-year tuition.
    # ========================================================

    "prog_mo_007": detail(
        "4",
        "",
        "English",
        "174000",
        "HKD",
        "Annual",
        "https://msb.must.edu.mo/page/id-3505.html?locale=en_US",
        "https://www.must.edu.mo/images/Admission/files/"
        "PreUBachelorFT_Non_Macao_residents_EN.pdf",
        "2026/27 non-Macao fee table verifies BBA normal duration "
        "4 years and first-year tuition HKD174,000.",
    ),

    "prog_mo_008": detail(
        "4",
        "",
        "English",
        "163000",
        "HKD",
        "Annual",
        "https://fhtm.must.edu.mo/id-1725/program/view/"
        "id-263.html?locale=en_US",
        "https://www.must.edu.mo/images/Admission/files/"
        "PreUBachelorFT_Non_Macao_residents_EN.pdf",
        "2026/27 non-Macao table verifies 4 years and first-year "
        "tuition HKD163,000 for International Tourism Management.",
    ),

    "prog_mo_009": detail(
        "4",
        "",
        "English",
        "174000",
        "HKD",
        "Annual",
        "https://ugadmissions.must.edu.mo/"
        "faculty/id-2878.html?locale=en_US",
        "https://www.must.edu.mo/images/Admission/files/"
        "PreUBachelorFT_Non_Macao_residents_EN.pdf",
        "2026/27 non-Macao table verifies 4 years and first-year "
        "tuition HKD174,000 for Applied Economics.",
    ),


    # ========================================================
    # City University of Macau
    # 2026/27 international/non-local prospectus.
    # ========================================================

    "prog_mo_010": detail(
        "4",
        "",
        "Unknown",
        "125000",
        "HKD",
        "Annual",
        "https://www.cityu.edu.mo/en/admissions/"
        "bachelors-degree-programmes/",
        "https://ado.cityu.edu.mo/en/uploads/userfiles/"
        "Prospectus%202026-2027%281%29.pdf",
        "Current 2026/27 Bachelor information supports 4-year "
        "duration and HKD125,000 annual non-local tuition. "
        "Whole-programme language is kept Unknown rather than "
        "inferred from an English webpage.",
    ),

    "prog_mo_011": detail(
        "4",
        "",
        "Chinese",
        "125000",
        "HKD",
        "Annual",
        "https://www.cityu.edu.mo/en/admissions/"
        "bachelors-degree-programmes/",
        "https://ado.cityu.edu.mo/en/uploads/userfiles/"
        "Prospectus%202026-2027%281%29.pdf",
        "Current Bachelor list identifies the selected BBA as "
        "Chinese-medium; 2026/27 tuition is HKD125,000 annually.",
    ),

    "prog_mo_012": detail(
        "4",
        "Full-time",
        "English",
        "115000",
        "HKD",
        "Annual",
        "https://www.cityu.edu.mo/en/admissions/"
        "bachelors-degree-programmes/",
        "https://ado.cityu.edu.mo/en/uploads/userfiles/"
        "Prospectus%202026-2027%281%29.pdf",
        "The selected International Tourism and Hotel Management "
        "English route is retained as English. Current sources "
        "support 4-year study and HKD115,000 annual tuition.",
    ),


    # ========================================================
    # University of Saint Joseph
    # 2026/27 international Bachelor tuition = USD 14,000/year.
    # ========================================================

    "prog_mo_013": detail(
        "4",
        "Full-time",
        "English",
        "14000",
        "USD",
        "Annual",
        "https://www.usj.edu.mo/en/course/"
        "ba-business-administration/",
        "https://www.usj.edu.mo/en/admissions/"
        "undergraduate-admissions/"
        "undergraduate-programmes-tuition-fees/",
        "Official USJ programme information supports 4 years, "
        "full-time daytime and English. 2026/27 international "
        "Bachelor tuition is USD14,000 per year.",
    ),

    "prog_mo_014": detail(
        "4",
        "Full-time",
        "English",
        "14000",
        "USD",
        "Annual",
        "https://www.usj.edu.mo/en/course/"
        "bachelor-of-biology-and-biotechnology/",
        "https://www.usj.edu.mo/en/admissions/"
        "undergraduate-admissions/"
        "undergraduate-programmes-tuition-fees/",
        "Official USJ programme and 2026/27 international tuition "
        "information verified.",
    ),

    "prog_mo_015": detail(
        "4",
        "Full-time",
        "English",
        "14000",
        "USD",
        "Annual",
        "https://www.usj.edu.mo/en/course/ba-psychology/",
        "https://www.usj.edu.mo/en/admissions/"
        "undergraduate-admissions/"
        "undergraduate-programmes-tuition-fees/",
        "Official USJ programme information supports 4 years "
        "full-time in English and international tuition of "
        "USD14,000 per year.",
    ),


    # ========================================================
    # Macao University of Tourism
    # Official wording = daytime, so mode remains blank.
    # 4-year full tuition for students from other countries/
    # regions = MOP 480,000.
    # ========================================================

    "prog_mo_016": detail(
        "4",
        "",
        "English",
        "480000",
        "MOP",
        "Total",
        "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
        "upload/18/2026-2027%20UG%20admission%20brochure%20"
        "%28ENG%29.pdf",
        "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
        "upload/18/2026-2027%20UG%20admission%20brochure%20"
        "%28ENG%29.pdf",
        "2026/27 official non-local brochure lists Hotel "
        "Management under English-medium daytime programmes. "
        "Daytime is not force-mapped to Full-time.",
    ),

    "prog_mo_017": detail(
        "4",
        "",
        "English",
        "480000",
        "MOP",
        "Total",
        "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
        "upload/18/2026-2027%20UG%20admission%20brochure%20"
        "%28ENG%29.pdf",
        "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
        "upload/18/2026-2027%20UG%20admission%20brochure%20"
        "%28ENG%29.pdf",
        "Official 2026/27 brochure supports 4-year English-medium "
        "Tourism Business Management and MOP480,000 full tuition "
        "for students from other countries/regions.",
    ),

    "prog_mo_018": detail(
        "4",
        "",
        "English",
        "480000",
        "MOP",
        "Total",
        "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
        "upload/18/2026-2027%20UG%20admission%20brochure%20"
        "%28ENG%29.pdf",
        "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
        "upload/18/2026-2027%20UG%20admission%20brochure%20"
        "%28ENG%29.pdf",
        "Official 2026/27 brochure supports 4-year English-medium "
        "Tourism Event Management. Daytime wording is not "
        "force-normalized into study_mode.",
    ),


    # ========================================================
    # Kiang Wu Nursing College
    # ========================================================

    "prog_mo_022": detail(
        "4",
        "Full-time",
        "Unknown",
        "248000",
        "MOP",
        "Total",
        "https://www2.kwnc.edu.mo/en/standard/"
        "BSN_Programme.html",
        "https://www2.kwnc.edu.mo/en/standard/"
        "BSN_Programme.html",
        "Official 2026/27 BSN information supports 4 years "
        "full-time and MOP248,000 total non-Macao tuition. "
        "Whole-programme teaching language is not inferred.",
    ),


    # ========================================================
    # Macau Institute of Management
    # Current programme identity verified, but current comparable
    # tuition/duration/mode not safely verified in this pass.
    # ========================================================

    "prog_mo_025": detail(
        "",
        "",
        "Chinese",
        "",
        "",
        "",
        "https://mim.edu.mo/?list_186%2F=",
        "",
        "BBA identity and Chinese teaching language remain "
        "verified. Older fee information is not promoted as "
        "current 2026/27 tuition; unresolved fields stay blank.",
    ),


    # ========================================================
    # Macau Millennium College
    # Current July-2026 revised programme.
    # ========================================================

    "prog_mo_028": detail(
        "4",
        "Full-time",
        "Chinese / English",
        "",
        "",
        "",
        "https://mmc.edu.mo/en/blog/college_en/"
        "college_business_en/15367/",
        "",
        "Current official programme overview confirms standard "
        "full-time duration of 4 years. July 2026 approval confirms "
        "Chinese and English face-to-face delivery. Current exact "
        "tuition is not stored without verified evidence.",
    ),
}


EVIDENCE_HEADERS = [
    "program_id",
    "university_id",
    "program_name",
    "detail_research_status",
    "programme_detail_source_url",
    "tuition_source_url",
    "international_admissions_source_url",
    "verified_fields",
    "unresolved_fields",
    "evidence_note",
    "verified_at",
]


print("=" * 108)
print(
    "STEP 170.2C - MACAU CONSOLIDATED "
    "PROGRAMME DETAIL RESEARCH PASS"
)
print("=" * 108)


if not QUEUE.exists():
    raise FileNotFoundError(
        f"Research queue not found: {QUEUE}"
    )


with QUEUE.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)
    headers = reader.fieldnames or []
    rows = list(reader)


if len(rows) != 30:
    raise ValueError(
        f"Expected 30 Macau research rows, found {len(rows)}."
    )


verified_rows = [
    row
    for row in rows
    if str(
        row.get("research_status") or ""
    ).strip() == "VERIFIED"
]


if len(verified_rows) != 21:
    raise ValueError(
        f"Expected 21 VERIFIED programme rows, "
        f"found {len(verified_rows)}."
    )


verified_ids = {
    row["program_id"].strip()
    for row in verified_rows
}


if set(DETAILS) != verified_ids:
    raise ValueError(
        "DETAILS dictionary does not exactly match "
        "the 21 verified Macau programme IDs."
    )


# ============================================================
# Backup queue + prior evidence if present
# ============================================================

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)


queue_backup = BACKUP_DIR / (
    "20_macau_program_research_queue_before_"
    f"detail_pass_{timestamp}.csv"
)

shutil.copy2(
    QUEUE,
    queue_backup,
)


if EVIDENCE.exists():

    evidence_backup = BACKUP_DIR / (
        "21_macau_program_detail_evidence_before_"
        f"rewrite_{timestamp}.csv"
    )

    shutil.copy2(
        EVIDENCE,
        evidence_backup,
    )

    print(
        "Prior evidence backup            :",
        evidence_backup,
    )


# ============================================================
# Apply detail values ONLY to VERIFIED programmes
# ============================================================

CANONICAL_DETAIL_FIELDS = [
    "duration_years",
    "study_mode",
    "language_of_instruction",
    "tuition_fee",
    "tuition_currency",
    "tuition_period",
    "minimum_gpa",
    "gpa_scale",
    "ielts_requirement",
    "toefl_requirement",
    "intake",
    "application_deadline",
]


evidence_rows = []


for row in rows:

    program_id = str(
        row.get("program_id") or ""
    ).strip()


    if program_id not in DETAILS:
        continue


    d = DETAILS[
        program_id
    ]


    # Only explicitly researched detail fields are updated.
    for field in [
        "duration_years",
        "study_mode",
        "language_of_instruction",
        "tuition_fee",
        "tuition_currency",
        "tuition_period",
    ]:

        row[field] = d[field]


    # No fabricated admission minimums or future schedules.
    row["minimum_gpa"] = ""
    row["gpa_scale"] = ""
    row["ielts_requirement"] = ""
    row["toefl_requirement"] = ""
    row["intake"] = ""
    row["application_deadline"] = ""


    existing_note = str(
        row.get("research_note") or ""
    ).strip()

    detail_note = (
        "DETAIL PASS "
        + VERIFIED_AT
        + ": "
        + d["note"]
    )

    row["research_note"] = (
        existing_note
        + (" | " if existing_note else "")
        + detail_note
    )

    row["last_verified_at"] = VERIFIED_AT


    verified_fields = []

    unresolved_fields = []


    for field in CANONICAL_DETAIL_FIELDS:

        value = str(
            row.get(field) or ""
        ).strip()

        if value:
            verified_fields.append(
                field
            )
        else:
            unresolved_fields.append(
                field
            )


    evidence_rows.append(
        {
            "program_id": program_id,
            "university_id": row[
                "university_id"
            ].strip(),
            "program_name": row[
                "program_name"
            ].strip(),
            "detail_research_status":
                "REVIEWED_PARTIAL",
            "programme_detail_source_url":
                d["detail_source"],
            "tuition_source_url":
                d["tuition_source"],
            "international_admissions_source_url":
                str(
                    row.get(
                        "international_application_url"
                    ) or ""
                ).strip(),
            "verified_fields":
                "; ".join(
                    verified_fields
                ),
            "unresolved_fields":
                "; ".join(
                    unresolved_fields
                ),
            "evidence_note":
                d["note"],
            "verified_at":
                VERIFIED_AT,
        }
    )


# ============================================================
# Save updated research queue
# ============================================================

with QUEUE.open(
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


# ============================================================
# Save evidence ledger
# ============================================================

with EVIDENCE.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=EVIDENCE_HEADERS,
    )

    writer.writeheader()
    writer.writerows(
        evidence_rows
    )


# ============================================================
# Consolidated audit
# ============================================================

verified_rows = [
    row
    for row in rows
    if str(
        row.get("research_status") or ""
    ).strip() == "VERIFIED"
]

deferred_rows = [
    row
    for row in rows
    if str(
        row.get("research_status") or ""
    ).strip() == "DEFERRED"
]


def count_nonblank(field):

    return sum(
        bool(
            str(
                row.get(field) or ""
            ).strip()
        )
        for row in verified_rows
    )


duration_count = count_nonblank(
    "duration_years"
)

mode_count = count_nonblank(
    "study_mode"
)

language_count = count_nonblank(
    "language_of_instruction"
)

tuition_count = count_nonblank(
    "tuition_fee"
)

ielts_count = count_nonblank(
    "ielts_requirement"
)

toefl_count = count_nonblank(
    "toefl_requirement"
)

intake_count = count_nonblank(
    "intake"
)

deadline_count = count_nonblank(
    "application_deadline"
)


blank_duration_ids = sorted(
    row["program_id"]
    for row in verified_rows
    if not str(
        row.get("duration_years") or ""
    ).strip()
)


blank_mode_ids = sorted(
    row["program_id"]
    for row in verified_rows
    if not str(
        row.get("study_mode") or ""
    ).strip()
)


blank_tuition_ids = sorted(
    row["program_id"]
    for row in verified_rows
    if not str(
        row.get("tuition_fee") or ""
    ).strip()
)


unknown_language_ids = sorted(
    row["program_id"]
    for row in verified_rows
    if str(
        row.get(
            "language_of_instruction"
        ) or ""
    ).strip() == "Unknown"
)


tuition_parity_errors = []

for row in verified_rows:

    fee = str(
        row.get("tuition_fee") or ""
    ).strip()

    currency = str(
        row.get("tuition_currency") or ""
    ).strip()

    period = str(
        row.get("tuition_period") or ""
    ).strip()


    if bool(fee) != (
        bool(currency)
        and bool(period)
    ):

        tuition_parity_errors.append(
            row["program_id"]
        )


international_statuses = Counter(
    str(
        row.get(
            "international_applicants_status"
        ) or ""
    ).strip()
    for row in rows
)


print(
    "Verified programme rows          :",
    len(verified_rows),
)

print(
    "Deferred slots                   :",
    len(deferred_rows),
)

print(
    "Detail evidence rows             :",
    len(evidence_rows),
)

print()
print(
    "Duration populated               :",
    duration_count,
    "/ 21",
)

print(
    "Study mode populated             :",
    mode_count,
    "/ 21",
)

print(
    "Language populated               :",
    language_count,
    "/ 21",
)

print(
    "Tuition populated                :",
    tuition_count,
    "/ 21",
)

print(
    "IELTS populated                  :",
    ielts_count,
    "/ 21",
)

print(
    "TOEFL populated                  :",
    toefl_count,
    "/ 21",
)

print(
    "Future intake populated          :",
    intake_count,
    "/ 21",
)

print(
    "Future deadline populated        :",
    deadline_count,
    "/ 21",
)

print()
print(
    "Blank duration IDs               :",
    ", ".join(
        blank_duration_ids
    ),
)

print(
    "Blank study-mode IDs             :",
    ", ".join(
        blank_mode_ids
    ),
)

print(
    "Blank tuition IDs                :",
    ", ".join(
        blank_tuition_ids
    ),
)

print(
    "Unknown language IDs             :",
    ", ".join(
        unknown_language_ids
    ),
)

print(
    "Tuition fee/currency/period errors:",
    len(tuition_parity_errors),
)

print(
    "All-slot international statuses  :",
    dict(
        international_statuses
    ),
)

print()
print(
    "Queue backup                     :",
    queue_backup,
)

print(
    "Updated queue                    :",
    QUEUE,
)

print(
    "Evidence ledger                  :",
    EVIDENCE,
)


errors = []


if len(verified_rows) != 21:
    errors.append(
        "Expected 21 verified programmes."
    )

if len(deferred_rows) != 9:
    errors.append(
        "Expected 9 deferred slots."
    )

if len(evidence_rows) != 21:
    errors.append(
        "Expected 21 detail evidence rows."
    )

if duration_count != 20:
    errors.append(
        "Expected duration for 20/21 programmes."
    )

if mode_count != 9:
    errors.append(
        "Expected evidence-safe study mode "
        "for 9/21 programmes."
    )

if language_count != 21:
    errors.append(
        "Expected language status/value "
        "for all 21 programmes."
    )

if tuition_count != 19:
    errors.append(
        "Expected verified tuition for "
        "19/21 programmes."
    )

if blank_duration_ids != [
    "prog_mo_025",
]:
    errors.append(
        "Unexpected blank duration set."
    )

if blank_tuition_ids != [
    "prog_mo_025",
    "prog_mo_028",
]:
    errors.append(
        "Unexpected blank tuition set."
    )

if blank_mode_ids != [
    "prog_mo_004",
    "prog_mo_005",
    "prog_mo_006",
    "prog_mo_007",
    "prog_mo_008",
    "prog_mo_009",
    "prog_mo_010",
    "prog_mo_011",
    "prog_mo_016",
    "prog_mo_017",
    "prog_mo_018",
    "prog_mo_025",
]:
    errors.append(
        "Unexpected unresolved study-mode set."
    )

if unknown_language_ids != [
    "prog_mo_010",
    "prog_mo_022",
]:
    errors.append(
        "Unexpected Unknown language set."
    )

if tuition_parity_errors:
    errors.append(
        "Tuition fee/currency/period parity failed."
    )

if any([
    ielts_count,
    toefl_count,
    intake_count,
    deadline_count,
]):
    errors.append(
        "Unverified requirement/schedule values "
        "were unexpectedly populated."
    )

if international_statuses != Counter({
    "verified_yes": 20,
    "unknown": 10,
}):
    errors.append(
        "International eligibility status counts changed."
    )


print()
print("=" * 108)


if errors:

    print(
        "STEP 170.2C MACAU CONSOLIDATED "
        "DETAIL PASS: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 170.2C MACAU CONSOLIDATED "
    "DETAIL PASS: PASS"
)

print(
    "21 VERIFIED PROGRAMMES RETAINED"
)

print(
    "20/21 DURATION, 21/21 LANGUAGE, "
    "19/21 TUITION VERIFIED"
)

print(
    "UNSUPPORTED DETAIL FIELDS REMAIN "
    "BLANK / UNKNOWN RATHER THAN FABRICATED"
)

print(
    "NO programs.json OR MONGODB "
    "RECORDS WERE MODIFIED"
)

print("=" * 108)
