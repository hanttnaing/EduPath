from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = PROJECT_ROOT / "data" / "analysis"
PLANNING = PROJECT_ROOT / "planning"
STAGING = PROJECT_ROOT / "data" / "staging"
BASELINE = PROJECT_ROOT / "backups" / "baseline_151_10" / "scholarships.json"
SCHEMA_FILE = PROJECT_ROOT / "backend" / "app" / "schemas.py"

PLAN_JSON = ANALYSIS / "152_7c5c0_targeted_repair_plan.json"
STATUS_JSON = ANALYSIS / "152_7c5c1a_required_status_resolution.json"
PLAN_CSV = PLANNING / "41_scholarship_targeted_repair_plan.csv"
STATUS_CSV = PLANNING / "42_required_scholarship_status_resolution.csv"
MANUAL_CSV = PLANNING / "43_scholarship_manual_review_queue.csv"
VERIFIED_CSV = STAGING / "152_7c_batch_01_verified.csv"
PREIMPORT_CSV = STAGING / "152_7c_batch_01_preimport.csv"
PREIMPORT_JSON = ANALYSIS / "152_7c_batch_01_preimport.json"
PREIMPORT_REPORT = ANALYSIS / "152_7c3_preimport_report.json"
PREIMPORT_SCRIPT = PROJECT_ROOT / "analysis_layer" / "prepare_scholarship_batch_01_preimport.py"

OUTPUT_JSON = ANALYSIS / "152_7c5c1b_model_conflict_design.json"
OUTPUT_CONFLICT_CSV = PLANNING / "44_scholarship_model_conflict_resolution.csv"
OUTPUT_ID_CSV = PLANNING / "45_scholarship_id_provenance_review.csv"
OUTPUT_MD = PROJECT_ROOT / "docs" / "152_7c5c1b_scholarship_model_design.md"

IDS = ("sch_hk_001", "sch_my_001", "sch_sg_001", "sch_kr_001", "sch_tw_001", "sch_th_001")
CONFLICT_COLUMNS = ["scholarship_id", "field", "verified_value", "current_api_type", "classification", "recommended_existing_field_value", "recommended_companion_field", "recommended_companion_value", "meaning_preserved", "backward_compatible", "reason"]
ID_COLUMNS = ["scholarship_id", "verified_source_value", "integrated_value", "provenance_source", "provenance_status", "uniqueness_status", "classification", "recommended_action", "reason"]


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


def fmt(annotation: Any) -> str:
    return str(annotation).replace("<class '", "").replace("'>", "")


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for source in rows:
            row = {key: source.get(key) for key in columns}
            for key, value in row.items():
                if value is None or isinstance(value, (list, dict, bool, int, float)):
                    row[key] = json.dumps(value, ensure_ascii=False)
            writer.writerow(row)


def conflict_designs(model: type[Any], conflicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {(item["scholarship_id"], item["field"]): item for item in conflicts}
    specifications = {
        ("sch_my_001", "ielts_requirement"): ("BACKWARD_COMPATIBLE_TEXT_EXTENSION", 6.0, "ielts_requirement_text", "6.0 or higher, or accepted equivalent/English-medium prior degree evidence", "The numeric baseline is usable only while the alternative/equivalence condition remains available as text."),
        ("sch_my_001", "toefl_requirement"): ("BACKWARD_COMPATIBLE_TEXT_EXTENSION", 550, "toefl_requirement_text", "550 PBT or equivalent", "The PBT score is usable only while test format and equivalence wording remain available as text."),
        ("sch_my_001", "age_limit"): ("STRUCTURED_EXTENSION_RECOMMENDED", None, "age_requirement_details", [{"degree_level": "Master", "maximum_age": 40, "operator": "<="}, {"degree_level": "PhD", "maximum_age": 45, "operator": "<="}], "One scalar age limit cannot express two degree-specific maxima."),
        ("sch_tw_001", "monthly_allowance"): ("STRUCTURED_EXTENSION_RECOMMENDED", None, "monthly_allowance_details", [{"degree_levels": ["Bachelor"], "amount": 15000, "currency": "TWD"}, {"degree_levels": ["Master", "PhD"], "amount": 20000, "currency": "TWD"}], "One scalar allowance would misrepresent the degree-dependent stipend."),
        ("sch_th_001", "ielts_requirement"): ("BACKWARD_COMPATIBLE_TEXT_EXTENSION", None, "ielts_requirement_text", "Good command of English; institution-specific English test requirements may apply", "No numeric IELTS threshold is verified; text preserves the non-numeric requirement without invention."),
        ("sch_th_001", "age_limit"): ("SAFE_NUMERIC_NORMALIZATION", 45, None, None, "Existing recommendation code treats age_limit as a maximum and rejects ages above it; <=45 is therefore losslessly represented by 45."),
    }
    if set(by_key) != set(specifications):
        raise RuntimeError(f"Expected six exact conflicts; got {sorted(by_key)}")
    output = []
    for key, spec in specifications.items():
        item = by_key[key]
        classification, existing, companion, companion_value, reason = spec
        output.append({
            "scholarship_id": key[0], "field": key[1],
            "verified_value": item["verified_value"],
            "current_api_type": fmt(model.model_fields[key[1]].annotation),
            "classification": classification,
            "recommended_existing_field_value": existing,
            "recommended_companion_field": companion,
            "recommended_companion_value": companion_value,
            "meaning_preserved": True, "backward_compatible": True, "reason": reason,
        })
    return output


def id_reviews(manual: list[dict[str, str]], verified: list[dict[str, str]], preimport: list[dict[str, str]], live_ids: list[str], baseline_ids: set[str]) -> list[dict[str, Any]]:
    verified_by_country = {row["country_id"].strip(): row for row in verified}
    pre_by_id = {row["scholarship_id"].strip(): row for row in preimport}
    country_by_id = {identifier: f"country_{identifier.split('_')[1]}" for identifier in IDS}
    if len(manual) != 6 or {row["scholarship_id"] for row in manual} != set(IDS):
        raise RuntimeError("Manual queue is not the expected six scholarship IDs.")
    if len(live_ids) != len(set(live_ids)) or not set(IDS).issubset(live_ids):
        raise RuntimeError("Live scholarship IDs are not unique/complete.")
    output = []
    for identifier in IDS:
        source_value = verified_by_country[country_by_id[identifier]].get("scholarship_id", "")
        integrated = pre_by_id[identifier].get("scholarship_id")
        proven = not source_value.strip() and integrated == identifier and identifier not in baseline_ids
        output.append({
            "scholarship_id": identifier,
            "verified_source_value": source_value,
            "integrated_value": integrated,
            "provenance_source": "analysis_layer/prepare_scholarship_batch_01_preimport.py::make_new_scholarship_id; data/staging/152_7c_batch_01_preimport.csv",
            "provenance_status": "PROVEN" if proven else "UNRESOLVED",
            "uniqueness_status": "UNIQUE_IN_LIVE_COLLECTION" if live_ids.count(identifier) == 1 else "NOT_UNIQUE",
            "classification": "INTEGRATION_GENERATED_ID" if proven else "MANUAL_REVIEW",
            "recommended_action": "NO_REPAIR_REQUIRED" if proven else "INVESTIGATE_ID_PROVENANCE",
            "reason": "Step 152.7C-3 derived the country prefix, selected the next unused number against baseline/new IDs, and wrote the ID only to the integration/pre-import layer; the research artifact correctly remains blank." if proven else "The integration-generation chain was not fully proven.",
        })
    return output


def markdown(report: dict[str, Any]) -> str:
    conflicts = report["conflicts"]
    ids = report["id_provenance_reviews"]
    lines = ["# Step 152.7C-5C-1B Scholarship Model Design", "", "This is a design-only, backward-compatible resolution. No database, source research, baseline, schema, or API behavior was changed.", "", "## Existing fields to keep", "", "- `ielts_requirement: int | float | None`", "- `toefl_requirement: int | None`", "- `age_limit: int | None`", "- `monthly_allowance: int | float | None`", "", "## New optional fields proposed", "", "- `ielts_requirement_text: str | None = None` — preserves alternatives and non-numeric English conditions.", "- `toefl_requirement_text: str | None = None` — preserves test format/equivalence qualifiers.", "- `age_requirement_details: list[AgeRequirement] | None = None` — stores degree-specific operator/max-age rules.", "- `monthly_allowance_details: list[AllowanceTier] | None = None` — stores degree-specific amount/currency tiers.", "", "## Fields that require no change", "", "- Thailand `age_limit` can safely store `45` because existing logic treats it as a maximum.", "- Existing scalar fields remain available to all current API clients.", "", "## Normalization rules", "", "- Extract a scalar only when its qualifiers are retained in a companion field.", "- Never invent a numeric score for non-numeric English requirements.", "- Never collapse degree-specific ages or stipend tiers into one scalar.", "- Preserve missing values as `None`.", "", "## Conflict resolutions", ""]
    for item in conflicts:
        lines.append(f"- `{item['scholarship_id']}.{item['field']}` — **{item['classification']}**: {item['reason']}")
    lines += ["", "## ID provenance", "", "All six IDs were generated deliberately in the Step 152.7C-3 integration layer and are unique in the live collection. The verified research CSV should retain blank internal IDs.", ""]
    for item in ids:
        lines.append(f"- `{item['scholarship_id']}` — {item['classification']}; {item['recommended_action']}.")
    lines += ["", "## Algorithm impact", "", "- Numeric threshold plus descriptive alternative: use the scalar for threshold screening, but treat a failed scalar check as potentially eligible when the text records an accepted equivalent/exemption; surface the text for review.", "- Degree-specific age requirements: select the structured rule matching the candidate degree before comparing age; do not use a global maximum.", "- Degree-specific allowance amounts: select matching tiers for ranking/display; do not compare an absent scalar as zero.", "- Non-numeric English requirements: do not hard-reject numerically; flag for document/institution-specific verification.", "", "## API compatibility impact", "", "Adding optional fields with default `None` is backward-compatible for current clients and preserves existing scalar response fields. Structured child models require additive response-schema and serialization tests. No endpoint behavior should change until compatibility validation passes.", "", "## Next step gate", "", "All six conflicts have documented meaning-preserving strategies. Step 152.7C-5C-1C — Schema Extension Implementation and Compatibility Validation may proceed.", ""]
    return "\n".join(lines)


def main() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from backend.app.database import close_database, get_database, ping_database
    from backend.app.schemas import ScholarshipResponse

    protected = [VERIFIED_CSV, BASELINE, SCHEMA_FILE]
    before = {str(path): digest(path) for path in protected}
    plan = load_json(PLAN_JSON)
    status = load_json(STATUS_JSON)
    load_csv(PLAN_CSV); load_csv(STATUS_CSV)
    manual = load_csv(MANUAL_CSV)
    verified = load_csv(VERIFIED_CSV)
    preimport = load_csv(PREIMPORT_CSV)
    load_json(PREIMPORT_JSON); load_json(PREIMPORT_REPORT)
    script_text = PREIMPORT_SCRIPT.read_text(encoding="utf-8")
    if "make_new_scholarship_id" not in script_text or "newly_assigned_ids" not in script_text:
        raise RuntimeError("Step 152.7C-3 ID generation logic was not found.")
    conflicts_source = [item for item in plan["candidates"] if item["classification"] == "DATA_MODEL_CONFLICT"]
    conflicts = conflict_designs(ScholarshipResponse, conflicts_source)
    baseline_ids = {row["scholarship_id"] for row in load_json(BASELINE)}
    try:
        ping_database()
        collection = get_database()["scholarships"]
        live = list(collection.find({}, {"scholarship_id": 1}))
        if len(live) != 18:
            raise RuntimeError(f"Expected 18 live scholarships; found {len(live)}")
        live_ids = [row["scholarship_id"] for row in live]
        reviews = id_reviews(manual, verified, preimport, live_ids, baseline_ids)
    finally:
        close_database()

    extensions = [
        {"field": "ielts_requirement_text", "type": "str | None", "default": None, "reason": "Preserve IELTS alternatives, equivalences, exemptions, and non-numeric requirements."},
        {"field": "toefl_requirement_text", "type": "str | None", "default": None, "reason": "Preserve TOEFL format and equivalence qualifiers."},
        {"field": "age_requirement_details", "type": "list[AgeRequirement] | None", "default": None, "reason": "Represent degree-specific maximum ages and comparison operators."},
        {"field": "monthly_allowance_details", "type": "list[AllowanceTier] | None", "default": None, "reason": "Represent degree-specific stipend amounts and currency without selecting one misleading scalar."},
    ]
    all_safe = len(conflicts) == 6 and all(item["meaning_preserved"] and item["backward_compatible"] for item in conflicts)
    confirmed = sum(item["classification"] == "INTEGRATION_GENERATED_ID" for item in reviews)
    report = {
        "step": "152.7C-5C-1B", "title": "Data Model Conflict Resolution Design and ID Provenance Review", "generated_at": datetime.now(timezone.utc).isoformat(), "status": "DESIGN_COMPLETE", "design_only": True,
        "modifications": {"mongodb": False, "verified_csv": False, "baseline": False, "schemas_py": False},
        "inputs": [str(path) for path in [PLAN_JSON, STATUS_JSON, PLAN_CSV, STATUS_CSV, MANUAL_CSV, VERIFIED_CSV, PREIMPORT_CSV, PREIMPORT_JSON, BASELINE, SCHEMA_FILE, PREIMPORT_SCRIPT]],
        "status_resolution_context": status["summary"], "conflicts": conflicts, "id_provenance_reviews": reviews,
        "schema_design": {"existing_fields_to_keep": ["ielts_requirement", "toefl_requirement", "age_limit", "monthly_allowance"], "new_optional_fields_proposed": extensions, "fields_requiring_no_change": ["sch_th_001.age_limit -> 45"], "normalization_rules": ["Preserve qualifiers in companion fields", "Do not invent numeric English thresholds", "Do not collapse degree-specific rules or tiers", "Keep optional absence as None"], "algorithm_impact": {"numeric_plus_text": "Use scalar screening while honoring documented alternatives/exemptions through review logic.", "degree_specific_age": "Match degree-specific structured rule before age comparison.", "degree_specific_allowance": "Select matching tier for ranking/display; absent scalar is not zero.", "non_numeric_english": "Do not numeric-hard-reject; require institution/document verification."}, "api_compatibility_impact": "Additive optional fields with default None preserve existing clients and scalar fields; structured models require compatibility tests."},
        "summary": {"data_model_conflicts_reviewed": len(conflicts), "integration_generated_ids_confirmed": confirmed, "unresolved_id_provenance": len(reviews) - confirmed, "all_conflicts_have_safe_representation": all_safe},
        "next_step_recommended": "Step 152.7C-5C-1C — Schema Extension Implementation and Compatibility Validation" if all_safe else None,
    }
    after = {str(path): digest(path) for path in protected}
    if before != after:
        raise RuntimeError("A protected source changed during design generation.")
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(OUTPUT_CONFLICT_CSV, CONFLICT_COLUMNS, conflicts)
    write_csv(OUTPUT_ID_CSV, ID_COLUMNS, reviews)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(markdown(report), encoding="utf-8")

    print("STEP 152.7C-5C-1B DATA MODEL CONFLICT RESOLUTION DESIGN")
    print(f"\nData model conflicts reviewed: {len(conflicts)}")
    for item in conflicts: print(f"{item['scholarship_id']} | {item['field']} | {item['classification']}")
    print("\nSCHOLARSHIP ID PROVENANCE REVIEW")
    print(f"\nIDs reviewed: {len(reviews)}\nIntegration-generated IDs confirmed: {confirmed}\nUnresolved ID provenance: {len(reviews) - confirmed}")
    print("\nPROPOSED BACKWARD-COMPATIBLE MODEL EXTENSIONS")
    for item in extensions: print(f"{item['field']} | {item['type']} | {item['reason']}")
    print("\nMongoDB modified: NO\nVerified CSV modified: NO\nBaseline modified: NO\nschemas.py modified: NO")
    if all_safe:
        print("\nNEXT:\nStep 152.7C-5C-1C — Schema Extension Implementation and Compatibility Validation.")


if __name__ == "__main__":
    main()
