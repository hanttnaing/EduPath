import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_tuition_enriched.csv"
)

OUTPUT_PATH = Path(
    "planning/"
    "18_hong_kong_program_intake_deadline_research_queue.csv"
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

    "intake",
    "application_deadline",

    "schedule_research_status",

    "applicant_scope",
    "admission_route",
    "academic_year",
    "schedule_type",

    "schedule_source_name",
    "schedule_source_url",
    "schedule_evidence",
    "storage_reason",
    "verified_at",
]


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 100)
    print(
        "STEP 169.2BH - CREATE HONG KONG "
        "INTAKE + DEADLINE RESEARCH QUEUE"
    )
    print("=" * 100)

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
            "Expected exact ID range "
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
                f"{program_id}: unexpected degree level "
                f"{degree_level!r}."
            )

        if not program_url:
            raise ValueError(
                f"{program_id}: missing program_url."
            )

        # Safety:
        # current master intake/deadline must still
        # be blank before research begins.
        if clean(row.get("intake")):
            raise ValueError(
                f"{program_id}: intake is unexpectedly "
                "prefilled."
            )

        if clean(
            row.get("application_deadline")
        ):
            raise ValueError(
                f"{program_id}: application_deadline "
                "is unexpectedly prefilled."
            )

        output_rows.append(
            {
                "program_id": program_id,
                "university_id": university_id,
                "program_name": program_name,
                "degree_level": degree_level,
                "program_url": program_url,

                # Never infer schedule values.
                "intake": "",
                "application_deadline": "",

                "schedule_research_status": "PENDING",

                # Evidence context.
                "applicant_scope": "",
                "admission_route": "",
                "academic_year": "",
                "schedule_type": "",

                "schedule_source_name": "",
                "schedule_source_url": "",
                "schedule_evidence": "",
                "storage_reason": "",
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
            row["schedule_research_status"]
            == "PENDING"
            for row in output_rows
        ),
    )

    print(
        "Intake values prefilled         :",
        sum(
            bool(row["intake"])
            for row in output_rows
        ),
    )

    print(
        "Deadline values prefilled       :",
        sum(
            bool(row["application_deadline"])
            for row in output_rows
        ),
    )

    print()
    print(
        "Output:",
        OUTPUT_PATH,
    )

    print()
    print("=" * 100)

    print(
        "STEP 169.2BH INTAKE + DEADLINE "
        "RESEARCH QUEUE BUILD: PASS"
    )

    print(
        "NO CLEANED DATASET, WORKBOOK OR "
        "MONGODB DATA WAS MODIFIED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
