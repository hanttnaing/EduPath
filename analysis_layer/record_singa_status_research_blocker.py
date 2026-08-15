from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = PROJECT_ROOT / "data" / "analysis"
PLANNING = PROJECT_ROOT / "planning"
DOCS = PROJECT_ROOT / "docs"

STATUS_RESOLUTION = ANALYSIS / "152_7c5c1a_required_status_resolution.json"
REPAIR_PLAN = ANALYSIS / "152_7c5c1c2_live_compatibility_repair_plan.json"
VERIFIED_CSV = PROJECT_ROOT / "data" / "staging" / "152_7c_batch_01_verified.csv"
BASELINE = PROJECT_ROOT / "backups" / "baseline_151_10" / "scholarships.json"

OUTPUT_JSON = ANALYSIS / "152_7c5c1c2a_singa_status_research.json"
OUTPUT_CSV = PLANNING / "48_singa_status_research.csv"
OUTPUT_MD = DOCS / "152_7c5c1c2a_singa_status_research.md"

SCHOLARSHIP_ID = "sch_sg_001"
SCHOLARSHIP_NAME = "Singapore International Graduate Award (SINGA)"
OLD_OFFICIAL_URL = (
    "https://www.a-star.edu.sg/talent/for-graduate-studies/"
    "singapore-international-graduate-award-singa"
)
EVIDENCE_CLASSIFICATION = "PROGRAM_CONFIRMED_STATUS_UNRESOLVED"
NEXT_ACTION = "FIND_CURRENT_APPLICATION_SOURCE_OR_OFFICIAL_STATUS_EVIDENCE"

CSV_COLUMNS = [
    "scholarship_id",
    "scholarship_name",
    "field",
    "current_status_resolution",
    "old_official_url",
    "old_url_state",
    "programme_still_listed",
    "evidence_classification",
    "current_official_listing_url",
    "research_blocker_reason",
    "recommended_next_action",
    "verified_at",
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


def main() -> None:
    protected = (VERIFIED_CSV, BASELINE)
    before = {str(path): digest(path) for path in protected}

    status_package = load_json(STATUS_RESOLUTION)
    repair_plan = load_json(REPAIR_PLAN)
    verified_rows = load_csv(VERIFIED_CSV)

    status_record = next(
        (
            item
            for item in status_package.get("resolutions", [])
            if item.get("scholarship_id") == SCHOLARSHIP_ID
        ),
        None,
    )
    if not status_record:
        raise RuntimeError("Step 1A has no SINGA status resolution record.")
    if (
        status_record.get("resolution_status") != "RESEARCH_REQUIRED"
        or status_record.get("safe_to_patch") is not False
        or status_record.get("proposed_value") is not None
    ):
        raise RuntimeError("Existing SINGA status resolution is no longer unresolved.")

    if SCHOLARSHIP_ID not in repair_plan.get("research_blockers", []):
        raise RuntimeError("Step 1C-2 does not identify SINGA as a research blocker.")

    verified_row = next(
        (row for row in verified_rows if row.get("country_id") == "country_sg"),
        None,
    )
    if not verified_row:
        raise RuntimeError("Verified Batch 01 has no Singapore research row.")
    current_listing_url = (
        verified_row.get("source_url", "").strip()
        or verified_row.get("official_website", "").strip()
    )
    if not current_listing_url:
        raise RuntimeError("No existing official A*STAR listing URL is available.")

    repair_candidate = next(
        (
            item
            for item in repair_plan.get("repair_candidates", [])
            if item.get("scholarship_id") == SCHOLARSHIP_ID
            and item.get("field") == "scholarship_status"
        ),
        None,
    )
    if (
        not repair_candidate
        or repair_candidate.get("repair_classification") != "RESEARCH_REQUIRED"
        or repair_candidate.get("safe_to_apply") is not False
    ):
        raise RuntimeError("Step 1C-2 SINGA live blocker evidence is inconsistent.")

    verified_at = datetime.now(timezone.utc).isoformat()
    blocker_reason = (
        "The previous official SINGA detail URL currently returns Page Not Found. "
        "That URL state does not prove that SINGA is closed or discontinued. "
        "Current official A*STAR material still lists SINGA as an international "
        "graduate/PhD award, but authoritative current application-cycle status "
        "or deadline evidence has not been confirmed. OPEN or CLOSED must not be inferred."
    )
    record = {
        "scholarship_id": SCHOLARSHIP_ID,
        "scholarship_name": SCHOLARSHIP_NAME,
        "field": "scholarship_status",
        "current_status_resolution": "RESEARCH_REQUIRED",
        "old_official_url": OLD_OFFICIAL_URL,
        "old_url_state": "PAGE_NOT_FOUND",
        "programme_still_listed": True,
        "evidence_classification": EVIDENCE_CLASSIFICATION,
        "current_official_listing_url": current_listing_url,
        "research_blocker_reason": blocker_reason,
        "recommended_next_action": NEXT_ACTION,
        "verified_at": verified_at,
    }
    report = {
        "step": "152.7C-5C-1C-2A",
        "title": "SINGA Status Research Blocker Record",
        "status": "BLOCKED_BY_RESEARCH",
        "generated_at": verified_at,
        "source_of_truth_chain": {
            "status_resolution": str(STATUS_RESOLUTION),
            "live_compatibility_repair_plan": str(REPAIR_PLAN),
            "verified_research_artifact": str(VERIFIED_CSV),
            "live_record_evidence": str(REPAIR_PLAN),
        },
        "research_record": record,
        "modifications": {
            "mongodb": False,
            "verified_csv": False,
            "baseline": False,
        },
    }

    after = {str(path): digest(path) for path in protected}
    if before != after:
        raise RuntimeError("A protected source changed during read-only recording.")

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerow({key: record[key] for key in CSV_COLUMNS})

    markdown = f"""# Step 152.7C-5C-1C-2A SINGA Status Research

## Resolution

- Scholarship: `{SCHOLARSHIP_ID}` — {SCHOLARSHIP_NAME}
- Field: `scholarship_status`
- Current resolution: **RESEARCH_REQUIRED**
- Evidence classification: **{EVIDENCE_CLASSIFICATION}**

## Evidence

The [previous official SINGA detail URL]({OLD_OFFICIAL_URL}) currently returns **Page Not Found**. This does not establish that the programme is closed or discontinued.

Current official A*STAR material, represented in the existing provenance chain by the [current official listing URL]({current_listing_url}), still lists SINGA as an international graduate/PhD award. It does not yet provide authoritative current application-cycle status evidence sufficient to assign `OPEN`, `CLOSED`, or another status.

## Blocker

{blocker_reason}

Recommended next action: `{NEXT_ACTION}`.

## Safety

MongoDB, the verified CSV, and the immutable baseline were not modified.
"""
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")

    print("STEP 152.7C-5C-1C-2A SINGA STATUS RESEARCH BLOCKER")
    print(f"\n{SCHOLARSHIP_ID} | scholarship_status | RESEARCH_REQUIRED")
    print(f"Old URL state: PAGE_NOT_FOUND")
    print(f"Programme still listed: YES")
    print(f"Evidence classification: {EVIDENCE_CLASSIFICATION}")
    print(f"Recommended next action: {NEXT_ACTION}")
    print("\nMongoDB modified: NO")
    print("Verified CSV modified: NO")
    print("Baseline modified: NO")
    print("\nSTEP STATUS:")
    print("BLOCKED_BY_RESEARCH")
if __name__ == "__main__":
    main()
