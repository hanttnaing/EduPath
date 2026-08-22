import csv
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path


QUEUE = Path(
    "planning/20_macau_program_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_170_2b"
)

TODAY = "2026-08-21"


def clean(value):
    return str(value or "").strip()


# ============================================================
# Research results
#
# IMPORTANT:
# - Up to 3 programmes per university is only a ceiling.
# - Unsupported slots are DEFERRED.
# - International eligibility is separate from programme identity.
# ============================================================

RESULTS = {

    # --------------------------------------------------------
    # University of Macau
    # --------------------------------------------------------

    "prog_mo_001": {
        "program_name": "Bachelor of Science in Computer Science",
        "degree_level": "Bachelor",
        "field_of_study": "Computer Science",
        "program_url":
            "https://www.cis.um.edu.mo/bsc_computer_science.html",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official University of Macau Computer and Information "
            "Science programme page confirms the Bachelor of Science "
            "in Computer Science.",
        "language_of_instruction": "English",
        "research_status": "VERIFIED",
        "research_note":
            "Current official programme identity verified. "
            "Optional detail fields not explicitly supported in this "
            "pass remain blank.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://reg.um.edu.mo/admissions/nonlocal/"
            "others-regions/app-adm-rules/",
        "international_requirements_note":
            "UM 2026/2027 international admission page states that "
            "foreign-passport international applicants may apply to "
            "Bachelor programmes through Admission Examination or "
            "Direct Admission.",
    },

    "prog_mo_002": {
        "program_name":
            "Bachelor of Science in Electrical and Computer Engineering",
        "degree_level": "Bachelor",
        "field_of_study": "Electrical and Computer Engineering",
        "program_url":
            "https://www.fst.um.edu.mo/academics/programs/",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official University of Macau Faculty of Science and "
            "Technology programme list confirms this Bachelor programme.",
        "language_of_instruction": "English",
        "research_status": "VERIFIED",
        "research_note":
            "Identity and English medium supported by current official "
            "FST programme information.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://reg.um.edu.mo/admissions/nonlocal/"
            "others-regions/app-adm-rules/",
        "international_requirements_note":
            "UM has a 2026/2027 Bachelor admission route specifically "
            "for international students holding foreign passports.",
    },

    "prog_mo_003": {
        "program_name": "Bachelor of Science in Civil Engineering",
        "degree_level": "Bachelor",
        "field_of_study": "Civil Engineering",
        "program_url":
            "https://www.fst.um.edu.mo/cee/degrees/bachelor/",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official University of Macau Faculty of Science and "
            "Technology Civil Engineering page confirms this programme.",
        "language_of_instruction": "English",
        "research_status": "VERIFIED",
        "research_note":
            "Current official programme identity verified.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://reg.um.edu.mo/admissions/nonlocal/"
            "others-regions/app-adm-rules/",
        "international_requirements_note":
            "UM 2026/2027 international Bachelor admission route "
            "supports foreign-passport applicants.",
    },


    # --------------------------------------------------------
    # Macao Polytechnic University
    # --------------------------------------------------------

    "prog_mo_004": {
        "program_name": "Bachelor of Science in Computing",
        "degree_level": "Bachelor",
        "field_of_study": "Computing",
        "program_url":
            "https://fca.mpu.edu.mo/en/study/bachelor-degree-programmes/"
            "bachelor-of-science-in-computing-applicable-to-20232024-"
            "intake-and-onwards",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official MPU current programme page confirms the programme.",
        "duration_years": "4",
        "language_of_instruction": "English",
        "research_status": "VERIFIED",
        "research_note":
            "Official programme page reports 4 years, English medium "
            "and daytime mode. Daytime is not force-mapped to the final "
            "study_mode enum in this pass.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://mpusite.mpu.edu.mo/admission_overseas/"
            "en/direct_admission.php",
        "international_requirements_note":
            "MPU overseas direct admission explicitly lists Bachelor "
            "of Science in Computing as an applicable programme.",
    },

    "prog_mo_005": {
        "program_name": "Bachelor of Science in Artificial Intelligence",
        "degree_level": "Bachelor",
        "field_of_study": "Artificial Intelligence",
        "program_url":
            "https://fca.mpu.edu.mo/en/study/bachelor-degree-programmes/"
            "bachelor-of-science-in-artificial-intelligence",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official MPU programme page confirms the Bachelor of "
            "Science in Artificial Intelligence.",
        "duration_years": "4",
        "language_of_instruction": "English",
        "research_status": "VERIFIED",
        "research_note":
            "Official page reports four years, English medium and "
            "daytime mode.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://mpusite.mpu.edu.mo/admission_overseas/"
            "en/direct_admission.php",
        "international_requirements_note":
            "MPU overseas admission explicitly includes this programme.",
    },

    "prog_mo_006": {
        "program_name": "Bachelor of Management",
        "degree_level": "Bachelor",
        "field_of_study": "Management",
        "program_url":
            "https://fcg.mpu.edu.mo/en/study/"
            "bachelor-degree-programmes/bachelor-of-management",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official MPU programme page confirms Bachelor of Management.",
        "duration_years": "4",
        "language_of_instruction": "Chinese / English",
        "research_status": "VERIFIED",
        "research_note":
            "Official programme information reports four years and "
            "Chinese/English medium.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://mpusite.mpu.edu.mo/admission_overseas/"
            "en/direct_admission.php",
        "international_requirements_note":
            "MPU overseas direct admission includes Bachelor of "
            "Management among applicable Bachelor programmes.",
    },


    # --------------------------------------------------------
    # Macau University of Science and Technology
    # --------------------------------------------------------

    "prog_mo_007": {
        "program_name": "Bachelor of Business Administration",
        "degree_level": "Bachelor",
        "field_of_study": "Business Administration",
        "program_url":
            "https://msb.must.edu.mo/page/id-3505.html?locale=en_US",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official MUST School of Business programme page confirms "
            "the Bachelor of Business Administration.",
        "duration_years": "4",
        "language_of_instruction": "English",
        "research_status": "VERIFIED",
        "research_note":
            "Official current programme information reports four "
            "academic years and English-medium instruction.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.must.edu.mo/en/academic-affairs-office/"
            "938-admissions/international-student/"
            "6159-international-student-e",
        "international_requirements_note":
            "MUST explicitly lists BBA among undergraduate programmes "
            "open to international students.",
    },

    "prog_mo_008": {
        "program_name": "Bachelor of International Tourism Management",
        "degree_level": "Bachelor",
        "field_of_study": "Tourism and Hospitality Management",
        "program_url":
            "https://fhtm.must.edu.mo/id-1725/program/view/"
            "id-263.html?locale=en_US",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official MUST Faculty of Hospitality and Tourism "
            "Management programme page confirms the programme.",
        "duration_years": "4",
        "language_of_instruction": "English",
        "research_status": "VERIFIED",
        "research_note":
            "Official page reports four-year normal duration, "
            "face-to-face teaching and English teaching language.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.must.edu.mo/en/academic-affairs-office/"
            "938-admissions/international-student/"
            "6159-international-student-e",
        "international_requirements_note":
            "MUST explicitly lists Bachelor of International Tourism "
            "Management for international-student applications.",
    },

    "prog_mo_009": {
        "program_name": "Bachelor of Applied Economics",
        "degree_level": "Bachelor",
        "field_of_study": "Economics",
        "program_url":
            "https://ugadmissions.must.edu.mo/"
            "faculty/id-2878.html?locale=en_US",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official MUST undergraduate programme list confirms "
            "Bachelor of Applied Economics.",
        "duration_years": "4",
        "language_of_instruction": "English",
        "research_status": "VERIFIED",
        "research_note":
            "Current official programme list reports four years "
            "and English medium.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.must.edu.mo/en/academic-affairs-office/"
            "938-admissions/international-student/"
            "6159-international-student-e",
        "international_requirements_note":
            "MUST international-student page explicitly includes "
            "Bachelor of Applied Economics.",
    },


    # --------------------------------------------------------
    # City University of Macau
    # --------------------------------------------------------

    "prog_mo_010": {
        "program_name": "Bachelor of Computer Science",
        "degree_level": "Bachelor",
        "field_of_study": "Computer Science",
        "program_url":
            "https://fds.cityu.edu.mo/en/page-132",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official CityU Faculty of Data Science programme page "
            "confirms Bachelor of Computer Science.",
        "research_status": "VERIFIED",
        "research_note":
            "Programme identity verified; unsupported optional "
            "details remain blank.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.cityu.edu.mo/en/apply-now-bachelors-degree-"
            "programs-2026-2027-macao-hong-kong-taiwan-overseas/",
        "international_requirements_note":
            "CityU 2026/2027 admissions explicitly accepts "
            "international students and lists Computer Science.",
    },

    "prog_mo_011": {
        "program_name": "Bachelor of Business Administration",
        "degree_level": "Bachelor",
        "field_of_study": "Business Administration",
        "program_url":
            "https://www.cityu.edu.mo/en/admissions/"
            "bachelors-degree-programmes/",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official CityU Bachelor programme list confirms "
            "Bachelor of Business Administration.",
        "language_of_instruction": "Chinese",
        "research_status": "VERIFIED",
        "research_note":
            "Official current Bachelor list identifies the main "
            "BBA programme as Chinese-medium.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.cityu.edu.mo/en/apply-now-bachelors-degree-"
            "programs-2026-2027-macao-hong-kong-taiwan-overseas/",
        "international_requirements_note":
            "CityU 2026/2027 international admission offering "
            "includes Business Administration.",
    },

    "prog_mo_012": {
        "program_name":
            "Bachelor of International Tourism and Hotel Management",
        "degree_level": "Bachelor",
        "field_of_study": "Tourism and Hotel Management",
        "program_url":
            "https://www.cityu.edu.mo/en/admissions/"
            "bachelors-degree-programmes/",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official CityU Bachelor programme list confirms "
            "International Tourism and Hotel Management.",
        "language_of_instruction": "English Available",
        "research_status": "VERIFIED",
        "research_note":
            "Official CityU list provides both Chinese and English "
            "versions; English-medium route is available.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.cityu.edu.mo/en/apply-now-bachelors-degree-"
            "programs-2026-2027-macao-hong-kong-taiwan-overseas/",
        "international_requirements_note":
            "CityU explicitly lists this programme for its "
            "2026/2027 international applicant route.",
    },


    # --------------------------------------------------------
    # University of Saint Joseph
    # --------------------------------------------------------

    "prog_mo_013": {
        "program_name": "Bachelor of Business Administration",
        "degree_level": "Bachelor",
        "field_of_study": "Business Administration",
        "program_url":
            "https://www.usj.edu.mo/en/admissions/"
            "undergraduate-admissions/",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "USJ 2026/2027 official undergraduate admissions page "
            "lists Bachelor of Business Administration.",
        "research_status": "VERIFIED",
        "research_note":
            "Current programme identity verified.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.usj.edu.mo/en/international/"
            "international-application/",
        "international_requirements_note":
            "USJ has a dedicated international application process "
            "and its admissions requirements explicitly refer to "
            "international prospective students.",
    },

    "prog_mo_014": {
        "program_name": "Bachelor of Biology and Biotechnology",
        "degree_level": "Bachelor",
        "field_of_study": "Biology and Biotechnology",
        "program_url":
            "https://www.usj.edu.mo/en/admissions/"
            "undergraduate-admissions/",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "USJ official 2026/2027 undergraduate list confirms "
            "Bachelor of Biology and Biotechnology.",
        "research_status": "VERIFIED",
        "research_note":
            "Current official programme identity verified.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.usj.edu.mo/en/international/"
            "international-application/",
        "international_requirements_note":
            "USJ accepts international applicants through its "
            "official international application process.",
    },

    "prog_mo_015": {
        "program_name": "Bachelor of Psychology",
        "degree_level": "Bachelor",
        "field_of_study": "Psychology",
        "program_url":
            "https://www.usj.edu.mo/en/admissions/"
            "undergraduate-admissions/",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "USJ official 2026/2027 undergraduate list confirms "
            "Bachelor of Psychology.",
        "research_status": "VERIFIED",
        "research_note":
            "Current official programme identity verified.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.usj.edu.mo/en/international/"
            "international-application/",
        "international_requirements_note":
            "International applicants may apply through USJ's "
            "official international application procedure.",
    },


    # --------------------------------------------------------
    # Macao University of Tourism
    # --------------------------------------------------------

    "prog_mo_016": {
        "program_name": "Bachelor of Science in Hotel Management",
        "degree_level": "Bachelor",
        "field_of_study": "Hotel Management",
        "program_url":
            "https://www.utm.edu.mo/about-utm/"
            "quality-assurance-policy",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official UTM programme information confirms "
            "Bachelor of Science in Hotel Management.",
        "duration_years": "4",
        "language_of_instruction": "English Available",
        "research_status": "VERIFIED",
        "research_note":
            "UTM official materials show English/Chinese programme "
            "options; 2026/27 undergraduate normal duration is four years.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
            "upload/18/2026-2027%20UG%20admission%20brochure%20"
            "%28ENG%29.pdf",
        "international_requirements_note":
            "UTM 2026/2027 undergraduate brochure explicitly provides "
            "admission and tuition information for students from "
            "other countries or regions and non-local applicants.",
    },

    "prog_mo_017": {
        "program_name":
            "Bachelor of Science in Tourism Business Management",
        "degree_level": "Bachelor",
        "field_of_study": "Tourism Business Management",
        "program_url":
            "https://www.utm.edu.mo/about-utm/"
            "quality-assurance-policy",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official UTM degree programme information confirms "
            "Bachelor of Science in Tourism Business Management.",
        "duration_years": "4",
        "language_of_instruction": "English Available",
        "research_status": "VERIFIED",
        "research_note":
            "Official UTM sources support the programme identity "
            "and English/Chinese provision.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
            "upload/18/2026-2027%20UG%20admission%20brochure%20"
            "%28ENG%29.pdf",
        "international_requirements_note":
            "UTM 2026/2027 admission brochure explicitly covers "
            "non-local applicants and students from other countries.",
    },

    "prog_mo_018": {
        "program_name":
            "Bachelor of Science in Tourism Event Management",
        "degree_level": "Bachelor",
        "field_of_study": "Tourism Event Management",
        "program_url":
            "https://www.utm.edu.mo/about-utm/"
            "quality-assurance-policy",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official UTM programme information confirms Bachelor "
            "of Science in Tourism Event Management.",
        "duration_years": "4",
        "language_of_instruction": "English Available",
        "research_status": "VERIFIED",
        "research_note":
            "Official UTM sources support the programme identity "
            "and English/Chinese provision.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www.utm.edu.mo/admission/filemanager/Flyer/en/"
            "upload/18/2026-2027%20UG%20admission%20brochure%20"
            "%28ENG%29.pdf",
        "international_requirements_note":
            "UTM provides an official 2026/2027 non-local "
            "undergraduate admission route.",
    },


    # --------------------------------------------------------
    # Academy of Public Security Forces of Macao
    #
    # Degree-bearing security courses exist, but the current
    # public source does not establish a general international
    # student admission route appropriate for EduPath.
    # --------------------------------------------------------

    "prog_mo_019": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "Official ESFSM source confirms degree-bearing officer "
            "training in security disciplines, but no sufficiently "
            "current general programme/admission page suitable for "
            "EduPath international-student recommendation was verified.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "General international-student admission eligibility "
            "could not be verified from current official evidence.",
    },

    "prog_mo_020": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "Slot deferred rather than translating or fabricating an "
            "exact current English programme title from older security "
            "training information.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "No current general international admission route verified.",
    },

    "prog_mo_021": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "Unsupported Phase-1 slot deferred.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "International eligibility unresolved.",
    },


    # --------------------------------------------------------
    # Kiang Wu Nursing College of Macau
    # --------------------------------------------------------

    "prog_mo_022": {
        "program_name":
            "Bachelor of Science in Nursing Programme",
        "degree_level": "Bachelor",
        "field_of_study": "Nursing",
        "program_url":
            "https://www2.kwnc.edu.mo/en/standard/"
            "BSN_Programme.html",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official Kiang Wu Nursing College 2026/2027 BSN "
            "admission page confirms the programme.",
        "duration_years": "4",
        "study_mode": "Full-time",
        "language_of_instruction": "Unknown",
        "research_status": "VERIFIED",
        "research_note":
            "Official page explicitly reports 4 years full-time. "
            "Whole-programme medium of instruction was not safely "
            "inferred and remains Unknown.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://www2.kwnc.edu.mo/en/standard/"
            "BSN_Programme.html",
        "international_requirements_note":
            "Official 2026/2027 BSN page contains a dedicated "
            "International Students admission section and requirements.",
    },

    "prog_mo_023": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "A second distinct current undergraduate degree programme "
            "was not sufficiently verified. Slot deferred.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "No separate programme identity exists for this slot.",
    },

    "prog_mo_024": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "A third distinct current undergraduate degree programme "
            "was not sufficiently verified. Slot deferred.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "No separate programme identity exists for this slot.",
    },


    # --------------------------------------------------------
    # Macau Institute of Management
    # --------------------------------------------------------

    "prog_mo_025": {
        "program_name": "Bachelor of Business Administration",
        "degree_level": "Bachelor",
        "field_of_study": "Business Administration",
        "program_url":
            "https://mim.edu.mo/?list_186%2F=",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official MIM degree programme page confirms the "
            "Bachelor of Business Administration.",
        "language_of_instruction": "Chinese",
        "research_status": "VERIFIED",
        "research_note":
            "Programme identity is official. MIM states teaching "
            "language is Chinese with Chinese/English textbooks. "
            "International admission eligibility remains unresolved.",
        "international_applicants_status": "unknown",
        "international_application_url": "",
        "international_requirements_note":
            "A sufficiently explicit current international-student "
            "admission route for this BBA was not verified; do not "
            "infer eligibility from the public programme page.",
    },

    "prog_mo_026": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "Additional programme slot deferred because parent/"
            "awarding-institution and admission applicability were "
            "not sufficiently clear for canonical inclusion.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "International eligibility unresolved.",
    },

    "prog_mo_027": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "Third slot deferred rather than force-mapping diploma "
            "or partner provision into the canonical programme model.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "International eligibility unresolved.",
    },


    # --------------------------------------------------------
    # Macau Millennium College
    # --------------------------------------------------------

    "prog_mo_028": {
        "program_name":
            "Bachelor's Degree Programme in Smart Tourism "
            "and Entertainment Management",
        "degree_level": "Bachelor",
        "field_of_study":
            "Smart Tourism and Entertainment Management",
        "program_url":
            "https://mmc.edu.mo/en/blog/notice_en/15696/",
        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence":
            "Official MMC July 2026 notice confirms government "
            "approval, registration and 2026/2027 implementation "
            "of the renamed Bachelor programme.",
        "study_mode": "",
        "language_of_instruction": "Chinese / English",
        "research_status": "VERIFIED",
        "research_note":
            "Current official source states face-to-face delivery "
            "in Chinese and English. Face-to-face is not force-mapped "
            "to a canonical study_mode value.",
        "international_applicants_status": "verified_yes",
        "international_application_url":
            "https://mmc.edu.mo/en/blog/category/enrollment_en/",
        "international_requirements_note":
            "MMC official enrolment area provides Macao "
            "International/Overseas Enrollment and international "
            "student enrolment information.",
    },

    "prog_mo_029": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "The current Associate Degree in Smart Tourism and "
            "Entertainment Management is not force-mapped to the "
            "existing canonical degree-level enum. Slot deferred.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "Deferred programme slot.",
    },

    "prog_mo_030": {
        "programme_identity_status": "REVIEWED_UNRESOLVED",
        "research_status": "DEFERRED",
        "research_note":
            "No third current programme was added without sufficient "
            "programme-level evidence and schema compatibility.",
        "international_applicants_status": "unknown",
        "international_requirements_note":
            "Deferred programme slot.",
    },
}


print("=" * 105)
print(
    "STEP 170.2B - MACAU PROGRAMME IDENTITY + "
    "INTERNATIONAL ELIGIBILITY BATCH"
)
print("=" * 105)


if not QUEUE.exists():
    raise FileNotFoundError(
        f"Queue not found: {QUEUE}"
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
        f"Expected 30 queue rows, found {len(rows)}."
    )


expected_ids = {
    f"prog_mo_{i:03d}"
    for i in range(1, 31)
}

actual_ids = {
    clean(row["program_id"])
    for row in rows
}


if actual_ids != expected_ids:
    raise ValueError(
        "Macau queue ID set mismatch."
    )


if set(RESULTS) != expected_ids:
    raise ValueError(
        "Research result ID set does not cover exactly "
        "prog_mo_001 through prog_mo_030."
    )


# ------------------------------------------------------------
# Backup before modification
# ------------------------------------------------------------

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup_path = BACKUP_DIR / (
    "20_macau_program_research_queue_before_"
    f"identity_international_{timestamp}.csv"
)

shutil.copy2(
    QUEUE,
    backup_path,
)


# ------------------------------------------------------------
# Apply results
# ------------------------------------------------------------

for row in rows:

    program_id = clean(
        row["program_id"]
    )

    result = RESULTS[
        program_id
    ]

    for field, value in result.items():

        if field not in headers:
            raise ValueError(
                f"Queue missing field {field!r}."
            )

        row[field] = value

    row["last_verified_at"] = TODAY

    if (
        "international_applicants_last_verified_at"
        in headers
    ):
        row[
            "international_applicants_last_verified_at"
        ] = TODAY


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


# ------------------------------------------------------------
# Audit
# ------------------------------------------------------------

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


verified_rows = [
    row
    for row in rows
    if clean(
        row["research_status"]
    ) == "VERIFIED"
]


deferred_rows = [
    row
    for row in rows
    if clean(
        row["research_status"]
    ) == "DEFERRED"
]


verified_missing_identity = [
    row["program_id"]
    for row in verified_rows
    if not clean(row["program_name"])
    or not clean(row["degree_level"])
    or not clean(row["field_of_study"])
    or not clean(row["program_url"])
]


verified_yes_blank_url = [
    row["program_id"]
    for row in rows
    if clean(
        row["international_applicants_status"]
    ) == "verified_yes"
    and not clean(
        row["international_application_url"]
    )
]


print(
    "Queue rows                       :",
    len(rows),
)

print(
    "Identity statuses                :",
    dict(identity_statuses),
)

print(
    "Research statuses                :",
    dict(research_statuses),
)

print(
    "International statuses           :",
    dict(international_statuses),
)

print(
    "Verified programme rows          :",
    len(verified_rows),
)

print(
    "Deferred research slots          :",
    len(deferred_rows),
)

print(
    "Verified rows missing identity   :",
    len(verified_missing_identity),
)

print(
    "verified_yes with blank URL      :",
    len(verified_yes_blank_url),
)

print()
print(
    "Verified programme IDs:"
)

print(
    ", ".join(
        row["program_id"]
        for row in verified_rows
    )
)

print()
print(
    "Deferred IDs:"
)

print(
    ", ".join(
        row["program_id"]
        for row in deferred_rows
    )
)

print()
print(
    "Backup:",
    backup_path,
)

print(
    "Updated queue:",
    QUEUE,
)


errors = []


if identity_statuses != Counter({
    "VERIFIED": 21,
    "REVIEWED_UNRESOLVED": 9,
}):
    errors.append(
        "Expected 21 VERIFIED and "
        "9 REVIEWED_UNRESOLVED identity rows."
    )


if research_statuses != Counter({
    "VERIFIED": 21,
    "DEFERRED": 9,
}):
    errors.append(
        "Expected 21 verified programmes "
        "and 9 deferred slots."
    )


if international_statuses != Counter({
    "verified_yes": 20,
    "unknown": 10,
}):
    errors.append(
        "Expected international statuses "
        "20 verified_yes / 10 unknown."
    )


if verified_missing_identity:
    errors.append(
        "Verified programme rows have missing "
        "identity fields."
    )


if verified_yes_blank_url:
    errors.append(
        "verified_yes records have blank "
        "international application URLs."
    )


print()
print("=" * 105)


if errors:

    print(
        "STEP 170.2B MACAU IDENTITY + "
        "INTERNATIONAL BATCH: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 170.2B MACAU IDENTITY + "
    "INTERNATIONAL BATCH: PASS"
)

print(
    "21 PROGRAMMES VERIFIED"
)

print(
    "9 UNSUPPORTED SLOTS SAFELY DEFERRED"
)

print(
    "20 PROGRAMMES HAVE VERIFIED "
    "INTERNATIONAL-STUDENT ELIGIBILITY"
)

print(
    "NO PROGRAMS.JSON OR MONGODB "
    "RECORDS WERE MODIFIED"
)

print("=" * 105)
