import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_preimport_corrected.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_final_ready.csv"
)


EXPECTED_HEADERS = [
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


def clean(value):
    return str(value or "").strip()


print("=" * 100)
print(
    "STEP 169.2BV - HONG KONG "
    "FINAL FRESHNESS NORMALIZATION"
)
print("=" * 100)


if not INPUT_PATH.exists():
    raise FileNotFoundError(
        f"Input not found: {INPUT_PATH}"
    )


if OUTPUT_PATH.exists():

    print(
        "Safety stop: final-ready file "
        "already exists:"
    )

    print(
        OUTPUT_PATH
    )

    print(
        "No file was overwritten."
    )

    raise SystemExit(1)


with INPUT_PATH.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as f:

    reader = csv.DictReader(f)

    headers = reader.fieldnames or []

    rows = list(reader)


if headers != EXPECTED_HEADERS:
    raise ValueError(
        "Input does not match the exact "
        "21-column programme contract."
    )


if len(rows) != 45:
    raise ValueError(
        f"Expected 45 rows, found {len(rows)}."
    )


expected_ids = {
    f"prog_hk_{i:03d}"
    for i in range(1, 46)
}

actual_ids = {
    clean(row["program_id"])
    for row in rows
}


if actual_ids != expected_ids:
    raise ValueError(
        "Programme ID set is not exactly "
        "prog_hk_001 through prog_hk_045."
    )


for row in rows:

    row[
        "freshness_status"
    ] = "current"


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


with OUTPUT_PATH.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=EXPECTED_HEADERS,
    )

    writer.writeheader()
    writer.writerows(rows)


current_count = sum(
    clean(row["freshness_status"])
    == "current"
    for row in rows
)

tuition_numeric = sum(
    bool(clean(row["tuition_fee"]))
    for row in rows
)

toefl_numeric = sum(
    bool(clean(row["toefl_requirement"]))
    for row in rows
)

unknown_language = [
    row["program_id"]
    for row in rows
    if clean(
        row["language_of_instruction"]
    ) == "Unknown"
]

intake_count = sum(
    bool(clean(row["intake"]))
    for row in rows
)

deadline_count = sum(
    bool(clean(row["application_deadline"]))
    for row in rows
)


print(
    "Rows normalized                 :",
    len(rows),
)

print(
    "freshness_status = current       :",
    current_count,
)

print(
    "Numeric tuition rows             :",
    tuition_numeric,
)

print(
    "Blank tuition rows               :",
    len(rows) - tuition_numeric,
)

print(
    "Numeric TOEFL rows               :",
    toefl_numeric,
)

print(
    "Unknown language rows            :",
    len(unknown_language),
)

print(
    "Unknown language IDs             :",
    ", ".join(unknown_language),
)

print(
    "Stored intake rows               :",
    intake_count,
)

print(
    "Stored deadline rows             :",
    deadline_count,
)

print()
print(
    "Output:",
    OUTPUT_PATH,
)


errors = []


if current_count != 45:
    errors.append(
        "Expected 45 current rows."
    )

if tuition_numeric != 35:
    errors.append(
        "Expected 35 numeric tuition rows."
    )

if toefl_numeric != 24:
    errors.append(
        "Expected 24 numeric TOEFL rows."
    )

if sorted(unknown_language) != [
    "prog_hk_020",
    "prog_hk_028",
]:
    errors.append(
        "Unexpected Unknown language set."
    )

if intake_count != 0:
    errors.append(
        "Unexpected 2027 intake values exist."
    )

if deadline_count != 0:
    errors.append(
        "Unexpected 2027 deadline values exist."
    )


print()
print("=" * 100)


if errors:

    print(
        "STEP 169.2BV FINAL FRESHNESS "
        "NORMALIZATION: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 169.2BV FINAL FRESHNESS "
    "NORMALIZATION: PASS"
)

print(
    "HONG KONG 21-COLUMN DATASET "
    "IS TRANSFORM-COMPATIBLE"
)

print(
    "WORKBOOK AND MONGODB WERE NOT MODIFIED"
)

print("=" * 100)
