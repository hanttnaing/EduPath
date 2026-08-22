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

WORKING_SOURCE = (
    PLANNING
    / "33_south_korea_program_research_queue_batch02_applied.csv"
)

BATCH02_LOCK = (
    PLANNING
    / "31_south_korea_program_research_batch02_lock.csv"
)

BATCH02_EVIDENCE = (
    PLANNING
    / "32_south_korea_program_research_batch02_evidence.csv"
)

BATCH03_LOCK = (
    PLANNING
    / "34_south_korea_program_research_batch03_lock.csv"
)

TEMP = (
    PLANNING
    / "34_south_korea_program_research_batch03_lock.tmp.csv"
)

CANONICAL = (
    ROOT
    / "data"
    / "cleaned"
    / "programs.json"
)


EXPECTED_WORKING_SOURCE_SHA = (
    "43b94582702e5f0f03eff806c9c991cd"
    "ed96f33dd1f7c91d71e54afb0e072a9c"
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

VERIFIED_IDS = {
    f"prog_kr_{i:03d}"
    for i in range(1, 73)
}

BATCH03_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(73, 109)
]

EXPECTED_BATCH03_PARENTS = {
    f"uni_kr_{i:03d}"
    for i in range(25, 37)
}

POST_BATCH03_REMAINING_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(109, 151)
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


print("=" * 138)
print(
    "STEP 172.2J - SOUTH KOREA "
    "BATCH 03 IMMUTABLE LOCK BUILD"
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
    print("PRE-WRITE BATCH 03 LOCK AUDIT")
    print("-" * 138)

    for label, passed, detail in checks:

        print(
            f"{label:<72}: "
            f"{'PASS' if passed else 'FAIL'}"
            f" | {detail}"
        )

    print()
    print("=" * 138)

    print(
        "STEP 172.2J SOUTH KOREA "
        "BATCH 03 IMMUTABLE LOCK BUILD: FAIL"
    )

    print(
        "STOP: REQUIRED SOURCE FILE MISSING"
    )

    print(
        "DO NOT RESEARCH BATCH 03"
    )

    print("=" * 138)

    sys.exit(1)


# =====================================================================
# HASH LOCKS
# =====================================================================

working_sha_before = sha256(
    WORKING_SOURCE
)

batch02_lock_sha_before = sha256(
    BATCH02_LOCK
)

batch02_evidence_sha_before = sha256(
    BATCH02_EVIDENCE
)

canonical_sha_before = sha256(
    CANONICAL
)


record(
    "72-verified working source SHA256 exact",
    working_sha_before
    == EXPECTED_WORKING_SOURCE_SHA,
    working_sha_before,
)

record(
    "Batch 02 lock SHA256 exact",
    batch02_lock_sha_before
    == EXPECTED_BATCH02_LOCK_SHA,
    batch02_lock_sha_before,
)

record(
    "Batch 02 evidence SHA256 exact",
    batch02_evidence_sha_before
    == EXPECTED_BATCH02_EVIDENCE_SHA,
    batch02_evidence_sha_before,
)


# =====================================================================
# LOAD WORKING SOURCE
# =====================================================================

working_rows, working_cols = load_csv(
    WORKING_SOURCE
)


record(
    "Working source rows = 150",
    len(working_rows) == 150,
    len(working_rows),
)

record(
    "Working source schema exact 31 columns",
    working_cols == EXPECTED_COLUMNS,
    len(working_cols),
)


working_ids = [
    text(row.get("program_id"))
    for row in working_rows
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


working_map = {
    text(row["program_id"]): row
    for row in working_rows
}


# =====================================================================
# CURRENT VERIFIED STATE MUST STILL BE EXACTLY 001 - 072
# =====================================================================

verified_research_ids = {
    pid
    for pid in ALL_IDS
    if norm(
        working_map[
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
        working_map[
            pid
        ].get(
            "programme_identity_status"
        )
    )
    == "verified"
}


record(
    "Existing VERIFIED research IDs exact = 72",
    verified_research_ids
    == VERIFIED_IDS,
    len(verified_research_ids),
)

record(
    "Existing VERIFIED identity IDs exact = 72",
    verified_identity_ids
    == VERIFIED_IDS,
    len(verified_identity_ids),
)


# =====================================================================
# BATCH 03 MUST NOT ALREADY BE RESEARCHED
# =====================================================================

batch03_verified_research = [
    pid
    for pid in BATCH03_IDS
    if norm(
        working_map[
            pid
        ].get(
            "research_status"
        )
    )
    == "verified"
]


batch03_verified_identity = [
    pid
    for pid in BATCH03_IDS
    if norm(
        working_map[
            pid
        ].get(
            "programme_identity_status"
        )
    )
    == "verified"
]


record(
    "Batch 03 has no VERIFIED research rows",
    not batch03_verified_research,
    (
        "0"
        if not batch03_verified_research
        else ", ".join(
            batch03_verified_research
        )
    ),
)

record(
    "Batch 03 has no VERIFIED identity rows",
    not batch03_verified_identity,
    (
        "0"
        if not batch03_verified_identity
        else ", ".join(
            batch03_verified_identity
        )
    ),
)


# =====================================================================
# SELECT BATCH 03
# =====================================================================

batch03_rows = [
    {
        column: text(
            working_map[
                pid
            ].get(column)
        )
        for column in EXPECTED_COLUMNS
    }
    for pid in BATCH03_IDS
]


selected_ids = [
    text(
        row.get(
            "program_id"
        )
    )
    for row in batch03_rows
]


record(
    "Selected Batch 03 rows = 36",
    len(batch03_rows) == 36,
    len(batch03_rows),
)

record(
    "Selected Batch 03 IDs exact/order exact",
    selected_ids == BATCH03_IDS,
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
        row.get(
            "university_id"
        )
    )
    for row in batch03_rows
)


record(
    "Batch 03 parent universities exact = 12",
    set(parent_counts)
    == EXPECTED_BATCH03_PARENTS,
    len(parent_counts),
)


record(
    "Batch 03 exactly 3 programmes per parent",
    (
        set(parent_counts)
        == EXPECTED_BATCH03_PARENTS
        and all(
            parent_counts[parent]
            == 3
            for parent
            in EXPECTED_BATCH03_PARENTS
        )
    ),
    (
        f"{sum(parent_counts[p] == 3 for p in EXPECTED_BATCH03_PARENTS)} / 12"
    ),
)


slots_by_parent = defaultdict(set)


for row in batch03_rows:

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
    for parent in sorted(
        EXPECTED_BATCH03_PARENTS
    )
    if slots_by_parent[
        parent
    ]
    != {"1", "2", "3"}
]


record(
    "Batch 03 parent slots exact 1 / 2 / 3",
    not bad_slots,
    (
        "12 / 12"
        if not bad_slots
        else ", ".join(
            bad_slots
        )
    ),
)


# =====================================================================
# UNIVERSITY ID CONTINUITY
# =====================================================================

batch03_parent_order = []


for row in batch03_rows:

    parent = text(
        row.get(
            "university_id"
        )
    )

    if (
        not batch03_parent_order
        or batch03_parent_order[-1]
        != parent
    ):

        batch03_parent_order.append(
            parent
        )


expected_parent_order = [
    f"uni_kr_{i:03d}"
    for i in range(25, 37)
]


record(
    "Batch 03 university order exact",
    batch03_parent_order
    == expected_parent_order,
    (
        f"{batch03_parent_order[0]} -> "
        f"{batch03_parent_order[-1]}"
        if batch03_parent_order
        else "EMPTY"
    ),
)


# =====================================================================
# POST-BATCH03 REMAINING 42 MUST ALSO BE UNVERIFIED
# =====================================================================

remaining_verified = [
    pid
    for pid in POST_BATCH03_REMAINING_IDS
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
    "Post-Batch03 remaining 42 rows outside VERIFIED set",
    not remaining_verified,
    (
        "42 / 42"
        if not remaining_verified
        else ", ".join(
            remaining_verified[:15]
        )
    ),
)


# =====================================================================
# DUPLICATES
# =====================================================================

duplicate_ids = [
    pid
    for pid, count
    in Counter(
        selected_ids
    ).items()
    if count > 1
]


record(
    "Batch 03 duplicate programme IDs = 0",
    not duplicate_ids,
    (
        "0"
        if not duplicate_ids
        else ", ".join(
            duplicate_ids
        )
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
        and len(
            canonical_rows
        )
        == 600
    ),
    (
        len(
            canonical_rows
        )
        if isinstance(
            canonical_rows,
            list,
        )
        else "NOT A LIST"
    ),
)


canonical_kr_ids = []


if isinstance(
    canonical_rows,
    list,
):

    for row in canonical_rows:

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

            canonical_kr_ids.append(
                pid
            )


record(
    "South Korea canonical programmes = 0",
    len(canonical_kr_ids) == 0,
    len(canonical_kr_ids),
)


# =====================================================================
# PRE-WRITE GATE
# =====================================================================

print()
print(
    "PRE-WRITE BATCH 03 LOCK AUDIT"
)
print("-" * 138)


for label, passed, detail in checks:

    print(
        f"{label:<74}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


failed = [
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


if failed:

    print()
    print("=" * 138)

    print(
        "STEP 172.2J SOUTH KOREA "
        "BATCH 03 IMMUTABLE LOCK BUILD: FAIL"
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
        "STOP: BATCH 03 LOCK NOT CREATED"
    )

    print(
        "DO NOT RESEARCH BATCH 03"
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
# WRITE TEMP LOCK
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
        batch03_rows
    )


candidate_sha = sha256(
    TEMP
)


# =====================================================================
# SAFE OUTPUT POLICY
# =====================================================================

created_new = False
existing_identical = False


if BATCH03_LOCK.exists():

    existing_sha = sha256(
        BATCH03_LOCK
    )

    if existing_sha == candidate_sha:

        existing_identical = True

        TEMP.unlink()

    else:

        TEMP.unlink()

        print()
        print("=" * 138)

        print(
            "STEP 172.2J SOUTH KOREA "
            "BATCH 03 IMMUTABLE LOCK BUILD: FAIL"
        )

        print()
        print(
            "A DIFFERENT BATCH 03 LOCK "
            "ALREADY EXISTS"
        )

        print(
            str(
                BATCH03_LOCK.relative_to(
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
            "DO NOT RESEARCH BATCH 03 "
            "UNTIL THE CONFLICT IS RESOLVED"
        )

        print("=" * 138)

        sys.exit(1)

else:

    os.replace(
        TEMP,
        BATCH03_LOCK,
    )

    created_new = True


# =====================================================================
# POST-WRITE VERIFICATION
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


batch03_sha = sha256(
    BATCH03_LOCK
)

written_rows, written_cols = load_csv(
    BATCH03_LOCK
)


post_record(
    "Batch 03 lock output exists",
    BATCH03_LOCK.exists(),
    str(
        BATCH03_LOCK.relative_to(
            ROOT
        )
    ),
)

post_record(
    "Batch 03 lock SHA matches candidate",
    batch03_sha == candidate_sha,
    batch03_sha,
)

post_record(
    "Written Batch 03 columns = 31",
    written_cols == EXPECTED_COLUMNS,
    len(written_cols),
)

post_record(
    "Written Batch 03 rows = 36",
    len(written_rows) == 36,
    len(written_rows),
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
    "Written Batch 03 IDs exact",
    written_ids == BATCH03_IDS,
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


source_snapshot_mismatches = []


for pid in BATCH03_IDS:

    if not rows_equal(
        written_map[pid],
        working_map[pid],
    ):

        for column in EXPECTED_COLUMNS:

            if text(
                written_map[
                    pid
                ].get(column)
            ) != text(
                working_map[
                    pid
                ].get(column)
            ):

                source_snapshot_mismatches.append(
                    f"{pid}:{column}"
                )


post_record(
    "Written Batch 03 exact working-source snapshot",
    not source_snapshot_mismatches,
    (
        "36 / 36"
        if not source_snapshot_mismatches
        else ", ".join(
            source_snapshot_mismatches[:15]
        )
    ),
)


# =====================================================================
# SOURCE LOCKS MUST REMAIN UNCHANGED
# =====================================================================

working_sha_after = sha256(
    WORKING_SOURCE
)

batch02_lock_sha_after = sha256(
    BATCH02_LOCK
)

batch02_evidence_sha_after = sha256(
    BATCH02_EVIDENCE
)

canonical_sha_after = sha256(
    CANONICAL
)


post_record(
    "72-verified working source unchanged",
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
        batch02_lock_sha_after
        == batch02_lock_sha_before
        == EXPECTED_BATCH02_LOCK_SHA
    ),
    batch02_lock_sha_after,
)

post_record(
    "Batch 02 evidence unchanged",
    (
        batch02_evidence_sha_after
        == batch02_evidence_sha_before
        == EXPECTED_BATCH02_EVIDENCE_SHA
    ),
    batch02_evidence_sha_after,
)

post_record(
    "Canonical programs.json unchanged",
    canonical_sha_after
    == canonical_sha_before,
    canonical_sha_after,
)


print()
print(
    "POST-WRITE BATCH 03 LOCK AUDIT"
)
print("-" * 138)


for label, passed, detail in post_checks:

    print(
        f"{label:<74}: "
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
        and BATCH03_LOCK.exists()
    ):

        BATCH03_LOCK.unlink()

    print()
    print("=" * 138)

    print(
        "STEP 172.2J SOUTH KOREA "
        "BATCH 03 IMMUTABLE LOCK BUILD: FAIL"
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
            "INVALID NEW BATCH 03 LOCK REMOVED"
        )

    print(
        "DO NOT RESEARCH BATCH 03"
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
# FINAL SUMMARY
# =====================================================================

print()
print("=" * 138)

print(
    "STEP 172.2J SOUTH KOREA "
    "BATCH 03 IMMUTABLE LOCK BUILD: PASS"
)

print()

print(
    "BATCH 03 LOCK FILE               : "
    "planning\\34_south_korea_program_research_batch03_lock.csv"
)

print(
    f"BATCH 03 LOCK SHA256             : "
    f"{batch03_sha}"
)

print(
    "BATCH 03 PROGRAMMES              : 36"
)

print(
    "BATCH 03 UNIVERSITIES            : 12"
)

print(
    "BATCH 03 PROGRAMME IDS           : "
    "prog_kr_073 -> prog_kr_108"
)

print(
    "BATCH 03 UNIVERSITY IDS          : "
    "uni_kr_025 -> uni_kr_036"
)

print(
    "PROGRAMMES PER UNIVERSITY        : 3"
)

print(
    "BATCH 03 RESEARCH VERIFIED       : 0"
)

print(
    "BATCH 03 IDENTITY VERIFIED       : 0"
)

print()

print(
    "WORKING SOURCE QUEUE             : "
    "planning\\33_south_korea_program_research_queue_batch02_applied.csv"
)

print(
    f"WORKING SOURCE SHA256            : "
    f"{EXPECTED_WORKING_SOURCE_SHA}"
)

print(
    "ALREADY VERIFIED                 : 72 / 150"
)

print(
    "ALREADY VERIFIED UNIVERSITIES    : 24 / 50"
)

print()

print(
    "BATCH 03 TARGET                  : 36 programmes / 12 universities"
)

print(
    "REMAINING AFTER BATCH 03         : 42 programmes"
)

print(
    "REMAINING AFTER BATCH 03         : 14 universities"
)

print()

print(
    "72-VERIFIED WORKING SOURCE       : UNCHANGED"
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
        "BATCH 03 LOCK STATUS            : "
        "EXISTING IDENTICAL FILE REUSED"
    )

else:

    print(
        "BATCH 03 LOCK STATUS            : "
        "NEW IMMUTABLE LOCK CREATED"
    )

print()

print(
    "NEXT: STEP 172.2K"
)

print(
    "SOUTH KOREA BATCH 03 "
    "OFFICIAL-SOURCE RESEARCH "
    "EVIDENCE BUILD"
)

print("=" * 138)
