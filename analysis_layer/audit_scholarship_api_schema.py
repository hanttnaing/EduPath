from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError


# ============================================================
# EduPath - Step 152.7C-5A
# Scholarship API Schema Diagnostic
#
# Diagnostic only:
# - reads the existing MongoDB scholarship collection
# - uses the exact ScholarshipResponse model used by the API
# - never writes to MongoDB or changes a backend schema
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = (
    PROJECT_ROOT / "backups" / "baseline_151_10" / "scholarships.json"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7c5a_scholarship_api_schema_audit.json"
)

COLLECTION_NAME = "scholarships"
EXPECTED_TOTAL = 18
EXPECTED_BASELINE_TOTAL = 12

NEW_IDS = (
    "sch_hk_001",
    "sch_my_001",
    "sch_sg_001",
    "sch_kr_001",
    "sch_tw_001",
    "sch_th_001",
)

# This is the projection used by both scholarship GET routes in main.py.
API_EXCLUDED_FIELDS = {
    "_id",
    "content_hash",
    "created_at",
    "database_updated_at",
}

MISSING = object()


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Required baseline was not found: {path}")

    with path.open("r", encoding="utf-8-sig") as source_file:
        value = json.load(source_file)

    if not isinstance(value, list) or not all(
        isinstance(record, dict) for record in value
    ):
        raise ValueError(f"Expected a JSON list of objects: {path}")

    return value


def json_safe(value: Any) -> Any:
    """Represent MongoDB/Python values safely in the JSON audit report."""

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


def python_type_name(value: Any) -> str:
    if value is MISSING:
        return "missing"
    value_type = type(value)
    return f"{value_type.__module__}.{value_type.__qualname__}"


def format_annotation(annotation: Any) -> str:
    """Create a readable description from the live Pydantic model field."""

    text = str(annotation)
    return text.replace("<class '", "").replace("'>", "")


def value_at_location(document: Any, location: tuple[Any, ...]) -> Any:
    """Resolve Pydantic's field/index location against the API document."""

    current = document
    for part in location:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, (list, tuple)) and isinstance(part, int):
            if 0 <= part < len(current):
                current = current[part]
            else:
                return MISSING
        else:
            return MISSING
    return current


def field_path(location: tuple[Any, ...]) -> str:
    if not location:
        return "<record>"

    result = ""
    for part in location:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += ("." if result else "") + str(part)
    return result


def expected_type_for_location(
    location: tuple[Any, ...],
    response_model: type[Any],
) -> str:
    if not location or not isinstance(location[0], str):
        return response_model.__name__

    model_field = response_model.model_fields.get(location[0])
    if model_field is None:
        return "field not declared by response schema"

    expected = format_annotation(model_field.annotation)
    if len(location) > 1:
        expected += f" (value at {field_path(location)})"
    return expected


def api_projection(document: dict[str, Any]) -> dict[str, Any]:
    """Mirror the exclusion projection in GET /api/scholarships."""

    return {
        key: value
        for key, value in document.items()
        if key not in API_EXCLUDED_FIELDS
    }


def validation_issue(
    error: dict[str, Any],
    api_document: dict[str, Any],
    response_model: type[Any],
) -> dict[str, Any]:
    location = tuple(error.get("loc", ()))
    value = value_at_location(api_document, location)

    return {
        "failing_field": field_path(location),
        "mongodb_value": json_safe(value),
        "actual_python_type": python_type_name(value),
        "response_schema_expected_type": expected_type_for_location(
            location, response_model
        ),
        "pydantic_error_type": error.get("type"),
        "pydantic_validation_message": error.get("msg", "Validation failed."),
        "location": list(location),
    }


def serialization_issue(
    error: Exception,
    document: dict[str, Any],
    response_model: type[Any],
) -> dict[str, Any]:
    return {
        "failing_field": "<serialization>",
        "mongodb_value": json_safe(document),
        "actual_python_type": python_type_name(document),
        "response_schema_expected_type": (
            f"JSON-serializable {response_model.__name__}"
        ),
        "pydantic_error_type": type(error).__name__,
        "pydantic_validation_message": str(error),
        "location": [],
    }


def print_failure(record: dict[str, Any]) -> None:
    print(
        f"{record['scholarship_id']} | {record['country_id']} | "
        f"{record['scholarship_name']}"
    )
    for issue in record["issues"]:
        print(f"Field: {issue['failing_field']}")
        print(
            "Value: "
            + json.dumps(
                issue["mongodb_value"], ensure_ascii=False, default=str
            )
        )
        print(f"Actual type: {issue['actual_python_type']}")
        print(
            "Expected type: "
            f"{issue['response_schema_expected_type']}"
        )
        print(
            "Validation error: "
            f"{issue['pydantic_validation_message']}"
        )
    print()


def classify_failure_source(
    failed_ids: set[str],
    baseline_ids: set[str],
) -> str:
    old_failed = bool(failed_ids & baseline_ids)
    new_failed = bool(failed_ids & set(NEW_IDS))

    if old_failed and new_failed:
        return "both old and newly imported records"
    if new_failed:
        return "newly imported records"
    if old_failed:
        return "old records"
    if failed_ids:
        return "records outside the expected old/new ID sets"
    return "none"


def main() -> None:
    # These imports guarantee that this diagnostic follows the current project
    # database configuration and current API model instead of duplicating them.
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from backend.app.database import close_database, get_database, ping_database
    from backend.app.schemas import ScholarshipResponse

    baseline = load_json_list(BASELINE_PATH)
    baseline_ids = {
        str(record.get("scholarship_id", "")).strip() for record in baseline
    }

    audit_records: list[dict[str, Any]] = []
    infrastructure_issues: list[dict[str, Any]] = []

    try:
        ping_database()
        database = get_database()
        documents = list(database[COLLECTION_NAME].find({}))

        if len(documents) != EXPECTED_TOTAL:
            infrastructure_issues.append(
                {
                    "check": "live_scholarship_count",
                    "expected": EXPECTED_TOTAL,
                    "actual": len(documents),
                    "message": "Live collection does not contain exactly 18 records.",
                }
            )

        if len(baseline) != EXPECTED_BASELINE_TOTAL:
            infrastructure_issues.append(
                {
                    "check": "immutable_baseline_count",
                    "expected": EXPECTED_BASELINE_TOTAL,
                    "actual": len(baseline),
                    "message": "Immutable baseline does not contain exactly 12 records.",
                }
            )

        documents.sort(key=lambda item: str(item.get("scholarship_id", "")))

        for document in documents:
            api_document = api_projection(document)
            scholarship_id = str(document.get("scholarship_id", "")).strip()
            issues: list[dict[str, Any]] = []

            try:
                validated = ScholarshipResponse.model_validate(api_document)
                # FastAPI serializes validated response objects to JSON. Testing
                # this separately catches datetime or custom-type serialization.
                validated.model_dump(mode="json")
            except ValidationError as error:
                issues.extend(
                    validation_issue(item, api_document, ScholarshipResponse)
                    for item in error.errors(include_url=False)
                )
            except Exception as error:
                issues.append(
                    serialization_issue(
                        error, api_document, ScholarshipResponse
                    )
                )

            audit_records.append(
                {
                    "scholarship_id": scholarship_id,
                    "scholarship_name": document.get("scholarship_name"),
                    "country_id": document.get("country_id"),
                    "record_group": (
                        "new_batch_01"
                        if scholarship_id in NEW_IDS
                        else "step_151_10_baseline"
                        if scholarship_id in baseline_ids
                        else "unexpected"
                    ),
                    "status": "FAIL" if issues else "PASS",
                    "issues": issues,
                    "object_id_handling": {
                        "raw_id_present": "_id" in document,
                        "raw_id_python_type": python_type_name(
                            document.get("_id", MISSING)
                        ),
                        "excluded_by_api_projection": "_id" not in api_document,
                        "schema_extra_policy": str(
                            ScholarshipResponse.model_config.get("extra")
                        ),
                    },
                }
            )

        found_ids = {record["scholarship_id"] for record in audit_records}
        missing_new_ids = sorted(set(NEW_IDS) - found_ids)
        missing_baseline_ids = sorted(baseline_ids - found_ids)

        if missing_new_ids:
            infrastructure_issues.append(
                {
                    "check": "explicit_new_id_coverage",
                    "expected": list(NEW_IDS),
                    "missing": missing_new_ids,
                    "message": "One or more Batch 01 IDs were not found for validation.",
                }
            )
        if missing_baseline_ids:
            infrastructure_issues.append(
                {
                    "check": "original_record_coverage",
                    "expected_count": EXPECTED_BASELINE_TOTAL,
                    "missing": missing_baseline_ids,
                    "message": "One or more original scholarship IDs were not found.",
                }
            )

        failed_records = [
            record for record in audit_records if record["status"] == "FAIL"
        ]
        passed_records = [
            record for record in audit_records if record["status"] == "PASS"
        ]
        failed_ids = {record["scholarship_id"] for record in failed_records}

        report = {
            "step": "152.7C-5A",
            "title": "Scholarship API Schema Diagnostic",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": (
                "FAIL"
                if failed_records or infrastructure_issues
                else "PASS"
            ),
            "diagnostic_only": True,
            "mongodb_modified": False,
            "database_source": "backend.app.database",
            "collection": COLLECTION_NAME,
            "api_response_model": (
                f"{ScholarshipResponse.__module__}."
                f"{ScholarshipResponse.__name__}"
            ),
            "api_projection_excluded_fields": sorted(API_EXCLUDED_FIELDS),
            "summary": {
                "total_mongodb_scholarships": len(documents),
                "records_passed": len(passed_records),
                "records_failed": len(failed_records),
                "original_records_tested": sum(
                    record["record_group"] == "step_151_10_baseline"
                    for record in audit_records
                ),
                "new_batch_01_records_tested": sum(
                    record["record_group"] == "new_batch_01"
                    for record in audit_records
                ),
                "failure_source": classify_failure_source(
                    failed_ids, baseline_ids
                ),
            },
            "explicit_new_ids": {
                "expected": list(NEW_IDS),
                "found": sorted(set(NEW_IDS) & found_ids),
                "missing": missing_new_ids,
            },
            "infrastructure_issues": infrastructure_issues,
            "records": audit_records,
        }

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as output_file:
            json.dump(
                json_safe(report),
                output_file,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            output_file.write("\n")

        print("=" * 76)
        print("STEP 152.7C-5A SCHOLARSHIP API SCHEMA DIAGNOSTIC")
        print("=" * 76)
        print(f"Total MongoDB scholarships: {len(documents)}")
        print(f"Records passed:             {len(passed_records)}")
        print(f"Records failed:             {len(failed_records)}")
        print()
        print("FAILED RECORDS")
        if failed_records:
            for record in failed_records:
                print_failure(record)
        else:
            print("None")
            print()

        if infrastructure_issues:
            print("AUDIT COVERAGE ISSUES")
            for issue in infrastructure_issues:
                print(f"- {issue['message']}")
            print()

        print("MongoDB modified: NO")
        print(f"Report: {REPORT_PATH}")

        if failed_records or infrastructure_issues:
            raise SystemExit(1)
    finally:
        close_database()


if __name__ == "__main__":
    main()
