from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE = PROJECT_ROOT / "backups" / "baseline_151_10" / "scholarships.json"
VERIFIED = PROJECT_ROOT / "data" / "staging" / "152_7c_batch_01_verified.csv"
SCHEMAS = PROJECT_ROOT / "backend" / "app" / "schemas.py"
BACKUP = PROJECT_ROOT / "backups" / "pre_152_7c5c1c" / "schemas.py"
MAIN = PROJECT_ROOT / "backend" / "app" / "main.py"
OUTPUT_JSON = PROJECT_ROOT / "data" / "analysis" / "152_7c5c1c_schema_extension_validation.json"
OUTPUT_CSV = PROJECT_ROOT / "planning" / "46_scholarship_schema_extension_validation.csv"
OUTPUT_MD = PROJECT_ROOT / "docs" / "152_7c5c1c_schema_extension_design.md"

NEW_FIELDS = (
    "ielts_requirement_text",
    "toefl_requirement_text",
    "age_requirement_details",
    "monthly_allowance_details",
)
PROJECTION_EXCLUDES = {"_id", "content_hash", "created_at", "database_updated_at"}
CSV_COLUMNS = ["scope", "record_id", "test_name", "status", "errors"]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(model: type[Any], value: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    try:
        model.model_validate(value).model_dump(mode="json")
        return "PASS", []
    except ValidationError as error:
        return "FAIL", [
            {"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]}
            for item in error.errors(include_url=False)
        ]
    except Exception as error:
        return "FAIL", [{"field": "<serialization>", "message": str(error), "type": type(error).__name__}]


def base_record(baseline: list[dict[str, Any]]) -> dict[str, Any]:
    if not baseline:
        raise RuntimeError("Baseline is empty.")
    return {key: value for key, value in baseline[0].items() if key not in PROJECTION_EXCLUDES}


def conflict_tests(baseline: list[dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    legacy = base_record(baseline)
    malaysia_ielts = {**legacy, "scholarship_id": "test_my_ielts", "ielts_requirement": 6.0, "ielts_requirement_text": "6.0 or higher, or accepted equivalent/English-medium prior degree evidence"}
    malaysia_toefl = {**legacy, "scholarship_id": "test_my_toefl", "toefl_requirement": 550, "toefl_requirement_text": "550 PBT or equivalent"}
    malaysia_age = {**legacy, "scholarship_id": "test_my_age", "age_limit": None, "age_requirement_details": [{"degree_level": "Master", "operator": "<=", "age": 40}, {"degree_level": "PhD", "operator": "<=", "age": 45}]}
    taiwan_allowance = {**legacy, "scholarship_id": "test_tw_allowance", "monthly_allowance": None, "monthly_allowance_details": [{"degree_level": "Undergraduate", "amount": 15000, "currency": "TWD"}, {"degree_level": "Master's/Doctorate", "amount": 20000, "currency": "TWD"}]}
    thailand_english = {**legacy, "scholarship_id": "test_th_english", "ielts_requirement": None, "ielts_requirement_text": "Good command of English; institution-specific English test requirements may apply"}
    thailand_age = {**legacy, "scholarship_id": "test_th_age", "age_limit": 45, "age_requirement_details": [{"operator": "<=", "age": 45, "description": "Maximum age 45; source meaning <=45."}]}
    old_without_companions = {key: value for key, value in legacy.items() if key not in NEW_FIELDS}
    return [
        ("legacy_japan_old_fields", legacy),
        ("malaysia_ielts_numeric_plus_text", malaysia_ielts),
        ("malaysia_toefl_numeric_plus_text", malaysia_toefl),
        ("malaysia_degree_specific_age", malaysia_age),
        ("taiwan_degree_specific_allowance", taiwan_allowance),
        ("thailand_non_numeric_english", thailand_english),
        ("thailand_age_maximum_45", thailand_age),
        ("old_document_without_companion_fields", old_without_companions),
    ]


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            output = dict(row)
            output["errors"] = json.dumps(output["errors"], ensure_ascii=False)
            writer.writerow(output)


def write_docs(report: dict[str, Any]) -> None:
    summary = report["summary"]
    text = f"""# Step 152.7C-5C-1C Schema Extension

The existing `ScholarshipResponse` model was extended additively. Existing fields were not removed or renamed.

## New nested models

- `AgeRequirement`: optional `degree_level`, `operator`, `age`, and `description` fields.
- `AllowanceTier`: optional `degree_level`, `amount`, `currency`, and `description` fields.

## New optional response fields

- `ielts_requirement_text: str | None = None`
- `toefl_requirement_text: str | None = None`
- `age_requirement_details: list[AgeRequirement] | None = None`
- `monthly_allowance_details: list[AllowanceTier] | None = None`

All defaults are `None`; old documents and clients remain compatible.

## Validation outcome

- Conflict cases: {summary['conflict_tests_passed']}/{summary['conflict_tests_executed']} passed.
- Immutable baseline: {summary['baseline_records_passed']}/{summary['baseline_records_checked']} passed.
- Live MongoDB snapshot: {summary['mongodb_records_passed']}/{summary['mongodb_records_checked']} passed.
- API structural compatibility: {report['api_compatibility']['status']}.

The live failures, if any, are pre-existing record issues and were not hidden or repaired in this schema step. No MongoDB records, verified research, baseline data, or frontend files were changed.
"""
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(text, encoding="utf-8")


def main() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from backend.app.database import close_database, get_database, ping_database
    from backend.app.schemas import AllowanceTier, AgeRequirement, ScholarshipListResponse, ScholarshipResponse

    protected_before = {str(path): digest(path) for path in (BASELINE, VERIFIED)}
    baseline = load_json(BASELINE)
    if len(baseline) != 12:
        raise RuntimeError(f"Expected 12 baseline records; found {len(baseline)}")
    if not BACKUP.is_file() or digest(BACKUP) == digest(SCHEMAS):
        raise RuntimeError("Required pre-change schema backup is absent or schema was not extended.")

    for field in NEW_FIELDS:
        model_field = ScholarshipResponse.model_fields.get(field)
        if model_field is None or model_field.is_required() or model_field.default is not None:
            raise RuntimeError(f"Companion field is not optional with default None: {field}")
    if AgeRequirement.model_fields["age"].is_required() or AllowanceTier.model_fields["amount"].is_required():
        raise RuntimeError("Nested extension fields unexpectedly became required.")

    rows: list[dict[str, Any]] = []
    tests = conflict_tests(baseline)
    for name, payload in tests:
        status, errors = validate(ScholarshipResponse, payload)
        rows.append({"scope": "CONFLICT_TEST", "record_id": payload.get("scholarship_id"), "test_name": name, "status": status, "errors": errors})

    baseline_results = []
    for record in baseline:
        status, errors = validate(ScholarshipResponse, {key: value for key, value in record.items() if key not in PROJECTION_EXCLUDES})
        baseline_results.append(status)
        rows.append({"scope": "BASELINE", "record_id": record.get("scholarship_id"), "test_name": "extended_schema_validation", "status": status, "errors": errors})

    mongo_results: list[str] = []
    try:
        ping_database()
        documents = list(get_database()["scholarships"].find({}))
        for document in documents:
            projected = {key: value for key, value in document.items() if key not in PROJECTION_EXCLUDES}
            status, errors = validate(ScholarshipResponse, projected)
            mongo_results.append(status)
            rows.append({"scope": "MONGODB", "record_id": document.get("scholarship_id"), "test_name": "extended_schema_validation", "status": status, "errors": errors})
    finally:
        close_database()

    main_text = MAIN.read_text(encoding="utf-8")
    old_document_status, _ = validate(ScholarshipResponse, tests[-1][1])
    list_status, list_errors = validate(ScholarshipListResponse, {"total": 1, "count": 1, "items": [tests[-1][1]]})
    api_pass = all(("response_model=ScholarshipListResponse" in main_text, old_document_status == "PASS", list_status == "PASS"))
    rows.append({"scope": "API", "record_id": "/api/scholarships", "test_name": "old_document_response_compatibility", "status": "PASS" if api_pass else "FAIL", "errors": list_errors})

    test_passed = sum(row["status"] == "PASS" for row in rows if row["scope"] == "CONFLICT_TEST")
    baseline_passed = baseline_results.count("PASS")
    mongo_passed = mongo_results.count("PASS")
    all_required_pass = (
        test_passed == len(tests)
        and baseline_passed == len(baseline)
        and mongo_passed == len(mongo_results)
        and api_pass
        and protected_before == {str(path): digest(path) for path in (BASELINE, VERIFIED)}
    )
    report = {
        "step": "152.7C-5C-1C", "title": "Schema Extension Implementation & Compatibility Validation", "generated_at": datetime.now(timezone.utc).isoformat(), "status": "PASS" if all_required_pass else "FAIL",
        "schema_extensions": list(NEW_FIELDS), "nested_models": ["AgeRequirement", "AllowanceTier"],
        "summary": {"conflict_tests_executed": len(tests), "conflict_tests_passed": test_passed, "conflict_tests_failed": len(tests) - test_passed, "baseline_records_checked": len(baseline), "baseline_records_passed": baseline_passed, "baseline_records_failed": len(baseline) - baseline_passed, "mongodb_records_checked": len(mongo_results), "mongodb_records_passed": mongo_passed, "mongodb_records_failed": len(mongo_results) - mongo_passed},
        "api_compatibility": {"status": "PASS" if api_pass else "FAIL", "route": "GET /api/scholarships", "response_model": "ScholarshipListResponse", "old_documents_without_companions_valid": old_document_status == "PASS"},
        "results": rows, "modifications": {"mongodb": False, "verified_csv": False, "baseline": False, "schemas_py": True}, "backup": str(BACKUP),
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(rows)
    write_docs(report)

    print("STEP 152.7C-5C-1C SCHEMA EXTENSION IMPLEMENTATION & COMPATIBILITY VALIDATION")
    print("\nSCHEMA EXTENSIONS")
    for field in NEW_FIELDS: print(field)
    print(f"\nCONFLICT TEST CASES\nTests executed: {len(tests)}\nPassed: {test_passed}\nFailed: {len(tests)-test_passed}")
    print(f"\nBACKWARD COMPATIBILITY\nBaseline records checked: {len(baseline)}\nBaseline records passed: {baseline_passed}\nBaseline records failed: {len(baseline)-baseline_passed}")
    print(f"\nMongoDB records checked: {len(mongo_results)}\nMongoDB records passed: {mongo_passed}\nMongoDB records failed: {len(mongo_results)-mongo_passed}")
    print(f"\nAPI compatibility: {'PASS' if api_pass else 'FAIL'}")
    print("\nMongoDB modified: NO\nVerified CSV modified: NO\nBaseline modified: NO\nschemas.py modified: YES")
    print(f"\nSTEP 152.7C-5C-1C STATUS: {report['status']}")
    if all_required_pass:
        print("\nNEXT:\nStep 152.7C-5C-1D — Safe Existing Scholarship Record Repair Preparation.")
    raise SystemExit(0 if all_required_pass else 1)


if __name__ == "__main__":
    main()
