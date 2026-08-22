import csv
from collections import Counter
from pathlib import Path


BEFORE_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_language_enriched.csv"
)

AFTER_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_requirements_enriched.csv"
)


ALLOWED_CHANGE_FIELDS = {
    "minimum_gpa",
    "gpa_scale",
    "ielts_requirement",
    "toefl_requirement",
    "last_verified_at",
    "freshness_status",
}


def clean(value):
    return str(value or "").strip()


def read_csv(path):
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


print("=" * 100)
print(
    "STEP 169.2AW - HONG KONG "
    "REQUIREMENTS PARITY AUDIT"
)
print("=" * 100)


before_headers, before_rows = read_csv(
    BEFORE_PATH
)

after_headers, after_rows = read_csv(
    AFTER_PATH
)


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
        "Before/after headers differ."
    )


before_by_id = {
    clean(row["program_id"]): row
    for row in before_rows
}

after_by_id = {
    clean(row["program_id"]): row
    for row in after_rows
}


before_ids = set(
    before_by_id
)

after_ids = set(
    after_by_id
)


print(
    "ID set parity                     :",
    before_ids == after_ids,
)

print(
    "Duplicate IDs before              :",
    len(before_rows) - len(before_ids),
)

print(
    "Duplicate IDs after               :",
    len(after_rows) - len(after_ids),
)


if before_ids != after_ids:
    raise ValueError(
        "Programme ID sets differ."
    )


field_change_counts = Counter()

approved_changes = []
unexpected_changes = []


for program_id in sorted(before_ids):

    before = before_by_id[
        program_id
    ]

    after = after_by_id[
        program_id
    ]

    for field in before_headers:

        before_value = clean(
            before.get(field)
        )

        after_value = clean(
            after.get(field)
        )

        if before_value == after_value:
            continue

        field_change_counts[
            field
        ] += 1

        change = (
            program_id,
            field,
            before_value,
            after_value,
        )

        if field in ALLOWED_CHANGE_FIELDS:
            approved_changes.append(
                change
            )

        else:
            unexpected_changes.append(
                change
            )


print()
print("FIELD CHANGE COUNTS")
print("-" * 100)

if field_change_counts:

    for field, count in sorted(
        field_change_counts.items()
    ):
        print(
            f"{field:<32}: {count}"
        )

else:
    print(
        "No field changes detected."
    )


print()
print(
    "Approved field changes             :",
    len(approved_changes),
)

print(
    "Unexpected field changes           :",
    len(unexpected_changes),
)


if unexpected_changes:

    print()
    print("UNEXPECTED CHANGES")
    print("-" * 100)

    for (
        program_id,
        field,
        before_value,
        after_value,
    ) in unexpected_changes[:20]:

        print(
            program_id,
            "|",
            field,
            "|",
            repr(before_value),
            "->",
            repr(after_value),
        )


errors = []


if len(before_rows) != 45:
    errors.append(
        "Before dataset must contain 45 rows."
    )

if len(after_rows) != 45:
    errors.append(
        "After dataset must contain 45 rows."
    )

if before_headers != after_headers:
    errors.append(
        "Headers changed."
    )

if before_ids != after_ids:
    errors.append(
        "Programme ID set changed."
    )

if unexpected_changes:
    errors.append(
        "Unexpected fields changed."
    )


print()
print("=" * 100)


if errors:

    print(
        "STEP 169.2AW REQUIREMENTS "
        "PARITY AUDIT: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 169.2AW REQUIREMENTS "
    "PARITY AUDIT: PASS"
)

print(
    "Only approved requirement-related "
    "fields changed."
)

print(
    "NO WORKBOOK OR MONGODB DATA WAS MODIFIED"
)

print("=" * 100)
