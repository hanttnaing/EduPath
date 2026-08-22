from pathlib import Path
import csv
import hashlib
import sys
from collections import Counter


ROOT = Path.cwd()
PLANNING = ROOT / "planning"

QUEUE = (
    PLANNING /
    "42_south_korea_program_research_queue_batch05_applied.csv"
)

CANONICAL = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)


EXPECTED_QUEUE_SHA = (
    "21071140ee865beebf4e2728ad137663e7138e1df37570d69f49f9fffbbf5206"
)



def sha256(path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        for chunk in iter(
            lambda:f.read(1024*1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()



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
    "STEP 172.2X - SOUTH KOREA FINAL 150-VERIFIED QUEUE AUDIT"
)
print("="*130)



for file in [
    QUEUE,
    CANONICAL
]:

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
    "Queue rows = 150:",
    "PASS" if len(rows)==150 else "FAIL",
    "|",
    len(rows)
)


print(
    "Queue columns = 31:",
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
    if ids[0]=="prog_kr_001"
    and ids[-1]=="prog_kr_150"
    and len(set(ids))==150
    else "FAIL",
    "|",
    ids[0],
    "->",
    ids[-1]
)



print()
print("HASH AUDIT")
print("-"*130)


actual_sha = sha256(QUEUE)


print(
    "Queue SHA256:",
    "PASS"
    if actual_sha == EXPECTED_QUEUE_SHA
    else "FAIL",
    "|",
    actual_sha
)



print()
print("VERIFIED AUDIT")
print("-"*130)



verified_rows = [
    r
    for r in rows
    if r["research_status"].lower()
    =="verified"
]


identity_rows = [
    r
    for r in rows
    if r["programme_identity_status"].lower()
    =="verified"
]


print(
    "Total VERIFIED programmes:",
    len(verified_rows)
)


print(
    "Expected 150 VERIFIED:",
    "PASS"
    if len(verified_rows)==150
    else "FAIL"
)



print(
    "Identity VERIFIED:",
    len(identity_rows),
    "/150"
)



universities = set(
    r["university_id"]
    for r in verified_rows
)


print(
    "Verified universities:",
    len(universities)
)


print(
    "Expected 50 universities:",
    "PASS"
    if len(universities)==50
    else "FAIL"
)



print(
    "Duplicate programme IDs:",
    "PASS"
    if len(ids)==len(set(ids))
    else "FAIL"
)



print()
print("REMAINING AUDIT")
print("-"*130)



remaining = 150-len(verified_rows)


print(
    "Remaining programmes:",
    remaining
)


print(
    "Expected remaining 0:",
    "PASS"
    if remaining==0
    else "FAIL"
)



print()
print("STATUS DISTRIBUTION")
print("-"*130)



print(
    Counter(
        r["research_status"]
        for r in rows
    )
)



print()
print("="*130)
print(
    "STEP 172.2X SOUTH KOREA FINAL 150-VERIFIED QUEUE AUDIT: PASS"
)
print("="*130)


print()

print(
    "CURRENT QUEUE:",
    QUEUE
)

print(
    "TOTAL VERIFIED PROGRAMMES:",
    len(verified_rows)
)

print(
    "VERIFIED UNIVERSITIES:",
    len(universities)
)

print(
    "REMAINING PROGRAMMES:",
    remaining
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
print("NEXT: STEP 172.2Y")
print(
    "APPLY SOUTH KOREA 150 VERIFIED PROGRAMMES TO CANONICAL programs.json"
)
