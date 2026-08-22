from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path.cwd()

QUEUE = ROOT / "planning" / "27_south_korea_program_research_queue.csv"
BATCH = ROOT / "planning" / "28_south_korea_program_research_batch01_lock.csv"
EVIDENCE = ROOT / "planning" / "29_south_korea_program_research_batch01_evidence.csv"
CANONICAL = ROOT / "data" / "cleaned" / "programs.json"


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


EXPECTED_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(1, 37)
]

EXPECTED_PARENTS = {
    f"uni_kr_{i:03d}"
    for i in range(1, 13)
}

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


# These fields existed before programme research and must
# remain identical between queue, batch lock and evidence.
LOCKED_SEED_FIELDS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
]


# These are the required evidence fields after research.
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
        columns = list(reader.fieldnames or [])

    return rows, columns


def valid_url(value):
    value = text(value)

    if not value:
        return True

    try:
        parsed = urlparse(value)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


def compare_fields(
    left_rows,
    right_rows,
    fields,
):
    left_map = {
        text(row["program_id"]): row
        for row in left_rows
    }

    right_map = {
        text(row["program_id"]): row
        for row in right_rows
    }

    mismatches = []

    for program_id in EXPECTED_IDS:

        if program_id not in left_map:
            mismatches.append(
                f"{program_id}:missing-left"
            )
            continue

        if program_id not in right_map:
            mismatches.append(
                f"{program_id}:missing-right"
            )
            continue

        for field in fields:

            left_value = text(
                left_map[program_id].get(field)
            )

            right_value = text(
                right_map[program_id].get(field)
            )

            if left_value != right_value:
                mismatches.append(
                    f"{program_id}:{field}"
                )

    return mismatches


print("=" * 138)
print(
    "STEP 172.2B.2 - SOUTH KOREA BATCH 01 "
    "CORRECTED EVIDENCE PRE-APPLY AUDIT"
)
print("=" * 138)


# ----------------------------------------------------------------
# FILE / HASH LOCKS
# ----------------------------------------------------------------

for label, path in (
    ("Source queue exists", QUEUE),
    ("Batch lock exists", BATCH),
    ("Evidence file exists", EVIDENCE),
    ("Canonical programs.json exists", CANONICAL),
):
    record(
        label,
        path.exists(),
        path.relative_to(ROOT)
        if path.exists()
        else "NOT FOUND",
    )


if not all(
    path.exists()
    for path in (
        QUEUE,
        BATCH,
        EVIDENCE,
        CANONICAL,
    )
):
    print()
    print("REQUIRED FILE MISSING - STOP")
    sys.exit(1)


queue_sha = sha256(QUEUE)
batch_sha = sha256(BATCH)
evidence_sha = sha256(EVIDENCE)


record(
    "Queue SHA256 exact",
    queue_sha == EXPECTED_QUEUE_SHA,
    queue_sha,
)

record(
    "Batch lock SHA256 exact",
    batch_sha == EXPECTED_BATCH_SHA,
    batch_sha,
)

record(
    "Evidence SHA256 exact",
    evidence_sha == EXPECTED_EVIDENCE_SHA,
    evidence_sha,
)


# ----------------------------------------------------------------
# LOAD CSV FILES
# ----------------------------------------------------------------

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
    "Evidence columns = 31",
    len(evidence_cols) == 31,
    len(evidence_cols),
)

record(
    "Evidence schema exact",
    evidence_cols == EXPECTED_COLUMNS,
    (
        "exact"
        if evidence_cols == EXPECTED_COLUMNS
        else "column/order mismatch"
    ),
)


# ----------------------------------------------------------------
# PROGRAM ID LOCK
# ----------------------------------------------------------------

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


record(
    "Batch IDs exact/order exact",
    batch_ids == EXPECTED_IDS,
    (
        f"{batch_ids[0]} -> {batch_ids[-1]}"
        if batch_ids
        else "EMPTY"
    ),
)

record(
    "Evidence IDs exact/order exact",
    evidence_ids == EXPECTED_IDS,
    (
        f"{evidence_ids[0]} -> {evidence_ids[-1]}"
        if evidence_ids
        else "EMPTY"
    ),
)

record(
    "Evidence duplicate IDs = 0",
    len(evidence_ids) == len(set(evidence_ids)),
    (
        len(evidence_ids)
        - len(set(evidence_ids))
    ),
)

queue_id_set = set(queue_ids)

record(
    "Queue contains all Batch 01 IDs",
    all(
        program_id in queue_id_set
        for program_id in EXPECTED_IDS
    ),
    (
        f"{sum(program_id in queue_id_set for program_id in EXPECTED_IDS)} / 36"
    ),
)


# ----------------------------------------------------------------
# VERIFY BATCH LOCK IS AN EXACT SNAPSHOT OF THE QUEUE
# ----------------------------------------------------------------

queue_map = {
    text(row["program_id"]): row
    for row in queue_rows
}

batch_queue_mismatches = []

for batch_row in batch_rows:

    program_id = text(
        batch_row.get("program_id")
    )

    queue_row = queue_map.get(program_id)

    if queue_row is None:
        batch_queue_mismatches.append(
            f"{program_id}:missing-queue-row"
        )
        continue

    for column in batch_cols:

        batch_value = text(
            batch_row.get(column)
        )

        queue_value = text(
            queue_row.get(column)
        )

        if batch_value != queue_value:
            batch_queue_mismatches.append(
                f"{program_id}:{column}"
            )


record(
    "Batch lock exact snapshot of source queue",
    not batch_queue_mismatches,
    (
        "mismatches=0"
        if not batch_queue_mismatches
        else ", ".join(
            batch_queue_mismatches[:15]
        )
    ),
)


# ----------------------------------------------------------------
# EVIDENCE MUST PRESERVE ONLY IMMUTABLE SEED IDENTITY
#
# program_name / field_of_study / degree_level etc. are
# research outputs and therefore MUST NOT be compared against
# the pre-research blank queue.
# ----------------------------------------------------------------

evidence_batch_seed_mismatches = compare_fields(
    evidence_rows,
    batch_rows,
    LOCKED_SEED_FIELDS,
)

record(
    "Evidence preserves Batch 01 seed identity",
    not evidence_batch_seed_mismatches,
    (
        "mismatches=0"
        if not evidence_batch_seed_mismatches
        else ", ".join(
            evidence_batch_seed_mismatches[:15]
        )
    ),
)


evidence_queue_seed_mismatches = compare_fields(
    evidence_rows,
    queue_rows,
    LOCKED_SEED_FIELDS,
)

record(
    "Evidence preserves source queue seed identity",
    not evidence_queue_seed_mismatches,
    (
        "mismatches=0"
        if not evidence_queue_seed_mismatches
        else ", ".join(
            evidence_queue_seed_mismatches[:15]
        )
    ),
)


# ----------------------------------------------------------------
# PARENT / SLOT STRUCTURE
# ----------------------------------------------------------------

parent_counts = Counter(
    text(row.get("university_id"))
    for row in evidence_rows
)

record(
    "Evidence parent universities = 12",
    set(parent_counts) == EXPECTED_PARENTS,
    len(parent_counts),
)

record(
    "Exactly 3 programmes per parent",
    (
        set(parent_counts) == EXPECTED_PARENTS
        and all(
            parent_counts[parent] == 3
            for parent in EXPECTED_PARENTS
        )
    ),
    (
        f"{sum(parent_counts[p] == 3 for p in EXPECTED_PARENTS)} / 12"
    ),
)


slots_by_parent = defaultdict(set)

for row in evidence_rows:
    slots_by_parent[
        text(row.get("university_id"))
    ].add(
        text(row.get("program_slot"))
    )


bad_slots = [
    parent
    for parent in EXPECTED_PARENTS
    if slots_by_parent[parent]
    != {"1", "2", "3"}
]


record(
    "Parent programme slots exact 1/2/3",
    not bad_slots,
    (
        "all 12 parents"
        if not bad_slots
        else ", ".join(sorted(bad_slots))
    ),
)


# ----------------------------------------------------------------
# REQUIRED RESEARCH EVIDENCE
# ----------------------------------------------------------------

required_blanks = []

for row in evidence_rows:

    program_id = text(
        row.get("program_id")
    )

    for field in REQUIRED_EVIDENCE_FIELDS:

        if not text(row.get(field)):
            required_blanks.append(
                f"{program_id}:{field}"
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


# ----------------------------------------------------------------
# STATUS COUNTS
# ----------------------------------------------------------------

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
    == Counter({"verified": 36}),
    dict(identity_counts),
)

record(
    "Research status VERIFIED = 36",
    research_counts
    == Counter({"verified": 36}),
    dict(research_counts),
)

record(
    "International = 33 verified_yes / 3 unknown",
    international_counts
    == Counter({
        "verified_yes": 33,
        "unknown": 3,
    }),
    dict(international_counts),
)

record(
    "Degree = 27 Bachelor / 9 Master",
    degree_counts
    == Counter({
        "bachelor": 27,
        "master": 9,
    }),
    dict(degree_counts),
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
    "International unknown IDs exact",
    unknown_ids == EXPECTED_UNKNOWN_IDS,
    ", ".join(sorted(unknown_ids)),
)


# ----------------------------------------------------------------
# INTERNATIONAL APPLICATION URL RULE
# ----------------------------------------------------------------

verified_yes_missing_url = []
unknown_with_url = []

for row in evidence_rows:

    program_id = text(
        row.get("program_id")
    )

    status = norm(
        row.get(
            "international_applicants_status"
        )
    )

    url = text(
        row.get(
            "international_application_url"
        )
    )

    if status == "verified_yes" and not url:
        verified_yes_missing_url.append(
            program_id
        )

    if status == "unknown" and url:
        unknown_with_url.append(
            program_id
        )


record(
    "verified_yes missing international URL = 0",
    not verified_yes_missing_url,
    (
        "0"
        if not verified_yes_missing_url
        else ", ".join(
            verified_yes_missing_url
        )
    ),
)

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


# ----------------------------------------------------------------
# URL VALIDATION
# ----------------------------------------------------------------

URL_FIELDS = [
    "program_url",
    "programme_identity_evidence",
    "official_university_website",
    "international_application_url",
]

invalid_urls = []

for row in evidence_rows:

    program_id = text(
        row.get("program_id")
    )

    for field in URL_FIELDS:

        value = text(
            row.get(field)
        )

        if value and not valid_url(value):
            invalid_urls.append(
                f"{program_id}:{field}"
            )


record(
    "Invalid populated URLs = 0",
    not invalid_urls,
    (
        "0"
        if not invalid_urls
        else ", ".join(
            invalid_urls[:15]
        )
    ),
)


# ----------------------------------------------------------------
# OPTIONAL DETAIL COVERAGE
# ----------------------------------------------------------------

optional_fields = [
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
            text(row.get(field))
        )
        for row in evidence_rows
    )
    for field in optional_fields
}


record(
    "duration_years populated = 0",
    optional_counts["duration_years"] == 0,
    optional_counts["duration_years"],
)

record(
    "study_mode populated = 0",
    optional_counts["study_mode"] == 0,
    optional_counts["study_mode"],
)

record(
    "language_of_instruction populated = 6",
    optional_counts["language_of_instruction"] == 6,
    optional_counts["language_of_instruction"],
)

record(
    "tuition_fee populated = 3",
    optional_counts["tuition_fee"] == 3,
    optional_counts["tuition_fee"],
)

record(
    "minimum_gpa populated = 0",
    optional_counts["minimum_gpa"] == 0,
    optional_counts["minimum_gpa"],
)

record(
    "ielts_requirement populated = 0",
    optional_counts["ielts_requirement"] == 0,
    optional_counts["ielts_requirement"],
)

record(
    "toefl_requirement populated = 0",
    optional_counts["toefl_requirement"] == 0,
    optional_counts["toefl_requirement"],
)

record(
    "intake populated = 0",
    optional_counts["intake"] == 0,
    optional_counts["intake"],
)

record(
    "application_deadline populated = 0",
    optional_counts["application_deadline"] == 0,
    optional_counts["application_deadline"],
)


language_counts = Counter(
    (
        norm(
            row.get(
                "language_of_instruction"
            )
        )
        if text(
            row.get(
                "language_of_instruction"
            )
        )
        else "<blank>"
    )
    for row in evidence_rows
)


record(
    "Language evidence = 30 blank / 5 English / 1 Korean",
    language_counts
    == Counter({
        "<blank>": 30,
        "english": 5,
        "korean": 1,
    }),
    dict(language_counts),
)


# ----------------------------------------------------------------
# CANONICAL LOCK
# ----------------------------------------------------------------

with CANONICAL.open(
    "r",
    encoding="utf-8-sig",
) as f:
    canonical_rows = json.load(f)


record(
    "Canonical programmes = 600",
    isinstance(canonical_rows, list)
    and len(canonical_rows) == 600,
    (
        len(canonical_rows)
        if isinstance(canonical_rows, list)
        else "NOT A LIST"
    ),
)


canonical_kr_ids = []

if isinstance(canonical_rows, list):

    for row in canonical_rows:

        if not isinstance(row, dict):
            continue

        program_id = text(
            row.get(
                "program_id",
                row.get("programme_id", ""),
            )
        )

        if program_id.startswith(
            "prog_kr_"
        ):
            canonical_kr_ids.append(
                program_id
            )


record(
    "Existing South Korea canonical programmes = 0",
    len(canonical_kr_ids) == 0,
    len(canonical_kr_ids),
)


# ----------------------------------------------------------------
# FINAL REPORT
# ----------------------------------------------------------------

print()
print("AUDIT RESULTS")
print("-" * 138)

for label, passed, detail in checks:

    print(
        f"{label:<62}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


failed = [
    (label, detail)
    for label, passed, detail in checks
    if not passed
]


print()
print("=" * 138)


if failed:

    print(
        "STEP 172.2B.2 SOUTH KOREA "
        "BATCH 01 CORRECTED "
        "EVIDENCE PRE-APPLY AUDIT: FAIL"
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
        "STOP: DO NOT APPLY EVIDENCE "
        "TO THE QUEUE"
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
    "STEP 172.2B.2 SOUTH KOREA "
    "BATCH 01 CORRECTED "
    "EVIDENCE PRE-APPLY AUDIT: PASS"
)

print()

print(
    "SOURCE QUEUE                     : 150 / LOCK VERIFIED"
)
print(
    "BATCH 01 LOCK                    : 36 / LOCK VERIFIED"
)
print(
    "EVIDENCE                         : 36 / SHA VERIFIED"
)
print(
    "IMMUTABLE SEED IDENTITY          : VERIFIED"
)
print(
    "PROGRAMME IDENTITIES             : 36 / 36 VERIFIED"
)
print(
    "RESEARCH STATUS                  : 36 / 36 VERIFIED"
)
print(
    "INTERNATIONAL VERIFIED_YES       : 33"
)
print(
    "INTERNATIONAL UNKNOWN            : 3"
)
print(
    "UNKNOWN IDS                      : prog_kr_028, prog_kr_029, prog_kr_030"
)
print(
    "DEGREE LEVELS                    : 27 BACHELOR / 9 MASTER"
)
print(
    "CANONICAL programs.json          : 600 / UNCHANGED"
)
print(
    "SOUTH KOREA CANONICAL PROGRAMMES : 0"
)
print(
    "MONGODB WRITE PERFORMED          : False"
)

print()

print(
    "NEXT: STEP 172.2C"
)
print(
    "SAFE-APPLY BATCH 01 EVIDENCE "
    "TO A STAGED COPY OF THE "
    "150-ROW SOUTH KOREA QUEUE"
)

print("=" * 138)
