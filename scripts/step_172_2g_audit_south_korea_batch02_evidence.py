
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse


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


BATCH01_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(1, 37)
]

BATCH02_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(37, 73)
]

BATCH02_ID_SET = set(BATCH02_IDS)

REMAINING_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(73, 151)
]

EXPECTED_PARENTS = {
    f"uni_kr_{i:03d}"
    for i in range(13, 25)
}


IMMUTABLE_SEED_FIELDS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
]


REQUIRED_EVIDENCE_FIELDS = [
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
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
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


def valid_url(value):
    value = text(value)

    if not value:
        return False

    try:
        parsed = urlparse(value)

        return (
            parsed.scheme
            in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


print("=" * 138)
print(
    "STEP 172.2G - SOUTH KOREA BATCH 02 "
    "EVIDENCE PRE-APPLY AUDIT"
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
    print("AUDIT RESULTS")
    print("-" * 138)

    for label, passed, detail in checks:

        print(
            f"{label:<68}: "
            f"{'PASS' if passed else 'FAIL'}"
            f" | {detail}"
        )

    print()
    print("=" * 138)
    print(
        "STEP 172.2G SOUTH KOREA "
        "BATCH 02 EVIDENCE PRE-APPLY AUDIT: FAIL"
    )
    print(
        "STOP: REQUIRED FILE MISSING"
    )
    print("=" * 138)

    sys.exit(1)


# =====================================================================
# HASH LOCKS
# =====================================================================

working_sha_before = sha256(
    WORKING_SOURCE
)

batch_sha_before = sha256(
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
    batch_sha_before
    == EXPECTED_BATCH02_LOCK_SHA,
    batch_sha_before,
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

batch_rows, batch_cols = load_csv(
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
    len(batch_rows) == 36,
    len(batch_rows),
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
    batch_cols == EXPECTED_COLUMNS,
    len(batch_cols),
)

record(
    "Batch 02 evidence columns = 31",
    evidence_cols == EXPECTED_COLUMNS,
    len(evidence_cols),
)


# =====================================================================
# ID STRUCTURE
# =====================================================================

working_ids = [
    text(row.get("program_id"))
    for row in working_rows
]

batch_ids = [
    text(row.get("program_id"))
    for row in batch_rows
]

evidence_ids = [
    text(row.get("program_id"))
    for row in evidence_rows
]

expected_all_ids = [
    f"prog_kr_{i:03d}"
    for i in range(1, 151)
]


record(
    "Working source IDs exact",
    working_ids == expected_all_ids,
    (
        f"{working_ids[0]} -> {working_ids[-1]}"
        if working_ids
        else "EMPTY"
    ),
)

record(
    "Batch 02 lock IDs exact/order exact",
    batch_ids == BATCH02_IDS,
    (
        f"{batch_ids[0]} -> {batch_ids[-1]}"
        if batch_ids
        else "EMPTY"
    ),
)

record(
    "Evidence IDs exact/order exact",
    evidence_ids == BATCH02_IDS,
    (
        f"{evidence_ids[0]} -> {evidence_ids[-1]}"
        if evidence_ids
        else "EMPTY"
    ),
)

record(
    "Evidence duplicate IDs = 0",
    len(evidence_ids)
    == len(set(evidence_ids)),
    (
        len(evidence_ids)
        - len(set(evidence_ids))
    ),
)


working_map = {
    text(row["program_id"]): row
    for row in working_rows
}

batch_map = {
    text(row["program_id"]): row
    for row in batch_rows
}

evidence_map = {
    text(row["program_id"]): row
    for row in evidence_rows
}


# =====================================================================
# BATCH 02 LOCK MUST REMAIN AN EXACT SNAPSHOT OF CURRENT WORKING SOURCE
# =====================================================================

lock_source_mismatches = []


for pid in BATCH02_IDS:

    source_row = working_map.get(pid)
    lock_row = batch_map.get(pid)

    if source_row is None or lock_row is None:

        lock_source_mismatches.append(
            f"{pid}:missing-row"
        )

        continue

    for field in EXPECTED_COLUMNS:

        if text(
            source_row.get(field)
        ) != text(
            lock_row.get(field)
        ):

            lock_source_mismatches.append(
                f"{pid}:{field}"
            )


record(
    "Batch 02 lock exact working-source snapshot",
    not lock_source_mismatches,
    (
        "mismatches=0"
        if not lock_source_mismatches
        else ", ".join(
            lock_source_mismatches[:15]
        )
    ),
)


# =====================================================================
# EVIDENCE MUST PRESERVE IMMUTABLE SEED IDENTITY
#
# program_name, field_of_study, degree_level etc. are research outputs
# and intentionally may differ from the pre-research lock.
# =====================================================================

evidence_seed_mismatches = []


for pid in BATCH02_IDS:

    lock_row = batch_map.get(pid)
    evidence_row = evidence_map.get(pid)

    if lock_row is None or evidence_row is None:

        evidence_seed_mismatches.append(
            f"{pid}:missing-row"
        )

        continue

    for field in IMMUTABLE_SEED_FIELDS:

        if text(
            lock_row.get(field)
        ) != text(
            evidence_row.get(field)
        ):

            evidence_seed_mismatches.append(
                f"{pid}:{field}"
            )


record(
    "Evidence preserves Batch 02 immutable seed identity",
    not evidence_seed_mismatches,
    (
        "mismatches=0"
        if not evidence_seed_mismatches
        else ", ".join(
            evidence_seed_mismatches[:15]
        )
    ),
)


# =====================================================================
# PARENT / SLOT STRUCTURE
# =====================================================================

parent_counts = Counter(
    text(
        row.get(
            "university_id"
        )
    )
    for row in evidence_rows
)


record(
    "Evidence parent universities = 12",
    set(parent_counts)
    == EXPECTED_PARENTS,
    len(parent_counts),
)

record(
    "Exactly 3 programmes per parent",
    (
        set(parent_counts)
        == EXPECTED_PARENTS
        and all(
            parent_counts[parent]
            == 3
            for parent
            in EXPECTED_PARENTS
        )
    ),
    (
        f"{sum(parent_counts[p] == 3 for p in EXPECTED_PARENTS)} / 12"
    ),
)


slots_by_parent = defaultdict(set)


for row in evidence_rows:

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
        EXPECTED_PARENTS
    )
    if slots_by_parent[parent]
    != {"1", "2", "3"}
]


record(
    "Parent programme slots exact 1 / 2 / 3",
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
# REQUIRED RESEARCH FIELDS
# =====================================================================

required_blanks = []


for row in evidence_rows:

    pid = text(
        row.get(
            "program_id"
        )
    )

    for field in REQUIRED_EVIDENCE_FIELDS:

        if not text(
            row.get(field)
        ):

            required_blanks.append(
                f"{pid}:{field}"
            )


record(
    "Required evidence blanks = 0",
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
# STATUS AUDIT
# =====================================================================

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

degree_counts = Counter(
    norm(
        row.get(
            "degree_level"
        )
    )
    for row in evidence_rows
)


record(
    "Programme identity VERIFIED = 36",
    identity_counts
    == Counter({
        "verified": 36,
    }),
    dict(identity_counts),
)

record(
    "Research status VERIFIED = 36",
    research_counts
    == Counter({
        "verified": 36,
    }),
    dict(research_counts),
)

record(
    "International verified_yes = 36",
    international_counts
    == Counter({
        "verified_yes": 36,
    }),
    dict(international_counts),
)

record(
    "Degree level Bachelor = 36",
    degree_counts
    == Counter({
        "bachelor": 36,
    }),
    dict(degree_counts),
)


# =====================================================================
# INTERNATIONAL URL CONSISTENCY
# =====================================================================

missing_international_urls = []


for row in evidence_rows:

    if (
        norm(
            row.get(
                "international_applicants_status"
            )
        )
        == "verified_yes"
        and not text(
            row.get(
                "international_application_url"
            )
        )
    ):

        missing_international_urls.append(
            text(
                row.get(
                    "program_id"
                )
            )
        )


record(
    "verified_yes missing international URL = 0",
    not missing_international_urls,
    (
        "0"
        if not missing_international_urls
        else ", ".join(
            missing_international_urls
        )
    ),
)


# =====================================================================
# URL FORMAT AUDIT
# =====================================================================

URL_FIELDS = [
    "program_url",
    "programme_identity_evidence",
    "official_university_website",
    "international_application_url",
]


invalid_urls = []


for row in evidence_rows:

    pid = text(
        row.get(
            "program_id"
        )
    )

    for field in URL_FIELDS:

        value = text(
            row.get(field)
        )

        if not valid_url(value):

            invalid_urls.append(
                f"{pid}:{field}"
            )


record(
    "Invalid required URLs = 0",
    not invalid_urls,
    (
        "0"
        if not invalid_urls
        else ", ".join(
            invalid_urls[:15]
        )
    ),
)


# =====================================================================
# OPTIONAL DETAIL COVERAGE
# =====================================================================

OPTIONAL_FIELDS = [
    "duration_years",
    "study_mode",
    "language_of_instruction",
    "tuition_fee",
    "minimum_gpa",
    "ielts_requirement",
    "toefl_requirement",
    "intake",
    "application_deadline",
]


optional_counts = {
    field: sum(
        bool(
            text(
                row.get(field)
            )
        )
        for row in evidence_rows
    )
    for field in OPTIONAL_FIELDS
}


for field in OPTIONAL_FIELDS:

    record(
        f"{field} populated = 0",
        optional_counts[field] == 0,
        optional_counts[field],
    )


# =====================================================================
# ENSURE BATCH 01 REMAINS VERIFIED IN WORKING SOURCE
# =====================================================================

batch01_identity_verified = {
    pid
    for pid in BATCH01_IDS
    if norm(
        working_map[
            pid
        ].get(
            "programme_identity_status"
        )
    )
    == "verified"
}

batch01_research_verified = {
    pid
    for pid in BATCH01_IDS
    if norm(
        working_map[
            pid
        ].get(
            "research_status"
        )
    )
    == "verified"
}


record(
    "Working source Batch 01 identity remains VERIFIED = 36",
    batch01_identity_verified
    == set(BATCH01_IDS),
    len(batch01_identity_verified),
)

record(
    "Working source Batch 01 research remains VERIFIED = 36",
    batch01_research_verified
    == set(BATCH01_IDS),
    len(batch01_research_verified),
)


# =====================================================================
# BATCH 02 MUST STILL BE UNAPPLIED IN CURRENT WORKING SOURCE
# =====================================================================

batch02_current_verified_research = [
    pid
    for pid in BATCH02_IDS
    if norm(
        working_map[
            pid
        ].get(
            "research_status"
        )
    )
    == "verified"
]

batch02_current_verified_identity = [
    pid
    for pid in BATCH02_IDS
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
    "Batch 02 not yet VERIFIED in working source",
    not batch02_current_verified_research,
    (
        "0 verified"
        if not batch02_current_verified_research
        else ", ".join(
            batch02_current_verified_research
        )
    ),
)

record(
    "Batch 02 identity not yet applied to working source",
    not batch02_current_verified_identity,
    (
        "0 verified"
        if not batch02_current_verified_identity
        else ", ".join(
            batch02_current_verified_identity
        )
    ),
)


# =====================================================================
# REMAINING 78 ROWS MUST STILL MATCH ORIGINAL WORKING SOURCE STATE
#
# We do not require their statuses to be blank.
# We only verify that none are VERIFIED yet.
# =====================================================================

remaining_verified = [
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
    not remaining_verified,
    (
        "78 / 78 outside VERIFIED set"
        if not remaining_verified
        else ", ".join(
            remaining_verified[:15]
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
        and len(canonical_rows)
        == 600
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
# VERIFY READ-ONLY AUDIT DID NOT MODIFY INPUTS
# =====================================================================

working_sha_after = sha256(
    WORKING_SOURCE
)

batch_sha_after = sha256(
    BATCH02_LOCK
)

evidence_sha_after = sha256(
    BATCH02_EVIDENCE
)

canonical_sha_after = sha256(
    CANONICAL
)


record(
    "Working source unchanged during audit",
    (
        working_sha_after
        == working_sha_before
        == EXPECTED_WORKING_SOURCE_SHA
    ),
    working_sha_after,
)

record(
    "Batch 02 lock unchanged during audit",
    (
        batch_sha_after
        == batch_sha_before
        == EXPECTED_BATCH02_LOCK_SHA
    ),
    batch_sha_after,
)

record(
    "Batch 02 evidence unchanged during audit",
    (
        evidence_sha_after
        == evidence_sha_before
        == EXPECTED_BATCH02_EVIDENCE_SHA
    ),
    evidence_sha_after,
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
        f"{label:<70}: "
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
        "STEP 172.2G SOUTH KOREA "
        "BATCH 02 EVIDENCE PRE-APPLY AUDIT: FAIL"
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
        "STOP: DO NOT APPLY BATCH 02 EVIDENCE"
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
    "STEP 172.2G SOUTH KOREA "
    "BATCH 02 EVIDENCE PRE-APPLY AUDIT: PASS"
)

print()

print(
    "WORKING SOURCE ROWS               : 150"
)

print(
    f"WORKING SOURCE SHA256             : {working_sha_after}"
)

print(
    "BATCH 01 VERIFIED                 : 36 / 36"
)

print(
    "BATCH 02 LOCK ROWS                : 36"
)

print(
    f"BATCH 02 LOCK SHA256              : {batch_sha_after}"
)

print(
    "BATCH 02 EVIDENCE ROWS            : 36"
)

print(
    f"BATCH 02 EVIDENCE SHA256          : {evidence_sha_after}"
)

print(
    "IMMUTABLE SEED IDENTITY           : VERIFIED"
)

print(
    "PROGRAMME IDENTITIES VERIFIED     : 36 / 36"
)

print(
    "RESEARCH STATUS VERIFIED          : 36 / 36"
)

print(
    "INTERNATIONAL VERIFIED_YES        : 36"
)

print(
    "INTERNATIONAL UNKNOWN             : 0"
)

print(
    "DEGREE LEVELS                     : 36 BACHELOR"
)

print(
    "OPTIONAL DETAIL FIELDS            : UNPOPULATED / PRESERVED"
)

print(
    "REMAINING AFTER BATCH 02          : 78"
)

print()

print(
    "WORKING SOURCE QUEUE              : UNCHANGED"
)

print(
    "BATCH 02 LOCK                     : UNCHANGED"
)

print(
    "BATCH 02 EVIDENCE                 : UNCHANGED"
)

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
    "NEXT: STEP 172.2H"
)

print(
    "SAFE-APPLY BATCH 02 EVIDENCE TO "
    "A NEW STAGED 150-ROW SOUTH KOREA QUEUE"
)

print("=" * 138)
