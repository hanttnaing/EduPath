import csv
from pathlib import Path
from datetime import date


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_fields_enriched.csv"
)

RESEARCH_PATH = Path(
    "planning/"
    "14_hong_kong_program_duration_mode_research_queue.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_duration_mode_enriched.csv"
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


def main():

    print("=" * 80)
    print(
        "STEP 169.2AB - HONG KONG "
        "DURATION/MODE ENRICHED DATASET BUILD"
    )
    print("=" * 80)

    with INPUT_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        master_rows = list(csv.DictReader(f))

    with RESEARCH_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        research_rows = list(csv.DictReader(f))


    research_map = {
        clean(row["program_id"]): row
        for row in research_rows
    }


    output_rows = []


    for row in master_rows:

        program_id = clean(
            row["program_id"]
        )

        research = research_map.get(
            program_id
        )

        if research is None:
            raise ValueError(
                f"Missing research row: {program_id}"
            )


        new_row = dict(row)


        new_row["duration_years"] = (
            research["duration_years"]
        )

        new_row["study_mode"] = (
            research["study_mode"]
        )

        new_row["last_verified_at"] = (
            research["verified_at"]
        )

        existing_status = clean(
            row.get("freshness_status")
        )

        addition = (
            "Duration Verified; "
            "Study Mode Verified"
        )

        if existing_status:
            new_row["freshness_status"] = (
                f"{existing_status}; {addition}"
            )
        else:
            new_row["freshness_status"] = addition


        output_rows.append(new_row)


    if len(output_rows) != 45:
        raise ValueError(
            "Expected exactly 45 Hong Kong programmes."
        )


    ids = [
        row["program_id"]
        for row in output_rows
    ]


    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate programme IDs detected."
        )


    for row in output_rows:

        if not row["duration_years"]:
            raise ValueError(
                f"Missing duration: "
                f"{row['program_id']}"
            )

        if not row["study_mode"]:
            raise ValueError(
                f"Missing study mode: "
                f"{row['program_id']}"
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
            fieldnames=EXPECTED_HEADERS
        )

        writer.writeheader()
        writer.writerows(output_rows)


    print()
    print("BUILD RESULT")
    print("-" * 80)

    print(
        "Input rows       :",
        len(master_rows)
    )

    print(
        "Research rows    :",
        len(research_rows)
    )

    print(
        "Output rows      :",
        len(output_rows)
    )

    print(
        "Output columns   :",
        len(EXPECTED_HEADERS)
    )

    print()

    print(
        "Output:",
        OUTPUT_PATH
    )

    print()
    print(
        "STEP 169.2AB BUILD COMPLETE"
    )


if __name__ == "__main__":
    main()