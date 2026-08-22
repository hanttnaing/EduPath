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

WORKING_SOURCE = (
    PLANNING
    / "30_south_korea_program_research_queue_batch01_applied.csv"
)

BATCH02_LOCK = (
    PLANNING
    / "31_south_korea_program_research_batch02_lock.csv"
)

BATCH02_EVIDENCE = (
    PLANNING
    / "32_south_korea_program_research_batch02_evidence.csv"
)

NEW_STAGED = (
    PLANNING
    / "33_south_korea_program_research_queue_batch02_applied.csv"
)

TEMP = (
    PLANNING
    / "33_south_korea_program_research_queue_batch02_applied.tmp.csv"
)

CANONICAL = (
    ROOT
    / "data"
    / "cleaned"
    / "programs.json"
)


EXPECTED_WORKING_SOURCE_SHA = (
    "0c23f17369fd1f774838736b0e21fe617"
    "bd1ef804b0bc98f05c723158435075a"
)

EXPECTED_BATCH02_LOCK_SHA = (
    "aaea6d2f161713b125cff7ca82870b91"
    "fa29e96be5638626b2c9f4fa654a511d"
)

EXPECTED_BATCH02_EVIDENCE_SHA = (
    "d697fc09b7f994c07dbaa799e298974845"
    "379cd3528ad1acad270f8e4d751622"
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


ALL_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(1, 151)
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

VERIFIED_AFTER_APPLY_IDS = {
    f"prog_kr_{i:03d}"
    for i in range(1, 73)
}

REMAINING_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(73, 151)
]

EXPECTED_UNKNOWN_IDS = {
    "prog_kr_028",
    "prog_kr_029",
    "prog_kr_030",
}


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

        columns = list(
            reader.fieldnames or []
        )

    return rows, columns


def rows_equal(a, b):
    return all(
        text(a.get(column))
        == text(b.get(column))
        for column in EXPECTED_COLUMNS
    )


def stop_before_write():
    print()
    print("=" * 138)

    print(
        "STEP 172.2H SOUTH KOREA "
        "BATCH 02 SAFE STAGING APPLY: FAIL"
    )

    print()
    print(
        "STOP: NEW STAGED QUEUE NOT CREATED"
    )

    print(
        "CURRENT WORKING SOURCE MUST REMAIN UNCHANGED"
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
    "STEP 172.2H - SOUTH KOREA "
    "BATCH 02 SAFE EVIDENCE APPLY "
    "TO NEW STAGED 150-ROW QUEUE"
)

print("=" * 138)


# =====================================================================
# REQUIRED FILES
# =====================================================================

required_files = [
    WORKING_SOURCE,
    BATCH02_LOCK,
    BATCH02_EVIDENCE,
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
            f"{label:<72}: "
            f"{'PASS' if passed else 'FAIL'}"
            + (
                f" | {detail}"
                if detail
                else ""
            )
        )

    stop_before_write()


# =====================================================================
# IMMUTABLE HASH LOCKS
# =====================================================================

working_sha_before = sha256(
    WORKING_SOURCE
)

batch_lock_sha_before = sha256(
    BATCH02_LOCK
)

evidence_sha_before = sha256(
    BATCH02_EVIDENCE
)

canonical_sha_before = sha256(
    CANONICAL
)


record(
    "Working source SHA256 exact",
    working_sha_before
    == EXPECTED_WORKING_SOURCE_SHA,
    working_sha_before,
)

record(
    "Batch 02 lock SHA256 exact",
    batch_lock_sha_before
    == EXPECTED_BATCH02_LOCK_SHA,
    batch_lock_sha_before,
)

record(
    "Batch 02 evidence SHA256 exact",
    evidence_sha_before
    == EXPECTED_BATCH02_EVIDENCE_SHA,
    evidence_sha_before,
)


# =====================================================================
# LOAD FILES
# =====================================================================

working_rows, working_cols = load_csv(
    WORKING_SOURCE
)

lock_rows, lock_cols = load_csv(
    BATCH02_LOCK
)

evidence_rows, evidence_cols = load_csv(
    BATCH02_EVIDENCE
)


record(
    "Working source rows = 150",
    len(working_rows) == 150,
    len(working_rows),
)

record(
    "Batch 02 lock rows = 36",
    len(lock_rows) == 36,
    len(lock_rows),
)

record(
    "Batch 02 evidence rows = 36",
    len(evidence_rows) == 36,
    len(evidence_rows),
)


record(
    "Working source columns = 31",
    working_cols == EXPECTED_COLUMNS,
    len(working_cols),
)

record(
    "Batch 02 lock columns = 31",
    lock_cols == EXPECTED_COLUMNS,
    len(lock_cols),
)

record(
    "Batch 02 evidence columns = 31",
    evidence_cols == EXPECTED_COLUMNS,
    len(evidence_cols),
)


working_ids = [
    text(row.get("program_id"))
    for row in working_rows
]

lock_ids = [
    text(row.get("program_id"))
    for row in lock_rows
]

evidence_ids = [
    text(row.get("program_id"))
    for row in evidence_rows
]


record(
    "Working source IDs exact",
    working_ids == ALL_IDS,
    (
        f"{working_ids[0]} -> {working_ids[-1]}"
        if working_ids
        else "EMPTY"
    ),
)

record(
    "Batch 02 lock IDs exact",
    lock_ids == BATCH02_IDS,
    (
        f"{lock_ids[0]} -> {lock_ids[-1]}"
        if lock_ids
        else "EMPTY"
    ),
)

record(
    "Batch 02 evidence IDs exact",
    evidence_ids == BATCH02_IDS,
    (
        f"{evidence_ids[0]} -> {evidence_ids[-1]}"
        if evidence_ids
        else "EMPTY"
    ),
)


working_map = {
    text(row["program_id"]): row
    for row in working_rows
}

lock_map = {
    text(row["program_id"]): row
    for row in lock_rows
}

evidence_map = {
    text(row["program_id"]): row
    for row in evidence_rows
}


# =====================================================================
# BATCH 02 LOCK MUST STILL MATCH CURRENT WORKING SOURCE
# =====================================================================

lock_source_mismatches = []


for pid in BATCH02_IDS:

    for column in EXPECTED_COLUMNS:

        if text(
            lock_map[
                pid
            ].get(column)
        ) != text(
            working_map[
                pid
            ].get(column)
        ):

            lock_source_mismatches.append(
                f"{pid}:{column}"
            )


record(
    "Batch 02 lock exact working-source snapshot",
    not lock_source_mismatches,
    (
        "36 / 36"
        if not lock_source_mismatches
        else ", ".join(
            lock_source_mismatches[:15]
        )
    ),
)


# =====================================================================
# EVIDENCE MUST PRESERVE IMMUTABLE SEED IDENTITY
# =====================================================================

seed_mismatches = []


for pid in BATCH02_IDS:

    for field in IMMUTABLE_SEED_FIELDS:

        if text(
            evidence_map[
                pid
            ].get(field)
        ) != text(
            lock_map[
                pid
            ].get(field)
        ):

            seed_mismatches.append(
                f"{pid}:{field}"
            )


record(
    "Evidence preserves Batch 02 immutable seed identity",
    not seed_mismatches,
    (
        "mismatches=0"
        if not seed_mismatches
        else ", ".join(
            seed_mismatches[:15]
        )
    ),
)


# =====================================================================
# PRE-APPLY EVIDENCE STATUS
# =====================================================================

evidence_identity_counts = Counter(
    norm(
        row.get(
            "programme_identity_status"
        )
    )
    for row in evidence_rows
)

evidence_research_counts = Counter(
    norm(
        row.get(
            "research_status"
        )
    )
    for row in evidence_rows
)

evidence_international_counts = Counter(
    norm(
        row.get(
            "international_applicants_status"
        )
    )
    for row in evidence_rows
)

evidence_degree_counts = Counter(
    norm(
        row.get(
            "degree_level"
        )
    )
    for row in evidence_rows
)


record(
    "Batch 02 evidence identity VERIFIED = 36",
    evidence_identity_counts
    == Counter({
        "verified": 36,
    }),
    dict(
        evidence_identity_counts
    ),
)

record(
    "Batch 02 evidence research VERIFIED = 36",
    evidence_research_counts
    == Counter({
        "verified": 36,
    }),
    dict(
        evidence_research_counts
    ),
)

record(
    "Batch 02 evidence international verified_yes = 36",
    evidence_international_counts
    == Counter({
        "verified_yes": 36,
    }),
    dict(
        evidence_international_counts
    ),
)

record(
    "Batch 02 evidence degree Bachelor = 36",
    evidence_degree_counts
    == Counter({
        "bachelor": 36,
    }),
    dict(
        evidence_degree_counts
    ),
)


# =====================================================================
# CURRENT WORKING SOURCE STATE
# =====================================================================

batch01_verified = {
    pid
    for pid in BATCH01_IDS
    if (
        norm(
            working_map[
                pid
            ].get(
                "research_status"
            )
        )
        == "verified"
        and norm(
            working_map[
                pid
            ].get(
                "programme_identity_status"
            )
        )
        == "verified"
    )
}


record(
    "Batch 01 remains fully VERIFIED before apply",
    batch01_verified
    == set(BATCH01_IDS),
    f"{len(batch01_verified)} / 36",
)


batch02_preexisting_verified = [
    pid
    for pid in BATCH02_IDS
    if (
        norm(
            working_map[
                pid
            ].get(
                "research_status"
            )
        )
        == "verified"
        or norm(
            working_map[
                pid
            ].get(
                "programme_identity_status"
            )
        )
        == "verified"
    )
]


record(
    "Batch 02 not already applied",
    not batch02_preexisting_verified,
    (
        "0 verified"
        if not batch02_preexisting_verified
        else ", ".join(
            batch02_preexisting_verified
        )
    ),
)


remaining_preexisting_verified = [
    pid
    for pid in REMAINING_IDS
    if norm(
        working_map[
            pid
        ].get(
            "research_status"
        )
    )
    == "verified"
]


record(
    "Remaining 78 rows contain no VERIFIED research",
    not remaining_preexisting_verified,
    (
        "78 / 78 outside VERIFIED set"
        if not remaining_preexisting_verified
        else ", ".join(
            remaining_preexisting_verified[:15]
        )
    ),
)


# =====================================================================
# CANONICAL PRE-WRITE LOCK
# =====================================================================

with CANONICAL.open(
    "r",
    encoding="utf-8-sig",
) as f:

    canonical_rows_before = json.load(f)


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
        len(
            canonical_rows_before
        )
        if isinstance(
            canonical_rows_before,
            list,
        )
        else "NOT A LIST"
    ),
)


canonical_kr_before = []


if isinstance(
    canonical_rows_before,
    list,
):

    for row in canonical_rows_before:

        if not isinstance(
            row,
            dict,
        ):
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

            canonical_kr_before.append(
                pid
            )


record(
    "South Korea canonical programmes before staging = 0",
    len(
        canonical_kr_before
    )
    == 0,
    len(
        canonical_kr_before
    ),
)


# =====================================================================
# PRE-WRITE REPORT
# =====================================================================

print()
print(
    "PRE-WRITE BATCH 02 APPLY AUDIT"
)
print("-" * 138)


for label, passed, detail in checks:

    print(
        f"{label:<72}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


prewrite_failed = [
    (
        label,
        detail,
    )
    for (
        label,
        passed,
        detail,
    )
    in checks
    if not passed
]


if prewrite_failed:

    stop_before_write()


# =====================================================================
# BUILD NEW STAGED QUEUE IN MEMORY
#
# prog_kr_001 - 036:
#     preserve current Batch 01 verified rows exactly
#
# prog_kr_037 - 072:
#     replace with Batch 02 verified evidence
#
# prog_kr_073 - 150:
#     preserve current working source exactly
# =====================================================================

staged_rows = []


for source_row in working_rows:

    pid = text(
        source_row.get(
            "program_id"
        )
    )

    if pid in BATCH02_ID_SET:

        evidence_row = evidence_map[
            pid
        ]

        staged_rows.append({
            column: text(
                evidence_row.get(
                    column
                )
            )
            for column
            in EXPECTED_COLUMNS
        })

    else:

        staged_rows.append({
            column: text(
                source_row.get(
                    column
                )
            )
            for column
            in EXPECTED_COLUMNS
        })


staged_map = {
    text(row["program_id"]): row
    for row in staged_rows
}

staged_ids = [
    text(row["program_id"])
    for row in staged_rows
]


build_checks = []


def build_record(
    label,
    passed,
    detail="",
):
    build_checks.append(
        (
            label,
            bool(passed),
            str(detail),
        )
    )


build_record(
    "New staged row count = 150",
    len(staged_rows) == 150,
    len(staged_rows),
)

build_record(
    "New staged programme order exact",
    staged_ids == ALL_IDS,
    (
        f"{staged_ids[0]} -> {staged_ids[-1]}"
        if staged_ids
        else "EMPTY"
    ),
)


# =====================================================================
# BATCH 01 MUST BE VALUE-IDENTICAL TO CURRENT WORKING SOURCE
# =====================================================================

batch01_mismatches = []


for pid in BATCH01_IDS:

    if not rows_equal(
        staged_map[pid],
        working_map[pid],
    ):

        for column in EXPECTED_COLUMNS:

            if text(
                staged_map[
                    pid
                ].get(column)
            ) != text(
                working_map[
                    pid
                ].get(column)
            ):

                batch01_mismatches.append(
                    f"{pid}:{column}"
                )


build_record(
    "Batch 01 rows preserved exactly",
    not batch01_mismatches,
    (
        "36 / 36"
        if not batch01_mismatches
        else ", ".join(
            batch01_mismatches[:15]
        )
    ),
)


# =====================================================================
# BATCH 02 MUST EXACTLY EQUAL EVIDENCE
# =====================================================================

batch02_apply_mismatches = []


for pid in BATCH02_IDS:

    if not rows_equal(
        staged_map[pid],
        evidence_map[pid],
    ):

        for column in EXPECTED_COLUMNS:

            if text(
                staged_map[
                    pid
                ].get(column)
            ) != text(
                evidence_map[
                    pid
                ].get(column)
            ):

                batch02_apply_mismatches.append(
                    f"{pid}:{column}"
                )


build_record(
    "Batch 02 staged rows exactly equal evidence",
    not batch02_apply_mismatches,
    (
        "36 / 36"
        if not batch02_apply_mismatches
        else ", ".join(
            batch02_apply_mismatches[:15]
        )
    ),
)


# =====================================================================
# REMAINING 78 MUST BE UNCHANGED
# =====================================================================

remaining_mismatches = []


for pid in REMAINING_IDS:

    if not rows_equal(
        staged_map[pid],
        working_map[pid],
    ):

        for column in EXPECTED_COLUMNS:

            if text(
                staged_map[
                    pid
                ].get(column)
            ) != text(
                working_map[
                    pid
                ].get(column)
            ):

                remaining_mismatches.append(
                    f"{pid}:{column}"
                )


build_record(
    "Remaining 78 rows unchanged",
    not remaining_mismatches,
    (
        "78 / 78"
        if not remaining_mismatches
        else ", ".join(
            remaining_mismatches[:15]
        )
    ),
)


# =====================================================================
# VERIFIED SET MUST NOW BE EXACTLY 001 - 072
# =====================================================================

verified_research_ids = {
    pid
    for pid in ALL_IDS
    if norm(
        staged_map[
            pid
        ].get(
            "research_status"
        )
    )
    == "verified"
}

verified_identity_ids = {
    pid
    for pid in ALL_IDS
    if norm(
        staged_map[
            pid
        ].get(
            "programme_identity_status"
        )
    )
    == "verified"
}


build_record(
    "Verified research ID set exact = 72",
    verified_research_ids
    == VERIFIED_AFTER_APPLY_IDS,
    len(
        verified_research_ids
    ),
)

build_record(
    "Verified identity ID set exact = 72",
    verified_identity_ids
    == VERIFIED_AFTER_APPLY_IDS,
    len(
        verified_identity_ids
    ),
)


remaining_verified_after = [
    pid
    for pid in REMAINING_IDS
    if (
        norm(
            staged_map[
                pid
            ].get(
                "research_status"
            )
        )
        == "verified"
        or norm(
            staged_map[
                pid
            ].get(
                "programme_identity_status"
            )
        )
        == "verified"
    )
]


build_record(
    "Remaining 78 rows remain outside VERIFIED set",
    not remaining_verified_after,
    (
        "78 / 78"
        if not remaining_verified_after
        else ", ".join(
            remaining_verified_after[:15]
        )
    ),
)


# =====================================================================
# AGGREGATE VERIFIED DATA CHECKS
# =====================================================================

verified_international_counts = Counter(
    norm(
        staged_map[
            pid
        ].get(
            "international_applicants_status"
        )
    )
    for pid in sorted(
        VERIFIED_AFTER_APPLY_IDS
    )
)


build_record(
    "Verified 72 international = 69 yes / 3 unknown",
    verified_international_counts
    == Counter({
        "verified_yes": 69,
        "unknown": 3,
    }),
    dict(
        verified_international_counts
    ),
)


unknown_ids_after = {
    pid
    for pid
    in VERIFIED_AFTER_APPLY_IDS
    if norm(
        staged_map[
            pid
        ].get(
            "international_applicants_status"
        )
    )
    == "unknown"
}


build_record(
    "Verified unknown international IDs exact",
    unknown_ids_after
    == EXPECTED_UNKNOWN_IDS,
    ", ".join(
        sorted(
            unknown_ids_after
        )
    ),
)


verified_degree_counts = Counter(
    norm(
        staged_map[
            pid
        ].get(
            "degree_level"
        )
    )
    for pid in sorted(
        VERIFIED_AFTER_APPLY_IDS
    )
)


build_record(
    "Verified 72 degrees = 63 Bachelor / 9 Master",
    verified_degree_counts
    == Counter({
        "bachelor": 63,
        "master": 9,
    }),
    dict(
        verified_degree_counts
    ),
)


print()
print(
    "IN-MEMORY NEW STAGED QUEUE AUDIT"
)
print("-" * 138)


for label, passed, detail in build_checks:

    print(
        f"{label:<72}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


if any(
    not passed
    for _, passed, _
    in build_checks
):

    stop_before_write()


# =====================================================================
# WRITE TEMP OUTPUT
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
        staged_rows
    )


candidate_sha = sha256(
    TEMP
)


# =====================================================================
# SAFE OUTPUT POLICY
#
# Existing identical file -> reuse
# Existing different file -> STOP, never overwrite
# =====================================================================

created_new = False
existing_identical = False


if NEW_STAGED.exists():

    existing_sha = sha256(
        NEW_STAGED
    )

    if existing_sha == candidate_sha:

        existing_identical = True

        TEMP.unlink()

    else:

        TEMP.unlink()

        print()
        print("=" * 138)

        print(
            "STEP 172.2H SOUTH KOREA "
            "BATCH 02 SAFE STAGING APPLY: FAIL"
        )

        print()

        print(
            "A DIFFERENT BATCH 02 STAGED "
            "QUEUE ALREADY EXISTS"
        )

        print(
            str(
                NEW_STAGED.relative_to(
                    ROOT
                )
            )
        )

        print(
            f"Existing SHA256 : "
            f"{existing_sha}"
        )

        print(
            f"Candidate SHA256: "
            f"{candidate_sha}"
        )

        print()

        print(
            "NO FILE WAS OVERWRITTEN"
        )

        print(
            "DO NOT CONTINUE TO BATCH 03"
        )

        print("=" * 138)

        sys.exit(1)

else:

    os.replace(
        TEMP,
        NEW_STAGED,
    )

    created_new = True


# =====================================================================
# POST-WRITE AUDIT
# =====================================================================

post_checks = []


def post_record(
    label,
    passed,
    detail="",
):

    post_checks.append(
        (
            label,
            bool(passed),
            str(detail),
        )
    )


new_staged_sha = sha256(
    NEW_STAGED
)

written_rows, written_cols = load_csv(
    NEW_STAGED
)


post_record(
    "New staged output exists",
    NEW_STAGED.exists(),
    str(
        NEW_STAGED.relative_to(
            ROOT
        )
    ),
)

post_record(
    "New staged SHA matches candidate",
    new_staged_sha
    == candidate_sha,
    new_staged_sha,
)

post_record(
    "Written columns = 31",
    written_cols
    == EXPECTED_COLUMNS,
    len(
        written_cols
    ),
)

post_record(
    "Written rows = 150",
    len(
        written_rows
    )
    == 150,
    len(
        written_rows
    ),
)


written_ids = [
    text(
        row.get(
            "program_id"
        )
    )
    for row in written_rows
]


post_record(
    "Written programme IDs exact",
    written_ids
    == ALL_IDS,
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


# Batch 01 written verification

written_batch01_mismatches = []


for pid in BATCH01_IDS:

    if not rows_equal(
        written_map[pid],
        working_map[pid],
    ):

        written_batch01_mismatches.append(
            pid
        )


post_record(
    "Written Batch 01 preserved",
    not written_batch01_mismatches,
    (
        "36 / 36"
        if not written_batch01_mismatches
        else ", ".join(
            written_batch01_mismatches[:15]
        )
    ),
)


# Batch 02 written verification

written_batch02_mismatches = []


for pid in BATCH02_IDS:

    if not rows_equal(
        written_map[pid],
        evidence_map[pid],
    ):

        written_batch02_mismatches.append(
            pid
        )


post_record(
    "Written Batch 02 exactly equals evidence",
    not written_batch02_mismatches,
    (
        "36 / 36"
        if not written_batch02_mismatches
        else ", ".join(
            written_batch02_mismatches[:15]
        )
    ),
)


# Remaining written verification

written_remaining_mismatches = []


for pid in REMAINING_IDS:

    if not rows_equal(
        written_map[pid],
        working_map[pid],
    ):

        written_remaining_mismatches.append(
            pid
        )


post_record(
    "Written remaining 78 preserved",
    not written_remaining_mismatches,
    (
        "78 / 78"
        if not written_remaining_mismatches
        else ", ".join(
            written_remaining_mismatches[:15]
        )
    ),
)


written_verified_research = {
    pid
    for pid in ALL_IDS
    if norm(
        written_map[
            pid
        ].get(
            "research_status"
        )
    )
    == "verified"
}


post_record(
    "Written VERIFIED research rows exact = 72",
    written_verified_research
    == VERIFIED_AFTER_APPLY_IDS,
    len(
        written_verified_research
    ),
)


written_verified_identity = {
    pid
    for pid in ALL_IDS
    if norm(
        written_map[
            pid
        ].get(
            "programme_identity_status"
        )
    )
    == "verified"
}


post_record(
    "Written VERIFIED identity rows exact = 72",
    written_verified_identity
    == VERIFIED_AFTER_APPLY_IDS,
    len(
        written_verified_identity
    ),
)


# =====================================================================
# VERIFY INPUT LOCKS STILL UNCHANGED
# =====================================================================

working_sha_after = sha256(
    WORKING_SOURCE
)

batch_lock_sha_after = sha256(
    BATCH02_LOCK
)

evidence_sha_after = sha256(
    BATCH02_EVIDENCE
)

canonical_sha_after = sha256(
    CANONICAL
)


post_record(
    "Previous staged working source unchanged",
    (
        working_sha_after
        == working_sha_before
        == EXPECTED_WORKING_SOURCE_SHA
    ),
    working_sha_after,
)

post_record(
    "Batch 02 lock unchanged",
    (
        batch_lock_sha_after
        == batch_lock_sha_before
        == EXPECTED_BATCH02_LOCK_SHA
    ),
    batch_lock_sha_after,
)

post_record(
    "Batch 02 evidence unchanged",
    (
        evidence_sha_after
        == evidence_sha_before
        == EXPECTED_BATCH02_EVIDENCE_SHA
    ),
    evidence_sha_after,
)

post_record(
    "Canonical programs.json byte-for-byte unchanged",
    canonical_sha_after
    == canonical_sha_before,
    canonical_sha_after,
)


# =====================================================================
# CANONICAL POST-WRITE VERIFICATION
# =====================================================================

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

        if not isinstance(
            row,
            dict,
        ):
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

            canonical_kr_after.append(
                pid
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
        len(
            canonical_rows_after
        )
        if isinstance(
            canonical_rows_after,
            list,
        )
        else "NOT A LIST"
    ),
)

post_record(
    "South Korea canonical programmes remain 0",
    len(
        canonical_kr_after
    )
    == 0,
    len(
        canonical_kr_after
    ),
)


print()
print(
    "POST-WRITE NEW STAGED QUEUE AUDIT"
)
print("-" * 138)


for label, passed, detail in post_checks:

    print(
        f"{label:<72}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


post_failed = [
    (
        label,
        detail,
    )
    for (
        label,
        passed,
        detail,
    )
    in post_checks
    if not passed
]


if post_failed:

    if (
        created_new
        and NEW_STAGED.exists()
    ):

        NEW_STAGED.unlink()

    print()
    print("=" * 138)

    print(
        "STEP 172.2H SOUTH KOREA "
        "BATCH 02 SAFE STAGING APPLY: FAIL"
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
            "INVALID NEW STAGED OUTPUT REMOVED"
        )

    print(
        "DO NOT CONTINUE TO BATCH 03"
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
# FINAL AGGREGATE SUMMARY
# =====================================================================

final_international_counts = Counter(
    norm(
        written_map[
            pid
        ].get(
            "international_applicants_status"
        )
    )
    for pid
    in VERIFIED_AFTER_APPLY_IDS
)


final_degree_counts = Counter(
    norm(
        written_map[
            pid
        ].get(
            "degree_level"
        )
    )
    for pid
    in VERIFIED_AFTER_APPLY_IDS
)


print()
print("=" * 138)

print(
    "STEP 172.2H SOUTH KOREA "
    "BATCH 02 SAFE STAGING APPLY: PASS"
)

print()

print(
    "NEW STAGED QUEUE FILE            : "
    "planning\\33_south_korea_program_research_queue_batch02_applied.csv"
)

print(
    f"NEW STAGED QUEUE SHA256          : "
    f"{new_staged_sha}"
)

print(
    "NEW STAGED QUEUE ROWS            : 150"
)

print(
    "NEW STAGED QUEUE COLUMNS         : 31"
)

print()

print(
    "BATCH 01 PRESERVED               : 36 / 36"
)

print(
    "BATCH 02 APPLIED                 : 36 / 36"
)

print(
    "TOTAL VERIFIED PROGRAMMES        : 72 / 150"
)

print(
    "TOTAL VERIFIED UNIVERSITIES      : 24"
)

print(
    "REMAINING PROGRAMMES             : 78"
)

print(
    "REMAINING UNIVERSITIES           : 26"
)

print()

print(
    "PROGRAMME IDENTITIES VERIFIED    : 72 / 72"
)

print(
    "RESEARCH STATUS VERIFIED         : 72 / 72"
)

print(
    "INTERNATIONAL VERIFIED_YES       : "
    f"{final_international_counts.get('verified_yes', 0)}"
)

print(
    "INTERNATIONAL UNKNOWN            : "
    f"{final_international_counts.get('unknown', 0)}"
)

print(
    "UNKNOWN IDS                      : "
    "prog_kr_028, prog_kr_029, prog_kr_030"
)

print(
    "DEGREE LEVELS                    : "
    f"{final_degree_counts.get('bachelor', 0)} BACHELOR / "
    f"{final_degree_counts.get('master', 0)} MASTER"
)

print()

print(
    "PREVIOUS STAGED QUEUE            : UNCHANGED"
)

print(
    "BATCH 02 LOCK                    : UNCHANGED"
)

print(
    "BATCH 02 EVIDENCE                : UNCHANGED"
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
        "NEW STAGED OUTPUT STATUS        : "
        "EXISTING IDENTICAL FILE REUSED"
    )

else:

    print(
        "NEW STAGED OUTPUT STATUS        : "
        "NEW FILE CREATED"
    )

print()

print(
    "NEXT: STEP 172.2I"
)

print(
    "FINAL AUDIT OF THE 72-VERIFIED "
    "BATCH 01 + BATCH 02 STAGED QUEUE "
    "BEFORE LOCKING BATCH 03"
)

print("=" * 138)
