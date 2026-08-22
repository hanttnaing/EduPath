import csv
from collections import Counter
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_master_ready.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "hong_kong_programs_fields_enriched.csv"
)

EXPECTED_COUNT = 45

EXPECTED_IDS = [
    f"prog_hk_{i:03d}"
    for i in range(1, 46)
]

FIELD_MAPPING = {
    "prog_hk_001": "Data Science",
    "prog_hk_002": "Business & Management",
    "prog_hk_003": "General Science",

    "prog_hk_004": "Computer Science",
    "prog_hk_005": "Business & Management",
    "prog_hk_006": "Data Science",

    "prog_hk_007": "Computer Engineering",
    "prog_hk_008": "Biomedical & Health Sciences",
    "prog_hk_009": "Economics",

    "prog_hk_010":
        "Artificial Intelligence & Intelligent Systems",
    "prog_hk_011": "Data Science",
    "prog_hk_012": "Business & Management",

    "prog_hk_013": "Computer Science",
    "prog_hk_014": "Data Science",
    "prog_hk_015": "Business & Management",

    "prog_hk_016":
        "Business Analytics & Information Systems",
    "prog_hk_017": "Business & Management",
    "prog_hk_018": "Communication & Media",

    "prog_hk_019": "Data Science",
    "prog_hk_020":
        "International Relations & Public Policy",
    "prog_hk_021": "Data Science",

    "prog_hk_022":
        "Artificial Intelligence & Intelligent Systems",
    "prog_hk_023": "Communication & Media",
    "prog_hk_024": "Psychology",

    "prog_hk_025": "Computer Science",
    "prog_hk_026": "Business & Management",
    "prog_hk_027": "Finance & Financial Technology",

    "prog_hk_028": "Data Science",
    "prog_hk_029": "Finance & Financial Technology",
    "prog_hk_030": "Psychology",

    "prog_hk_031": "Computer Science",
    "prog_hk_032": "Data Science",
    "prog_hk_033":
        "Business Analytics & Information Systems",

    "prog_hk_034": "Computer Science",
    "prog_hk_035": "Finance & Financial Technology",
    "prog_hk_036": "Communication & Media",

    "prog_hk_037": "Business & Management",
    "prog_hk_038": "Languages & Translation",
    "prog_hk_039":
        "Artificial Intelligence & Intelligent Systems",

    "prog_hk_040": "Media & Design",
    "prog_hk_041": "Information Science & Informatics",
    "prog_hk_042": "Fashion & Design",

    "prog_hk_043": "Psychology",
    "prog_hk_044":
        "Sustainability & Social Sciences",
    "prog_hk_045": "Biomedical & Health Sciences",
}


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def main():
    print("=" * 80)
    print(
        "STEP 169.2M - HONG KONG "
        "FIELD-OF-STUDY ENRICHMENT BUILD"
    )
    print("=" * 80)
    print()

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
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
        fieldnames = reader.fieldnames
        rows = list(reader)

    if fieldnames is None:
        raise ValueError(
            "Input CSV has no headers."
        )

    if len(rows) != EXPECTED_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_COUNT} rows, "
            f"found {len(rows)}."
        )

    ids = [
        clean(row.get("program_id"))
        for row in rows
    ]

    if sorted(ids) != sorted(EXPECTED_IDS):
        raise ValueError(
            "Program ID range does not match "
            "prog_hk_001 through prog_hk_045."
        )

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate program_id detected."
        )

    if sorted(FIELD_MAPPING) != sorted(EXPECTED_IDS):
        raise ValueError(
            "FIELD_MAPPING does not cover "
            "exactly prog_hk_001 through prog_hk_045."
        )

    # Safety: this stage expects the master file
    # to still have blank field_of_study values.
    prefilled = [
        row["program_id"]
        for row in rows
        if clean(row.get("field_of_study"))
    ]

    if prefilled:
        raise ValueError(
            "Safety stop: field_of_study is already "
            "populated for: "
            + ", ".join(prefilled)
        )

    for row in rows:
        program_id = clean(
            row.get("program_id")
        )

        row["field_of_study"] = (
            FIELD_MAPPING[program_id]
        )

    blank_fields = [
        row["program_id"]
        for row in rows
        if not clean(
            row.get("field_of_study")
        )
    ]

    if blank_fields:
        raise ValueError(
            "Blank field_of_study remains for: "
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
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    # Read-back audit
    with OUTPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        written_headers = reader.fieldnames
        written_rows = list(reader)

    category_counts = Counter(
        clean(row.get("field_of_study"))
        for row in written_rows
    )

    written_ids = [
        clean(row.get("program_id"))
        for row in written_rows
    ]

    blank_after_write = sum(
        not clean(row.get("field_of_study"))
        for row in written_rows
    )

    print("BUILD RESULT")
    print("-" * 80)
    print(
        "Input rows                      :",
        len(rows),
    )
    print(
        "Output rows                     :",
        len(written_rows),
    )
    print(
        "Output columns                  :",
        len(written_headers or []),
    )
    print(
        "Full HK ID range correct        :",
        sorted(written_ids)
        == sorted(EXPECTED_IDS),
    )
    print(
        "Duplicate programme IDs         :",
        len(written_ids)
        - len(set(written_ids)),
    )
    print(
        "Blank field_of_study values     :",
        blank_after_write,
    )
    print(
        "Distinct normalized fields      :",
        len(category_counts),
    )
    print()

    print("NORMALIZED FIELD DISTRIBUTION")
    print("-" * 80)

    for category, count in sorted(
        category_counts.items()
    ):
        print(
            f"{category}: {count}"
        )

    pass_build = (
        len(written_rows) == 45
        and len(written_headers or []) == 21
        and sorted(written_ids)
        == sorted(EXPECTED_IDS)
        and len(written_ids)
        == len(set(written_ids))
        and blank_after_write == 0
        and len(category_counts) == 18
    )

    print()

    if pass_build:
        print("=" * 80)
        print(
            "STEP 169.2M HONG KONG "
            "FIELD ENRICHMENT BUILD: PASS"
        )
        print(
            "45 / 45 PROGRAMMES HAVE "
            "NORMALIZED FIELD_OF_STUDY"
        )
        print(
            "18 NORMALIZED FIELD CATEGORIES "
            "PRESERVED"
        )
        print(
            "MASTER INPUT FILE WAS NOT "
            "OVERWRITTEN"
        )
        print(
            "READY FOR STEP 169.2N "
            "FIELD ENRICHMENT PARITY AUDIT"
        )
        print("=" * 80)

    else:
        print("=" * 80)
        print(
            "STEP 169.2M HONG KONG "
            "FIELD ENRICHMENT BUILD: FAIL"
        )
        print(
            "DO NOT CONTINUE TO DURATION/"
            "STUDY MODE YET"
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
