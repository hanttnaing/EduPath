from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_WORKBOOK = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "05_prototype_dataset.xlsx"
)

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "cleaned"

OUTPUT_JSON = OUTPUT_DIRECTORY / "universities.json"

SHEET_NAME = "universities"


# ---------------------------------------------------------
# Validation rules
# ---------------------------------------------------------

REQUIRED_FIELDS = [
    "university_id",
    "university_name",
    "country_id",
    "city",
    "university_type",
    "official_website",
    "degree_levels",
    "scholarship_available",
    "source_url",
    "collected_at",
    "last_verified_at",
    "freshness_status",
]

ALLOWED_UNIVERSITY_TYPES = {
    "Public",
    "Private",
    "Autonomous",
    "Other",
    "Unknown",
}

ALLOWED_DEGREE_LEVELS = {
    "Foundation",
    "Diploma",
    "Bachelor",
    "Master",
    "PhD",
}

ALLOWED_FRESHNESS_STATUSES = {
    "current",
    "stale",
    "unknown",
}


# ---------------------------------------------------------
# Cleaning helper functions
# ---------------------------------------------------------

def is_missing(value: Any) -> bool:
    """Return True when a value is blank, NaN, or missing."""

    if value is None:
        return True

    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def clean_required_text(value: Any, field_name: str) -> str:
    """Clean a required text field and reject blank values."""

    if is_missing(value):
        raise ValueError(
            f"Required field '{field_name}' cannot be blank."
        )

    cleaned_value = str(value).strip()

    if not cleaned_value:
        raise ValueError(
            f"Required field '{field_name}' cannot be blank."
        )

    return cleaned_value


def clean_optional_text(value: Any) -> str | None:
    """Convert blank optional text values into None."""

    if is_missing(value):
        return None

    cleaned_value = str(value).strip()

    return cleaned_value if cleaned_value else None


def clean_optional_integer(
    value: Any,
    field_name: str,
) -> int | None:
    """Convert an optional Excel number into a Python integer."""

    if is_missing(value):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Field '{field_name}' must be a number."
        ) from error

    if not number.is_integer():
        raise ValueError(
            f"Field '{field_name}' must be a whole number."
        )

    return int(number)


def clean_boolean(value: Any, field_name: str) -> bool:
    """Convert Excel Boolean or text into a Python Boolean."""

    if isinstance(value, bool):
        return value

    if is_missing(value):
        raise ValueError(
            f"Required Boolean field '{field_name}' cannot be blank."
        )

    normalised_value = str(value).strip().lower()

    true_values = {"true", "yes", "1"}
    false_values = {"false", "no", "0"}

    if normalised_value in true_values:
        return True

    if normalised_value in false_values:
        return False

    raise ValueError(
        f"Field '{field_name}' must contain TRUE or FALSE."
    )


def clean_date(value: Any, field_name: str) -> str:
    """Convert an Excel date into YYYY-MM-DD text."""

    if is_missing(value):
        raise ValueError(
            f"Required date field '{field_name}' cannot be blank."
        )

    parsed_date = pd.to_datetime(value, errors="coerce")

    if pd.isna(parsed_date):
        raise ValueError(
            f"Field '{field_name}' contains an invalid date."
        )

    return parsed_date.strftime("%Y-%m-%d")


def clean_array(value: Any, field_name: str) -> list[str]:
    """
    Convert comma-separated Excel text into a clean Python list.

    Example:
    Bachelor, Master, PhD

    becomes:
    ["Bachelor", "Master", "PhD"]
    """

    if is_missing(value):
        raise ValueError(
            f"Required array field '{field_name}' cannot be blank."
        )

    items = [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]

    if not items:
        raise ValueError(
            f"Field '{field_name}' must contain at least one value."
        )

    # Remove duplicates while preserving the original order.
    return list(dict.fromkeys(items))


def validate_url(value: Any, field_name: str) -> str:
    """Validate and return an HTTP or HTTPS URL."""

    url = clean_required_text(value, field_name)

    parsed_url = urlparse(url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError(
            f"Field '{field_name}' must begin with http:// or https://"
        )

    if not parsed_url.netloc:
        raise ValueError(
            f"Field '{field_name}' must contain a valid domain."
        )

    return url


# ---------------------------------------------------------
# University transformation
# ---------------------------------------------------------

def transform_university(
    raw_record: dict[str, Any],
    row_number: int,
) -> dict[str, Any]:
    """Clean and validate one university record."""

    try:
        university_type = clean_required_text(
            raw_record.get("university_type"),
            "university_type",
        )

        if university_type not in ALLOWED_UNIVERSITY_TYPES:
            raise ValueError(
                "Field 'university_type' must be one of: "
                + ", ".join(sorted(ALLOWED_UNIVERSITY_TYPES))
            )

        degree_levels = clean_array(
            raw_record.get("degree_levels"),
            "degree_levels",
        )

        invalid_degree_levels = [
            level
            for level in degree_levels
            if level not in ALLOWED_DEGREE_LEVELS
        ]

        if invalid_degree_levels:
            raise ValueError(
                "Invalid degree level value(s): "
                + ", ".join(invalid_degree_levels)
            )

        freshness_status = clean_required_text(
            raw_record.get("freshness_status"),
            "freshness_status",
        ).lower()

        if freshness_status not in ALLOWED_FRESHNESS_STATUSES:
            raise ValueError(
                "Field 'freshness_status' must be one of: "
                + ", ".join(sorted(ALLOWED_FRESHNESS_STATUSES))
            )

        cleaned_record = {
            "university_id": clean_required_text(
                raw_record.get("university_id"),
                "university_id",
            ),
            "university_name": clean_required_text(
                raw_record.get("university_name"),
                "university_name",
            ),
            "country_id": clean_required_text(
                raw_record.get("country_id"),
                "country_id",
            ),
            "city": clean_required_text(
                raw_record.get("city"),
                "city",
            ),
            "university_type": university_type,
            "official_website": validate_url(
                raw_record.get("official_website"),
                "official_website",
            ),
            "establishment_year": clean_optional_integer(
                raw_record.get("establishment_year"),
                "establishment_year",
            ),
            "global_ranking": clean_optional_integer(
                raw_record.get("global_ranking"),
                "global_ranking",
            ),
            "ranking_source": clean_optional_text(
                raw_record.get("ranking_source")
            ),
            "ranking_year": clean_optional_integer(
                raw_record.get("ranking_year"),
                "ranking_year",
            ),
            "degree_levels": degree_levels,
            "scholarship_available": clean_boolean(
                raw_record.get("scholarship_available"),
                "scholarship_available",
            ),
            "source_url": validate_url(
                raw_record.get("source_url"),
                "source_url",
            ),
            "collected_at": clean_date(
                raw_record.get("collected_at"),
                "collected_at",
            ),
            "last_verified_at": clean_date(
                raw_record.get("last_verified_at"),
                "last_verified_at",
            ),
            "freshness_status": freshness_status,
        }

        return cleaned_record

    except ValueError as error:
        raise ValueError(
            f"Excel row {row_number}: {error}"
        ) from error


# ---------------------------------------------------------
# Dataset-level validation
# ---------------------------------------------------------

def validate_required_columns(
    dataframe: pd.DataFrame,
) -> None:
    """Check whether all required columns exist."""

    missing_columns = [
        column
        for column in REQUIRED_FIELDS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required columns are missing or misspelled:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )


def validate_unique_ids(
    records: list[dict[str, Any]],
) -> None:
    """Reject duplicate university IDs."""

    university_ids = [
        record["university_id"]
        for record in records
    ]

    duplicate_ids = sorted(
        {
            university_id
            for university_id in university_ids
            if university_ids.count(university_id) > 1
        }
    )

    if duplicate_ids:
        raise ValueError(
            "Duplicate university_id values found:\n"
            + "\n".join(
                f"- {university_id}"
                for university_id in duplicate_ids
            )
        )


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------

def main() -> None:
    """Read Excel, clean the records, and create JSON output."""

    print("=" * 60)
    print("EduPath University ETL")
    print("=" * 60)

    if not INPUT_WORKBOOK.exists():
        raise FileNotFoundError(
            "Input workbook was not found.\n"
            f"Expected location: {INPUT_WORKBOOK}"
        )

    print(f"Input file: {INPUT_WORKBOOK}")
    print(f"Input sheet: {SHEET_NAME}")

    universities_df = pd.read_excel(
        INPUT_WORKBOOK,
        sheet_name=SHEET_NAME,
        engine="openpyxl",
    )

    if universities_df.empty:
        raise ValueError(
            f"The '{SHEET_NAME}' sheet has no records."
        )

    validate_required_columns(universities_df)

    raw_records = universities_df.to_dict(orient="records")

    cleaned_records: list[dict[str, Any]] = []

    # Excel row 1 contains headings, so the first data row is row 2.
    for index, raw_record in enumerate(raw_records, start=2):
        cleaned_record = transform_university(
            raw_record=raw_record,
            row_number=index,
        )

        cleaned_records.append(cleaned_record)

    validate_unique_ids(cleaned_records)

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_JSON.open(
        mode="w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            cleaned_records,
            output_file,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    print("\nETL summary")
    print("-" * 60)
    print(f"Records read: {len(raw_records)}")
    print(f"Records cleaned: {len(cleaned_records)}")
    print("Validation errors: 0")
    print(f"Output file: {OUTPUT_JSON}")

    print("\nFirst cleaned record")
    print("-" * 60)
    print(
        json.dumps(
            cleaned_records[0],
            ensure_ascii=False,
            indent=2,
        )
    )

    print("\nETL completed successfully.")


if __name__ == "__main__":
    main()
    