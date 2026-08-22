import csv
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# ------------------------------------------------------------
# Import existing canonical transformer
# ------------------------------------------------------------

SCRIPTS_DIR = Path("scripts").resolve()

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS_DIR),
    )

import transform_programs as tp


QUEUE = Path(
    "planning/20_macau_program_research_queue.csv"
)

FINAL_PROGRAMS = Path(
    "data/cleaned/macau_programs_final_ready.csv"
)

FINAL_INTERNATIONAL = Path(
    "data/cleaned/"
    "macau_program_international_merge_ready.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_170_2e"
)


EXPECTED_COLUMNS = [
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

    return (
        None
        if value == ""
        else value
    )


print("=" * 110)
print(
    "STEP 170.2E - MACAU FINAL "
    "CANONICAL PROGRAMME BUILD"
)
print("=" * 110)


# ------------------------------------------------------------
# Verify transformer contract first
# ------------------------------------------------------------

actual_expected = list(
    tp.EXPECTED_COLUMNS
)


if actual_expected != EXPECTED_COLUMNS:

    print(
        "Transformer columns:",
        actual_expected,
    )

    raise ValueError(
        "transform_programs.py EXPECTED_COLUMNS "
        "does not match the required 21-column contract."
    )


print(
    "Canonical schema columns          :",
    len(EXPECTED_COLUMNS),
)

print(
    "Transformer contract              : PASS",
)


# ------------------------------------------------------------
# Load research queue
# ------------------------------------------------------------

if not QUEUE.exists():

    raise FileNotFoundError(
        f"Queue not found: {QUEUE}"
    )


with QUEUE.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)
    queue_headers = reader.fieldnames or []
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


if len(verified) != 21:

    raise ValueError(
        f"Expected 21 VERIFIED rows, "
        f"found {len(verified)}."
    )


if len(deferred) != 9:

    raise ValueError(
        f"Expected 9 DEFERRED rows, "
        f"found {len(deferred)}."
    )


required_international = set(
    INTERNATIONAL_COLUMNS[1:]
)


missing_international_columns = (
    required_international
    - set(queue_headers)
)


if missing_international_columns:

    raise ValueError(
        "Queue missing international fields: "
        + ", ".join(
            sorted(
                missing_international_columns
            )
        )
    )


valid_university_ids = (
    tp.load_valid_university_ids()
)


# ------------------------------------------------------------
# Transform 21 verified programmes
# ------------------------------------------------------------

canonical_rows = []

international_rows = []


for row_number, row in enumerate(
    verified,
    start=2,
):

    verification_date = clean(
        row.get("last_verified_at")
    )


    if not verification_date:

        raise ValueError(
            f"{row['program_id']}: "
            "last_verified_at is blank."
        )


    raw = {
        "program_id":
            optional(
                row.get("program_id")
            ),

        "university_id":
            optional(
                row.get("university_id")
            ),

        "program_name":
            optional(
                row.get("program_name")
            ),

        "field_of_study":
            optional(
                row.get("field_of_study")
            ),

        "degree_level":
            optional(
                row.get("degree_level")
            ),

        "duration_years":
            optional(
                row.get("duration_years")
            ),

        "study_mode":
            optional(
                row.get("study_mode")
            ),

        "language_of_instruction":
            optional(
                row.get(
                    "language_of_instruction"
                )
            ),

        "tuition_fee":
            optional(
                row.get("tuition_fee")
            ),

        "tuition_currency":
            optional(
                row.get("tuition_currency")
            ),

        "tuition_period":
            optional(
                row.get("tuition_period")
            ),

        "minimum_gpa":
            optional(
                row.get("minimum_gpa")
            ),

        "gpa_scale":
            optional(
                row.get("gpa_scale")
            ),

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
            optional(
                row.get("intake")
            ),

        "application_deadline":
            optional(
                row.get(
                    "application_deadline"
                )
            ),

        "program_url":
            optional(
                row.get("program_url")
            ),

        "collected_at":
            verification_date,

        "last_verified_at":
            verification_date,

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
    ) != EXPECTED_COLUMNS:

        raise ValueError(
            f"{row['program_id']}: transformed "
            "column order/schema mismatch."
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
            f"{row['program_id']}: international "
            "verification date is blank."
        )


    international_rows.append(
        {
            "program_id":
                clean(
                    row["program_id"]
                ),

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


# ------------------------------------------------------------
# Pre-write audit
# ------------------------------------------------------------

canonical_ids = [
    row["program_id"]
    for row in canonical_rows
]


international_ids = [
    row["program_id"]
    for row in international_rows
]


if len(canonical_ids) != len(
    set(canonical_ids)
):

    raise ValueError(
        "Duplicate Macau canonical program IDs."
    )


if set(canonical_ids) != set(
    international_ids
):

    raise ValueError(
        "Canonical/international ID sets differ."
    )


if any(
    not program_id.startswith(
        "prog_mo_"
    )
    for program_id in canonical_ids
):

    raise ValueError(
        "Non-Macau programme ID found."
    )


# ------------------------------------------------------------
# Backup existing outputs before write
# ------------------------------------------------------------

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
            "Existing output backup          :",
            backup,
        )


FINAL_PROGRAMS.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ------------------------------------------------------------
# Write exact 21-column programme CSV
# ------------------------------------------------------------

with FINAL_PROGRAMS.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=EXPECTED_COLUMNS,
        extrasaction="raise",
    )

    writer.writeheader()
    writer.writerows(
        canonical_rows
    )


# ------------------------------------------------------------
# Write exact 5-column international merge CSV
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Re-read outputs and final audit
# ------------------------------------------------------------

with FINAL_PROGRAMS.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    final_headers = reader.fieldnames or []
    final_rows = list(reader)


with FINAL_INTERNATIONAL.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    final_int_headers = (
        reader.fieldnames or []
    )

    final_int_rows = list(
        reader
    )


final_ids = [
    clean(
        row.get("program_id")
    )
    for row in final_rows
]


final_int_ids = [
    clean(
        row.get("program_id")
    )
    for row in final_int_rows
]


def populated(field):

    return sum(
        bool(
            clean(
                row.get(field)
            )
        )
        for row in final_rows
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
    for row in final_rows
    if clean(
        row.get(
            "language_of_instruction"
        )
    ) == "Unknown"
)


blank_duration_ids = sorted(
    clean(
        row["program_id"]
    )
    for row in final_rows
    if not clean(
        row.get(
            "duration_years"
        )
    )
)


blank_tuition_ids = sorted(
    clean(
        row["program_id"]
    )
    for row in final_rows
    if not clean(
        row.get("tuition_fee")
    )
)


freshness = Counter(
    clean(
        row.get(
            "freshness_status"
        )
    )
    for row in final_rows
)


international_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in final_int_rows
)


verified_yes_blank_urls = sorted(
    clean(
        row["program_id"]
    )
    for row in final_int_rows
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
    for row in final_int_rows
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
    for row in final_int_rows
    if not clean(
        row.get(
            "international_applicants_last_verified_at"
        )
    )
)


tuition_parity_errors = []


for row in final_rows:

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
print("FINAL CANONICAL AUDIT")
print("-" * 110)

print(
    "Programme rows                   :",
    len(final_rows),
)

print(
    "Programme columns                :",
    len(final_headers),
)

print(
    "Duplicate programme IDs          :",
    len(final_ids)
    - len(set(final_ids)),
)

print(
    "International merge rows         :",
    len(final_int_rows),
)

print(
    "International merge columns      :",
    len(final_int_headers),
)

print(
    "Canonical/international ID match :",
    set(final_ids)
    == set(final_int_ids),
)

print()
print(
    "Duration populated               :",
    duration_count,
    "/ 21",
)

print(
    "Study mode populated             :",
    mode_count,
    "/ 21",
)

print(
    "Language populated               :",
    language_count,
    "/ 21",
)

print(
    "Tuition populated                :",
    tuition_count,
    "/ 21",
)

print(
    "IELTS populated                  :",
    ielts_count,
    "/ 21",
)

print(
    "TOEFL populated                  :",
    toefl_count,
    "/ 21",
)

print(
    "Future intake populated          :",
    intake_count,
    "/ 21",
)

print(
    "Future deadline populated        :",
    deadline_count,
    "/ 21",
)

print(
    "Freshness statuses               :",
    dict(freshness),
)

print()
print(
    "Blank duration IDs               :",
    ", ".join(
        blank_duration_ids
    ),
)

print(
    "Blank tuition IDs                :",
    ", ".join(
        blank_tuition_ids
    ),
)

print(
    "Unknown language IDs             :",
    ", ".join(
        unknown_language_ids
    ),
)

print(
    "Tuition parity errors            :",
    len(tuition_parity_errors),
)

print()
print(
    "International statuses           :",
    dict(
        international_statuses
    ),
)

print(
    "verified_yes blank URLs          :",
    len(
        verified_yes_blank_urls
    ),
)

print(
    "Blank international notes        :",
    len(
        blank_international_notes
    ),
)

print(
    "Blank international dates        :",
    len(
        blank_international_dates
    ),
)

print()
print(
    "Final programme file             :",
    FINAL_PROGRAMS,
)

print(
    "International merge file         :",
    FINAL_INTERNATIONAL,
)


# ------------------------------------------------------------
# Exact acceptance gate
# ------------------------------------------------------------

errors = []


if final_headers != EXPECTED_COLUMNS:

    errors.append(
        "Programme output is not exact "
        "21-column canonical schema."
    )


if final_int_headers != INTERNATIONAL_COLUMNS:

    errors.append(
        "International output is not exact "
        "5-column merge schema."
    )


if len(final_rows) != 21:

    errors.append(
        "Expected exactly 21 canonical programmes."
    )


if len(final_int_rows) != 21:

    errors.append(
        "Expected exactly 21 international rows."
    )


if len(final_ids) != len(
    set(final_ids)
):

    errors.append(
        "Duplicate canonical programme IDs."
    )


if set(final_ids) != set(
    final_int_ids
):

    errors.append(
        "International ID set mismatch."
    )


if duration_count != 20:

    errors.append(
        "Expected duration 20/21."
    )


if mode_count != 9:

    errors.append(
        "Expected study_mode 9/21."
    )


if language_count != 21:

    errors.append(
        "Expected language coverage 21/21."
    )


if tuition_count != 19:

    errors.append(
        "Expected tuition 19/21."
    )


if blank_duration_ids != [
    "prog_mo_025",
]:

    errors.append(
        "Unexpected blank-duration ID set."
    )


if blank_tuition_ids != [
    "prog_mo_025",
    "prog_mo_028",
]:

    errors.append(
        "Unexpected blank-tuition ID set."
    )


if unknown_language_ids != [
    "prog_mo_010",
    "prog_mo_022",
]:

    errors.append(
        "Unexpected Unknown-language IDs."
    )


if tuition_parity_errors:

    errors.append(
        "Tuition fee/currency/period parity error."
    )


if freshness != Counter({
    "current": 21,
}):

    errors.append(
        "Expected freshness_status=current for all 21."
    )


if any([
    ielts_count,
    toefl_count,
    intake_count,
    deadline_count,
]):

    errors.append(
        "Unsupported requirements/future "
        "schedule data was unexpectedly populated."
    )


if international_statuses != Counter({
    "verified_yes": 20,
    "unknown": 1,
}):

    errors.append(
        "Expected 20 verified_yes and "
        "1 unknown among canonical programmes."
    )


if verified_yes_blank_urls:

    errors.append(
        "verified_yes international rows "
        "have blank application URLs."
    )


if blank_international_notes:

    errors.append(
        "International requirement notes missing."
    )


if blank_international_dates:

    errors.append(
        "International verification dates missing."
    )


print()
print("=" * 110)


if errors:

    print(
        "STEP 170.2E MACAU FINAL "
        "CANONICAL BUILD: FAIL"
    )

    for error in errors:

        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 170.2E MACAU FINAL "
    "CANONICAL BUILD: PASS"
)

print(
    "21 VERIFIED MACAU PROGRAMMES "
    "ARE CANONICAL-READY"
)

print(
    "INTERNATIONAL ELIGIBILITY MERGE "
    "READY: 21 / 21"
)

print(
    "DEFERRED SLOTS EXCLUDED: 9"
)

print(
    "programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 110)
