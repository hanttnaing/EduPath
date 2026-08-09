import csv
from datetime import datetime, timezone
from pathlib import Path


INPUT_PATH = Path(
    "data/raw/japan_program_seed.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/japan_programs_master_ready.csv"
)


EXPECTED_UNIVERSITY_COUNT = 12
EXPECTED_PROGRAM_COUNT = 36


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


def main() -> None:
    # ---------------------------------
    # 1. Check input file
    # ---------------------------------

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    # ---------------------------------
    # 2. Read Japan program seed
    # ---------------------------------

    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        seed_rows = list(reader)

    print(
        f"Seed program records: "
        f"{len(seed_rows)}"
    )

    if len(seed_rows) != EXPECTED_PROGRAM_COUNT:
        raise ValueError(
            "Expected exactly "
            f"{EXPECTED_PROGRAM_COUNT} "
            "Japan program records."
        )

    # ---------------------------------
    # 3. Validate universities
    # ---------------------------------

    university_ids = {
        row["university_id"].strip()
        for row in seed_rows
        if row.get("university_id")
    }

    if (
        len(university_ids)
        != EXPECTED_UNIVERSITY_COUNT
    ):
        raise ValueError(
            "Expected exactly "
            f"{EXPECTED_UNIVERSITY_COUNT} "
            "unique universities."
        )

    # ---------------------------------
    # 4. Validate university slots
    # ---------------------------------

    university_slots = {}

    for row in seed_rows:
        university_id = row[
            "university_id"
        ].strip()

        slot = row[
            "program_slot"
        ].strip()

        university_slots.setdefault(
            university_id,
            set(),
        ).add(slot)

    for university_id, slots in (
        university_slots.items()
    ):
        expected_slots = {
            "1",
            "2",
            "3",
        }

        if slots != expected_slots:
            raise ValueError(
                f"{university_id} has "
                f"invalid program slots: "
                f"{sorted(slots)}"
            )

    # ---------------------------------
    # 5. Build 21-column rows
    # ---------------------------------

    collected_at = datetime.now(
        timezone.utc
    ).date().isoformat()

    output_rows = []

    for sequence, seed in enumerate(
        seed_rows,
        start=1,
    ):
        program_name = seed.get(
            "program_name",
            "",
        ).strip()

        degree_level = seed.get(
            "degree_level_hint",
            "",
        ).strip()

        program_url = seed.get(
            "official_source_url",
            "",
        ).strip()

        university_id = seed.get(
            "university_id",
            "",
        ).strip()

        if not university_id:
            raise ValueError(
                "A program record is missing "
                "university_id."
            )

        if not program_name:
            raise ValueError(
                "A program record is missing "
                "program_name."
            )

        if not degree_level:
            raise ValueError(
                f"{program_name} is missing "
                "degree_level_hint."
            )

        if not program_url:
            raise ValueError(
                f"{program_name} is missing "
                "official_source_url."
            )

        program_id = (
            f"prog_jp_{sequence:03d}"
        )

        output_rows.append(
            {
                "program_id": program_id,
                "university_id": university_id,
                "program_name": program_name,

                # Will be enriched later
                "field_of_study": "",

                "degree_level": degree_level,

                # Recommendation-critical
                # fields remain blank until
                # official verification.
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

                "program_url": program_url,
                "collected_at": collected_at,

                # Identity verified,
                # details still pending.
                "last_verified_at": "",
                "freshness_status": (
                    "Pending Detail Verification"
                ),
            }
        )

    # ---------------------------------
    # 6. Check duplicate program IDs
    # ---------------------------------

    program_ids = [
        row["program_id"]
        for row in output_rows
    ]

    if (
        len(program_ids)
        != len(set(program_ids))
    ):
        raise ValueError(
            "Duplicate program_id detected."
        )

    # ---------------------------------
    # 7. Save CSV
    # ---------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=PROGRAM_HEADERS,
        )

        writer.writeheader()
        writer.writerows(
            output_rows
        )

    # ---------------------------------
    # 8. Summary
    # ---------------------------------

    degree_counts = {}

    for row in output_rows:
        degree = row[
            "degree_level"
        ]

        degree_counts[degree] = (
            degree_counts.get(
                degree,
                0,
            )
            + 1
        )

    print()
    print(
        "=== Japan Program Master "
        "Rows Created ==="
    )

    print(
        f"Universities: "
        f"{len(university_ids)}"
    )

    print(
        f"Programs: "
        f"{len(output_rows)}"
    )

    for degree, count in sorted(
        degree_counts.items()
    ):
        print(
            f"{degree}: {count}"
        )

    print(
        f"Columns: "
        f"{len(PROGRAM_HEADERS)}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()