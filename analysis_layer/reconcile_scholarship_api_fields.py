from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter, ValidationError
from pydantic_core import PydanticUndefined


# ============================================================
# EduPath - Step 152.7C-5B
# Verified Staging to MongoDB Field Reconciliation
#
# Read-only diagnostic. This script does not repair MongoDB, change
# response schemas, or create a replacement dataset.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFIED_CSV = (
    PROJECT_ROOT / "data" / "staging" / "152_7c_batch_01_verified.csv"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7c5b_scholarship_field_reconciliation.json"
)

COLLECTION_NAME = "scholarships"
MISSING = object()

EXPECTED_ID_BY_COUNTRY = {
    "country_hk": "sch_hk_001",
    "country_my": "sch_my_001",
    "country_sg": "sch_sg_001",
    "country_kr": "sch_kr_001",
    "country_tw": "sch_tw_001",
    "country_th": "sch_th_001",
}
EXPECTED_IDS = tuple(EXPECTED_ID_BY_COUNTRY.values())

FOCUS_FIELDS = (
    "scholarship_status",
    "monthly_allowance",
    "allowance_currency",
    "application_opening_date",
    "application_deadline",
    "funding_type",
    "tuition_coverage",
    "travel_allowance",
    "accommodation_support",
    "health_insurance",
    "minimum_gpa",
    "ielts_requirement",
    "toefl_requirement",
)

CLASSIFICATIONS = {
    "IMPORT_MAPPING_LOSS",
    "SOURCE_VALUE_BLANK",
    "FIELD_NAME_MISMATCH",
    "TYPE_CONVERSION_ERROR",
    "OPTIONAL_FIELD_OMITTED",
    "SCHEMA_REQUIREMENT_MISMATCH",
    "UNKNOWN",
    "NO_ACTION",
}

ACTIONS = {
    "RESTORE_FROM_VERIFIED_SOURCE",
    "NORMALIZE_MISSING_OPTIONAL_TO_NONE",
    "RESEARCH_REQUIRED",
    "IMPORT_MAPPING_FIX_REQUIRED",
    "SCHEMA_DEFAULT_FIX_CANDIDATE",
    "NO_ACTION",
}


def clean_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def is_blank(value: Any) -> bool:
    return value is MISSING or not clean_text(value)


def json_safe(value: Any) -> Any:
    if value is MISSING:
        return "<MISSING>"
    if isinstance(value, dict):
        return {str(key): json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(child) for child in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def type_name(value: Any) -> str:
    if value is MISSING:
        return "missing"
    value_type = type(value)
    return f"{value_type.__module__}.{value_type.__qualname__}"


def format_annotation(annotation: Any) -> str:
    return (
        str(annotation)
        .replace("<class '", "")
        .replace("'>", "")
    )


def schema_default(field: Any) -> tuple[str, bool]:
    """Return a report label and whether the model default is missing."""

    if field.default is PydanticUndefined:
        return "missing", True
    return repr(json_safe(field.default)), False


def annotation_allows_none(annotation: Any) -> bool:
    try:
        TypeAdapter(annotation).validate_python(None)
        return True
    except ValidationError:
        return False


def load_verified_rows() -> tuple[list[dict[str, str]], list[str]]:
    if not VERIFIED_CSV.is_file():
        raise FileNotFoundError(f"Verified CSV was not found: {VERIFIED_CSV}")

    with VERIFIED_CSV.open(
        "r", encoding="utf-8-sig", newline=""
    ) as source_file:
        reader = csv.DictReader(source_file)
        if not reader.fieldnames:
            raise ValueError("Verified CSV has no header.")
        rows = list(reader)
        headers = list(reader.fieldnames)

    if len(rows) != 6:
        raise ValueError(
            f"Verified Batch 01 must contain six rows; found {len(rows)}."
        )
    return rows, headers


def assign_expected_ids(
    rows: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    """
    Match verified rows to the six known integration IDs.

    The original verified research intentionally left scholarship_id blank.
    country_id is the stable verified key because Batch 01 has one row for
    each of the six target countries. No source value is changed here.
    """

    result: dict[str, dict[str, str]] = {}
    for row in rows:
        country_id = clean_text(row.get("country_id"))
        expected_id = EXPECTED_ID_BY_COUNTRY.get(country_id)
        if expected_id is None:
            raise ValueError(
                f"Unexpected verified Batch 01 country_id: {country_id!r}"
            )
        if expected_id in result:
            raise ValueError(f"Duplicate verified row for {country_id}.")
        result[expected_id] = row

    missing = sorted(set(EXPECTED_IDS) - set(result))
    if missing:
        raise ValueError(f"Verified CSV is missing expected rows: {missing}")
    return result


def plain_number(value: str) -> int | float | None:
    text = value.strip().replace(",", "")
    if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text):
        return None
    number = float(text)
    return int(number) if number.is_integer() else number


def comparable_source_value(value: str, mongo_value: Any) -> Any:
    """Normalise common CSV representations only for comparison evidence."""

    text = value.strip()
    if isinstance(mongo_value, list):
        return [
            item.strip()
            for item in re.split(r"[;|]", text)
            if item.strip()
        ]
    if isinstance(mongo_value, (int, float)) and not isinstance(
        mongo_value, bool
    ):
        parsed = plain_number(text)
        return parsed if parsed is not None else text
    if isinstance(mongo_value, (datetime, date)):
        return text[:10]
    return text


def values_equivalent(source_value: str, mongo_value: Any) -> bool:
    normalised_source = comparable_source_value(source_value, mongo_value)
    normalised_mongo = json_safe(mongo_value)
    if isinstance(mongo_value, (datetime, date)):
        normalised_mongo = mongo_value.isoformat()[:10]
    return normalised_source == normalised_mongo


def live_value_validation(
    value: Any,
    annotation: Any,
) -> tuple[bool, str | None]:
    if value is MISSING:
        return False, "MongoDB key is missing."
    try:
        TypeAdapter(annotation).validate_python(value)
        return True, None
    except ValidationError as error:
        messages = "; ".join(
            item["msg"] for item in error.errors(include_url=False)
        )
        return False, messages


def classify(
    *,
    csv_field_exists: bool,
    source_value: Any,
    mongo_value: Any,
    allows_none: bool,
    schema_required: bool,
    live_type_valid: bool,
    equivalent: bool,
) -> tuple[str, str]:
    """Apply source-first diagnostic rules without inventing a value."""

    if not csv_field_exists:
        return "FIELD_NAME_MISMATCH", "IMPORT_MAPPING_FIX_REQUIRED"

    source_blank = is_blank(source_value)
    mongo_missing = mongo_value is MISSING

    # Explicit project rule: a blank verified source is always identified as
    # SOURCE_VALUE_BLANK. Schema/default details remain separately reported.
    if source_blank:
        if mongo_missing and allows_none:
            if schema_required:
                return (
                    "SOURCE_VALUE_BLANK",
                    "SCHEMA_DEFAULT_FIX_CANDIDATE",
                )
            return (
                "SOURCE_VALUE_BLANK",
                "NORMALIZE_MISSING_OPTIONAL_TO_NONE",
            )
        if mongo_missing:
            return "SOURCE_VALUE_BLANK", "RESEARCH_REQUIRED"
        if not live_type_valid:
            return "TYPE_CONVERSION_ERROR", "IMPORT_MAPPING_FIX_REQUIRED"
        return "SOURCE_VALUE_BLANK", "NO_ACTION"

    # Explicit project rule: verified value present but MongoDB key absent.
    if mongo_missing:
        return "IMPORT_MAPPING_LOSS", "RESTORE_FROM_VERIFIED_SOURCE"

    if not live_type_valid:
        return "TYPE_CONVERSION_ERROR", "IMPORT_MAPPING_FIX_REQUIRED"

    if not equivalent:
        return "UNKNOWN", "RESEARCH_REQUIRED"

    return "NO_ACTION", "NO_ACTION"


def print_comparison(item: dict[str, Any]) -> None:
    print(f"Scholarship: {item['scholarship_id']}")
    print(f"Field: {item['field']}")
    print(
        "Verified CSV: "
        + json.dumps(item["verified_csv_value"], ensure_ascii=False)
    )
    print(
        "MongoDB: "
        + json.dumps(item["mongodb_value"], ensure_ascii=False)
    )
    print(f"API expected type: {item['api_expected_type']}")
    print(f"API default: {item['api_default']}")
    print(f"Classification: {item['classification']}")
    print(f"Recommended action: {item['recommended_action']}")
    print()


def main() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    # Reuse both the current connection and exact current API item schema.
    from backend.app.database import close_database, get_database, ping_database
    from backend.app.schemas import ScholarshipResponse

    verified_rows, csv_headers = load_verified_rows()
    verified_by_id = assign_expected_ids(verified_rows)

    comparisons: list[dict[str, Any]] = []
    try:
        ping_database()
        database = get_database()
        live_documents = list(
            database[COLLECTION_NAME].find(
                {"scholarship_id": {"$in": list(EXPECTED_IDS)}}
            )
        )
        live_by_id = {
            clean_text(document.get("scholarship_id")): document
            for document in live_documents
        }

        missing_live_ids = sorted(set(EXPECTED_IDS) - set(live_by_id))
        if missing_live_ids:
            raise RuntimeError(
                f"Live MongoDB is missing Batch 01 records: {missing_live_ids}"
            )
        if len(live_documents) != 6:
            raise RuntimeError(
                "Expected exactly six live Batch 01 scholarship documents; "
                f"found {len(live_documents)}."
            )

        schema_fields = ScholarshipResponse.model_fields
        focus_fields_missing = sorted(set(FOCUS_FIELDS) - set(schema_fields))
        if focus_fields_missing:
            raise RuntimeError(
                "Focus fields missing from current API schema: "
                f"{focus_fields_missing}"
            )

        for scholarship_id in EXPECTED_IDS:
            source = verified_by_id[scholarship_id]
            live = live_by_id[scholarship_id]

            for field_name, model_field in schema_fields.items():
                csv_field_exists = field_name in csv_headers
                source_value = (
                    source.get(field_name, MISSING)
                    if csv_field_exists
                    else MISSING
                )
                live_value = live.get(field_name, MISSING)
                annotation = model_field.annotation
                allows_none = annotation_allows_none(annotation)
                default_label, default_missing = schema_default(model_field)
                schema_required = model_field.is_required()
                type_valid, type_error = live_value_validation(
                    live_value, annotation
                )
                equivalent = (
                    False
                    if source_value is MISSING or live_value is MISSING
                    else values_equivalent(str(source_value), live_value)
                )
                schema_requirement_mismatch = (
                    live_value is MISSING
                    and allows_none
                    and schema_required
                )

                classification, action = classify(
                    csv_field_exists=csv_field_exists,
                    source_value=source_value,
                    mongo_value=live_value,
                    allows_none=allows_none,
                    schema_required=schema_required,
                    live_type_valid=type_valid,
                    equivalent=equivalent,
                )
                if classification not in CLASSIFICATIONS:
                    raise AssertionError(f"Invalid classification: {classification}")
                if action not in ACTIONS:
                    raise AssertionError(f"Invalid action: {action}")

                comparisons.append(
                    {
                        "scholarship_id": scholarship_id,
                        "scholarship_name": live.get("scholarship_name"),
                        "country_id": live.get("country_id"),
                        "field": field_name,
                        "focus_field": field_name in FOCUS_FIELDS,
                        "verified_csv_value": json_safe(source_value),
                        "verified_csv_blank": is_blank(source_value),
                        "mongodb_value": json_safe(live_value),
                        "mongodb_key_present": live_value is not MISSING,
                        "mongodb_python_type": type_name(live_value),
                        "api_expected_type": format_annotation(annotation),
                        "api_allows_none": allows_none,
                        "api_key_required": schema_required,
                        "api_default": default_label,
                        "api_default_missing": default_missing,
                        "schema_requirement_mismatch": (
                            schema_requirement_mismatch
                        ),
                        "mongodb_value_matches_api_type": type_valid,
                        "type_validation_error": type_error,
                        "source_and_mongodb_equivalent": equivalent,
                        "classification": classification,
                        "recommended_action": action,
                    }
                )

        counts = Counter(item["classification"] for item in comparisons)
        other_mismatch_categories = {
            "FIELD_NAME_MISMATCH",
            "TYPE_CONVERSION_ERROR",
            "OPTIONAL_FIELD_OMITTED",
            "UNKNOWN",
        }
        other_mismatches = sum(
            counts[category] for category in other_mismatch_categories
        )
        schema_requirement_mismatches = sum(
            bool(item["schema_requirement_mismatch"])
            for item in comparisons
        )

        report = {
            "step": "152.7C-5B",
            "title": "Verified Staging to MongoDB Field Reconciliation",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "COMPLETE",
            "diagnostic_only": True,
            "mongodb_modified": False,
            "inputs": {
                "verified_csv": str(VERIFIED_CSV),
                "database_source": "backend.app.database",
                "collection": COLLECTION_NAME,
                "api_response_model": (
                    f"{ScholarshipResponse.__module__}."
                    f"{ScholarshipResponse.__name__}"
                ),
            },
            "batch_ids": list(EXPECTED_IDS),
            "source_row_matching": {
                "method": "one verified Batch 01 row per country_id",
                "expected_id_by_country": EXPECTED_ID_BY_COUNTRY,
                "note": (
                    "The verified research CSV intentionally has blank "
                    "scholarship_id values; no source value was altered."
                ),
            },
            "focus_fields": list(FOCUS_FIELDS),
            "summary": {
                "batch_records_checked": len(EXPECTED_IDS),
                "api_schema_fields_per_record": len(schema_fields),
                "fields_checked": len(comparisons),
                "import_mapping_losses": counts["IMPORT_MAPPING_LOSS"],
                "source_blanks": counts["SOURCE_VALUE_BLANK"],
                "schema_requirement_mismatches": counts[
                    "SCHEMA_REQUIREMENT_MISMATCH"
                ] + schema_requirement_mismatches,
                "other_mismatches": other_mismatches,
                "classification_counts": dict(sorted(counts.items())),
            },
            "comparisons": comparisons,
        }

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as output_file:
            json.dump(
                report,
                output_file,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            output_file.write("\n")

        print("=" * 78)
        print("STEP 152.7C-5B VERIFIED STAGING ↔ MONGODB RECONCILIATION")
        print("=" * 78)
        print()
        for comparison in comparisons:
            print_comparison(comparison)

        summary = report["summary"]
        print(f"Batch records checked:          {summary['batch_records_checked']}")
        print(f"Fields checked:                 {summary['fields_checked']}")
        print(f"Import mapping losses:          {summary['import_mapping_losses']}")
        print(f"Source blanks:                  {summary['source_blanks']}")
        print(
            "Schema requirement mismatches: "
            f"{summary['schema_requirement_mismatches']}"
        )
        print(f"Other mismatches:               {summary['other_mismatches']}")
        print()
        print("MongoDB modified: NO")
        print(f"Report: {REPORT_PATH}")
    finally:
        close_database()


if __name__ == "__main__":
    main()
