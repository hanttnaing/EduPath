import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/japan_programs_master_ready.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/japan_programs_fields_enriched.csv"
)


FIELD_MAPPING = {
    "prog_jp_001": "Computer Science",
    "prog_jp_002": "Mathematics & Mathematical Informatics",
    "prog_jp_003": "Information Science & Informatics",

    "prog_jp_004": "Artificial Intelligence & Intelligent Systems",
    "prog_jp_005": "Networks & Communications",
    "prog_jp_006": "Data Science",

    "prog_jp_007": "Computer Science",
    "prog_jp_008": "Networks & Communications",
    "prog_jp_009": "Media & Design",

    "prog_jp_010": "Mathematics & Mathematical Informatics",
    "prog_jp_011": "Information Science & Informatics",
    "prog_jp_012": "Information Science & Informatics",

    "prog_jp_013": "Mathematics & Mathematical Informatics",
    "prog_jp_014": "Software & Systems Engineering",
    "prog_jp_015": "Artificial Intelligence & Intelligent Systems",

    "prog_jp_016": "Information Science & Informatics",
    "prog_jp_017": "Electrical & Electronic Engineering",
    "prog_jp_018": "Media & Design",

    "prog_jp_019": "Computer Science",
    "prog_jp_020": "Networks & Communications",
    "prog_jp_021": "Software & Systems Engineering",

    "prog_jp_022": "Computer Science",
    "prog_jp_023": "Mathematics & Mathematical Informatics",
    "prog_jp_024": "Artificial Intelligence & Intelligent Systems",

    "prog_jp_025": "Computer Science",
    "prog_jp_026": "Artificial Intelligence & Intelligent Systems",
    "prog_jp_027": "Information Science & Informatics",

    "prog_jp_028": "Software & Systems Engineering",
    "prog_jp_029": "Information Science & Informatics",
    "prog_jp_030": "Information Science & Informatics",

    "prog_jp_031": "Mathematics & Mathematical Informatics",
    "prog_jp_032": "Networks & Communications",
    "prog_jp_033": "Media & Design",

    "prog_jp_034": "Interdisciplinary Science & Engineering",
    "prog_jp_035": "Interdisciplinary Science & Engineering",
    "prog_jp_036": "Interdisciplinary Science & Engineering",
}


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        fieldnames = reader.fieldnames

        if fieldnames is None:
            raise ValueError(
                "Input CSV has no headers."
            )

        rows = list(reader)

    print(
        f"Input program records: {len(rows)}"
    )

    if len(rows) != 36:
        raise ValueError(
            "Expected exactly 36 "
            "Japan program records."
        )

    missing_mapping_ids = []

    for row in rows:
        program_id = row[
            "program_id"
        ].strip()

        field_of_study = FIELD_MAPPING.get(
            program_id
        )

        if field_of_study is None:
            missing_mapping_ids.append(
                program_id
            )
            continue

        row[
            "field_of_study"
        ] = field_of_study

    if missing_mapping_ids:
        raise ValueError(
            "Missing field mapping for: "
            + ", ".join(
                missing_mapping_ids
            )
        )

    blank_fields = [
        row["program_id"]
        for row in rows
        if not row[
            "field_of_study"
        ].strip()
    ]

    if blank_fields:
        raise ValueError(
            "Blank field_of_study found for: "
            + ", ".join(blank_fields)
        )

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
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    category_counts = {}

    for row in rows:
        category = row[
            "field_of_study"
        ]

        category_counts[category] = (
            category_counts.get(
                category,
                0,
            )
            + 1
        )

    print()
    print(
        "=== Japan Program Field "
        "Enrichment Complete ==="
    )

    print(
        f"Programs enriched: "
        f"{len(rows)}"
    )

    print(
        f"Field categories: "
        f"{len(category_counts)}"
    )

    print()

    for category, count in sorted(
        category_counts.items()
    ):
        print(
            f"{category}: {count}"
        )

    print()
    print(
        f"Output: {OUTPUT_PATH}"
    )

    print(
        "Verification: "
        "field_of_study is complete "
        "for all 36 records."
    )


if __name__ == "__main__":
    main()