import csv
from pathlib import Path
from collections import Counter


FILE = Path(
    "data/evidence/china_batch_01/china_programme_batch01_evidence.csv"
)


required_fields = [
    "program_id",
    "university_id",
    "university_name",
    "program_name",
    "field_of_study",
    "degree_level",
    "programme_identity_status",
    "research_status",
]


print("=" * 80)
print("STEP 183.6 - CHINA BATCH 01 EVIDENCE VALIDATION")
print("=" * 80)


with open(
    FILE,
    encoding="utf-8"
) as f:

    rows = list(csv.DictReader(f))


print()
print("Total rows:", len(rows))


# duplicate check

ids = [
    r["program_id"]
    for r in rows
]


duplicates = [
    x
    for x,c in Counter(ids).items()
    if c > 1
]


print(
    "Duplicate program IDs:",
    len(duplicates)
)


# required field check

invalid = []

for r in rows:

    missing = [
        field
        for field in required_fields
        if not r.get(field)
    ]

    if missing:
        invalid.append(
            (
                r.get("program_id"),
                missing
            )
        )


print(
    "Invalid rows:",
    len(invalid)
)


if invalid:
    print()

    for item in invalid:
        print(item)


print()
print("=" * 80)


if (
    len(duplicates) == 0
    and len(invalid) == 0
):
    print(
        "CHINA BATCH 01 VALIDATION: PASS"
    )
else:
    print(
        "CHINA BATCH 01 VALIDATION: FAIL"
    )

print("=" * 80)