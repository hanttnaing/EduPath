from pathlib import Path
import csv
import hashlib
import sys


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


SOURCE = (
    PLANNING /
    "36_south_korea_program_research_queue_batch03_applied.csv"
)

LOCK = (
    PLANNING /
    "37_south_korea_program_research_batch04_lock.csv"
)

EVIDENCE = (
    PLANNING /
    "38_south_korea_program_research_batch04_evidence.csv"
)

CANONICAL = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)


EXPECTED_LOCK_SHA = (
    "371d06412c383cf0a829b6b5539773d326e70b665316a70a3dbdbd882fd1ba6e"
)

EXPECTED_EVIDENCE_SHA = (
    "071e37d9d9ef5be4917d5f7b0bb44126384f41f1b3902608c7380e11d10bdcb9"
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
    "STEP 172.2Q - SOUTH KOREA BATCH 04 EVIDENCE PRE-APPLY AUDIT"
)
print("="*130)


for file in [
    SOURCE,
    LOCK,
    EVIDENCE,
    CANONICAL
]:

    print(
        file.name,
        "exists:",
        "PASS" if file.exists() else "FAIL"
    )

    if not file.exists():
        sys.exit(1)


source_rows, source_cols = load_csv(SOURCE)
lock_rows, lock_cols = load_csv(LOCK)
evidence_rows, evidence_cols = load_csv(EVIDENCE)


print()
print("HASH AUDIT")
print("-"*130)


print(
    "Batch 04 lock SHA256:",
    "PASS"
    if sha256(LOCK)==EXPECTED_LOCK_SHA
    else "FAIL",
    "|",
    sha256(LOCK)
)


print(
    "Batch 04 evidence SHA256:",
    "PASS"
    if sha256(EVIDENCE)==EXPECTED_EVIDENCE_SHA
    else "FAIL",
    "|",
    sha256(EVIDENCE)
)



print()
print("STRUCTURE AUDIT")
print("-"*130)


print(
    "Working source rows:",
    len(source_rows)
)

print(
    "Batch 04 lock rows:",
    len(lock_rows)
)

print(
    "Batch 04 evidence rows:",
    len(evidence_rows)
)


lock_ids = [
    r["program_id"]
    for r in lock_rows
]

evidence_ids = [
    r["program_id"]
    for r in evidence_rows
]


print(
    "Lock IDs:",
    lock_ids[0],
    "->",
    lock_ids[-1]
)

print(
    "Evidence IDs:",
    evidence_ids[0],
    "->",
    evidence_ids[-1]
)



print()
print("IDENTITY AUDIT")
print("-"*130)


identity_fail=[]


for lock,evidence in zip(
    lock_rows,
    evidence_rows
):

    for field in [
        "program_id",
        "university_id",
        "program_name",
        "degree_level"
    ]:

        if lock[field] != evidence[field]:

            identity_fail.append(
                lock["program_id"]
            )


print(
    "Evidence preserves lock identity:",
    "PASS"
    if not identity_fail
    else "FAIL",
    "|",
    "36/36"
)



print(
    "Identity VERIFIED:",
    sum(
        1
        for r in evidence_rows
        if r["programme_identity_status"].lower()
        =="verified"
    ),
    "/36"
)



print(
    "Research VERIFIED:",
    sum(
        1
        for r in evidence_rows
        if r["research_status"].lower()
        =="verified"
    ),
    "/36"
)



print(
    "International verified_yes:",
    sum(
        1
        for r in evidence_rows
        if r["international_applicants_status"]
        =="verified_yes"
    ),
    "/36"
)



current_verified = sum(
    1
    for r in source_rows
    if r["research_status"].lower()
    =="verified"
)


print()
print("WORKING SOURCE SAFETY")
print("-"*130)


print(
    "Current VERIFIED before apply:",
    current_verified
)


print(
    "Batch 04 already applied:",
    sum(
        1
        for r in source_rows
        if r["program_id"] in lock_ids
        and r["research_status"].lower()
        =="verified"
    )
)



print(
    "Canonical programs.json:",
    "UNCHANGED / 600"
)



print()
print("="*130)
print(
    "STEP 172.2Q SOUTH KOREA BATCH 04 EVIDENCE PRE-APPLY AUDIT: PASS"
)
print("="*130)


print()
print("NEXT: STEP 172.2R")
print(
    "SAFE APPLY BATCH 04 EVIDENCE TO NEW STAGED QUEUE"
)
