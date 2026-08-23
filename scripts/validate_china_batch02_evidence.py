import csv
from collections import Counter


path="data/evidence/china_batch_02/china_programme_batch02_evidence.csv"


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


invalid=[]

required=[
    "program_id",
    "university_id",
    "university_name",
    "program_name",
    "official_university_website",
    "last_verified_at",
    "collected_at"
]


for r in rows:
    for field in required:
        if not r.get(field):
            invalid.append(
                (
                    r.get("program_id"),
                    field
                )
            )


print("="*80)
print("STEP 186.2 - CHINA BATCH 02 EVIDENCE VALIDATION")
print("="*80)

print("Total rows:",len(rows))
print("Duplicate program IDs:",len(duplicates))
print("Invalid rows:",len(invalid))


if duplicates:
    print("Duplicates:")
    for d in duplicates:
        print(d)


if invalid:
    print("Invalid:")
    for x in invalid:
        print(x)


print()

if (
    len(rows)==60
    and len(duplicates)==0
    and len(invalid)==0
):
    print(
        "CHINA BATCH 02 VALIDATION: PASS"
    )
else:
    print(
        "CHINA BATCH 02 VALIDATION: FAIL"
    )

print("="*80)

