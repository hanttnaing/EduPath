import csv
from collections import Counter
from pathlib import Path


BEFORE_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_requirements_enriched.csv"
)

AFTER_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_tuition_enriched.csv"
)


ALLOWED_FIELDS = {
    "tuition_fee",
    "tuition_currency",
    "tuition_period",
    "last_verified_at",
    "freshness_status",
}


def clean(value):
    return str(value or "").strip()


def read(path):

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        return (
            reader.fieldnames,
            list(reader),
        )


before_headers, before_rows = read(
    BEFORE_PATH
)

after_headers, after_rows = read(
    AFTER_PATH
)


print("=" * 100)
print(
    "STEP 169.2BF - HONG KONG "
    "TUITION PARITY AUDIT"
)
print("=" * 100)

print(
    "Before rows                       :",
    len(before_rows),
)

print(
    "After rows                        :",
    len(after_rows),
)

print(
    "Header parity                     :",
    before_headers == after_headers,
)


if before_headers != after_headers:
    raise ValueError(
        "Headers changed."
    )


before_by_id = {
    clean(row["program_id"]): row
    for row in before_rows
}

after_by_id = {
    clean(row["program_id"]): row
    for row in after_rows
}


print(
    "ID set parity                     :",
    set(before_by_id)
    == set(after_by_id),
)


changes = Counter()

unexpected = []


for program_id in sorted(
    before_by_id
):

    before = before_by_id[
        program_id
    ]

    after = after_by_id[
        program_id
    ]


    for field in before_headers:

        a = clean(
            before.get(field)
        )

        b = clean(
            after.get(field)
        )


        if a == b:
            continue


        changes[field] += 1


        if field not in ALLOWED_FIELDS:

            unexpected.append(
                (
                    program_id,
                    field,
                    a,
                    b,
                )
            )


print()
print("FIELD CHANGE COUNTS")
print("-" * 100)

for field, count in sorted(
    changes.items()
):
    print(
        f"{field:<32}: {count}"
    )


print()
print(
    "Unexpected field changes          :",
    len(unexpected),
)


if unexpected:

    for item in unexpected[:20]:
        print(item)


numeric_after = sum(
    bool(
        clean(row["tuition_fee"])
    )
    for row in after_rows
)


blank_after = (
    len(after_rows)
    - numeric_after
)


print(
    "Numeric tuition after             :",
    numeric_after,
)

print(
    "Blank tuition after               :",
    blank_after,
)


errors = []


if len(before_rows) != 45:
    errors.append(
        "Before dataset must have 45 rows."
    )

if len(after_rows) != 45:
    errors.append(
        "After dataset must have 45 rows."
    )

if (
    set(before_by_id)
    != set(after_by_id)
):
    errors.append(
        "Programme ID set changed."
    )

if unexpected:
    errors.append(
        "Unexpected fields changed."
    )

if numeric_after != 35:
    errors.append(
        "Expected 35 numeric tuition rows."
    )

if blank_after != 10:
    errors.append(
        "Expected 10 blank tuition rows."
    )


print()
print("=" * 100)


if errors:

    print(
        "STEP 169.2BF TUITION "
        "PARITY AUDIT: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 169.2BF TUITION "
    "PARITY AUDIT: PASS"
)

print(
    "Only approved tuition-related "
    "fields changed."
)

print(
    "NO WORKBOOK OR MONGODB DATA WAS MODIFIED"
)

print("=" * 100)
