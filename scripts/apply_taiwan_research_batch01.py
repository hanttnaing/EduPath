import csv
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# ============================================================
# Existing transformer
# ============================================================

SCRIPTS_DIR = Path("scripts").resolve()

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS_DIR),
    )

import transform_programs as tp


QUEUE = Path(
    "planning/24_taiwan_program_research_queue.csv"
)

EVIDENCE = Path(
    "planning/25_taiwan_program_research_evidence_part01.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_170_4b1"
)

TODAY = "2026-08-22"


def clean(value):
    return str(value or "").strip()


def optional(value):
    value = clean(value)
    return None if value == "" else value


RESULTS = {}


def add(
    pid,
    name,
    field,
    program_url,
    international_url,
    international_note,
    *,
    duration="",
    language="Unknown",
    ielts="",
    note="",
):
    RESULTS[pid] = {
        "program_name": name,
        "field_of_study": field,
        "degree_level": "Bachelor",

        "duration_years": duration,
        "study_mode": "",
        "language_of_instruction": language,

        "tuition_fee": "",
        "tuition_currency": "",
        "tuition_period": "",

        "minimum_gpa": "",
        "gpa_scale": "",
        "ielts_requirement": ielts,
        "toefl_requirement": "",

        "intake": "",
        "application_deadline": "",

        "program_url": program_url,

        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence": (
            "Current official university source "
            "verifies this Bachelor programme."
        ),

        "research_status": "VERIFIED",
        "research_note": note,

        "international_applicants_status":
            "verified_yes",

        "international_application_url":
            international_url,

        "international_requirements_note":
            international_note,
    }


# ============================================================
# uni_tw_001 - National Taiwan University
# ============================================================

NTU_INTL = (
    "https://admissions.ntu.edu.tw/"
)

add(
    "prog_tw_001",
    "Economics",
    "Economics",
    "https://econ.ntu.edu.tw/en/"
    "bachelors-english-taught-program",
    NTU_INTL,
    (
        "NTU official international admissions "
        "and English-taught programme information "
        "support international Bachelor applicants."
    ),
    language="English",
    note=(
        "NTU officially lists Economics among "
        "its undergraduate English-taught programmes."
    ),
)

add(
    "prog_tw_002",
    "Civil Engineering",
    "Civil Engineering",
    "https://www.ce.ntu.edu.tw/en/programs/"
    "undergraduate-programs/",
    NTU_INTL,
    (
        "The Civil Engineering department explicitly "
        "states that both undergraduate tracks welcome "
        "international students."
    ),
    duration="4",
    language="English",
    note=(
        "Official Civil Engineering page explicitly "
        "states four years of training and provides "
        "a full English-taught track."
    ),
)

add(
    "prog_tw_003",
    "Mechanical Engineering",
    "Mechanical Engineering",
    "https://admissions.ntu.edu.tw/learn/"
    "taught-programs/",
    NTU_INTL,
    (
        "NTU international admissions information "
        "lists Mechanical Engineering among "
        "undergraduate English-taught offerings."
    ),
    language="English",
    note=(
        "Programme identity and English-taught "
        "availability are verified; duration remains "
        "blank without programme-specific evidence "
        "in this pass."
    ),
)


# ============================================================
# uni_tw_002 - National Tsing Hua University
# ============================================================

NTHU_INTL = (
    "https://apply.nthu.edu.tw/en/article/"
    "172-2026-fall-undergraduate"
)

add(
    "prog_tw_004",
    "Chemical Engineering",
    "Chemical Engineering",
    "https://apply.nthu.edu.tw/en/department/"
    "24-chemical-engineering",
    NTHU_INTL,
    (
        "NTHU official international applicant portal "
        "marks Chemical Engineering as available to "
        "international students."
    ),
    language="English Available",
    note=(
        "Official portal states sufficient "
        "English-taught courses are available "
        "to meet graduation requirements."
    ),
)

add(
    "prog_tw_005",
    "Electrical Engineering",
    "Electrical Engineering",
    "https://apply.nthu.edu.tw/tw/department/"
    "64-electrical-engineering",
    NTHU_INTL,
    (
        "NTHU official programme portal identifies "
        "Electrical Engineering for international "
        "student applicants."
    ),
    language="English Available",
    note=(
        "Official programme page reports sufficient "
        "English-taught courses for graduation. "
        "Duration is not inferred."
    ),
)

add(
    "prog_tw_006",
    (
        "International Bachelor Degree Program "
        "in Electrical Engineering and Computer Science"
    ),
    "Electrical Engineering and Computer Science",
    "https://ibp.nthu.edu.tw/ertss-EECS.html",
    NTHU_INTL,
    (
        "The current NTHU international Bachelor "
        "admission material explicitly supports "
        "international applicants to this programme."
    ),
    duration="4",
    language="English",
    ielts="6.0",
    note=(
        "Official NTHU source describes this as "
        "a four-year fully English-taught Bachelor "
        "programme. Current programme-specific "
        "admission material specifies IELTS 6.0 "
        "or equivalent; no TOEFL numeric value is "
        "invented."
    ),
)


# ============================================================
# uni_tw_003 - National Yang Ming Chiao Tung University
# ============================================================

NYCU_INTL = (
    "https://oia.nycu.edu.tw/oia/en/app/"
    "artwebsite/view?id=786&module=artwebsite&"
    "serno=aa792259-32d5-422d-b382-3171b79f64f3"
)

NYCU_CURRICULUM = (
    "https://www.nycu.edu.tw/aa/ch/app/data/view?"
    "id=2511&module=nycu0069&"
    "serno=26a3c36f-d833-4a3d-8e18-571d2ce72de4"
)

add(
    "prog_tw_007",
    "Computer Science and Information Engineering",
    "Computer Science",
    "https://www.cs.nycu.edu.tw/admission/"
    "undergraduate?locale=en",
    NYCU_INTL,
    (
        "NYCU Fall 2026 degree-seeking international "
        "admission results contain Bachelor admits "
        "to the Department of Computer Science."
    ),
    note=(
        "Current undergraduate programme and current "
        "international admission are verified. "
        "Whole-programme teaching language remains "
        "Unknown."
    ),
)

add(
    "prog_tw_008",
    "Microelectronics",
    "Microelectronics / Semiconductor Engineering",
    NYCU_CURRICULUM,
    NYCU_INTL,
    (
        "NYCU Fall 2026 international admission "
        "results include Bachelor admission to "
        "the Department of Microelectronics."
    ),
    note=(
        "Current AY2026 undergraduate curriculum "
        "identifies the Department of Microelectronics. "
        "Teaching language remains Unknown rather "
        "than inferred."
    ),
)

add(
    "prog_tw_009",
    "Electrophysics",
    "Electrophysics",
    NYCU_CURRICULUM,
    NYCU_INTL,
    (
        "NYCU Fall 2026 degree-seeking international "
        "admission results explicitly contain "
        "Bachelor admits to Electrophysics."
    ),
    note=(
        "Current Bachelor identity and international "
        "eligibility verified. Language remains Unknown."
    ),
)


# ============================================================
# uni_tw_004 - National Cheng Kung University
# ============================================================

NCKU_INTL = (
    "https://oia.ncku.edu.tw/p/"
    "404-1032-229816.php?Lang=en"
)

NCKU_PROGRAMS = (
    "https://management.oia.ncku.edu.tw/"
    "intladmission/application/brochure/"
    "applyIntladmissionSn/28"
)

add(
    "prog_tw_010",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    NCKU_PROGRAMS,
    NCKU_INTL,
    (
        "NCKU current 2026/2027 international "
        "admission programme list includes the "
        "Bachelor programme in Computer Science "
        "and Information Engineering."
    ),
    note=(
        "Current international programme identity "
        "verified. Language remains Unknown because "
        "individual English courses are not treated "
        "as proof of whole-programme English MOI."
    ),
)

add(
    "prog_tw_011",
    "Electrical Engineering",
    "Electrical Engineering",
    NCKU_PROGRAMS,
    NCKU_INTL,
    (
        "NCKU current 2026/2027 international "
        "admission programme list includes "
        "Electrical Engineering at Bachelor level."
    ),
    note=(
        "Current international Bachelor availability "
        "verified; programme-wide language remains "
        "Unknown."
    ),
)

add(
    "prog_tw_012",
    "Mechanical Engineering",
    "Mechanical Engineering",
    NCKU_PROGRAMS,
    NCKU_INTL,
    (
        "NCKU current international admissions "
        "evidence includes Mechanical Engineering "
        "Bachelor applicants/students."
    ),
    note=(
        "The official current course evidence shows "
        "many undergraduate courses in English, but "
        "this is not force-normalized into an "
        "English programme-level MOI."
    ),
)


# ============================================================
# uni_tw_005 - National Taiwan University of
# Science and Technology (Taiwan Tech / NTUST)
# ============================================================

NTUST_INTL = (
    "https://admission.ntust.edu.tw/p/"
    "412-1052-9572.php?Lang=en"
)

add(
    "prog_tw_013",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    "https://www.csie.ntust.edu.tw/p/"
    "412-1038-10472.php?Lang=en",
    NTUST_INTL,
    (
        "Taiwan Tech operates a current Fall 2026 "
        "international Bachelor admission route."
    ),
    duration="4",
    language="Chinese",
    note=(
        "Current Taiwan Tech Bachelor admissions "
        "state that regular programmes other than "
        "the designated international advanced "
        "programme are Chinese-taught. CSIE has "
        "a four-year undergraduate programme."
    ),
)

add(
    "prog_tw_014",
    "Electronic and Computer Engineering",
    "Electronic and Computer Engineering",
    "https://ece.ntust.edu.tw/p/"
    "412-1017-1415.php?Lang=en",
    NTUST_INTL,
    (
        "Taiwan Tech current international "
        "undergraduate admission route applies "
        "to eligible Bachelor programmes."
    ),
    duration="4",
    language="Chinese",
    note=(
        "Active four-year Bachelor identity verified. "
        "Current undergraduate admission guidance "
        "places regular programmes in the "
        "Chinese-taught category."
    ),
)

add(
    "prog_tw_015",
    "Industrial Management",
    "Industrial Management",
    "https://im-r.ntust.edu.tw/p/"
    "412-1014-11291.php?Lang=en",
    NTUST_INTL,
    (
        "The Department of Industrial Management "
        "explicitly invites international students "
        "to its Bachelor programme."
    ),
    duration="4",
    language="Chinese",
    note=(
        "Current department admission page states "
        "that the undergraduate programme is four "
        "years and instruction is mostly Chinese."
    ),
)


# ============================================================
# uni_tw_006 - National Chengchi University
# ============================================================

NCCU_INTL = (
    "https://nccuadmission.nccu.edu.tw/Post/277"
)

add(
    "prog_tw_016",
    "Chinese Literature",
    "Chinese Literature",
    NCCU_INTL,
    NCCU_INTL,
    (
        "NCCU's current 2026 international admission "
        "programme list marks Chinese Literature "
        "as available at Bachelor level."
    ),
    language="Chinese",
    note=(
        "Current NCCU medium-of-instruction table "
        "identifies the Bachelor programme as Chinese."
    ),
)

add(
    "prog_tw_017",
    "English",
    "English Language and Literature",
    NCCU_INTL,
    NCCU_INTL,
    (
        "NCCU current international programme list "
        "includes the Department of English "
        "at Bachelor level."
    ),
    language="English Available",
    note=(
        "NCCU marks this Bachelor programme as "
        "having sufficient English-taught courses "
        "to satisfy graduation requirements."
    ),
)

add(
    "prog_tw_018",
    (
        "Bachelor Degree Program of "
        "International College of Innovation"
    ),
    "Interdisciplinary Innovation",
    NCCU_INTL,
    NCCU_INTL,
    (
        "NCCU current international programme list "
        "explicitly includes this Bachelor programme."
    ),
    language="English",
    note=(
        "NCCU's current medium-of-instruction table "
        "marks the International College of "
        "Innovation Bachelor programme as "
        "English-taught."
    ),
)


# ============================================================
# uni_tw_007 - National Central University
# ============================================================

NCU_INTL = (
    "https://cis.ncu.edu.tw/admissions/"
    "default/college/open.programs"
)

add(
    "prog_tw_019",
    "Business Administration",
    "Business Administration",
    NCU_INTL,
    NCU_INTL,
    (
        "NCU's current Fall 2026 international "
        "degree-program list marks Business "
        "Administration as open at Bachelor level."
    ),
    note=(
        "Programme and international Bachelor "
        "availability verified. Language marker is "
        "not safely reconstructed from text extraction, "
        "so MOI remains Unknown."
    ),
)

add(
    "prog_tw_020",
    "Information Management",
    "Information Management",
    NCU_INTL,
    NCU_INTL,
    (
        "NCU's current international degree-program "
        "list marks Information Management as open "
        "at Bachelor level."
    ),
    note=(
        "Current international eligibility verified; "
        "language remains Unknown."
    ),
)

add(
    "prog_tw_021",
    "Economics",
    "Economics",
    NCU_INTL,
    NCU_INTL,
    (
        "NCU's current international degree-program "
        "list marks Economics as open at "
        "Bachelor level."
    ),
    note=(
        "Current Bachelor and international "
        "availability verified. Language remains "
        "Unknown rather than inferred."
    ),
)


# ============================================================
# uni_tw_008 - National Chung Hsing University
# ============================================================

NCHU_INTL = (
    "https://oia.nchu.edu.tw/images/File/"
    "03_Apply_to_NCHU/3-1-Degree-Programs/"
    "3-1-2-International-Students/"
    "115_Programs_and_Language_Instruction.pdf"
)

add(
    "prog_tw_022",
    "Business Administration",
    "Business Administration",
    NCHU_INTL,
    NCHU_INTL,
    (
        "NCHU's official 2026/2027 international "
        "degree-program document includes Business "
        "Administration at Bachelor level."
    ),
    note=(
        "Current international programme availability "
        "verified. Language symbol is not force-parsed "
        "from the PDF extraction, so MOI stays Unknown."
    ),
)

add(
    "prog_tw_023",
    "Computer Science and Engineering",
    "Computer Science",
    NCHU_INTL,
    NCHU_INTL,
    (
        "NCHU's current 2026/2027 international "
        "degree-program document includes Computer "
        "Science and Engineering at Bachelor level."
    ),
    note=(
        "Current international Bachelor identity "
        "verified; language remains Unknown."
    ),
)

add(
    "prog_tw_024",
    "Electrical Engineering",
    "Electrical Engineering",
    NCHU_INTL,
    NCHU_INTL,
    (
        "NCHU's current international programme "
        "document includes Electrical Engineering "
        "at Bachelor level."
    ),
    note=(
        "Programme identity and international "
        "eligibility verified; whole-programme "
        "language remains Unknown."
    ),
)


# ============================================================
# uni_tw_009 - National Taiwan Normal University
# ============================================================

NTNU_INTL = (
    "https://bds.oia.ntnu.edu.tw/bds/en/apply"
)

add(
    "prog_tw_025",
    "Bachelor of Education",
    "Education",
    "https://www.ed.ntnu.edu.tw/en/"
    "pro1?locale=zh_cn&locale=zh_tw",
    NTNU_INTL,
    (
        "NTNU Department of Education's official "
        "Bachelor information directly links "
        "international-student applications."
    ),
    note=(
        "Bachelor of Education identity and "
        "international application route verified. "
        "Programme-wide MOI remains Unknown."
    ),
)

add(
    "prog_tw_026",
    (
        "Program of Chinese Language and Culture "
        "for International Students"
    ),
    "Chinese Language and Culture",
    "https://www.tcsl.ntnu.edu.tw/index.php/"
    "en/admissions/for-international-students/"
    "adbachelor-program/",
    NTNU_INTL,
    (
        "This official Bachelor programme is "
        "specifically designed for international "
        "students and provides a direct "
        "international application route."
    ),
    duration="4",
    note=(
        "Official source explicitly describes "
        "a four-year Bachelor programme for "
        "international students. The teaching "
        "language is not inferred merely from "
        "the subject matter."
    ),
)

add(
    "prog_tw_027",
    (
        "Business Administration "
        "(English-taught Program)"
    ),
    "Business Administration",
    "https://www.mgt.ntnu.edu.tw/en/ba-etp",
    (
        "https://www.mgt.ntnu.edu.tw/"
        "en/ba-etp-admissions"
    ),
    (
        "The current BA-ETP admissions page "
        "explicitly recruits international applicants "
        "and publishes its admission requirements."
    ),
    language="English",
    note=(
        "Current programme states all courses "
        "are in English except specified university "
        "Chinese requirements. CEFR B2 is not "
        "converted into an invented IELTS/TOEFL "
        "numeric score."
    ),
)


# ============================================================
# uni_tw_010 - National Taipei University of Technology
# ============================================================

NTUT_INTL = (
    "https://taipeitech.oia.ntut.edu.tw/"
    "foreign/index/index/lang/en"
)

add(
    "prog_tw_028",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    "https://csie.ntut.edu.tw/p/"
    "426-1070-53.php?Lang=en",
    NTUT_INTL,
    (
        "Taipei Tech provides a current "
        "international degree-student application "
        "system, and the CSIE department maintains "
        "an international-student admission route."
    ),
    duration="4",
    language="Chinese",
    note=(
        "Current CSIE page explicitly states a "
        "four-year B.S. programme and that the "
        "majority of undergraduate courses "
        "are taught in Mandarin."
    ),
)

add(
    "prog_tw_029",
    "Electronic Engineering",
    "Electronic Engineering",
    "https://ece.ntut.edu.tw/p/"
    "412-1071-13195.php?Lang=en",
    NTUT_INTL,
    (
        "The current Electronic Engineering B.S. "
        "page explicitly directs international "
        "applicants to Taipei Tech's international "
        "degree-student system."
    ),
    duration="4",
    note=(
        "Official B.S. page identifies this as "
        "a four-year programme. Whole-programme "
        "teaching language remains Unknown."
    ),
)

add(
    "prog_tw_030",
    (
        "Industrial Engineering "
        "and Management"
    ),
    "Industrial Engineering and Management",
    "https://iem.ntut.edu.tw/p/"
    "412-1081-11891.php?Lang=en",
    NTUT_INTL,
    (
        "The current IEM B.S. programme page "
        "contains an International admission route "
        "through Taipei Tech OIA."
    ),
    duration="4",
    note=(
        "Current official B.S. page states that "
        "the Bachelor degree normally takes "
        "four years. Teaching language remains "
        "Unknown."
    ),
)


# ============================================================
# Start
# ============================================================

print("=" * 114)
print(
    "STEP 170.4B.1 - TAIWAN OFFICIAL RESEARCH "
    "BATCH 1 (UNIVERSITIES 001-010)"
)
print("=" * 114)


if not QUEUE.exists():
    raise FileNotFoundError(
        f"Taiwan research queue missing: {QUEUE}"
    )


with QUEUE.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)
    headers = reader.fieldnames or []
    rows = list(reader)


if len(rows) != 90:
    raise ValueError(
        f"Expected 90 Taiwan slots, found {len(rows)}."
    )


expected_batch_ids = {
    f"prog_tw_{i:03d}"
    for i in range(1, 31)
}


if set(RESULTS) != expected_batch_ids:
    raise ValueError(
        "Batch-1 result ID set must be "
        "exactly prog_tw_001..030."
    )


# ============================================================
# Verify ID -> university parent mapping
# ============================================================

row_by_id = {
    clean(row["program_id"]): row
    for row in rows
}


for number in range(1, 31):

    pid = f"prog_tw_{number:03d}"

    expected_parent_number = (
        ((number - 1) // 3) + 1
    )

    expected_parent = (
        f"uni_tw_{expected_parent_number:03d}"
    )

    actual_parent = clean(
        row_by_id[pid]["university_id"]
    )

    if actual_parent != expected_parent:
        raise ValueError(
            f"{pid}: expected parent "
            f"{expected_parent}, found "
            f"{actual_parent}."
        )


# ============================================================
# Backup queue
# ============================================================

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)


queue_backup = BACKUP_DIR / (
    "24_taiwan_program_research_queue_"
    f"before_batch01_{timestamp}.csv"
)


shutil.copy2(
    QUEUE,
    queue_backup,
)


if EVIDENCE.exists():

    evidence_backup = BACKUP_DIR / (
        "25_taiwan_program_research_evidence_part01_"
        f"before_rebuild_{timestamp}.csv"
    )

    shutil.copy2(
        EVIDENCE,
        evidence_backup,
    )

    print(
        "Previous evidence backup         :",
        evidence_backup,
    )


# ============================================================
# Apply only batch 001-030
# ============================================================

FIELDS = [
    "program_name",
    "field_of_study",
    "degree_level",
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

    "program_url",

    "programme_identity_status",
    "programme_identity_evidence",

    "research_status",
    "research_note",

    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
]


for field in FIELDS:

    if field not in headers:
        raise ValueError(
            f"Queue missing field: {field}"
        )


for row in rows:

    pid = clean(
        row.get("program_id")
    )

    if pid not in RESULTS:
        continue

    result = RESULTS[pid]

    for field in FIELDS:
        row[field] = result[field]

    row["last_verified_at"] = TODAY

    row[
        "international_applicants_last_verified_at"
    ] = TODAY


# ============================================================
# Evidence ledger
# ============================================================

EVIDENCE_HEADERS = [
    "program_id",
    "university_id",
    "university_name",
    "program_name",
    "degree_level",
    "programme_source_url",
    "international_source_url",
    "international_applicants_status",
    "verified_fields",
    "unresolved_fields",
    "evidence_note",
    "verified_at",
]


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

    pid = clean(
        row["program_id"]
    )

    if pid not in RESULTS:
        continue


    verified_fields = [
        field
        for field in CANONICAL_DETAIL_FIELDS
        if clean(row.get(field))
    ]


    unresolved_fields = [
        field
        for field in CANONICAL_DETAIL_FIELDS
        if not clean(row.get(field))
    ]


    evidence_rows.append(
        {
            "program_id":
                pid,

            "university_id":
                clean(row["university_id"]),

            "university_name":
                clean(row["university_name"]),

            "program_name":
                clean(row["program_name"]),

            "degree_level":
                clean(row["degree_level"]),

            "programme_source_url":
                clean(row["program_url"]),

            "international_source_url":
                clean(
                    row[
                        "international_application_url"
                    ]
                ),

            "international_applicants_status":
                clean(
                    row[
                        "international_applicants_status"
                    ]
                ),

            "verified_fields":
                "; ".join(
                    verified_fields
                ),

            "unresolved_fields":
                "; ".join(
                    unresolved_fields
                ),

            "evidence_note":
                clean(
                    row["research_note"]
                ),

            "verified_at":
                TODAY,
        }
    )


# ============================================================
# Write queue and evidence
# ============================================================

with QUEUE.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=headers,
        extrasaction="raise",
    )

    writer.writeheader()
    writer.writerows(rows)


with EVIDENCE.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=EVIDENCE_HEADERS,
        extrasaction="raise",
    )

    writer.writeheader()
    writer.writerows(
        evidence_rows
    )


# ============================================================
# Batch audit
# ============================================================

batch = [
    row
    for row in rows
    if clean(row["program_id"])
    in expected_batch_ids
]


remaining = [
    row
    for row in rows
    if clean(row["program_id"])
    not in expected_batch_ids
]


identity_statuses = Counter(
    clean(
        row["programme_identity_status"]
    )
    for row in rows
)


research_statuses = Counter(
    clean(
        row["research_status"]
    )
    for row in rows
)


international_statuses = Counter(
    clean(
        row["international_applicants_status"]
    )
    for row in rows
)


def count_batch(field):

    return sum(
        bool(
            clean(
                row.get(field)
            )
        )
        for row in batch
    )


duration_count = count_batch(
    "duration_years"
)

mode_count = count_batch(
    "study_mode"
)

language_count = count_batch(
    "language_of_instruction"
)

tuition_count = count_batch(
    "tuition_fee"
)

ielts_count = count_batch(
    "ielts_requirement"
)

toefl_count = count_batch(
    "toefl_requirement"
)

intake_count = count_batch(
    "intake"
)

deadline_count = count_batch(
    "application_deadline"
)


unknown_language_ids = sorted(
    clean(row["program_id"])
    for row in batch
    if clean(
        row.get(
            "language_of_instruction"
        )
    ) == "Unknown"
)


verified_yes_blank_urls = sorted(
    clean(row["program_id"])
    for row in batch
    if (
        clean(
            row[
                "international_applicants_status"
            ]
        ) == "verified_yes"
        and not clean(
            row[
                "international_application_url"
            ]
        )
    )
)


# ============================================================
# Transform gate for the 30 verified programmes
# ============================================================

valid_university_ids = (
    tp.load_valid_university_ids()
)


transform_pass = []
transform_fail = []


for row_number, row in enumerate(
    batch,
    start=2,
):

    raw = {
        "program_id":
            optional(row["program_id"]),

        "university_id":
            optional(row["university_id"]),

        "program_name":
            optional(row["program_name"]),

        "field_of_study":
            optional(row["field_of_study"]),

        "degree_level":
            optional(row["degree_level"]),

        "duration_years":
            optional(row["duration_years"]),

        "study_mode":
            optional(row["study_mode"]),

        "language_of_instruction":
            optional(
                row[
                    "language_of_instruction"
                ]
            ),

        "tuition_fee":
            optional(row["tuition_fee"]),

        "tuition_currency":
            optional(
                row["tuition_currency"]
            ),

        "tuition_period":
            optional(row["tuition_period"]),

        "minimum_gpa":
            optional(row["minimum_gpa"]),

        "gpa_scale":
            optional(row["gpa_scale"]),

        "ielts_requirement":
            optional(
                row["ielts_requirement"]
            ),

        "toefl_requirement":
            optional(
                row["toefl_requirement"]
            ),

        "intake":
            optional(row["intake"]),

        "application_deadline":
            optional(
                row["application_deadline"]
            ),

        "program_url":
            optional(row["program_url"]),

        "collected_at":
            TODAY,

        "last_verified_at":
            TODAY,

        "freshness_status":
            "current",
    }


    try:

        transformed = tp.transform_program(
            raw_record=raw,
            row_number=row_number,
            valid_university_ids=(
                valid_university_ids
            ),
        )

        transform_pass.append(
            transformed
        )

    except Exception as exc:

        transform_fail.append(
            (
                clean(row["program_id"]),
                str(exc),
            )
        )


# ============================================================
# Output
# ============================================================

print()
print(
    "TAIWAN BATCH-1 RESEARCH AUDIT"
)
print("-" * 114)

print(
    "Batch universities                :",
    10,
)

print(
    "Batch programme slots              :",
    len(batch),
)

print(
    "Batch VERIFIED programmes         :",
    sum(
        clean(row["research_status"])
        == "VERIFIED"
        for row in batch
    ),
)

print(
    "Remaining PENDING slots           :",
    sum(
        clean(row["research_status"])
        == "PENDING"
        for row in remaining
    ),
)

print()
print(
    "All-queue identity statuses       :",
    dict(identity_statuses),
)

print(
    "All-queue research statuses       :",
    dict(research_statuses),
)

print(
    "All-queue international statuses  :",
    dict(international_statuses),
)

print()
print(
    "Duration populated                :",
    duration_count,
    "/ 30",
)

print(
    "Study mode populated              :",
    mode_count,
    "/ 30",
)

print(
    "Language populated                :",
    language_count,
    "/ 30",
)

print(
    "Unknown language                  :",
    len(unknown_language_ids),
    "/ 30",
)

print(
    "Tuition populated                 :",
    tuition_count,
    "/ 30",
)

print(
    "IELTS populated                   :",
    ielts_count,
    "/ 30",
)

print(
    "TOEFL populated                   :",
    toefl_count,
    "/ 30",
)

print(
    "Future intake populated           :",
    intake_count,
    "/ 30",
)

print(
    "Future deadline populated         :",
    deadline_count,
    "/ 30",
)

print()
print(
    "verified_yes blank URLs           :",
    len(verified_yes_blank_urls),
)

print(
    "Transform PASS                    :",
    len(transform_pass),
)

print(
    "Transform FAIL                    :",
    len(transform_fail),
)


if transform_fail:

    print()

    for pid, error in transform_fail:
        print(
            "TRANSFORM FAIL:",
            pid,
            "->",
            error,
        )


print()
print(
    "Unknown-language IDs:"
)

print(
    ", ".join(
        unknown_language_ids
    )
)


print()
print(
    "Queue backup                      :",
    queue_backup,
)

print(
    "Updated queue                     :",
    QUEUE,
)

print(
    "Evidence ledger                   :",
    EVIDENCE,
)


# ============================================================
# Exact gate
# ============================================================

errors = []


if len(batch) != 30:
    errors.append(
        "Expected exactly 30 Batch-1 rows."
    )


if sum(
    clean(row["research_status"])
    == "VERIFIED"
    for row in batch
) != 30:
    errors.append(
        "Expected 30 verified Batch-1 programmes."
    )


if sum(
    clean(row["research_status"])
    == "PENDING"
    for row in remaining
) != 60:
    errors.append(
        "Expected remaining 60 slots to stay PENDING."
    )


if identity_statuses != Counter({
    "VERIFIED": 30,
    "PENDING": 60,
}):
    errors.append(
        "Unexpected all-queue identity statuses."
    )


if research_statuses != Counter({
    "VERIFIED": 30,
    "PENDING": 60,
}):
    errors.append(
        "Unexpected all-queue research statuses."
    )


if international_statuses != Counter({
    "verified_yes": 30,
    "PENDING": 60,
}):
    errors.append(
        "Unexpected international status counts."
    )


if duration_count != 9:
    errors.append(
        "Expected duration coverage 9/30."
    )


if mode_count != 0:
    errors.append(
        "No study_mode should be inferred "
        "in Batch 1."
    )


if language_count != 30:
    errors.append(
        "Expected language status/value 30/30."
    )


if len(unknown_language_ids) != 16:
    errors.append(
        "Expected 16 Unknown-language records."
    )


if tuition_count != 0:
    errors.append(
        "Unexpected tuition value populated."
    )


if ielts_count != 1:
    errors.append(
        "Expected exactly one numeric IELTS "
        "requirement in this batch."
    )


if toefl_count != 0:
    errors.append(
        "Unexpected TOEFL numeric value populated."
    )


if intake_count != 0:
    errors.append(
        "Current admission cycle was incorrectly "
        "promoted into canonical future intake."
    )


if deadline_count != 0:
    errors.append(
        "Current-cycle deadline was incorrectly "
        "promoted into canonical future deadline."
    )


if verified_yes_blank_urls:
    errors.append(
        "verified_yes programme has blank "
        "international application URL."
    )


if len(transform_pass) != 30:
    errors.append(
        "Expected all 30 Batch-1 programmes "
        "to pass transform."
    )


if transform_fail:
    errors.append(
        "Transformer compatibility failures exist."
    )


print()
print("=" * 114)


if errors:

    print(
        "STEP 170.4B.1 TAIWAN OFFICIAL "
        "RESEARCH BATCH 1: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 170.4B.1 TAIWAN OFFICIAL "
    "RESEARCH BATCH 1 + TRANSFORM GATE: PASS"
)

print(
    "UNIVERSITIES 001-010 COMPLETE"
)

print(
    "30 PROGRAMMES VERIFIED"
)

print(
    "30 / 30 HAVE VERIFIED "
    "INTERNATIONAL-STUDENT ELIGIBILITY"
)

print(
    "60 TAIWAN RESEARCH SLOTS "
    "REMAIN PENDING"
)

print(
    "ALL 30 VERIFIED PROGRAMMES PASS "
    "THE CURRENT CANONICAL TRANSFORMER"
)

print(
    "programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 114)
