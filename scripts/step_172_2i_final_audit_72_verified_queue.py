from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path.cwd()
PLANNING = ROOT / "planning"

BATCH01_STAGED = (
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

CURRENT_STAGED = (
    PLANNING
    / "33_south_korea_program_research_queue_batch02_applied.csv"
)

CANONICAL = (
    ROOT
    / "data"
    / "cleaned"
    / "programs.json"
)


EXPECTED_BATCH01_STAGED_SHA = (
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

EXPECTED_CURRENT_STAGED_SHA = (
    "43b94582702e5f0f03eff806c9c991cd"
    "ed96f33dd1f7c91d71e54afb0e072a9c"
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

VERIFIED_IDS = {
    f"prog_kr_{i:03d}"
    for i in range(1, 73)
}

REMAINING_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(73, 151)
]

EXPECTED_VERIFIED_PARENTS = {
    f"uni_kr_{i:03d}"
    for i in range(1, 25)
}

EXPECTED_UNKNOWN_IDS = {
    "prog_kr_028",
    "prog_kr_029",
    "prog_kr_030",
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
    "STEP 172.2I - SOUTH KOREA "
    "BATCH 01 + BATCH 02 "
    "72-VERIFIED STAGED QUEUE FINAL AUDIT"
)

print("=" * 138)


# =====================================================================
# REQUIRED FILES
# =====================================================================

required_files = [
    BATCH01_STAGED,
    BATCH02_LOCK,
    BATCH02_EVIDENCE,
    CURRENT_STAGED,
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
    print("AUDIT RESULTS")
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
        "STEP 172.2I SOUTH KOREA "
        "72-VERIFIED STAGED QUEUE FINAL AUDIT: FAIL"
    )

    print(
        "STOP: REQUIRED FILE MISSING"
    )

    print("=" * 138)

    sys.exit(1)


# =====================================================================
# HASH LOCKS
# =====================================================================

batch01_sha_before = sha256(
    BATCH01_STAGED
)

batch02_lock_sha_before = sha256(
    BATCH02_LOCK
)

batch02_evidence_sha_before = sha256(
    BATCH02_EVIDENCE
)

current_sha_before = sha256(
    CURRENT_STAGED
)

canonical_sha_before = sha256(
    CANONICAL
)


record(
    "Batch 01 staged SHA256 exact",
    batch01_sha_before
    == EXPECTED_BATCH01_STAGED_SHA,
    batch01_sha_before,
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

record(
    "Current 72-verified staged SHA256 exact",
    current_sha_before
    == EXPECTED_CURRENT_STAGED_SHA,
    current_sha_before,
)


# =====================================================================
# LOAD FILES
# =====================================================================

batch01_rows, batch01_cols = load_csv(
    BATCH01_STAGED
)

batch02_lock_rows, batch02_lock_cols = load_csv(
    BATCH02_LOCK
)

batch02_evidence_rows, batch02_evidence_cols = load_csv(
    BATCH02_EVIDENCE
)

current_rows, current_cols = load_csv(
    CURRENT_STAGED
)


record(
    "Batch 01 staged rows = 150",
    len(batch01_rows) == 150,
    len(batch01_rows),
)

record(
    "Batch 02 lock rows = 36",
    len(batch02_lock_rows) == 36,
    len(batch02_lock_rows),
)

record(
    "Batch 02 evidence rows = 36",
    len(batch02_evidence_rows) == 36,
    len(batch02_evidence_rows),
)

record(
    "Current staged rows = 150",
    len(current_rows) == 150,
    len(current_rows),
)


record(
    "Batch 01 staged schema exact",
    batch01_cols == EXPECTED_COLUMNS,
    len(batch01_cols),
)

record(
    "Batch 02 lock schema exact",
    batch02_lock_cols == EXPECTED_COLUMNS,
    len(batch02_lock_cols),
)

record(
    "Batch 02 evidence schema exact",
    batch02_evidence_cols == EXPECTED_COLUMNS,
    len(batch02_evidence_cols),
)

record(
    "Current staged schema exact",
    current_cols == EXPECTED_COLUMNS,
    len(current_cols),
)


# =====================================================================
# IDS
# =====================================================================

current_ids = [
    text(row.get("program_id"))
    for row in current_rows
]

batch02_lock_ids = [
    text(row.get("program_id"))
    for row in batch02_lock_rows
]

batch02_evidence_ids = [
    text(row.get("program_id"))
    for row in batch02_evidence_rows
]


record(
    "Current staged IDs exact",
    current_ids == ALL_IDS,
    (
        f"{current_ids[0]} -> {current_ids[-1]}"
        if current_ids
        else "EMPTY"
    ),
)

record(
    "Batch 02 lock IDs exact",
    batch02_lock_ids == BATCH02_IDS,
    (
        f"{batch02_lock_ids[0]} -> "
        f"{batch02_lock_ids[-1]}"
        if batch02_lock_ids
        else "EMPTY"
    ),
)

record(
    "Batch 02 evidence IDs exact",
    batch02_evidence_ids == BATCH02_IDS,
    (
        f"{batch02_evidence_ids[0]} -> "
        f"{batch02_evidence_ids[-1]}"
        if batch02_evidence_ids
        else "EMPTY"
    ),
)


batch01_map = {
    text(row["program_id"]): row
    for row in batch01_rows
}

batch02_evidence_map = {
    text(row["program_id"]): row
    for row in batch02_evidence_rows
}

current_map = {
    text(row["program_id"]): row
    for row in current_rows
}


# =====================================================================
# BATCH 01 PRESERVATION
# =====================================================================

batch01_mismatches = []


for pid in BATCH01_IDS:

    if not rows_equal(
        current_map[pid],
        batch01_map[pid],
    ):

        for column in EXPECTED_COLUMNS:

            if text(
                current_map[
                    pid
                ].get(column)
            ) != text(
                batch01_map[
                    pid
                ].get(column)
            ):

                batch01_mismatches.append(
                    f"{pid}:{column}"
                )


record(
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
# BATCH 02 MUST EXACTLY MATCH EVIDENCE
# =====================================================================

batch02_mismatches = []


for pid in BATCH02_IDS:

    if not rows_equal(
        current_map[pid],
        batch02_evidence_map[pid],
    ):

        for column in EXPECTED_COLUMNS:

            if text(
                current_map[
                    pid
                ].get(column)
            ) != text(
                batch02_evidence_map[
                    pid
                ].get(column)
            ):

                batch02_mismatches.append(
                    f"{pid}:{column}"
                )


record(
    "Batch 02 rows exactly equal evidence",
    not batch02_mismatches,
    (
        "36 / 36"
        if not batch02_mismatches
        else ", ".join(
            batch02_mismatches[:15]
        )
    ),
)


# =====================================================================
# REMAINING 78 MUST STILL MATCH PRE-BATCH02 STAGED SOURCE
# =====================================================================

remaining_mismatches = []


for pid in REMAINING_IDS:

    if not rows_equal(
        current_map[pid],
        batch01_map[pid],
    ):

        for column in EXPECTED_COLUMNS:

            if text(
                current_map[
                    pid
                ].get(column)
            ) != text(
                batch01_map[
                    pid
                ].get(column)
            ):

                remaining_mismatches.append(
                    f"{pid}:{column}"
                )


record(
    "Remaining 78 rows preserved exactly",
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
# VERIFIED SET
# =====================================================================

verified_research_ids = {
    pid
    for pid in ALL_IDS
    if norm(
        current_map[
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
        current_map[
            pid
        ].get(
            "programme_identity_status"
        )
    )
    == "verified"
}


record(
    "Verified research IDs exact = prog_kr_001 -> 072",
    verified_research_ids
    == VERIFIED_IDS,
    len(verified_research_ids),
)

record(
    "Verified identity IDs exact = prog_kr_001 -> 072",
    verified_identity_ids
    == VERIFIED_IDS,
    len(verified_identity_ids),
)


remaining_verified = [
    pid
    for pid in REMAINING_IDS
    if (
        norm(
            current_map[
                pid
            ].get(
                "research_status"
            )
        )
        == "verified"
        or norm(
            current_map[
                pid
            ].get(
                "programme_identity_status"
            )
        )
        == "verified"
    )
]


record(
    "Remaining 78 rows outside VERIFIED set",
    not remaining_verified,
    (
        "78 / 78"
        if not remaining_verified
        else ", ".join(
            remaining_verified[:15]
        )
    ),
)


# =====================================================================
# VERIFIED UNIVERSITY STRUCTURE
# =====================================================================

verified_parent_counts = Counter(
    text(
        current_map[
            pid
        ].get(
            "university_id"
        )
    )
    for pid in VERIFIED_IDS
)


record(
    "Verified parent universities exact = 24",
    set(
        verified_parent_counts
    )
    == EXPECTED_VERIFIED_PARENTS,
    len(
        verified_parent_counts
    ),
)


record(
    "Exactly 3 verified programmes per university",
    (
        set(
            verified_parent_counts
        )
        == EXPECTED_VERIFIED_PARENTS
        and all(
            verified_parent_counts[parent]
            == 3
            for parent
            in EXPECTED_VERIFIED_PARENTS
        )
    ),
    (
        f"{sum(verified_parent_counts[p] == 3 for p in EXPECTED_VERIFIED_PARENTS)} / 24"
    ),
)


slots_by_parent = defaultdict(set)


for pid in VERIFIED_IDS:

    row = current_map[
        pid
    ]

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
        EXPECTED_VERIFIED_PARENTS
    )
    if slots_by_parent[parent]
    != {"1", "2", "3"}
]


record(
    "Verified university programme slots exact 1 / 2 / 3",
    not bad_slots,
    (
        "24 / 24"
        if not bad_slots
        else ", ".join(
            bad_slots
        )
    ),
)


# =====================================================================
# AGGREGATE INTERNATIONAL STATUS
# =====================================================================

international_counts = Counter(
    norm(
        current_map[
            pid
        ].get(
            "international_applicants_status"
        )
    )
    for pid in VERIFIED_IDS
)


record(
    "Verified international = 69 verified_yes / 3 unknown",
    international_counts
    == Counter({
        "verified_yes": 69,
        "unknown": 3,
    }),
    dict(
        international_counts
    ),
)


unknown_ids = {
    pid
    for pid in VERIFIED_IDS
    if norm(
        current_map[
            pid
        ].get(
            "international_applicants_status"
        )
    )
    == "unknown"
}


record(
    "Unknown international IDs exact",
    unknown_ids
    == EXPECTED_UNKNOWN_IDS,
    ", ".join(
        sorted(
            unknown_ids
        )
    ),
)


verified_yes_missing_url = [
    pid
    for pid in VERIFIED_IDS
    if (
        norm(
            current_map[
                pid
            ].get(
                "international_applicants_status"
            )
        )
        == "verified_yes"
        and not text(
            current_map[
                pid
            ].get(
                "international_application_url"
            )
        )
    )
]


record(
    "verified_yes missing international URL = 0",
    not verified_yes_missing_url,
    (
        "0"
        if not verified_yes_missing_url
        else ", ".join(
            verified_yes_missing_url[:15]
        )
    ),
)


unknown_with_url = [
    pid
    for pid in VERIFIED_IDS
    if (
        norm(
            current_map[
                pid
            ].get(
                "international_applicants_status"
            )
        )
        == "unknown"
        and text(
            current_map[
                pid
            ].get(
                "international_application_url"
            )
        )
    )
]


record(
    "unknown with international URL = 0",
    not unknown_with_url,
    (
        "0"
        if not unknown_with_url
        else ", ".join(
            unknown_with_url
        )
    ),
)


# =====================================================================
# DEGREE DISTRIBUTION
# =====================================================================

degree_counts = Counter(
    norm(
        current_map[
            pid
        ].get(
            "degree_level"
        )
    )
    for pid in VERIFIED_IDS
)


record(
    "Verified degree levels = 63 Bachelor / 9 Master",
    degree_counts
    == Counter({
        "bachelor": 63,
        "master": 9,
    }),
    dict(
        degree_counts
    ),
)


# =====================================================================
# REQUIRED VERIFIED RESEARCH FIELDS
# =====================================================================

REQUIRED_FIELDS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
    "program_name",
    "field_of_study",
    "degree_level",
    "program_url",
    "programme_identity_status",
    "programme_identity_evidence",
    "official_university_website",
    "research_status",
    "research_note",
    "last_verified_at",
    "international_applicants_status",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


required_blanks = []


for pid in VERIFIED_IDS:

    row = current_map[
        pid
    ]

    for field in REQUIRED_FIELDS:

        if not text(
            row.get(
                field
            )
        ):

            required_blanks.append(
                f"{pid}:{field}"
            )


record(
    "Required verified evidence blanks = 0",
    not required_blanks,
    (
        "0"
        if not required_blanks
        else ", ".join(
            required_blanks[:15]
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
        current_ids
    ).items()
    if count > 1
]


record(
    "Duplicate programme IDs = 0",
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
    "Canonical programmes remain 600",
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
    "South Korea canonical programmes remain 0",
    len(
        canonical_kr_ids
    )
    == 0,
    len(
        canonical_kr_ids
    ),
)


# =====================================================================
# VERIFY READ-ONLY AUDIT CHANGED NOTHING
# =====================================================================

batch01_sha_after = sha256(
    BATCH01_STAGED
)

batch02_lock_sha_after = sha256(
    BATCH02_LOCK
)

batch02_evidence_sha_after = sha256(
    BATCH02_EVIDENCE
)

current_sha_after = sha256(
    CURRENT_STAGED
)

canonical_sha_after = sha256(
    CANONICAL
)


record(
    "Batch 01 staged unchanged during audit",
    (
        batch01_sha_after
        == batch01_sha_before
        == EXPECTED_BATCH01_STAGED_SHA
    ),
    batch01_sha_after,
)

record(
    "Batch 02 lock unchanged during audit",
    (
        batch02_lock_sha_after
        == batch02_lock_sha_before
        == EXPECTED_BATCH02_LOCK_SHA
    ),
    batch02_lock_sha_after,
)

record(
    "Batch 02 evidence unchanged during audit",
    (
        batch02_evidence_sha_after
        == batch02_evidence_sha_before
        == EXPECTED_BATCH02_EVIDENCE_SHA
    ),
    batch02_evidence_sha_after,
)

record(
    "Current staged queue unchanged during audit",
    (
        current_sha_after
        == current_sha_before
        == EXPECTED_CURRENT_STAGED_SHA
    ),
    current_sha_after,
)

record(
    "Canonical programs.json unchanged during audit",
    canonical_sha_after
    == canonical_sha_before,
    canonical_sha_after,
)


# =====================================================================
# FINAL REPORT
# =====================================================================

print()
print("AUDIT RESULTS")
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


print()
print("=" * 138)


if failed:

    print(
        "STEP 172.2I SOUTH KOREA "
        "72-VERIFIED STAGED QUEUE FINAL AUDIT: FAIL"
    )

    print(
        f"FAILED CHECKS: "
        f"{len(failed)}"
    )

    for label, detail in failed:

        print(
            f" - {label}: {detail}"
        )

    print()
    print(
        "STOP: DO NOT LOCK BATCH 03"
    )

    print(
        "DO NOT WRITE programs.json"
    )

    print(
        "DO NOT WRITE MONGODB"
    )

    print("=" * 138)

    sys.exit(1)


print(
    "STEP 172.2I SOUTH KOREA "
    "72-VERIFIED STAGED QUEUE FINAL AUDIT: PASS"
)

print()

print(
    "CURRENT WORKING SOURCE            : "
    "planning\\33_south_korea_program_research_queue_batch02_applied.csv"
)

print(
    f"CURRENT WORKING SOURCE SHA256     : "
    f"{current_sha_after}"
)

print(
    "WORKING SOURCE ROWS               : 150"
)

print(
    "WORKING SOURCE COLUMNS            : 31"
)

print()

print(
    "BATCH 01 VERIFIED                 : 36 / 36"
)

print(
    "BATCH 02 VERIFIED                 : 36 / 36"
)

print(
    "TOTAL VERIFIED PROGRAMMES         : 72 / 150"
)

print(
    "TOTAL VERIFIED UNIVERSITIES       : 24 / 50"
)

print(
    "REMAINING PROGRAMMES              : 78"
)

print(
    "REMAINING UNIVERSITIES            : 26"
)

print()

print(
    "PROGRAMME IDENTITIES VERIFIED     : 72 / 72"
)

print(
    "RESEARCH STATUS VERIFIED          : 72 / 72"
)

print(
    "INTERNATIONAL VERIFIED_YES        : 69"
)

print(
    "INTERNATIONAL UNKNOWN             : 3"
)

print(
    "UNKNOWN IDS                       : "
    "prog_kr_028, prog_kr_029, prog_kr_030"
)

print(
    "DEGREE LEVELS                     : "
    "63 BACHELOR / 9 MASTER"
)

print()

print(
    "REMAINING VERIFIED LEAKAGE        : 0"
)

print(
    "DUPLICATE PROGRAMME IDS           : 0"
)

print()

print(
    "CANONICAL programs.json           : UNCHANGED / 600"
)

print(
    "SOUTH KOREA CANONICAL PROGRAMMES  : 0"
)

print(
    "MONGODB WRITE PERFORMED           : False"
)

print()

print(
    "NEXT: STEP 172.2J"
)

print(
    "LOCK SOUTH KOREA BATCH 03 "
    "FROM THE 72-VERIFIED WORKING SOURCE"
)

print(
    "BATCH 03 TARGET                  : "
    "prog_kr_073 -> prog_kr_108"
)

print(
    "BATCH 03 UNIVERSITIES            : "
    "uni_kr_025 -> uni_kr_036"
)

print(
    "BATCH 03 SIZE                    : "
    "36 programmes / 12 universities"
)

print("=" * 138)
