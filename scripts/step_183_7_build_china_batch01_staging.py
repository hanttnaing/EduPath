import csv
import json
from pathlib import Path


INPUT = Path(
    "data/evidence/china_batch_01/china_programme_batch01_evidence.csv"
)

OUTPUT = Path(
    "data/staging/china_batch_01/china_programme_batch01_verified.json"
)


OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)


with open(
    INPUT,
    encoding="utf-8"
) as f:

    rows = list(csv.DictReader(f))


programmes = []


for row in rows:

    programmes.append({

        "program_id":
            row["program_id"],

        "university_id":
            row["university_id"],

        "university_name":
            row["university_name"],

        "country_id":
            "country_cn",

        "country":
            "China",

        "country_code":
            "CN",

        "program_slot":
            row["program_slot"],

        "program_name":
            row["program_name"],

        "field_of_study":
            row["field_of_study"],

        "degree_level":
            row["degree_level"],

        "duration_years":
            None,

        "study_mode":
            "",

        "language_of_instruction":
            "",

        "tuition_fee":
            None,

        "tuition_currency":
            "CNY",

        "tuition_period":
            "Annual",

        "minimum_gpa":
            None,

        "ielts_requirement":
            None,

        "toefl_requirement":
            None,

        "intake":
            [],

        "application_deadline":
            None,

        "program_url":
            row["program_url"],

        "programme_identity_status":
            row["programme_identity_status"],

        "programme_identity_evidence":
            row["programme_identity_evidence"],

        "official_university_website":
            row["official_university_website"],

        "research_status":
            row["research_status"],

        "research_note":
            row["research_note"],

        "last_verified_at":
            row["last_verified_at"],

        "international_applicants_status":
            row["international_applicants_status"],

        "international_application_url":
            row["international_application_url"],

        "international_requirements_note":
            row["international_requirements_note"],

    })


with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        programmes,
        f,
        ensure_ascii=False,
        indent=2
    )


print("="*80)
print("STEP 183.7 CHINA BATCH 01 STAGING BUILD")
print("="*80)

print(
    "Input rows:",
    len(rows)
)

print(
    "Output programmes:",
    len(programmes)
)

print(
    "Saved:",
    OUTPUT
)

print("="*80)
