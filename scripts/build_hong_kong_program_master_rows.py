import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/raw/"
    "hong_kong_program_international_research_queue.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_master_ready.csv"
)

EXPECTED_PROGRAM_COUNT = 45

EXPECTED_PROGRAM_IDS = [
    f"prog_hk_{number:03d}"
    for number in range(1, 46)
]

PROGRAM_HEADERS = [
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


def clean(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def main() -> None:
    print("=" * 80)
    print(
        "STEP 169.2D - BUILD HONG KONG "
        "PROGRAMME MASTER ROWS"
    )
    print("=" * 80)
    print()

    # -----------------------------------------------------
    # 1. Safety checks
    # -----------------------------------------------------

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input research queue not found: {INPUT_PATH}"
        )

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            "Safety stop: output file already exists: "
            f"{OUTPUT_PATH}"
        )

    # -----------------------------------------------------
    # 2. Read verified Hong Kong research queue
    # -----------------------------------------------------

    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        research_rows = list(reader)

    print(
        "Research queue rows              :",
        len(research_rows),
    )

    if len(research_rows) != EXPECTED_PROGRAM_COUNT:
        raise ValueError(
            "Expected exactly "
            f"{EXPECTED_PROGRAM_COUNT} research rows, "
            f"found {len(research_rows)}."
        )

    # -----------------------------------------------------
    # 3. Validate reserved IDs
    # -----------------------------------------------------

    program_ids = [
        clean(row.get("program_id"))
        for row in research_rows
    ]

    if len(program_ids) != len(set(program_ids)):
        raise ValueError(
            "Duplicate program_id detected "
            "in Hong Kong research queue."
        )

    if sorted(program_ids) != sorted(EXPECTED_PROGRAM_IDS):
        raise ValueError(
            "Hong Kong program_id range does not match "
            "prog_hk_001 through prog_hk_045."
        )

    # -----------------------------------------------------
    # 4. Validate research closure state
    # -----------------------------------------------------

    identity_verified = 0

    for row in research_rows:
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

        identity_status = clean(
            row.get("programme_identity_status")
        )

        verified_at = clean(
            row.get("last_verified_at")
        )

        if not university_id:
            raise ValueError(
                f"{program_id} is missing university_id."
            )

        if not program_name:
            raise ValueError(
                f"{program_id} is missing program_name."
            )

        if degree_level != "Bachelor":
            raise ValueError(
                f"{program_id} has unexpected degree_level: "
                f"{degree_level}"
            )

        if not program_url:
            raise ValueError(
                f"{program_id} is missing program_url."
            )

        if identity_status != "VERIFIED":
            raise ValueError(
                f"{program_id} programme identity "
                "is not VERIFIED."
            )

        if not verified_at:
            raise ValueError(
                f"{program_id} is missing "
                "last_verified_at research metadata."
            )

        identity_verified += 1

    print(
        "Identity VERIFIED               :",
        identity_verified,
    )

    # -----------------------------------------------------
    # 5. Build exact 21-column master rows
    # -----------------------------------------------------

    output_rows = []

    for research in research_rows:
        program_id = clean(
            research.get("program_id")
        )

        university_id = clean(
            research.get("university_id")
        )

        program_name = clean(
            research.get("program_name")
        )

        degree_level = clean(
            research.get("degree_level")
        )

        program_url = clean(
            research.get("program_url")
        )

        research_verified_at = clean(
            research.get("last_verified_at")
        )

        output_rows.append(
            {
                # Preserved verified identity
                "program_id": program_id,
                "university_id": university_id,
                "program_name": program_name,

                # Enriched in later official-source steps
                "field_of_study": "",

                "degree_level": degree_level,

                # Recommendation-critical details remain
                # blank until separately verified.
                "duration_years": "",
                "study_mode": "",
                "language_of_instruction": "",
                "tuition_fee": "",
                "tuition_currency": "",
                "tuition_period": "",
                "minimum_gpa": "",
                "gpa_scale": "",
                "ielts_requirement": "",
                "toefl_requirement": "",
                "intake": "",
                "application_deadline": "",

                # Official programme identity source
                "program_url": program_url,

                # Research verification date acts as
                # the collection date for this master row.
                "collected_at": research_verified_at,

                # Full programme-detail verification
                # will happen during enrichment.
                "last_verified_at": "",

                # Temporary pre-enrichment state.
                "freshness_status":
                    "Pending Detail Verification",
            }
        )

    # -----------------------------------------------------
    # 6. Final in-memory integrity checks
    # -----------------------------------------------------

    if len(output_rows) != EXPECTED_PROGRAM_COUNT:
        raise ValueError(
            "Master row count changed unexpectedly."
        )

    output_ids = [
        row["program_id"]
        for row in output_rows
    ]

    if output_ids != program_ids:
        raise ValueError(
            "Program ID order changed during build."
        )

    if len(output_ids) != len(set(output_ids)):
        raise ValueError(
            "Duplicate program_id detected "
            "in generated master rows."
        )

    for row in output_rows:
        if list(row.keys()) != PROGRAM_HEADERS:
            raise ValueError(
                "Generated master row does not match "
                "the exact 21-column contract."
            )

    # -----------------------------------------------------
    # 7. Write new master CSV
    # -----------------------------------------------------

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
            fieldnames=PROGRAM_HEADERS,
        )

        writer.writeheader()
        writer.writerows(output_rows)

    # -----------------------------------------------------
    # 8. Read-back audit
    # -----------------------------------------------------

    with OUTPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        written_headers = reader.fieldnames
        written_rows = list(reader)

    written_ids = [
        clean(row.get("program_id"))
        for row in written_rows
    ]

    blank_names = sum(
        not clean(row.get("program_name"))
        for row in written_rows
    )

    blank_urls = sum(
        not clean(row.get("program_url"))
        for row in written_rows
    )

    non_bachelor = sum(
        clean(row.get("degree_level"))
        != "Bachelor"
        for row in written_rows
    )

    id_range_correct = (
        sorted(written_ids)
        == sorted(EXPECTED_PROGRAM_IDS)
    )

    print()
    print("MASTER BUILD RESULT")
    print("-" * 80)

    print(
        "Output rows                     :",
        len(written_rows),
    )

    print(
        "Output columns                  :",
        len(written_headers or []),
    )

    print(
        "Exact header contract           :",
        written_headers == PROGRAM_HEADERS,
    )

    print(
        "Full HK ID range correct        :",
        id_range_correct,
    )

    print(
        "Duplicate programme IDs         :",
        len(written_ids) - len(set(written_ids)),
    )

    print(
        "Blank programme names           :",
        blank_names,
    )

    print(
        "Blank programme URLs            :",
        blank_urls,
    )

    print(
        "Non-Bachelor rows               :",
        non_bachelor,
    )

    print(
        "Pending detail verification rows:",
        sum(
            clean(
                row.get("freshness_status")
            )
            == "Pending Detail Verification"
            for row in written_rows
        ),
    )

    pass_build = (
        len(written_rows) == 45
        and len(written_headers or []) == 21
        and written_headers == PROGRAM_HEADERS
        and id_range_correct
        and len(written_ids) == len(set(written_ids))
        and blank_names == 0
        and blank_urls == 0
        and non_bachelor == 0
    )

    print()

    if pass_build:
        print("=" * 80)
        print(
            "STEP 169.2D HONG KONG PROGRAMME "
            "MASTER BUILD: PASS"
        )
        print(
            "45 / 45 VERIFIED PROGRAMME "
            "IDENTITIES PRESERVED"
        )
        print(
            "prog_hk_001 -> prog_hk_045 "
            "PRESERVED WITHOUT RE-GENERATION"
        )
        print(
            "21-COLUMN PROGRAMME MASTER "
            "CONTRACT PRESERVED"
        )
        print(
            "READY FOR OFFICIAL-SOURCE "
            "DETAIL ENRICHMENT"
        )
        print("=" * 80)
    else:
        print("=" * 80)
        print(
            "STEP 169.2D HONG KONG PROGRAMME "
            "MASTER BUILD: FAIL"
        )
        print(
            "REVIEW THE OUTPUT BEFORE CONTINUING"
        )
        print("=" * 80)

    print()
    print(
        "Output:",
        OUTPUT_PATH,
    )
    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )


if __name__ == "__main__":
    main()
