import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_duration_mode_enriched.csv"
)


RESEARCH_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_language_enriched.csv"
)


EXPECTED_ROWS = 45


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 90)
    print(
        "STEP 169.2AN - HONG KONG "
        "LANGUAGE ENRICHED DATASET BUILD"
    )
    print("=" * 90)


    with INPUT_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        master_rows = list(
            csv.DictReader(f)
        )


    with RESEARCH_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        language_rows = list(
            csv.DictReader(f)
        )


    language_map = {
        clean(row["program_id"]): row
        for row in language_rows
    }


    output_rows = []


    for row in master_rows:

        program_id = clean(
            row["program_id"]
        )


        if program_id not in language_map:
            raise ValueError(
                f"Missing language research: {program_id}"
            )


        research = language_map[program_id]


        new_row = dict(row)


        new_row["language_of_instruction"] = (
            research["language_of_instruction"]
        )


        new_row["last_verified_at"] = (
            research["verified_at"]
        )


        existing_status = clean(
            row.get("freshness_status")
        )


        addition = (
            "Language Verified"
        )


        if existing_status:
            new_row["freshness_status"] = (
                f"{existing_status}; {addition}"
            )
        else:
            new_row["freshness_status"] = addition


        output_rows.append(new_row)



    if len(output_rows) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} rows"
        )


    ids = [
        row["program_id"]
        for row in output_rows
    ]


    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate programme IDs"
        )


    for row in output_rows:

        if not clean(
            row["language_of_instruction"]
        ):
            raise ValueError(
                f"Missing language: {row['program_id']}"
            )


    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=output_rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(output_rows)



    print()
    print("BUILD RESULT")
    print("-" * 90)

    print(
        f"Input rows       : {len(master_rows)}"
    )

    print(
        f"Language rows    : {len(language_rows)}"
    )

    print(
        f"Output rows      : {len(output_rows)}"
    )


    print()
    print("=" * 90)

    print(
        "STEP 169.2AN HONG KONG "
        "LANGUAGE ENRICHED DATASET BUILD: PASS"
    )

    print(
        "45 / 45 PROGRAMMES HAVE LANGUAGE DATA"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )



if __name__ == "__main__":
    main()

