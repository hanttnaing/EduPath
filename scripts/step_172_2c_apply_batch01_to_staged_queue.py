from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
PLANNING = ROOT / "planning"

QUEUE = (
    PLANNING
    / "27_south_korea_program_research_queue.csv"
)

BATCH = (
    PLANNING
    / "28_south_korea_program_research_batch01_lock.csv"
)

EVIDENCE = (
    PLANNING
    / "29_south_korea_program_research_batch01_evidence.csv"
)

STAGED = (
    PLANNING
    / "30_south_korea_program_research_queue_batch01_applied.csv"
)

TEMP = (
    PLANNING
    / "30_south_korea_program_research_queue_batch01_applied.tmp.csv"
)

CANONICAL = (
    ROOT
    / "data"
    / "cleaned"
    / "programs.json"
)


EXPECTED_QUEUE_SHA = (
    "94657aa0d191c4b483cdc5e170f142266"
    "b96b2fecae4e3a0c8cf4367c28848dc"
)

EXPECTED_BATCH_SHA = (
    "904a187bbda3225aac522c7cc07368b1"
    "f2a257b6695d965a44e066e0b61a53ab"
)

EXPECTED_EVIDENCE_SHA = (
    "cbe859fc5259f51889f949222fd48d58"
    "be85225782b8126dc7f359a2689fa708"
)


BATCH_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(1, 37)
]

BATCH_ID_SET = set(BATCH_IDS)

NON_BATCH_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(37, 151)
]

EXPECTED_UNKNOWN_IDS = {
    "prog_kr_028",
    "prog_kr_029",
    "prog_kr_030",
}


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


IMMUTABLE_SEED_FIELDS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
]


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
        cols = list(reader.fieldnames or [])

    return rows, cols


def row_equal(left, right, columns):
    return all(
        text(left.get(column))
        == text(right.get(column))
        for column in columns
    )


def fail_before_write():
    print()
    print("=" * 138)
    print(
        "STEP 172.2C SOUTH KOREA "
        "BATCH 01 SAFE STAGING APPLY: FAIL"
    )
    print()
    print(
        "STOP: STAGED QUEUE NOT CREATED"
    )
    print(
        "ORIGINAL 150-ROW QUEUE MUST REMAIN UNCHANGED"
    )
    print(
        "DO NOT WRITE programs.json"
    )
    print(
        "DO NOT WRITE MONGODB"
    )
    print("=" * 138)
    sys.exit(1)


print("=" * 138)
print(
    "STEP 172.2C - SOUTH KOREA BATCH 01 "
    "SAFE EVIDENCE APPLY TO STAGED 150-ROW QUEUE"
)
print("=" * 138)


# ================================================================
# PRE-WRITE SOURCE LOCK
# ================================================================

required_files = [
    QUEUE,
    BATCH,
    EVIDENCE,
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


if not all(path.exists() for path in required_files):

    for label, passed, detail in checks:
        print(
            f"{label:<65}: "
            f"{'PASS' if passed else 'FAIL'}"
            f" | {detail}"
        )

    fail_before_write()


queue_sha_before = sha256(QUEUE)
batch_sha_before = sha256(BATCH)
evidence_sha_before = sha256(EVIDENCE)
canonical_sha_before = sha256(CANONICAL)


record(
    "Source queue SHA256 lock",
    queue_sha_before == EXPECTED_QUEUE_SHA,
    queue_sha_before,
)

record(
    "Batch 01 SHA256 lock",
    batch_sha_before == EXPECTED_BATCH_SHA,
    batch_sha_before,
)

record(
    "Evidence SHA256 lock",
    evidence_sha_before == EXPECTED_EVIDENCE_SHA,
    evidence_sha_before,
)


queue_rows, queue_cols = load_csv(QUEUE)
batch_rows, batch_cols = load_csv(BATCH)
evidence_rows, evidence_cols = load_csv(EVIDENCE)


record(
    "Source queue rows = 150",
    len(queue_rows) == 150,
    len(queue_rows),
)

record(
    "Batch lock rows = 36",
    len(batch_rows) == 36,
    len(batch_rows),
)

record(
    "Evidence rows = 36",
    len(evidence_rows) == 36,
    len(evidence_rows),
)

record(
    "Source queue schema exact 31 columns",
    queue_cols == EXPECTED_COLUMNS,
    len(queue_cols),
)

record(
    "Batch lock schema exact 31 columns",
    batch_cols == EXPECTED_COLUMNS,
    len(batch_cols),
)

record(
    "Evidence schema exact 31 columns",
    evidence_cols == EXPECTED_COLUMNS,
    len(evidence_cols),
)


queue_ids = [
    text(row.get("program_id"))
    for row in queue_rows
]

batch_ids = [
    text(row.get("program_id"))
    for row in batch_rows
]

evidence_ids = [
    text(row.get("program_id"))
    for row in evidence_rows
]


expected_queue_ids = [
    f"prog_kr_{i:03d}"
    for i in range(1, 151)
]


record(
    "Source queue IDs exact prog_kr_001 -> prog_kr_150",
    queue_ids == expected_queue_ids,
    (
        f"{queue_ids[0]} -> {queue_ids[-1]}"
        if queue_ids
        else "EMPTY"
    ),
)

record(
    "Batch lock IDs exact prog_kr_001 -> prog_kr_036",
    batch_ids == BATCH_IDS,
    (
        f"{batch_ids[0]} -> {batch_ids[-1]}"
        if batch_ids
        else "EMPTY"
    ),
)

record(
    "Evidence IDs exact prog_kr_001 -> prog_kr_036",
    evidence_ids == BATCH_IDS,
    (
        f"{evidence_ids[0]} -> {evidence_ids[-1]}"
        if evidence_ids
        else "EMPTY"
    ),
)


queue_map = {
    text(row["program_id"]): row
    for row in queue_rows
}

batch_map = {
    text(row["program_id"]): row
    for row in batch_rows
}

evidence_map = {
    text(row["program_id"]): row
    for row in evidence_rows
}


# ================================================================
# BATCH LOCK MUST STILL MATCH SOURCE QUEUE EXACTLY
# ================================================================

batch_lock_mismatches = []

for program_id in BATCH_IDS:

    qrow = queue_map.get(program_id)
    brow = batch_map.get(program_id)

    if qrow is None or brow is None:
        batch_lock_mismatches.append(
            f"{program_id}:missing-row"
        )
        continue

    if not row_equal(
        qrow,
        brow,
        EXPECTED_COLUMNS,
    ):
        for column in EXPECTED_COLUMNS:

            if text(qrow.get(column)) != text(
                brow.get(column)
            ):
                batch_lock_mismatches.append(
                    f"{program_id}:{column}"
                )


record(
    "Batch lock exact snapshot of source queue",
    not batch_lock_mismatches,
    (
        "mismatches=0"
        if not batch_lock_mismatches
        else ", ".join(
            batch_lock_mismatches[:15]
        )
    ),
)


# ================================================================
# EVIDENCE MUST PRESERVE SEED IDENTITY
# ================================================================

seed_mismatches = []

for program_id in BATCH_IDS:

    qrow = queue_map.get(program_id)
    erow = evidence_map.get(program_id)

    if qrow is None or erow is None:
        seed_mismatches.append(
            f"{program_id}:missing-row"
        )
        continue

    for field in IMMUTABLE_SEED_FIELDS:

        if text(qrow.get(field)) != text(
            erow.get(field)
        ):
            seed_mismatches.append(
                f"{program_id}:{field}"
            )


record(
    "Evidence preserves immutable seed identity",
    not seed_mismatches,
    (
        "mismatches=0"
        if not seed_mismatches
        else ", ".join(
            seed_mismatches[:15]
        )
    ),
)


identity_counts = Counter(
    norm(
        row.get(
            "programme_identity_status"
        )
    )
    for row in evidence_rows
)

research_counts = Counter(
    norm(
        row.get(
            "research_status"
        )
    )
    for row in evidence_rows
)

international_counts = Counter(
    norm(
        row.get(
            "international_applicants_status"
        )
    )
    for row in evidence_rows
)


record(
    "Evidence identity VERIFIED = 36",
    identity_counts
    == Counter({"verified": 36}),
    dict(identity_counts),
)

record(
    "Evidence research VERIFIED = 36",
    research_counts
    == Counter({"verified": 36}),
    dict(research_counts),
)

record(
    "International status 33 verified_yes / 3 unknown",
    international_counts
    == Counter({
        "verified_yes": 33,
        "unknown": 3,
    }),
    dict(international_counts),
)


unknown_ids = {
    text(row.get("program_id"))
    for row in evidence_rows
    if norm(
        row.get(
            "international_applicants_status"
        )
    )
    == "unknown"
}


record(
    "Unknown international IDs exact",
    unknown_ids == EXPECTED_UNKNOWN_IDS,
    ", ".join(sorted(unknown_ids)),
)


# ================================================================
# CANONICAL PRE-WRITE LOCK
# ================================================================

with CANONICAL.open(
    "r",
    encoding="utf-8-sig",
) as f:
    canonical_rows_before = json.load(f)


canonical_kr_before = []

if isinstance(
    canonical_rows_before,
    list,
):
    for row in canonical_rows_before:

        if not isinstance(row, dict):
            continue

        program_id = text(
            row.get(
                "program_id",
                row.get("programme_id", ""),
            )
        )

        if program_id.startswith("prog_kr_"):
            canonical_kr_before.append(
                program_id
            )


record(
    "Canonical programmes before staging = 600",
    (
        isinstance(
            canonical_rows_before,
            list,
        )
        and len(
            canonical_rows_before
        )
        == 600
    ),
    (
        len(canonical_rows_before)
        if isinstance(
            canonical_rows_before,
            list,
        )
        else "NOT A LIST"
    ),
)

record(
    "South Korea canonical programmes before staging = 0",
    len(canonical_kr_before) == 0,
    len(canonical_kr_before),
)


# ================================================================
# PRE-WRITE GATE
# ================================================================

prewrite_failed = [
    (label, detail)
    for label, passed, detail in checks
    if not passed
]


print()
print("PRE-WRITE AUDIT")
print("-" * 138)

for label, passed, detail in checks:

    print(
        f"{label:<65}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


if prewrite_failed:
    fail_before_write()


# ================================================================
# BUILD STAGED COPY IN MEMORY
#
# Batch 01 rows:
#     full row comes from verified evidence.
#
# Remaining 114 rows:
#     full row remains from original source queue.
# ================================================================

staged_rows = []

for queue_row in queue_rows:

    program_id = text(
        queue_row.get("program_id")
    )

    if program_id in BATCH_ID_SET:

        evidence_row = evidence_map[
            program_id
        ]

        staged_rows.append({
            column: text(
                evidence_row.get(column)
            )
            for column in EXPECTED_COLUMNS
        })

    else:

        staged_rows.append({
            column: text(
                queue_row.get(column)
            )
            for column in EXPECTED_COLUMNS
        })


staged_ids = [
    text(row.get("program_id"))
    for row in staged_rows
]


build_checks = []


def build_record(label, passed, detail=""):
    build_checks.append(
        (
            label,
            bool(passed),
            str(detail),
        )
    )


build_record(
    "Staged row count = 150",
    len(staged_rows) == 150,
    len(staged_rows),
)

build_record(
    "Staged programme order unchanged",
    staged_ids == queue_ids,
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


batch_apply_mismatches = []

for program_id in BATCH_IDS:

    staged_row = staged_map[
        program_id
    ]

    evidence_row = evidence_map[
        program_id
    ]

    for column in EXPECTED_COLUMNS:

        if text(
            staged_row.get(column)
        ) != text(
            evidence_row.get(column)
        ):
            batch_apply_mismatches.append(
                f"{program_id}:{column}"
            )


build_record(
    "Batch 01 staged rows exactly equal evidence",
    not batch_apply_mismatches,
    (
        "36 / 36"
        if not batch_apply_mismatches
        else ", ".join(
            batch_apply_mismatches[:15]
        )
    ),
)


non_batch_mismatches = []

for program_id in NON_BATCH_IDS:

    staged_row = staged_map[
        program_id
    ]

    queue_row = queue_map[
        program_id
    ]

    for column in EXPECTED_COLUMNS:

        if text(
            staged_row.get(column)
        ) != text(
            queue_row.get(column)
        ):
            non_batch_mismatches.append(
                f"{program_id}:{column}"
            )


build_record(
    "Non-Batch 01 rows unchanged from source queue",
    not non_batch_mismatches,
    (
        "114 / 114"
        if not non_batch_mismatches
        else ", ".join(
            non_batch_mismatches[:15]
        )
    ),
)


staged_researched_ids = {
    text(row.get("program_id"))
    for row in staged_rows
    if norm(
        row.get(
            "research_status"
        )
    )
    == "verified"
}


build_record(
    "Staged VERIFIED research rows exact = 36",
    staged_researched_ids
    == BATCH_ID_SET,
    len(staged_researched_ids),
)


staged_identity_ids = {
    text(row.get("program_id"))
    for row in staged_rows
    if norm(
        row.get(
            "programme_identity_status"
        )
    )
    == "verified"
}


build_record(
    "Staged VERIFIED identity rows exact = 36",
    staged_identity_ids
    == BATCH_ID_SET,
    len(staged_identity_ids),
)


non_batch_verified = [
    program_id
    for program_id in NON_BATCH_IDS
    if norm(
        staged_map[
            program_id
        ].get(
            "research_status"
        )
    )
    == "verified"
]


build_record(
    "No non-Batch 01 rows marked VERIFIED",
    not non_batch_verified,
    (
        "114 / 114 remain outside VERIFIED set"
        if not non_batch_verified
        else ", ".join(
            non_batch_verified[:15]
        )
    ),
)


print()
print("IN-MEMORY STAGING AUDIT")
print("-" * 138)

for label, passed, detail in build_checks:

    print(
        f"{label:<65}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


if any(
    not passed
    for _, passed, _ in build_checks
):
    fail_before_write()


# ================================================================
# WRITE TEMP FILE
# ================================================================

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
        staged_rows
    )


candidate_sha = sha256(TEMP)


# ================================================================
# SAFE OUTPUT RULE
#
# If output already exists:
# - identical hash -> accept existing output
# - different hash -> STOP, never overwrite it
# ================================================================

created_new = False
existing_identical = False


if STAGED.exists():

    existing_sha = sha256(
        STAGED
    )

    if existing_sha == candidate_sha:

        existing_identical = True

        TEMP.unlink()

    else:

        TEMP.unlink()

        print()
        print("=" * 138)
        print(
            "STEP 172.2C SAFE STAGING APPLY: FAIL"
        )
        print()
        print(
            "A DIFFERENT STAGED FILE ALREADY EXISTS:"
        )
        print(
            str(
                STAGED.relative_to(ROOT)
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
            "NO FILE WAS OVERWRITTEN."
        )
        print("=" * 138)

        sys.exit(1)

else:

    os.replace(
        TEMP,
        STAGED,
    )

    created_new = True


# ================================================================
# POST-WRITE AUDIT
# ================================================================

post_checks = []


def post_record(label, passed, detail=""):
    post_checks.append(
        (
            label,
            bool(passed),
            str(detail),
        )
    )


staged_sha = sha256(
    STAGED
)

written_rows, written_cols = load_csv(
    STAGED
)


post_record(
    "Staged output exists",
    STAGED.exists(),
    str(
        STAGED.relative_to(ROOT)
    ),
)

post_record(
    "Written staged SHA256 matches candidate",
    staged_sha == candidate_sha,
    staged_sha,
)

post_record(
    "Written columns = 31",
    written_cols == EXPECTED_COLUMNS,
    len(written_cols),
)

post_record(
    "Written rows = 150",
    len(written_rows) == 150,
    len(written_rows),
)


written_ids = [
    text(row.get("program_id"))
    for row in written_rows
]


post_record(
    "Written programme order exact",
    written_ids == expected_queue_ids,
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


written_batch_mismatches = []

for program_id in BATCH_IDS:

    for column in EXPECTED_COLUMNS:

        if text(
            written_map[
                program_id
            ].get(column)
        ) != text(
            evidence_map[
                program_id
            ].get(column)
        ):
            written_batch_mismatches.append(
                f"{program_id}:{column}"
            )


post_record(
    "Written Batch 01 rows exactly equal evidence",
    not written_batch_mismatches,
    (
        "36 / 36"
        if not written_batch_mismatches
        else ", ".join(
            written_batch_mismatches[:15]
        )
    ),
)


written_non_batch_mismatches = []

for program_id in NON_BATCH_IDS:

    for column in EXPECTED_COLUMNS:

        if text(
            written_map[
                program_id
            ].get(column)
        ) != text(
            queue_map[
                program_id
            ].get(column)
        ):
            written_non_batch_mismatches.append(
                f"{program_id}:{column}"
            )


post_record(
    "Written remaining rows unchanged",
    not written_non_batch_mismatches,
    (
        "114 / 114"
        if not written_non_batch_mismatches
        else ", ".join(
            written_non_batch_mismatches[:15]
        )
    ),
)


# ================================================================
# VERIFY ALL SOURCE LOCKS STILL UNCHANGED
# ================================================================

queue_sha_after = sha256(
    QUEUE
)

batch_sha_after = sha256(
    BATCH
)

evidence_sha_after = sha256(
    EVIDENCE
)

canonical_sha_after = sha256(
    CANONICAL
)


post_record(
    "Source queue unchanged",
    (
        queue_sha_after
        == queue_sha_before
        == EXPECTED_QUEUE_SHA
    ),
    queue_sha_after,
)

post_record(
    "Batch lock unchanged",
    (
        batch_sha_after
        == batch_sha_before
        == EXPECTED_BATCH_SHA
    ),
    batch_sha_after,
)

post_record(
    "Evidence file unchanged",
    (
        evidence_sha_after
        == evidence_sha_before
        == EXPECTED_EVIDENCE_SHA
    ),
    evidence_sha_after,
)

post_record(
    "Canonical programs.json byte-for-byte unchanged",
    canonical_sha_after
    == canonical_sha_before,
    canonical_sha_after,
)


with CANONICAL.open(
    "r",
    encoding="utf-8-sig",
) as f:
    canonical_rows_after = json.load(f)


canonical_kr_after = []

if isinstance(
    canonical_rows_after,
    list,
):
    for row in canonical_rows_after:

        if not isinstance(row, dict):
            continue

        program_id = text(
            row.get(
                "program_id",
                row.get("programme_id", ""),
            )
        )

        if program_id.startswith("prog_kr_"):
            canonical_kr_after.append(
                program_id
            )


post_record(
    "Canonical programmes remain 600",
    (
        isinstance(
            canonical_rows_after,
            list,
        )
        and len(
            canonical_rows_after
        )
        == 600
    ),
    (
        len(canonical_rows_after)
        if isinstance(
            canonical_rows_after,
            list,
        )
        else "NOT A LIST"
    ),
)

post_record(
    "South Korea canonical programmes remain 0",
    len(canonical_kr_after) == 0,
    len(canonical_kr_after),
)


print()
print("POST-WRITE STAGED QUEUE AUDIT")
print("-" * 138)

for label, passed, detail in post_checks:

    print(
        f"{label:<65}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


post_failed = [
    (label, detail)
    for label, passed, detail in post_checks
    if not passed
]


if post_failed:

    if created_new and STAGED.exists():
        STAGED.unlink()

    print()
    print("=" * 138)
    print(
        "STEP 172.2C SOUTH KOREA "
        "BATCH 01 SAFE STAGING APPLY: FAIL"
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
        print()
        print(
            "INVALID NEW STAGED OUTPUT REMOVED."
        )

    print(
        "DO NOT MODIFY SOURCE QUEUE."
    )
    print(
        "DO NOT WRITE programs.json."
    )
    print(
        "DO NOT WRITE MONGODB."
    )
    print("=" * 138)

    sys.exit(1)


# ================================================================
# FINAL SUMMARY
# ================================================================

written_international_counts = Counter(
    norm(
        written_map[
            program_id
        ].get(
            "international_applicants_status"
        )
    )
    for program_id in BATCH_IDS
)


written_degree_counts = Counter(
    norm(
        written_map[
            program_id
        ].get(
            "degree_level"
        )
    )
    for program_id in BATCH_IDS
)


print()
print("=" * 138)
print(
    "STEP 172.2C SOUTH KOREA "
    "BATCH 01 SAFE STAGING APPLY: PASS"
)
print()

print(
    "STAGED QUEUE FILE                : "
    "planning\\30_south_korea_program_research_queue_batch01_applied.csv"
)

print(
    f"STAGED QUEUE SHA256              : "
    f"{staged_sha}"
)

print(
    "STAGED QUEUE ROWS                : 150"
)

print(
    "STAGED QUEUE COLUMNS             : 31"
)

print(
    "BATCH 01 APPLIED                 : 36 / 36"
)

print(
    "NON-BATCH ROWS PRESERVED         : 114 / 114"
)

print(
    "PROGRAMME IDENTITIES VERIFIED    : 36 / 36"
)

print(
    "RESEARCH STATUS VERIFIED         : 36 / 36"
)

print(
    "INTERNATIONAL VERIFIED_YES       : "
    f"{written_international_counts.get('verified_yes', 0)}"
)

print(
    "INTERNATIONAL UNKNOWN            : "
    f"{written_international_counts.get('unknown', 0)}"
)

print(
    "UNKNOWN IDS                      : "
    "prog_kr_028, prog_kr_029, prog_kr_030"
)

print(
    "DEGREE LEVELS                    : "
    f"{written_degree_counts.get('bachelor', 0)} BACHELOR / "
    f"{written_degree_counts.get('master', 0)} MASTER"
)

print()

print(
    "SOURCE 150-ROW QUEUE             : UNCHANGED"
)

print(
    "BATCH 01 LOCK                    : UNCHANGED"
)

print(
    "BATCH 01 EVIDENCE                : UNCHANGED"
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
        "STAGED OUTPUT STATUS             : "
        "EXISTING IDENTICAL FILE REUSED"
    )
else:
    print(
        "STAGED OUTPUT STATUS             : "
        "NEW FILE CREATED"
    )

print()
print(
    "NEXT: STEP 172.2D"
)

print(
    "FINAL AUDIT OF THE BATCH 01 "
    "STAGED 150-ROW QUEUE BEFORE "
    "LOCKING THE NEXT SOUTH KOREA BATCH"
)

print("=" * 138)
