import csv
from pathlib import Path


INPUT_DATASET = Path(
    "data/cleaned/"
    "hong_kong_programs_language_enriched.csv"
)

RESEARCH_QUEUE = Path(
    "planning/"
    "16_hong_kong_program_requirements_research_queue.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_requirements_enriched.csv"
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
        "STEP 169.2AV - BUILD HONG KONG "
        "REQUIREMENTS-ENRICHED DATASET"
    )
    print("=" * 100)


    if not INPUT_DATASET.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_DATASET}"
        )

    if not RESEARCH_QUEUE.exists():
        raise FileNotFoundError(
            f"Research queue not found: {RESEARCH_QUEUE}"
        )

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            "Safety stop: output already exists: "
            f"{OUTPUT_PATH}"
        )


    with INPUT_DATASET.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        headers = reader.fieldnames

        dataset_rows = list(reader)


    if headers != EXPECTED_HEADERS:
        raise ValueError(
            "Input dataset does not match the "
            "expected 21-column programme schema."
        )


    with RESEARCH_QUEUE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        research_rows = list(
            csv.DictReader(file)
        )


    if len(dataset_rows) != 45:
        raise ValueError(
            "Expected 45 programme rows in dataset."
        )

    if len(research_rows) != 45:
        raise ValueError(
            "Expected 45 requirements research rows."
        )


    research_by_id = {
        clean(row["program_id"]): row
        for row in research_rows
    }


    output_rows = []


    for row in dataset_rows:

        program_id = clean(
            row["program_id"]
        )

        if program_id not in research_by_id:
            raise ValueError(
                f"No requirements research found "
                f"for {program_id}."
            )


        research = research_by_id[
            program_id
        ]


        if clean(
            research[
                "requirements_research_status"
            ]
        ) != "VERIFIED":

            raise ValueError(
                f"{program_id}: requirements "
                "research is not VERIFIED."
            )


        if clean(
            research["university_id"]
        ) != clean(
            row["university_id"]
        ):

            raise ValueError(
                f"{program_id}: university_id "
                "mismatch."
            )


        enriched = row.copy()


        # Numeric GPA remains blank unless
        # a universal numeric threshold was verified.
        enriched["minimum_gpa"] = clean(
            research["minimum_gpa"]
        )

        enriched["gpa_scale"] = clean(
            research["gpa_scale"]
        )

        enriched["ielts_requirement"] = clean(
            research["ielts_requirement"]
        )

        enriched["toefl_requirement"] = clean(
            research["toefl_requirement"]
        )


        verified_at = clean(
            research["verified_at"]
        )

        if not verified_at:
            raise ValueError(
                f"{program_id}: missing verified_at."
            )

        enriched[
            "last_verified_at"
        ] = verified_at


        existing_freshness = clean(
            enriched["freshness_status"]
        )

        requirement_flag = (
            "Requirements Verified"
        )

        if requirement_flag not in existing_freshness:

            if existing_freshness:

                enriched[
                    "freshness_status"
                ] = (
                    f"{existing_freshness}; "
                    f"{requirement_flag}"
                )

            else:

                enriched[
                    "freshness_status"
                ] = requirement_flag


        output_rows.append(
            enriched
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

        writer.writerows(
            output_rows
        )


    print(
        "Input dataset rows              :",
        len(dataset_rows),
    )

    print(
        "Requirements research rows      :",
        len(research_rows),
    )

    print(
        "Output rows                     :",
        len(output_rows),
    )

    print(
        "IELTS values stored             :",
        sum(
            bool(
                clean(
                    row["ielts_requirement"]
                )
            )
            for row in output_rows
        ),
    )

    print(
        "TOEFL values stored             :",
        sum(
            bool(
                clean(
                    row["toefl_requirement"]
                )
            )
            for row in output_rows
        ),
    )

    print(
        "Numeric GPA rows                :",
        sum(
            bool(clean(row["minimum_gpa"]))
            or bool(clean(row["gpa_scale"]))
            for row in output_rows
        ),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )


    print()
    print("=" * 100)

    print(
        "STEP 169.2AV REQUIREMENTS "
        "ENRICHED DATASET BUILD: PASS"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
