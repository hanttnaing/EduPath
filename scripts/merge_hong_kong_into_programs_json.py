import csv
import json
from collections import Counter
from pathlib import Path

import transform_programs as tp


EXISTING_JSON = Path(
    "data/cleaned/programs.json"
)

HK_CSV = Path(
    "data/cleaned/"
    "hong_kong_programs_final_ready.csv"
)

INTERNATIONAL_CSV = Path(
    "data/cleaned/"
    "hong_kong_program_international_merge_ready.csv"
)

OUTPUT_JSON = Path(
    "data/cleaned/"
    "programs_with_hong_kong_staging.json"
)


EXPECTED_EXISTING_COUNT = 291
EXPECTED_HK_COUNT = 45
EXPECTED_FINAL_COUNT = 336


EXPECTED_HK_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(1, 46)
}


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
}


INTERNATIONAL_FIELDS = [
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


def clean(value):
    return str(value or "").strip()


def prefix(program_id):

    parts = program_id.split("_")

    if len(parts) >= 3:
        return "_".join(parts[:2])

    return "unknown"


print("=" * 105)
print(
    "STEP 169.3B - FAST SAFE "
    "HONG KONG JSON MERGE"
)
print("=" * 105)


# -------------------------------------------------
# Safety: staging file only
# -------------------------------------------------

if OUTPUT_JSON.exists():

    raise FileExistsError(
        "Safety stop: staging JSON already exists: "
        f"{OUTPUT_JSON}"
    )


for path in [
    EXISTING_JSON,
    HK_CSV,
    INTERNATIONAL_CSV,
]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required input missing: {path}"
        )


# -------------------------------------------------
# 1. Existing 291 JSON records
# -------------------------------------------------

with EXISTING_JSON.open(
    "r",
    encoding="utf-8",
) as file:

    existing_records = json.load(file)


if not isinstance(
    existing_records,
    list,
):

    raise ValueError(
        "Existing programs.json must contain a list."
    )


existing_ids = [
    clean(
        row.get("program_id")
    )
    for row in existing_records
]


if len(existing_records) != EXPECTED_EXISTING_COUNT:

    raise ValueError(
        "Expected existing programs.json to contain "
        f"{EXPECTED_EXISTING_COUNT} rows, found "
        f"{len(existing_records)}."
    )


if len(existing_ids) != len(set(existing_ids)):

    raise ValueError(
        "Duplicate program_id exists in current "
        "programs.json."
    )


existing_hk_ids = {
    program_id
    for program_id in existing_ids
    if program_id.startswith(
        "prog_hk_"
    )
}


if existing_hk_ids:

    raise ValueError(
        "Safety stop: existing programs.json already "
        "contains Hong Kong records."
    )


# -------------------------------------------------
# 2. Read final-ready Hong Kong CSV
# -------------------------------------------------

with HK_CSV.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    hk_headers = reader.fieldnames or []
    hk_raw_rows = list(reader)


if hk_headers != tp.EXPECTED_COLUMNS:

    raise ValueError(
        "Hong Kong final-ready CSV does not match "
        "transform_programs.py EXPECTED_COLUMNS."
    )


if len(hk_raw_rows) != EXPECTED_HK_COUNT:

    raise ValueError(
        f"Expected 45 Hong Kong rows, found "
        f"{len(hk_raw_rows)}."
    )


hk_raw_ids = {
    clean(row["program_id"])
    for row in hk_raw_rows
}


if hk_raw_ids != EXPECTED_HK_IDS:

    raise ValueError(
        "Hong Kong source ID set mismatch."
    )


# -------------------------------------------------
# 3. Transform HK using project's existing
#    transform_program() logic
# -------------------------------------------------

valid_university_ids = (
    tp.load_valid_university_ids()
)


hk_cleaned_records = []


for row_number, raw_record in enumerate(
    hk_raw_rows,
    start=2,
):

    # csv.DictReader returns blank cells as "".
    # transform_program.py normally receives records
    # originating from Excel/Pandas, where optional
    # blank cells are represented as None/NaN.
    #
    # Normalize CSV blanks to None before reusing the
    # project's existing transformation logic.
    normalized_raw_record = {
        key: (
            None
            if clean(value) == ""
            else value
        )
        for key, value in raw_record.items()
    }

    cleaned_record = tp.transform_program(
        raw_record=normalized_raw_record,
        row_number=row_number,
        valid_university_ids=(
            valid_university_ids
        ),
    )

    hk_cleaned_records.append(
        cleaned_record
    )


tp.validate_unique_program_ids(
    hk_cleaned_records
)

tp.validate_unique_program_signatures(
    hk_cleaned_records
)


hk_transformed_ids = {
    clean(row["program_id"])
    for row in hk_cleaned_records
}


if hk_transformed_ids != EXPECTED_HK_IDS:

    raise ValueError(
        "Hong Kong transformed ID set mismatch."
    )


# -------------------------------------------------
# 4. Load normalized international fields
# -------------------------------------------------

with INTERNATIONAL_CSV.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    international_rows = list(reader)


if len(international_rows) != 45:

    raise ValueError(
        "International merge source must "
        "contain 45 rows."
    )


international_by_id = {
    clean(row["program_id"]): row
    for row in international_rows
}


if set(
    international_by_id
) != EXPECTED_HK_IDS:

    raise ValueError(
        "International merge ID set mismatch."
    )


# -------------------------------------------------
# 5. Merge international data into HK records
# -------------------------------------------------

for record in hk_cleaned_records:

    program_id = clean(
        record["program_id"]
    )

    intl = international_by_id[
        program_id
    ]

    for field in INTERNATIONAL_FIELDS:

        record[field] = clean(
            intl.get(field)
        )


# -------------------------------------------------
# 6. Preserve all existing records + append HK
# -------------------------------------------------

merged_records = (
    existing_records
    + hk_cleaned_records
)


merged_ids = [
    clean(
        row.get("program_id")
    )
    for row in merged_records
]


if len(merged_records) != EXPECTED_FINAL_COUNT:

    raise ValueError(
        f"Expected {EXPECTED_FINAL_COUNT} merged rows, "
        f"found {len(merged_records)}."
    )


if len(merged_ids) != len(set(merged_ids)):

    raise ValueError(
        "Duplicate program_id created during merge."
    )


# Existing 291 IDs must be completely preserved.
merged_id_set = set(
    merged_ids
)

missing_existing = (
    set(existing_ids)
    - merged_id_set
)


if missing_existing:

    raise ValueError(
        "Existing programme IDs were lost: "
        + ", ".join(
            sorted(missing_existing)[:20]
        )
    )


# -------------------------------------------------
# 7. Prefix audit
# -------------------------------------------------

prefix_counts = Counter(
    prefix(program_id)
    for program_id in merged_ids
)


if dict(prefix_counts) != EXPECTED_PREFIX_COUNTS:

    raise ValueError(
        "Merged programme prefix counts are "
        f"unexpected: {dict(prefix_counts)}"
    )


# -------------------------------------------------
# 8. HK-specific final validation
# -------------------------------------------------

hk_final = [
    row
    for row in merged_records
    if clean(
        row.get("program_id")
    ).startswith(
        "prog_hk_"
    )
]


international_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in hk_final
)


numeric_tuition = sum(
    row.get("tuition_fee")
    is not None
    for row in hk_final
)


numeric_toefl = sum(
    row.get("toefl_requirement")
    is not None
    for row in hk_final
)


unknown_language = sorted(
    clean(row["program_id"])
    for row in hk_final
    if clean(
        row.get(
            "language_of_instruction"
        )
    ) == "Unknown"
)


if international_statuses != Counter({
    "verified_yes": 39,
    "unknown": 6,
}):

    raise ValueError(
        "Hong Kong international status count mismatch."
    )


if numeric_tuition != 35:

    raise ValueError(
        "Expected 35 HK numeric tuition rows."
    )


if numeric_toefl != 24:

    raise ValueError(
        "Expected 24 HK numeric TOEFL rows."
    )


if unknown_language != [
    "prog_hk_020",
    "prog_hk_028",
]:

    raise ValueError(
        "Unexpected HK Unknown language set."
    )


# -------------------------------------------------
# 9. Write STAGING file only
# -------------------------------------------------

OUTPUT_JSON.parent.mkdir(
    parents=True,
    exist_ok=True,
)


with OUTPUT_JSON.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        merged_records,
        file,
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
    )


# -------------------------------------------------
# Summary
# -------------------------------------------------

print(
    "Existing programmes preserved     :",
    len(existing_records),
)

print(
    "Hong Kong programmes added        :",
    len(hk_cleaned_records),
)

print(
    "Merged staging programmes         :",
    len(merged_records),
)

print(
    "Duplicate IDs                     :",
    len(merged_ids)
    - len(set(merged_ids)),
)

print(
    "Missing existing IDs              :",
    len(missing_existing),
)

print()
print(
    "Programme prefix counts           :",
    dict(prefix_counts),
)

print()
print(
    "HK numeric tuition rows           :",
    numeric_tuition,
)

print(
    "HK numeric TOEFL rows             :",
    numeric_toefl,
)

print(
    "HK Unknown language IDs           :",
    ", ".join(
        unknown_language
    ),
)

print(
    "HK international statuses        :",
    dict(
        international_statuses
    ),
)

print()
print(
    "Staging JSON:",
    OUTPUT_JSON,
)

print()
print("=" * 105)

print(
    "STEP 169.3B FAST SAFE "
    "HONG KONG JSON MERGE: PASS"
)

print(
    "ALL EXISTING 291 PROGRAMMES "
    "WERE PRESERVED"
)

print(
    "45 HONG KONG PROGRAMMES WERE "
    "ADDED TO A STAGING JSON"
)

print(
    "ORIGINAL programs.json WAS NOT MODIFIED"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 105)
