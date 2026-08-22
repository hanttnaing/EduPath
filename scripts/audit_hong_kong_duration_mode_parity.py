import csv
from pathlib import Path


BEFORE = Path(
    "data/cleaned/"
    "hong_kong_programs_fields_enriched.csv"
)

AFTER = Path(
    "data/cleaned/"
    "hong_kong_programs_duration_mode_enriched.csv"
)


ALLOWED_FIELDS = {
    "duration_years",
    "study_mode",
    "last_verified_at",
    "freshness_status",
}


def clean(value):
    return str(value or "").strip()


with BEFORE.open(
    encoding="utf-8-sig",
    newline=""
) as f:
    before_rows = list(csv.DictReader(f))


with AFTER.open(
    encoding="utf-8-sig",
    newline=""
) as f:
    after_rows = list(csv.DictReader(f))


print("=" * 90)
print(
    "STEP 169.2AC - HONG KONG "
    "DURATION/MODE PARITY AUDIT"
)
print("=" * 90)
print()


print("STRUCTURE")
print("-" * 90)

print(
    "Before rows:",
    len(before_rows)
)

print(
    "After rows :",
    len(after_rows)
)


unexpected = []

changed = []


before_map = {
    row["program_id"]: row
    for row in before_rows
}

after_map = {
    row["program_id"]: row
    for row in after_rows
}


for pid in before_map:

    old = before_map[pid]
    new = after_map[pid]

    for field in old:

        if clean(old[field]) != clean(new[field]):

            changed.append(
                (pid, field)
            )

            if field not in ALLOWED_FIELDS:
                unexpected.append(
                    (pid, field)
                )


duration_complete = sum(
    bool(
        clean(
            row["duration_years"]
        )
    )
    for row in after_rows
)


mode_complete = sum(
    bool(
        clean(
            row["study_mode"]
        )
    )
    for row in after_rows
)


print()
print("CHANGE CONTROL")
print("-" * 90)

print(
    "Total changed fields:",
    len(changed)
)

print(
    "Unexpected changes:",
    len(unexpected)
)

print()

print("ENRICHMENT STATE")
print("-" * 90)

print(
    "Duration completed:",
    duration_complete
)

print(
    "Study mode completed:",
    mode_complete
)


print()

if (
    len(unexpected) == 0
    and duration_complete == 45
    and mode_complete == 45
):

    print("=" * 90)
    print(
        "STEP 169.2AC HONG KONG "
        "DURATION/MODE PARITY AUDIT: PASS"
    )
    print(
        "ONLY APPROVED FIELDS CHANGED"
    )
    print(
        "READY FOR STEP 169.2AD "
        "LANGUAGE RESEARCH QUEUE"
    )
    print("=" * 90)

else:

    print("=" * 90)
    print(
        "STEP 169.2AC AUDIT: FAIL"
    )
    print("=" * 90)


print()
print(
    "NO FILES OR DATABASE RECORDS WERE MODIFIED"
)