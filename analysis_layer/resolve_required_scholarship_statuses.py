from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# EduPath - Step 152.7C-5C-1A
# Required Scholarship Status Research Resolution
#
# Evidence packaging only. MongoDB and all source datasets are read-only.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPAIR_PLAN_JSON = (
    PROJECT_ROOT / "data" / "analysis" / "152_7c5c0_targeted_repair_plan.json"
)
REPAIR_PLAN_CSV = (
    PROJECT_ROOT / "planning" / "41_scholarship_targeted_repair_plan.csv"
)
VERIFIED_CSV = (
    PROJECT_ROOT / "data" / "staging" / "152_7c_batch_01_verified.csv"
)
BASELINE_DIR = PROJECT_ROOT / "backups" / "baseline_151_10"
BASELINE_SCHOLARSHIPS = BASELINE_DIR / "scholarships.json"

OUTPUT_JSON = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7c5c1a_required_status_resolution.json"
)
OUTPUT_STATUS_CSV = (
    PROJECT_ROOT / "planning" / "42_required_scholarship_status_resolution.csv"
)
OUTPUT_MANUAL_CSV = (
    PROJECT_ROOT / "planning" / "43_scholarship_manual_review_queue.csv"
)

COLLECTION_NAME = "scholarships"
EXPECTED_LIVE_COUNT = 18
EXPECTED_BASELINE_COUNT = 12
VERIFIED_ON = "2026-08-13"

EXPECTED_ID_BY_COUNTRY = {
    "country_hk": "sch_hk_001",
    "country_sg": "sch_sg_001",
    "country_kr": "sch_kr_001",
}

STATUS_COLUMNS = [
    "scholarship_id",
    "scholarship_name",
    "field",
    "application_cycle",
    "previous_value",
    "proposed_value",
    "resolution_status",
    "evidence_type",
    "evidence_summary",
    "evidence_source_url",
    "verified_on",
    "confidence",
    "safe_to_patch",
    "notes",
]

MANUAL_COLUMNS = [
    "scholarship_id",
    "scholarship_name",
    "field",
    "verified_value",
    "mongodb_value",
    "api_type",
    "reason",
    "recommended_next_action",
]


def clean_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required project file was not found: {path}")
    with path.open("r", encoding="utf-8-sig") as source_file:
        return json.load(source_file)


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Required project CSV was not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as source_file:
        reader = csv.DictReader(source_file)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        return list(reader)


def verified_status_rows() -> dict[str, dict[str, str]]:
    rows = load_csv(VERIFIED_CSV)
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        scholarship_id = EXPECTED_ID_BY_COUNTRY.get(clean_text(row.get("country_id")))
        if scholarship_id:
            result[scholarship_id] = row
    if set(result) != set(EXPECTED_ID_BY_COUNTRY.values()):
        raise ValueError("Verified CSV does not contain all three status research rows.")
    return result


def json_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_csv(
    path: Path,
    columns: list[str],
    rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=columns)
        writer.writeheader()
        for source in rows:
            row = {column: source.get(column) for column in columns}
            for field in ("previous_value", "proposed_value", "verified_value", "mongodb_value"):
                if field in row:
                    row[field] = json_value(row[field])
            writer.writerow(row)


def resolution_records(
    verified: dict[str, dict[str, str]],
    live_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    definitions = {
        "sch_hk_001": {
            "proposed_value": "CLOSED",
            "resolution_status": "RESOLVED_FROM_OFFICIAL_CYCLE_DATES",
            "evidence_type": "OFFICIAL_CYCLE_DATES",
            "evidence_summary": (
                "Official Hong Kong Research Grants Council information states "
                "that the HKPFS 2026/27 application window ran from 1 September "
                "2025 to 1 December 2025. The integrated record represents that "
                "completed cycle."
            ),
            "confidence": "HIGH",
            "safe_to_patch": True,
            "notes": (
                "Cycle-specific conclusion. Do not use a generic/current website "
                "banner to override the completed 2026/27 application dates."
            ),
        },
        "sch_kr_001": {
            "proposed_value": "CLOSED",
            "resolution_status": "RESOLVED_FROM_OFFICIAL_CYCLE_DATES",
            "evidence_type": "OFFICIAL_CYCLE_SCHEDULE_AND_FINAL_RESULT",
            "evidence_summary": (
                "Official Study in Korea/NIIED schedule information places 2026 "
                "graduate applications in February-March and selection through "
                "June; the 2026 GKS Graduate Degree final result announcement was "
                "published in July 2026."
            ),
            "confidence": "HIGH",
            "safe_to_patch": True,
            "notes": "Cycle-specific resolution for the integrated 2026 record.",
        },
        "sch_sg_001": {
            "proposed_value": None,
            "resolution_status": "RESEARCH_REQUIRED",
            "evidence_type": "OFFICIAL_PROGRAMME_INFORMATION_INSUFFICIENT_FOR_CYCLE_STATUS",
            "evidence_summary": (
                "Official A*STAR material confirms SINGA remains an international "
                "graduate programme, but an authoritative current application-cycle "
                "deadline/status has not been confirmed."
            ),
            "confidence": "INSUFFICIENT_FOR_STATUS_ASSIGNMENT",
            "safe_to_patch": False,
            "notes": (
                "Do not assign OPEN, CLOSED, UPCOMING, or CURRENT by assumption."
            ),
        },
    }

    records: list[dict[str, Any]] = []
    for scholarship_id in ("sch_hk_001", "sch_kr_001", "sch_sg_001"):
        source = verified[scholarship_id]
        live = live_by_id[scholarship_id]
        source_url = clean_text(source.get("source_url")) or clean_text(
            source.get("official_website")
        )
        if not source_url:
            raise ValueError(f"No existing official source URL for {scholarship_id}.")

        record = {
            "scholarship_id": scholarship_id,
            "scholarship_name": live.get("scholarship_name"),
            "field": "scholarship_status",
            "application_cycle": live.get("application_cycle"),
            "previous_value": live.get("scholarship_status"),
            "evidence_source_url": source_url,
            "verified_on": VERIFIED_ON,
            **definitions[scholarship_id],
        }
        records.append(record)
    return records


def main() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from backend.app.database import close_database, get_database, ping_database
    from backend.app.schemas import ScholarshipResponse

    plan = load_json(REPAIR_PLAN_JSON)
    plan_csv = load_csv(REPAIR_PLAN_CSV)
    verified = verified_status_rows()
    baseline = load_json(BASELINE_SCHOLARSHIPS)

    candidates = plan.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("5C-0 JSON plan has no candidates list.")
    research_items = [
        item for item in candidates if item.get("classification") == "RESEARCH_REQUIRED"
    ]
    manual_items = [
        item for item in candidates if item.get("classification") == "MANUAL_REVIEW"
    ]
    csv_research = [
        row for row in plan_csv if row.get("classification") == "RESEARCH_REQUIRED"
    ]
    csv_manual = [
        row for row in plan_csv if row.get("classification") == "MANUAL_REVIEW"
    ]

    if len(research_items) != 3 or len(csv_research) != 3:
        raise RuntimeError("5C-0 plan must contain exactly three research-required items.")
    if len(manual_items) != 6 or len(csv_manual) != 6:
        raise RuntimeError("5C-0 plan must contain exactly six manual-review items.")
    if not isinstance(baseline, list) or len(baseline) != EXPECTED_BASELINE_COUNT:
        raise RuntimeError("Immutable baseline must contain exactly 12 scholarships.")

    expected_research_keys = {
        (scholarship_id, "scholarship_status")
        for scholarship_id in EXPECTED_ID_BY_COUNTRY.values()
    }
    actual_research_keys = {
        (clean_text(item.get("scholarship_id")), clean_text(item.get("field")))
        for item in research_items
    }
    if actual_research_keys != expected_research_keys:
        raise RuntimeError("Research-required items do not match the expected status fields.")

    status_field = ScholarshipResponse.model_fields.get("scholarship_status")
    if (
        status_field is None
        or status_field.annotation is not str
        or not status_field.is_required()
    ):
        raise RuntimeError("Current ScholarshipResponse status contract is not required str.")

    try:
        ping_database()
        database = get_database()
        collection = database[COLLECTION_NAME]
        if collection.count_documents({}) != EXPECTED_LIVE_COUNT:
            raise RuntimeError("Live scholarship collection must contain exactly 18 records.")
        live_documents = list(
            collection.find({"scholarship_id": {"$in": list(EXPECTED_ID_BY_COUNTRY.values())}})
        )
        live_by_id = {
            clean_text(document.get("scholarship_id")): document
            for document in live_documents
        }
        if set(live_by_id) != set(EXPECTED_ID_BY_COUNTRY.values()):
            raise RuntimeError("One or more status-resolution records are absent from MongoDB.")
        if any("scholarship_status" in document for document in live_documents):
            raise RuntimeError(
                "A target live status changed after 5C-0; refresh diagnostics before resolving."
            )

        resolutions = resolution_records(verified, live_by_id)
        resolved = [item for item in resolutions if item["safe_to_patch"]]
        unresolved = [item for item in resolutions if not item["safe_to_patch"]]

        manual_queue = [
            {column: item.get(column) for column in MANUAL_COLUMNS}
            for item in manual_items
        ]

        report = {
            "step": "152.7C-5C-1A",
            "title": "Required Scholarship Status Research Resolution",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "RESOLUTION_PACKAGE_COMPLETE",
            "diagnostic_and_planning_only": True,
            "mongodb_modified": False,
            "verified_csv_modified": False,
            "baseline_modified": False,
            "inputs": {
                "targeted_repair_plan_json": str(REPAIR_PLAN_JSON),
                "targeted_repair_plan_csv": str(REPAIR_PLAN_CSV),
                "verified_csv": str(VERIFIED_CSV),
                "baseline_directory": str(BASELINE_DIR),
                "mongodb_collection": COLLECTION_NAME,
                "api_model": f"{ScholarshipResponse.__module__}.{ScholarshipResponse.__name__}",
            },
            "summary": {
                "research_required_records": len(resolutions),
                "resolved_safely": len(resolved),
                "still_research_required": len(unresolved),
                "manual_review_queue": len(manual_queue),
            },
            "resolutions": resolutions,
            "manual_review_queue": manual_queue,
            "next_step": "Step 152.7C-5C-1B — Data Model Conflict Resolution Design",
        }

        OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_JSON.open("w", encoding="utf-8", newline="\n") as output_file:
            json.dump(report, output_file, indent=2, ensure_ascii=False, allow_nan=False)
            output_file.write("\n")
        write_csv(OUTPUT_STATUS_CSV, STATUS_COLUMNS, resolutions)
        write_csv(OUTPUT_MANUAL_CSV, MANUAL_COLUMNS, manual_queue)

        print("=" * 78)
        print("STEP 152.7C-5C-1A REQUIRED STATUS RESEARCH RESOLUTION")
        print("=" * 78)
        print(f"Research-required records: {len(resolutions)}")
        print(f"Resolved safely:           {len(resolved)}")
        print(f"Still research-required:   {len(unresolved)}")
        print()
        print("RESOLVED")
        for item in resolved:
            print(f"{item['scholarship_id']} | {item['field']} | {item['proposed_value']}")
        print()
        print("UNRESOLVED")
        for item in unresolved:
            print(f"{item['scholarship_id']} | {item['field']} | RESEARCH_REQUIRED")
        print()
        print("MANUAL REVIEW QUEUE")
        print(len(manual_queue))
        for item in manual_queue:
            print(f"Scholarship: {item['scholarship_id']}")
            print(f"Field: {item['field']}")
            print(f"Verified value: {json_value(item['verified_value'])}")
            print(f"MongoDB value: {json_value(item['mongodb_value'])}")
            print(f"API type: {item['api_type']}")
            print(f"Reason: {item['reason']}")
            print(f"Recommended next action: {item['recommended_next_action']}")
            print()
        print("MongoDB modified: NO")
        print("Verified CSV modified: NO")
        print("Baseline modified: NO")
        print()
        print("NEXT:")
        print("Step 152.7C-5C-1B — Data Model Conflict Resolution Design.")
    finally:
        close_database()


if __name__ == "__main__":
    main()
