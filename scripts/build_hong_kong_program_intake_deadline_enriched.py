import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_tuition_enriched.csv"
)

QUEUE_PATH = Path(
    "planning/"
    "18_hong_kong_program_intake_deadline_research_queue.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_intake_deadline_enriched.csv"
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

    print("=" * 100)
    print(
        "STEP 169.2BO - BUILD HONG KONG "
        "INTAKE/DEADLINE-ENRICHED DATASET"
    )
    print("=" * 100)


    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_PATH}"
        )

    if not QUEUE_PATH.exists():
        raise FileNotFoundError(
            f"Schedule queue not found: {QUEUE_PATH}"
        )

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            "Safety stop: output already exists: "
            f"{OUTPUT_PATH}"
        )


    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)
        headers = reader.fieldnames
        dataset_rows = list(reader)


    if headers != EXPECTED_HEADERS:
        raise ValueError(
            "Input dataset does not match "
            "the exact 21-column programme schema."
        )


    with QUEUE_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        schedule_rows = list(
            csv.DictReader(file)
        )


    if len(dataset_rows) != 45:
        raise ValueError(
            "Expected 45 programme rows."
        )

    if len(schedule_rows) != 45:
        raise ValueError(
            "Expected 45 schedule research rows."
        )


    schedule_by_id = {
        clean(row["program_id"]): row
        for row in schedule_rows
    }


    output_rows = []


    for source_row in dataset_rows:

        program_id = clean(
            source_row["program_id"]
        )

        if program_id not in schedule_by_id:
            raise ValueError(
                f"{program_id}: missing schedule research."
            )


        research = schedule_by_id[
            program_id
        ]


        if clean(
            research["university_id"]
        ) != clean(
            source_row["university_id"]
        ):
            raise ValueError(
                f"{program_id}: university_id mismatch."
            )


        status = clean(
            research[
                "schedule_research_status"
            ]
        )


        if status != "REVIEWED_UNRESOLVED":
            raise ValueError(
                f"{program_id}: expected "
                "REVIEWED_UNRESOLVED, "
                f"found {status!r}."
            )


        if clean(research["intake"]):
            raise ValueError(
                f"{program_id}: unsupported intake "
                "value is present."
            )

        if clean(
            research["application_deadline"]
        ):
            raise ValueError(
                f"{program_id}: unsupported deadline "
                "value is present."
            )


        output = source_row.copy()


        # Preserve blanks in the master dataset.
        output["intake"] = ""
        output["application_deadline"] = ""


        verified_at = clean(
            research["verified_at"]
        )

        if not verified_at:
            raise ValueError(
                f"{program_id}: missing verified_at."
            )


        output[
            "last_verified_at"
        ] = verified_at


        schedule_flag = (
            "Intake/Deadline Reviewed Unresolved"
        )


        existing_freshness = clean(
            output["freshness_status"]
        )


        if schedule_flag not in existing_freshness:

            if existing_freshness:

                output[
                    "freshness_status"
                ] = (
                    f"{existing_freshness}; "
                    f"{schedule_flag}"
                )

            else:

                output[
                    "freshness_status"
                ] = schedule_flag


        output_rows.append(
            output
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
            fieldnames=EXPECTED_HEADERS,
        )

        writer.writeheader()
        writer.writerows(output_rows)


    intake_count = sum(
        bool(clean(row["intake"]))
        for row in output_rows
    )

    deadline_count = sum(
        bool(
            clean(
                row["application_deadline"]
            )
        )
        for row in output_rows
    )


    print(
        "Input programme rows            :",
        len(dataset_rows),
    )

    print(
        "Schedule research rows          :",
        len(schedule_rows),
    )

    print(
        "Output rows                     :",
        len(output_rows),
    )

    print(
        "Stored intake values            :",
        intake_count,
    )

    print(
        "Stored deadline values          :",
        deadline_count,
    )

    print(
        "Evidence-closed schedule blanks :",
        len(output_rows),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )


    if intake_count != 0:
        raise ValueError(
            "Unexpected intake values were stored."
        )

    if deadline_count != 0:
        raise ValueError(
            "Unexpected deadlines were stored."
        )


    print()
    print("=" * 100)

    print(
        "STEP 169.2BO INTAKE/DEADLINE-"
        "ENRICHED DATASET BUILD: PASS"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
