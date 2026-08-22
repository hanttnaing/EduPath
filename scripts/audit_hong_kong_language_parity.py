import csv
from pathlib import Path


BEFORE = Path(
    "data/cleaned/"
    "hong_kong_programs_duration_mode_enriched.csv"
)

AFTER = Path(
    "data/cleaned/"
    "hong_kong_programs_language_enriched.csv"
)


ALLOWED_CHANGES = {
    "language_of_instruction",
    "last_verified_at",
    "freshness_status",
}


def main():

    print("=" * 90)
    print(
        "STEP 169.2AO - HONG KONG "
        "FINAL LANGUAGE PARITY AUDIT"
    )
    print("=" * 90)


    with BEFORE.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        before_rows = list(
            csv.DictReader(f)
        )


    with AFTER.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        after_rows = list(
            csv.DictReader(f)
        )


    before_map = {
        row["program_id"]: row
        for row in before_rows
    }

    after_map = {
        row["program_id"]: row
        for row in after_rows
    }


    unexpected = []
    approved_changes = 0


    for pid in before_map:

        before = before_map[pid]
        after = after_map[pid]


        for key in before.keys():

            if before[key] != after[key]:

                if key in ALLOWED_CHANGES:
                    approved_changes += 1

                else:
                    unexpected.append(
                        {
                            "program_id": pid,
                            "field": key
                        }
                    )


    print()
    print("STRUCTURE")
    print("-" * 90)

    print(
        f"Before rows : {len(before_rows)}"
    )

    print(
        f"After rows  : {len(after_rows)}"
    )


    print()
    print("CHANGE CONTROL")
    print("-" * 90)

    print(
        f"Approved field changes : {approved_changes}"
    )

    print(
        f"Unexpected changes     : {len(unexpected)}"
    )


    print()
    print("=" * 90)


    if (
        len(before_rows) == 45
        and len(after_rows) == 45
        and len(unexpected) == 0
    ):

        print(
            "STEP 169.2AO HONG KONG "
            "FINAL LANGUAGE PARITY AUDIT: PASS"
        )

        print(
            "ONLY APPROVED LANGUAGE ENRICHMENT "
            "FIELDS CHANGED"
        )

        print(
            "READY FOR DATABASE IMPORT PREPARATION"
        )

    else:

        print(
            "STEP 169.2AO AUDIT: FAIL"
        )

        print(unexpected[:5])


if __name__ == "__main__":
    main()

