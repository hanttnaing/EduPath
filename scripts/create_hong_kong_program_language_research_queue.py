import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_duration_mode_enriched.csv"
)

OUTPUT_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


EXPECTED_COUNT = 45


OUTPUT_HEADERS = [
    "program_id",
    "university_id",
    "program_name",
    "field_of_study",
    "degree_level",
    "duration_years",
    "study_mode",
    "program_url",
    "language_of_instruction",
    "language_research_status",
    "language_source_name",
    "language_source_url",
    "language_reason",
    "verified_at",
]


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 80)
    print(
        "STEP 169.2AD - CREATE HONG KONG "
        "LANGUAGE RESEARCH QUEUE"
    )
    print("=" * 80)


    with INPUT_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        rows = list(csv.DictReader(f))


    if len(rows) != EXPECTED_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_COUNT} programmes."
        )


    ids = [
        clean(row["program_id"])
        for row in rows
    ]


    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate programme IDs detected."
        )


    output_rows = []


    for row in rows:

        output_rows.append(
            {
                "program_id":
                    clean(row["program_id"]),

                "university_id":
                    clean(row["university_id"]),

                "program_name":
                    clean(row["program_name"]),

                "field_of_study":
                    clean(row["field_of_study"]),

                "degree_level":
                    clean(row["degree_level"]),

                "duration_years":
                    clean(row["duration_years"]),

                "study_mode":
                    clean(row["study_mode"]),

                "program_url":
                    clean(row["program_url"]),

                "language_of_instruction":
                    "",

                "language_research_status":
                    "PENDING",

                "language_source_name":
                    "",

                "language_source_url":
                    "",

                "language_reason":
                    "",

                "verified_at":
                    "",
            }
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
            fieldnames=OUTPUT_HEADERS
        )

        writer.writeheader()
        writer.writerows(output_rows)


    print()
    print("QUEUE BUILD RESULT")
    print("-" * 80)
    print(
        f"Rows                         : "
        f"{len(output_rows)}"
    )

    print(
        f"Full prog_hk_001-045 range   : "
        f"{ids[0] == 'prog_hk_001' and ids[-1] == 'prog_hk_045'}"
    )

    print(
        "Duplicate programme IDs      : 0"
    )

    print(
        "Language research PENDING    : "
        f"{len(output_rows)}"
    )

    print()
    print("=" * 80)
    print(
        "STEP 169.2AD HONG KONG "
        "LANGUAGE RESEARCH QUEUE: PASS"
    )
    print(
        "45 / 45 PROGRAMMES READY FOR "
        "OFFICIAL-SOURCE LANGUAGE RESEARCH"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()