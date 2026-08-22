import csv
import json
import shutil
import sys

from collections import Counter
from datetime import datetime
from pathlib import Path


# ============================================================
# Paths
# ============================================================

SCRIPTS_DIR = Path("scripts").resolve()

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS_DIR),
    )

import transform_programs as tp


EXISTING_JSON = Path(
    "data/cleaned/programs.json"
)

MACAU_PROGRAMS = Path(
    "data/cleaned/macau_programs_final_ready.csv"
)

MACAU_INTERNATIONAL = Path(
    "data/cleaned/"
    "macau_program_international_merge_ready.csv"
)

STAGING_JSON = Path(
    "data/cleaned/"
    "programs_with_macau_staging.json"
)

BACKUP_DIR = Path(
    "data/backups/step_170_2f"
)


EXPECTED_EXISTING = 336
EXPECTED_MACAU = 21
EXPECTED_STAGING = 357


EXPECTED_PROGRAM_COLUMNS = [
    "program_id",
    "university_id",
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
    "collected_at",
    "last_verified_at",
    "freshness_status",
]


EXPECTED_INTERNATIONAL_COLUMNS = [
    "program_id",
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


def clean(value):
    return str(value or "").strip()


def prefix(program_id):

    parts = clean(
        program_id
    ).split("_")

    if len(parts) >= 3:
        return "_".join(
            parts[:2]
        )

    return "unknown"


def csv_optional(value):

    value = clean(value)

    if value == "":
        return None

    return value


print("=" * 110)
print(
    "STEP 170.2F - MACAU SAFE "
    "PROGRAMS.JSON STAGING MERGE"
)
print("=" * 110)


# ============================================================
# Source existence checks
# ============================================================

for path in [
    EXISTING_JSON,
    MACAU_PROGRAMS,
    MACAU_INTERNATIONAL,
]:

    if not path.exists():

        raise FileNotFoundError(
            f"Required source missing: {path}"
        )


# ============================================================
# Load existing canonical programmes
# ============================================================

with EXISTING_JSON.open(
    "r",
    encoding="utf-8",
) as file:

    existing = json.load(file)


if not isinstance(
    existing,
    list,
):

    raise ValueError(
        "programs.json must contain a JSON list."
    )


existing_ids = [
    clean(
        row.get("program_id")
    )
    for row in existing
]


existing_duplicates = (
    len(existing_ids)
    - len(set(existing_ids))
)


print(
    "Existing programs.json rows       :",
    len(existing),
)

print(
    "Existing duplicate IDs            :",
    existing_duplicates,
)


if len(existing) != EXPECTED_EXISTING:

    raise ValueError(
        f"Expected existing programs.json "
        f"count {EXPECTED_EXISTING}, "
        f"found {len(existing)}."
    )


if existing_duplicates != 0:

    raise ValueError(
        "Existing programs.json contains "
        "duplicate program IDs."
    )


existing_macau = [
    program_id
    for program_id in existing_ids
    if program_id.startswith(
        "prog_mo_"
    )
]


print(
    "Existing Macau IDs                :",
    len(existing_macau),
)


if existing_macau:

    raise ValueError(
        "Safety stop: programs.json already "
        "contains Macau programme IDs."
    )


# Keep a deep data-equivalent reference for
# preservation verification later.
existing_snapshot = json.loads(
    json.dumps(
        existing,
        ensure_ascii=False,
    )
)


# ============================================================
# Load Macau 21-column source
# ============================================================

with MACAU_PROGRAMS.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    programme_headers = (
        reader.fieldnames or []
    )

    programme_rows = list(
        reader
    )


if programme_headers != EXPECTED_PROGRAM_COLUMNS:

    raise ValueError(
        "Macau programme CSV is not the "
        "exact canonical 21-column schema."
    )


if len(programme_rows) != EXPECTED_MACAU:

    raise ValueError(
        f"Expected {EXPECTED_MACAU} Macau "
        f"programme rows, found "
        f"{len(programme_rows)}."
    )


# ============================================================
# Load international merge source
# ============================================================

with MACAU_INTERNATIONAL.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    international_headers = (
        reader.fieldnames or []
    )

    international_rows = list(
        reader
    )


if (
    international_headers
    != EXPECTED_INTERNATIONAL_COLUMNS
):

    raise ValueError(
        "Macau international CSV is not "
        "the exact 5-column merge schema."
    )


if len(
    international_rows
) != EXPECTED_MACAU:

    raise ValueError(
        "Expected exactly 21 Macau "
        "international rows."
    )


international_by_id = {
    clean(
        row["program_id"]
    ): row
    for row in international_rows
}


if (
    len(international_by_id)
    != EXPECTED_MACAU
):

    raise ValueError(
        "Duplicate programme IDs found in "
        "Macau international merge file."
    )


# ============================================================
# Re-transform programme CSV
#
# CSV blanks are "".
# Existing transformer expects optional blanks as None.
# ============================================================

valid_university_ids = (
    tp.load_valid_university_ids()
)


macau_documents = []


for row_number, row in enumerate(
    programme_rows,
    start=2,
):

    normalized = {
        field: csv_optional(
            row.get(field)
        )
        for field in EXPECTED_PROGRAM_COLUMNS
    }


    transformed = tp.transform_program(
        raw_record=normalized,
        row_number=row_number,
        valid_university_ids=(
            valid_university_ids
        ),
    )


    program_id = clean(
        transformed.get(
            "program_id"
        )
    )


    if not program_id.startswith(
        "prog_mo_"
    ):

        raise ValueError(
            f"Unexpected Macau programme ID: "
            f"{program_id}"
        )


    international = (
        international_by_id.get(
            program_id
        )
    )


    if international is None:

        raise ValueError(
            f"{program_id}: international "
            "merge row missing."
        )


    # --------------------------------------------------------
    # Preserve the 21 canonical fields, then append only the
    # four international programme-level fields used by API/DB.
    # --------------------------------------------------------

    transformed[
        "international_applicants_status"
    ] = clean(
        international.get(
            "international_applicants_status"
        )
    )

    transformed[
        "international_application_url"
    ] = clean(
        international.get(
            "international_application_url"
        )
    )

    transformed[
        "international_requirements_note"
    ] = clean(
        international.get(
            "international_requirements_note"
        )
    )

    transformed[
        "international_applicants_last_verified_at"
    ] = clean(
        international.get(
            "international_applicants_last_verified_at"
        )
    )


    macau_documents.append(
        transformed
    )


# ============================================================
# Macau pre-merge audit
# ============================================================

macau_ids = [
    clean(
        row.get("program_id")
    )
    for row in macau_documents
]


duplicate_macau = (
    len(macau_ids)
    - len(set(macau_ids))
)


overlap = sorted(
    set(existing_ids)
    & set(macau_ids)
)


international_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in macau_documents
)


verified_yes_blank_urls = [
    clean(
        row["program_id"]
    )
    for row in macau_documents
    if (
        clean(
            row.get(
                "international_applicants_status"
            )
        ) == "verified_yes"
        and not clean(
            row.get(
                "international_application_url"
            )
        )
    )
]


blank_international_dates = [
    clean(
        row["program_id"]
    )
    for row in macau_documents
    if not clean(
        row.get(
            "international_applicants_last_verified_at"
        )
    )
]


print()
print("MACAU PRE-MERGE AUDIT")
print("-" * 110)

print(
    "Macau canonical rows              :",
    len(macau_documents),
)

print(
    "Macau duplicate IDs               :",
    duplicate_macau,
)

print(
    "Existing/Macau ID overlap         :",
    len(overlap),
)

print(
    "International statuses            :",
    dict(
        international_statuses
    ),
)

print(
    "verified_yes blank URLs           :",
    len(
        verified_yes_blank_urls
    ),
)

print(
    "Blank international dates         :",
    len(
        blank_international_dates
    ),
)


if len(
    macau_documents
) != EXPECTED_MACAU:

    raise ValueError(
        "Macau transformed count mismatch."
    )


if duplicate_macau:

    raise ValueError(
        "Duplicate Macau programme IDs."
    )


if overlap:

    raise ValueError(
        "Safety stop: Macau IDs overlap "
        "existing canonical IDs: "
        + ", ".join(overlap)
    )


if international_statuses != Counter({
    "verified_yes": 20,
    "unknown": 1,
}):

    raise ValueError(
        "Unexpected international "
        "eligibility status counts."
    )


if verified_yes_blank_urls:

    raise ValueError(
        "verified_yes programme has blank "
        "international application URL."
    )


if blank_international_dates:

    raise ValueError(
        "International verification date "
        "missing from one or more programmes."
    )


# ============================================================
# Construct staging data
# ============================================================

staging = (
    existing
    + macau_documents
)


staging_ids = [
    clean(
        row.get("program_id")
    )
    for row in staging
]


staging_duplicates = (
    len(staging_ids)
    - len(set(staging_ids))
)


# ============================================================
# Critical preservation checks
# ============================================================

existing_preserved = (
    staging[
        :len(existing_snapshot)
    ]
    == existing_snapshot
)


existing_ids_after = set(
    staging_ids[
        :len(existing_snapshot)
    ]
)


missing_existing_ids = sorted(
    set(existing_ids)
    - existing_ids_after
)


unexpected_existing_change_count = 0


for index, original in enumerate(
    existing_snapshot
):

    if staging[index] != original:

        unexpected_existing_change_count += 1


prefix_counts = Counter(
    prefix(program_id)
    for program_id in staging_ids
)


print()
print("STAGING MERGE AUDIT")
print("-" * 110)

print(
    "Existing programmes preserved     :",
    len(existing),
)

print(
    "Macau programmes added            :",
    len(macau_documents),
)

print(
    "Expected staging total            :",
    EXPECTED_STAGING,
)

print(
    "Actual staging total              :",
    len(staging),
)

print(
    "Staging duplicate IDs             :",
    staging_duplicates,
)

print(
    "Existing records exact-preserved  :",
    existing_preserved,
)

print(
    "Existing records changed          :",
    unexpected_existing_change_count,
)

print(
    "Missing existing IDs              :",
    len(missing_existing_ids),
)

print(
    "Programme prefix counts           :",
    dict(prefix_counts),
)


# ============================================================
# Acceptance gate BEFORE writing staging file
# ============================================================

errors = []


if len(staging) != EXPECTED_STAGING:

    errors.append(
        f"Expected staging total "
        f"{EXPECTED_STAGING}, found "
        f"{len(staging)}."
    )


if staging_duplicates != 0:

    errors.append(
        "Duplicate programme IDs exist "
        "after merge."
    )


if not existing_preserved:

    errors.append(
        "One or more existing programme "
        "records changed."
    )


if unexpected_existing_change_count != 0:

    errors.append(
        "Existing record preservation "
        "audit failed."
    )


if missing_existing_ids:

    errors.append(
        "Existing programme IDs were lost."
    )


if prefix_counts.get(
    "prog_mo",
    0,
) != 21:

    errors.append(
        "Expected exactly 21 prog_mo "
        "records in staging."
    )


if errors:

    print()
    print("=" * 110)

    print(
        "STEP 170.2F MACAU SAFE "
        "STAGING MERGE: FAIL"
    )

    for error in errors:

        print(
            "ERROR:",
            error,
        )

    print(
        "STAGING FILE WAS NOT WRITTEN"
    )

    print(
        "programs.json WAS NOT MODIFIED"
    )

    print(
        "MONGODB WAS NOT MODIFIED"
    )

    print("=" * 110)

    raise SystemExit(1)


# ============================================================
# Backup old staging target if it already exists
# ============================================================

if STAGING_JSON.exists():

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = BACKUP_DIR / (
        "programs_with_macau_staging_"
        f"before_rebuild_{timestamp}.json"
    )

    shutil.copy2(
        STAGING_JSON,
        backup_path,
    )

    print(
        "Previous staging backup          :",
        backup_path,
    )


# ============================================================
# Write staging JSON only
# ============================================================

STAGING_JSON.parent.mkdir(
    parents=True,
    exist_ok=True,
)


with STAGING_JSON.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        staging,
        file,
        ensure_ascii=False,
        indent=2,
    )


# ============================================================
# Re-read staging file after write
# ============================================================

with STAGING_JSON.open(
    "r",
    encoding="utf-8",
) as file:

    written = json.load(file)


written_ids = [
    clean(
        row.get("program_id")
    )
    for row in written
]


written_macau = [
    row
    for row in written
    if clean(
        row.get("program_id")
    ).startswith(
        "prog_mo_"
    )
]


written_existing_preserved = (
    written[:EXPECTED_EXISTING]
    == existing_snapshot
)


written_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in written_macau
)


print()
print("POST-WRITE STAGING VERIFICATION")
print("-" * 110)

print(
    "Written staging rows              :",
    len(written),
)

print(
    "Written duplicate IDs             :",
    len(written_ids)
    - len(set(written_ids)),
)

print(
    "Written Macau programmes          :",
    len(written_macau),
)

print(
    "Existing 336 still exact          :",
    written_existing_preserved,
)

print(
    "Macau international statuses      :",
    dict(written_statuses),
)

print(
    "Staging output                    :",
    STAGING_JSON,
)


if len(written) != EXPECTED_STAGING:
    raise ValueError(
        "Post-write staging count failed."
    )


if len(written_ids) != len(
    set(written_ids)
):
    raise ValueError(
        "Post-write duplicate check failed."
    )


if len(written_macau) != EXPECTED_MACAU:
    raise ValueError(
        "Post-write Macau count failed."
    )


if not written_existing_preserved:
    raise ValueError(
        "Post-write existing record "
        "preservation failed."
    )


if written_statuses != Counter({
    "verified_yes": 20,
    "unknown": 1,
}):
    raise ValueError(
        "Post-write international status "
        "verification failed."
    )


print()
print("=" * 110)

print(
    "STEP 170.2F MACAU SAFE "
    "STAGING MERGE: PASS"
)

print(
    "EXISTING 336 PROGRAMMES "
    "PRESERVED EXACTLY"
)

print(
    "MACAU PROGRAMMES ADDED TO "
    "STAGING: 21"
)

print(
    "STAGING TOTAL: 357"
)

print(
    "programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 110)
