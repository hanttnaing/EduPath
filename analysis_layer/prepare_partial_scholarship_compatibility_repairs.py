from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter, ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = PROJECT_ROOT / "data" / "analysis"
PLANNING = PROJECT_ROOT / "planning"
DOCS = PROJECT_ROOT / "docs"
STAGING = PROJECT_ROOT / "data" / "staging"

BASELINE = PROJECT_ROOT / "backups" / "baseline_151_10" / "scholarships.json"
VERIFIED = STAGING / "152_7c_batch_01_verified.csv"
CLEANED = PROJECT_ROOT / "data" / "cleaned" / "scholarships.json"
SOURCE_PLAN_CSV = STAGING / "152_7b_scholarship_source_collection.csv"
SOURCE_PLAN_JSON = ANALYSIS / "152_7b_scholarship_source_plan.json"

STATUS_RESOLUTION = ANALYSIS / "152_7c5c1a_required_status_resolution.json"
MODEL_DESIGN = ANALYSIS / "152_7c5c1b_model_conflict_design.json"
SCHEMA_VALIDATION = ANALYSIS / "152_7c5c1c_schema_extension_validation.json"
LIVE_REPAIR_PLAN = ANALYSIS / "152_7c5c1c2_live_compatibility_repair_plan.json"
SINGA_BLOCKER = ANALYSIS / "152_7c5c1c2a_singa_status_research.json"
LIVE_REPAIR_CSV = PLANNING / "47_live_scholarship_compatibility_repair_plan.csv"
SINGA_BLOCKER_CSV = PLANNING / "48_singa_status_research.csv"

OUTPUT_JSON = ANALYSIS / "152_7c5c1c2b_partial_repair_simulation.json"
OUTPUT_CSV = PLANNING / "49_partial_scholarship_compatibility_repairs.csv"
OUTPUT_MD = DOCS / "152_7c5c1c2b_partial_repair_simulation.md"

COLLECTION = "scholarships"
EXCLUDED_ID = "sch_sg_001"
EXPECTED_LIVE_COUNT = 18
INTERNAL_FIELDS = {"_id", "content_hash", "created_at", "database_updated_at"}
CSV_COLUMNS = [
    "scholarship_id", "scholarship_name", "field",
    "current_mongodb_value", "proposed_value",
    "proposed_monthly_allowance_details", "classification",
    "source_provenance", "simulation_status", "simulation_errors",
]


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
    return {key: value for key, value in document.items() if key not in INTERNAL_FIELDS}


def validate(model: type[Any], document: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    try:
        model.model_validate(project(document)).model_dump(mode="json")
        return "PASS", []
    except ValidationError as error:
        return "FAIL", [
            {
                "field": ".".join(map(str, item["loc"])),
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
                "current_mongodb_value", "proposed_value",
                "proposed_monthly_allowance_details", "simulation_errors",
            ):
                row[key] = json.dumps(row[key], ensure_ascii=False)
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use the previous 18-record live report without attempting MongoDB.",
    )
    args = parser.parse_args()

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from backend.app.schemas import ScholarshipResponse

    protected = tuple(
        path
        for path in (BASELINE, VERIFIED, CLEANED, SOURCE_PLAN_CSV, SOURCE_PLAN_JSON)
        if path.is_file()
    )
    before = {str(path): digest(path) for path in protected}

    baseline = load_json(BASELINE)
    status_package = load_json(STATUS_RESOLUTION)
    model_design = load_json(MODEL_DESIGN)
    schema_validation = load_json(SCHEMA_VALIDATION)
    live_plan = load_json(LIVE_REPAIR_PLAN)
    singa = load_json(SINGA_BLOCKER)
    live_plan_rows = load_csv_rows(LIVE_REPAIR_CSV)
    singa_rows = load_csv_rows(SINGA_BLOCKER_CSV)

    if len(baseline) != 12:
        raise RuntimeError(f"Immutable baseline must contain 12 records; found {len(baseline)}")
    if schema_validation.get("api_compatibility", {}).get("status") != "PASS":
        raise RuntimeError("Schema/API compatibility is not confirmed.")
    if model_design.get("summary", {}).get("all_conflicts_have_safe_representation") is not True:
        raise RuntimeError("Model-conflict design has not approved safe representations.")
    if (
        singa.get("status") != "BLOCKED_BY_RESEARCH"
        or singa.get("research_record", {}).get("scholarship_id") != EXCLUDED_ID
        or singa.get("research_record", {}).get("current_status_resolution") != "RESEARCH_REQUIRED"
    ):
        raise RuntimeError("SINGA blocker evidence is missing or inconsistent.")
    if len(live_plan_rows) != 4:
        raise RuntimeError("Planning/47 must contain four live repair candidates.")
    if (
        len(singa_rows) != 1
        or singa_rows[0].get("scholarship_id") != EXCLUDED_ID
        or singa_rows[0].get("current_status_resolution") != "RESEARCH_REQUIRED"
    ):
        raise RuntimeError("Planning/48 SINGA blocker evidence is inconsistent.")

    approved = {
        (item["scholarship_id"], item["field"]): item
        for item in live_plan.get("repair_candidates", [])
        if item.get("safe_to_apply") is True
    }
    expected_approved = {
        ("sch_hk_001", "scholarship_status"),
        ("sch_kr_001", "scholarship_status"),
        ("sch_tw_001", "monthly_allowance"),
    }
    if set(approved) != expected_approved:
        raise RuntimeError(f"Approved partial candidates changed: {sorted(approved)}")
    status_by_id = {
        item["scholarship_id"]: item
        for item in status_package.get("resolutions", [])
    }
    for identifier in ("sch_hk_001", "sch_kr_001"):
        resolution = status_by_id.get(identifier, {})
        if resolution.get("proposed_value") != "CLOSED" or resolution.get("safe_to_patch") is not True:
            raise RuntimeError(f"Safe CLOSED resolution is not confirmed for {identifier}.")

    documents: list[dict[str, Any]] | None = None
    connection_error: str | None = None
    if not args.offline:
        try:
            from backend.app.database import close_database, get_database, ping_database

            try:
                ping_database()
                documents = list(get_database()[COLLECTION].find({}))
            finally:
                close_database()
        except Exception as error:
            connection_error = f"{type(error).__name__}: {error}"

    validation_source = "LIVE_MONGODB" if documents is not None else "PREVIOUS_LIVE_REPORT"
    live_database_recheck_required = documents is None
    live_by_id: dict[str, dict[str, Any]] = {}
    excluded_before: Any = None
    if documents is not None:
        if len(documents) != EXPECTED_LIVE_COUNT:
            raise RuntimeError(f"Expected 18 live records; found {len(documents)}")
        live_by_id = {document.get("scholarship_id"): document for document in documents}
        if len(live_by_id) != EXPECTED_LIVE_COUNT:
            raise RuntimeError("Live scholarship IDs are not unique.")
        if EXCLUDED_ID not in live_by_id:
            raise RuntimeError("Excluded SINGA record is absent from MongoDB.")
        excluded_before = safe(copy.deepcopy(live_by_id[EXCLUDED_ID]))
    else:
        live_summary = live_plan.get("summary", {})
        if (
            live_summary.get("mongodb_records_checked") != EXPECTED_LIVE_COUNT
            or live_summary.get("mongodb_records_passed") != 14
            or live_summary.get("mongodb_records_failed") != 4
        ):
            raise RuntimeError("Previous live report is not the approved 18-record snapshot.")
        if EXCLUDED_ID not in live_plan.get("research_blockers", []):
            raise RuntimeError("Previous live report does not isolate SINGA.")
    allowance_details = [
        {
            "degree_level": "Undergraduate",
            "amount": 15000,
            "currency": "TWD",
            "description": "15000 TWD per month for Undergraduate",
        },
        {
            "degree_level": "Master's",
            "amount": 20000,
            "currency": "TWD",
            "description": "20000 TWD per month for Master's",
        },
        {
            "degree_level": "Doctorate",
            "amount": 20000,
            "currency": "TWD",
            "description": "20000 TWD per month for Doctorate",
        },
    ]
    proposals = {
        "sch_hk_001": {
            "field": "scholarship_status", "value": "CLOSED",
            "details": None, "classification": "SAFE_RESTORE_FROM_VERIFIED_SOURCE",
            "source": "Step 152.7C-5C-1A official-cycle status resolution",
        },
        "sch_kr_001": {
            "field": "scholarship_status", "value": "CLOSED",
            "details": None, "classification": "SAFE_RESTORE_FROM_VERIFIED_SOURCE",
            "source": "Step 152.7C-5C-1A official-cycle status resolution",
        },
        "sch_tw_001": {
            "field": "monthly_allowance", "value": None,
            "details": allowance_details, "classification": "STRUCTURED_SCHEMA_MIGRATION",
            "source": "Steps 152.7C-5C-1B and 1C-2 verified tiered allowance design",
        },
    }

    results: list[dict[str, Any]] = []
    cached_by_id = {
        item["scholarship_id"]: item
        for item in live_plan.get("repair_candidates", [])
    }
    for identifier, proposal in proposals.items():
        if documents is not None:
            if identifier not in live_by_id:
                raise RuntimeError(f"Repair candidate is absent from MongoDB: {identifier}")
            simulated = copy.deepcopy(live_by_id[identifier])
            simulated[proposal["field"]] = proposal["value"]
            if proposal["details"] is not None:
                simulated["monthly_allowance_details"] = proposal["details"]
            status, errors = validate(ScholarshipResponse, simulated)
            scholarship_name = simulated.get("scholarship_name")
            current_value = safe(live_by_id[identifier].get(proposal["field"]))
        else:
            cached = cached_by_id.get(identifier)
            if not cached or cached.get("simulation_status") != "PASS":
                raise RuntimeError(f"Previous full-record simulation is not PASS: {identifier}")
            errors = []
            try:
                field_annotation = ScholarshipResponse.model_fields[
                    proposal["field"]
                ].annotation
                TypeAdapter(field_annotation).validate_python(proposal["value"])
                if proposal["details"] is not None:
                    details_annotation = ScholarshipResponse.model_fields[
                        "monthly_allowance_details"
                    ].annotation
                    TypeAdapter(details_annotation).validate_python(
                        proposal["details"]
                    )
                status = "PASS"
            except ValidationError as error:
                status = "FAIL"
                errors = [
                    {
                        "field": ".".join(map(str, item["loc"])),
                        "message": item["msg"],
                        "type": item["type"],
                    }
                    for item in error.errors(include_url=False)
                ]
            scholarship_name = cached.get("scholarship_name")
            current_value = cached.get("current_mongodb_value")
        results.append({
            "scholarship_id": identifier,
            "scholarship_name": scholarship_name,
            "field": proposal["field"],
            "current_mongodb_value": current_value,
            "proposed_value": proposal["value"],
            "proposed_monthly_allowance_details": proposal["details"],
            "classification": proposal["classification"],
            "source_provenance": proposal["source"],
            "simulation_status": status,
            "simulation_errors": errors,
        })

    if documents is not None and safe(live_by_id[EXCLUDED_ID]) != excluded_before:
        raise RuntimeError("Excluded SINGA record changed during simulation.")

    baseline_results = [validate(ScholarshipResponse, record)[0] for record in baseline]
    baseline_pass = all(status == "PASS" for status in baseline_results)
    simulated_passed = sum(item["simulation_status"] == "PASS" for item in results)
    all_pass = (
        len(results) == 3
        and simulated_passed == 3
        and baseline_pass
        and (
            documents is None
            or safe(live_by_id[EXCLUDED_ID]) == excluded_before
        )
    )
    step_status = (
        "READY_FOR_PARTIAL_REPAIR"
        if all_pass and validation_source == "LIVE_MONGODB"
        else "READY_FOR_PARTIAL_REPAIR_PENDING_LIVE_RECHECK"
        if all_pass
        else "BLOCKED"
    )
    summary = {
        "safe_repair_candidates": len(results),
        "research_blockers_excluded": 1,
        "excluded_scholarship": EXCLUDED_ID,
        "records_simulated": len(results),
        "records_passed_after_simulated_repair": simulated_passed,
        "records_failed_after_simulated_repair": len(results) - simulated_passed,
        "baseline_records_checked": len(baseline),
        "baseline_records_passed": baseline_results.count("PASS"),
        "baseline_records_failed": baseline_results.count("FAIL"),
        "baseline_compatibility": "PASS" if baseline_pass else "FAIL",
        "validation_source": validation_source,
        "live_database_recheck_required": live_database_recheck_required,
    }
    report = {
        "step": "152.7C-5C-1C-2B",
        "title": "Partial Scholarship Compatibility Repair Simulation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": step_status,
        "read_only_simulation": True,
        "validation_source": validation_source,
        "live_database_recheck_required": live_database_recheck_required,
        "live_connection_error": connection_error,
        "summary": summary,
        "research_blocker": {
            "scholarship_id": EXCLUDED_ID,
            "field": "scholarship_status",
            "classification": "RESEARCH_BLOCKER_EXCLUDED_FROM_PARTIAL_REPAIR",
            "resolution": "RESEARCH_REQUIRED",
            "modified_in_simulation": False,
        },
        "repair_simulations": results,
        "fallback_evidence": (
            str(LIVE_REPAIR_PLAN)
            if validation_source == "PREVIOUS_LIVE_REPORT"
            else None
        ),
        "modifications": {
            "mongodb": False, "verified_csv": False, "baseline": False,
            "cleaned_datasets": False, "source_plan_files": False,
        },
    }

    after = {str(path): digest(path) for path in protected}
    if before != after:
        raise RuntimeError("A protected project file changed during simulation.")
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(results)

    lines = [
        "# Step 152.7C-5C-1C-2B Partial Repair Simulation", "",
        "This read-only simulation isolates the unresolved SINGA status while retaining the existing 18-record architecture.", "",
        "## Safe candidates", "",
    ]
    for item in results:
        lines.append(f"- `{item['scholarship_id']}.{item['field']}` — {item['classification']} — {item['simulation_status']}")
    lines += [
        "", "## Research blocker excluded", "",
        "- `sch_sg_001.scholarship_status` — `RESEARCH_BLOCKER_EXCLUDED_FROM_PARTIAL_REPAIR`.",
        "- The live and simulated SINGA document was not changed.", "",
        "## Taiwan allowance representation", "",
        "The invalid scalar is proposed as `None`. Three structured tiers preserve Undergraduate 15000 TWD/month, Master's 20000 TWD/month, and Doctorate 20000 TWD/month.", "",
        "## Validation", "",
        f"- Simulated records: {len(results)}; passed: {simulated_passed}; failed: {len(results)-simulated_passed}.",
        f"- Baseline compatibility: {summary['baseline_compatibility']} ({summary['baseline_records_passed']}/12).", "",
        f"- Validation source: `{validation_source}`.",
        f"- Fresh live database recheck required before any write: `{'YES' if live_database_recheck_required else 'NO'}`.", "",
        "MongoDB, verified research, immutable baseline, cleaned datasets, and source-plan files were not modified.",
    ]
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("STEP 152.7C-5C-1C-2B PARTIAL REPAIR SIMULATION")
    print(f"\nSafe repair candidates: {len(results)}")
    print("Research blockers excluded: 1")
    print(f"Excluded scholarship: {EXCLUDED_ID}")
    print(f"Records simulated: {len(results)}")
    print(f"Records passed after simulated repair: {simulated_passed}")
    print(f"Records failed after simulated repair: {len(results)-simulated_passed}")
    print(f"Baseline compatibility: {summary['baseline_compatibility']}")
    print(f"\nValidation source: {validation_source}")
    print(
        "Live database recheck required: "
        f"{'YES' if live_database_recheck_required else 'NO'}"
    )
    print("\nMongoDB modified: NO")
    print("Verified CSV modified: NO")
    print("Baseline modified: NO")
    print("\nSTEP 152.7C-5C-1C-2B STATUS:")
    print(step_status)
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
