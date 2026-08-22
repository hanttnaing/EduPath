import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_language_enriched.csv"
)

OUTPUT_PATH = Path(
    "planning/"
    "16_hong_kong_program_requirements_research_queue.csv"
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
    "minimum_gpa",
    "gpa_scale",
    "ielts_requirement",
    "toefl_requirement",
    "requirements_research_status",
    "gpa_status",
    "english_status",
    "accepted_tests",
    "numeric_minimum_status",
    "requirements_source_name",
    "requirements_source_url",
    "requirements_reason",
    "verified_at",
]


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def main():
    print("=" * 90)
    print(
        "STEP 169.2AR - CREATE HONG KONG "
        "PROGRAM REQUIREMENTS RESEARCH QUEUE"
    )
    print("=" * 90)

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_PATH}"
        )

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            "Safety stop: research queue already exists: "
            f"{OUTPUT_PATH}"
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
            f"Expected exactly {EXPECTED_COUNT} "
            f"Hong Kong programmes, found {len(rows)}."
        )

    ids = [
        clean(row.get("program_id"))
        for row in rows
    ]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate program_id detected."
        )

    if sorted(ids) != EXPECTED_IDS:
        raise ValueError(
            "Expected prog_hk_001 through "
            "prog_hk_045 exactly."
        )

    output_rows = []

    for row in rows:
        program_id = clean(
            row.get("program_id")
        )

        university_id = clean(
            row.get("university_id")
        )

        program_name = clean(
            row.get("program_name")
        )

        degree_level = clean(
            row.get("degree_level")
        )

        program_url = clean(
            row.get("program_url")
        )

        if not university_id:
            raise ValueError(
                f"{program_id}: missing university_id"
            )

        if not program_name:
            raise ValueError(
                f"{program_id}: missing program_name"
            )

        if not program_url:
            raise ValueError(
                f"{program_id}: missing program_url"
            )

        if degree_level != "Bachelor":
            raise ValueError(
                f"{program_id}: unexpected degree_level "
                f"{degree_level!r}"
            )

        output_rows.append(
            {
                "program_id": program_id,
                "university_id": university_id,
                "program_name": program_name,
                "degree_level": degree_level,
                "program_url": program_url,

                # Do not infer numeric requirements.
                "minimum_gpa": "",
                "gpa_scale": "",
                "ielts_requirement": "",
                "toefl_requirement": "",

                # Research closure metadata.
                "requirements_research_status": "PENDING",
                "gpa_status": "",
                "english_status": "",
                "accepted_tests": "",
                "numeric_minimum_status": "",
                "requirements_source_name": "",
                "requirements_source_url": "",
                "requirements_reason": "",
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
            row["requirements_research_status"]
            == "PENDING"
            for row in output_rows
        ),
    )

    print(
        "Numeric GPA prefilled           :",
        sum(
            bool(row["minimum_gpa"])
            for row in output_rows
        ),
    )

    print(
        "IELTS prefilled                 :",
        sum(
            bool(row["ielts_requirement"])
            for row in output_rows
        ),
    )

    print(
        "TOEFL prefilled                 :",
        sum(
            bool(row["toefl_requirement"])
            for row in output_rows
        ),
    )

    print()
    print(
        "Output:",
        OUTPUT_PATH,
    )

    print()
    print("=" * 90)
    print(
        "STEP 169.2AR REQUIREMENTS "
        "RESEARCH QUEUE BUILD: PASS"
    )
    print(
        "NO WORKBOOK OR MONGODB DATA WAS MODIFIED"
    )
    print("=" * 90)


if __name__ == "__main__":
    main()
