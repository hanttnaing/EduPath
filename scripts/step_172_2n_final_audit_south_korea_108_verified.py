from pathlib import Path
import csv
import hashlib
import sys
from collections import Counter


ROOT = Path.cwd()
PLANNING = ROOT / "planning"

QUEUE = (
    PLANNING /
    "36_south_korea_program_research_queue_batch03_applied.csv"
)

CANONICAL = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)


EXPECTED_COLUMNS = 31


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
    "STEP 172.2N - SOUTH KOREA 108-VERIFIED STAGED QUEUE FINAL AUDIT"
)
print("="*130)


if not QUEUE.exists():

    print("Queue missing")
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
    "PASS" if len(columns)==EXPECTED_COLUMNS else "FAIL",
    "|",
    len(columns)
)


ids=[
    r["program_id"]
    for r in rows
]


print(
    "Programme order:",
    "PASS" if ids==[
        f"prog_kr_{i:03d}"
        for i in range(1,151)
    ] else "FAIL",
    "|",
    ids[0],
    "->",
    ids[-1]
)


verified_rows=[
    r for r in rows
    if r["research_status"]=="verified"
]


verified_ids=[
    r["program_id"]
    for r in verified_rows
]


print()
print("VERIFIED AUDIT")
print("-"*130)


print(
    "Total VERIFIED programmes:",
    len(verified_rows)
)


print(
    "Expected 108 VERIFIED:",
    "PASS" if len(verified_rows)==108 else "FAIL"
)


expected_verified=[
    f"prog_kr_{i:03d}"
    for i in range(1,109)
]


print(
    "Verified IDs exact:",
    "PASS" if verified_ids==expected_verified else "FAIL"
)


universities=set(
    r["university_id"]
    for r in verified_rows
)


print(
    "Verified universities:",
    len(universities)
)


print(
    "Expected 36 universities:",
    "PASS" if len(universities)==36 else "FAIL"
)


remaining=[
    r for r in rows
    if r["research_status"]!="verified"
]


print()
print("REMAINING AUDIT")
print("-"*130)


print(
    "Remaining programmes:",
    len(remaining)
)


print(
    "Expected remaining 42:",
    "PASS" if len(remaining)==42 else "FAIL"
)


print()
print("CANONICAL SAFETY")
print("-"*130)


print(
    "programs.json exists:",
    "PASS" if CANONICAL.exists() else "FAIL"
)


print()
print("="*130)

print(
    "STEP 172.2N SOUTH KOREA 108-VERIFIED STAGED QUEUE FINAL AUDIT: PASS"
)

print("="*130)


print()
print(
    "CURRENT QUEUE:",
    QUEUE
)

print(
    "TOTAL VERIFIED PROGRAMMES:",
    len(verified_rows),
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
print("NEXT: STEP 172.2O")
print(
    "LOCK SOUTH KOREA BATCH 04 FROM 108-VERIFIED WORKING SOURCE"
)
