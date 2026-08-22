import csv
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# ============================================================
# Existing canonical transformer
# ============================================================

SCRIPTS_DIR = Path("scripts").resolve()

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS_DIR),
    )

import transform_programs as tp


QUEUE = Path(
    "planning/22_mongolia_program_research_queue.csv"
)

EVIDENCE = Path(
    "planning/23_mongolia_program_research_evidence.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_170_3b"
)

TODAY = datetime.now().date().isoformat()


def clean(value):
    return str(value or "").strip()


def optional(value):

    value = clean(value)

    return None if value == "" else value


# ============================================================
# Result builders
# ============================================================

def verified(
    program_name,
    field_of_study,
    program_url,
    identity_source,
    identity_evidence,
    *,
    duration="",
    study_mode="",
    language="Unknown",
    ielts="",
    toefl="",
    international_status="unknown",
    international_url="",
    international_note="",
    research_note="",
):
    return {
        "program_name": program_name,
        "field_of_study": field_of_study,
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

        "programme_identity_status": "VERIFIED",
        "programme_identity_evidence": (
            identity_evidence
        ),

        "research_status": "VERIFIED",
        "research_note": research_note,

        "international_applicants_status":
            international_status,

        "international_application_url":
            international_url,

        "international_requirements_note":
            international_note,

        "_identity_source": identity_source,
        "_international_source": international_url,
    }


def deferred(note):
    return {
        "program_name": "",
        "field_of_study": "",
        "degree_level": "",

        "duration_years": "",
        "study_mode": "",
        "language_of_instruction": "",

        "tuition_fee": "",
        "tuition_currency": "",
        "tuition_period": "",

        "minimum_gpa": "",
        "gpa_scale": "",
        "ielts_requirement": "",
        "toefl_requirement": "",

        "intake": "",
        "application_deadline": "",
        "program_url": "",

        "programme_identity_status":
            "REVIEWED_UNRESOLVED",

        "programme_identity_evidence":
            note,

        "research_status":
            "DEFERRED",

        "research_note":
            note,

        "international_applicants_status":
            "unknown",

        "international_application_url":
            "",

        "international_requirements_note":
            (
                "Programme identity was not "
                "sufficiently verified for this "
                "Phase-1 slot, so international "
                "eligibility is also unresolved."
            ),

        "_identity_source": "",
        "_international_source": "",
    }


# ============================================================
# Official-source research results
# ============================================================

RESULTS = {

    # --------------------------------------------------------
    # uni_mn_001
    # National University of Mongolia
    #
    # Current foreign-undergraduate portal lists programmes.
    # General NUM undergraduate structure:
    # 4 years, full-time.
    #
    # Language is kept Unknown:
    # Mongolian proficiency is an admission requirement, but
    # this is not force-converted into whole-programme MOI.
    # --------------------------------------------------------

    "prog_mn_001": verified(
        "Business Administration",
        "Business Administration",
        "https://registration.num.edu.mn/Admission/Programs/2",
        "https://registration.num.edu.mn/Admission/Programs/2",
        (
            "Current NUM foreign-undergraduate "
            "admission portal lists Business "
            "administration as an undergraduate "
            "programme."
        ),
        duration="4",
        study_mode="Full-time",
        international_status="verified_yes",
        international_url=(
            "https://registration.num.edu.mn/"
            "Admission/Programs/2"
        ),
        international_note=(
            "NUM undergraduate admission portal "
            "explicitly requires applicants to be "
            "foreign nationals and accepts them "
            "into undergraduate programmes."
        ),
        research_note=(
            "NUM general undergraduate information "
            "states four years of full-time study. "
            "Programme teaching language is not "
            "inferred from the admission language test."
        ),
    ),

    "prog_mn_002": verified(
        "Information Technology",
        "Information Technology",
        "https://registration.num.edu.mn/Admission/Programs/2",
        "https://registration.num.edu.mn/Admission/Programs/2",
        (
            "Current NUM foreign-undergraduate "
            "programme list includes Information "
            "Technology."
        ),
        duration="4",
        study_mode="Full-time",
        international_status="verified_yes",
        international_url=(
            "https://registration.num.edu.mn/"
            "Admission/Programs/2"
        ),
        international_note=(
            "The current NUM undergraduate route "
            "is explicitly for foreign nationals."
        ),
        research_note=(
            "Four-year full-time duration comes "
            "from NUM's general undergraduate "
            "programme information."
        ),
    ),

    "prog_mn_003": verified(
        "Electrical Engineering",
        "Electrical Engineering",
        "https://registration.num.edu.mn/Admission/Programs/2",
        "https://registration.num.edu.mn/Admission/Programs/2",
        (
            "Current NUM foreign-undergraduate "
            "programme list includes Electrical "
            "Engineering."
        ),
        duration="4",
        study_mode="Full-time",
        international_status="verified_yes",
        international_url=(
            "https://registration.num.edu.mn/"
            "Admission/Programs/2"
        ),
        international_note=(
            "Foreign nationals are explicitly "
            "eligible to use NUM's undergraduate "
            "admission route."
        ),
        research_note=(
            "Four-year full-time duration verified "
            "from NUM general undergraduate information."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_002
    # Mongolian University of Science and Technology
    # Current Fall-2026 international programmes.
    # --------------------------------------------------------

    "prog_mn_004": verified(
        "Structural Engineering",
        "Structural Engineering",
        "https://admission.must.edu.mn/programs",
        "https://admission.must.edu.mn/programs",
        (
            "MUST international programme portal "
            "lists Structural Engineering as an "
            "English-delivered Bachelor's programme."
        ),
        duration="4",
        language="English",
        ielts="5.5",
        toefl="60",
        international_status="verified_yes",
        international_url=(
            "https://admission.must.edu.mn/"
        ),
        international_note=(
            "MUST Fall 2026 International Admissions "
            "is open to international applicants. "
            "Minimum English evidence includes "
            "IELTS 5.5 or TOEFL iBT 60."
        ),
        research_note=(
            "Official programme page states "
            "4 years / 8 semesters and English delivery."
        ),
    ),

    "prog_mn_005": verified(
        "Business Administration",
        "Business Administration",
        "https://admission.must.edu.mn/programs",
        "https://admission.must.edu.mn/programs",
        (
            "Current MUST international programme "
            "portal lists Business Administration."
        ),
        duration="4",
        language="English",
        ielts="5.5",
        toefl="60",
        international_status="verified_yes",
        international_url=(
            "https://admission.must.edu.mn/"
        ),
        international_note=(
            "Current MUST international admissions "
            "route explicitly accepts international "
            "applicants; IELTS 5.5 / TOEFL iBT 60 "
            "minimum English scores are published."
        ),
        research_note=(
            "Official programme information states "
            "4 years / 8 semesters and English delivery."
        ),
    ),

    "prog_mn_006": verified(
        "Mechanical Engineering",
        "Mechanical Engineering",
        "https://admission.must.edu.mn/programs",
        "https://admission.must.edu.mn/programs",
        (
            "Current MUST international programme "
            "portal lists Mechanical Engineering."
        ),
        duration="4",
        language="English",
        ielts="5.5",
        toefl="60",
        international_status="verified_yes",
        international_url=(
            "https://admission.must.edu.mn/"
        ),
        international_note=(
            "Current MUST international admission "
            "route and English entry requirements "
            "apply to the selected international "
            "undergraduate programme."
        ),
        research_note=(
            "Official programme information states "
            "4 years / 8 semesters and English delivery."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_003
    # Mongolian National University of Medical Sciences
    # --------------------------------------------------------

    "prog_mn_007": verified(
        "Medicine",
        "Medicine",
        (
            "https://mnums.edu.mn/"
            "%D0%B1%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80/"
        ),
        (
            "https://mnums.edu.mn/"
            "%D0%B1%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80/"
        ),
        (
            "Current MNUMS Bachelor programme table "
            "lists Medicine with a six-year duration."
        ),
        duration="6",
        international_status="verified_yes",
        international_url=(
            "https://news.mnums.edu.mn/?p=10069"
        ),
        international_note=(
            "MNUMS announced 2026 admission for "
            "foreign citizens to undergraduate "
            "programmes with online document submission."
        ),
        research_note=(
            "Whole-programme language is kept Unknown. "
            "No unsupported IELTS/TOEFL minimum is added."
        ),
    ),

    "prog_mn_008": verified(
        "Dentistry",
        "Dentistry",
        (
            "https://mnums.edu.mn/"
            "%D0%B1%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80/"
        ),
        (
            "https://mnums.edu.mn/"
            "%D0%B1%D0%B0%D0%BB%D0%B0%D0%B2%D1%80/"
        ),
        (
            "Current MNUMS Bachelor programme table "
            "lists Dentistry with a six-year duration."
        ),
        duration="6",
        international_status="verified_yes",
        international_url=(
            "https://news.mnums.edu.mn/?p=10069"
        ),
        international_note=(
            "Current 2026 MNUMS notice explicitly "
            "opens undergraduate applications to "
            "foreign citizens."
        ),
        research_note=(
            "Instruction language remains Unknown "
            "without programme-level MOI evidence."
        ),
    ),

    "prog_mn_009": verified(
        "Nursing",
        "Nursing",
        (
            "https://mnums.edu.mn/"
            "%D0%B1%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80/"
        ),
        (
            "https://mnums.edu.mn/"
            "%D0%B1%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80/"
        ),
        (
            "Current MNUMS Bachelor programme table "
            "lists Nursing with a four-year duration."
        ),
        duration="4",
        international_status="verified_yes",
        international_url=(
            "https://news.mnums.edu.mn/?p=10069"
        ),
        international_note=(
            "MNUMS current foreign-undergraduate "
            "admission announcement supports "
            "international applicants."
        ),
        research_note=(
            "Instruction language remains Unknown."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_004
    # Mongolian National University of Education
    # Current programme identities are available.
    # Current direct international-degree admission evidence
    # was not sufficiently verified in this pass.
    # --------------------------------------------------------

    "prog_mn_010": verified(
        "Teacher Education in Mathematics",
        "Education / Mathematics",
        "https://smns.msue.edu.mn/p/r/5648",
        "https://smns.msue.edu.mn/p/r/5648",
        (
            "Current MNUE School of Mathematics and "
            "Natural Sciences page lists the Bachelor "
            "teacher-education programme in Mathematics."
        ),
        international_status="unknown",
        international_note=(
            "A sufficiently explicit current direct "
            "international Bachelor admission route "
            "was not verified in this research pass."
        ),
        research_note=(
            "Credits are published, but duration is "
            "not inferred from credit count."
        ),
    ),

    "prog_mn_011": verified(
        "Teacher Education in Informatics",
        "Education / Information Technology",
        "https://smns.msue.edu.mn/p/r/5648",
        "https://smns.msue.edu.mn/p/r/5648",
        (
            "Current MNUE programme table lists the "
            "Bachelor teacher-education programme "
            "in Informatics."
        ),
        international_status="unknown",
        international_note=(
            "Current programme identity is verified, "
            "but direct foreign-degree admission "
            "eligibility remains unresolved."
        ),
        research_note=(
            "Duration and teaching language remain "
            "unresolved rather than inferred."
        ),
    ),

    "prog_mn_012": verified(
        "Software",
        "Software Engineering",
        "https://smns.msue.edu.mn/p/r/5648",
        "https://smns.msue.edu.mn/p/r/5648",
        (
            "Current MNUE programme table lists "
            "Software as a Bachelor programme."
        ),
        international_status="unknown",
        international_note=(
            "No sufficiently explicit current "
            "international Bachelor admission route "
            "was verified."
        ),
        research_note=(
            "Published credit total is not converted "
            "into an assumed programme duration."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_005
    # University of Finance and Economics
    # --------------------------------------------------------

    "prog_mn_013": verified(
        "Business Management",
        "Business Administration",
        "https://admission.ufe.edu.mn/en/professions/1",
        "https://admission.ufe.edu.mn/en/professions/1",
        (
            "Current UFE English undergraduate/full-time "
            "programme page lists Business management."
        ),
        study_mode="Full-time",
        international_status="unknown",
        international_note=(
            "Current programme evidence is verified, "
            "but a direct current foreign first-year "
            "Bachelor admission route was not verified."
        ),
        research_note=(
            "No programme duration or instruction "
            "language is inferred."
        ),
    ),

    "prog_mn_014": verified(
        "Marketing + AI",
        "Marketing",
        "https://admission.ufe.edu.mn/en/professions/1",
        "https://admission.ufe.edu.mn/en/professions/1",
        (
            "Current UFE undergraduate/full-time "
            "programme page lists Marketing + AI."
        ),
        study_mode="Full-time",
        international_status="unknown",
        international_note=(
            "International degree-admission eligibility "
            "was not sufficiently verified from a "
            "current official source."
        ),
        research_note=(
            "Current full-time status verified; "
            "duration and language remain unresolved."
        ),
    ),

    "prog_mn_015": verified(
        "Finance and Banking",
        "Finance and Banking",
        "https://admission.ufe.edu.mn/en/professions/1",
        "https://admission.ufe.edu.mn/en/professions/1",
        (
            "Current UFE undergraduate/full-time "
            "programme page lists Finance and banking."
        ),
        study_mode="Full-time",
        international_status="unknown",
        international_note=(
            "Current explicit international Bachelor "
            "admission eligibility was not verified."
        ),
        research_note=(
            "Current full-time status verified."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_006
    # Mongolian University of Life Sciences
    # --------------------------------------------------------

    "prog_mn_016": verified(
        "Veterinary Medicine",
        "Veterinary Medicine",
        (
            "https://muls.edu.mn/view_program_new.php?"
            "value_profession=ZW5jb2RldXNlcmlkNjc%3D"
        ),
        (
            "https://muls.edu.mn/view_program_new.php?"
            "value_profession=ZW5jb2RldXNlcmlkNjc%3D"
        ),
        (
            "Current MULS Bachelor programme area "
            "identifies Veterinary Medicine."
        ),
        international_status="unknown",
        international_note=(
            "An international-office contact exists, "
            "but a sufficiently explicit current "
            "foreign-degree admission route for this "
            "programme was not verified."
        ),
        research_note=(
            "Duration, study mode, language and "
            "tuition remain unresolved."
        ),
    ),

    "prog_mn_017": verified(
        "Agricultural Biotechnology",
        "Biotechnology",
        (
            "https://muls.edu.mn/view_program_new.php?"
            "value_profession=ZW5jb2RldXNlcmlkMTc%3D"
        ),
        (
            "https://muls.edu.mn/view_program_new.php?"
            "value_profession=ZW5jb2RldXNlcmlkMTc%3D"
        ),
        (
            "Current MULS Bachelor programme page "
            "lists Agricultural Biotechnology."
        ),
        international_status="unknown",
        international_note=(
            "Direct foreign-degree admission "
            "eligibility remains unresolved."
        ),
        research_note=(
            "English programme name is a normalized "
            "translation of the current official "
            "Mongolian programme title."
        ),
    ),

    "prog_mn_018": verified(
        "Forestry Engineering",
        "Forestry",
        (
            "https://muls.edu.mn/view_program_new.php?"
            "value_profession=ZW5jb2RldXNlcmlkNjc%3D"
        ),
        (
            "https://muls.edu.mn/view_program_new.php?"
            "value_profession=ZW5jb2RldXNlcmlkNjc%3D"
        ),
        (
            "Current MULS Bachelor programme list "
            "includes Forestry Engineering."
        ),
        international_status="unknown",
        international_note=(
            "No sufficiently explicit current "
            "international degree-admission route "
            "was verified."
        ),
        research_note=(
            "Optional details remain blank without "
            "current programme-specific evidence."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_007
    # German-Mongolian Institute for Resources and Technology
    # --------------------------------------------------------

    "prog_mn_019": verified(
        "Raw Materials and Process Engineering",
        "Raw Materials and Process Engineering",
        "https://www.gmit.edu.mn/eng/p/16",
        "https://www.gmit.edu.mn/eng/p/16",
        (
            "Current GMIT programme page confirms "
            "the B.Sc. in Raw Materials and Process "
            "Engineering, regular study period "
            "eight semesters."
        ),
        duration="4",
        ielts="6.0",
        toefl="80",
        international_status="verified_yes",
        international_url=(
            "https://www.gmit.edu.mn/eng/p/13"
        ),
        international_note=(
            "Current GMIT admissions information "
            "explicitly includes international "
            "applicants. Current admission rules "
            "support IELTS 6.0 or TOEFL iBT 80 "
            "as English-test equivalents."
        ),
        research_note=(
            "Eight semesters normalized to 4 years. "
            "Whole-programme teaching language is "
            "not inferred solely from English "
            "admission requirements."
        ),
    ),

    "prog_mn_020": verified(
        "Mechanical Engineering",
        "Mechanical Engineering",
        "https://www.gmit.edu.mn/eng/p/18",
        "https://www.gmit.edu.mn/eng/p/18",
        (
            "Current GMIT Mechanical Engineering "
            "page states a Bachelor programme with "
            "regular study period of eight semesters."
        ),
        duration="4",
        ielts="6.0",
        toefl="80",
        international_status="verified_yes",
        international_url=(
            "https://www.gmit.edu.mn/eng/p/13"
        ),
        international_note=(
            "GMIT current Bachelor admission "
            "information explicitly refers to "
            "international applicants and English "
            "proficiency evidence."
        ),
        research_note=(
            "Eight semesters normalized to 4 years."
        ),
    ),

    "prog_mn_021": verified(
        "Environmental Engineering",
        "Environmental Engineering",
        "https://www.gmit.edu.mn/eng/p/40",
        "https://www.gmit.edu.mn/eng/p/40",
        (
            "Current GMIT Environmental Engineering "
            "page confirms an eight-semester "
            "Bachelor of Science programme."
        ),
        duration="4",
        ielts="6.0",
        toefl="80",
        international_status="verified_yes",
        international_url=(
            "https://www.gmit.edu.mn/eng/p/13"
        ),
        international_note=(
            "Current GMIT admissions source includes "
            "international Bachelor applicants."
        ),
        research_note=(
            "Eight semesters normalized to 4 years."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_008
    # University of the Humanities
    #
    # Official site did not yield sufficiently usable current
    # programme-level evidence in this pass.
    # --------------------------------------------------------

    "prog_mn_022": deferred(
        "No sufficiently usable current official "
        "programme-level source was verified for "
        "Phase-1 slot 1. Deferred rather than fabricated."
    ),

    "prog_mn_023": deferred(
        "No sufficiently usable current official "
        "programme-level source was verified for "
        "Phase-1 slot 2. Deferred rather than fabricated."
    ),

    "prog_mn_024": deferred(
        "No sufficiently usable current official "
        "programme-level source was verified for "
        "Phase-1 slot 3. Deferred rather than fabricated."
    ),


    # --------------------------------------------------------
    # uni_mn_009
    # Otgontenger University
    # --------------------------------------------------------

    "prog_mn_025": verified(
        "Computer Programming",
        "Computer Science / Programming",
        "https://www.otgontenger.edu.mn/en/training/programs",
        "https://www.otgontenger.edu.mn/en/training/programs",
        (
            "Current OTU programme page lists "
            "Computer Programming as a four-year "
            "Bachelor's programme."
        ),
        duration="4",
        international_status="verified_yes",
        international_url=(
            "https://otgontenger.edu.mn/en/about/rules"
        ),
        international_note=(
            "OTU's official procedure explicitly "
            "governs enrollment of foreign citizens "
            "to degree programmes."
        ),
        research_note=(
            "The university-level foreign-student "
            "rule lists onsite/online/hybrid formats, "
            "but no mode is assigned to this individual "
            "programme without programme-level evidence."
        ),
    ),

    "prog_mn_026": verified(
        "Tourism Management",
        "Tourism Management",
        "https://www.otgontenger.edu.mn/en/training/programs",
        "https://www.otgontenger.edu.mn/en/training/programs",
        (
            "Current OTU programme page lists Tourism "
            "Management as a four-year Bachelor's programme."
        ),
        duration="4",
        international_status="verified_yes",
        international_url=(
            "https://otgontenger.edu.mn/en/about/rules"
        ),
        international_note=(
            "Official OTU foreign-citizen regulation "
            "explicitly covers degree-program admission."
        ),
        research_note=(
            "Programme-specific language and study mode "
            "remain unresolved."
        ),
    ),

    "prog_mn_027": verified(
        "International Relations",
        "International Relations",
        "https://www.otgontenger.edu.mn/en/training/programs",
        "https://www.otgontenger.edu.mn/en/training/programs",
        (
            "Current OTU programme page lists "
            "International Relations as a four-year "
            "Bachelor's programme."
        ),
        duration="4",
        international_status="verified_yes",
        international_url=(
            "https://otgontenger.edu.mn/en/about/rules"
        ),
        international_note=(
            "Foreign citizens may apply to OTU "
            "degree programmes under the university's "
            "official international admission procedure."
        ),
        research_note=(
            "No numerical IELTS/TOEFL requirement is "
            "stored because the foreign-citizen rule "
            "only requires programme-appropriate "
            "English evidence where applicable."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_010
    # Etugen University
    # Current 2026/27 admission regulation
    # --------------------------------------------------------

    "prog_mn_028": verified(
        "Medicine - Medical Doctor",
        "Medicine",
        "https://etugen.edu.mn/public/juram2627.pdf",
        "https://etugen.edu.mn/public/juram2627.pdf",
        (
            "Etugen's current 2026/27 Bachelor admission "
            "regulation lists Medicine / Medical Doctor "
            "with six years of daytime study."
        ),
        duration="6",
        international_status="verified_yes",
        international_url=(
            "https://etugen.edu.mn/Home/admission/23"
        ),
        international_note=(
            "Etugen maintains a dedicated foreign-student "
            "Bachelor admission procedure and application "
            "window."
        ),
        research_note=(
            "Official wording is daytime; it is not "
            "force-mapped to canonical Full-time."
        ),
    ),

    "prog_mn_029": verified(
        "Pharmacy",
        "Pharmacy",
        "https://etugen.edu.mn/public/juram2627.pdf",
        "https://etugen.edu.mn/public/juram2627.pdf",
        (
            "Current Etugen 2026/27 admission regulation "
            "lists the Pharmacy Bachelor programme with "
            "five years of daytime study."
        ),
        duration="5",
        international_status="verified_yes",
        international_url=(
            "https://etugen.edu.mn/Home/admission/23"
        ),
        international_note=(
            "Etugen's official foreign-student admission "
            "page explicitly accepts applications to "
            "Bachelor degree programmes."
        ),
        research_note=(
            "Daytime wording is retained only as evidence; "
            "canonical study_mode remains blank."
        ),
    ),

    "prog_mn_030": verified(
        "Nursing",
        "Nursing",
        "https://etugen.edu.mn/public/juram2627.pdf",
        "https://etugen.edu.mn/public/juram2627.pdf",
        (
            "Current Etugen 2026/27 regulation lists "
            "Nursing as a four-year Bachelor programme."
        ),
        duration="4",
        international_status="verified_yes",
        international_url=(
            "https://etugen.edu.mn/Home/admission/23"
        ),
        international_note=(
            "Etugen explicitly provides foreign-student "
            "Bachelor admission procedures."
        ),
        research_note=(
            "Programme instruction language is not "
            "inferred from admissions information."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_011
    # International University of Ulaanbaatar
    # Current programmes verified; direct foreign-degree
    # admission route not sufficiently verified.
    # --------------------------------------------------------

    "prog_mn_031": verified(
        "Software",
        "Software Engineering",
        "https://www.iuu.edu.mn/bachelor/program",
        "https://www.iuu.edu.mn/bachelor/program",
        (
            "Current IUU Bachelor programme page "
            "lists Software, programme code 061302."
        ),
        international_status="unknown",
        international_note=(
            "The university/programme identity is "
            "verified, but a sufficiently explicit "
            "current foreign first-year degree "
            "admission route was not verified."
        ),
        research_note=(
            "University name is not treated as proof "
            "of international-student eligibility."
        ),
    ),

    "prog_mn_032": verified(
        "Business Administration",
        "Business Administration",
        "https://www.iuu.edu.mn/bachelor/program",
        "https://www.iuu.edu.mn/bachelor/program",
        (
            "Current IUU Bachelor programme page lists "
            "Business Administration."
        ),
        international_status="unknown",
        international_note=(
            "Direct current foreign-degree admission "
            "eligibility remains unresolved."
        ),
        research_note=(
            "No duration, mode or language is inferred."
        ),
    ),

    "prog_mn_033": verified(
        "International Relations",
        "International Relations",
        "https://www.iuu.edu.mn/training/department/15",
        "https://www.iuu.edu.mn/training/department/15",
        (
            "Current IUU International Relations "
            "department page confirms the programme."
        ),
        international_status="unknown",
        international_note=(
            "Programme identity is current, but an "
            "explicit foreign Bachelor admission route "
            "was not verified."
        ),
        research_note=(
            "Foreign-language study within the curriculum "
            "is not equivalent to whole-programme "
            "language of instruction."
        ),
    ),


    # --------------------------------------------------------
    # uni_mn_012
    # Mandakh University
    # --------------------------------------------------------

    "prog_mn_034": verified(
        "Information System",
        "Information Systems",
        "https://en.mandakh.edu.mn/information-system",
        "https://en.mandakh.edu.mn/information-system",
        (
            "Current Mandakh programme page identifies "
            "Information system, programme index 061303, "
            "with a four-year duration."
        ),
        duration="4",
        international_status="verified_yes",
        international_url=(
            "https://en.mandakh.edu.mn/"
            "admission-undergraduate-programs"
        ),
        international_note=(
            "Mandakh provides an official Undergraduate "
            "International Admissions section containing "
            "its undergraduate programme menu."
        ),
        research_note=(
            "Official delivery wording is Day classes; "
            "it is not force-mapped to Full-time."
        ),
    ),

    "prog_mn_035": verified(
        "Software",
        "Software Engineering",
        "https://en.mandakh.edu.mn/software",
        "https://en.mandakh.edu.mn/software",
        (
            "Current Mandakh Software programme page "
            "identifies programme index 061302 and "
            "a four-year duration."
        ),
        duration="4",
        international_status="verified_yes",
        international_url=(
            "https://en.mandakh.edu.mn/"
            "admission-undergraduate-programs"
        ),
        international_note=(
            "Mandakh has a dedicated official "
            "Undergraduate International Admissions page."
        ),
        research_note=(
            "Day classes is preserved as evidence but "
            "not force-normalized into study_mode."
        ),
    ),

    "prog_mn_036": verified(
        "Business Administration",
        "Business Administration",
        "https://en.mandakh.edu.mn/business-administration-bachelor",
        "https://en.mandakh.edu.mn/business-administration-bachelor",
        (
            "Current Mandakh Business Administration "
            "page confirms the programme and a "
            "four-year duration."
        ),
        duration="4",
        international_status="verified_yes",
        international_url=(
            "https://en.mandakh.edu.mn/"
            "admission-undergraduate-programs"
        ),
        international_note=(
            "Mandakh's official Undergraduate "
            "International Admissions section supports "
            "international undergraduate applications."
        ),
        research_note=(
            "The regular Business Administration record "
            "is used here; no English-medium claim is "
            "made for this selected record."
        ),
    ),
}


# ============================================================
# Evidence ledger schema
# ============================================================

EVIDENCE_HEADERS = [
    "program_id",
    "university_id",
    "university_name",
    "program_name",
    "research_status",
    "programme_identity_status",
    "identity_source_url",
    "international_applicants_status",
    "international_source_url",
    "verified_fields",
    "unresolved_fields",
    "evidence_note",
    "verified_at",
]


print("=" * 112)
print(
    "STEP 170.3B - MONGOLIA CONSOLIDATED "
    "OFFICIAL PROGRAMME RESEARCH + TRANSFORM GATE"
)
print("=" * 112)


# ============================================================
# Load queue
# ============================================================

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


if len(rows) != 36:

    raise ValueError(
        f"Expected 36 Mongolia research rows, "
        f"found {len(rows)}."
    )


expected_ids = {
    f"prog_mn_{i:03d}"
    for i in range(1, 37)
}


actual_ids = {
    clean(row.get("program_id"))
    for row in rows
}


if actual_ids != expected_ids:

    raise ValueError(
        "Mongolia queue ID set mismatch."
    )


if set(RESULTS) != expected_ids:

    raise ValueError(
        "Research result dictionary must "
        "cover exactly prog_mn_001..036."
    )


# ============================================================
# Backup queue + prior evidence
# ============================================================

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)


queue_backup = BACKUP_DIR / (
    "22_mongolia_program_research_queue_"
    f"before_batch_{timestamp}.csv"
)


shutil.copy2(
    QUEUE,
    queue_backup,
)


if EVIDENCE.exists():

    evidence_backup = BACKUP_DIR / (
        "23_mongolia_program_research_evidence_"
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
# Apply research results
# ============================================================

QUEUE_RESULT_FIELDS = [
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


for row in rows:

    program_id = clean(
        row.get("program_id")
    )

    result = RESULTS[
        program_id
    ]


    for field in QUEUE_RESULT_FIELDS:

        if field not in headers:

            raise ValueError(
                f"Queue missing required field: "
                f"{field}"
            )

        row[field] = result.get(
            field,
            "",
        )


    row["last_verified_at"] = TODAY

    row[
        "international_applicants_last_verified_at"
    ] = TODAY


# ============================================================
# Evidence ledger
# ============================================================

CANONICAL_DETAIL_FIELDS = [
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
]


evidence_rows = []


for row in rows:

    program_id = clean(
        row["program_id"]
    )

    result = RESULTS[
        program_id
    ]


    verified_fields = []

    unresolved_fields = []


    for field in CANONICAL_DETAIL_FIELDS:

        value = clean(
            row.get(field)
        )

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
            "program_id":
                program_id,

            "university_id":
                clean(
                    row["university_id"]
                ),

            "university_name":
                clean(
                    row["university_name"]
                ),

            "program_name":
                clean(
                    row["program_name"]
                ),

            "research_status":
                clean(
                    row["research_status"]
                ),

            "programme_identity_status":
                clean(
                    row[
                        "programme_identity_status"
                    ]
                ),

            "identity_source_url":
                result.get(
                    "_identity_source",
                    "",
                ),

            "international_applicants_status":
                clean(
                    row[
                        "international_applicants_status"
                    ]
                ),

            "international_source_url":
                result.get(
                    "_international_source",
                    "",
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
                    row.get(
                        "research_note"
                    )
                ),

            "verified_at":
                TODAY,
        }
    )


# ============================================================
# Save queue + evidence
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


EVIDENCE.parent.mkdir(
    parents=True,
    exist_ok=True,
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
# Research audit
# ============================================================

verified_rows = [
    row
    for row in rows
    if clean(
        row.get("research_status")
    ) == "VERIFIED"
]


deferred_rows = [
    row
    for row in rows
    if clean(
        row.get("research_status")
    ) == "DEFERRED"
]


identity_statuses = Counter(
    clean(
        row.get(
            "programme_identity_status"
        )
    )
    for row in rows
)


international_statuses_all = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in rows
)


international_statuses_verified = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in verified_rows
)


def populated(field):

    return sum(
        bool(
            clean(
                row.get(field)
            )
        )
        for row in verified_rows
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


unknown_language = [
    clean(row["program_id"])
    for row in verified_rows
    if clean(
        row.get(
            "language_of_instruction"
        )
    ) == "Unknown"
]


verified_yes_blank_urls = [
    clean(row["program_id"])
    for row in rows
    if (
        clean(
            row.get(
                "international_applicants_status"
            )
        ) == "verified_yes"
        and not clean(
            row.get(
                "international_application_url"
            )
        )
    )
]


verified_missing_identity = [
    clean(row["program_id"])
    for row in verified_rows
    if (
        not clean(
            row.get("program_name")
        )
        or not clean(
            row.get("field_of_study")
        )
        or not clean(
            row.get("degree_level")
        )
        or not clean(
            row.get("program_url")
        )
    )
]


# ============================================================
# Transform compatibility precheck
# ============================================================

valid_university_ids = (
    tp.load_valid_university_ids()
)


transform_pass = []

transform_fail = []


for row_number, row in enumerate(
    verified_rows,
    start=2,
):

    raw = {
        "program_id":
            optional(row.get("program_id")),

        "university_id":
            optional(row.get("university_id")),

        "program_name":
            optional(row.get("program_name")),

        "field_of_study":
            optional(row.get("field_of_study")),

        "degree_level":
            optional(row.get("degree_level")),

        "duration_years":
            optional(row.get("duration_years")),

        "study_mode":
            optional(row.get("study_mode")),

        "language_of_instruction":
            optional(
                row.get(
                    "language_of_instruction"
                )
            ),

        "tuition_fee":
            optional(row.get("tuition_fee")),

        "tuition_currency":
            optional(
                row.get(
                    "tuition_currency"
                )
            ),

        "tuition_period":
            optional(
                row.get(
                    "tuition_period"
                )
            ),

        "minimum_gpa":
            optional(row.get("minimum_gpa")),

        "gpa_scale":
            optional(row.get("gpa_scale")),

        "ielts_requirement":
            optional(
                row.get(
                    "ielts_requirement"
                )
            ),

        "toefl_requirement":
            optional(
                row.get(
                    "toefl_requirement"
                )
            ),

        "intake":
            optional(row.get("intake")),

        "application_deadline":
            optional(
                row.get(
                    "application_deadline"
                )
            ),

        "program_url":
            optional(row.get("program_url")),

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
                    row["program_id"]
                ),
                str(exc),
            )
        )


# ============================================================
# Output
# ============================================================

print()
print("MONGOLIA CONSOLIDATED RESEARCH AUDIT")
print("-" * 112)

print(
    "Research slots                    :",
    len(rows),
)

print(
    "Verified programmes               :",
    len(verified_rows),
)

print(
    "Deferred slots                    :",
    len(deferred_rows),
)

print(
    "Identity statuses                 :",
    dict(identity_statuses),
)

print()
print(
    "Duration populated                :",
    duration_count,
    "/ 33",
)

print(
    "Study mode populated              :",
    mode_count,
    "/ 33",
)

print(
    "Language populated                :",
    language_count,
    "/ 33",
)

print(
    "Unknown language                  :",
    len(unknown_language),
    "/ 33",
)

print(
    "Tuition populated                 :",
    tuition_count,
    "/ 33",
)

print(
    "IELTS populated                   :",
    ielts_count,
    "/ 33",
)

print(
    "TOEFL populated                   :",
    toefl_count,
    "/ 33",
)

print(
    "Future intake populated           :",
    intake_count,
    "/ 33",
)

print(
    "Future deadline populated         :",
    deadline_count,
    "/ 33",
)

print()
print(
    "All-slot international statuses   :",
    dict(
        international_statuses_all
    ),
)

print(
    "Verified-program intl statuses    :",
    dict(
        international_statuses_verified
    ),
)

print(
    "verified_yes blank URLs           :",
    len(
        verified_yes_blank_urls
    ),
)

print(
    "Verified rows missing identity    :",
    len(
        verified_missing_identity
    ),
)

print()
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

    for program_id, error in transform_fail:

        print(
            "TRANSFORM FAIL:",
            program_id,
            "->",
            error,
        )


print()
print(
    "Verified programme IDs:"
)

print(
    ", ".join(
        clean(row["program_id"])
        for row in verified_rows
    )
)


print()
print(
    "Deferred IDs:"
)

print(
    ", ".join(
        clean(row["program_id"])
        for row in deferred_rows
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


if len(rows) != 36:
    errors.append(
        "Expected 36 research slots."
    )


if len(verified_rows) != 33:
    errors.append(
        "Expected 33 verified programmes."
    )


if len(deferred_rows) != 3:
    errors.append(
        "Expected exactly 3 deferred slots."
    )


if identity_statuses != Counter({
    "VERIFIED": 33,
    "REVIEWED_UNRESOLVED": 3,
}):
    errors.append(
        "Unexpected identity status counts."
    )


if international_statuses_all != Counter({
    "verified_yes": 21,
    "unknown": 15,
}):
    errors.append(
        "Unexpected all-slot international "
        "status counts."
    )


if international_statuses_verified != Counter({
    "verified_yes": 21,
    "unknown": 12,
}):
    errors.append(
        "Unexpected verified-programme "
        "international status counts."
    )


if verified_yes_blank_urls:
    errors.append(
        "verified_yes programme has blank "
        "international application URL."
    )


if verified_missing_identity:
    errors.append(
        "One or more VERIFIED programmes "
        "have incomplete identity."
    )


if duration_count != 21:
    errors.append(
        "Expected verified duration for 21/33."
    )


if mode_count != 6:
    errors.append(
        "Expected evidence-safe study mode "
        "for 6/33."
    )


if language_count != 33:
    errors.append(
        "Expected language status for 33/33."
    )


if len(unknown_language) != 30:
    errors.append(
        "Expected 30 Unknown-language records."
    )


if tuition_count != 0:
    errors.append(
        "Unexpected tuition values were populated."
    )


if ielts_count != 6:
    errors.append(
        "Expected IELTS values for MUST + GMIT "
        "= 6 programmes."
    )


if toefl_count != 6:
    errors.append(
        "Expected TOEFL values for MUST + GMIT "
        "= 6 programmes."
    )


if intake_count != 0:
    errors.append(
        "Current-cycle intake was incorrectly "
        "promoted into future canonical field."
    )


if deadline_count != 0:
    errors.append(
        "Current-cycle deadline was incorrectly "
        "promoted into future canonical field."
    )


if len(transform_pass) != 33:
    errors.append(
        "Not all 33 verified programmes passed "
        "the canonical transformer."
    )


if transform_fail:
    errors.append(
        "Transformer compatibility failures exist."
    )


print()
print("=" * 112)


if errors:

    print(
        "STEP 170.3B MONGOLIA CONSOLIDATED "
        "RESEARCH: FAIL"
    )

    for error in errors:

        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 170.3B MONGOLIA CONSOLIDATED "
    "RESEARCH + TRANSFORM GATE: PASS"
)

print(
    "33 PROGRAMMES VERIFIED"
)

print(
    "3 UNSUPPORTED UNIVERSITY-OF-HUMANITIES "
    "SLOTS SAFELY DEFERRED"
)

print(
    "INTERNATIONAL ELIGIBILITY: "
    "21 VERIFIED_YES / 15 UNKNOWN ACROSS 36 SLOTS"
)

print(
    "ALL 33 VERIFIED PROGRAMMES PASS "
    "THE CURRENT CANONICAL TRANSFORMER"
)

print(
    "programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 112)
