import csv
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


SCRIPTS_DIR = Path("scripts").resolve()

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import transform_programs as tp


QUEUE = Path(
    "planning/24_taiwan_program_research_queue.csv"
)

EVIDENCE = Path(
    "planning/25_taiwan_program_research_evidence_part03.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_170_4b3"
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
    international_status,
    international_url,
    international_note,
    *,
    duration="",
    study_mode="",
    language="Unknown",
    tuition="",
    currency="",
    period="",
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

        "tuition_fee": tuition,
        "tuition_currency": currency,
        "tuition_period": period,

        "minimum_gpa": "",
        "gpa_scale": "",

        "ielts_requirement": ielts,
        "toefl_requirement": toefl,

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
            international_status,

        "international_application_url":
            international_url,

        "international_requirements_note":
            international_note,
    }


# ============================================================
# uni_tw_021 - National Taipei University
# prog_tw_061..063
# ============================================================

NTPU_GUIDE = (
    "https://cms-carrier.ntpu.edu.tw/uploads/"
    "114_NTPU_Admission_Brochure_"
    "Spring_semester_2026_1_628562954d.pdf"
)

add(
    "prog_tw_061",
    (
        "Bachelor Program in Smart Sustainable "
        "Development and Management"
    ),
    "Sustainability and Management",
    NTPU_GUIDE,
    "verified_yes",
    NTPU_GUIDE,
    (
        "NTPU's official international-student "
        "admission brochure lists this programme "
        "as open at Bachelor level."
    ),
    language="English",
    note=(
        "Official international brochure marks "
        "this Bachelor programme as English-taught."
    ),
)

add(
    "prog_tw_062",
    "Business Administration",
    "Business Administration",
    "https://www.aacsb.ntpu.edu.tw/en/page.php?id=3&ids=1",
    "verified_yes",
    NTPU_GUIDE,
    (
        "NTPU international admission material "
        "lists Business Administration as open "
        "to international Bachelor applicants."
    ),
    duration="4",
    language="English Available",
    note=(
        "Official NTPU business-school information "
        "states the BBA has a four-year curriculum. "
        "English-taught courses are available, but "
        "the whole programme is not represented "
        "as fully English-taught."
    ),
)

add(
    "prog_tw_063",
    "Statistics",
    "Statistics",
    NTPU_GUIDE,
    "verified_yes",
    NTPU_GUIDE,
    (
        "NTPU's international-student brochure "
        "lists the Department of Statistics as "
        "available at Bachelor level."
    ),
    language="English Available",
    note=(
        "Official brochure reports some English "
        "instruction; it is stored as English "
        "Available rather than full English MOI."
    ),
)


# ============================================================
# uni_tw_022 - Fu Jen Catholic University
# prog_tw_064..066
# ============================================================

FJU_GUIDE = (
    "https://idsaoie.fju.edu.tw/"
    "DownloadNewsFileServlet?file=14"
)

FJU_INTL = (
    "https://idsaoie.fju.edu.tw/"
)


add(
    "prog_tw_064",
    "English Language and Literature",
    "English Language and Literature",
    (
        "https://english.fju.edu.tw/"
        "admission_ba_detail_e.asp?"
        "AUC_No=8&AU_ID=10"
    ),
    "verified_yes",
    FJU_INTL,
    (
        "FJCU's current Fall 2026 foreign-student "
        "admission materials explicitly provide "
        "Bachelor admission to the Department of "
        "English Language and Literature."
    ),
    language="Unknown",
    tuition="47430",
    currency="TWD",
    period="Semester",
    note=(
        "Current Fall 2026 application evidence "
        "requires English evaluation, but this is "
        "not treated as proof that every programme "
        "course is delivered in English. "
        "Current international-student tuition "
        "category is NT$47,430 per semester."
    ),
)

add(
    "prog_tw_065",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    FJU_GUIDE,
    "verified_yes",
    FJU_INTL,
    (
        "The current FJCU foreign-student "
        "admission brochure includes CSIE at "
        "Bachelor level."
    ),
    language="Unknown",
    tuition="55350",
    currency="TWD",
    period="Semester",
    note=(
        "Current FJCU tuition table places CSIE "
        "at NT$55,350 per semester. "
        "Whole-programme language remains Unknown."
    ),
)

add(
    "prog_tw_066",
    (
        "Bachelor's Program in "
        "Interdisciplinary Studies"
    ),
    "Interdisciplinary Studies",
    FJU_GUIDE,
    "verified_yes",
    FJU_INTL,
    (
        "FJCU's current Fall 2026 international "
        "admission materials and admission results "
        "explicitly include this Bachelor programme."
    ),
    language="English",
    tuition="71360",
    currency="TWD",
    period="Semester",
    note=(
        "The programme is explicitly presented as "
        "the English-taught interdisciplinary "
        "Bachelor programme. Current tuition is "
        "NT$71,360 per semester."
    ),
)


# ============================================================
# uni_tw_023 - Feng Chia University
# prog_tw_067..069
#
# Programme identity = verified.
# International eligibility stays unknown because this pass
# did not obtain sufficiently explicit current programme-level
# first-year foreign degree admission evidence.
# ============================================================

FCU_PROGRAMS = (
    "https://registration.fcu.edu.tw/en/news/"
    "114%E5%AD%B8%E5%B9%B4%E5%BA%A6"
    "%E6%96%B0%E7%94%9F%E5%BF%85"
    "%E9%81%B8%E4%BF%AE%E7%A7%91%E7%9B%AE/"
)

FCU_OIA = (
    "https://oia.fcu.edu.tw/en/"
)


add(
    "prog_tw_067",
    (
        "Bachelor's Program of "
        "International Business "
        "Administration in English"
    ),
    "International Business Administration",
    "https://business.fcu.edu.tw/en/%E6%8B%9B%E7%94%9F/",
    "unknown",
    "",
    (
        "The current programme identity and its "
        "international learning environment are "
        "verified, but an explicit current "
        "programme-level first-year foreign-degree "
        "admission route was not sufficiently "
        "verified in this pass."
    ),
    language="English",
    note=(
        "FCU officially identifies this as an "
        "English-taught Bachelor programme with "
        "international students. International "
        "eligibility is nevertheless kept unknown "
        "under the stricter evidence rule."
    ),
)

add(
    "prog_tw_068",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    FCU_PROGRAMS,
    "unknown",
    "",
    (
        "Current FCU sources verify the Bachelor "
        "programme, but explicit current "
        "programme-level international first-year "
        "eligibility was not sufficiently verified."
    ),
    language="Unknown",
    note=(
        "Programme identity is current. "
        "International status remains unknown "
        "rather than inferred from university-level "
        "international-student services."
    ),
)

add(
    "prog_tw_069",
    (
        "Bachelor's Program in Artificial "
        "Intelligence Technology and Applications"
    ),
    "Artificial Intelligence",
    FCU_PROGRAMS,
    "unknown",
    "",
    (
        "Current FCU curriculum information "
        "verifies this Bachelor programme. "
        "Programme-level current foreign-degree "
        "eligibility remains unresolved."
    ),
    language="Unknown",
    note=(
        "No international eligibility or MOI "
        "is inferred from the English university "
        "website."
    ),
)


# ============================================================
# uni_tw_024 - Tunghai University
# prog_tw_070..072
# ============================================================

THU_GUIDE = (
    "https://exam2.thu.edu.tw/EXAM/"
    "download_doc_25/115_regulations.pdf?"
    "s=20260224120522"
)

THU_INTL = (
    "https://exam2.thu.edu.tw/EXAM/"
    "index.jsp?DOC=25"
)


add(
    "prog_tw_070",
    (
        "Computer Science "
        "(International Division)"
    ),
    "Computer Science",
    THU_GUIDE,
    "verified_yes",
    THU_INTL,
    (
        "Tunghai's current 2026 international "
        "degree-student brochure lists the "
        "Computer Science International Division "
        "at Bachelor level."
    ),
    language="English",
    note=(
        "Current Tunghai official EMI information "
        "identifies the Computer Science "
        "International Division as an "
        "English-medium Bachelor programme."
    ),
)

add(
    "prog_tw_071",
    (
        "Business Administration: "
        "Global Elite Program"
    ),
    "Business Administration",
    THU_GUIDE,
    "verified_yes",
    THU_INTL,
    (
        "Current Tunghai international admission "
        "brochure lists this programme at "
        "Bachelor level."
    ),
    language="English",
    note=(
        "Official 2026 brochure explicitly marks "
        "the Global Elite Program as English-taught."
    ),
)

add(
    "prog_tw_072",
    (
        "International Business: "
        "Global Elite Program"
    ),
    "International Business",
    THU_GUIDE,
    "verified_yes",
    THU_INTL,
    (
        "Current Tunghai international admission "
        "brochure lists the International Business "
        "Global Elite Program at Bachelor level."
    ),
    language="English",
    note=(
        "Official 2026 material identifies this "
        "as an English-taught Bachelor programme."
    ),
)


# ============================================================
# uni_tw_025 - Soochow University
# prog_tw_073..075
# ============================================================

SCU_GUIDE = (
    "https://www.scu.edu.tw/entrance/"
    "anounce/115/H/01Fall/h-book-1t.pdf"
)

SCU_INTL = (
    "https://web-en.scu.edu.tw/"
    "entrance/web_page/460"
)


add(
    "prog_tw_073",
    "Data Science",
    "Data Science",
    "https://web-en.scu.edu.tw/datascience",
    "verified_yes",
    SCU_INTL,
    (
        "Soochow's current 2026 international "
        "admission prospectus includes the "
        "Department of Data Science at "
        "Bachelor level."
    ),
    duration="4",
    language="Unknown",
    note=(
        "Soochow's 2026 prospectus states "
        "Bachelor programmes outside Law have "
        "a four-year normal duration. "
        "Chinese admission proficiency is not "
        "automatically converted into MOI."
    ),
)

add(
    "prog_tw_074",
    "Business Administration",
    "Business Administration",
    "https://www.ba.scu.edu.tw/en/",
    "verified_yes",
    SCU_INTL,
    (
        "Current Soochow international admission "
        "materials and department admissions "
        "information support international "
        "Bachelor applicants."
    ),
    duration="4",
    language="Unknown",
    note=(
        "Four-year duration comes from the current "
        "2026 international prospectus. "
        "Programme-wide MOI remains Unknown."
    ),
)

add(
    "prog_tw_075",
    "International Business",
    "International Business",
    (
        "https://web-en.scu.edu.tw/"
        "ibsu/web_page/1569"
    ),
    "verified_yes",
    SCU_INTL,
    (
        "The Department of International Business "
        "links directly to Soochow's current 2026 "
        "international-student admission prospectus."
    ),
    duration="4",
    language="Unknown",
    note=(
        "Current prospectus supports four-year "
        "Bachelor duration. Language remains "
        "Unknown without whole-programme MOI evidence."
    ),
)


# ============================================================
# uni_tw_026 - Taipei Medical University
# prog_tw_076..078
# ============================================================

TMU_PROGRAMS = (
    "https://oge.tmu.edu.tw/"
    "degree-students/undergraduate/"
)

TMU_INTL = (
    "https://ogeadmission.tmu.edu.tw/"
    "foreign/index/index/applyForeignSn/112"
)


add(
    "prog_tw_076",
    "Pharmacy",
    "Pharmacy",
    TMU_PROGRAMS,
    "verified_yes",
    TMU_INTL,
    (
        "TMU's official Fall 2026 undergraduate "
        "international admission system accepts "
        "international applicants."
    ),
    duration="4",
    language="Chinese",
    note=(
        "TMU official undergraduate programme "
        "information gives Pharmacy a four-year "
        "duration. Fall 2026 admissions explicitly "
        "state all undergraduate programmes are "
        "taught in Chinese."
    ),
)

add(
    "prog_tw_077",
    "Public Health",
    "Public Health",
    "https://ph.tmu.edu.tw/en/",
    "verified_yes",
    TMU_INTL,
    (
        "TMU Fall 2026 international undergraduate "
        "admissions support foreign applicants and "
        "the School of Public Health maintains an "
        "undergraduate programme."
    ),
    duration="4",
    language="Chinese",
    note=(
        "Current TMU undergraduate information "
        "lists Public Health as four years. "
        "Current Fall 2026 admissions state all "
        "undergraduate programmes are Chinese-taught."
    ),
)

add(
    "prog_tw_078",
    (
        "Medical Laboratory Science "
        "and Biotechnology"
    ),
    "Medical Laboratory Science and Biotechnology",
    "http://mts.tmu.edu.tw",
    "verified_yes",
    TMU_INTL,
    (
        "TMU's Fall 2026 international "
        "undergraduate admission route supports "
        "international applicants."
    ),
    duration="4",
    language="Chinese",
    note=(
        "TMU official programme profile identifies "
        "a traditional four-year undergraduate "
        "programme. Current Fall 2026 admission "
        "system states undergraduate programmes "
        "are Chinese-taught."
    ),
)


# ============================================================
# uni_tw_027 - China Medical University
# prog_tw_079..081
# ============================================================

CMU_GUIDE = (
    "https://cmucia.cmu.edu.tw/english/doc/"
    "Application_Guidelines115.pdf"
)

CMU_INTL = (
    "https://cmucia.cmu.edu.tw/english/"
    "admission_international.html"
)


add(
    "prog_tw_079",
    "Pharmacy",
    "Pharmacy",
    CMU_GUIDE,
    "verified_yes",
    CMU_INTL,
    (
        "China Medical University's current "
        "Fall 2026 / Spring 2027 international "
        "student admission guide lists Pharmacy "
        "at Bachelor level."
    ),
    duration="5",
    language="Unknown",
    note=(
        "Current official guide identifies the "
        "five-year B.S. Pharmacy track. "
        "Chinese proficiency requirements are "
        "not automatically treated as programme MOI."
    ),
)

add(
    "prog_tw_080",
    "Physical Therapy",
    "Physical Therapy",
    CMU_GUIDE,
    "verified_yes",
    CMU_INTL,
    (
        "Current CMU international admission "
        "guide lists the Department of Physical "
        "Therapy at Bachelor level."
    ),
    language="Unknown",
    note=(
        "International Bachelor eligibility is "
        "explicitly supported by the current guide. "
        "Unverified optional fields remain blank."
    ),
)

add(
    "prog_tw_081",
    "Nutrition",
    "Nutrition",
    CMU_GUIDE,
    "verified_yes",
    CMU_INTL,
    (
        "Current CMU Fall 2026 / Spring 2027 "
        "international admission guide lists "
        "Nutrition at Bachelor level."
    ),
    language="Unknown",
    note=(
        "No whole-programme MOI or duration is "
        "inferred without explicit evidence."
    ),
)


# ============================================================
# uni_tw_028 - Chang Gung University
# prog_tw_082..084
# ============================================================

CGU_INTL = (
    "https://www.cgu.edu.tw/recruit_intl"
)


add(
    "prog_tw_082",
    (
        "Computer Science and "
        "Information Engineering"
    ),
    "Computer Science",
    (
        "https://recruit-intl.cgu.edu.tw/"
        "courses/course/58"
    ),
    "verified_yes",
    CGU_INTL,
    (
        "CGU's current international application "
        "portal exposes this Bachelor programme "
        "directly to international applicants."
    ),
    duration="4",
    study_mode="Full-time",
    language="Chinese",
    tuition="44537",
    currency="TWD",
    period="Semester",
    note=(
        "Current CGU application page states "
        "Undergraduate, Full-time, 4 years, "
        "Chinese, NT$44,537 per semester."
    ),
)

add(
    "prog_tw_083",
    "Electrical Engineering",
    "Electrical Engineering",
    (
        "https://recruit-intl.cgu.edu.tw/"
        "en_US/courses/course/53-bs-bachelors-"
        "department-electrical-engineering"
    ),
    "verified_yes",
    CGU_INTL,
    (
        "Current CGU international application "
        "portal lists this Bachelor programme "
        "for international students."
    ),
    duration="4",
    study_mode="Full-time",
    language="Chinese",
    tuition="44537",
    currency="TWD",
    period="Semester",
    note=(
        "Official current application record: "
        "4 years, full-time, Chinese, "
        "NT$44,537 per semester."
    ),
)

add(
    "prog_tw_084",
    "Biomedical Engineering",
    "Biomedical Engineering",
    (
        "https://recruit-intl.cgu.edu.tw/"
        "en_US/courses/course/56-bs-bachelors-"
        "department-biomedical-engineering"
    ),
    "verified_yes",
    CGU_INTL,
    (
        "Current CGU application portal exposes "
        "Biomedical Engineering Bachelor admission "
        "to international students."
    ),
    duration="4",
    study_mode="Full-time",
    language="Chinese",
    tuition="44537",
    currency="TWD",
    period="Semester",
    note=(
        "Official current CGU programme page "
        "states full-time, four years, Chinese, "
        "and NT$44,537 per semester."
    ),
)


# ============================================================
# uni_tw_029 - Yuan Ze University
# prog_tw_085..087
# ============================================================

YZU_INTL = (
    "https://gao.yzu.edu.tw/index.php/en/"
    "admission/international-degree-student"
)


add(
    "prog_tw_085",
    (
        "International Bachelor "
        "Program in Informatics"
    ),
    "Computer Science and Informatics",
    (
        "https://yzu-apply.yzu.edu.tw/en_US/"
        "courses/course/74-international-"
        "bachelor-program-informatics"
    ),
    "verified_yes",
    YZU_INTL,
    (
        "YZU's current application system "
        "explicitly offers this Bachelor programme "
        "to International Student applicants."
    ),
    study_mode="Full-time",
    language="English",
    note=(
        "Current official programme application "
        "record states Bachelor, Full-time, "
        "study language English."
    ),
)

add(
    "prog_tw_086",
    (
        "International Program "
        "in Engineering for Bachelor"
    ),
    "Engineering",
    (
        "https://yzu-apply.yzu.edu.tw/en_US/"
        "courses/course/14-international-"
        "program-engineering-bachelor"
    ),
    "verified_yes",
    YZU_INTL,
    (
        "YZU's current international-degree "
        "application system exposes this "
        "Bachelor programme to international "
        "student applicants."
    ),
    study_mode="Full-time",
    language="Chinese / English",
    note=(
        "Official application page states "
        "Bachelor, Full-time, combined "
        "English/Chinese. Compulsory courses "
        "are taught in English."
    ),
)

add(
    "prog_tw_087",
    "Information Communication",
    "Information Communication",
    (
        "https://yzu-apply.yzu.edu.tw/en_US/"
        "courses/course/140-bachelor-"
        "information-communication"
    ),
    "verified_yes",
    YZU_INTL,
    (
        "YZU's current application page explicitly "
        "accepts International Student applicants "
        "for this Bachelor programme."
    ),
    study_mode="Full-time",
    language="Chinese",
    note=(
        "Current official application page states "
        "Bachelor, Full-time and Chinese as "
        "study language."
    ),
)


# ============================================================
# uni_tw_030 - Chung Yuan Christian University
# prog_tw_088..090
# ============================================================

CYCU_GUIDE = (
    "https://oia.cycu.edu.tw/wp-content/uploads/"
    "115%E5%A4%96%E5%9C%8B%E5%AD%B8%E7%94%9F"
    "%E7%A7%8B%E5%AD%A3%E7%8F%AD%E5%85%A5%E5%AD%B8"
    "%E7%94%B3%E8%AB%8B%E7%B0%A1%E7%AB%A0251104"
    "%E6%9B%B4%E6%96%B0.pdf"
)

CYCU_INTL = (
    "https://oia.cycu.edu.tw/"
)


add(
    "prog_tw_088",
    "Business Administration",
    "Business Administration",
    CYCU_GUIDE,
    "verified_yes",
    CYCU_GUIDE,
    (
        "CYCU's current 2026 foreign-student "
        "admission brochure lists Business "
        "Administration among undergraduate "
        "programmes open to foreign students."
    ),
    language="Chinese",
    note=(
        "The current official brochure groups "
        "Business Administration under "
        "Chinese-taught undergraduate programmes."
    ),
)

add(
    "prog_tw_089",
    "International Business",
    "International Business",
    CYCU_GUIDE,
    "verified_yes",
    CYCU_GUIDE,
    (
        "CYCU's 2026 international-student "
        "admission brochure explicitly lists "
        "International Business at "
        "undergraduate level."
    ),
    language="Chinese",
    note=(
        "The programme appears in the current "
        "Chinese-taught undergraduate section."
    ),
)

add(
    "prog_tw_090",
    (
        "International Undergraduate "
        "Program in Business Management"
    ),
    "Business Management",
    CYCU_GUIDE,
    "verified_yes",
    CYCU_GUIDE,
    (
        "CYCU's current foreign-student brochure "
        "explicitly lists this programme in the "
        "English-taught undergraduate section."
    ),
    language="English",
    note=(
        "Current 2026 official brochure explicitly "
        "categorizes this as an English-taught "
        "undergraduate programme."
    ),
)


# ============================================================
# Load queue
# ============================================================

print("=" * 116)
print(
    "STEP 170.4B.3 - TAIWAN OFFICIAL RESEARCH "
    "BATCH 3 (UNIVERSITIES 021-030)"
)
print("=" * 116)


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
        f"Expected 90 Taiwan slots, found {len(rows)}."
    )


expected_batch_ids = {
    f"prog_tw_{i:03d}"
    for i in range(61, 91)
}


if set(RESULTS) != expected_batch_ids:
    raise ValueError(
        "Batch-3 result set must be exactly "
        "prog_tw_061..090."
    )


row_by_id = {
    clean(row["program_id"]): row
    for row in rows
}


# ============================================================
# Parent mapping + precondition
# ============================================================

for number in range(61, 91):

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

    if clean(
        row_by_id[pid]["research_status"]
    ) != "PENDING":
        raise ValueError(
            f"{pid}: expected PENDING before "
            f"Batch 3, found "
            f"{row_by_id[pid]['research_status']}."
        )


# Batch 1 + 2 must remain intact.

for number in range(1, 61):

    pid = f"prog_tw_{number:03d}"

    if clean(
        row_by_id[pid]["research_status"]
    ) != "VERIFIED":
        raise ValueError(
            f"Safety stop: {pid} is no longer VERIFIED."
        )


# ============================================================
# Backup
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
    f"before_batch03_{timestamp}.csv"
)

shutil.copy2(
    QUEUE,
    queue_backup,
)


if EVIDENCE.exists():

    evidence_backup = BACKUP_DIR / (
        "25_taiwan_program_research_"
        "evidence_part03_before_rebuild_"
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
# Apply Batch 3
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
        row.get("program_id")
    )

    if pid not in RESULTS:
        continue

    result = RESULTS[pid]

    for field in UPDATE_FIELDS:
        row[field] = result[field]

    row["last_verified_at"] = TODAY

    row[
        "international_applicants_last_verified_at"
    ] = TODAY


# ============================================================
# Evidence Part 03
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
        if clean(row.get(field))
    ]

    unresolved_fields = [
        field
        for field in DETAIL_FIELDS
        if not clean(row.get(field))
    ]

    evidence_rows.append(
        {
            "program_id": pid,
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
                "; ".join(verified_fields),
            "unresolved_fields":
                "; ".join(unresolved_fields),
            "evidence_note":
                clean(row["research_note"]),
            "verified_at":
                TODAY,
        }
    )


# ============================================================
# Write queue + evidence
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
    writer.writerows(evidence_rows)


# ============================================================
# Batch 3 audit
# ============================================================

batch3 = [
    row
    for row in rows
    if clean(row["program_id"])
    in expected_batch_ids
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

batch3_international = Counter(
    clean(
        row["international_applicants_status"]
    )
    for row in batch3
)


def populated(field):

    return sum(
        bool(clean(row.get(field)))
        for row in batch3
    )


duration_count = populated("duration_years")
mode_count = populated("study_mode")
language_count = populated(
    "language_of_instruction"
)
tuition_count = populated("tuition_fee")
ielts_count = populated("ielts_requirement")
toefl_count = populated("toefl_requirement")
intake_count = populated("intake")
deadline_count = populated(
    "application_deadline"
)


unknown_language_ids = sorted(
    clean(row["program_id"])
    for row in batch3
    if clean(
        row["language_of_instruction"]
    ) == "Unknown"
)


unknown_international_ids = sorted(
    clean(row["program_id"])
    for row in batch3
    if clean(
        row["international_applicants_status"]
    ) == "unknown"
)


verified_yes_blank_urls = sorted(
    clean(row["program_id"])
    for row in batch3
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
    clean(row["program_id"])
    for row in batch3
    if (
        not clean(row["program_name"])
        or not clean(row["field_of_study"])
        or not clean(row["degree_level"])
        or not clean(row["program_url"])
    )
)


# Tuition parity
tuition_parity_errors = []

for row in batch3:

    fee = clean(row["tuition_fee"])
    currency = clean(row["tuition_currency"])
    period = clean(row["tuition_period"])

    if bool(fee) != (
        bool(currency) and bool(period)
    ):
        tuition_parity_errors.append(
            clean(row["program_id"])
        )


# ============================================================
# Transform gate
# ============================================================

valid_university_ids = (
    tp.load_valid_university_ids()
)

transform_pass = []
transform_fail = []


for row_number, row in enumerate(
    batch3,
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
                row["language_of_instruction"]
            ),
        "tuition_fee":
            optional(row["tuition_fee"]),
        "tuition_currency":
            optional(row["tuition_currency"]),
        "tuition_period":
            optional(row["tuition_period"]),
        "minimum_gpa":
            optional(row["minimum_gpa"]),
        "gpa_scale":
            optional(row["gpa_scale"]),
        "ielts_requirement":
            optional(row["ielts_requirement"]),
        "toefl_requirement":
            optional(row["toefl_requirement"]),
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
print("TAIWAN BATCH-3 RESEARCH AUDIT")
print("-" * 116)

print(
    "Batch universities                :",
    10,
)

print(
    "Batch programme slots              :",
    len(batch3),
)

print(
    "Batch VERIFIED programmes         :",
    sum(
        clean(row["research_status"])
        == "VERIFIED"
        for row in batch3
    ),
)

print(
    "Remaining PENDING slots           :",
    sum(
        clean(row["research_status"])
        == "PENDING"
        for row in rows
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

print(
    "Batch-3 international statuses    :",
    dict(batch3_international),
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
    "Tuition parity errors             :",
    len(tuition_parity_errors),
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
    len(missing_identity),
)

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

print()
print("Unknown international IDs:")
print(
    ", ".join(unknown_international_ids)
)

print()
print("Unknown-language IDs:")
print(
    ", ".join(unknown_language_ids)
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


if len(batch3) != 30:
    errors.append(
        "Expected 30 Batch-3 records."
    )


if sum(
    clean(row["research_status"])
    == "VERIFIED"
    for row in batch3
) != 30:
    errors.append(
        "Expected 30 VERIFIED Batch-3 programmes."
    )


if identity_statuses != Counter({
    "VERIFIED": 90,
}):
    errors.append(
        "Expected all 90 programme identities VERIFIED."
    )


if research_statuses != Counter({
    "VERIFIED": 90,
}):
    errors.append(
        "Expected all 90 research rows VERIFIED."
    )


if international_statuses != Counter({
    "verified_yes": 87,
    "unknown": 3,
}):
    errors.append(
        "Unexpected Taiwan international "
        "eligibility totals."
    )


if batch3_international != Counter({
    "verified_yes": 27,
    "unknown": 3,
}):
    errors.append(
        "Unexpected Batch-3 international statuses."
    )


if unknown_international_ids != [
    "prog_tw_067",
    "prog_tw_068",
    "prog_tw_069",
]:
    errors.append(
        "Unexpected international-unknown ID set."
    )


if duration_count != 11:
    errors.append(
        "Expected duration coverage 11/30."
    )


if mode_count != 6:
    errors.append(
        "Expected study mode coverage 6/30."
    )


if language_count != 30:
    errors.append(
        "Expected language value/status 30/30."
    )


if len(unknown_language_ids) != 10:
    errors.append(
        "Expected 10 Unknown-language records."
    )


if tuition_count != 6:
    errors.append(
        "Expected tuition coverage 6/30."
    )


if tuition_parity_errors:
    errors.append(
        "Tuition fee/currency/period parity error."
    )


if ielts_count != 0:
    errors.append(
        "Unexpected IELTS numeric value."
    )


if toefl_count != 0:
    errors.append(
        "Unexpected TOEFL numeric value."
    )


if intake_count != 0:
    errors.append(
        "Current-cycle intake should not "
        "populate canonical future intake."
    )


if deadline_count != 0:
    errors.append(
        "Current-cycle deadline should not "
        "populate canonical future deadline."
    )


if missing_identity:
    errors.append(
        "One or more verified programme "
        "identities are incomplete."
    )


if verified_yes_blank_urls:
    errors.append(
        "verified_yes programme has blank "
        "international application URL."
    )


if len(transform_pass) != 30:
    errors.append(
        "Expected Transform PASS 30."
    )


if transform_fail:
    errors.append(
        "Transformer compatibility failures exist."
    )


print()
print("=" * 116)


if errors:

    print(
        "STEP 170.4B.3 TAIWAN OFFICIAL "
        "RESEARCH BATCH 3: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 170.4B.3 TAIWAN OFFICIAL "
    "RESEARCH BATCH 3 + TRANSFORM GATE: PASS"
)

print(
    "UNIVERSITIES 021-030 COMPLETE"
)

print(
    "30 ADDITIONAL PROGRAMMES VERIFIED"
)

print(
    "TAIWAN PROGRAMME IDENTITY "
    "RESEARCH COMPLETE: 90 / 90"
)

print(
    "INTERNATIONAL ELIGIBILITY: "
    "87 VERIFIED_YES / 3 UNKNOWN"
)

print(
    "NO TAIWAN PROGRAMME SLOT "
    "REMAINS PENDING"
)

print(
    "ALL 30 BATCH-3 PROGRAMMES PASS "
    "THE CURRENT CANONICAL TRANSFORMER"
)

print(
    "programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 116)
