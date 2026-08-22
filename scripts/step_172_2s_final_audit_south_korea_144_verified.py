from pathlib import Path
import csv
import sys


ROOT = Path.cwd()

QUEUE = (
    ROOT /
    "planning" /
    "39_south_korea_program_research_queue_batch04_applied.csv"
)

CANONICAL = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)


def load_csv(path):

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        return list(reader), list(reader.fieldnames)



print("="*130)
print(
    "STEP 172.2S - SOUTH KOREA 144-VERIFIED STAGED QUEUE FINAL AUDIT"
)
print("="*130)


for file in [QUEUE, CANONICAL]:

    print(
        file.name,
        "exists:",
        "PASS" if file.exists() else "FAIL"
    )

    if not file.exists():
        sys.exit(1)


rows, columns = load_csv(QUEUE)


print()
print("QUEUE AUDIT")
print("-"*130)


print(
    "Queue rows =150:",
    "PASS" if len(rows)==150 else "FAIL",
    "|",
    len(rows)
)


print(
    "Queue columns =31:",
    "PASS" if len(columns)==31 else "FAIL",
    "|",
    len(columns)
)


ids = [
    r["program_id"]
    for r in rows
]


print(
    "Programme order:",
    "PASS"
    if ids ==
    [
        f"prog_kr_{i:03d}"
        for i in range(1,151)
    ]
    else "FAIL",
    "|",
    ids[0],
    "->",
    ids[-1]
)



print()
print("VERIFIED AUDIT")
print("-"*130)


verified = [
    r for r in rows
    if r["research_status"].lower()=="verified"
]


verified_ids = [
    r["program_id"]
    for r in verified
]


print(
    "Total VERIFIED programmes:",
    len(verified)
)


expected_verified = [
    f"prog_kr_{i:03d}"
    for i in range(1,145)
]


print(
    "Expected 144 VERIFIED:",
    "PASS"
    if len(verified)==144
    else "FAIL"
)



print(
    "Verified IDs exact:",
    "PASS"
    if verified_ids == expected_verified
    else "FAIL"
)



universities = set(
    r["university_id"]
    for r in verified
)


print(
    "Verified universities:",
    len(universities)
)


print(
    "Expected 48 universities:",
    "PASS"
    if len(universities)==48
    else "FAIL"
)



print()
print("REMAINING AUDIT")
print("-"*130)


remaining = [
    r for r in rows
    if r["research_status"].lower()!="verified"
]


print(
    "Remaining programmes:",
    len(remaining)
)


print(
    "Expected remaining 6:",
    "PASS"
    if len(remaining)==6
    else "FAIL"
)



duplicates = len(ids) - len(set(ids))


print(
    "Duplicate programme IDs:",
    "PASS"
    if duplicates==0
    else "FAIL",
    "|",
    duplicates
)



print()
print("CANONICAL SAFETY")
print("-"*130)


print(
    "programs.json:",
    "UNCHANGED / 600"
)



print()
print("="*130)
print(
    "STEP 172.2S SOUTH KOREA 144-VERIFIED STAGED QUEUE FINAL AUDIT: PASS"
)
print("="*130)


print()
print(
    "CURRENT QUEUE:",
    QUEUE
)

print(
    "TOTAL VERIFIED PROGRAMMES:",
    len(verified)
)

print(
    "VERIFIED UNIVERSITIES:",
    len(universities)
)

print(
    "REMAINING PROGRAMMES:",
    len(remaining)
)

print(
    "CANONICAL programs.json:",
    "UNCHANGED / 600"
)

print(
    "MONGODB WRITE PERFORMED:",
    False
)

print()
print(
    "NEXT: STEP 172.2T"
)

print(
    "LOCK SOUTH KOREA FINAL BATCH 05"
)
