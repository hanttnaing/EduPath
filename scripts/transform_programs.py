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

UNIVERSITIES_JSON = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "universities.json"
)

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "cleaned"

OUTPUT_JSON = OUTPUT_DIRECTORY / "programs.json"

SHEET_NAME = "programs"


# ---------------------------------------------------------
# Expected Excel columns
# ---------------------------------------------------------

EXPECTED_COLUMNS = [
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


# ---------------------------------------------------------
# Allowed standard values
# ---------------------------------------------------------

ALLOWED_DEGREE_LEVELS = {
    "Foundation",
    "Diploma",
    "Bachelor",
    "Master",
    "PhD",
}

ALLOWED_STUDY_MODES = {
    "Full-time",
    "Part-time",
    "Online",
    "Hybrid",
}

ALLOWED_TUITION_PERIODS = {
    "Annual",
    "Semester",
    "Total",
}

ALLOWED_FRESHNESS_STATUSES = {
    "current",
    "stale",
    "unknown",
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
    """Clean text that must not be blank."""

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
    """Convert an optional Excel value into a valid number."""

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
    """Convert an optional value into a whole number."""

    cleaned_number = clean_optional_number(
        value=value,
        field_name=field_name,
        minimum=minimum,
        maximum=maximum,
    )

    if cleaned_number is None:
        return None

    if isinstance(cleaned_number, float):
        raise ValueError(
            f"Field '{field_name}' must be a whole number."
        )

    return cleaned_number


def clean_required_date(
    value: Any,
    field_name: str,
) -> str:
    """Convert a required Excel date into YYYY-MM-DD."""

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


def clean_optional_date(
    value: Any,
    field_name: str,
) -> str | None:
    """Convert an optional Excel date into YYYY-MM-DD."""

    if is_missing(value):
        return None

    parsed_date = pd.to_datetime(
        value,
        errors="coerce",
    )

    if pd.isna(parsed_date):
        raise ValueError(
            f"Field '{field_name}' contains an invalid date."
        )

    return parsed_date.strftime("%Y-%m-%d")


def clean_optional_array(value: Any) -> list[str] | None:
    """
    Convert comma-separated text into a list.

    Example:
    April, October

    becomes:
    ["April", "October"]
    """

    if is_missing(value):
        return None

    items = [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]

    if not items:
        return None

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(items))


def validate_url(
    value: Any,
    field_name: str,
) -> str:
    """Validate an HTTP or HTTPS URL."""

    url = clean_required_text(value, field_name)

    parsed_url = urlparse(url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError(
            f"Field '{field_name}' must begin with "
            "http:// or https://"
        )

    if not parsed_url.netloc:
        raise ValueError(
            f"Field '{field_name}' must contain a valid domain."
        )

    return url


# ---------------------------------------------------------
# Relationship validation
# ---------------------------------------------------------

def load_valid_university_ids() -> set[str]:
    """
    Read universities.json and return all valid university IDs.

    This prevents a programme from referring to a university
    that does not exist in the cleaned university dataset.
    """

    if not UNIVERSITIES_JSON.exists():
        raise FileNotFoundError(
            "The cleaned universities JSON file was not found.\n"
            f"Expected location: {UNIVERSITIES_JSON}"
        )

    with UNIVERSITIES_JSON.open(
        mode="r",
        encoding="utf-8",
    ) as input_file:
        university_records = json.load(input_file)

    if not isinstance(university_records, list):
        raise ValueError(
            "universities.json must contain a list of records."
        )

    university_ids = {
        str(record.get("university_id")).strip()
        for record in university_records
        if record.get("university_id")
    }

    if not university_ids:
        raise ValueError(
            "No university IDs were found in universities.json."
        )

    return university_ids


# ---------------------------------------------------------
# Programme transformation
# ---------------------------------------------------------

def transform_program(
    raw_record: dict[str, Any],
    row_number: int,
    valid_university_ids: set[str],
) -> dict[str, Any]:
    """Clean and validate one programme record."""

    try:
        program_id = clean_required_text(
            raw_record.get("program_id"),
            "program_id",
        )

        university_id = clean_required_text(
            raw_record.get("university_id"),
            "university_id",
        )

        if university_id not in valid_university_ids:
            raise ValueError(
                f"University ID '{university_id}' does not exist "
                "in universities.json."
            )

        degree_level = clean_required_text(
            raw_record.get("degree_level"),
            "degree_level",
        )

        if degree_level not in ALLOWED_DEGREE_LEVELS:
            raise ValueError(
                "Field 'degree_level' must be one of: "
                + ", ".join(sorted(ALLOWED_DEGREE_LEVELS))
            )

        study_mode = clean_optional_text(
            raw_record.get("study_mode")
        )

        if (
            study_mode is not None
            and study_mode not in ALLOWED_STUDY_MODES
        ):
            raise ValueError(
                "Field 'study_mode' must be one of: "
                + ", ".join(sorted(ALLOWED_STUDY_MODES))
            )

        tuition_fee = clean_optional_number(
            raw_record.get("tuition_fee"),
            "tuition_fee",
            minimum=0,
        )

        tuition_currency = clean_optional_text(
            raw_record.get("tuition_currency")
        )

        tuition_period = clean_optional_text(
            raw_record.get("tuition_period")
        )

        if (
            tuition_period is not None
            and tuition_period not in ALLOWED_TUITION_PERIODS
        ):
            raise ValueError(
                "Field 'tuition_period' must be one of: "
                + ", ".join(sorted(ALLOWED_TUITION_PERIODS))
            )

        # Logical consistency for tuition information.
        if tuition_fee is not None:
            if tuition_currency is None:
                raise ValueError(
                    "Field 'tuition_currency' is required "
                    "when tuition_fee is provided."
                )

            if tuition_period is None:
                raise ValueError(
                    "Field 'tuition_period' is required "
                    "when tuition_fee is provided."
                )

        minimum_gpa = clean_optional_number(
            raw_record.get("minimum_gpa"),
            "minimum_gpa",
            minimum=0,
        )

        gpa_scale = clean_optional_number(
            raw_record.get("gpa_scale"),
            "gpa_scale",
            minimum=0,
        )

        # GPA and GPA scale should appear together.
        if minimum_gpa is not None and gpa_scale is None:
            raise ValueError(
                "Field 'gpa_scale' is required when "
                "minimum_gpa is provided."
            )

        if minimum_gpa is None and gpa_scale is not None:
            raise ValueError(
                "Field 'minimum_gpa' is required when "
                "gpa_scale is provided."
            )

        if (
            minimum_gpa is not None
            and gpa_scale is not None
            and minimum_gpa > gpa_scale
        ):
            raise ValueError(
                "minimum_gpa cannot be greater than gpa_scale."
            )

        freshness_status = clean_required_text(
            raw_record.get("freshness_status"),
            "freshness_status",
        ).lower()

        if freshness_status not in ALLOWED_FRESHNESS_STATUSES:
            raise ValueError(
                "Field 'freshness_status' must be one of: "
                + ", ".join(
                    sorted(ALLOWED_FRESHNESS_STATUSES)
                )
            )

        cleaned_record = {
            "program_id": program_id,
            "university_id": university_id,
            "program_name": clean_required_text(
                raw_record.get("program_name"),
                "program_name",
            ),
            "field_of_study": clean_required_text(
                raw_record.get("field_of_study"),
                "field_of_study",
            ),
            "degree_level": degree_level,
            "duration_years": clean_optional_number(
                raw_record.get("duration_years"),
                "duration_years",
                minimum=0.1,
            ),
            "study_mode": study_mode,
            "language_of_instruction": clean_required_text(
                raw_record.get("language_of_instruction"),
                "language_of_instruction",
            ),
            "tuition_fee": tuition_fee,
            "tuition_currency": tuition_currency,
            "tuition_period": tuition_period,
            "minimum_gpa": minimum_gpa,
            "gpa_scale": gpa_scale,
            "ielts_requirement": clean_optional_number(
                raw_record.get("ielts_requirement"),
                "ielts_requirement",
                minimum=0,
                maximum=9,
            ),
            "toefl_requirement": clean_optional_integer(
                raw_record.get("toefl_requirement"),
                "toefl_requirement",
                minimum=0,
                maximum=120,
            ),
            "intake": clean_optional_array(
                raw_record.get("intake")
            ),
            "application_deadline": clean_optional_date(
                raw_record.get("application_deadline"),
                "application_deadline",
            ),
            "program_url": validate_url(
                raw_record.get("program_url"),
                "program_url",
            ),
            "collected_at": clean_required_date(
                raw_record.get("collected_at"),
                "collected_at",
            ),
            "last_verified_at": clean_required_date(
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

def validate_expected_columns(
    dataframe: pd.DataFrame,
) -> None:
    """Check whether all 21 programme columns exist."""

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required programme columns are missing "
            "or misspelled:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )


def validate_unique_program_ids(
    records: list[dict[str, Any]],
) -> None:
    """Reject duplicate program_id values."""

    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()

    for record in records:
        program_id = record["program_id"]

        if program_id in seen_ids:
            duplicate_ids.add(program_id)

        seen_ids.add(program_id)

    if duplicate_ids:
        raise ValueError(
            "Duplicate program_id values found:\n"
            + "\n".join(
                f"- {program_id}"
                for program_id in sorted(duplicate_ids)
            )
        )


def validate_unique_program_signatures(
    records: list[dict[str, Any]],
) -> None:
    """
    Detect logically duplicated programmes.

    Signature:
    university_id + program_name + degree_level + intake
    """

    seen_signatures: set[tuple[Any, ...]] = set()
    duplicate_programs: list[str] = []

    for record in records:
        intake_values = tuple(
            sorted(record.get("intake") or [])
        )

        signature = (
            record["university_id"],
            record["program_name"].strip().lower(),
            record["degree_level"],
            intake_values,
        )

        if signature in seen_signatures:
            duplicate_programs.append(
                record["program_id"]
            )

        seen_signatures.add(signature)

    if duplicate_programs:
        raise ValueError(
            "Logically duplicated programme records found:\n"
            + "\n".join(
                f"- {program_id}"
                for program_id in duplicate_programs
            )
        )


# ---------------------------------------------------------
# Main programme
# ---------------------------------------------------------

def main() -> None:
    """Read programmes from Excel and create cleaned JSON."""

    print("=" * 60)
    print("EduPath Programme ETL")
    print("=" * 60)

    if not INPUT_WORKBOOK.exists():
        raise FileNotFoundError(
            "The prototype workbook was not found.\n"
            f"Expected location: {INPUT_WORKBOOK}"
        )

    print(f"Input workbook: {INPUT_WORKBOOK}")
    print(f"Input sheet: {SHEET_NAME}")

    programs_df = pd.read_excel(
        INPUT_WORKBOOK,
        sheet_name=SHEET_NAME,
        engine="openpyxl",
    )

    if programs_df.empty:
        raise ValueError(
            f"The '{SHEET_NAME}' sheet contains no records."
        )

    validate_expected_columns(programs_df)

    valid_university_ids = load_valid_university_ids()

    print(
        "Valid university IDs loaded: "
        f"{len(valid_university_ids)}"
    )

    raw_records = programs_df.to_dict(
        orient="records"
    )

    cleaned_records: list[dict[str, Any]] = []

    # Excel row 1 contains headers.
    # The first data record is Excel row 2.
    for row_number, raw_record in enumerate(
        raw_records,
        start=2,
    ):
        cleaned_record = transform_program(
            raw_record=raw_record,
            row_number=row_number,
            valid_university_ids=valid_university_ids,
        )

        cleaned_records.append(cleaned_record)

    validate_unique_program_ids(cleaned_records)
    validate_unique_program_signatures(cleaned_records)

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

    print("\nFirst cleaned programme")
    print("-" * 60)
    print(
        json.dumps(
            cleaned_records[0],
            ensure_ascii=False,
            indent=2,
        )
    )

    print("\nProgramme ETL completed successfully.")


if __name__ == "__main__":
    main()