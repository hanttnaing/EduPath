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

COUNTRIES_JSON = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "countries.json"
)

UNIVERSITIES_JSON = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "universities.json"
)

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "cleaned"

OUTPUT_JSON = (
    OUTPUT_DIRECTORY
    / "scholarships.json"
)

SHEET_NAME = "scholarships"


# ---------------------------------------------------------
# Expected Excel columns
# ---------------------------------------------------------

EXPECTED_COLUMNS = [
    "scholarship_id",
    "scholarship_name",
    "provider_name",
    "provider_type",
    "country_id",
    "host_university_id",
    "eligible_nationalities",
    "degree_levels",
    "fields_of_study",
    "minimum_gpa",
    "gpa_scale",
    "ielts_requirement",
    "toefl_requirement",
    "age_limit",
    "funding_type",
    "tuition_coverage",
    "monthly_allowance",
    "allowance_currency",
    "travel_allowance",
    "accommodation_support",
    "health_insurance",
    "required_documents",
    "application_opening_date",
    "application_deadline",
    "scholarship_status",
    "application_cycle",
    "official_website",
    "source_url",
    "collected_at",
    "last_verified_at",
    "freshness_status",
    "data_quality_status",
]


# ---------------------------------------------------------
# Allowed standard values
# ---------------------------------------------------------

ALLOWED_PROVIDER_TYPES = {
    "Government",
    "University",
    "Private",
    "Foundation",
    "International Organization",
    "Other",
}

ALLOWED_DEGREE_LEVELS = {
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
    "Self-Funded",
}

ALLOWED_SCHOLARSHIP_STATUSES = {
    "upcoming",
    "open",
    "closed",
    "unknown",
}

ALLOWED_FRESHNESS_STATUSES = {
    "current",
    "stale",
    "unknown",
}

ALLOWED_DATA_QUALITY_STATUSES = {
    "verified",
    "partial",
    "unverified",
}


# ---------------------------------------------------------
# General cleaning helpers
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


def clean_optional_array(
    value: Any,
) -> list[str] | None:
    """Convert comma-separated Excel text into a list."""

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

    if (
        len(currency_code) != 3
        or not currency_code.isalpha()
    ):
        raise ValueError(
            f"Field '{field_name}' must contain "
            "a three-letter currency code."
        )

    return currency_code


def clean_application_cycle(value: Any) -> str:
    """Convert the scholarship cycle into clean text."""

    if is_missing(value):
        raise ValueError(
            "Required field 'application_cycle' cannot be blank."
        )

    # Excel may read 2027 as an integer or as 2027.0.
    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    cleaned_value = str(value).strip()

    if not cleaned_value:
        raise ValueError(
            "Required field 'application_cycle' cannot be blank."
        )

    return cleaned_value


# ---------------------------------------------------------
# Reference-data loading
# ---------------------------------------------------------

def load_json_list(
    file_path: Path,
    dataset_name: str,
) -> list[dict[str, Any]]:
    """Load a required JSON reference dataset."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"The cleaned {dataset_name} JSON file was not found.\n"
            f"Expected location: {file_path}"
        )

    with file_path.open(
        mode="r",
        encoding="utf-8",
    ) as input_file:
        records = json.load(input_file)

    if not isinstance(records, list):
        raise ValueError(
            f"{file_path.name} must contain a list of records."
        )

    if not records:
        raise ValueError(
            f"{file_path.name} contains no records."
        )

    return records


def load_country_ids() -> set[str]:
    """Return valid country IDs from countries.json."""

    records = load_json_list(
        COUNTRIES_JSON,
        "countries",
    )

    return {
        str(record["country_id"]).strip()
        for record in records
        if record.get("country_id")
    }


def load_university_country_map() -> dict[str, str]:
    """
    Return university_id -> country_id relationships.

    This lets the script verify that a host university
    belongs to the scholarship country.
    """

    records = load_json_list(
        UNIVERSITIES_JSON,
        "universities",
    )

    return {
        str(record["university_id"]).strip():
        str(record["country_id"]).strip()
        for record in records
        if (
            record.get("university_id")
            and record.get("country_id")
        )
    }


# ---------------------------------------------------------
# Scholarship transformation
# ---------------------------------------------------------

def transform_scholarship(
    raw_record: dict[str, Any],
    row_number: int,
    valid_country_ids: set[str],
    university_country_map: dict[str, str],
) -> dict[str, Any]:
    """Clean and validate one scholarship record."""

    try:
        country_id = clean_required_text(
            raw_record.get("country_id"),
            "country_id",
        )

        if country_id not in valid_country_ids:
            raise ValueError(
                f"Country ID '{country_id}' does not exist "
                "in countries.json."
            )

        host_university_id = clean_optional_text(
            raw_record.get("host_university_id")
        )

        if host_university_id is not None:
            if host_university_id not in university_country_map:
                raise ValueError(
                    f"Host university ID "
                    f"'{host_university_id}' does not exist "
                    "in universities.json."
                )

            university_country_id = (
                university_country_map[host_university_id]
            )

            if university_country_id != country_id:
                raise ValueError(
                    f"Host university '{host_university_id}' "
                    f"belongs to '{university_country_id}', "
                    f"not '{country_id}'."
                )

        provider_type = clean_required_text(
            raw_record.get("provider_type"),
            "provider_type",
        )

        if provider_type not in ALLOWED_PROVIDER_TYPES:
            raise ValueError(
                "Field 'provider_type' must be one of: "
                + ", ".join(sorted(ALLOWED_PROVIDER_TYPES))
            )

        degree_levels = clean_required_array(
            raw_record.get("degree_levels"),
            "degree_levels",
        )

        invalid_degree_levels = [
            degree_level
            for degree_level in degree_levels
            if degree_level not in ALLOWED_DEGREE_LEVELS
        ]

        if invalid_degree_levels:
            raise ValueError(
                "Invalid degree level values: "
                + ", ".join(invalid_degree_levels)
            )

        funding_type = clean_required_text(
            raw_record.get("funding_type"),
            "funding_type",
        )

        if funding_type not in ALLOWED_FUNDING_TYPES:
            raise ValueError(
                "Field 'funding_type' must be one of: "
                + ", ".join(sorted(ALLOWED_FUNDING_TYPES))
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

        monthly_allowance = clean_optional_number(
            raw_record.get("monthly_allowance"),
            "monthly_allowance",
            minimum=0,
        )

        allowance_currency_raw = clean_optional_text(
            raw_record.get("allowance_currency")
        )

        allowance_currency: str | None = None

        if allowance_currency_raw is not None:
            allowance_currency = validate_currency_code(
                allowance_currency_raw,
                "allowance_currency",
            )

        if (
            monthly_allowance is not None
            and allowance_currency is None
        ):
            raise ValueError(
                "Field 'allowance_currency' is required "
                "when monthly_allowance is provided."
            )

        if (
            monthly_allowance is None
            and allowance_currency is not None
        ):
            raise ValueError(
                "Field 'monthly_allowance' is required "
                "when allowance_currency is provided."
            )

        opening_date = clean_optional_date(
            raw_record.get("application_opening_date"),
            "application_opening_date",
        )

        deadline = clean_optional_date(
            raw_record.get("application_deadline"),
            "application_deadline",
        )

        if (
            opening_date is not None
            and deadline is not None
            and deadline < opening_date
        ):
            raise ValueError(
                "application_deadline cannot be earlier "
                "than application_opening_date."
            )

        scholarship_status = clean_required_text(
            raw_record.get("scholarship_status"),
            "scholarship_status",
        ).lower()

        if (
            scholarship_status
            not in ALLOWED_SCHOLARSHIP_STATUSES
        ):
            raise ValueError(
                "Field 'scholarship_status' must be one of: "
                + ", ".join(
                    sorted(ALLOWED_SCHOLARSHIP_STATUSES)
                )
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

        data_quality_status = clean_required_text(
            raw_record.get("data_quality_status"),
            "data_quality_status",
        ).lower()

        if (
            data_quality_status
            not in ALLOWED_DATA_QUALITY_STATUSES
        ):
            raise ValueError(
                "Field 'data_quality_status' must be one of: "
                + ", ".join(
                    sorted(ALLOWED_DATA_QUALITY_STATUSES)
                )
            )

        collected_at = clean_required_date(
            raw_record.get("collected_at"),
            "collected_at",
        )

        last_verified_at = clean_required_date(
            raw_record.get("last_verified_at"),
            "last_verified_at",
        )

        if last_verified_at < collected_at:
            raise ValueError(
                "last_verified_at cannot be earlier "
                "than collected_at."
            )

        cleaned_record = {
            "scholarship_id": clean_required_text(
                raw_record.get("scholarship_id"),
                "scholarship_id",
            ),
            "scholarship_name": clean_required_text(
                raw_record.get("scholarship_name"),
                "scholarship_name",
            ),
            "provider_name": clean_required_text(
                raw_record.get("provider_name"),
                "provider_name",
            ),
            "provider_type": provider_type,
            "country_id": country_id,
            "host_university_id": host_university_id,
            "eligible_nationalities": clean_optional_array(
                raw_record.get("eligible_nationalities")
            ),
            "degree_levels": degree_levels,
            "fields_of_study": clean_optional_array(
                raw_record.get("fields_of_study")
            ),
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
            "age_limit": clean_optional_integer(
                raw_record.get("age_limit"),
                "age_limit",
                minimum=0,
                maximum=100,
            ),
            "funding_type": funding_type,
            "tuition_coverage": clean_optional_text(
                raw_record.get("tuition_coverage")
            ),
            "monthly_allowance": monthly_allowance,
            "allowance_currency": allowance_currency,
            "travel_allowance": clean_optional_text(
                raw_record.get("travel_allowance")
            ),
            "accommodation_support": clean_optional_text(
                raw_record.get("accommodation_support")
            ),
            "health_insurance": clean_optional_text(
                raw_record.get("health_insurance")
            ),
            "required_documents": clean_optional_array(
                raw_record.get("required_documents")
            ),
            "application_opening_date": opening_date,
            "application_deadline": deadline,
            "scholarship_status": scholarship_status,
            "application_cycle": clean_application_cycle(
                raw_record.get("application_cycle")
            ),
            "official_website": validate_url(
                raw_record.get("official_website"),
                "official_website",
            ),
            "source_url": validate_url(
                raw_record.get("source_url"),
                "source_url",
            ),
            "collected_at": collected_at,
            "last_verified_at": last_verified_at,
            "freshness_status": freshness_status,
            "data_quality_status": data_quality_status,
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
    """Check whether all 32 scholarship columns exist."""

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required scholarship columns are missing "
            "or misspelled:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )


def validate_unique_scholarship_ids(
    records: list[dict[str, Any]],
) -> None:
    """Reject duplicate scholarship_id values."""

    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()

    for record in records:
        scholarship_id = record["scholarship_id"]

        if scholarship_id in seen_ids:
            duplicate_ids.add(scholarship_id)

        seen_ids.add(scholarship_id)

    if duplicate_ids:
        raise ValueError(
            "Duplicate scholarship_id values found:\n"
            + "\n".join(
                f"- {scholarship_id}"
                for scholarship_id in sorted(duplicate_ids)
            )
        )


def validate_unique_scholarship_signatures(
    records: list[dict[str, Any]],
) -> None:
    """
    Detect logically duplicated scholarships.

    Signature:
    provider_name + scholarship_name + application_cycle
    """

    seen_signatures: set[tuple[str, str, str]] = set()
    duplicate_ids: list[str] = []

    for record in records:
        signature = (
            record["provider_name"].strip().lower(),
            record["scholarship_name"].strip().lower(),
            record["application_cycle"].strip().lower(),
        )

        if signature in seen_signatures:
            duplicate_ids.append(
                record["scholarship_id"]
            )

        seen_signatures.add(signature)

    if duplicate_ids:
        raise ValueError(
            "Logically duplicated scholarship records found:\n"
            + "\n".join(
                f"- {scholarship_id}"
                for scholarship_id in duplicate_ids
            )
        )


# ---------------------------------------------------------
# Main programme
# ---------------------------------------------------------

def main() -> None:
    """Read scholarships from Excel and create cleaned JSON."""

    print("=" * 60)
    print("EduPath Scholarship ETL")
    print("=" * 60)

    if not INPUT_WORKBOOK.exists():
        raise FileNotFoundError(
            "The prototype workbook was not found.\n"
            f"Expected location: {INPUT_WORKBOOK}"
        )

    print(f"Input workbook: {INPUT_WORKBOOK}")
    print(f"Input sheet: {SHEET_NAME}")

    scholarships_df = pd.read_excel(
        INPUT_WORKBOOK,
        sheet_name=SHEET_NAME,
        engine="openpyxl",
    )

    if scholarships_df.empty:
        raise ValueError(
            f"The '{SHEET_NAME}' sheet contains no records."
        )

    validate_expected_columns(scholarships_df)

    valid_country_ids = load_country_ids()
    university_country_map = load_university_country_map()

    print(
        "Valid country IDs loaded: "
        f"{len(valid_country_ids)}"
    )

    print(
        "Valid university IDs loaded: "
        f"{len(university_country_map)}"
    )

    raw_records = scholarships_df.to_dict(
        orient="records"
    )

    cleaned_records: list[dict[str, Any]] = []

    # Excel row 1 contains headers.
    # The first data record is Excel row 2.
    for row_number, raw_record in enumerate(
        raw_records,
        start=2,
    ):
        cleaned_record = transform_scholarship(
            raw_record=raw_record,
            row_number=row_number,
            valid_country_ids=valid_country_ids,
            university_country_map=university_country_map,
        )

        cleaned_records.append(cleaned_record)

    validate_unique_scholarship_ids(cleaned_records)

    validate_unique_scholarship_signatures(
        cleaned_records
    )

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

    print("\nFirst cleaned scholarship")
    print("-" * 60)

    print(
        json.dumps(
            cleaned_records[0],
            ensure_ascii=False,
            indent=2,
        )
    )

    print(
        "\nScholarship ETL completed successfully."
    )


if __name__ == "__main__":
    main()