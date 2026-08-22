import csv
from collections import Counter
from pathlib import Path


INPUT_PATH = Path(
    "data/raw/"
    "hong_kong_program_international_research_queue.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_program_international_merge_ready.csv"
)


OUTPUT_HEADERS = [
    "program_id",
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


def clean(value):
    return str(value or "").strip()


print("=" * 100)
print(
    "STEP 169.2BW.1B - BUILD NORMALIZED "
    "INTERNATIONAL MERGE SOURCE"
)
print("=" * 100)


if not INPUT_PATH.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_PATH}"
    )


if OUTPUT_PATH.exists():
    raise FileExistsError(
        "Safety stop: merge-ready output "
        f"already exists: {OUTPUT_PATH}"
    )


with INPUT_PATH.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:

    reader = csv.DictReader(file)

    input_headers = reader.fieldnames or []

    rows = list(reader)


required_input = {
    "program_id",
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "last_verified_at",
}


missing_columns = (
    required_input
    - set(input_headers)
)


if missing_columns:
    raise ValueError(
        "Input research queue missing columns: "
        + ", ".join(
            sorted(missing_columns)
        )
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


if len(actual_ids) != len(rows):
    raise ValueError(
        "Duplicate program_id detected."
    )


output_rows = []


for row in rows:

    program_id = clean(
        row["program_id"]
    )

    status = clean(
        row[
            "international_applicants_status"
        ]
    )

    url = clean(
        row[
            "international_application_url"
        ]
    )

    note = clean(
        row[
            "international_requirements_note"
        ]
    )

    verified_at = clean(
        row["last_verified_at"]
    )


    if status not in {
        "verified_yes",
        "unknown",
    }:
        raise ValueError(
            f"{program_id}: unexpected "
            f"international status {status!r}."
        )


    # VERIFIED eligibility must have a usable
    # international application/admission URL.
    if status == "verified_yes" and not url:
        raise ValueError(
            f"{program_id}: verified_yes row "
            "has no international application URL."
        )


    # UNKNOWN rows may legitimately lack a
    # programme-specific application URL.
    if not note:
        raise ValueError(
            f"{program_id}: blank international "
            "requirements note."
        )


    if not verified_at:
        raise ValueError(
            f"{program_id}: blank last_verified_at."
        )


    output_rows.append(
        {
            "program_id": program_id,

            "international_applicants_status": (
                status
            ),

            "international_application_url": (
                url
            ),

            "international_requirements_note": (
                note
            ),

            "international_applicants_last_verified_at": (
                verified_at
            ),
        }
    )


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


with OUTPUT_PATH.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=OUTPUT_HEADERS,
    )

    writer.writeheader()
    writer.writerows(output_rows)


statuses = Counter(
    row[
        "international_applicants_status"
    ]
    for row in output_rows
)


verified_blank_urls = sum(
    row[
        "international_applicants_status"
    ] == "verified_yes"
    and not row[
        "international_application_url"
    ]
    for row in output_rows
)


unknown_blank_urls = sum(
    row[
        "international_applicants_status"
    ] == "unknown"
    and not row[
        "international_application_url"
    ]
    for row in output_rows
)


blank_notes = sum(
    not row[
        "international_requirements_note"
    ]
    for row in output_rows
)


blank_verified_dates = sum(
    not row[
        "international_applicants_last_verified_at"
    ]
    for row in output_rows
)


print(
    "Input research rows              :",
    len(rows),
)

print(
    "Output merge rows                :",
    len(output_rows),
)

print(
    "International statuses           :",
    dict(statuses),
)

print(
    "verified_yes with blank URL      :",
    verified_blank_urls,
)

print(
    "unknown with blank URL           :",
    unknown_blank_urls,
)

print(
    "Blank requirement notes          :",
    blank_notes,
)

print(
    "Blank international verified_at  :",
    blank_verified_dates,
)


if statuses.get(
    "verified_yes",
    0,
) != 39:
    raise ValueError(
        "Expected exactly 39 verified_yes rows."
    )


if statuses.get(
    "unknown",
    0,
) != 6:
    raise ValueError(
        "Expected exactly 6 unknown rows."
    )


if verified_blank_urls:
    raise ValueError(
        "One or more verified_yes records "
        "lack an international URL."
    )


if blank_notes:
    raise ValueError(
        "International requirement notes "
        "must be evidence-complete."
    )


if blank_verified_dates:
    raise ValueError(
        "International verification dates "
        "must be complete."
    )


print()
print(
    "Output:",
    OUTPUT_PATH,
)

print()
print("=" * 100)

print(
    "STEP 169.2BW.1B NORMALIZED "
    "INTERNATIONAL MERGE SOURCE: PASS"
)

print(
    "UNKNOWN ELIGIBILITY ROWS MAY "
    "SAFELY RETAIN BLANK APPLICATION URLs"
)

print(
    "ORIGINAL RESEARCH QUEUE WAS NOT MODIFIED"
)

print(
    "WORKBOOK AND MONGODB WERE NOT MODIFIED"
)

print("=" * 100)
