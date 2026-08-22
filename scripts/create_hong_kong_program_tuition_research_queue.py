import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_requirements_enriched.csv"
)

OUTPUT_PATH = Path(
    "planning/"
    "17_hong_kong_program_tuition_research_queue.csv"
)

EXPECTED_COUNT = 45

EXPECTED_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(1, 46)
]


QUEUE_HEADERS = [
    "program_id",
    "university_id",
    "program_name",
    "degree_level",
    "program_url",

    "tuition_fee",
    "tuition_currency",
    "tuition_period",

    "tuition_research_status",
    "tuition_applicant_scope",
    "tuition_academic_year",
    "tuition_fee_basis",

    "tuition_source_name",
    "tuition_source_url",
    "tuition_reason",
    "verified_at",
]


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 96)
    print(
        "STEP 169.2AY - CREATE HONG KONG "
        "PROGRAM TUITION RESEARCH QUEUE"
    )
    print("=" * 96)

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_PATH}"
        )

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            "Safety stop: tuition research queue "
            f"already exists: {OUTPUT_PATH}"
        )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)


    print(
        "Input programme rows            :",
        len(rows),
    )


    if len(rows) != EXPECTED_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_COUNT} Hong Kong "
            f"programmes, found {len(rows)}."
        )


    ids = [
        clean(row["program_id"])
        for row in rows
    ]


    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate program_id detected."
        )


    if sorted(ids) != EXPECTED_IDS:
        raise ValueError(
            "Expected exact programme ID range "
            "prog_hk_001 through prog_hk_045."
        )


    output_rows = []


    for row in rows:

        program_id = clean(
            row["program_id"]
        )

        university_id = clean(
            row["university_id"]
        )

        program_name = clean(
            row["program_name"]
        )

        degree_level = clean(
            row["degree_level"]
        )

        program_url = clean(
            row["program_url"]
        )


        if not university_id:
            raise ValueError(
                f"{program_id}: missing university_id."
            )

        if not program_name:
            raise ValueError(
                f"{program_id}: missing program_name."
            )

        if degree_level != "Bachelor":
            raise ValueError(
                f"{program_id}: unexpected degree_level "
                f"{degree_level!r}."
            )

        if not program_url:
            raise ValueError(
                f"{program_id}: missing program_url."
            )


        # Tuition fields MUST still be blank before
        # official-source tuition research begins.
        for field in [
            "tuition_fee",
            "tuition_currency",
            "tuition_period",
        ]:

            if clean(row.get(field)):
                raise ValueError(
                    f"{program_id}: {field} is already "
                    "prefilled. Safety stop."
                )


        output_rows.append(
            {
                "program_id": program_id,
                "university_id": university_id,
                "program_name": program_name,
                "degree_level": degree_level,
                "program_url": program_url,

                # No tuition amount is inferred here.
                "tuition_fee": "",
                "tuition_currency": "",
                "tuition_period": "",

                "tuition_research_status": "PENDING",

                # Must verify whether the published
                # amount applies to international /
                # non-local students.
                "tuition_applicant_scope": "",

                # Example:
                # 2026/27
                "tuition_academic_year": "",

                # Example:
                # Annual tuition
                # Per credit
                # Programme total
                "tuition_fee_basis": "",

                "tuition_source_name": "",
                "tuition_source_url": "",
                "tuition_reason": "",
                "verified_at": "",
            }
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
            fieldnames=QUEUE_HEADERS,
        )

        writer.writeheader()

        writer.writerows(
            output_rows
        )


    print(
        "Queue rows                      :",
        len(output_rows),
    )

    print(
        "PENDING rows                    :",
        sum(
            row["tuition_research_status"]
            == "PENDING"
            for row in output_rows
        ),
    )

    print(
        "Tuition fees prefilled          :",
        sum(
            bool(row["tuition_fee"])
            for row in output_rows
        ),
    )

    print(
        "Applicant scopes prefilled      :",
        sum(
            bool(row["tuition_applicant_scope"])
            for row in output_rows
        ),
    )

    print()
    print(
        "Output:",
        OUTPUT_PATH,
    )

    print()
    print("=" * 96)
    print(
        "STEP 169.2AY TUITION "
        "RESEARCH QUEUE BUILD: PASS"
    )
    print(
        "NO CLEANED DATASET, WORKBOOK OR "
        "MONGODB DATA WAS MODIFIED"
    )
    print("=" * 96)


if __name__ == "__main__":
    main()
