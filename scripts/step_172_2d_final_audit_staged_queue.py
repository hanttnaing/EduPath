from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
PLANNING = ROOT / "planning"

SOURCE_QUEUE = PLANNING / "27_south_korea_program_research_queue.csv"
BATCH01_LOCK = PLANNING / "28_south_korea_program_research_batch01_lock.csv"
BATCH01_EVIDENCE = PLANNING / "29_south_korea_program_research_batch01_evidence.csv"
STAGED_QUEUE = PLANNING / "30_south_korea_program_research_queue_batch01_applied.csv"
CANONICAL = ROOT / "data" / "cleaned" / "programs.json"


EXPECTED_SOURCE_SHA = (
    "94657aa0d191c4b483cdc5e170f142266"
    "b96b2fecae4e3a0c8cf4367c28848dc"
)

EXPECTED_BATCH01_LOCK_SHA = (
    "904a187bbda3225aac522c7cc07368b1"
    "f2a257b6695d965a44e066e0b61a53ab"
)

EXPECTED_EVIDENCE_SHA = (
    "cbe859fc5259f51889f949222fd48d58"
    "be85225782b8126dc7f359a2689fa708"
)

EXPECTED_STAGED_SHA = (
    "0c23f17369fd1f774838736b0e21fe617"
    "bd1ef804b0bc98f05c723158435075a"
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

BATCH01_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(1, 37)
]

NON_BATCH01_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(37, 151)
]

EXPECTED_ALL_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(1, 151)
]

EXPECTED_UNKNOWN_IDS = {
    "prog_kr_028",
    "prog_kr_029",
    "prog_kr_030",
}

checks = []


def record(label, passed, detail=""):
    checks.append((label, bool(passed), str(detail)))


def text(value):
    if value is None:
        return ""
    return str(value).strip()


def norm(value):
    return text(value).lower()


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        cols = list(reader.fieldnames or [])
    return rows, cols


def row_equal(left, right, columns):
    return all(
        text(left.get(col)) == text(right.get(col))
        for col in columns
    )


print("=" * 138)
print("STEP 172.2D - SOUTH KOREA BATCH 01 STAGED QUEUE FINAL AUDIT")
print("=" * 138)


required_files = [
    SOURCE_QUEUE,
    BATCH01_LOCK,
    BATCH01_EVIDENCE,
    STAGED_QUEUE,
    CANONICAL,
]

for path in required_files:
    record(
        f"{path.name} exists",
        path.exists(),
        str(path.relative_to(ROOT)) if path.exists() else "NOT FOUND",
    )

if not all(path.exists() for path in required_files):
    print()
    print("AUDIT RESULTS")
    print("-" * 138)
    for label, passed, detail in checks:
        print(f"{label:<68}: {'PASS' if passed else 'FAIL'} | {detail}")
    print()
    print("=" * 138)
    print("STEP 172.2D SOUTH KOREA BATCH 01 STAGED QUEUE FINAL AUDIT: FAIL")
    print("STOP: REQUIRED FILE MISSING")
    print("=" * 138)
    sys.exit(1)


source_sha = sha256(SOURCE_QUEUE)
lock_sha = sha256(BATCH01_LOCK)
evidence_sha = sha256(BATCH01_EVIDENCE)
staged_sha = sha256(STAGED_QUEUE)
canonical_sha_before = sha256(CANONICAL)

record("Source queue SHA256 exact", source_sha == EXPECTED_SOURCE_SHA, source_sha)
record("Batch 01 lock SHA256 exact", lock_sha == EXPECTED_BATCH01_LOCK_SHA, lock_sha)
record("Batch 01 evidence SHA256 exact", evidence_sha == EXPECTED_EVIDENCE_SHA, evidence_sha)
record("Staged queue SHA256 exact", staged_sha == EXPECTED_STAGED_SHA, staged_sha)

source_rows, source_cols = load_csv(SOURCE_QUEUE)
lock_rows, lock_cols = load_csv(BATCH01_LOCK)
evidence_rows, evidence_cols = load_csv(BATCH01_EVIDENCE)
staged_rows, staged_cols = load_csv(STAGED_QUEUE)

record("Source queue rows = 150", len(source_rows) == 150, len(source_rows))
record("Batch 01 lock rows = 36", len(lock_rows) == 36, len(lock_rows))
record("Batch 01 evidence rows = 36", len(evidence_rows) == 36, len(evidence_rows))
record("Staged queue rows = 150", len(staged_rows) == 150, len(staged_rows))

record("Source queue columns = 31", source_cols == EXPECTED_COLUMNS, len(source_cols))
record("Batch 01 lock columns = 31", lock_cols == EXPECTED_COLUMNS, len(lock_cols))
record("Batch 01 evidence columns = 31", evidence_cols == EXPECTED_COLUMNS, len(evidence_cols))
record("Staged queue columns = 31", staged_cols == EXPECTED_COLUMNS, len(staged_cols))

source_ids = [text(r.get("program_id")) for r in source_rows]
lock_ids = [text(r.get("program_id")) for r in lock_rows]
evidence_ids = [text(r.get("program_id")) for r in evidence_rows]
staged_ids = [text(r.get("program_id")) for r in staged_rows]

record("Source queue IDs exact", source_ids == EXPECTED_ALL_IDS, f"{source_ids[0]} -> {source_ids[-1]}")
record("Batch 01 lock IDs exact", lock_ids == BATCH01_IDS, f"{lock_ids[0]} -> {lock_ids[-1]}")
record("Batch 01 evidence IDs exact", evidence_ids == BATCH01_IDS, f"{evidence_ids[0]} -> {evidence_ids[-1]}")
record("Staged queue IDs exact", staged_ids == EXPECTED_ALL_IDS, f"{staged_ids[0]} -> {staged_ids[-1]}")

source_map = {text(r["program_id"]): r for r in source_rows}
lock_map = {text(r["program_id"]): r for r in lock_rows}
evidence_map = {text(r["program_id"]): r for r in evidence_rows}
staged_map = {text(r["program_id"]): r for r in staged_rows}

lock_vs_source = []
for pid in BATCH01_IDS:
    if not row_equal(lock_map[pid], source_map[pid], EXPECTED_COLUMNS):
        lock_vs_source.append(pid)

record(
    "Batch 01 lock remains exact source snapshot",
    not lock_vs_source,
    "mismatches=0" if not lock_vs_source else ", ".join(lock_vs_source[:10]),
)

batch01_vs_evidence = []
for pid in BATCH01_IDS:
    if not row_equal(staged_map[pid], evidence_map[pid], EXPECTED_COLUMNS):
        batch01_vs_evidence.append(pid)

record(
    "Staged Batch 01 rows exactly equal evidence",
    not batch01_vs_evidence,
    "36 / 36" if not batch01_vs_evidence else ", ".join(batch01_vs_evidence[:10]),
)

non_batch_preserved = []
for pid in NON_BATCH01_IDS:
    if not row_equal(staged_map[pid], source_map[pid], EXPECTED_COLUMNS):
        non_batch_preserved.append(pid)

record(
    "Staged non-Batch rows unchanged from source",
    not non_batch_preserved,
    "114 / 114" if not non_batch_preserved else ", ".join(non_batch_preserved[:10]),
)

verified_identity_ids = {
    text(r.get("program_id"))
    for r in staged_rows
    if norm(r.get("programme_identity_status")) == "verified"
}

verified_research_ids = {
    text(r.get("program_id"))
    for r in staged_rows
    if norm(r.get("research_status")) == "verified"
}

record(
    "Verified identity rows exact = 36",
    verified_identity_ids == set(BATCH01_IDS),
    len(verified_identity_ids),
)

record(
    "Verified research rows exact = 36",
    verified_research_ids == set(BATCH01_IDS),
    len(verified_research_ids),
)

batch01_international_counts = Counter(
    norm(staged_map[pid].get("international_applicants_status"))
    for pid in BATCH01_IDS
)

record(
    "Batch 01 international = 33 verified_yes / 3 unknown",
    batch01_international_counts == Counter({
        "verified_yes": 33,
        "unknown": 3,
    }),
    dict(batch01_international_counts),
)

batch01_unknown_ids = {
    pid
    for pid in BATCH01_IDS
    if norm(staged_map[pid].get("international_applicants_status")) == "unknown"
}

record(
    "Batch 01 unknown IDs exact",
    batch01_unknown_ids == EXPECTED_UNKNOWN_IDS,
    ", ".join(sorted(batch01_unknown_ids)),
)

batch01_degree_counts = Counter(
    norm(staged_map[pid].get("degree_level"))
    for pid in BATCH01_IDS
)

record(
    "Batch 01 degrees = 27 bachelor / 9 master",
    batch01_degree_counts == Counter({
        "bachelor": 27,
        "master": 9,
    }),
    dict(batch01_degree_counts),
)

with CANONICAL.open("r", encoding="utf-8-sig") as f:
    canonical_rows = json.load(f)

record(
    "Canonical programmes remain 600",
    isinstance(canonical_rows, list) and len(canonical_rows) == 600,
    len(canonical_rows) if isinstance(canonical_rows, list) else "NOT A LIST",
)

canonical_kr_ids = []

if isinstance(canonical_rows, list):
    for row in canonical_rows:
        if not isinstance(row, dict):
            continue
        pid = text(row.get("program_id", row.get("programme_id", "")))
        if pid.startswith("prog_kr_"):
            canonical_kr_ids.append(pid)

record(
    "South Korea canonical programmes remain 0",
    len(canonical_kr_ids) == 0,
    len(canonical_kr_ids),
)

canonical_sha_after = sha256(CANONICAL)

record(
    "Canonical programs.json unchanged during audit",
    canonical_sha_after == canonical_sha_before,
    canonical_sha_after,
)

print()
print("AUDIT RESULTS")
print("-" * 138)

for label, passed, detail in checks:
    print(
        f"{label:<68}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (f" | {detail}" if detail else "")
    )

failed = [(label, detail) for label, passed, detail in checks if not passed]

print()
print("=" * 138)

if failed:
    print("STEP 172.2D SOUTH KOREA BATCH 01 STAGED QUEUE FINAL AUDIT: FAIL")
    print(f"FAILED CHECKS: {len(failed)}")
    for label, detail in failed:
        print(f" - {label}: {detail}")
    print()
    print("STOP: DO NOT LOCK THE NEXT BATCH")
    print("DO NOT WRITE programs.json")
    print("DO NOT WRITE MONGODB")
    print("=" * 138)
    sys.exit(1)

print("STEP 172.2D SOUTH KOREA BATCH 01 STAGED QUEUE FINAL AUDIT: PASS")
print()
print("STAGED QUEUE FILE                : planning\\30_south_korea_program_research_queue_batch01_applied.csv")
print(f"STAGED QUEUE SHA256              : {staged_sha}")
print("STAGED QUEUE ROWS                : 150")
print("STAGED QUEUE COLUMNS             : 31")
print("BATCH 01 VERIFIED ROWS           : 36")
print("NON-BATCH ROWS PRESERVED         : 114")
print("PROGRAMME IDENTITIES VERIFIED    : 36 / 36")
print("RESEARCH STATUS VERIFIED         : 36 / 36")
print(f"INTERNATIONAL VERIFIED_YES       : {batch01_international_counts.get('verified_yes', 0)}")
print(f"INTERNATIONAL UNKNOWN            : {batch01_international_counts.get('unknown', 0)}")
print("UNKNOWN IDS                      : prog_kr_028, prog_kr_029, prog_kr_030")
print(f"DEGREE LEVELS                    : {batch01_degree_counts.get('bachelor', 0)} BACHELOR / {batch01_degree_counts.get('master', 0)} MASTER")
print()
print("SOURCE 150-ROW QUEUE             : UNCHANGED")
print("BATCH 01 LOCK                    : UNCHANGED")
print("BATCH 01 EVIDENCE                : UNCHANGED")
print("CANONICAL programs.json          : UNCHANGED / 600")
print("SOUTH KOREA CANONICAL PROGRAMMES : 0")
print("MONGODB WRITE PERFORMED          : False")
print()
print("NEXT: STEP 172.2E")
print("LOCK SOUTH KOREA BATCH 02 FROM THE STAGED 150-ROW QUEUE")
print("=" * 138)
