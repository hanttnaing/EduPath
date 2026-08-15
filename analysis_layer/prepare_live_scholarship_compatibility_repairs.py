from __future__ import annotations

import copy
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = PROJECT_ROOT / "data" / "analysis"
PLANNING = PROJECT_ROOT / "planning"
DOCS = PROJECT_ROOT / "docs"

PLAN_5C0 = ANALYSIS / "152_7c5c0_targeted_repair_plan.json"
STATUS_RESOLUTION = ANALYSIS / "152_7c5c1a_required_status_resolution.json"
STATUS_CSV = PLANNING / "42_required_scholarship_status_resolution.csv"
MANUAL_CSV = PLANNING / "43_scholarship_manual_review_queue.csv"
MODEL_DESIGN = ANALYSIS / "152_7c5c1b_model_conflict_design.json"
MODEL_CSV = PLANNING / "44_scholarship_model_conflict_resolution.csv"
ID_CSV = PLANNING / "45_scholarship_id_provenance_review.csv"
MODEL_DOC = DOCS / "152_7c5c1b_scholarship_model_design.md"
SCHEMA_VALIDATION = ANALYSIS / "152_7c5c1c_schema_extension_validation.json"
SCHEMAS = PROJECT_ROOT / "backend" / "app" / "schemas.py"

BASELINE = PROJECT_ROOT / "backups" / "baseline_151_10" / "scholarships.json"
VERIFIED = PROJECT_ROOT / "data" / "staging" / "152_7c_batch_01_verified.csv"
CLEANED = PROJECT_ROOT / "data" / "cleaned" / "scholarships.json"

OUTPUT_JSON = ANALYSIS / "152_7c5c1c2_live_compatibility_repair_plan.json"
OUTPUT_CSV = PLANNING / "47_live_scholarship_compatibility_repair_plan.csv"
OUTPUT_MD = DOCS / "152_7c5c1c2_live_compatibility_repair_plan.md"

COLLECTION = "scholarships"
EXPECTED_LIVE_COUNT = 18
EXCLUDED = {"_id", "content_hash", "created_at", "database_updated_at"}
ALLOWED_CLASSES = {
    "SAFE_RESTORE_FROM_VERIFIED_SOURCE",
    "SAFE_NORMALIZATION",
    "STRUCTURED_SCHEMA_MIGRATION",
    "RESEARCH_REQUIRED",
    "NO_ACTION",
}
CSV_COLUMNS = [
    "scholarship_id", "scholarship_name", "field",
    "current_mongodb_value", "verified_source_value", "proposed_value",
    "proposed_companion_field_value", "repair_classification", "reason",
    "source/provenance", "requires_research", "safe_to_apply",
    "simulation_status", "simulation_errors",
]


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [safe(child) for child in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def project(document: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key not in EXCLUDED}


def validate(model: type[Any], document: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    try:
        model.model_validate(project(document)).model_dump(mode="json")
        return "PASS", []
    except ValidationError as error:
        return "FAIL", [
            {
                "field": ".".join(map(str, item["loc"])),
                "root_field": str(item["loc"][0]) if item["loc"] else "<record>",
                "message": item["msg"],
                "type": item["type"],
            }
            for item in error.errors(include_url=False)
        ]


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for item in rows:
            row = {key: item.get(key) for key in CSV_COLUMNS}
            for key in (
                "current_mongodb_value", "verified_source_value", "proposed_value",
                "proposed_companion_field_value", "simulation_errors",
            ):
                row[key] = json.dumps(row[key], ensure_ascii=False)
            writer.writerow(row)


def write_docs(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Step 152.7C-5C-1C-2 Live Compatibility Repair Plan", "",
        "This package is read-only. It proposes updates to existing integrated records but applies none.", "",
        "## Live validation", "",
        f"- Checked: {summary['mongodb_records_checked']}",
        f"- Passing: {summary['mongodb_records_passed']}",
        f"- Failing: {summary['mongodb_records_failed']}", "",
        "## Proposed repairs", "",
    ]
    for item in report["repair_candidates"]:
        lines.append(
            f"- `{item['scholarship_id']}.{item['field']}` — "
            f"**{item['repair_classification']}**: {item['reason']}"
        )
    lines += ["", "## Simulation", "",
        f"- Records simulated: {summary['records_simulated']}",
        f"- Passed: {summary['simulated_records_passed']}",
        f"- Failed: {summary['simulated_records_failed']}", "",
        "Singapore remains blocked because no authoritative cycle status is available. No placeholder was used.", "",
        "## Safety", "", "MongoDB, verified research, baseline, cleaned data, schemas, API routes, and frontend files were not modified.",
    ]
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from backend.app.database import close_database, get_database, ping_database
    from backend.app.schemas import ScholarshipResponse

    protected = (BASELINE, VERIFIED, CLEANED, SCHEMAS)
    before = {str(path): digest(path) for path in protected}

    plan = load_json(PLAN_5C0)
    status_package = load_json(STATUS_RESOLUTION)
    model_design = load_json(MODEL_DESIGN)
    schema_validation = load_json(SCHEMA_VALIDATION)
    load_csv(STATUS_CSV); load_csv(MANUAL_CSV); load_csv(MODEL_CSV); load_csv(ID_CSV)
    if not MODEL_DOC.is_file():
        raise FileNotFoundError(MODEL_DOC)
    if schema_validation.get("api_compatibility", {}).get("status") != "PASS":
        raise RuntimeError("Step 1C API compatibility did not pass.")
    if len([item for item in plan["candidates"] if item["classification"] == "DATA_MODEL_CONFLICT"]) != 6:
        raise RuntimeError("Step 5C-0 conflict plan is incomplete.")
    if model_design["summary"]["all_conflicts_have_safe_representation"] is not True:
        raise RuntimeError("Step 1B did not approve safe representations.")

    status_by_id = {item["scholarship_id"]: item for item in status_package["resolutions"]}
    expected_status_ids = {"sch_hk_001", "sch_kr_001", "sch_sg_001"}
    if set(status_by_id) != expected_status_ids:
        raise RuntimeError("Step 1A status package has unexpected IDs.")

    try:
        ping_database()
        documents = list(get_database()[COLLECTION].find({}))
    finally:
        close_database()
    if len(documents) != EXPECTED_LIVE_COUNT:
        raise RuntimeError(f"Expected 18 live scholarships; found {len(documents)}")

    live_results: list[dict[str, Any]] = []
    failed_documents: dict[str, dict[str, Any]] = {}
    failed_fields: dict[str, set[str]] = {}
    for document in documents:
        status, errors = validate(ScholarshipResponse, document)
        identifier = document.get("scholarship_id")
        live_results.append({"scholarship_id": identifier, "status": status, "errors": errors})
        if status == "FAIL":
            failed_documents[identifier] = document
            failed_fields[identifier] = {error["root_field"] for error in errors}

    expected_failures = {
        "sch_hk_001": {"scholarship_status"},
        "sch_sg_001": {"scholarship_status"},
        "sch_kr_001": {"scholarship_status"},
        "sch_tw_001": {"monthly_allowance"},
    }
    if failed_fields != expected_failures:
        raise RuntimeError(f"Live failures changed unexpectedly: {failed_fields}")

    candidates: list[dict[str, Any]] = []
    for identifier in ("sch_hk_001", "sch_kr_001", "sch_sg_001"):
        document = failed_documents[identifier]
        resolution = status_by_id[identifier]
        resolved = bool(resolution["safe_to_patch"])
        candidate = {
            "scholarship_id": identifier,
            "scholarship_name": document.get("scholarship_name"),
            "field": "scholarship_status",
            "current_mongodb_value": document.get("scholarship_status"),
            "verified_source_value": resolution.get("proposed_value"),
            "proposed_value": resolution.get("proposed_value"),
            "proposed_companion_field_value": None,
            "repair_classification": "SAFE_RESTORE_FROM_VERIFIED_SOURCE" if resolved else "RESEARCH_REQUIRED",
            "reason": resolution["evidence_summary"] if resolved else "Authoritative current application-cycle status remains unconfirmed; no value may be invented.",
            "source/provenance": f"Step 152.7C-5C-1A; {resolution['evidence_source_url']}",
            "requires_research": not resolved,
            "safe_to_apply": resolved,
        }
        candidates.append(candidate)

    tw = failed_documents["sch_tw_001"]
    verified_tier_text = "15000 undergraduate; 20000 Master's/Doctorate"
    tiers = [
        {"degree_level": "Bachelor's", "amount": 15000, "currency": "TWD", "description": "15000 undergraduate"},
        {"degree_level": "Master's/Doctorate", "amount": 20000, "currency": "TWD", "description": "20000 Master's/Doctorate"},
    ]
    candidates.append({
        "scholarship_id": "sch_tw_001",
        "scholarship_name": tw.get("scholarship_name"),
        "field": "monthly_allowance",
        "current_mongodb_value": tw.get("monthly_allowance"),
        "verified_source_value": verified_tier_text,
        "proposed_value": None,
        "proposed_companion_field_value": {"monthly_allowance_details": tiers},
        "repair_classification": "STRUCTURED_SCHEMA_MIGRATION",
        "reason": "The verified stipend has two degree-dependent amounts; clearing the invalid scalar and storing both tiers preserves meaning without selecting a misleading number.",
        "source/provenance": "Step 152.7C-5C-1B model conflict design and planning/44_scholarship_model_conflict_resolution.csv",
        "requires_research": False,
        "safe_to_apply": True,
    })

    for item in candidates:
        if item["repair_classification"] not in ALLOWED_CLASSES:
            raise AssertionError(item["repair_classification"])

    simulations: list[dict[str, Any]] = []
    by_id = {item["scholarship_id"]: item for item in candidates}
    for identifier, document in failed_documents.items():
        simulated = copy.deepcopy(document)
        candidate = by_id[identifier]
        if candidate["safe_to_apply"]:
            simulated[candidate["field"]] = candidate["proposed_value"]
            companion = candidate["proposed_companion_field_value"]
            if isinstance(companion, dict):
                simulated.update(companion)
        status, errors = validate(ScholarshipResponse, simulated)
        expected = "BLOCKED_BY_RESEARCH" if identifier == "sch_sg_001" else "PASS"
        if status != ("FAIL" if expected == "BLOCKED_BY_RESEARCH" else expected):
            raise RuntimeError(f"Unexpected simulation result for {identifier}: {status}")
        simulations.append({"scholarship_id": identifier, "status": status, "expected_outcome": expected, "errors": errors})
        candidate["simulation_status"] = status
        candidate["simulation_errors"] = errors

    class_counts = Counter(item["repair_classification"] for item in candidates)
    passing_live = sum(item["status"] == "PASS" for item in live_results)
    passing_sim = sum(item["status"] == "PASS" for item in simulations)
    blockers = [item["scholarship_id"] for item in candidates if item["requires_research"]]
    overall_status = "BLOCKED_BY_RESEARCH" if blockers else "READY_FOR_REPAIR"
    summary = {
        "mongodb_records_checked": len(documents),
        "mongodb_records_passed": passing_live,
        "mongodb_records_failed": len(documents) - passing_live,
        "safe_restores": class_counts["SAFE_RESTORE_FROM_VERIFIED_SOURCE"],
        "safe_normalizations": class_counts["SAFE_NORMALIZATION"],
        "structured_migrations": class_counts["STRUCTURED_SCHEMA_MIGRATION"],
        "research_required": class_counts["RESEARCH_REQUIRED"],
        "records_simulated": len(simulations),
        "simulated_records_passed": passing_sim,
        "simulated_records_failed": len(simulations) - passing_sim,
    }
    report = {
        "step": "152.7C-5C-1C-2",
        "title": "Live Scholarship Compatibility Repair Preparation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": overall_status,
        "read_only": True,
        "summary": summary,
        "live_validation": live_results,
        "failed_fields": {key: sorted(value) for key, value in failed_fields.items()},
        "repair_candidates": [safe(item) for item in candidates],
        "simulation_results": simulations,
        "research_blockers": blockers,
        "modifications": {"mongodb": False, "verified_csv": False, "baseline": False, "cleaned_datasets": False, "schemas_py": False},
    }

    after = {str(path): digest(path) for path in protected}
    if before != after:
        raise RuntimeError("A protected input changed during read-only planning.")
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(candidates)
    write_docs(report)

    print("STEP 152.7C-5C-1C-2 LIVE COMPATIBILITY REPAIR PREPARATION")
    print(f"\nLIVE VALIDATION\n\nMongoDB records checked: {len(documents)}\nMongoDB records passed: {passing_live}\nMongoDB records failed: {len(documents)-passing_live}")
    print("\nFAILED RECORDS\n")
    for item in candidates:
        print(f"{item['scholarship_id']} | {item['field']} | {item['repair_classification']}")
    print(f"\nREPAIR PLAN\n\nSafe restores: {summary['safe_restores']}\nSafe normalizations: {summary['safe_normalizations']}\nStructured migrations: {summary['structured_migrations']}\nResearch required: {summary['research_required']}")
    print(f"\nSIMULATED REPAIR VALIDATION\n\nRecords simulated: {len(simulations)}\nPassed after simulated repair: {passing_sim}\nFailed after simulated repair: {len(simulations)-passing_sim}")
    print("\nResearch blockers:")
    for blocker in blockers: print(blocker)
    print("\nMongoDB modified: NO\nVerified CSV modified: NO\nBaseline modified: NO\nschemas.py modified: NO")
    print(f"\nSTEP 152.7C-5C-1C-2 STATUS:\n{overall_status}")


if __name__ == "__main__":
    main()
