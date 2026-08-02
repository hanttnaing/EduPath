from __future__ import annotations

import json
import math
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
OUTPUT_JSON = OUTPUT_DIRECTORY / "countries.json"

SHEET_NAME = "countries"


# ---------------------------------------------------------
# Expected columns
# ---------------------------------------------------------

EXPECTED_COLUMNS = [
    "country_id",
    "country_name",
    "region",
    "capital_city",
    "currency_code",
    "main_language",
    "estimated_living_cost",
    "cost_currency",
    "source_url",
    "collected_at",
    "last_verified_at",
]


ALLOWED_REGIONS = {
    "East Asia",
    "Southeast Asia",
}


# ---------------------------------------------------------
# General helper functions
# ---------------------------------------------------------

def is_missing(value: Any) -> bool:
    """Return True for blank, None, or NaN values."""

    if value is None:
        return True

    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def clean_required_text(
    value: Any,
    field_name: str,
) -> str:
    """Clean a required text field."""

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
    """Convert optional blank text into None."""

    if is_missing(value):
        return None

    cleaned_value = str(value).strip()

    return cleaned_value if cleaned_value else None


def clean_optional_number(
    value: Any,
    field_name: str,
    minimum: float | None = None,
) -> int | float | None:
    """Convert an optional Excel value into a number."""

    if is_missing(value):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Field '{field_name}' must contain a number."
        ) from error

    if not math.isfinite(number):
        raise ValueError(
            f"Field '{field_name}' must contain a finite number."
        )

    if minimum is not None and number < minimum:
        raise ValueError(
            f"Field '{field_name}' must be at least {minimum}."
        )

    if number.is_integer():
        return int(number)

    return number


def clean_required_date(
    value: Any,
    field_name: str,
) -> str:
    """Convert an Excel date into YYYY-MM-DD."""

    if is_missing(value):
        raise ValueError(
            f"Required date field '{field_name}' cannot be blank."
        )

    parsed_date = pd.to_datetime(
        value,
        errors="coerce",
    )

    if pd.isna(parsed_date):
        raise ValueError(
            f"Field '{field_name}' contains an invalid date."
        )

    return parsed_date.strftime("%Y-%m-%d")


def clean_language_array(value: Any) -> list[str]:
    """
    Convert comma-separated languages into an array.

    Example:
    English, Malay

    becomes:
    ["English", "Malay"]
    """

    cleaned_text = clean_required_text(
        value,
        "main_language",
    )

    languages = [
        language.strip()
        for language in cleaned_text.split(",")
        if language.strip()
    ]

    if not languages:
        raise ValueError(
            "Field 'main_language' must contain "
            "at least one language."
        )

    # Remove duplicate values while keeping their order.
    return list(dict.fromkeys(languages))


def validate_url(
    value: Any,
    field_name: str,
) -> str:
    """Validate an HTTP or HTTPS URL."""

    url = clean_required_text(
        value,
        field_name,
    )

    parsed_url = urlparse(url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError(
            f"Field '{field_name}' must begin with "
            "http:// or https://."
        )

    if not parsed_url.netloc:
        raise ValueError(
            f"Field '{field_name}' must contain a valid domain."
        )

    return url


def validate_currency_code(
    value: Any,
    field_name: str,
) -> str:
    """Validate a three-letter currency code."""

    currency_code = clean_required_text(
        value,
        field_name,
    ).upper()

    if len(currency_code) != 3:
        raise ValueError(
            f"Field '{field_name}' must contain "
            "a three-letter currency code."
        )

    if not currency_code.isalpha():
        raise ValueError(
            f"Field '{field_name}' must contain letters only."
        )

    return currency_code


# ---------------------------------------------------------
# Country transformation
# ---------------------------------------------------------

def transform_country(
    raw_record: dict[str, Any],
    row_number: int,
) -> dict[str, Any]:
    """Clean and validate one country record."""

    try:
        region = clean_required_text(
            raw_record.get("region"),
            "region",
        )

        if region not in ALLOWED_REGIONS:
            raise ValueError(
                "Field 'region' must be one of: "
                + ", ".join(sorted(ALLOWED_REGIONS))
            )

        estimated_living_cost = clean_optional_number(
            raw_record.get("estimated_living_cost"),
            "estimated_living_cost",
            minimum=0,
        )

        cost_currency = clean_optional_text(
            raw_record.get("cost_currency")
        )

        if cost_currency is not None:
            cost_currency = cost_currency.upper()

            if (
                len(cost_currency) != 3
                or not cost_currency.isalpha()
            ):
                raise ValueError(
                    "Field 'cost_currency' must contain "
                    "a three-letter currency code."
                )

        # Living cost and its currency must appear together.
        if (
            estimated_living_cost is not None
            and cost_currency is None
        ):
            raise ValueError(
                "Field 'cost_currency' is required when "
                "estimated_living_cost is provided."
            )

        if (
            estimated_living_cost is None
            and cost_currency is not None
        ):
            raise ValueError(
                "Field 'estimated_living_cost' is required "
                "when cost_currency is provided."
            )

        cleaned_record = {
            "country_id": clean_required_text(
                raw_record.get("country_id"),
                "country_id",
            ),
            "country_name": clean_required_text(
                raw_record.get("country_name"),
                "country_name",
            ),
            "region": region,
            "capital_city": clean_required_text(
                raw_record.get("capital_city"),
                "capital_city",
            ),
            "currency_code": validate_currency_code(
                raw_record.get("currency_code"),
                "currency_code",
            ),
            "main_language": clean_language_array(
                raw_record.get("main_language")
            ),
            "estimated_living_cost": (
                estimated_living_cost
            ),
            "cost_currency": cost_currency,
            "source_url": validate_url(
                raw_record.get("source_url"),
                "source_url",
            ),
            "collected_at": clean_required_date(
                raw_record.get("collected_at"),
                "collected_at",
            ),
            "last_verified_at": clean_required_date(
                raw_record.get("last_verified_at"),
                "last_verified_at",
            ),
        }

        return cleaned_record

    except ValueError as error:
        raise ValueError(
            f"Excel row {row_number}: {error}"
        ) from error


# ---------------------------------------------------------
# Dataset-level validation
# ---------------------------------------------------------

def validate_expected_columns(
    dataframe: pd.DataFrame,
) -> None:
    """Check whether all required columns exist."""

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required country columns are missing "
            "or misspelled:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )


def validate_unique_country_ids(
    records: list[dict[str, Any]],
) -> None:
    """Reject duplicate country_id values."""

    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()

    for record in records:
        country_id = record["country_id"]

        if country_id in seen_ids:
            duplicate_ids.add(country_id)

        seen_ids.add(country_id)

    if duplicate_ids:
        raise ValueError(
            "Duplicate country_id values found:\n"
            + "\n".join(
                f"- {country_id}"
                for country_id in sorted(duplicate_ids)
            )
        )


def validate_unique_country_names(
    records: list[dict[str, Any]],
) -> None:
    """Reject duplicated country names."""

    seen_names: set[str] = set()
    duplicate_names: set[str] = set()

    for record in records:
        normalised_name = (
            record["country_name"]
            .strip()
            .lower()
        )

        if normalised_name in seen_names:
            duplicate_names.add(
                record["country_name"]
            )

        seen_names.add(normalised_name)

    if duplicate_names:
        raise ValueError(
            "Duplicate country names found:\n"
            + "\n".join(
                f"- {country_name}"
                for country_name in sorted(duplicate_names)
            )
        )


# ---------------------------------------------------------
# Main programme
# ---------------------------------------------------------

def main() -> None:
    """Read countries from Excel and create cleaned JSON."""

    print("=" * 60)
    print("EduPath Country ETL")
    print("=" * 60)

    if not INPUT_WORKBOOK.exists():
        raise FileNotFoundError(
            "The prototype workbook was not found.\n"
            f"Expected location: {INPUT_WORKBOOK}"
        )

    print(f"Input workbook: {INPUT_WORKBOOK}")
    print(f"Input sheet: {SHEET_NAME}")

    countries_df = pd.read_excel(
        INPUT_WORKBOOK,
        sheet_name=SHEET_NAME,
        engine="openpyxl",
    )

    if countries_df.empty:
        raise ValueError(
            f"The '{SHEET_NAME}' sheet contains no records."
        )

    validate_expected_columns(countries_df)

    raw_records = countries_df.to_dict(
        orient="records"
    )

    cleaned_records: list[dict[str, Any]] = []

    # Excel row 1 contains the headers.
    # The first data record is Excel row 2.
    for row_number, raw_record in enumerate(
        raw_records,
        start=2,
    ):
        cleaned_record = transform_country(
            raw_record=raw_record,
            row_number=row_number,
        )

        cleaned_records.append(cleaned_record)

    validate_unique_country_ids(cleaned_records)
    validate_unique_country_names(cleaned_records)

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
    print(f"Output JSON: {OUTPUT_JSON}")

    print("\nCleaned countries")
    print("-" * 60)

    print(
        json.dumps(
            cleaned_records,
            ensure_ascii=False,
            indent=2,
        )
    )

    print("\nCountry ETL completed successfully.")


if __name__ == "__main__":
    main()