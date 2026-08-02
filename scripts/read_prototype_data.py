from pathlib import Path

import pandas as pd


# This script is inside:
# C:\EduPath\scripts\read_prototype_data.py
#
# parents[1] points to:
# C:\EduPath
PROJECT_ROOT = Path(__file__).resolve().parents[1]

WORKBOOK_PATH = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "05_prototype_dataset.xlsx"
)

SHEET_NAME = "universities"

EXPECTED_COLUMNS = [
    "university_id",
    "university_name",
    "country_id",
    "city",
    "university_type",
    "official_website",
    "establishment_year",
    "global_ranking",
    "ranking_source",
    "ranking_year",
    "degree_levels",
    "scholarship_available",
    "source_url",
    "collected_at",
    "last_verified_at",
    "freshness_status",
]


def main() -> None:
    """Read and perform basic checks on the prototype university data."""

    print("=" * 60)
    print("EduPath Prototype Dataset Reader")
    print("=" * 60)

    # Check whether the Excel file exists.
    if not WORKBOOK_PATH.exists():
        raise FileNotFoundError(
            "The prototype workbook could not be found.\n"
            f"Expected location: {WORKBOOK_PATH}"
        )

    print(f"Workbook found: {WORKBOOK_PATH}")
    print(f"Reading sheet: {SHEET_NAME}")

    # Read the universities worksheet.
    universities_df = pd.read_excel(
        WORKBOOK_PATH,
        sheet_name=SHEET_NAME,
        engine="openpyxl",
    )

    # Check whether the sheet contains data.
    if universities_df.empty:
        raise ValueError(
            f"The '{SHEET_NAME}' sheet does not contain any records."
        )

    # Check for missing or incorrectly named columns.
    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in universities_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The following required columns are missing or misspelled:\n"
            + "\n".join(f"- {column}" for column in missing_columns)
        )

    # Convert date columns into pandas date values.
    date_columns = ["collected_at", "last_verified_at"]

    for column in date_columns:
        universities_df[column] = pd.to_datetime(
            universities_df[column],
            errors="coerce",
        )

    print("\nDataset summary")
    print("-" * 60)
    print(f"Number of rows: {len(universities_df)}")
    print(f"Number of columns: {len(universities_df.columns)}")

    print("\nUniversity records")
    print("-" * 60)
    print(universities_df.to_string(index=False))

    print("\nColumn data types")
    print("-" * 60)
    print(universities_df.dtypes)

    print("\nFirst university")
    print("-" * 60)

    first_record = universities_df.iloc[0]

    print(f"University ID: {first_record['university_id']}")
    print(f"University name: {first_record['university_name']}")
    print(f"Country ID: {first_record['country_id']}")
    print(f"City: {first_record['city']}")
    print(
        "Scholarship available: "
        f"{first_record['scholarship_available']}"
    )
    print(
        "Last verified at: "
        f"{first_record['last_verified_at'].date()}"
    )

    print("\nValidation completed successfully.")


if __name__ == "__main__":
    main()
    