import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_language_enriched.csv"
)


EXPECTED_ROWS = 45


REQUIRED_FIELDS = [
    "program_id",
    "university_id",
    "program_name",
    "field_of_study",
    "degree_level",
    "duration_years",
    "study_mode",
    "language_of_instruction",
    "program_url",
]


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 90)
    print(
        "STEP 169.2AP - HONG KONG "
        "FINAL PROGRAMME DATA VALIDATION"
    )
    print("=" * 90)


    with INPUT_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        rows = list(
            csv.DictReader(f)
        )


    duplicate_ids = (
        len(
            [
                r["program_id"]
                for r in rows
            ]
        )
        !=
        len(
            set(
                r["program_id"]
                for r in rows
            )
        )
    )


    print()
    print("DATASET")
    print("-" * 90)

    print(
        f"Programme rows : {len(rows)}"
    )


    print()
    print("COMPLETENESS")
    print("-" * 90)


    for field in REQUIRED_FIELDS:

        blanks = sum(
            1
            for row in rows
            if not clean(row.get(field))
        )

        print(
            f"{field}: blank={blanks}"
        )


    print()
    print("DUPLICATE CHECK")
    print("-" * 90)

    print(
        f"Duplicate IDs : {duplicate_ids}"
    )


    print()
    print("=" * 90)


    if (
        len(rows) == EXPECTED_ROWS
        and not duplicate_ids
    ):

        print(
            "STEP 169.2AP HONG KONG "
            "FINAL PROGRAMME DATA VALIDATION: PASS"
        )

        print(
            "READY FOR MONGODB IMPORT PREPARATION"
        )

    else:

        print(
            "STEP 169.2AP VALIDATION: FAIL"
        )


if __name__ == "__main__":
    main()

