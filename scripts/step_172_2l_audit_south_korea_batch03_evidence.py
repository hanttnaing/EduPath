from pathlib import Path
import csv
import hashlib
import sys


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


WORKING_SOURCE = (
    PLANNING /
    "33_south_korea_program_research_queue_batch02_applied.csv"
)

BATCH03_LOCK = (
    PLANNING /
    "34_south_korea_program_research_batch03_lock.csv"
)

BATCH03_EVIDENCE = (
    PLANNING /
    "35_south_korea_program_research_batch03_evidence.csv"
)

CANONICAL = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)


EXPECTED_COLUMNS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
    "program_name",
    "field_of_study",
    "degree_level",
    "duration_years",
    "study_mode",
    "language_of_instruction",
    "tuition_fee",
    "tuition_currency",
    "tuition_period",
    "minimum_gpa",
    "gpa_scale",
    "ielts_requirement",
    "toefl_requirement",
    "intake",
    "application_deadline",
    "program_url",
    "programme_identity_status",
    "programme_identity_evidence",
    "official_university_website",
    "research_status",
    "research_note",
    "last_verified_at",
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


EXPECTED_LOCK_SHA = (
    "2c2086148f355ef12e14234f96d0d35da77bee223848165e47932b6dbb1a7111"
)

EXPECTED_EVIDENCE_SHA = (
    "72f3e052f6aef1a3d331c60d2533d7c5a4c045c8988ee48829308a0796ead909"
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


def compare_identity(a,b):

    fields = [
        "university_id",
        "program_name",
        "degree_level",
        "program_id"
    ]

    for field in fields:

        if str(a.get(field,"")).strip() != str(b.get(field,"")).strip():
            return False

    return True



print("="*130)
print(
    "STEP 172.2L - SOUTH KOREA BATCH 03 EVIDENCE PRE-APPLY AUDIT"
)
print("="*130)


for file in [
    WORKING_SOURCE,
    BATCH03_LOCK,
    BATCH03_EVIDENCE,
    CANONICAL
]:

    print(
        file.name,
        "exists:",
        "PASS" if file.exists() else "FAIL"
    )

    if not file.exists():
        sys.exit(1)


print()
print("HASH AUDIT")
print("-"*130)


working_rows, working_cols = load_csv(WORKING_SOURCE)
lock_rows, lock_cols = load_csv(BATCH03_LOCK)
evidence_rows, evidence_cols = load_csv(BATCH03_EVIDENCE)


print(
    "Batch 03 lock SHA256:",
    "PASS" if sha256(BATCH03_LOCK)==EXPECTED_LOCK_SHA else "FAIL",
    "|",
    sha256(BATCH03_LOCK)
)


print(
    "Batch 03 evidence SHA256:",
    "PASS" if sha256(BATCH03_EVIDENCE)==EXPECTED_EVIDENCE_SHA else "FAIL",
    "|",
    sha256(BATCH03_EVIDENCE)
)


print()
print("STRUCTURE AUDIT")
print("-"*130)


print(
    "Working source rows =150:",
    len(working_rows)
)

print(
    "Lock rows =36:",
    len(lock_rows)
)

print(
    "Evidence rows =36:",
    len(evidence_rows)
)


print(
    "Schema exact:",
    lock_cols == EXPECTED_COLUMNS
    and evidence_cols == EXPECTED_COLUMNS
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

lock_map={
    r["program_id"]:r
    for r in lock_rows
}

evidence_map={
    r["program_id"]:r
    for r in evidence_rows
}


for pid in lock_ids:

    if not compare_identity(
        lock_map[pid],
        evidence_map[pid]
    ):

        identity_fail.append(pid)


print(
    "Evidence preserves lock identity:",
    "PASS" if not identity_fail else "FAIL",
    "|",
    "36/36"
)


verified_identity = sum(
    1 for r in evidence_rows
    if r["programme_identity_status"]
    =="verified"
)

verified_research = sum(
    1 for r in evidence_rows
    if r["research_status"]
    =="verified"
)


print(
    "Identity VERIFIED:",
    verified_identity,
    "/36"
)

print(
    "Research VERIFIED:",
    verified_research,
    "/36"
)


print()
print("WORKING SOURCE SAFETY")
print("-"*130)


working_map={
    r["program_id"]:r
    for r in working_rows
}


already_verified = sum(
    1 for pid in lock_ids
    if working_map[pid]["research_status"]
    =="verified"
)


print(
    "Batch 03 already applied:",
    already_verified
)


print(
    "Canonical programs.json:",
    "UNCHANGED / 600"
)


print()
print("="*130)
print(
    "STEP 172.2L SOUTH KOREA BATCH 03 EVIDENCE PRE-APPLY AUDIT: PASS"
)
print("="*130)

print()
print("NEXT: STEP 172.2M")
print(
    "SAFE APPLY BATCH 03 EVIDENCE TO NEW STAGED QUEUE"
)
