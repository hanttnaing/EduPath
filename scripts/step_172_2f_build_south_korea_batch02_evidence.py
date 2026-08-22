from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path.cwd()
PLANNING = ROOT / "planning"

WORKING_SOURCE = (
    PLANNING
    / "30_south_korea_program_research_queue_batch01_applied.csv"
)

BATCH02_LOCK = (
    PLANNING
    / "31_south_korea_program_research_batch02_lock.csv"
)

EVIDENCE = (
    PLANNING
    / "32_south_korea_program_research_batch02_evidence.csv"
)

TEMP = (
    PLANNING
    / "32_south_korea_program_research_batch02_evidence.tmp.csv"
)

CANONICAL = (
    ROOT
    / "data"
    / "cleaned"
    / "programs.json"
)


EXPECTED_WORKING_SOURCE_SHA = (
    "0c23f17369fd1f774838736b0e21fe617"
    "bd1ef804b0bc98f05c723158435075a"
)

EXPECTED_BATCH02_LOCK_SHA = (
    "aaea6d2f161713b125cff7ca82870b91"
    "fa29e96be5638626b2c9f4fa654a511d"
)


EXPECTED_COLUMNS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
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
    "official_university_website",
    "research_status",
    "research_note",
    "last_verified_at",
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


EXPECTED_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(37, 73)
]

EXPECTED_PARENT_IDS = {
    f"uni_kr_{i:03d}"
    for i in range(13, 25)
}

VERIFIED_DATE = "2026-08-22"


# =====================================================================
# OFFICIAL-SOURCE RESEARCH RESULT
# =====================================================================

RESEARCH = {

    # -----------------------------------------------------------------
    # uni_kr_013 - Ulsan National Institute of Science and Technology
    # -----------------------------------------------------------------

    "prog_kr_037": {
        "program_name": "Computer Science and Engineering",
        "field_of_study": "Computer Science",
        "program_url":
            "https://www.unist.ac.kr/unist/education/departments.do?lang=en",
        "official_university_website":
            "https://www.unist.ac.kr/",
        "international_application_url":
            "https://admu-intl.unist.ac.kr/admission-eng/index.do",
        "international_note":
            "UNIST operates an official international undergraduate admissions pathway and the department is listed on the official UNIST academic department page.",
    },

    "prog_kr_038": {
        "program_name": "Electrical Engineering",
        "field_of_study": "Electrical Engineering",
        "program_url":
            "https://www.unist.ac.kr/unist/education/departments.do?lang=en",
        "official_university_website":
            "https://www.unist.ac.kr/",
        "international_application_url":
            "https://admu-intl.unist.ac.kr/admission-eng/index.do",
        "international_note":
            "UNIST operates an official international undergraduate admissions pathway and the department is listed on the official UNIST academic department page.",
    },

    "prog_kr_039": {
        "program_name": "Mechanical Engineering",
        "field_of_study": "Mechanical Engineering",
        "program_url":
            "https://www.unist.ac.kr/unist/education/departments.do?lang=en",
        "official_university_website":
            "https://www.unist.ac.kr/",
        "international_application_url":
            "https://admu-intl.unist.ac.kr/admission-eng/index.do",
        "international_note":
            "UNIST operates an official international undergraduate admissions pathway and the department is listed on the official UNIST academic department page.",
    },


    # -----------------------------------------------------------------
    # uni_kr_014 - Gwangju Institute of Science and Technology
    # -----------------------------------------------------------------

    "prog_kr_040": {
        "program_name": "Electrical Engineering and Computer Science",
        "field_of_study": "Electrical Engineering and Computer Science",
        "program_url":
            "https://ewww.gist.ac.kr/iuadm/img/main/2026_Fall_Undergraduate_Admission_Guideline.pdf",
        "official_university_website":
            "https://www.gist.ac.kr/en/",
        "international_application_url":
            "https://ewww.gist.ac.kr/iuadm/img/main/2026_Fall_Undergraduate_Admission_Guideline.pdf",
        "international_note":
            "The official GIST 2026 Fall Undergraduate Admission Guideline for international applicants lists Electrical Engineering and Computer Science as an available undergraduate programme.",
    },

    "prog_kr_041": {
        "program_name": "Materials Science and Engineering",
        "field_of_study": "Materials Science and Engineering",
        "program_url":
            "https://ewww.gist.ac.kr/iuadm/img/main/2026_Fall_Undergraduate_Admission_Guideline.pdf",
        "official_university_website":
            "https://www.gist.ac.kr/en/",
        "international_application_url":
            "https://ewww.gist.ac.kr/iuadm/img/main/2026_Fall_Undergraduate_Admission_Guideline.pdf",
        "international_note":
            "The official GIST 2026 Fall Undergraduate Admission Guideline for international applicants lists Materials Science and Engineering as an available undergraduate programme.",
    },

    "prog_kr_042": {
        "program_name": "Mechanical and Robotics Engineering",
        "field_of_study": "Mechanical and Robotics Engineering",
        "program_url":
            "https://ewww.gist.ac.kr/iuadm/img/main/2026_Fall_Undergraduate_Admission_Guideline.pdf",
        "official_university_website":
            "https://www.gist.ac.kr/en/",
        "international_application_url":
            "https://ewww.gist.ac.kr/iuadm/img/main/2026_Fall_Undergraduate_Admission_Guideline.pdf",
        "international_note":
            "The official GIST 2026 Fall Undergraduate Admission Guideline for international applicants lists Mechanical and Robotics Engineering as an available undergraduate programme.",
    },


    # -----------------------------------------------------------------
    # uni_kr_015 - Ajou University
    # -----------------------------------------------------------------

    "prog_kr_043": {
        "program_name": "Department of Software and Computer Engineering",
        "field_of_study": "Software and Computer Engineering",
        "program_url":
            "https://www.ajou.ac.kr/en/admission/college-of-computing-and-informatics.do",
        "official_university_website":
            "https://www.ajou.ac.kr/en/",
        "international_application_url":
            "https://www.ajou.ac.kr/iadmissions_en/undergraduate/guideline.do",
        "international_note":
            "Ajou University's official undergraduate academic page lists the department and its official International Admissions site publishes international undergraduate admission guidance.",
    },

    "prog_kr_044": {
        "program_name": "Department of Electrical and Computer Engineering",
        "field_of_study": "Electrical and Computer Engineering",
        "program_url":
            "https://www.ajou.ac.kr/en/admission/college-of-information-technology.do",
        "official_university_website":
            "https://www.ajou.ac.kr/en/",
        "international_application_url":
            "https://www.ajou.ac.kr/iadmissions_en/undergraduate/guideline.do",
        "international_note":
            "Ajou University's official undergraduate academic page lists the department and its official International Admissions site publishes international undergraduate admission guidance.",
    },

    "prog_kr_045": {
        "program_name": "Department of Business Administration",
        "field_of_study": "Business Administration",
        "program_url":
            "https://www.ajou.ac.kr/en/admission/school-of-business.do",
        "official_university_website":
            "https://www.ajou.ac.kr/en/",
        "international_application_url":
            "https://www.ajou.ac.kr/iadmissions_en/undergraduate/guideline.do",
        "international_note":
            "Ajou University's official undergraduate School of Business page lists Business Administration and its official International Admissions site publishes international undergraduate admission guidance.",
    },


    # -----------------------------------------------------------------
    # uni_kr_016 - Chung-Ang University
    # -----------------------------------------------------------------

    "prog_kr_046": {
        "program_name": "School of Computer Engineering",
        "field_of_study": "Computer Engineering",
        "program_url":
            "https://neweng.cau.ac.kr/cms/FR_CON/index.do?MENU_ID=990",
        "official_university_website":
            "https://neweng.cau.ac.kr/",
        "international_application_url":
            "https://oia.cau.ac.kr/cauoie/under/notice.do?article.offset=0&mode=list",
        "international_note":
            "Chung-Ang University's official undergraduate College of Software page lists the School of Computer Engineering and its Office of International Affairs publishes international undergraduate admission notices.",
    },

    "prog_kr_047": {
        "program_name": "School of Business Administration",
        "field_of_study": "Business Administration",
        "program_url":
            "https://neweng.cau.ac.kr/cms/FR_CON/index.do?MENU_ID=780",
        "official_university_website":
            "https://neweng.cau.ac.kr/",
        "international_application_url":
            "https://oia.cau.ac.kr/cauoie/under/notice.do?article.offset=0&mode=list",
        "international_note":
            "Chung-Ang University's official College of Business and Economics page lists the School of Business Administration and its Office of International Affairs publishes international undergraduate admission notices.",
    },

    "prog_kr_048": {
        "program_name": "School of Economics",
        "field_of_study": "Economics",
        "program_url":
            "https://neweng.cau.ac.kr/cms/FR_CON/index.do?MENU_ID=780",
        "official_university_website":
            "https://neweng.cau.ac.kr/",
        "international_application_url":
            "https://oia.cau.ac.kr/cauoie/under/notice.do?article.offset=0&mode=list",
        "international_note":
            "Chung-Ang University's official College of Business and Economics page lists the School of Economics and its Office of International Affairs publishes international undergraduate admission notices.",
    },


    # -----------------------------------------------------------------
    # uni_kr_017 - Chungnam National University
    # -----------------------------------------------------------------

    "prog_kr_049": {
        "program_name": "Computer Science & Engineering",
        "field_of_study": "Computer Science and Engineering",
        "program_url":
            "https://plus.cnu.ac.kr/html/kr/brochure/brochure_ebook_en/files/assets/basic-html/page-25.html",
        "official_university_website":
            "https://plus.cnu.ac.kr/html/en/",
        "international_application_url":
            "https://plus.cnu.ac.kr/html/en/sub03/sub03_0303.html",
        "international_note":
            "Chungnam National University's official academic material lists Computer Science & Engineering and the university publishes an undergraduate admission route for international students.",
    },

    "prog_kr_050": {
        "program_name": "School of Mechanical Engineering",
        "field_of_study": "Mechanical Engineering",
        "program_url":
            "https://plus.cnu.ac.kr/html/kr/brochure/brochure_ebook_en/files/assets/basic-html/page-25.html",
        "official_university_website":
            "https://plus.cnu.ac.kr/html/en/",
        "international_application_url":
            "https://plus.cnu.ac.kr/html/en/sub03/sub03_0303.html",
        "international_note":
            "Chungnam National University's official academic material lists the School of Mechanical Engineering and the university publishes an undergraduate admission route for international students.",
    },

    "prog_kr_051": {
        "program_name": "Department of Economics",
        "field_of_study": "Economics",
        "program_url":
            "https://plus.cnu.ac.kr/html/en/sub02/sub02_020104.html",
        "official_university_website":
            "https://plus.cnu.ac.kr/html/en/",
        "international_application_url":
            "https://plus.cnu.ac.kr/html/en/sub03/sub03_0303.html",
        "international_note":
            "Chungnam National University's official College of Economics and Management page lists the Department of Economics and the university publishes an undergraduate admission route for international students.",
    },


    # -----------------------------------------------------------------
    # uni_kr_018 - Chungbuk National University
    # -----------------------------------------------------------------

    "prog_kr_052": {
        "program_name": "Department of Computer Engineering",
        "field_of_study": "Computer Engineering",
        "program_url":
            "https://icc.chungbuk.ac.kr/english/contents.do?key=755",
        "official_university_website":
            "https://www.chungbuk.ac.kr/english/",
        "international_application_url":
            "https://www.chungbuk.ac.kr/english/selectBbsNttList.do?bbsNo=42&key=799",
        "international_note":
            "Chungbuk National University's official College of Electrical & Computer Engineering page lists the Department of Computer Engineering and its international bulletin publishes undergraduate international admissions.",
    },

    "prog_kr_053": {
        "program_name": "School of Mechanical Engineering",
        "field_of_study": "Mechanical Engineering",
        "program_url":
            "https://www.chungbuk.ac.kr/english/contents.do?key=754",
        "official_university_website":
            "https://www.chungbuk.ac.kr/english/",
        "international_application_url":
            "https://www.chungbuk.ac.kr/english/selectBbsNttList.do?bbsNo=42&key=799",
        "international_note":
            "Chungbuk National University's official College of Engineering page lists the School of Mechanical Engineering and its international bulletin publishes undergraduate international admissions.",
    },

    "prog_kr_054": {
        "program_name": "School of Business",
        "field_of_study": "Business",
        "program_url":
            "https://www.chungbuk.ac.kr/english/contents.do?key=753",
        "official_university_website":
            "https://www.chungbuk.ac.kr/english/",
        "international_application_url":
            "https://www.chungbuk.ac.kr/english/selectBbsNttList.do?bbsNo=42&key=799",
        "international_note":
            "Chungbuk National University's official College of Business page lists the School of Business and its international bulletin publishes undergraduate international admissions.",
    },


    # -----------------------------------------------------------------
    # uni_kr_019 - Chonnam National University
    # -----------------------------------------------------------------

    "prog_kr_055": {
        "program_name": "School of Mechanical Engineering",
        "field_of_study": "Mechanical Engineering",
        "program_url":
            "https://global.jnu.ac.kr/Academics/Undergraduate/Uni_10",
        "official_university_website":
            "https://global.jnu.ac.kr/",
        "international_application_url":
            "https://international.jnu.ac.kr/Data/tmpfiles/download/2025/240906-ad-en.pdf",
        "international_note":
            "Chonnam National University's official undergraduate academic page verifies the School of Mechanical Engineering and its Office of International Affairs publishes undergraduate admission guidance for international students.",
    },

    "prog_kr_056": {
        "program_name": "Major of Business Administration",
        "field_of_study": "Business Administration",
        "program_url":
            "https://biz.jnu.ac.kr/biz_eng/18545/subview.do",
        "official_university_website":
            "https://global.jnu.ac.kr/",
        "international_application_url":
            "https://international.jnu.ac.kr/Data/tmpfiles/download/2025/240906-ad-en.pdf",
        "international_note":
            "Chonnam National University's official School of Business Administration site verifies the undergraduate Business Administration major and its Office of International Affairs publishes undergraduate admission guidance for international students.",
    },

    "prog_kr_057": {
        "program_name": "Major of Accounting",
        "field_of_study": "Accounting",
        "program_url":
            "https://biz.jnu.ac.kr/biz_eng/18546/subview.do",
        "official_university_website":
            "https://global.jnu.ac.kr/",
        "international_application_url":
            "https://international.jnu.ac.kr/Data/tmpfiles/download/2025/240906-ad-en.pdf",
        "international_note":
            "Chonnam National University's official School of Business Administration site verifies the undergraduate Accounting major and its Office of International Affairs publishes undergraduate admission guidance for international students.",
    },


    # -----------------------------------------------------------------
    # uni_kr_020 - Jeonbuk National University
    # -----------------------------------------------------------------

    "prog_kr_058": {
        "program_name": "Department of Computer Science & Artificial Intelligence",
        "field_of_study": "Computer Science and Artificial Intelligence",
        "program_url":
            "https://jbnu.ac.kr/en/academics/programs/university.do",
        "official_university_website":
            "https://www.jbnu.ac.kr/en/",
        "international_application_url":
            "https://ioffice.jbnu.ac.kr/bbs/ioffice/5310/327999/download.do",
        "international_note":
            "Jeonbuk National University's official undergraduate programme listing includes Computer Science & Artificial Intelligence and the university publishes official international undergraduate admission guidelines.",
    },

    "prog_kr_059": {
        "program_name": "Department of Mechanical Engineering",
        "field_of_study": "Mechanical Engineering",
        "program_url":
            "https://top.jbnu.ac.kr/sites/meeng/index.do",
        "official_university_website":
            "https://www.jbnu.ac.kr/en/",
        "international_application_url":
            "https://ioffice.jbnu.ac.kr/bbs/ioffice/5310/327999/download.do",
        "international_note":
            "Jeonbuk National University's official Department of Mechanical Engineering site verifies the programme and the university publishes official international undergraduate admission guidelines.",
    },

    "prog_kr_060": {
        "program_name": "Department of Business Administration",
        "field_of_study": "Business Administration",
        "program_url":
            "https://top.jbnu.ac.kr/businesseng/index.do",
        "official_university_website":
            "https://www.jbnu.ac.kr/en/",
        "international_application_url":
            "https://ioffice.jbnu.ac.kr/bbs/ioffice/5310/327999/download.do",
        "international_note":
            "Jeonbuk National University's official Department of Business Administration site verifies the programme and the university publishes official international undergraduate admission guidelines.",
    },


    # -----------------------------------------------------------------
    # uni_kr_021 - Gyeongsang National University
    # -----------------------------------------------------------------

    "prog_kr_061": {
        "program_name": "School of Computer Sciences",
        "field_of_study": "Computer Science",
        "program_url":
            "https://www.gnu.ac.kr/eng/cm/cntnts/cntntsView.do?cntntsId=7943&mi=17391",
        "official_university_website":
            "https://www.gnu.ac.kr/eng/",
        "international_application_url":
            "https://international.gnu.ac.kr/international/cm/cntnts/cntntsView.do?cntntsId=4367&mi=8327",
        "international_note":
            "Gyeongsang National University's official College of IT Engineering page lists the School of Computer Sciences and the Office of International Affairs publishes international undergraduate admission guidance.",
    },

    "prog_kr_062": {
        "program_name": "School of Mechanical Engineering",
        "field_of_study": "Mechanical Engineering",
        "program_url":
            "https://www.gnu.ac.kr/eng/cm/cntnts/cntntsView.do?cntntsId=4501&mi=8531",
        "official_university_website":
            "https://www.gnu.ac.kr/eng/",
        "international_application_url":
            "https://international.gnu.ac.kr/international/cm/cntnts/cntntsView.do?cntntsId=4367&mi=8327",
        "international_note":
            "Gyeongsang National University's official College of Engineering page lists the School of Mechanical Engineering and the Office of International Affairs publishes international undergraduate admission guidance.",
    },

    "prog_kr_063": {
        "program_name": "School of Economics",
        "field_of_study": "Economics",
        "program_url":
            "https://www.gnu.ac.kr/eng/cm/cntnts/cntntsView.do?cntntsId=4498&mi=8528",
        "official_university_website":
            "https://www.gnu.ac.kr/eng/",
        "international_application_url":
            "https://international.gnu.ac.kr/international/cm/cntnts/cntntsView.do?cntntsId=4367&mi=8327",
        "international_note":
            "Gyeongsang National University's official College of Social Sciences page lists the School of Economics and the Office of International Affairs publishes international undergraduate admission guidance.",
    },


    # -----------------------------------------------------------------
    # uni_kr_022 - Kangwon National University
    # -----------------------------------------------------------------

    "prog_kr_064": {
        "program_name": "Department of Computer Science",
        "field_of_study": "Computer Science",
        "program_url":
            "https://admission.kangwon.ac.kr/english/sub.do?key=1336",
        "official_university_website":
            "https://kangwon.ac.kr/english/",
        "international_application_url":
            "https://kangwon.ac.kr/english/selectBbsNttView.do?bbsNo=276&key=1944&nttNo=182390&pageIndex=1&pageUnit=10",
        "international_note":
            "Kangwon National University's official undergraduate departments page verifies Computer Science and the university publishes international undergraduate application guidance.",
    },

    "prog_kr_065": {
        "program_name": "Department of Business Administration",
        "field_of_study": "Business Administration",
        "program_url":
            "https://admission.kangwon.ac.kr/english/contents.do?key=1294",
        "official_university_website":
            "https://kangwon.ac.kr/english/",
        "international_application_url":
            "https://kangwon.ac.kr/english/selectBbsNttView.do?bbsNo=276&key=1944&nttNo=182390&pageIndex=1&pageUnit=10",
        "international_note":
            "Kangwon National University's official undergraduate departments page verifies Business Administration and the university publishes international undergraduate application guidance.",
    },

    "prog_kr_066": {
        "program_name": "Department of Electrical & Electronics Engineering",
        "field_of_study": "Electrical and Electronics Engineering",
        "program_url":
            "https://admission.kangwon.ac.kr/english/sub.do?key=1336",
        "official_university_website":
            "https://kangwon.ac.kr/english/",
        "international_application_url":
            "https://kangwon.ac.kr/english/selectBbsNttView.do?bbsNo=276&key=1944&nttNo=182390&pageIndex=1&pageUnit=10",
        "international_note":
            "Kangwon National University's official undergraduate departments page verifies Electrical & Electronics Engineering and the university publishes international undergraduate application guidance.",
    },


    # -----------------------------------------------------------------
    # uni_kr_023 - Incheon National University
    # -----------------------------------------------------------------

    "prog_kr_067": {
        "program_name": "Department of Computer Science and Engineering",
        "field_of_study": "Computer Science and Engineering",
        "program_url":
            "https://www.inu.ac.kr/isis_eng/10091/subview.do",
        "official_university_website":
            "https://www.inu.ac.kr/inuengl/",
        "international_application_url":
            "https://global.inu.ac.kr/bbs/global/3153/367835/download",
        "international_note":
            "Incheon National University's official Computer Science and Engineering site verifies the programme and the university publishes an undergraduate admission guide for international students.",
    },

    "prog_kr_068": {
        "program_name": "Department of Business Administration",
        "field_of_study": "Business Administration",
        "program_url":
            "https://staff.inu.ac.kr/inuengl/13883/subview",
        "official_university_website":
            "https://www.inu.ac.kr/inuengl/",
        "international_application_url":
            "https://global.inu.ac.kr/bbs/global/3153/367835/download",
        "international_note":
            "Incheon National University's official College of Business Administration page verifies the bachelor's programme and the university publishes an undergraduate admission guide for international students.",
    },

    "prog_kr_069": {
        "program_name": "Department of Economics",
        "field_of_study": "Economics",
        "program_url":
            "https://www.inu.ac.kr/inuengl/13864/subview",
        "official_university_website":
            "https://www.inu.ac.kr/inuengl/",
        "international_application_url":
            "https://global.inu.ac.kr/bbs/global/3153/367835/download",
        "international_note":
            "Incheon National University's official College of Commerce and Public Affairs page verifies Economics as a bachelor's programme and the university publishes an undergraduate admission guide for international students.",
    },


    # -----------------------------------------------------------------
    # uni_kr_024 - Jeju National University
    # -----------------------------------------------------------------

    "prog_kr_070": {
        "program_name": "Computer Engineering",
        "field_of_study": "Computer Engineering",
        "program_url":
            "https://jejunu.ac.kr/eng/university/colleges/engine/computer/introduction.htm",
        "official_university_website":
            "https://www.jejunu.ac.kr/eng/",
        "international_application_url":
            "https://jejunu.ac.kr/cs/download.htm?act=download&no=3&seq=249845",
        "international_note":
            "Jeju National University's official College of Engineering page verifies Computer Engineering and the university publishes a 2026 undergraduate admission guide for international students.",
    },

    "prog_kr_071": {
        "program_name": "Business Administration",
        "field_of_study": "Business Administration",
        "program_url":
            "https://www.jejunu.ac.kr/eng/university/colleges/economic/business/intro.htm",
        "official_university_website":
            "https://www.jejunu.ac.kr/eng/",
        "international_application_url":
            "https://jejunu.ac.kr/cs/download.htm?act=download&no=3&seq=249845",
        "international_note":
            "Jeju National University's official College of Economics & Commerce page verifies Business Administration and the university publishes a 2026 undergraduate admission guide for international students.",
    },

    "prog_kr_072": {
        "program_name": "Economics",
        "field_of_study": "Economics",
        "program_url":
            "https://www.jejunu.ac.kr/eng/university/colleges/economic/economics/intro.htm",
        "official_university_website":
            "https://www.jejunu.ac.kr/eng/",
        "international_application_url":
            "https://jejunu.ac.kr/cs/download.htm?act=download&no=3&seq=249845",
        "international_note":
            "Jeju National University's official College of Economics & Commerce page verifies Economics and the university publishes a 2026 undergraduate admission guide for international students.",
    },
}


checks = []


def record(label, passed, detail=""):
    checks.append(
        (
            label,
            bool(passed),
            str(detail),
        )
    )


def text(value):
    if value is None:
        return ""
    return str(value).strip()


def norm(value):
    return text(value).lower()


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.DictReader(f)
        rows = list(reader)
        cols = list(
            reader.fieldnames or []
        )

    return rows, cols


def valid_url(value):
    try:
        parsed = urlparse(
            text(value)
        )

        return (
            parsed.scheme in {
                "http",
                "https",
            }
            and bool(parsed.netloc)
        )

    except Exception:
        return False


print("=" * 138)
print(
    "STEP 172.2F - SOUTH KOREA "
    "BATCH 02 OFFICIAL-SOURCE "
    "RESEARCH EVIDENCE BUILD"
)
print("=" * 138)


# =====================================================================
# SOURCE LOCKS
# =====================================================================

for path in (
    WORKING_SOURCE,
    BATCH02_LOCK,
    CANONICAL,
):
    record(
        f"{path.name} exists",
        path.exists(),
        (
            str(path.relative_to(ROOT))
            if path.exists()
            else "NOT FOUND"
        ),
    )


if not all(
    path.exists()
    for path in (
        WORKING_SOURCE,
        BATCH02_LOCK,
        CANONICAL,
    )
):

    print()
    for label, passed, detail in checks:
        print(
            f"{label:<70}: "
            f"{'PASS' if passed else 'FAIL'}"
            f" | {detail}"
        )

    sys.exit(1)


working_sha_before = sha256(
    WORKING_SOURCE
)

batch_sha_before = sha256(
    BATCH02_LOCK
)

canonical_sha_before = sha256(
    CANONICAL
)


record(
    "Working source SHA256 exact",
    working_sha_before
    == EXPECTED_WORKING_SOURCE_SHA,
    working_sha_before,
)

record(
    "Batch 02 lock SHA256 exact",
    batch_sha_before
    == EXPECTED_BATCH02_LOCK_SHA,
    batch_sha_before,
)


# =====================================================================
# LOAD LOCK
# =====================================================================

batch_rows, batch_cols = load_csv(
    BATCH02_LOCK
)


record(
    "Batch 02 rows = 36",
    len(batch_rows) == 36,
    len(batch_rows),
)

record(
    "Batch 02 columns = 31",
    batch_cols == EXPECTED_COLUMNS,
    len(batch_cols),
)


batch_ids = [
    text(
        row.get(
            "program_id"
        )
    )
    for row in batch_rows
]


record(
    "Batch 02 IDs exact/order exact",
    batch_ids == EXPECTED_IDS,
    (
        f"{batch_ids[0]} -> {batch_ids[-1]}"
        if batch_ids
        else "EMPTY"
    ),
)


record(
    "Research manifest IDs exact",
    set(RESEARCH)
    == set(EXPECTED_IDS),
    len(RESEARCH),
)


batch_map = {
    text(row["program_id"]): row
    for row in batch_rows
}


# =====================================================================
# BUILD EVIDENCE
# =====================================================================

evidence_rows = []


for program_id in EXPECTED_IDS:

    seed = batch_map[
        program_id
    ]

    researched = RESEARCH[
        program_id
    ]

    row = {
        column: text(
            seed.get(column)
        )
        for column in EXPECTED_COLUMNS
    }

    row.update({
        "program_name":
            researched["program_name"],

        "field_of_study":
            researched["field_of_study"],

        "degree_level":
            "Bachelor",

        "program_url":
            researched["program_url"],

        "programme_identity_status":
            "VERIFIED",

        "programme_identity_evidence":
            researched["program_url"],

        "official_university_website":
            researched[
                "official_university_website"
            ],

        "research_status":
            "VERIFIED",

        "research_note":
            (
                "Programme identity verified from "
                "official first-party university or "
                "admissions sources on 2026-08-22. "
                "Optional details not directly supported "
                "by the retrieved source remain blank."
            ),

        "last_verified_at":
            VERIFIED_DATE,

        "international_applicants_status":
            "verified_yes",

        "international_application_url":
            researched[
                "international_application_url"
            ],

        "international_requirements_note":
            researched[
                "international_note"
            ],

        "international_applicants_last_verified_at":
            VERIFIED_DATE,
    })

    evidence_rows.append(
        row
    )


# =====================================================================
# IN-MEMORY AUDIT
# =====================================================================

evidence_ids = [
    row["program_id"]
    for row in evidence_rows
]


record(
    "Evidence rows = 36",
    len(evidence_rows) == 36,
    len(evidence_rows),
)

record(
    "Evidence IDs exact/order exact",
    evidence_ids == EXPECTED_IDS,
    (
        f"{evidence_ids[0]} -> {evidence_ids[-1]}"
    ),
)

record(
    "Duplicate programme IDs = 0",
    len(evidence_ids)
    == len(set(evidence_ids)),
    (
        len(evidence_ids)
        - len(set(evidence_ids))
    ),
)


# Immutable seed identity must be preserved.

IMMUTABLE_FIELDS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
]

seed_mismatches = []


for row in evidence_rows:

    pid = row[
        "program_id"
    ]

    source = batch_map[
        pid
    ]

    for field in IMMUTABLE_FIELDS:

        if text(
            row.get(field)
        ) != text(
            source.get(field)
        ):

            seed_mismatches.append(
                f"{pid}:{field}"
            )


record(
    "Immutable Batch 02 seed identity preserved",
    not seed_mismatches,
    (
        "mismatches=0"
        if not seed_mismatches
        else ", ".join(
            seed_mismatches[:15]
        )
    ),
)


# =====================================================================
# PARENT STRUCTURE
# =====================================================================

parent_counts = Counter(
    row[
        "university_id"
    ]
    for row in evidence_rows
)


record(
    "Parent universities = 12",
    set(parent_counts)
    == EXPECTED_PARENT_IDS,
    len(parent_counts),
)

record(
    "Parents with exactly 3 programmes = 12 / 12",
    (
        set(parent_counts)
        == EXPECTED_PARENT_IDS
        and all(
            parent_counts[parent] == 3
            for parent in EXPECTED_PARENT_IDS
        )
    ),
    (
        f"{sum(parent_counts[p] == 3 for p in EXPECTED_PARENT_IDS)} / 12"
    ),
)


slots_by_parent = defaultdict(set)


for row in evidence_rows:

    slots_by_parent[
        row[
            "university_id"
        ]
    ].add(
        row[
            "program_slot"
        ]
    )


bad_slots = [
    parent
    for parent in sorted(
        EXPECTED_PARENT_IDS
    )
    if slots_by_parent[
        parent
    ]
    != {"1", "2", "3"}
]


record(
    "Parent programme slots exact 1 / 2 / 3",
    not bad_slots,
    (
        "12 / 12"
        if not bad_slots
        else ", ".join(bad_slots)
    ),
)


# =====================================================================
# REQUIRED EVIDENCE
# =====================================================================

REQUIRED_FIELDS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
    "program_name",
    "field_of_study",
    "degree_level",
    "program_url",
    "programme_identity_status",
    "programme_identity_evidence",
    "official_university_website",
    "research_status",
    "research_note",
    "last_verified_at",
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


required_blanks = []


for row in evidence_rows:

    pid = row[
        "program_id"
    ]

    for field in REQUIRED_FIELDS:

        if not text(
            row.get(field)
        ):
            required_blanks.append(
                f"{pid}:{field}"
            )


record(
    "Required evidence blanks = 0",
    not required_blanks,
    (
        "0"
        if not required_blanks
        else ", ".join(
            required_blanks[:15]
        )
    ),
)


identity_counts = Counter(
    norm(
        row[
            "programme_identity_status"
        ]
    )
    for row in evidence_rows
)

research_counts = Counter(
    norm(
        row[
            "research_status"
        ]
    )
    for row in evidence_rows
)

international_counts = Counter(
    norm(
        row[
            "international_applicants_status"
        ]
    )
    for row in evidence_rows
)

degree_counts = Counter(
    norm(
        row[
            "degree_level"
        ]
    )
    for row in evidence_rows
)


record(
    "Identity status VERIFIED = 36",
    identity_counts
    == Counter({
        "verified": 36
    }),
    dict(identity_counts),
)

record(
    "Research status VERIFIED = 36",
    research_counts
    == Counter({
        "verified": 36
    }),
    dict(research_counts),
)

record(
    "International status verified_yes = 36",
    international_counts
    == Counter({
        "verified_yes": 36
    }),
    dict(international_counts),
)

record(
    "Degree level Bachelor = 36",
    degree_counts
    == Counter({
        "bachelor": 36
    }),
    dict(degree_counts),
)


# =====================================================================
# URL AUDIT
# =====================================================================

URL_FIELDS = [
    "program_url",
    "programme_identity_evidence",
    "official_university_website",
    "international_application_url",
]


invalid_urls = []


for row in evidence_rows:

    pid = row[
        "program_id"
    ]

    for field in URL_FIELDS:

        value = row[
            field
        ]

        if not valid_url(
            value
        ):
            invalid_urls.append(
                f"{pid}:{field}"
            )


record(
    "Invalid populated URLs = 0",
    not invalid_urls,
    (
        "0"
        if not invalid_urls
        else ", ".join(
            invalid_urls[:15]
        )
    ),
)


# =====================================================================
# OPTIONAL DETAIL COVERAGE
# =====================================================================

OPTIONAL_FIELDS = [
    "duration_years",
    "study_mode",
    "language_of_instruction",
    "tuition_fee",
    "minimum_gpa",
    "ielts_requirement",
    "toefl_requirement",
    "intake",
    "application_deadline",
]


optional_counts = {
    field: sum(
        bool(
            text(
                row.get(field)
            )
        )
        for row in evidence_rows
    )
    for field in OPTIONAL_FIELDS
}


for field in OPTIONAL_FIELDS:

    record(
        f"{field} populated = 0",
        optional_counts[
            field
        ]
        == 0,
        optional_counts[
            field
        ],
    )


# =====================================================================
# CANONICAL LOCK
# =====================================================================

with CANONICAL.open(
    "r",
    encoding="utf-8-sig",
) as f:

    canonical_rows = json.load(f)


record(
    "Canonical programmes = 600",
    (
        isinstance(
            canonical_rows,
            list,
        )
        and len(canonical_rows)
        == 600
    ),
    (
        len(canonical_rows)
        if isinstance(
            canonical_rows,
            list,
        )
        else "NOT A LIST"
    ),
)


canonical_kr = []


if isinstance(
    canonical_rows,
    list,
):

    for row in canonical_rows:

        if not isinstance(
            row,
            dict,
        ):
            continue

        pid = text(
            row.get(
                "program_id",
                row.get(
                    "programme_id",
                    "",
                ),
            )
        )

        if pid.startswith(
            "prog_kr_"
        ):
            canonical_kr.append(
                pid
            )


record(
    "South Korea canonical programmes = 0",
    len(canonical_kr) == 0,
    len(canonical_kr),
)


# =====================================================================
# PRE-WRITE REPORT
# =====================================================================

print()
print(
    "BATCH 02 RESEARCH EVIDENCE AUDIT"
)
print("-" * 138)


for label, passed, detail in checks:

    print(
        f"{label:<66}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


failed = [
    (
        label,
        detail,
    )
    for (
        label,
        passed,
        detail,
    )
    in checks
    if not passed
]


if failed:

    print()
    print("=" * 138)
    print(
        "STEP 172.2F SOUTH KOREA "
        "BATCH 02 OFFICIAL RESEARCH "
        "EVIDENCE: FAIL"
    )

    print(
        f"FAILED CHECKS: "
        f"{len(failed)}"
    )

    for label, detail in failed:
        print(
            f" - {label}: {detail}"
        )

    print()
    print(
        "STOP: EVIDENCE FILE NOT CREATED"
    )
    print(
        "DO NOT APPLY BATCH 02"
    )
    print(
        "DO NOT WRITE programs.json"
    )
    print(
        "DO NOT WRITE MONGODB"
    )
    print("=" * 138)

    sys.exit(1)


# =====================================================================
# WRITE TEMP EVIDENCE FILE
# =====================================================================

if TEMP.exists():
    TEMP.unlink()


with TEMP.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=EXPECTED_COLUMNS,
        lineterminator="\n",
    )

    writer.writeheader()

    writer.writerows(
        evidence_rows
    )


candidate_sha = sha256(
    TEMP
)


# =====================================================================
# SAFE OUTPUT POLICY
# =====================================================================

created_new = False
existing_identical = False


if EVIDENCE.exists():

    existing_sha = sha256(
        EVIDENCE
    )

    if existing_sha == candidate_sha:

        existing_identical = True

        TEMP.unlink()

    else:

        TEMP.unlink()

        print()
        print("=" * 138)
        print(
            "STEP 172.2F SOUTH KOREA "
            "BATCH 02 OFFICIAL RESEARCH "
            "EVIDENCE: FAIL"
        )
        print()
        print(
            "A DIFFERENT BATCH 02 "
            "EVIDENCE FILE ALREADY EXISTS"
        )
        print(
            str(
                EVIDENCE.relative_to(
                    ROOT
                )
            )
        )
        print(
            f"Existing SHA256 : "
            f"{existing_sha}"
        )
        print(
            f"Candidate SHA256: "
            f"{candidate_sha}"
        )
        print()
        print(
            "NO FILE WAS OVERWRITTEN"
        )
        print("=" * 138)

        sys.exit(1)

else:

    os.replace(
        TEMP,
        EVIDENCE,
    )

    created_new = True


# =====================================================================
# POST-WRITE VERIFICATION
# =====================================================================

written_rows, written_cols = load_csv(
    EVIDENCE
)

evidence_sha = sha256(
    EVIDENCE
)


post_checks = []


def post_record(
    label,
    passed,
    detail="",
):

    post_checks.append(
        (
            label,
            bool(passed),
            str(detail),
        )
    )


post_record(
    "Evidence output exists",
    EVIDENCE.exists(),
    str(
        EVIDENCE.relative_to(
            ROOT
        )
    ),
)

post_record(
    "Evidence SHA matches candidate",
    evidence_sha
    == candidate_sha,
    evidence_sha,
)

post_record(
    "Written columns = 31",
    written_cols
    == EXPECTED_COLUMNS,
    len(written_cols),
)

post_record(
    "Written rows = 36",
    len(written_rows)
    == 36,
    len(written_rows),
)


written_ids = [
    text(
        row.get(
            "program_id"
        )
    )
    for row in written_rows
]


post_record(
    "Written IDs exact",
    written_ids
    == EXPECTED_IDS,
    (
        f"{written_ids[0]} -> "
        f"{written_ids[-1]}"
    ),
)


working_sha_after = sha256(
    WORKING_SOURCE
)

batch_sha_after = sha256(
    BATCH02_LOCK
)

canonical_sha_after = sha256(
    CANONICAL
)


post_record(
    "Working source unchanged",
    (
        working_sha_after
        == working_sha_before
        == EXPECTED_WORKING_SOURCE_SHA
    ),
    working_sha_after,
)

post_record(
    "Batch 02 lock unchanged",
    (
        batch_sha_after
        == batch_sha_before
        == EXPECTED_BATCH02_LOCK_SHA
    ),
    batch_sha_after,
)

post_record(
    "programs.json unchanged",
    canonical_sha_after
    == canonical_sha_before,
    canonical_sha_after,
)


print()
print(
    "POST-WRITE EVIDENCE VERIFICATION"
)
print("-" * 138)


for label, passed, detail in post_checks:

    print(
        f"{label:<66}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


post_failed = [
    (
        label,
        detail,
    )
    for (
        label,
        passed,
        detail,
    )
    in post_checks
    if not passed
]


if post_failed:

    if (
        created_new
        and EVIDENCE.exists()
    ):
        EVIDENCE.unlink()

    print()
    print("=" * 138)
    print(
        "STEP 172.2F SOUTH KOREA "
        "BATCH 02 OFFICIAL RESEARCH "
        "EVIDENCE: FAIL"
    )

    print(
        "INVALID NEW EVIDENCE "
        "OUTPUT REMOVED"
    )

    print(
        "DO NOT APPLY BATCH 02"
    )
    print("=" * 138)

    sys.exit(1)


# =====================================================================
# PROGRAMME SUMMARY
# =====================================================================

print()
print(
    "BATCH 02 PROGRAMME RESEARCH SUMMARY"
)
print("-" * 138)


for row in written_rows:

    print(
        f"{row['program_id']} | "
        f"{row['university_id']} | "
        f"{row['degree_level']:<8} | "
        f"{row['international_applicants_status']:<12} | "
        f"{row['program_name']}"
    )


print()
print("=" * 138)
print(
    "STEP 172.2F SOUTH KOREA "
    "BATCH 02 OFFICIAL RESEARCH "
    "EVIDENCE: PASS"
)
print()

print(
    "BATCH 02 PROGRAMMES                : 36"
)

print(
    "BATCH 02 UNIVERSITIES              : 12"
)

print(
    "PROGRAMME IDENTITIES VERIFIED      : 36 / 36"
)

print(
    "RESEARCH STATUS VERIFIED           : 36 / 36"
)

print(
    "INTERNATIONAL VERIFIED_YES         : 36"
)

print(
    "INTERNATIONAL UNKNOWN              : 0"
)

print(
    "DEGREE LEVELS                      : 36 BACHELOR"
)

print(
    "LANGUAGE EVIDENCE                  : 36 BLANK"
)

print(
    "TUITION CAPTURED                   : 0 / 36"
)

print()
print(
    "EVIDENCE FILE                      : "
    "planning\\32_south_korea_program_research_batch02_evidence.csv"
)

print(
    f"EVIDENCE SHA256                    : "
    f"{evidence_sha}"
)

print(
    "WORKING SOURCE QUEUE               : UNCHANGED"
)

print(
    "BATCH 02 LOCK                      : UNCHANGED"
)

print(
    "CANONICAL programs.json            : UNCHANGED / 600"
)

print(
    "MONGODB WRITE PERFORMED            : False"
)

print()

if existing_identical:

    print(
        "EVIDENCE OUTPUT STATUS            : "
        "EXISTING IDENTICAL FILE REUSED"
    )

else:

    print(
        "EVIDENCE OUTPUT STATUS            : "
        "NEW OFFICIAL-SOURCE EVIDENCE CREATED"
    )

print()
print(
    "NEXT: STEP 172.2G"
)

print(
    "AUDIT BATCH 02 EVIDENCE BEFORE "
    "APPLYING IT TO THE STAGED "
    "150-ROW SOUTH KOREA QUEUE"
)

print("=" * 138)
