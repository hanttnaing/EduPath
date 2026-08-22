from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path.cwd()
PLANNING = ROOT / "planning"

ORIGINAL_QUEUE = (
    PLANNING
    / "27_south_korea_program_research_queue.csv"
)

BATCH01_LOCK = (
    PLANNING
    / "28_south_korea_program_research_batch01_lock.csv"
)

BATCH01_EVIDENCE = (
    PLANNING
    / "29_south_korea_program_research_batch01_evidence.csv"
)

STAGED_QUEUE = (
    PLANNING
    / "30_south_korea_program_research_queue_batch01_applied.csv"
)

BATCH02_LOCK = (
    PLANNING
    / "31_south_korea_program_research_batch02_lock.csv"
)

TEMP = (
    PLANNING
    / "31_south_korea_program_research_batch02_lock.tmp.csv"
)

CANONICAL = (
    ROOT
    / "data"
    / "cleaned"
    / "programs.json"
)


EXPECTED_ORIGINAL_QUEUE_SHA = (
    "94657aa0d191c4b483cdc5e170f142266"
    "b96b2fecae4e3a0c8cf4367c28848dc"
)

EXPECTED_BATCH01_LOCK_SHA = (
    "904a187bbda3225aac522c7cc07368b1"
    "f2a257b6695d965a44e066e0b61a53ab"
)

EXPECTED_BATCH01_EVIDENCE_SHA = (
    "cbe859fc5259f51889f949222fd48d58"
    "be85225782b8126dc7f359a2689fa708"
)

EXPECTED_STAGED_QUEUE_SHA = (
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

BATCH02_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(37, 73)
]

BATCH02_ID_SET = set(BATCH02_IDS)

EXPECTED_BATCH02_PARENTS = {
    f"uni_kr_{i:03d}"
    for i in range(13, 25)
}


checks = []


def record(label, passed, detail=""):
    checks.append(
        (
            label,
            bool(passed),
            str(detail),
        )
    )


def text(value):
    if value is None:
        return ""
    return str(value).strip()


def norm(value):
    return text(value).lower()


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.DictReader(f)
        rows = list(reader)
        cols = list(
            reader.fieldnames or []
        )

    return rows, cols


def row_equal(a, b, columns):
    return all(
        text(a.get(col))
        == text(b.get(col))
        for col in columns
    )


print("=" * 138)
print(
    "STEP 172.2E - SOUTH KOREA "
    "BATCH 02 IMMUTABLE LOCK BUILD"
)
print("=" * 138)


# =====================================================================
# REQUIRED FILES
# =====================================================================

required_files = [
    ORIGINAL_QUEUE,
    BATCH01_LOCK,
    BATCH01_EVIDENCE,
    STAGED_QUEUE,
    CANONICAL,
]


for path in required_files:

    record(
        f"{path.name} exists",
        path.exists(),
        (
            str(path.relative_to(ROOT))
            if path.exists()
            else "NOT FOUND"
        ),
    )


if not all(
    path.exists()
    for path in required_files
):

    print()
    print("PRE-WRITE AUDIT")
    print("-" * 138)

    for label, passed, detail in checks:
        print(
            f"{label:<70}: "
            f"{'PASS' if passed else 'FAIL'}"
            f" | {detail}"
        )

    print()
    print("=" * 138)
    print(
        "STEP 172.2E SOUTH KOREA "
        "BATCH 02 LOCK BUILD: FAIL"
    )
    print(
        "STOP: REQUIRED SOURCE FILE MISSING"
    )
    print("=" * 138)

    sys.exit(1)


# =====================================================================
# HASH LOCKS
# =====================================================================

original_sha_before = sha256(
    ORIGINAL_QUEUE
)

batch01_lock_sha_before = sha256(
    BATCH01_LOCK
)

batch01_evidence_sha_before = sha256(
    BATCH01_EVIDENCE
)

staged_sha_before = sha256(
    STAGED_QUEUE
)

canonical_sha_before = sha256(
    CANONICAL
)


record(
    "Original queue SHA256 exact",
    original_sha_before
    == EXPECTED_ORIGINAL_QUEUE_SHA,
    original_sha_before,
)

record(
    "Batch 01 lock SHA256 exact",
    batch01_lock_sha_before
    == EXPECTED_BATCH01_LOCK_SHA,
    batch01_lock_sha_before,
)

record(
    "Batch 01 evidence SHA256 exact",
    batch01_evidence_sha_before
    == EXPECTED_BATCH01_EVIDENCE_SHA,
    batch01_evidence_sha_before,
)

record(
    "Batch 01 staged queue SHA256 exact",
    staged_sha_before
    == EXPECTED_STAGED_QUEUE_SHA,
    staged_sha_before,
)


# =====================================================================
# LOAD STAGED SOURCE
# =====================================================================

staged_rows, staged_cols = load_csv(
    STAGED_QUEUE
)

original_rows, original_cols = load_csv(
    ORIGINAL_QUEUE
)


record(
    "Staged queue rows = 150",
    len(staged_rows) == 150,
    len(staged_rows),
)

record(
    "Staged queue schema exact 31 columns",
    staged_cols == EXPECTED_COLUMNS,
    len(staged_cols),
)

record(
    "Original queue rows = 150",
    len(original_rows) == 150,
    len(original_rows),
)

record(
    "Original queue schema exact 31 columns",
    original_cols == EXPECTED_COLUMNS,
    len(original_cols),
)


staged_ids = [
    text(row.get("program_id"))
    for row in staged_rows
]

expected_all_ids = [
    f"prog_kr_{i:03d}"
    for i in range(1, 151)
]


record(
    "Staged programme IDs exact",
    staged_ids == expected_all_ids,
    (
        f"{staged_ids[0]} -> {staged_ids[-1]}"
        if staged_ids
        else "EMPTY"
    ),
)


staged_map = {
    text(row["program_id"]): row
    for row in staged_rows
}

original_map = {
    text(row["program_id"]): row
    for row in original_rows
}


# =====================================================================
# VERIFY BATCH 01 STILL APPLIED
# =====================================================================

batch01_verified_identity = {
    pid
    for pid in BATCH01_IDS
    if norm(
        staged_map[
            pid
        ].get(
            "programme_identity_status"
        )
    )
    == "verified"
}

batch01_verified_research = {
    pid
    for pid in BATCH01_IDS
    if norm(
        staged_map[
            pid
        ].get(
            "research_status"
        )
    )
    == "verified"
}


record(
    "Batch 01 identity remains VERIFIED 36 / 36",
    batch01_verified_identity
    == set(BATCH01_IDS),
    len(batch01_verified_identity),
)

record(
    "Batch 01 research remains VERIFIED 36 / 36",
    batch01_verified_research
    == set(BATCH01_IDS),
    len(batch01_verified_research),
)


# =====================================================================
# VERIFY BATCH 02 STILL EXACTLY MATCHES ORIGINAL QUEUE
#
# Batch 02 has not been researched yet.
# Therefore its 36 rows must still be exact source rows.
# =====================================================================

batch02_source_mismatches = []


for pid in BATCH02_IDS:

    if pid not in staged_map:
        batch02_source_mismatches.append(
            f"{pid}:missing-staged"
        )
        continue

    if pid not in original_map:
        batch02_source_mismatches.append(
            f"{pid}:missing-original"
        )
        continue

    for column in EXPECTED_COLUMNS:

        if text(
            staged_map[
                pid
            ].get(column)
        ) != text(
            original_map[
                pid
            ].get(column)
        ):

            batch02_source_mismatches.append(
                f"{pid}:{column}"
            )


record(
    "Batch 02 rows unchanged from original queue",
    not batch02_source_mismatches,
    (
        "36 / 36"
        if not batch02_source_mismatches
        else ", ".join(
            batch02_source_mismatches[:15]
        )
    ),
)


# =====================================================================
# BATCH 02 MUST NOT ALREADY BE VERIFIED
# =====================================================================

batch02_research_verified = [
    pid
    for pid in BATCH02_IDS
    if norm(
        staged_map[
            pid
        ].get(
            "research_status"
        )
    )
    == "verified"
]

batch02_identity_verified = [
    pid
    for pid in BATCH02_IDS
    if norm(
        staged_map[
            pid
        ].get(
            "programme_identity_status"
        )
    )
    == "verified"
]


record(
    "Batch 02 has no VERIFIED research rows",
    not batch02_research_verified,
    (
        "0"
        if not batch02_research_verified
        else ", ".join(
            batch02_research_verified
        )
    ),
)

record(
    "Batch 02 has no VERIFIED identity rows",
    not batch02_identity_verified,
    (
        "0"
        if not batch02_identity_verified
        else ", ".join(
            batch02_identity_verified
        )
    ),
)


# =====================================================================
# SELECT BATCH 02
# =====================================================================

batch02_rows = [
    {
        column: text(
            staged_map[
                pid
            ].get(column)
        )
        for column in EXPECTED_COLUMNS
    }
    for pid in BATCH02_IDS
]


selected_ids = [
    text(row.get("program_id"))
    for row in batch02_rows
]


record(
    "Selected Batch 02 rows = 36",
    len(batch02_rows) == 36,
    len(batch02_rows),
)

record(
    "Selected Batch 02 IDs exact/order exact",
    selected_ids == BATCH02_IDS,
    (
        f"{selected_ids[0]} -> {selected_ids[-1]}"
        if selected_ids
        else "EMPTY"
    ),
)


# =====================================================================
# PARENT UNIVERSITY STRUCTURE
# =====================================================================

parent_counts = Counter(
    text(
        row.get("university_id")
    )
    for row in batch02_rows
)


record(
    "Batch 02 parent universities exact = 12",
    set(parent_counts)
    == EXPECTED_BATCH02_PARENTS,
    len(parent_counts),
)


record(
    "Batch 02 exactly 3 programmes per parent",
    (
        set(parent_counts)
        == EXPECTED_BATCH02_PARENTS
        and all(
            parent_counts[parent] == 3
            for parent
            in EXPECTED_BATCH02_PARENTS
        )
    ),
    (
        f"{sum(parent_counts[p] == 3 for p in EXPECTED_BATCH02_PARENTS)} / 12"
    ),
)


slots_by_parent = defaultdict(set)


for row in batch02_rows:

    slots_by_parent[
        text(
            row.get(
                "university_id"
            )
        )
    ].add(
        text(
            row.get(
                "program_slot"
            )
        )
    )


bad_slots = [
    parent
    for parent
    in sorted(
        EXPECTED_BATCH02_PARENTS
    )
    if slots_by_parent[
        parent
    ]
    != {"1", "2", "3"}
]


record(
    "Batch 02 parent slots exact 1 / 2 / 3",
    not bad_slots,
    (
        "12 / 12"
        if not bad_slots
        else ", ".join(bad_slots)
    ),
)


# =====================================================================
# CANONICAL LOCK
# =====================================================================

with CANONICAL.open(
    "r",
    encoding="utf-8-sig",
) as f:

    canonical_rows = json.load(f)


record(
    "Canonical programmes = 600",
    (
        isinstance(
            canonical_rows,
            list,
        )
        and len(canonical_rows) == 600
    ),
    (
        len(canonical_rows)
        if isinstance(
            canonical_rows,
            list,
        )
        else "NOT A LIST"
    ),
)


canonical_kr_ids = []


if isinstance(canonical_rows, list):

    for row in canonical_rows:

        if not isinstance(row, dict):
            continue

        pid = text(
            row.get(
                "program_id",
                row.get(
                    "programme_id",
                    "",
                ),
            )
        )

        if pid.startswith(
            "prog_kr_"
        ):

            canonical_kr_ids.append(pid)


record(
    "South Korea canonical programmes = 0",
    len(canonical_kr_ids) == 0,
    len(canonical_kr_ids),
)


# =====================================================================
# PRE-WRITE GATE
# =====================================================================

print()
print("PRE-WRITE BATCH 02 LOCK AUDIT")
print("-" * 138)


for label, passed, detail in checks:

    print(
        f"{label:<70}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


failed = [
    (label, detail)
    for label, passed, detail
    in checks
    if not passed
]


if failed:

    print()
    print("=" * 138)
    print(
        "STEP 172.2E SOUTH KOREA "
        "BATCH 02 LOCK BUILD: FAIL"
    )

    print(
        f"FAILED CHECKS: {len(failed)}"
    )

    for label, detail in failed:
        print(
            f" - {label}: {detail}"
        )

    print()
    print(
        "STOP: BATCH 02 LOCK NOT CREATED"
    )
    print(
        "DO NOT RESEARCH BATCH 02 YET"
    )
    print(
        "DO NOT WRITE programs.json"
    )
    print(
        "DO NOT WRITE MONGODB"
    )
    print("=" * 138)

    sys.exit(1)


# =====================================================================
# BUILD TEMP LOCK FILE
# =====================================================================

if TEMP.exists():
    TEMP.unlink()


with TEMP.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=EXPECTED_COLUMNS,
        lineterminator="\n",
    )

    writer.writeheader()
    writer.writerows(
        batch02_rows
    )


candidate_sha = sha256(
    TEMP
)


# =====================================================================
# SAFE OUTPUT POLICY
# =====================================================================

created_new = False
existing_identical = False


if BATCH02_LOCK.exists():

    existing_sha = sha256(
        BATCH02_LOCK
    )

    if existing_sha == candidate_sha:

        existing_identical = True
        TEMP.unlink()

    else:

        TEMP.unlink()

        print()
        print("=" * 138)
        print(
            "STEP 172.2E SOUTH KOREA "
            "BATCH 02 LOCK BUILD: FAIL"
        )
        print()
        print(
            "A DIFFERENT BATCH 02 LOCK "
            "ALREADY EXISTS"
        )
        print(
            str(
                BATCH02_LOCK.relative_to(
                    ROOT
                )
            )
        )
        print(
            f"Existing SHA256 : {existing_sha}"
        )
        print(
            f"Candidate SHA256: {candidate_sha}"
        )
        print()
        print(
            "NO FILE WAS OVERWRITTEN"
        )
        print(
            "DO NOT RESEARCH UNTIL "
            "THE LOCK CONFLICT IS RESOLVED"
        )
        print("=" * 138)

        sys.exit(1)

else:

    os.replace(
        TEMP,
        BATCH02_LOCK,
    )

    created_new = True


# =====================================================================
# POST-WRITE VERIFICATION
# =====================================================================

post_checks = []


def post_record(label, passed, detail=""):

    post_checks.append(
        (
            label,
            bool(passed),
            str(detail),
        )
    )


batch02_sha = sha256(
    BATCH02_LOCK
)

written_rows, written_cols = load_csv(
    BATCH02_LOCK
)


post_record(
    "Batch 02 lock output exists",
    BATCH02_LOCK.exists(),
    str(
        BATCH02_LOCK.relative_to(
            ROOT
        )
    ),
)

post_record(
    "Batch 02 lock SHA matches candidate",
    batch02_sha == candidate_sha,
    batch02_sha,
)

post_record(
    "Written Batch 02 columns = 31",
    written_cols == EXPECTED_COLUMNS,
    len(written_cols),
)

post_record(
    "Written Batch 02 rows = 36",
    len(written_rows) == 36,
    len(written_rows),
)


written_ids = [
    text(
        row.get("program_id")
    )
    for row in written_rows
]


post_record(
    "Written Batch 02 IDs exact",
    written_ids == BATCH02_IDS,
    (
        f"{written_ids[0]} -> {written_ids[-1]}"
        if written_ids
        else "EMPTY"
    ),
)


written_map = {
    text(row["program_id"]): row
    for row in written_rows
}


written_source_mismatches = []


for pid in BATCH02_IDS:

    for column in EXPECTED_COLUMNS:

        if text(
            written_map[
                pid
            ].get(column)
        ) != text(
            staged_map[
                pid
            ].get(column)
        ):

            written_source_mismatches.append(
                f"{pid}:{column}"
            )


post_record(
    "Written Batch 02 exact staged-source snapshot",
    not written_source_mismatches,
    (
        "36 / 36"
        if not written_source_mismatches
        else ", ".join(
            written_source_mismatches[:15]
        )
    ),
)


# =====================================================================
# SOURCE FILES MUST REMAIN UNCHANGED
# =====================================================================

original_sha_after = sha256(
    ORIGINAL_QUEUE
)

batch01_lock_sha_after = sha256(
    BATCH01_LOCK
)

batch01_evidence_sha_after = sha256(
    BATCH01_EVIDENCE
)

staged_sha_after = sha256(
    STAGED_QUEUE
)

canonical_sha_after = sha256(
    CANONICAL
)


post_record(
    "Original queue unchanged",
    (
        original_sha_after
        == original_sha_before
        == EXPECTED_ORIGINAL_QUEUE_SHA
    ),
    original_sha_after,
)

post_record(
    "Batch 01 lock unchanged",
    (
        batch01_lock_sha_after
        == batch01_lock_sha_before
        == EXPECTED_BATCH01_LOCK_SHA
    ),
    batch01_lock_sha_after,
)

post_record(
    "Batch 01 evidence unchanged",
    (
        batch01_evidence_sha_after
        == batch01_evidence_sha_before
        == EXPECTED_BATCH01_EVIDENCE_SHA
    ),
    batch01_evidence_sha_after,
)

post_record(
    "Batch 01 staged queue unchanged",
    (
        staged_sha_after
        == staged_sha_before
        == EXPECTED_STAGED_QUEUE_SHA
    ),
    staged_sha_after,
)

post_record(
    "Canonical programs.json unchanged",
    canonical_sha_after
    == canonical_sha_before,
    canonical_sha_after,
)


print()
print("POST-WRITE BATCH 02 LOCK AUDIT")
print("-" * 138)


for label, passed, detail in post_checks:

    print(
        f"{label:<70}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


post_failed = [
    (label, detail)
    for label, passed, detail
    in post_checks
    if not passed
]


if post_failed:

    if created_new and BATCH02_LOCK.exists():
        BATCH02_LOCK.unlink()

    print()
    print("=" * 138)
    print(
        "STEP 172.2E SOUTH KOREA "
        "BATCH 02 LOCK BUILD: FAIL"
    )

    print(
        f"FAILED POST-WRITE CHECKS: "
        f"{len(post_failed)}"
    )

    for label, detail in post_failed:
        print(
            f" - {label}: {detail}"
        )

    if created_new:
        print(
            "INVALID NEW LOCK FILE REMOVED"
        )

    print(
        "DO NOT RESEARCH BATCH 02"
    )
    print(
        "DO NOT WRITE programs.json"
    )
    print(
        "DO NOT WRITE MONGODB"
    )
    print("=" * 138)

    sys.exit(1)


# =====================================================================
# BATCH 02 SUMMARY
# =====================================================================

print()
print("=" * 138)
print(
    "STEP 172.2E SOUTH KOREA "
    "BATCH 02 IMMUTABLE LOCK BUILD: PASS"
)
print()

print(
    "BATCH 02 LOCK FILE               : "
    "planning\\31_south_korea_program_research_batch02_lock.csv"
)

print(
    f"BATCH 02 LOCK SHA256             : "
    f"{batch02_sha}"
)

print(
    "BATCH 02 PROGRAMMES              : 36"
)

print(
    "BATCH 02 UNIVERSITIES            : 12"
)

print(
    "BATCH 02 PROGRAMME IDS           : "
    "prog_kr_037 -> prog_kr_072"
)

print(
    "BATCH 02 UNIVERSITY IDS          : "
    "uni_kr_013 -> uni_kr_024"
)

print(
    "PROGRAMMES PER UNIVERSITY        : 3"
)

print(
    "BATCH 02 RESEARCH VERIFIED       : 0"
)

print(
    "BATCH 02 IDENTITY VERIFIED       : 0"
)

print()

print(
    "WORKING SOURCE QUEUE             : "
    "planning\\30_south_korea_program_research_queue_batch01_applied.csv"
)

print(
    f"WORKING SOURCE SHA256            : "
    f"{EXPECTED_STAGED_QUEUE_SHA}"
)

print(
    "BATCH 01 VERIFIED                : 36 / 36"
)

print(
    "REMAINING AFTER BATCH 02         : 78 programmes"
)

print()

print(
    "ORIGINAL 150-ROW QUEUE           : UNCHANGED"
)

print(
    "BATCH 01 LOCK                    : UNCHANGED"
)

print(
    "BATCH 01 EVIDENCE                : UNCHANGED"
)

print(
    "BATCH 01 STAGED QUEUE            : UNCHANGED"
)

print(
    "CANONICAL programs.json          : UNCHANGED / 600"
)

print(
    "SOUTH KOREA CANONICAL PROGRAMMES : 0"
)

print(
    "MONGODB WRITE PERFORMED          : False"
)

print()

if existing_identical:
    print(
        "BATCH 02 LOCK STATUS            : "
        "EXISTING IDENTICAL FILE REUSED"
    )
else:
    print(
        "BATCH 02 LOCK STATUS            : "
        "NEW IMMUTABLE LOCK CREATED"
    )

print()
print(
    "NEXT: STEP 172.2F"
)

print(
    "SOUTH KOREA BATCH 02 "
    "OFFICIAL-SOURCE RESEARCH "
    "EVIDENCE BUILD"
)

print("=" * 138)
