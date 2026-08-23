import csv
from collections import Counter


path="data/evidence/china_verified_batch_01/china_verified_programme_evidence.csv"


with open(
    path,
    encoding="utf-8"
) as f:
    rows=list(csv.DictReader(f))


ids=[
    r["program_id"]
    for r in rows
]


duplicates=[
    k
    for k,v in Counter(ids).items()
    if v>1
]


required=[
    "program_id",
    "university_id",
    "university_name",
    "program_name",
    "program_url",
    "official_university_website",
    "research_status",
    "last_verified_at"
]


invalid=[]


for r in rows:
    for field in required:
        if not r.get(field):
            invalid.append(
                (r["program_id"],field)
            )


print("="*80)
print("STEP 187.3 CHINA VERIFIED BATCH 01 VALIDATION")
print("="*80)

print("Total rows:",len(rows))
print("Duplicate IDs:",len(duplicates))
print("Invalid rows:",len(invalid))


if (
    len(duplicates)==0
    and len(invalid)==0
):
    print()
    print("CHINA VERIFIED BATCH 01 VALIDATION: PASS")
else:
    print()
    print("CHINA VERIFIED BATCH 01 VALIDATION: FAIL")


print("="*80)

