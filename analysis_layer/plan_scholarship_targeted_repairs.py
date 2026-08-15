from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from types import UnionType
from typing import Any, Union, get_args, get_origin

from pydantic import TypeAdapter, ValidationError


# ============================================================
# EduPath - Step 152.7C-5C-0
# Scholarship Targeted Repair Planning and Type Compatibility Gate
#
# Planning only. MongoDB is read for cross-checking and is never written.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFIED_CSV = (
    PROJECT_ROOT / "data" / "staging" / "152_7c_batch_01_verified.csv"
)
RECONCILIATION_REPORT = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7c5b_scholarship_field_reconciliation.json"
)
BASELINE_SCHOLARSHIPS = (
    PROJECT_ROOT / "backups" / "baseline_151_10" / "scholarships.json"
)
CLEANED_SCHOLARSHIPS = (
    PROJECT_ROOT / "data" / "cleaned" / "scholarships.json"
)
OUTPUT_JSON = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7c5c0_targeted_repair_plan.json"
)
OUTPUT_CSV = (
    PROJECT_ROOT / "planning" / "41_scholarship_targeted_repair_plan.csv"
)

COLLECTION_NAME = "scholarships"
EXPECTED_LIVE_COUNT = 18
EXPECTED_BASELINE_COUNT = 12
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

CATEGORIES = {
    "SAFE_RESTORE",
    "SAFE_OPTIONAL_MISSING",
    "RESEARCH_REQUIRED",
    "DATA_MODEL_CONFLICT",
    "MANUAL_REVIEW",
}

CSV_COLUMNS = [
    "scholarship_id",
    "scholarship_name",
    "field",
    "verified_value",
    "mongodb_value",
    "api_type",
    "classification",
    "safe_normalized_value",
    "reason",
    "recommended_next_action",
]


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


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required project file was not found: {path}")
    with path.open("r", encoding="utf-8-sig") as source_file:
        return json.load(source_file)


def load_json_list(path: Path) -> list[dict[str, Any]]:
    value = load_json(path)
    if not isinstance(value, list) or not all(
        isinstance(item, dict) for item in value
    ):
        raise ValueError(f"Expected a JSON list of objects: {path}")
    return value


def load_verified_rows() -> dict[str, dict[str, str]]:
    if not VERIFIED_CSV.is_file():
        raise FileNotFoundError(f"Verified CSV was not found: {VERIFIED_CSV}")

    with VERIFIED_CSV.open(
        "r", encoding="utf-8-sig", newline=""
    ) as source_file:
        reader = csv.DictReader(source_file)
        if not reader.fieldnames:
            raise ValueError("Verified CSV has no header.")
        rows = list(reader)

    if len(rows) != 6:
        raise ValueError(f"Expected six verified rows; found {len(rows)}.")

    by_id: dict[str, dict[str, str]] = {}
    for row in rows:
        country_id = clean_text(row.get("country_id"))
        scholarship_id = EXPECTED_ID_BY_COUNTRY.get(country_id)
        if scholarship_id is None:
            raise ValueError(f"Unexpected verified country_id: {country_id!r}")
        if scholarship_id in by_id:
            raise ValueError(f"Duplicate verified row for {country_id}.")
        by_id[scholarship_id] = row

    missing = sorted(set(EXPECTED_IDS) - set(by_id))
    if missing:
        raise ValueError(f"Verified CSV is missing Batch 01 rows: {missing}")
    return by_id


def format_annotation(annotation: Any) -> str:
    return str(annotation).replace("<class '", "").replace("'>", "")


def flattened_types(annotation: Any) -> set[type[Any]]:
    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        result: set[type[Any]] = set()
        for argument in get_args(annotation):
            result.update(flattened_types(argument))
        return result
    if annotation is None or annotation is type(None):
        return {type(None)}
    if isinstance(annotation, type):
        return {annotation}
    return set()


def list_item_annotation(annotation: Any) -> Any | None:
    origin = get_origin(annotation)
    if origin is list:
        arguments = get_args(annotation)
        return arguments[0] if arguments else Any
    if origin in (Union, UnionType):
        for argument in get_args(annotation):
            item_type = list_item_annotation(argument)
            if item_type is not None:
                return item_type
    return None


def allows_none(annotation: Any) -> bool:
    try:
        TypeAdapter(annotation).validate_python(None)
        return True
    except ValidationError:
        return False


def plain_number(text: str) -> int | float | None:
    candidate = text.strip().replace(",", "")
    if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", candidate):
        return None
    number = float(candidate)
    return int(number) if number.is_integer() else number


def safe_normalize(value: str, annotation: Any) -> tuple[bool, Any, str]:
    """
    Convert only representations whose meaning is unchanged.

    Conditional numeric text, score descriptions, inequalities, and tiered
    amounts deliberately fail this gate.
    """

    text = value.strip()
    item_annotation = list_item_annotation(annotation)
    types = flattened_types(annotation) - {type(None)}

    if item_annotation is not None:
        items = [
            item.strip()
            for item in re.split(r"[;|]", text)
            if item.strip()
        ]
        if not items:
            return False, None, "No non-blank list items were available."
        normalized: Any = items
        reason = "Semicolon/pipe-delimited source text converts losslessly to list[str]."
    elif types and types.issubset({int, float}):
        number = plain_number(text)
        if number is None:
            return (
                False,
                None,
                "Descriptive, conditional, or multi-value numeric text cannot "
                "be reduced to one number without losing meaning.",
            )
        if types == {int} and not isinstance(number, int):
            return False, None, "A non-integer value cannot be restored to an int field."
        normalized = number
        reason = "Plain numeric source text converts losslessly to a number."
    elif datetime in types:
        try:
            normalized = datetime.fromisoformat(text)
        except ValueError:
            try:
                normalized = datetime.strptime(text, "%Y-%m-%d")
            except ValueError:
                return False, None, "Source text is not an unambiguous ISO date/time."
        reason = "ISO date text converts losslessly to datetime."
    elif types == {str}:
        normalized = text
        reason = "Verified text already matches the API string type."
    else:
        return False, None, "The schema type has no approved lossless conversion rule."

    try:
        validated = TypeAdapter(annotation).validate_python(normalized)
    except ValidationError as error:
        message = "; ".join(
            item["msg"] for item in error.errors(include_url=False)
        )
        return False, None, f"Normalized value still fails the API type: {message}"

    return True, validated, reason


def values_match(left: Any, right: Any) -> bool:
    return json_safe(left) == json_safe(right)


def classify_candidate(
    *,
    source_value: Any,
    mongo_value: Any,
    model_field: Any,
    prior_classification: str,
) -> tuple[str, Any, str, str]:
    annotation = model_field.annotation
    source_blank = is_blank(source_value)
    mongo_missing = mongo_value is MISSING
    optional_none_default = (
        allows_none(annotation)
        and not model_field.is_required()
        and model_field.default is None
    )

    if source_blank:
        if mongo_missing and optional_none_default:
            return (
                "SAFE_OPTIONAL_MISSING",
                None,
                "Verified source is blank, MongoDB omits the key, and the API "
                "field has default None; omission is already valid.",
                "NO_DATABASE_CHANGE",
            )
        if mongo_missing and model_field.is_required():
            return (
                "RESEARCH_REQUIRED",
                None,
                "The API/business field is required, but the verified source "
                "contains no value. A value must not be invented.",
                "VERIFY_REQUIRED_FIELD_FROM_OFFICIAL_SOURCE",
            )
        return (
            "MANUAL_REVIEW",
            None,
            "The verified source is blank while MongoDB contains a value, or "
            "the field does not meet the safe optional-missing rule.",
            "REVIEW_PROVENANCE_AND_INTEGRATION_MAPPING",
        )

    conversion_safe, normalized, conversion_reason = safe_normalize(
        clean_text(source_value), annotation
    )
    if not conversion_safe:
        return (
            "DATA_MODEL_CONFLICT",
            None,
            conversion_reason,
            "RESOLVE_DATA_MODEL_WITHOUT_DISCARDING_VERIFIED_MEANING",
        )

    if mongo_missing and prior_classification == "IMPORT_MAPPING_LOSS":
        return (
            "SAFE_RESTORE",
            normalized,
            "MongoDB lost a verified value and the type gate found a lossless "
            f"conversion. {conversion_reason}",
            "UPDATE_EXISTING_INTEGRATED_RECORD_IN_LATER_REPAIR",
        )

    if mongo_missing:
        return (
            "MANUAL_REVIEW",
            normalized,
            "A safe representation exists, but the prior reconciliation did "
            "not identify this missing value as import mapping loss.",
            "REVIEW_RECONCILIATION_BEFORE_LATER_REPAIR",
        )

    try:
        validated_mongo = TypeAdapter(annotation).validate_python(mongo_value)
    except ValidationError:
        return (
            "DATA_MODEL_CONFLICT",
            None,
            "The current MongoDB value fails the API type. Although the source "
            "was inspected, no automatic replacement is approved at planning time.",
            "RESOLVE_DATA_MODEL_WITHOUT_DISCARDING_VERIFIED_MEANING",
        )

    if values_match(normalized, validated_mongo):
        return (
            "MANUAL_REVIEW",
            normalized,
            "The live value is type-compatible and equivalent after normalization, "
            "but 5B still classified the item as a mismatch.",
            "REVIEW_RECONCILIATION_EVIDENCE",
        )

    return (
        "MANUAL_REVIEW",
        normalized,
        "Both values are type-compatible but differ; selecting either value "
        "automatically could alter verified meaning.",
        "REVIEW_PROVENANCE_AND_INTEGRATION_MAPPING",
    )


def print_item(item: dict[str, Any]) -> None:
    print(
        f"{item['scholarship_id']} | {item['field']} | "
        f"verified={json.dumps(item['verified_value'], ensure_ascii=False)} | "
        f"proposed={json.dumps(item['safe_normalized_value'], ensure_ascii=False)}"
    )
    print(f"Reason: {item['reason']}")
    print(f"Next: {item['recommended_next_action']}")


def write_outputs(report: dict[str, Any], candidates: list[dict[str, Any]]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSON.open("w", encoding="utf-8", newline="\n") as output_file:
        json.dump(
            report,
            output_file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        output_file.write("\n")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open(
        "w", encoding="utf-8-sig", newline=""
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for candidate in candidates:
            row = {key: candidate[key] for key in CSV_COLUMNS}
            row["verified_value"] = json.dumps(
                row["verified_value"], ensure_ascii=False
            )
            row["mongodb_value"] = json.dumps(
                row["mongodb_value"], ensure_ascii=False
            )
            row["safe_normalized_value"] = json.dumps(
                row["safe_normalized_value"], ensure_ascii=False
            )
            writer.writerow(row)


def main() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from backend.app.database import close_database, get_database, ping_database
    from backend.app.schemas import ScholarshipResponse

    verified_by_id = load_verified_rows()
    reconciliation = load_json(RECONCILIATION_REPORT)
    baseline = load_json_list(BASELINE_SCHOLARSHIPS)
    cleaned = load_json_list(CLEANED_SCHOLARSHIPS)

    comparisons = reconciliation.get("comparisons")
    if not isinstance(comparisons, list):
        raise ValueError("5B reconciliation report has no comparisons list.")
    source_candidates = [
        item
        for item in comparisons
        if isinstance(item, dict) and item.get("classification") != "NO_ACTION"
    ]

    candidates: list[dict[str, Any]] = []
    try:
        ping_database()
        database = get_database()
        all_live = list(database[COLLECTION_NAME].find({}))
        if len(all_live) != EXPECTED_LIVE_COUNT:
            raise RuntimeError(
                f"Expected 18 live scholarships; found {len(all_live)}."
            )

        live_by_id = {
            clean_text(document.get("scholarship_id")): document
            for document in all_live
        }
        baseline_ids = {
            clean_text(document.get("scholarship_id")) for document in baseline
        }
        cleaned_ids = {
            clean_text(document.get("scholarship_id")) for document in cleaned
        }

        if len(baseline) != EXPECTED_BASELINE_COUNT:
            raise RuntimeError(
                f"Immutable baseline must contain 12 records; found {len(baseline)}."
            )
        if len(cleaned) != EXPECTED_LIVE_COUNT:
            raise RuntimeError(
                f"Cleaned scholarships must contain 18 records; found {len(cleaned)}."
            )
        if baseline_ids & set(EXPECTED_IDS):
            raise RuntimeError("Batch 01 IDs unexpectedly overlap the immutable baseline.")
        if not set(EXPECTED_IDS).issubset(live_by_id):
            raise RuntimeError("One or more Batch 01 IDs are missing from MongoDB.")
        if not set(EXPECTED_IDS).issubset(cleaned_ids):
            raise RuntimeError("One or more Batch 01 IDs are missing from cleaned data.")

        for source_item in source_candidates:
            scholarship_id = clean_text(source_item.get("scholarship_id"))
            field_name = clean_text(source_item.get("field"))
            if scholarship_id not in EXPECTED_IDS:
                raise ValueError(f"Unexpected 5B scholarship ID: {scholarship_id}")
            model_field = ScholarshipResponse.model_fields.get(field_name)
            if model_field is None:
                raise ValueError(f"5B field is not in ScholarshipResponse: {field_name}")

            verified_row = verified_by_id[scholarship_id]
            live_document = live_by_id[scholarship_id]
            verified_value = verified_row.get(field_name, MISSING)
            mongo_value = live_document.get(field_name, MISSING)

            # Reject stale/tampered 5B evidence before planning against it.
            if not values_match(
                json_safe(verified_value), source_item.get("verified_csv_value")
            ):
                raise RuntimeError(
                    f"5B verified value no longer matches CSV: {scholarship_id}.{field_name}"
                )
            if not values_match(
                json_safe(mongo_value), source_item.get("mongodb_value")
            ):
                raise RuntimeError(
                    f"5B MongoDB value no longer matches live data: {scholarship_id}.{field_name}"
                )

            category, normalized, reason, next_action = classify_candidate(
                source_value=verified_value,
                mongo_value=mongo_value,
                model_field=model_field,
                prior_classification=clean_text(
                    source_item.get("classification")
                ),
            )
            if category not in CATEGORIES:
                raise AssertionError(f"Invalid repair category: {category}")

            candidate = {
                "scholarship_id": scholarship_id,
                "scholarship_name": live_document.get("scholarship_name"),
                "field": field_name,
                "verified_value": json_safe(verified_value),
                "mongodb_value": json_safe(mongo_value),
                "api_type": format_annotation(model_field.annotation),
                "classification": category,
                "safe_normalized_value": json_safe(normalized),
                "reason": reason,
                "recommended_next_action": next_action,
                "prior_5b_classification": source_item.get("classification"),
                "api_required": model_field.is_required(),
                "api_default": (
                    "missing" if model_field.is_required() else json_safe(model_field.default)
                ),
            }
            candidates.append(candidate)

        counts = Counter(item["classification"] for item in candidates)
        actionable = (
            counts["SAFE_RESTORE"]
            + counts["RESEARCH_REQUIRED"]
            + counts["DATA_MODEL_CONFLICT"]
            + counts["MANUAL_REVIEW"]
        )
        summary = {
            "safe_restores": counts["SAFE_RESTORE"],
            "optional_missing_no_repair": counts["SAFE_OPTIONAL_MISSING"],
            "research_required": counts["RESEARCH_REQUIRED"],
            "data_model_conflicts": counts["DATA_MODEL_CONFLICT"],
            "manual_review": counts["MANUAL_REVIEW"],
            "total_actionable_fields": actionable,
            "total_non_no_action_5b_items": len(source_candidates),
        }

        report = {
            "step": "152.7C-5C-0",
            "title": "Scholarship Targeted Repair Planning and Type Compatibility Gate",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "PLAN_COMPLETE",
            "planning_only": True,
            "mongodb_modified": False,
            "architecture": {
                "live_dataset": "Existing 18-record MongoDB scholarships collection",
                "immutable_baseline": str(BASELINE_SCHOLARSHIPS),
                "batch_provenance": str(VERIFIED_CSV),
                "repair_target_policy": (
                    "Any later approved repair updates existing integrated records; "
                    "it must not create duplicate scholarship records."
                ),
            },
            "inputs": {
                "verified_csv": str(VERIFIED_CSV),
                "reconciliation_report": str(RECONCILIATION_REPORT),
                "cleaned_scholarships": str(CLEANED_SCHOLARSHIPS),
                "baseline_directory": str(BASELINE_SCHOLARSHIPS.parent),
                "mongodb_collection": COLLECTION_NAME,
                "api_model": (
                    f"{ScholarshipResponse.__module__}.{ScholarshipResponse.__name__}"
                ),
            },
            "input_validation": {
                "live_scholarships": len(all_live),
                "cleaned_scholarships": len(cleaned),
                "baseline_scholarships": len(baseline),
                "verified_batch_records": len(verified_by_id),
                "all_batch_ids_in_live_dataset": True,
                "all_batch_ids_in_cleaned_dataset": True,
                "batch_ids_absent_from_immutable_baseline": True,
                "reconciliation_values_match_current_sources": True,
            },
            "summary": summary,
            "candidates": candidates,
        }
        write_outputs(report, candidates)

        print("=" * 76)
        print("STEP 152.7C-5C-0 TARGETED REPAIR PLAN")
        print("=" * 76)
        print(f"Safe restores:              {summary['safe_restores']}")
        print(
            "Optional missing/no repair: "
            f"{summary['optional_missing_no_repair']}"
        )
        print(f"Research required:          {summary['research_required']}")
        print(f"Data model conflicts:       {summary['data_model_conflicts']}")
        print(f"Manual review:              {summary['manual_review']}")
        print(f"Total actionable fields:    {summary['total_actionable_fields']}")

        for category, heading in (
            ("RESEARCH_REQUIRED", "RESEARCH_REQUIRED ITEMS"),
            ("DATA_MODEL_CONFLICT", "DATA_MODEL_CONFLICT ITEMS"),
            ("SAFE_RESTORE", "SAFE_RESTORE ITEMS"),
        ):
            print()
            print(heading)
            selected = [
                item for item in candidates if item["classification"] == category
            ]
            if not selected:
                print("None")
            for item in selected:
                print_item(item)

        print()
        print("MongoDB modified: NO")
        print(f"JSON plan: {OUTPUT_JSON}")
        print(f"CSV plan:  {OUTPUT_CSV}")
    finally:
        close_database()


if __name__ == "__main__":
    main()
