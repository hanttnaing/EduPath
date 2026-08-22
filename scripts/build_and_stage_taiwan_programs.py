import csv
import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# ============================================================
# Canonical transformer
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
    "planning/24_taiwan_program_research_queue.csv"
)

FINAL_PROGRAMS = Path(
    "data/cleaned/taiwan_programs_final_ready.csv"
)

FINAL_INTERNATIONAL = Path(
    "data/cleaned/"
    "taiwan_program_international_merge_ready.csv"
)

EXISTING_JSON = Path(
    "data/cleaned/programs.json"
)

STAGING_JSON = Path(
    "data/cleaned/"
    "programs_with_taiwan_staging.json"
)

BACKUP_DIR = Path(
    "data/backups/step_170_4c"
)


EXPECTED_EXISTING = 390
EXPECTED_TAIWAN = 90
EXPECTED_STAGING = 480


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


EXPECTED_PREFIX_COUNTS = {
    "prog_jp": 36,
    "prog_bn": 12,
    "prog_la": 15,
    "prog_sg": 18,
    "prog_tl": 18,
    "prog_kh": 39,
    "prog_mm": 33,
    "prog_my": 120,
    "prog_hk": 45,
    "prog_mo": 21,
    "prog_mn": 33,
    "prog_tw": 90,
}


def clean(value):
    return str(value or "").strip()


def optional(value):

    value = clean(value)

    return (
        None
        if value == ""
        else value
    )


def prefix(program_id):

    parts = clean(
        program_id
    ).split("_")

    if len(parts) >= 3:
        return "_".join(
            parts[:2]
        )

    return "unknown"


print("=" * 116)

print(
    "STEP 170.4C - TAIWAN FINAL CANONICAL BUILD "
    "+ SAFE 480-ROW STAGING MERGE"
)

print("=" * 116)


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
# Load Taiwan research queue
# ============================================================

if not QUEUE.exists():

    raise FileNotFoundError(
        f"Taiwan queue missing: {QUEUE}"
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


if len(rows) != EXPECTED_TAIWAN:

    raise ValueError(
        f"Expected 90 Taiwan rows, "
        f"found {len(rows)}."
    )


verified = [
    row
    for row in rows
    if clean(
        row.get("research_status")
    ) == "VERIFIED"
]


pending = [
    row
    for row in rows
    if clean(
        row.get("research_status")
    ) == "PENDING"
]


deferred = [
    row
    for row in rows
    if clean(
        row.get("research_status")
    ) == "DEFERRED"
]


if len(verified) != 90:

    raise ValueError(
        f"Expected 90 VERIFIED rows, "
        f"found {len(verified)}."
    )


if pending:

    raise ValueError(
        "Taiwan queue still contains "
        "PENDING programme slots."
    )


if deferred:

    raise ValueError(
        "Unexpected Taiwan DEFERRED rows."
    )


expected_ids = [
    f"prog_tw_{i:03d}"
    for i in range(
        1,
        91,
    )
]


verified_ids = [
    clean(
        row["program_id"]
    )
    for row in verified
]


if verified_ids != expected_ids:

    raise ValueError(
        "Taiwan programme ID sequence "
        "is not exactly prog_tw_001..090."
    )


for field in INTERNATIONAL_COLUMNS[1:]:

    if field not in queue_headers:

        raise ValueError(
            f"Queue missing international "
            f"field: {field}"
        )


# ============================================================
# Transform all 90 verified programmes
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
        row["program_id"]
    )


    verified_at = clean(
        row.get(
            "last_verified_at"
        )
    )


    if not verified_at:

        raise ValueError(
            f"{program_id}: "
            "last_verified_at is blank."
        )


    raw = {
        "program_id":
            optional(
                row["program_id"]
            ),

        "university_id":
            optional(
                row["university_id"]
            ),

        "program_name":
            optional(
                row["program_name"]
            ),

        "field_of_study":
            optional(
                row["field_of_study"]
            ),

        "degree_level":
            optional(
                row["degree_level"]
            ),

        "duration_years":
            optional(
                row["duration_years"]
            ),

        "study_mode":
            optional(
                row["study_mode"]
            ),

        "language_of_instruction":
            optional(
                row[
                    "language_of_instruction"
                ]
            ),

        "tuition_fee":
            optional(
                row["tuition_fee"]
            ),

        "tuition_currency":
            optional(
                row[
                    "tuition_currency"
                ]
            ),

        "tuition_period":
            optional(
                row[
                    "tuition_period"
                ]
            ),

        "minimum_gpa":
            optional(
                row["minimum_gpa"]
            ),

        "gpa_scale":
            optional(
                row["gpa_scale"]
            ),

        "ielts_requirement":
            optional(
                row[
                    "ielts_requirement"
                ]
            ),

        "toefl_requirement":
            optional(
                row[
                    "toefl_requirement"
                ]
            ),

        "intake":
            optional(
                row["intake"]
            ),

        "application_deadline":
            optional(
                row[
                    "application_deadline"
                ]
            ),

        "program_url":
            optional(
                row["program_url"]
            ),

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
            f"{program_id}: "
            "transformed schema mismatch."
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
            "verification date is blank."
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
# Taiwan canonical audit
# ============================================================

canonical_ids = [
    clean(
        row["program_id"]
    )
    for row in canonical_rows
]


international_ids = [
    clean(
        row["program_id"]
    )
    for row in international_rows
]


if canonical_ids != expected_ids:

    raise ValueError(
        "Canonical Taiwan ID sequence changed."
    )


if set(canonical_ids) != set(
    international_ids
):

    raise ValueError(
        "Taiwan canonical/international "
        "ID sets differ."
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


unknown_international_ids = sorted(
    clean(
        row["program_id"]
    )
    for row in international_rows
    if clean(
        row.get(
            "international_applicants_status"
        )
    ) == "unknown"
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


tuition_parity_errors = []


for row in canonical_rows:

    fee = clean(
        row.get("tuition_fee")
    )

    currency = clean(
        row.get(
            "tuition_currency"
        )
    )

    period = clean(
        row.get(
            "tuition_period"
        )
    )


    if bool(fee) != (
        bool(currency)
        and bool(period)
    ):

        tuition_parity_errors.append(
            clean(
                row["program_id"]
            )
        )


print()
print("TAIWAN FINAL CANONICAL AUDIT")
print("-" * 116)


print(
    "Canonical programme rows           :",
    len(canonical_rows),
)

print(
    "Canonical programme columns        :",
    len(PROGRAM_COLUMNS),
)

print(
    "Duplicate Taiwan IDs               :",
    len(canonical_ids)
    - len(set(canonical_ids)),
)


print()
print(
    "Duration populated                 :",
    duration_count,
    "/ 90",
)

print(
    "Study mode populated               :",
    mode_count,
    "/ 90",
)

print(
    "Language populated                 :",
    language_count,
    "/ 90",
)

print(
    "Unknown language                   :",
    len(unknown_language_ids),
    "/ 90",
)

print(
    "Tuition populated                  :",
    tuition_count,
    "/ 90",
)

print(
    "Tuition parity errors              :",
    len(tuition_parity_errors),
)

print(
    "IELTS populated                    :",
    ielts_count,
    "/ 90",
)

print(
    "TOEFL populated                    :",
    toefl_count,
    "/ 90",
)

print(
    "Future intake populated            :",
    intake_count,
    "/ 90",
)

print(
    "Future deadline populated          :",
    deadline_count,
    "/ 90",
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
    "Unknown international IDs          :",
    ", ".join(
        unknown_international_ids
    ),
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


# ============================================================
# Exact Taiwan acceptance gate
# ============================================================

errors = []


if len(canonical_rows) != 90:

    errors.append(
        "Expected exactly 90 Taiwan "
        "canonical programmes."
    )


if len(canonical_ids) != len(
    set(canonical_ids)
):

    errors.append(
        "Duplicate Taiwan programme IDs."
    )


# Batch totals:
# B1: duration 9, mode 0, unknown language 16,
#     tuition 0, IELTS 1, TOEFL 0
# B2: duration 0, mode 0, unknown language 16,
#     tuition 0, IELTS 3, TOEFL 3
# B3: duration 11, mode 6, unknown language 10,
#     tuition 6, IELTS 0, TOEFL 0

if duration_count != 20:

    errors.append(
        "Expected Taiwan duration coverage 20/90."
    )


if mode_count != 6:

    errors.append(
        "Expected Taiwan study mode coverage 6/90."
    )


if language_count != 90:

    errors.append(
        "Expected language status/value 90/90."
    )


if len(
    unknown_language_ids
) != 42:

    errors.append(
        "Expected 42 Unknown-language programmes."
    )


if tuition_count != 6:

    errors.append(
        "Expected Taiwan tuition coverage 6/90."
    )


if tuition_parity_errors:

    errors.append(
        "Taiwan tuition fee/currency/period "
        "parity errors exist."
    )


if ielts_count != 4:

    errors.append(
        "Expected IELTS coverage 4/90."
    )


if toefl_count != 3:

    errors.append(
        "Expected TOEFL coverage 3/90."
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
    "current": 90,
}):

    errors.append(
        "Expected freshness=current for all 90."
    )


if international_statuses != Counter({
    "verified_yes": 87,
    "unknown": 3,
}):

    errors.append(
        "Unexpected Taiwan international "
        "status counts."
    )


if unknown_international_ids != [
    "prog_tw_067",
    "prog_tw_068",
    "prog_tw_069",
]:

    errors.append(
        "Unexpected Taiwan international "
        "unknown ID set."
    )


if verified_yes_blank_urls:

    errors.append(
        "verified_yes Taiwan programme "
        "has blank international URL."
    )


if blank_international_notes:

    errors.append(
        "Taiwan international notes missing."
    )


if blank_international_dates:

    errors.append(
        "Taiwan international verification "
        "dates missing."
    )


if errors:

    print()
    print(
        "TAIWAN CANONICAL PRE-WRITE: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


# ============================================================
# Backup existing output targets
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
# Write Taiwan exact 21-column canonical CSV
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
# Write Taiwan international 5-column merge file
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
# Load current canonical programs.json
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


if not isinstance(
    existing,
    list,
):

    raise ValueError(
        "programs.json must contain a JSON list."
    )


existing_ids = [
    clean(
        row.get(
            "program_id"
        )
    )
    for row in existing
]


print()
print("EXISTING CANONICAL SAFETY AUDIT")
print("-" * 116)


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
        f"{EXPECTED_EXISTING}, "
        f"found {len(existing)}."
    )


if len(existing_ids) != len(
    set(existing_ids)
):

    raise ValueError(
        "Existing canonical contains duplicates."
    )


existing_taiwan = [
    program_id
    for program_id in existing_ids
    if program_id.startswith(
        "prog_tw_"
    )
]


print(
    "Existing Taiwan IDs                :",
    len(existing_taiwan),
)


if existing_taiwan:

    raise ValueError(
        "Safety stop: Taiwan programmes "
        "already exist in programs.json."
    )


existing_snapshot = json.loads(
    json.dumps(
        existing,
        ensure_ascii=False,
    )
)


# ============================================================
# Attach international extras to Taiwan canonical rows
# ============================================================

international_by_id = {
    clean(
        row["program_id"]
    ): row
    for row in international_rows
}


taiwan_documents = []


for canonical in canonical_rows:

    program_id = clean(
        canonical["program_id"]
    )


    international = (
        international_by_id[
            program_id
        ]
    )


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


    taiwan_documents.append(
        document
    )


taiwan_ids = [
    clean(
        row["program_id"]
    )
    for row in taiwan_documents
]


overlap = sorted(
    set(existing_ids)
    & set(taiwan_ids)
)


if overlap:

    raise ValueError(
        "Existing/Taiwan ID overlap: "
        + ", ".join(overlap)
    )


# ============================================================
# Build staging 390 + 90 = 480
# ============================================================

staging = (
    existing
    + taiwan_documents
)


staging_ids = [
    clean(
        row.get(
            "program_id"
        )
    )
    for row in staging
]


staging_duplicates = (
    len(staging_ids)
    - len(set(staging_ids))
)


existing_preserved = (
    staging[
        :EXPECTED_EXISTING
    ]
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
print("SAFE TAIWAN STAGING MERGE AUDIT")
print("-" * 116)


print(
    "Existing programmes preserved      :",
    len(existing),
)

print(
    "Taiwan programmes added            :",
    len(taiwan_documents),
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
    "Existing 390 exact-preserved       :",
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
        "Expected staging total 480."
    )


if staging_duplicates != 0:

    merge_errors.append(
        "Staging contains duplicate IDs."
    )


if not existing_preserved:

    merge_errors.append(
        "Existing 390 records changed."
    )


if changed_existing != 0:

    merge_errors.append(
        "Existing-record preservation failed."
    )


if missing_existing:

    merge_errors.append(
        "Existing programme IDs were lost."
    )


if prefix_counts != Counter(
    EXPECTED_PREFIX_COUNTS
):

    merge_errors.append(
        "Programme prefix counts mismatch."
    )


if merge_errors:

    print()
    print(
        "TAIWAN STAGING PRE-WRITE: FAIL"
    )

    for error in merge_errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


# ============================================================
# Write staging only
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
# Post-write verification
# ============================================================

with FINAL_PROGRAMS.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    written_program_headers = (
        reader.fieldnames or []
    )

    written_programs = list(
        reader
    )


with FINAL_INTERNATIONAL.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    written_int_headers = (
        reader.fieldnames or []
    )

    written_int = list(
        reader
    )


with STAGING_JSON.open(
    "r",
    encoding="utf-8",
) as file:

    written_staging = json.load(
        file
    )


written_ids = [
    clean(
        row.get(
            "program_id"
        )
    )
    for row in written_staging
]


written_taiwan = [
    row
    for row in written_staging
    if clean(
        row.get(
            "program_id"
        )
    ).startswith(
        "prog_tw_"
    )
]


written_existing_preserved = (
    written_staging[
        :EXPECTED_EXISTING
    ]
    == existing_snapshot
)


written_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in written_taiwan
)


print()
print("POST-WRITE VERIFICATION")
print("-" * 116)


print(
    "Final Taiwan programme CSV rows    :",
    len(written_programs),
)

print(
    "Final Taiwan programme columns     :",
    len(written_program_headers),
)

print(
    "International merge rows           :",
    len(written_int),
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
    len(written_ids)
    - len(set(written_ids)),
)

print(
    "Written Taiwan programmes          :",
    len(written_taiwan),
)

print(
    "Existing 390 still exact           :",
    written_existing_preserved,
)

print(
    "Taiwan international statuses      :",
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
) == 90

assert len(
    written_int
) == 90

assert len(
    written_staging
) == 480

assert (
    len(written_ids)
    == len(set(written_ids))
)

assert len(
    written_taiwan
) == 90

assert written_existing_preserved

assert written_statuses == Counter({
    "verified_yes": 87,
    "unknown": 3,
})


print()
print("=" * 116)

print(
    "STEP 170.4C TAIWAN FINAL CANONICAL "
    "+ STAGING BUILD: PASS"
)

print(
    "90 TAIWAN PROGRAMMES ARE "
    "CANONICAL-READY"
)

print(
    "INTERNATIONAL ELIGIBILITY: "
    "87 VERIFIED_YES / 3 UNKNOWN"
)

print(
    "EXISTING 390 PROGRAMMES "
    "PRESERVED EXACTLY"
)

print(
    "TAIWAN ADDED TO STAGING: 90"
)

print(
    "STAGING TOTAL: 480"
)

print(
    "programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 116)
