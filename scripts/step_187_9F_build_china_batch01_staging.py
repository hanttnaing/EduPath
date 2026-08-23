import csv
import json
from pathlib import Path


input_file = Path(
    "data/evidence/china_verified_batch_01/"
    "china_verified_programme_final_audit.csv"
)


output_file = Path(
    "data/staging/china_batch_01/"
    "china_batch01_verified_programmes.json"
)


output_file.parent.mkdir(
    parents=True,
    exist_ok=True
)


with input_file.open(
    encoding="utf-8"
) as f:

    rows = list(csv.DictReader(f))


programmes=[]


for r in rows:

    programmes.append({

        "program_id": r["program_id"],

        "university_id": r["university_id"],

        "university_name": r["university_name"],

        "program_name": r["program_name"],

        "field_of_study": r["field_of_study"],

        "degree_level": r["degree_level"],

        "official_program_url": r["official_program_url"],

        "official_department_source": r["official_department_source"],

        "programme_identity_status": r["programme_identity_status"],

        "international_applicants_status": r["international_applicants_status"],

        "research_status": r["research_status"],

        "last_verified_at": r["last_verified_at"],

        "collected_at": r["collected_at"]

    })


with output_file.open(
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
print("STEP 187.9F CHINA BATCH 01 STAGING BUILD")
print("="*80)

print("Input rows:",len(rows))
print("Output programmes:",len(programmes))

print("Saved:",output_file)

print("="*80)

