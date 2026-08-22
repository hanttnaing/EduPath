import csv
from pathlib import Path


INPUT_DATASET = Path(
    "data/cleaned/"
    "hong_kong_programs_requirements_enriched.csv"
)

TUITION_QUEUE = Path(
    "planning/"
    "17_hong_kong_program_tuition_research_queue.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_tuition_enriched.csv"
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
        "STEP 169.2BE - BUILD HONG KONG "
        "TUITION-ENRICHED DATASET"
    )
    print("=" * 100)

    if not INPUT_DATASET.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_DATASET}"
        )

    if not TUITION_QUEUE.exists():
        raise FileNotFoundError(
            f"Tuition queue not found: {TUITION_QUEUE}"
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
            "Input does not match exact "
            "21-column programme schema."
        )


    with TUITION_QUEUE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        tuition_rows = list(
            csv.DictReader(file)
        )


    if len(dataset_rows) != 45:
        raise ValueError(
            "Expected 45 input programme rows."
        )

    if len(tuition_rows) != 45:
        raise ValueError(
            "Expected 45 tuition research rows."
        )


    tuition_by_id = {
        clean(row["program_id"]): row
        for row in tuition_rows
    }


    output_rows = []


    for source_row in dataset_rows:

        program_id = clean(
            source_row["program_id"]
        )

        if program_id not in tuition_by_id:
            raise ValueError(
                f"{program_id}: missing tuition research."
            )


        research = tuition_by_id[
            program_id
        ]


        if clean(
            research["university_id"]
        ) != clean(
            source_row["university_id"]
        ):
            raise ValueError(
                f"{program_id}: university mismatch."
            )


        status = clean(
            research[
                "tuition_research_status"
            ]
        )


        if status not in {
            "VERIFIED",
            "REVIEWED_UNRESOLVED",
        }:
            raise ValueError(
                f"{program_id}: tuition research "
                f"not closed: {status!r}"
            )


        output = source_row.copy()


        if status == "VERIFIED":

            fee = clean(
                research["tuition_fee"]
            )

            currency = clean(
                research["tuition_currency"]
            )

            period = clean(
                research["tuition_period"]
            )


            if (
                not fee
                or currency != "HKD"
                or period != "Annual"
            ):
                raise ValueError(
                    f"{program_id}: VERIFIED tuition "
                    "is incomplete."
                )


            output["tuition_fee"] = fee
            output["tuition_currency"] = currency
            output["tuition_period"] = period

            tuition_flag = (
                "Tuition Verified"
            )


        else:

            # Preserve unknown master tuition rather
            # than inventing or mis-normalising it.
            if (
                clean(research["tuition_fee"])
                or clean(
                    research["tuition_currency"]
                )
                or clean(
                    research["tuition_period"]
                )
            ):
                raise ValueError(
                    f"{program_id}: unresolved tuition "
                    "contains unsupported master values."
                )


            output["tuition_fee"] = ""
            output["tuition_currency"] = ""
            output["tuition_period"] = ""

            tuition_flag = (
                "Tuition Reviewed Unresolved"
            )


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


        existing_freshness = clean(
            output["freshness_status"]
        )


        if tuition_flag not in existing_freshness:

            if existing_freshness:

                output[
                    "freshness_status"
                ] = (
                    f"{existing_freshness}; "
                    f"{tuition_flag}"
                )

            else:

                output[
                    "freshness_status"
                ] = tuition_flag


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

        writer.writerows(
            output_rows
        )


    numeric_rows = sum(
        bool(clean(row["tuition_fee"]))
        for row in output_rows
    )

    blank_rows = sum(
        not clean(row["tuition_fee"])
        for row in output_rows
    )


    print(
        "Input programme rows            :",
        len(dataset_rows),
    )

    print(
        "Tuition research rows           :",
        len(tuition_rows),
    )

    print(
        "Output rows                     :",
        len(output_rows),
    )

    print(
        "Numeric tuition rows            :",
        numeric_rows,
    )

    print(
        "Evidence-closed blank tuition   :",
        blank_rows,
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )


    if numeric_rows != 35:
        raise ValueError(
            "Expected 35 numeric tuition rows."
        )

    if blank_rows != 10:
        raise ValueError(
            "Expected 10 evidence-closed "
            "blank tuition rows."
        )


    print()
    print("=" * 100)

    print(
        "STEP 169.2BE TUITION-ENRICHED "
        "DATASET BUILD: PASS"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
