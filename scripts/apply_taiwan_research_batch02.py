import csv
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


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
    "planning/25_taiwan_program_research_evidence_part02.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_170_4b2"
)

TODAY = datetime.now().date().isoformat()


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
    language="Unknown",
    duration="",
    study_mode="",
    ielts="",
    toefl="",
    note="",
):

    RESULTS[pid] = {
        "program_name": name,
        "field_of_study": field,
        "degree_level": "Bachelor",

        "duration_years": duration,
        "study_mode": study_mode,
        "language_of_instruction": language,

        "tuition_fee": "",
        "tuition_currency": "",
        "tuition_period": "",

        "minimum_gpa": "",
        "gpa_scale": "",

        "ielts_requirement": ielts,
        "toefl_requirement": toefl,

        "intake": "",
        "application_deadline": "",

        "program_url": program_url,

        "programme_identity_status":
            "VERIFIED",

        "programme_identity_evidence":
            (
                "Current official university "
                "source verifies this Bachelor "
                "programme."
            ),

        "research_status":
            "VERIFIED",

        "research_note":
            note,

        "international_applicants_status":
            "verified_yes",

        "international_application_url":
            international_url,

        "international_requirements_note":
            international_note,
    }


# ============================================================
# uni_tw_011 - Tamkang University
# prog_tw_031..033
# ============================================================

TKU_PROGRAMS = (
    "https://english.tku.edu.tw/"
    "InternationalPrograms.asp"
)

TKU_INTL = (
    "https://adms.tku.edu.tw/Front/"
    "ForeignStudent/foreignstudentstku/"
    "admissionthefallclass/Page.aspx?"
    "id=3GJ0s4TB73E%3D"
)


add(
    "prog_tw_031",
    (
        "Business Administration "
        "(English-Taught Program)"
    ),
    "Business Administration",
    TKU_PROGRAMS,
    TKU_INTL,
    (
        "Tamkang University's current "
        "2026-2027 international-student "
        "admission route accepts Bachelor "
        "applications, and the programme is "
        "listed as an English-taught Bachelor."
    ),
    language="English",
    note=(
        "Current official international-program "
        "list identifies Business Administration "
        "as an English-taught Bachelor programme."
    ),
)


add(
    "prog_tw_032",
    (
        "English "
        "(English-Taught Program)"
    ),
    "English Language and Literature",
    TKU_PROGRAMS,
    TKU_INTL,
    (
        "Current Tamkang international admission "
        "route supports Bachelor applicants and "
        "the English Department maintains an "
        "English-taught Bachelor programme."
    ),
    language="English",
    note=(
        "Official department information states "
        "that major courses in this Bachelor "
        "programme are conducted in English."
    ),
)


add(
    "prog_tw_033",
    (
        "International Tourism Management "
        "(English-Taught Program)"
    ),
    "Tourism Management",
    TKU_PROGRAMS,
    TKU_INTL,
    (
        "Current 2026-2027 foreign-student "
        "Bachelor admission and the official "
        "international programme list support "
        "international applicants."
    ),
    language="English",
    note=(
        "Current official Tamkang programme "
        "information identifies International "
        "Tourism Management as English-taught."
    ),
)


# ============================================================
# uni_tw_012 - National Sun Yat-sen University
# prog_tw_034..036
# ============================================================

NSYSU_INTL = (
    "https://admission.nsysu.edu.tw/"
    "Member/index"
)


add(
    "prog_tw_034",
    "Electrical Engineering",
    "Electrical Engineering",
    (
        "https://web.ee.nsysu.edu.tw/p/"
        "412-1203-15218.php?Lang=zh-tw"
    ),
    NSYSU_INTL,
    (
        "The current Fall 2026 / Spring 2027 "
        "Electrical Engineering admission page "
        "is explicitly for international "
        "Bachelor applicants."
    ),
    language="English",
    ielts="5.0",
    toefl="61",
    note=(
        "Current department admission page "
        "states Bachelor language of instruction "
        "is EMI/English-taught and requires "
        "IELTS 5.0 or TOEFL iBT 61 for "
        "non-native English applicants."
    ),
)


add(
    "prog_tw_035",
    (
        "Computer Science "
        "and Engineering"
    ),
    "Computer Science",
    (
        "https://cse.nsysu.edu.tw/p/"
        "412-1205-16761.php?Lang=en"
    ),
    NSYSU_INTL,
    (
        "The NSYSU CSE international admission "
        "page explicitly accepts foreign "
        "applicants to its undergraduate "
        "Bachelor programme."
    ),
    language="Unknown",
    ielts="6.5",
    toefl="61",
    note=(
        "Current CSE page publishes undergraduate "
        "international English requirements of "
        "IELTS 6.5 / TOEFL iBT 61. "
        "It also requires Chinese evidence, so "
        "whole-programme language is not inferred "
        "from the English admission requirement."
    ),
)


add(
    "prog_tw_036",
    (
        "International Business "
        "Bachelor Program"
    ),
    "International Business",
    (
        "https://ib.nsysu.edu.tw/"
    ),
    NSYSU_INTL,
    (
        "The current 2026-2027 international "
        "admission guide explicitly lists the "
        "International Business Bachelor Program."
    ),
    language="English Available",
    ielts="6.0",
    toefl="79",
    note=(
        "Current admission guide states that "
        "the programme provides sufficient "
        "English-taught core courses and requires "
        "IELTS 6.0 or TOEFL iBT 79. "
        "English Available is used rather than "
        "claiming every credit is English-taught."
    ),
)


# ============================================================
# uni_tw_013 - National Chung Cheng University
# prog_tw_037..039
#
# Use three Bachelor programmes directly exposed by the
# current CCU international-admission programme pages.
# ============================================================

CCU_INTL = (
    "https://oia.ccu.edu.tw/p/"
    "412-1008-1828.php?Lang=en"
)


add(
    "prog_tw_037",
    (
        "Accounting and "
        "Information Technology"
    ),
    "Accounting and Information Technology",
    CCU_INTL,
    CCU_INTL,
    (
        "CCU's official international-admission "
        "programme information identifies this "
        "department at Bachelor level."
    ),
    language="Chinese",
    note=(
        "Current official international-programme "
        "page states most Bachelor courses are "
        "taught in Chinese. CEFR-level entry "
        "requirements are not converted into "
        "IELTS/TOEFL numeric scores."
    ),
)


add(
    "prog_tw_038",
    "Finance",
    "Finance",
    CCU_INTL,
    CCU_INTL,
    (
        "CCU's current international admission "
        "programme information explicitly lists "
        "Finance at Bachelor level."
    ),
    language="Chinese",
    note=(
        "Current official CCU page states most "
        "courses in the Bachelor programme are "
        "taught in Chinese."
    ),
)


add(
    "prog_tw_039",
    "Information Management",
    "Information Management",
    CCU_INTL,
    CCU_INTL,
    (
        "Current CCU international-admission "
        "programme information explicitly lists "
        "Information Management at Bachelor level."
    ),
    language="Chinese",
    note=(
        "The current official programme information "
        "states most courses are taught in Chinese. "
        "CEFR language requirements are preserved "
        "only as evidence and are not converted "
        "to unsupported IELTS/TOEFL scores."
    ),
)


# ============================================================
# uni_tw_014 - National Taiwan Ocean University
# prog_tw_040..042
# ============================================================

NTOU_PROGRAMS = (
    "https://academic.ntou.edu.tw/p/"
    "412-1005-3456.php?Lang=en"
)

NTOU_INTL = (
    "https://oia.ntou.edu.tw/p/"
    "412-1022-7231.php?Lang=en"
)


add(
    "prog_tw_040",
    "Food Science",
    "Food Science",
    NTOU_PROGRAMS,
    NTOU_INTL,
    (
        "NTOU's current international admission "
        "information lists Food Science as "
        "available at Bachelor level."
    ),
    note=(
        "Programme identity and international "
        "Bachelor eligibility are verified. "
        "Whole-programme MOI remains Unknown."
    ),
)


add(
    "prog_tw_041",
    "Aquaculture",
    "Aquaculture",
    NTOU_PROGRAMS,
    NTOU_INTL,
    (
        "NTOU's official international admission "
        "list marks Aquaculture as available "
        "at Bachelor level."
    ),
    note=(
        "No language is inferred from the "
        "existence of English webpages or "
        "general language requirements."
    ),
)


add(
    "prog_tw_042",
    (
        "Computer Science "
        "and Engineering"
    ),
    "Computer Science",
    NTOU_PROGRAMS,
    NTOU_INTL,
    (
        "NTOU's official international admission "
        "list marks Computer Science and "
        "Engineering as available at Bachelor level."
    ),
    note=(
        "Bachelor identity and international "
        "eligibility verified; whole-programme "
        "language remains Unknown."
    ),
)


# ============================================================
# uni_tw_015 - National Dong Hwa University
# prog_tw_043..045
# ============================================================

NDHU_GUIDE = (
    "https://rb027.ndhu.edu.tw/var/file/"
    "27/1027/img/4756/894840940.pdf"
)

NDHU_INTL = (
    "https://oia.ndhu.edu.tw/p/"
    "412-1027-21529.php?Lang=en"
)


add(
    "prog_tw_043",
    (
        "Management Science "
        "and Finance"
    ),
    "Management Science and Finance",
    NDHU_GUIDE,
    NDHU_INTL,
    (
        "NDHU's current 2026 Fall international "
        "admission guide lists the Bachelor Program "
        "of Management Science and Finance."
    ),
    language="English",
    note=(
        "Current official guide states all courses "
        "in this international Bachelor programme "
        "are taught in English."
    ),
)


add(
    "prog_tw_044",
    (
        "Computer Science and "
        "Information Engineering "
        "(International Bachelor)"
    ),
    "Computer Science",
    NDHU_GUIDE,
    NDHU_INTL,
    (
        "The current NDHU admission guide "
        "explicitly lists the International "
        "Bachelor track in CSIE."
    ),
    language="English",
    note=(
        "Current official guide differentiates "
        "the regular Chinese-taught Bachelor "
        "from the English-taught International "
        "Bachelor. This record uses the "
        "International Bachelor track."
    ),
)


add(
    "prog_tw_045",
    (
        "Bachelor Degree Program "
        "of Data Science"
    ),
    "Data Science",
    NDHU_GUIDE,
    NDHU_INTL,
    (
        "NDHU's current international admission "
        "guide lists the Bachelor Degree Program "
        "of Data Science."
    ),
    language="English",
    note=(
        "Current 2026 guide marks the programme "
        "as full English-taught."
    ),
)


# ============================================================
# uni_tw_016 - National University of Kaohsiung
# prog_tw_046..048
# ============================================================

NUK_GUIDE = (
    "https://interadmission.nuk.edu.tw/"
    "var/file/63/1063/img/659330395.pdf"
)

NUK_INTL = (
    "https://rinteradmission.nuk.edu.tw/"
)


add(
    "prog_tw_046",
    "Electrical Engineering",
    "Electrical Engineering",
    NUK_GUIDE,
    NUK_INTL,
    (
        "NUK's official international admission "
        "material lists Electrical Engineering "
        "as a Bachelor programme available "
        "to international applicants."
    ),
    note=(
        "Programme-level language remains Unknown. "
        "General admission language thresholds "
        "are not treated as programme MOI."
    ),
)


add(
    "prog_tw_047",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    NUK_GUIDE,
    NUK_INTL,
    (
        "NUK's official international admission "
        "material lists CSIE at Bachelor level."
    ),
    note=(
        "International Bachelor availability "
        "verified; language remains Unknown."
    ),
)


add(
    "prog_tw_048",
    (
        "Asia-Pacific Industrial "
        "and Business Management"
    ),
    "Business Administration",
    NUK_GUIDE,
    NUK_INTL,
    (
        "NUK's official international admission "
        "material lists Asia-Pacific Industrial "
        "and Business Management at Bachelor level."
    ),
    note=(
        "International Bachelor programme "
        "identity verified. Whole-programme "
        "teaching language remains Unknown."
    ),
)


# ============================================================
# uni_tw_017 - National Kaohsiung University
# of Science and Technology
# prog_tw_049..051
# ============================================================

NKUST_2026 = (
    "https://oia.nkust.edu.tw/images/upload/"
    "files/%E5%AD%B8%E5%A3%ABBachelor%20"
    "Admission%20List.pdf"
)

NKUST_INTL = (
    "https://oia.nkust.edu.tw/en/"
    "news_det-149.html"
)


add(
    "prog_tw_049",
    "International Management",
    "International Management",
    NKUST_2026,
    NKUST_INTL,
    (
        "NKUST's official 2026 Fall Bachelor "
        "international admission list contains "
        "accepted applicants to the Department "
        "of International Management."
    ),
    note=(
        "Current real admission evidence verifies "
        "programme identity and international "
        "eligibility. Language remains Unknown."
    ),
)


add(
    "prog_tw_050",
    "Logistics Management",
    "Logistics Management",
    NKUST_2026,
    NKUST_INTL,
    (
        "The official 2026 Fall Bachelor admission "
        "list contains accepted foreign applicants "
        "to Logistics Management."
    ),
    note=(
        "No programme-wide language is inferred "
        "from admission evidence."
    ),
)


add(
    "prog_tw_051",
    "Business Management",
    "Business Administration",
    NKUST_2026,
    NKUST_INTL,
    (
        "NKUST's official 2026 Fall Bachelor "
        "admission results contain accepted "
        "international applicants to Business "
        "Management."
    ),
    note=(
        "International eligibility is supported "
        "by actual current admission results; "
        "language remains Unknown."
    ),
)


# ============================================================
# uni_tw_018 - National Yunlin University
# of Science and Technology
# prog_tw_052..054
# ============================================================

YUNTECH_GUIDE = (
    "https://aax.yuntech.edu.tw/images/content/"
    "%E5%9C%8B%E9%9A%9B%E5%AD%B8%E7%94%9F"
    "%E7%94%B3%E8%AB%8B%E5%85%A5%E5%AD%B8/"
    "115/2026%E5%B9%B4%E7%A7%8B%E5%AD%A3"
    "%E7%8F%AD%E5%A4%96%E5%9C%8B%E5%AD%B8"
    "%E7%94%9F%E7%94%B3%E8%AB%8B%E5%85%A5"
    "%E5%AD%B8%E7%B0%A1%E7%AB%A0%202026%20"
    "Fall%20Application%20Guide%20.pdf"
)

YUNTECH_INTL = (
    "https://admissions-oia.yuntech.edu.tw/"
    "intladmission/index/index/"
    "applyIntladmissionSn/68"
)


add(
    "prog_tw_052",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    YUNTECH_GUIDE,
    YUNTECH_INTL,
    (
        "YunTech's official 2026 Fall foreign "
        "student guide includes the Department "
        "of Computer Science and Information "
        "Engineering at Bachelor level."
    ),
    note=(
        "The guide requires Chinese A2 for "
        "Bachelor admission, but an admission "
        "language threshold is not automatically "
        "treated as whole-programme MOI."
    ),
)


add(
    "prog_tw_053",
    (
        "Industrial Engineering "
        "and Management"
    ),
    "Industrial Engineering and Management",
    YUNTECH_GUIDE,
    YUNTECH_INTL,
    (
        "The current 2026 Fall international "
        "admission guide lists Industrial "
        "Engineering and Management at "
        "Bachelor level."
    ),
    note=(
        "Chinese A2 is an admission requirement; "
        "programme MOI remains Unknown unless "
        "the teaching-method legend can be "
        "unambiguously normalized."
    ),
)


add(
    "prog_tw_054",
    "Business Administration",
    "Business Administration",
    YUNTECH_GUIDE,
    YUNTECH_INTL,
    (
        "YunTech's current 2026 Fall guide "
        "lists Business Administration "
        "at Bachelor level."
    ),
    note=(
        "The Bachelor requires Chinese B1 "
        "admission proficiency. This is not "
        "force-converted into programme MOI."
    ),
)


# ============================================================
# uni_tw_019 - National Pingtung University
# of Science and Technology
# prog_tw_055..057
# ============================================================

NPUST_INTL = (
    "https://courseeng.npust.edu.tw/"
    "Admission/"
)


add(
    "prog_tw_055",
    (
        "Tropical Agriculture "
        "and International Cooperation"
    ),
    "Agriculture",
    (
        "https://dtaic.npust.edu.tw/en/"
    ),
    NPUST_INTL,
    (
        "NPUST's current international admission "
        "system accepts Bachelor applicants, and "
        "the current OIA programme list identifies "
        "this department at Bachelor level."
    ),
    language="English",
    note=(
        "The department states that it offers "
        "full degree programmes in English; "
        "the current NPUST OIA list also marks "
        "this Bachelor as English-taught."
    ),
)


add(
    "prog_tw_056",
    "Aquaculture",
    "Aquaculture",
    (
        "https://aqua.npust.edu.tw/"
        "english-version/"
    ),
    NPUST_INTL,
    (
        "NPUST's current international admission "
        "information lists Aquaculture at "
        "Bachelor level."
    ),
    language="Chinese",
    note=(
        "Current NPUST OIA programme/language "
        "information lists the Aquaculture "
        "Bachelor among Chinese-taught programmes."
    ),
)


add(
    "prog_tw_057",
    "Veterinary Medicine",
    "Veterinary Medicine",
    (
        "https://vm.npust.edu.tw/english/"
    ),
    NPUST_INTL,
    (
        "NPUST's current international admission "
        "guidance explicitly provides a Bachelor "
        "admission language requirement for "
        "Veterinary Medicine, confirming foreign "
        "Bachelor eligibility."
    ),
    language="Chinese",
    note=(
        "Current OIA guidance requires TOCFL B1 "
        "for Veterinary Medicine Bachelor "
        "applicants. The programme is retained "
        "as Chinese in line with the current "
        "OIA Chinese-program admission route. "
        "No IELTS/TOEFL score is invented."
    ),
)


# ============================================================
# uni_tw_020 - National United University
# prog_tw_058..060
# ============================================================

NUU_INTL = (
    "https://enroll.nuu.edu.tw/p/"
    "405-1065-76354%2Cc735.php"
)


add(
    "prog_tw_058",
    "Electrical Engineering",
    "Electrical Engineering",
    (
        "https://ee.nuu.edu.tw/"
        "app/index.php?Lang=en"
    ),
    NUU_INTL,
    (
        "NUU's official Academic Year 2026 "
        "International Student Admission Brochure "
        "provides the foreign-student application "
        "route, while the EE department confirms "
        "its undergraduate programme."
    ),
    note=(
        "Programme identity and current "
        "international application route verified. "
        "Whole-programme MOI remains Unknown."
    ),
)


add(
    "prog_tw_059",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    (
        "https://csie.nuu.edu.tw/p/"
        "404-1041-40579.php?Lang=zh-tw"
    ),
    NUU_INTL,
    (
        "NUU has a current 2026 international "
        "admission brochure and CSIE confirms "
        "an active undergraduate programme."
    ),
    note=(
        "Department source confirms the regular "
        "undergraduate programme. The separately "
        "mentioned four-year evening programme "
        "is not used to infer duration for the "
        "regular Bachelor record."
    ),
)


add(
    "prog_tw_060",
    "Business Management",
    "Business Administration",
    (
        "https://bm.nuu.edu.tw/"
    ),
    NUU_INTL,
    (
        "NUU's current 2026 international "
        "admission route supports degree-seeking "
        "foreign students and the university "
        "maintains the Business Management "
        "undergraduate programme."
    ),
    note=(
        "Programme identity and international "
        "eligibility verified. Duration and "
        "whole-programme language remain unresolved."
    ),
)


# ============================================================
# Load queue
# ============================================================

print("=" * 114)

print(
    "STEP 170.4B.2 - TAIWAN OFFICIAL RESEARCH "
    "BATCH 2 (UNIVERSITIES 011-020)"
)

print("=" * 114)


if not QUEUE.exists():

    raise FileNotFoundError(
        f"Taiwan queue missing: {QUEUE}"
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
        f"Expected 90 Taiwan slots, "
        f"found {len(rows)}."
    )


expected_batch_ids = {
    f"prog_tw_{i:03d}"
    for i in range(
        31,
        61,
    )
}


if set(RESULTS) != expected_batch_ids:

    raise ValueError(
        "Batch-2 result set must be "
        "exactly prog_tw_031..060."
    )


row_by_id = {
    clean(
        row["program_id"]
    ): row
    for row in rows
}


# ============================================================
# Parent mapping + safe state precondition
# ============================================================

for number in range(
    31,
    61,
):

    pid = (
        f"prog_tw_{number:03d}"
    )

    expected_parent_number = (
        ((number - 1) // 3) + 1
    )

    expected_parent = (
        f"uni_tw_{expected_parent_number:03d}"
    )

    actual_parent = clean(
        row_by_id[
            pid
        ][
            "university_id"
        ]
    )


    if actual_parent != expected_parent:

        raise ValueError(
            f"{pid}: expected parent "
            f"{expected_parent}, found "
            f"{actual_parent}."
        )


    if clean(
        row_by_id[
            pid
        ][
            "research_status"
        ]
    ) != "PENDING":

        raise ValueError(
            f"{pid}: expected PENDING before "
            "Batch 2, found "
            f"{row_by_id[pid]['research_status']}."
        )


# Ensure Batch 1 remains complete.

batch1 = [
    row_by_id[
        f"prog_tw_{i:03d}"
    ]
    for i in range(
        1,
        31,
    )
]


if any(
    clean(
        row["research_status"]
    ) != "VERIFIED"
    for row in batch1
):

    raise ValueError(
        "Safety stop: Batch 1 is no longer "
        "30/30 VERIFIED."
    )


# Ensure Batch 3 has not been modified.

batch3 = [
    row_by_id[
        f"prog_tw_{i:03d}"
    ]
    for i in range(
        61,
        91,
    )
]


if any(
    clean(
        row["research_status"]
    ) != "PENDING"
    for row in batch3
):

    raise ValueError(
        "Safety stop: Batch 3 should still "
        "be completely PENDING."
    )


# ============================================================
# Backup queue before modification
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
    f"before_batch02_{timestamp}.csv"
)


shutil.copy2(
    QUEUE,
    queue_backup,
)


if EVIDENCE.exists():

    evidence_backup = BACKUP_DIR / (
        "25_taiwan_program_research_"
        "evidence_part02_before_rebuild_"
        f"{timestamp}.csv"
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
# Apply only prog_tw_031..060
# ============================================================

UPDATE_FIELDS = [
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


for field in UPDATE_FIELDS:

    if field not in headers:

        raise ValueError(
            f"Queue missing field: {field}"
        )


for row in rows:

    pid = clean(
        row.get(
            "program_id"
        )
    )

    if pid not in RESULTS:
        continue


    result = RESULTS[
        pid
    ]


    for field in UPDATE_FIELDS:

        row[field] = result[
            field
        ]


    row[
        "last_verified_at"
    ] = TODAY


    row[
        "international_applicants_last_verified_at"
    ] = TODAY


# ============================================================
# Evidence ledger Part 02
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


DETAIL_FIELDS = [
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

    if pid not in expected_batch_ids:
        continue


    verified_fields = [
        field
        for field in DETAIL_FIELDS
        if clean(
            row.get(field)
        )
    ]


    unresolved_fields = [
        field
        for field in DETAIL_FIELDS
        if not clean(
            row.get(field)
        )
    ]


    evidence_rows.append(
        {
            "program_id":
                pid,

            "university_id":
                clean(
                    row[
                        "university_id"
                    ]
                ),

            "university_name":
                clean(
                    row[
                        "university_name"
                    ]
                ),

            "program_name":
                clean(
                    row[
                        "program_name"
                    ]
                ),

            "degree_level":
                clean(
                    row[
                        "degree_level"
                    ]
                ),

            "programme_source_url":
                clean(
                    row[
                        "program_url"
                    ]
                ),

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
                    row[
                        "research_note"
                    ]
                ),

            "verified_at":
                TODAY,
        }
    )


# ============================================================
# Write updated queue + evidence
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
    writer.writerows(
        rows
    )


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
# Audit Batch 2
# ============================================================

batch2 = [
    row
    for row in rows
    if clean(
        row["program_id"]
    ) in expected_batch_ids
]


identity_statuses = Counter(
    clean(
        row[
            "programme_identity_status"
        ]
    )
    for row in rows
)


research_statuses = Counter(
    clean(
        row[
            "research_status"
        ]
    )
    for row in rows
)


international_statuses = Counter(
    clean(
        row[
            "international_applicants_status"
        ]
    )
    for row in rows
)


def populated(field):

    return sum(
        bool(
            clean(
                row.get(field)
            )
        )
        for row in batch2
    )


duration_count = populated(
    "duration_years"
)

mode_count = populated(
    "study_mode"
)

language_count = populated(
    "language_of_instruction"
)

tuition_count = populated(
    "tuition_fee"
)

ielts_count = populated(
    "ielts_requirement"
)

toefl_count = populated(
    "toefl_requirement"
)

intake_count = populated(
    "intake"
)

deadline_count = populated(
    "application_deadline"
)


unknown_language_ids = sorted(
    clean(
        row["program_id"]
    )
    for row in batch2
    if clean(
        row[
            "language_of_instruction"
        ]
    ) == "Unknown"
)


verified_yes_blank_urls = sorted(
    clean(
        row[
            "program_id"
        ]
    )
    for row in batch2
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


missing_identity = sorted(
    clean(
        row[
            "program_id"
        ]
    )
    for row in batch2
    if (
        not clean(
            row[
                "program_name"
            ]
        )
        or not clean(
            row[
                "field_of_study"
            ]
        )
        or not clean(
            row[
                "degree_level"
            ]
        )
        or not clean(
            row[
                "program_url"
            ]
        )
    )
)


# ============================================================
# Canonical transform gate
# ============================================================

valid_university_ids = (
    tp.load_valid_university_ids()
)


transform_pass = []

transform_fail = []


for row_number, row in enumerate(
    batch2,
    start=2,
):

    raw = {
        "program_id":
            optional(
                row[
                    "program_id"
                ]
            ),

        "university_id":
            optional(
                row[
                    "university_id"
                ]
            ),

        "program_name":
            optional(
                row[
                    "program_name"
                ]
            ),

        "field_of_study":
            optional(
                row[
                    "field_of_study"
                ]
            ),

        "degree_level":
            optional(
                row[
                    "degree_level"
                ]
            ),

        "duration_years":
            optional(
                row[
                    "duration_years"
                ]
            ),

        "study_mode":
            optional(
                row[
                    "study_mode"
                ]
            ),

        "language_of_instruction":
            optional(
                row[
                    "language_of_instruction"
                ]
            ),

        "tuition_fee":
            optional(
                row[
                    "tuition_fee"
                ]
            ),

        "tuition_currency":
            optional(
                row[
                    "tuition_currency"
                ]
            ),

        "tuition_period":
            optional(
                row[
                    "tuition_period"
                ]
            ),

        "minimum_gpa":
            optional(
                row[
                    "minimum_gpa"
                ]
            ),

        "gpa_scale":
            optional(
                row[
                    "gpa_scale"
                ]
            ),

        "ielts_requirement":
            optional(
                row[
                    "ielts_requirement"
                ]
            ),

        "toefl_requirement":
            optional(
                row[
                    "toefl_requirement"
                ]
            ),

        "intake":
            optional(
                row[
                    "intake"
                ]
            ),

        "application_deadline":
            optional(
                row[
                    "application_deadline"
                ]
            ),

        "program_url":
            optional(
                row[
                    "program_url"
                ]
            ),

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
                clean(
                    row[
                        "program_id"
                    ]
                ),
                str(exc),
            )
        )


# ============================================================
# Output
# ============================================================

print()
print(
    "TAIWAN BATCH-2 RESEARCH AUDIT"
)

print("-" * 114)


print(
    "Batch universities                :",
    10,
)

print(
    "Batch programme slots              :",
    len(batch2),
)

print(
    "Batch VERIFIED programmes         :",
    sum(
        clean(
            row[
                "research_status"
            ]
        ) == "VERIFIED"
        for row in batch2
    ),
)

print(
    "Remaining PENDING slots           :",
    sum(
        clean(
            row[
                "research_status"
            ]
        ) == "PENDING"
        for row in rows
    ),
)


print()
print(
    "All-queue identity statuses       :",
    dict(
        identity_statuses
    ),
)

print(
    "All-queue research statuses       :",
    dict(
        research_statuses
    ),
)

print(
    "All-queue international statuses  :",
    dict(
        international_statuses
    ),
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
    len(
        unknown_language_ids
    ),
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
    "Verified rows missing identity    :",
    len(
        missing_identity
    ),
)

print(
    "verified_yes blank URLs           :",
    len(
        verified_yes_blank_urls
    ),
)

print(
    "Transform PASS                    :",
    len(
        transform_pass
    ),
)

print(
    "Transform FAIL                    :",
    len(
        transform_fail
    ),
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
# Exact acceptance gate
# ============================================================

errors = []


if len(
    batch2
) != 30:

    errors.append(
        "Expected 30 Batch-2 records."
    )


if sum(
    clean(
        row[
            "research_status"
        ]
    ) == "VERIFIED"
    for row in batch2
) != 30:

    errors.append(
        "Expected 30 VERIFIED Batch-2 programmes."
    )


if identity_statuses != Counter({
    "VERIFIED": 60,
    "PENDING": 30,
}):

    errors.append(
        "Unexpected all-queue identity statuses."
    )


if research_statuses != Counter({
    "VERIFIED": 60,
    "PENDING": 30,
}):

    errors.append(
        "Unexpected all-queue research statuses."
    )


if international_statuses != Counter({
    "verified_yes": 60,
    "PENDING": 30,
}):

    errors.append(
        "Unexpected international status counts."
    )


if duration_count != 0:

    errors.append(
        "Unexpected duration populated in Batch 2."
    )


if mode_count != 0:

    errors.append(
        "Unexpected study_mode populated."
    )


if language_count != 30:

    errors.append(
        "Expected language/status value 30/30."
    )


if len(
    unknown_language_ids
) != 16:

    errors.append(
        "Expected 16 Unknown-language records."
    )


if tuition_count != 0:

    errors.append(
        "Unexpected tuition value populated."
    )


if ielts_count != 3:

    errors.append(
        "Expected numeric IELTS evidence "
        "for 3 NSYSU programmes."
    )


if toefl_count != 3:

    errors.append(
        "Expected numeric TOEFL evidence "
        "for 3 NSYSU programmes."
    )


if intake_count != 0:

    errors.append(
        "Current-cycle intake was incorrectly "
        "promoted into the future intake field."
    )


if deadline_count != 0:

    errors.append(
        "Current-cycle deadline was incorrectly "
        "promoted into future deadline."
    )


if missing_identity:

    errors.append(
        "One or more VERIFIED programmes "
        "have incomplete identity."
    )


if verified_yes_blank_urls:

    errors.append(
        "verified_yes row has blank "
        "international application URL."
    )


if len(
    transform_pass
) != 30:

    errors.append(
        "Expected Transform PASS 30."
    )


if transform_fail:

    errors.append(
        "Transformer compatibility failures exist."
    )


print()
print("=" * 114)


if errors:

    print(
        "STEP 170.4B.2 TAIWAN OFFICIAL "
        "RESEARCH BATCH 2: FAIL"
    )

    for error in errors:

        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 170.4B.2 TAIWAN OFFICIAL "
    "RESEARCH BATCH 2 + TRANSFORM GATE: PASS"
)

print(
    "UNIVERSITIES 011-020 COMPLETE"
)

print(
    "30 ADDITIONAL PROGRAMMES VERIFIED"
)

print(
    "TAIWAN VERIFIED SO FAR: 60 / 90"
)

print(
    "INTERNATIONAL ELIGIBILITY "
    "VERIFIED_YES: 60 / 90"
)

print(
    "30 TAIWAN RESEARCH SLOTS "
    "REMAIN PENDING"
)

print(
    "ALL BATCH-2 PROGRAMMES PASS "
    "THE CURRENT CANONICAL TRANSFORMER"
)

print(
    "programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 114)
