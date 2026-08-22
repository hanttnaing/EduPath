import csv
import json
import shutil
import sys

from collections import Counter
from datetime import datetime
from pathlib import Path


# ============================================================
# Existing canonical transformer
# ============================================================

SCRIPTS_DIR = Path("scripts").resolve()

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS_DIR),
    )

import transform_programs as tp


# ============================================================
# Paths
# ============================================================

QUEUE = Path(
    "planning/22_mongolia_program_research_queue.csv"
)

FINAL_PROGRAMS = Path(
    "data/cleaned/mongolia_programs_final_ready.csv"
)

FINAL_INTERNATIONAL = Path(
    "data/cleaned/"
    "mongolia_program_international_merge_ready.csv"
)

EXISTING_JSON = Path(
    "data/cleaned/programs.json"
)

STAGING_JSON = Path(
    "data/cleaned/"
    "programs_with_mongolia_staging.json"
)

BACKUP_DIR = Path(
    "data/backups/step_170_3c"
)


EXPECTED_EXISTING = 357
EXPECTED_MONGOLIA = 33
EXPECTED_STAGING = 390


PROGRAM_COLUMNS = [
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


INTERNATIONAL_COLUMNS = [
    "program_id",
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


def clean(value):
    return str(value or "").strip()


def optional(value):

    value = clean(value)

    return None if value == "" else value


def prefix(program_id):

    parts = clean(program_id).split("_")

    if len(parts) >= 3:
        return "_".join(parts[:2])

    return "unknown"


print("=" * 112)
print(
    "STEP 170.3C - MONGOLIA FINAL CANONICAL BUILD "
    "+ SAFE 390-ROW STAGING MERGE"
)
print("=" * 112)


# ============================================================
# Transformer contract
# ============================================================

if list(
    tp.EXPECTED_COLUMNS
) != PROGRAM_COLUMNS:

    raise ValueError(
        "transform_programs.py canonical "
        "21-column contract changed."
    )


print(
    "Canonical transformer columns      :",
    len(PROGRAM_COLUMNS),
)

print(
    "Transformer contract               : PASS",
)


# ============================================================
# Load Mongolia queue
# ============================================================

if not QUEUE.exists():

    raise FileNotFoundError(
        f"Mongolia queue missing: {QUEUE}"
    )


with QUEUE.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    queue_headers = (
        reader.fieldnames or []
    )

    rows = list(reader)


verified = [
    row
    for row in rows
    if clean(
        row.get("research_status")
    ) == "VERIFIED"
]


deferred = [
    row
    for row in rows
    if clean(
        row.get("research_status")
    ) == "DEFERRED"
]


if len(rows) != 36:

    raise ValueError(
        f"Expected 36 research slots, "
        f"found {len(rows)}."
    )


if len(verified) != EXPECTED_MONGOLIA:

    raise ValueError(
        f"Expected 33 verified programmes, "
        f"found {len(verified)}."
    )


if len(deferred) != 3:

    raise ValueError(
        f"Expected 3 deferred slots, "
        f"found {len(deferred)}."
    )


deferred_ids = sorted(
    clean(row["program_id"])
    for row in deferred
)


if deferred_ids != [
    "prog_mn_022",
    "prog_mn_023",
    "prog_mn_024",
]:

    raise ValueError(
        "Unexpected Mongolia deferred ID set."
    )


for field in INTERNATIONAL_COLUMNS[1:]:

    if field not in queue_headers:

        raise ValueError(
            f"Queue missing international field: "
            f"{field}"
        )


# ============================================================
# Transform 33 verified rows
# ============================================================

valid_university_ids = (
    tp.load_valid_university_ids()
)


canonical_rows = []

international_rows = []


for row_number, row in enumerate(
    verified,
    start=2,
):

    program_id = clean(
        row.get("program_id")
    )


    verified_at = clean(
        row.get("last_verified_at")
    )


    if not verified_at:

        raise ValueError(
            f"{program_id}: last_verified_at blank."
        )


    raw = {
        "program_id":
            optional(row.get("program_id")),

        "university_id":
            optional(row.get("university_id")),

        "program_name":
            optional(row.get("program_name")),

        "field_of_study":
            optional(row.get("field_of_study")),

        "degree_level":
            optional(row.get("degree_level")),

        "duration_years":
            optional(row.get("duration_years")),

        "study_mode":
            optional(row.get("study_mode")),

        "language_of_instruction":
            optional(
                row.get(
                    "language_of_instruction"
                )
            ),

        "tuition_fee":
            optional(row.get("tuition_fee")),

        "tuition_currency":
            optional(
                row.get(
                    "tuition_currency"
                )
            ),

        "tuition_period":
            optional(row.get("tuition_period")),

        "minimum_gpa":
            optional(row.get("minimum_gpa")),

        "gpa_scale":
            optional(row.get("gpa_scale")),

        "ielts_requirement":
            optional(
                row.get(
                    "ielts_requirement"
                )
            ),

        "toefl_requirement":
            optional(
                row.get(
                    "toefl_requirement"
                )
            ),

        "intake":
            optional(row.get("intake")),

        "application_deadline":
            optional(
                row.get(
                    "application_deadline"
                )
            ),

        "program_url":
            optional(row.get("program_url")),

        "collected_at":
            verified_at,

        "last_verified_at":
            verified_at,

        "freshness_status":
            "current",
    }


    transformed = tp.transform_program(
        raw_record=raw,
        row_number=row_number,
        valid_university_ids=(
            valid_university_ids
        ),
    )


    if list(
        transformed.keys()
    ) != PROGRAM_COLUMNS:

        raise ValueError(
            f"{program_id}: transformed schema mismatch."
        )


    canonical_rows.append(
        transformed
    )


    international_date = clean(
        row.get(
            "international_applicants_last_verified_at"
        )
    )


    if not international_date:

        raise ValueError(
            f"{program_id}: international "
            "verification date blank."
        )


    international_rows.append(
        {
            "program_id":
                program_id,

            "international_applicants_status":
                clean(
                    row.get(
                        "international_applicants_status"
                    )
                ),

            "international_application_url":
                clean(
                    row.get(
                        "international_application_url"
                    )
                ),

            "international_requirements_note":
                clean(
                    row.get(
                        "international_requirements_note"
                    )
                ),

            "international_applicants_last_verified_at":
                international_date,
        }
    )


# ============================================================
# Canonical pre-write audit
# ============================================================

canonical_ids = [
    clean(
        row.get("program_id")
    )
    for row in canonical_rows
]


international_ids = [
    clean(
        row.get("program_id")
    )
    for row in international_rows
]


if len(canonical_ids) != len(
    set(canonical_ids)
):

    raise ValueError(
        "Duplicate Mongolia canonical IDs."
    )


if set(
    canonical_ids
) != set(
    international_ids
):

    raise ValueError(
        "Canonical/international Mongolia "
        "ID sets differ."
    )


if any(
    not program_id.startswith(
        "prog_mn_"
    )
    for program_id in canonical_ids
):

    raise ValueError(
        "Non-Mongolia ID found in canonical build."
    )


def populated(field):

    return sum(
        bool(
            clean(
                row.get(field)
            )
        )
        for row in canonical_rows
    )


duration_count = populated(
    "duration_years"
)

mode_count = populated(
    "study_mode"
)

language_count = populated(
    "language_of_instruction"
)

tuition_count = populated(
    "tuition_fee"
)

ielts_count = populated(
    "ielts_requirement"
)

toefl_count = populated(
    "toefl_requirement"
)

intake_count = populated(
    "intake"
)

deadline_count = populated(
    "application_deadline"
)


unknown_language_ids = sorted(
    clean(
        row["program_id"]
    )
    for row in canonical_rows
    if clean(
        row.get(
            "language_of_instruction"
        )
    ) == "Unknown"
)


freshness = Counter(
    clean(
        row.get(
            "freshness_status"
        )
    )
    for row in canonical_rows
)


international_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in international_rows
)


verified_yes_blank_urls = sorted(
    clean(
        row["program_id"]
    )
    for row in international_rows
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
)


blank_international_notes = sorted(
    clean(
        row["program_id"]
    )
    for row in international_rows
    if not clean(
        row.get(
            "international_requirements_note"
        )
    )
)


blank_international_dates = sorted(
    clean(
        row["program_id"]
    )
    for row in international_rows
    if not clean(
        row.get(
            "international_applicants_last_verified_at"
        )
    )
)


print()
print("MONGOLIA FINAL CANONICAL AUDIT")
print("-" * 112)

print(
    "Canonical programme rows           :",
    len(canonical_rows),
)

print(
    "Canonical programme columns        :",
    len(PROGRAM_COLUMNS),
)

print(
    "Duplicate Mongolia IDs             :",
    len(canonical_ids)
    - len(set(canonical_ids)),
)

print(
    "Deferred slots excluded            :",
    len(deferred),
)

print()
print(
    "Duration populated                 :",
    duration_count,
    "/ 33",
)

print(
    "Study mode populated               :",
    mode_count,
    "/ 33",
)

print(
    "Language populated                 :",
    language_count,
    "/ 33",
)

print(
    "Unknown language                   :",
    len(unknown_language_ids),
    "/ 33",
)

print(
    "Tuition populated                  :",
    tuition_count,
    "/ 33",
)

print(
    "IELTS populated                    :",
    ielts_count,
    "/ 33",
)

print(
    "TOEFL populated                    :",
    toefl_count,
    "/ 33",
)

print(
    "Future intake populated            :",
    intake_count,
    "/ 33",
)

print(
    "Future deadline populated          :",
    deadline_count,
    "/ 33",
)

print(
    "Freshness                          :",
    dict(freshness),
)

print()
print(
    "International merge rows           :",
    len(international_rows),
)

print(
    "International statuses             :",
    dict(international_statuses),
)

print(
    "verified_yes blank URLs            :",
    len(verified_yes_blank_urls),
)

print(
    "Blank international notes          :",
    len(blank_international_notes),
)

print(
    "Blank international dates          :",
    len(blank_international_dates),
)


errors = []


if len(canonical_rows) != 33:
    errors.append(
        "Expected 33 canonical programmes."
    )


if duration_count != 21:
    errors.append(
        "Expected duration 21/33."
    )


if mode_count != 6:
    errors.append(
        "Expected study mode 6/33."
    )


if language_count != 33:
    errors.append(
        "Expected language status 33/33."
    )


if len(unknown_language_ids) != 30:
    errors.append(
        "Expected 30 Unknown language records."
    )


if tuition_count != 0:
    errors.append(
        "Unexpected tuition values populated."
    )


if ielts_count != 6:
    errors.append(
        "Expected IELTS 6/33."
    )


if toefl_count != 6:
    errors.append(
        "Expected TOEFL 6/33."
    )


if intake_count != 0:
    errors.append(
        "Future intake should remain blank."
    )


if deadline_count != 0:
    errors.append(
        "Future deadline should remain blank."
    )


if freshness != Counter({
    "current": 33,
}):
    errors.append(
        "Expected freshness=current for 33."
    )


if international_statuses != Counter({
    "verified_yes": 21,
    "unknown": 12,
}):
    errors.append(
        "Unexpected international status counts."
    )


if verified_yes_blank_urls:
    errors.append(
        "verified_yes rows have blank "
        "international URLs."
    )


if blank_international_notes:
    errors.append(
        "International requirement notes missing."
    )


if blank_international_dates:
    errors.append(
        "International verification dates missing."
    )


if errors:

    print()
    print(
        "CANONICAL BUILD PRE-WRITE: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


# ============================================================
# Backup prior outputs
# ============================================================

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)


for target in [
    FINAL_PROGRAMS,
    FINAL_INTERNATIONAL,
    STAGING_JSON,
]:

    if target.exists():

        backup = BACKUP_DIR / (
            target.stem
            + "_before_rebuild_"
            + timestamp
            + target.suffix
        )

        shutil.copy2(
            target,
            backup,
        )

        print(
            "Existing output backup           :",
            backup,
        )


# ============================================================
# Write exact 21-column Mongolia canonical CSV
# ============================================================

FINAL_PROGRAMS.parent.mkdir(
    parents=True,
    exist_ok=True,
)


with FINAL_PROGRAMS.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=PROGRAM_COLUMNS,
        extrasaction="raise",
    )

    writer.writeheader()
    writer.writerows(
        canonical_rows
    )


# ============================================================
# Write exact 5-column international merge
# ============================================================

with FINAL_INTERNATIONAL.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=INTERNATIONAL_COLUMNS,
        extrasaction="raise",
    )

    writer.writeheader()
    writer.writerows(
        international_rows
    )


# ============================================================
# Load existing canonical programs.json
# ============================================================

if not EXISTING_JSON.exists():

    raise FileNotFoundError(
        f"Canonical programs.json missing: "
        f"{EXISTING_JSON}"
    )


with EXISTING_JSON.open(
    "r",
    encoding="utf-8",
) as file:

    existing = json.load(file)


if not isinstance(existing, list):

    raise ValueError(
        "programs.json must contain a list."
    )


existing_ids = [
    clean(
        row.get("program_id")
    )
    for row in existing
]


print()
print("EXISTING CANONICAL SAFETY AUDIT")
print("-" * 112)

print(
    "Existing programs.json rows        :",
    len(existing),
)

print(
    "Existing duplicate IDs             :",
    len(existing_ids)
    - len(set(existing_ids)),
)


if len(existing) != EXPECTED_EXISTING:

    raise ValueError(
        f"Expected existing canonical "
        f"{EXPECTED_EXISTING}, found "
        f"{len(existing)}."
    )


if len(existing_ids) != len(
    set(existing_ids)
):

    raise ValueError(
        "Existing programs.json has duplicates."
    )


existing_mongolia = [
    program_id
    for program_id in existing_ids
    if program_id.startswith(
        "prog_mn_"
    )
]


print(
    "Existing Mongolia IDs              :",
    len(existing_mongolia),
)


if existing_mongolia:

    raise ValueError(
        "Safety stop: Mongolia programmes "
        "already exist in programs.json."
    )


existing_snapshot = json.loads(
    json.dumps(
        existing,
        ensure_ascii=False,
    )
)


# ============================================================
# Attach international extras to new 33 records
# ============================================================

international_by_id = {
    clean(
        row["program_id"]
    ): row
    for row in international_rows
}


mongolia_documents = []


for canonical in canonical_rows:

    program_id = clean(
        canonical["program_id"]
    )


    international = international_by_id[
        program_id
    ]


    document = dict(
        canonical
    )


    document[
        "international_applicants_status"
    ] = clean(
        international[
            "international_applicants_status"
        ]
    )


    document[
        "international_application_url"
    ] = clean(
        international[
            "international_application_url"
        ]
    )


    document[
        "international_requirements_note"
    ] = clean(
        international[
            "international_requirements_note"
        ]
    )


    document[
        "international_applicants_last_verified_at"
    ] = clean(
        international[
            "international_applicants_last_verified_at"
        ]
    )


    mongolia_documents.append(
        document
    )


mongolia_ids = [
    clean(
        row["program_id"]
    )
    for row in mongolia_documents
]


overlap = sorted(
    set(existing_ids)
    & set(mongolia_ids)
)


if overlap:

    raise ValueError(
        "Existing/Mongolia program ID overlap: "
        + ", ".join(overlap)
    )


# ============================================================
# Construct staging = 357 existing + 33 Mongolia
# ============================================================

staging = (
    existing
    + mongolia_documents
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


existing_preserved = (
    staging[:EXPECTED_EXISTING]
    == existing_snapshot
)


changed_existing = sum(
    staging[index]
    != existing_snapshot[index]
    for index in range(
        EXPECTED_EXISTING
    )
)


missing_existing = sorted(
    set(existing_ids)
    - set(
        staging_ids[
            :EXPECTED_EXISTING
        ]
    )
)


prefix_counts = Counter(
    prefix(program_id)
    for program_id in staging_ids
)


print()
print("SAFE STAGING MERGE AUDIT")
print("-" * 112)

print(
    "Existing programmes preserved      :",
    len(existing),
)

print(
    "Mongolia programmes added          :",
    len(mongolia_documents),
)

print(
    "Expected staging total             :",
    EXPECTED_STAGING,
)

print(
    "Actual staging total               :",
    len(staging),
)

print(
    "Staging duplicate IDs              :",
    staging_duplicates,
)

print(
    "Existing 357 exact-preserved       :",
    existing_preserved,
)

print(
    "Existing records changed           :",
    changed_existing,
)

print(
    "Missing existing IDs               :",
    len(missing_existing),
)

print(
    "Programme prefix counts            :",
    dict(prefix_counts),
)


merge_errors = []


if len(staging) != EXPECTED_STAGING:

    merge_errors.append(
        "Staging total must equal 390."
    )


if staging_duplicates:

    merge_errors.append(
        "Duplicate IDs found in staging."
    )


if not existing_preserved:

    merge_errors.append(
        "Existing canonical records changed."
    )


if changed_existing:

    merge_errors.append(
        "Existing record preservation failed."
    )


if missing_existing:

    merge_errors.append(
        "Existing programme IDs were lost."
    )


if prefix_counts.get(
    "prog_mn",
    0,
) != 33:

    merge_errors.append(
        "Expected exactly 33 prog_mn records."
    )


if merge_errors:

    print()
    print(
        "STAGING MERGE PRE-WRITE: FAIL"
    )

    for error in merge_errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


# ============================================================
# Write staging JSON only
# ============================================================

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
# Re-read all three outputs
# ============================================================

with FINAL_PROGRAMS.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    programme_reader = csv.DictReader(
        file
    )

    written_program_headers = (
        programme_reader.fieldnames or []
    )

    written_programs = list(
        programme_reader
    )


with FINAL_INTERNATIONAL.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    international_reader = csv.DictReader(
        file
    )

    written_int_headers = (
        international_reader.fieldnames or []
    )

    written_international = list(
        international_reader
    )


with STAGING_JSON.open(
    "r",
    encoding="utf-8",
) as file:

    written_staging = json.load(
        file
    )


written_staging_ids = [
    clean(
        row.get("program_id")
    )
    for row in written_staging
]


written_mongolia = [
    row
    for row in written_staging
    if clean(
        row.get("program_id")
    ).startswith(
        "prog_mn_"
    )
]


written_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in written_mongolia
)


written_existing_preserved = (
    written_staging[
        :EXPECTED_EXISTING
    ]
    == existing_snapshot
)


print()
print("POST-WRITE VERIFICATION")
print("-" * 112)

print(
    "Final programme CSV rows           :",
    len(written_programs),
)

print(
    "Final programme CSV columns        :",
    len(written_program_headers),
)

print(
    "International merge rows           :",
    len(written_international),
)

print(
    "International merge columns        :",
    len(written_int_headers),
)

print(
    "Written staging rows               :",
    len(written_staging),
)

print(
    "Written duplicate IDs              :",
    len(written_staging_ids)
    - len(set(written_staging_ids)),
)

print(
    "Written Mongolia programmes        :",
    len(written_mongolia),
)

print(
    "Existing 357 still exact           :",
    written_existing_preserved,
)

print(
    "Mongolia international statuses    :",
    dict(written_statuses),
)

print()
print(
    "Final programme file               :",
    FINAL_PROGRAMS,
)

print(
    "International merge file           :",
    FINAL_INTERNATIONAL,
)

print(
    "Staging file                       :",
    STAGING_JSON,
)


assert (
    written_program_headers
    == PROGRAM_COLUMNS
)

assert (
    written_int_headers
    == INTERNATIONAL_COLUMNS
)

assert len(
    written_programs
) == 33

assert len(
    written_international
) == 33

assert len(
    written_staging
) == 390

assert (
    len(written_staging_ids)
    == len(set(written_staging_ids))
)

assert len(
    written_mongolia
) == 33

assert written_existing_preserved

assert written_statuses == Counter({
    "verified_yes": 21,
    "unknown": 12,
})


print()
print("=" * 112)

print(
    "STEP 170.3C MONGOLIA FINAL "
    "CANONICAL + STAGING BUILD: PASS"
)

print(
    "33 VERIFIED PROGRAMMES "
    "ARE CANONICAL-READY"
)

print(
    "3 DEFERRED SLOTS EXCLUDED"
)

print(
    "EXISTING 357 PROGRAMMES "
    "PRESERVED EXACTLY"
)

print(
    "MONGOLIA ADDED TO STAGING: 33"
)

print(
    "STAGING TOTAL: 390"
)

print(
    "programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 112)
