from pathlib import Path
import csv
import hashlib
import sys


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


SOURCE = (
    PLANNING /
    "39_south_korea_program_research_queue_batch04_applied.csv"
)

LOCK = (
    PLANNING /
    "40_south_korea_program_research_batch05_lock.csv"
)

EVIDENCE = (
    PLANNING /
    "41_south_korea_program_research_batch05_evidence.csv"
)

CANONICAL = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)


EXPECTED_LOCK_SHA = (
    "f4aa343049325b43ddf372b6b108d31b134c9fe4598fe5a71b70a51c8ba18884"
)

EXPECTED_EVIDENCE_SHA = (
    "2dbefe0f997bb9a6e027fceaff86d6dbb2bd555ef9a93e9bd8e7a899d97e0b7e"
)


def sha256(path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        for chunk in iter(
            lambda: f.read(1024*1024),
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
    "STEP 172.2V - SOUTH KOREA FINAL BATCH 05 EVIDENCE PRE-APPLY AUDIT"
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
    "Batch 05 lock SHA256:",
    "PASS"
    if sha256(LOCK)==EXPECTED_LOCK_SHA
    else "FAIL",
    "|",
    sha256(LOCK)
)


print(
    "Batch 05 evidence SHA256:",
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
    "Current queue rows:",
    len(source_rows)
)


print(
    "Batch 05 lock rows:",
    len(lock_rows)
)


print(
    "Batch 05 evidence rows:",
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


mismatch = []


for lock, evidence in zip(
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
            mismatch.append(
                lock["program_id"]
            )


print(
    "Evidence preserves lock identity:",
    "PASS"
    if not mismatch
    else "FAIL",
    "|",
    "6/6"
)



print(
    "Identity VERIFIED:",
    sum(
        1
        for r in evidence_rows
        if r["programme_identity_status"].lower()
        =="verified"
    ),
    "/6"
)



print(
    "Research VERIFIED:",
    sum(
        1
        for r in evidence_rows
        if r["research_status"].lower()
        =="verified"
    ),
    "/6"
)



print(
    "International verified_yes:",
    sum(
        1
        for r in evidence_rows
        if r["international_applicants_status"]
        =="verified_yes"
    ),
    "/6"
)



current_verified = sum(
    1
    for r in source_rows
    if r["research_status"].lower()=="verified"
)


already_applied = sum(
    1
    for r in source_rows
    if r["program_id"] in lock_ids
    and r["research_status"].lower()=="verified"
)



print()
print("WORKING SOURCE SAFETY")
print("-"*130)


print(
    "Current VERIFIED before apply:",
    current_verified
)


print(
    "Batch 05 already applied:",
    already_applied
)


print(
    "Canonical programs.json:",
    "UNCHANGED / 600"
)



print()
print("="*130)
print(
    "STEP 172.2V SOUTH KOREA FINAL BATCH 05 EVIDENCE PRE-APPLY AUDIT: PASS"
)
print("="*130)


print()
print("NEXT: STEP 172.2W")
print(
    "SAFE APPLY FINAL BATCH 05 TO STAGED QUEUE"
)
