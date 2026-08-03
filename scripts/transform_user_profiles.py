from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

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

COUNTRIES_JSON = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "countries.json"
)

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "cleaned"

OUTPUT_JSON = (
    OUTPUT_DIRECTORY
    / "user_profiles.json"
)

SHEET_NAME = "user_profiles"


# ---------------------------------------------------------
# Expected Excel columns
# ---------------------------------------------------------

EXPECTED_COLUMNS = [
    "user_id",
    "nationality",
    "current_education_level",
    "target_degree_level",
    "preferred_major",
    "gpa",
    "gpa_scale",
    "ielts_score",
    "toefl_score",
    "annual_budget",
    "budget_currency",
    "preferred_countries",
    "scholarship_required",
    "preferred_funding_type",
    "preferred_intake",
    "saved_universities",
    "saved_scholarships",
    "recommendation_history",
]


# ---------------------------------------------------------
# Allowed standard values
# ---------------------------------------------------------

ALLOWED_EDUCATION_LEVELS = {
    "High School",
    "Foundation",
    "Diploma",
    "Bachelor",
    "Master",
    "PhD",
}

ALLOWED_TARGET_DEGREE_LEVELS = {
    "Foundation",
    "Diploma",
    "Bachelor",
    "Master",
    "PhD",
}

ALLOWED_FUNDING_TYPES = {
    "Fully Funded",
    "Partially Funded",
    "Tuition Only",
    "Allowance Only",
    "Any",
}


# ---------------------------------------------------------
# General cleaning functions
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
    """Clean a required text value."""

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
    maximum: float | None = None,
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

    if maximum is not None and number > maximum:
        raise ValueError(
            f"Field '{field_name}' must not exceed {maximum}."
        )

    if number.is_integer():
        return int(number)

    return number


def clean_optional_integer(
    value: Any,
    field_name: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int | None:
    """Convert an optional Excel value into a whole number."""

    number = clean_optional_number(
        value=value,
        field_name=field_name,
        minimum=minimum,
        maximum=maximum,
    )

    if number is None:
        return None

    if isinstance(number, float):
        raise ValueError(
            f"Field '{field_name}' must be a whole number."
        )

    return number


def clean_boolean(
    value: Any,
    field_name: str,
) -> bool:
    """Convert Excel TRUE/FALSE values into Python Boolean."""

    if is_missing(value):
        raise ValueError(
            f"Required field '{field_name}' cannot be blank."
        )

    normalised_value = str(value).strip().lower()

    true_values = {
        "true",
        "1",
        "yes",
        "y",
    }

    false_values = {
        "false",
        "0",
        "no",
        "n",
    }

    if normalised_value in true_values:
        return True

    if normalised_value in false_values:
        return False

    raise ValueError(
        f"Field '{field_name}' must contain TRUE or FALSE."
    )


def clean_optional_array(
    value: Any,
) -> list[str]:
    """
    Convert comma-separated text into a list.

    Blank cells become an empty list.
    """

    if is_missing(value):
        return []

    items = [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]

    # Remove duplicate values while preserving order.
    return list(dict.fromkeys(items))


def clean_required_array(
    value: Any,
    field_name: str,
) -> list[str]:
    """Convert required comma-separated text into a list."""

    items = clean_optional_array(value)

    if not items:
        raise ValueError(
            f"Field '{field_name}' must contain "
            "at least one value."
        )

    return items


def validate_currency_code(
    value: Any,
    field_name: str,
) -> str:
    """Validate a three-letter currency code."""

    currency_code = clean_required_text(
        value,
        field_name,
    ).upper()

    if (
        len(currency_code) != 3
        or not currency_code.isalpha()
    ):
        raise ValueError(
            f"Field '{field_name}' must contain "
            "a three-letter currency code."
        )

    return currency_code


# ---------------------------------------------------------
# Reference data
# ---------------------------------------------------------

def load_valid_country_names() -> set[str]:
    """Read all country names from countries.json."""

    if not COUNTRIES_JSON.exists():
        raise FileNotFoundError(
            "The cleaned countries JSON file was not found.\n"
            f"Expected location: {COUNTRIES_JSON}"
        )

    with COUNTRIES_JSON.open(
        mode="r",
        encoding="utf-8",
    ) as input_file:
        country_records = json.load(input_file)

    if not isinstance(country_records, list):
        raise ValueError(
            "countries.json must contain a list of records."
        )

    country_names = {
        str(record["country_name"]).strip()
        for record in country_records
        if record.get("country_name")
    }

    if not country_names:
        raise ValueError(
            "No country names were found in countries.json."
        )

    return country_names


# ---------------------------------------------------------
# User-profile transformation
# ---------------------------------------------------------

def transform_user_profile(
    raw_record: dict[str, Any],
    row_number: int,
    valid_country_names: set[str],
) -> dict[str, Any]:
    """Clean and validate one user profile."""

    try:
        current_education_level = clean_required_text(
            raw_record.get("current_education_level"),
            "current_education_level",
        )

        if (
            current_education_level
            not in ALLOWED_EDUCATION_LEVELS
        ):
            raise ValueError(
                "Field 'current_education_level' must be one of: "
                + ", ".join(
                    sorted(ALLOWED_EDUCATION_LEVELS)
                )
            )

        target_degree_level = clean_required_text(
            raw_record.get("target_degree_level"),
            "target_degree_level",
        )

        if (
            target_degree_level
            not in ALLOWED_TARGET_DEGREE_LEVELS
        ):
            raise ValueError(
                "Field 'target_degree_level' must be one of: "
                + ", ".join(
                    sorted(ALLOWED_TARGET_DEGREE_LEVELS)
                )
            )

        gpa = clean_optional_number(
            raw_record.get("gpa"),
            "gpa",
            minimum=0,
        )

        gpa_scale = clean_optional_number(
            raw_record.get("gpa_scale"),
            "gpa_scale",
            minimum=0.1,
        )

        if gpa is not None and gpa_scale is None:
            raise ValueError(
                "Field 'gpa_scale' is required when "
                "gpa is provided."
            )

        if gpa is None and gpa_scale is not None:
            raise ValueError(
                "Field 'gpa' is required when "
                "gpa_scale is provided."
            )

        if (
            gpa is not None
            and gpa_scale is not None
            and gpa > gpa_scale
        ):
            raise ValueError(
                "gpa cannot be greater than gpa_scale."
            )

        annual_budget = clean_optional_number(
            raw_record.get("annual_budget"),
            "annual_budget",
            minimum=0,
        )

        budget_currency_raw = clean_optional_text(
            raw_record.get("budget_currency")
        )

        budget_currency: str | None = None

        if budget_currency_raw is not None:
            budget_currency = validate_currency_code(
                budget_currency_raw,
                "budget_currency",
            )

        if (
            annual_budget is not None
            and budget_currency is None
        ):
            raise ValueError(
                "Field 'budget_currency' is required "
                "when annual_budget is provided."
            )

        if (
            annual_budget is None
            and budget_currency is not None
        ):
            raise ValueError(
                "Field 'annual_budget' is required "
                "when budget_currency is provided."
            )

        preferred_countries = clean_required_array(
            raw_record.get("preferred_countries"),
            "preferred_countries",
        )

        invalid_countries = [
            country_name
            for country_name in preferred_countries
            if country_name not in valid_country_names
        ]

        if invalid_countries:
            raise ValueError(
                "The following preferred countries do not "
                "exist in countries.json: "
                + ", ".join(invalid_countries)
            )

        scholarship_required = clean_boolean(
            raw_record.get("scholarship_required"),
            "scholarship_required",
        )

        preferred_funding_type = clean_optional_text(
            raw_record.get("preferred_funding_type")
        )

        if (
            preferred_funding_type is not None
            and preferred_funding_type
            not in ALLOWED_FUNDING_TYPES
        ):
            raise ValueError(
                "Field 'preferred_funding_type' must be one of: "
                + ", ".join(
                    sorted(ALLOWED_FUNDING_TYPES)
                )
            )

        if (
            scholarship_required
            and preferred_funding_type is None
        ):
            raise ValueError(
                "Field 'preferred_funding_type' is required "
                "when scholarship_required is TRUE."
            )

        cleaned_record = {
            "user_id": clean_required_text(
                raw_record.get("user_id"),
                "user_id",
            ),
            "nationality": clean_required_text(
                raw_record.get("nationality"),
                "nationality",
            ),
            "current_education_level": (
                current_education_level
            ),
            "target_degree_level": target_degree_level,
            "preferred_major": clean_required_text(
                raw_record.get("preferred_major"),
                "preferred_major",
            ),
            "gpa": gpa,
            "gpa_scale": gpa_scale,
            "ielts_score": clean_optional_number(
                raw_record.get("ielts_score"),
                "ielts_score",
                minimum=0,
                maximum=9,
            ),
            "toefl_score": clean_optional_integer(
                raw_record.get("toefl_score"),
                "toefl_score",
                minimum=0,
                maximum=120,
            ),
            "annual_budget": annual_budget,
            "budget_currency": budget_currency,
            "preferred_countries": preferred_countries,
            "scholarship_required": scholarship_required,
            "preferred_funding_type": (
                preferred_funding_type
            ),
            "preferred_intake": clean_optional_text(
                raw_record.get("preferred_intake")
            ),
            "saved_universities": clean_optional_array(
                raw_record.get("saved_universities")
            ),
            "saved_scholarships": clean_optional_array(
                raw_record.get("saved_scholarships")
            ),
            "recommendation_history": clean_optional_array(
                raw_record.get("recommendation_history")
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
    """Check whether all 18 user-profile columns exist."""

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required user-profile columns are missing "
            "or misspelled:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )


def validate_unique_user_ids(
    records: list[dict[str, Any]],
) -> None:
    """Reject duplicate user_id values."""

    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()

    for record in records:
        user_id = record["user_id"]

        if user_id in seen_ids:
            duplicate_ids.add(user_id)

        seen_ids.add(user_id)

    if duplicate_ids:
        raise ValueError(
            "Duplicate user_id values found:\n"
            + "\n".join(
                f"- {user_id}"
                for user_id in sorted(duplicate_ids)
            )
        )


# ---------------------------------------------------------
# Main programme
# ---------------------------------------------------------

def main() -> None:
    """Read user profiles from Excel and create cleaned JSON."""

    print("=" * 60)
    print("EduPath User Profile ETL")
    print("=" * 60)

    if not INPUT_WORKBOOK.exists():
        raise FileNotFoundError(
            "The prototype workbook was not found.\n"
            f"Expected location: {INPUT_WORKBOOK}"
        )

    print(f"Input workbook: {INPUT_WORKBOOK}")
    print(f"Input sheet: {SHEET_NAME}")

    profiles_df = pd.read_excel(
        INPUT_WORKBOOK,
        sheet_name=SHEET_NAME,
        engine="openpyxl",
    )

    if profiles_df.empty:
        raise ValueError(
            f"The '{SHEET_NAME}' sheet contains no records."
        )

    validate_expected_columns(profiles_df)

    valid_country_names = load_valid_country_names()

    print(
        "Valid country names loaded: "
        f"{len(valid_country_names)}"
    )

    raw_records = profiles_df.to_dict(
        orient="records"
    )

    cleaned_records: list[dict[str, Any]] = []

    # Excel row 1 contains headers.
    # The first data record is Excel row 2.
    for row_number, raw_record in enumerate(
        raw_records,
        start=2,
    ):
        cleaned_record = transform_user_profile(
            raw_record=raw_record,
            row_number=row_number,
            valid_country_names=valid_country_names,
        )

        cleaned_records.append(cleaned_record)

    validate_unique_user_ids(cleaned_records)

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

    print("\nFirst cleaned user profile")
    print("-" * 60)

    print(
        json.dumps(
            cleaned_records[0],
            ensure_ascii=False,
            indent=2,
        )
    )

    print(
        "\nUser profile ETL completed successfully."
    )


if __name__ == "__main__":
    main()