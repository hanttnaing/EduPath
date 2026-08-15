from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from bson import json_util
from dotenv import load_dotenv
from pydantic import BaseModel
from pymongo import MongoClient


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BASELINE_FILE = ROOT / "backups" / "baseline_151_10" / "scholarships.json"

REPORT_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "152_7c5c1c2c_partial_mongodb_repair_report.json"
)

REPORT_CSV = (
    ROOT
    / "planning"
    / "50_partial_scholarship_mongodb_repair.csv"
)

REPORT_MD = (
    ROOT
    / "docs"
    / "152_7c5c1c2c_partial_mongodb_repair.md"
)


TARGET_IDS = [
    "sch_hk_001",
    "sch_kr_001",
    "sch_tw_001",
]

BLOCKER_ID = "sch_sg_001"


TAIWAN_ALLOWANCE_DETAILS = [
    {
        "degree_level": "Bachelor's",
        "amount": 15000,
        "currency": "TWD",
        "description": "Monthly living allowance for undergraduate recipients",
    },
    {
        "degree_level": "Master's",
        "amount": 20000,
        "currency": "TWD",
        "description": "Monthly living allowance for master's recipients",
    },
    {
        "degree_level": "Doctorate",
        "amount": 20000,
        "currency": "TWD",
        "description": "Monthly living allowance for doctoral recipients",
    },
]


# ============================================================
# HELPERS
# ============================================================

def sanitize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    copied = deepcopy(doc)
    copied.pop("_id", None)
    return copied


def load_baseline() -> list[dict[str, Any]]:
    if not BASELINE_FILE.exists():
        raise RuntimeError(f"Baseline file not found: {BASELINE_FILE}")

    with BASELINE_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise RuntimeError("Baseline scholarships.json must contain a list.")

    return data


def find_scholarship_schema():
    """
    Dynamically finds the existing Scholarship Pydantic model.

    This avoids hard-coding a model class name while preserving
    the existing backend schema.
    """
    from backend.app import schemas

    candidates = []

    for name, obj in vars(schemas).items():
        if not isinstance(obj, type):
            continue

        try:
            if not issubclass(obj, BaseModel):
                continue
        except TypeError:
            continue

        fields = getattr(obj, "model_fields", None)

        if fields is None:
            fields = getattr(obj, "__fields__", {})

        field_names = set(fields.keys())

        required_fields = {
            "scholarship_id",
            "scholarship_status",
            "monthly_allowance",
            "monthly_allowance_details",
        }

        if required_fields.issubset(field_names):
            candidates.append((name, obj))

    if not candidates:
        raise RuntimeError(
            "Could not find Scholarship schema containing the "
            "required compatibility fields."
        )

    # Prefer a response/read schema if multiple models match.
    candidates.sort(
        key=lambda item: (
            "response" not in item[0].lower(),
            "read" not in item[0].lower(),
            item[0],
        )
    )

    name, model = candidates[0]

    print(f"Scholarship schema detected: {name}")

    return model


def validate_document(model, doc: dict[str, Any]) -> tuple[bool, str | None]:
    clean = sanitize_doc(doc)

    try:
        if hasattr(model, "model_validate"):
            model.model_validate(clean)
        else:
            model.parse_obj(clean)

        return True, None

    except Exception as exc:
        return False, str(exc)


def connect_database():
    load_dotenv(ROOT / ".env", override=True)

    uri = os.getenv("MONGODB_URI")

    if not uri:
        raise RuntimeError("MONGODB_URI is missing from .env")

    db_name = (
        os.getenv("MONGODB_DATABASE")
        or os.getenv("MONGODB_DB")
        or os.getenv("DB_NAME")
        or "edupath_db"
    )

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=20000,
    )

    ping = client.admin.command("ping")

    if not ping.get("ok"):
        client.close()
        raise RuntimeError("MongoDB ping failed.")

    return client, client[db_name]


def build_simulated_document(doc: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(doc)

    scholarship_id = result.get("scholarship_id")

    if scholarship_id == "sch_hk_001":
        result["scholarship_status"] = "CLOSED"

    elif scholarship_id == "sch_kr_001":
        result["scholarship_status"] = "CLOSED"

    elif scholarship_id == "sch_tw_001":
        result["monthly_allowance"] = None
        result["monthly_allowance_details"] = deepcopy(
            TAIWAN_ALLOWANCE_DETAILS
        )

    else:
        raise RuntimeError(
            f"Unexpected repair target: {scholarship_id}"
        )

    return result


def validate_baseline(model) -> tuple[int, int, list]:
    baseline = load_baseline()

    passed = 0
    failures = []

    for record in baseline:
        ok, error = validate_document(model, record)

        if ok:
            passed += 1
        else:
            failures.append(
                {
                    "scholarship_id": record.get("scholarship_id"),
                    "error": error,
                }
            )

    return passed, len(failures), failures


def create_backup(collection) -> tuple[Path, int]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_dir = (
        ROOT
        / "backups"
        / f"pre_152_7c5c1c2c_{timestamp}"
    )

    backup_dir.mkdir(parents=True, exist_ok=False)

    backup_file = (
        backup_dir
        / "scholarships_before_partial_repair.json"
    )

    records = list(collection.find({}))

    backup_file.write_text(
        json_util.dumps(records, indent=2),
        encoding="utf-8",
    )

    return backup_file, len(records)


def write_outputs(report: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_CSV.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)

    REPORT_JSON.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    csv_rows = []

    for item in report.get("targets", []):
        csv_rows.append(
            {
                "scholarship_id": item.get("scholarship_id"),
                "status": item.get("status"),
                "fields_changed": ", ".join(
                    item.get("fields_changed", [])
                ),
                "validation": item.get("validation"),
            }
        )

    with REPORT_CSV.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "scholarship_id",
                "status",
                "fields_changed",
                "validation",
            ],
        )

        writer.writeheader()
        writer.writerows(csv_rows)

    md = f"""# Step 152.7C-5C-1C-2C Partial MongoDB Repair

Mode: {report.get("mode")}

MongoDB count before: {report.get("mongodb_count_before")}
MongoDB count after: {report.get("mongodb_count_after")}

Target scholarships:
- sch_hk_001
- sch_kr_001
- sch_tw_001

Research blocker excluded:
- sch_sg_001

Target validation passed:
{report.get("target_validation_passed")}

Target validation failed:
{report.get("target_validation_failed")}

All MongoDB validation passed:
{report.get("all_records_passed")}

All MongoDB validation failed:
{report.get("all_records_failed")}

Baseline compatibility:
{report.get("baseline_compatibility")}

MongoDB modified:
{report.get("mongodb_modified")}

Verified CSV modified:
NO

Baseline modified:
NO

Final status:
{report.get("status")}
"""

    REPORT_MD.write_text(md, encoding="utf-8")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually apply the approved MongoDB repairs.",
    )

    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY_RUN"

    print()
    print(
        "STEP 152.7C-5C-1C-2C "
        "SAFE PARTIAL MONGODB COMPATIBILITY REPAIR"
    )
    print()
    print(f"Mode: {mode}")
    print()

    client = None

    try:
        model = find_scholarship_schema()

        client, db = connect_database()

        collection = db["scholarships"]

        count_before = collection.count_documents({})

        print(f"MongoDB count before: {count_before}")

        if count_before != 18:
            raise RuntimeError(
                f"Expected 18 scholarships, found {count_before}. "
                "Stopping safely."
            )

        # ----------------------------------------------------
        # Validate target existence
        # ----------------------------------------------------

        target_docs = {}

        for scholarship_id in TARGET_IDS:
            docs = list(
                collection.find(
                    {"scholarship_id": scholarship_id}
                )
            )

            if len(docs) != 1:
                raise RuntimeError(
                    f"{scholarship_id} expected exactly once, "
                    f"found {len(docs)}."
                )

            target_docs[scholarship_id] = docs[0]

        blocker_docs = list(
            collection.find(
                {"scholarship_id": BLOCKER_ID}
            )
        )

        if len(blocker_docs) != 1:
            raise RuntimeError(
                f"{BLOCKER_ID} expected exactly once, "
                f"found {len(blocker_docs)}."
            )

        blocker_before = deepcopy(blocker_docs[0])

        print(f"Target records found: {len(target_docs)}")
        print(f"Research blocker excluded: {BLOCKER_ID}")
        print()

        # ----------------------------------------------------
        # Simulate
        # ----------------------------------------------------

        simulated_docs = {}

        target_failures = []

        for scholarship_id, original in target_docs.items():
            simulated = build_simulated_document(original)

            simulated_docs[scholarship_id] = simulated

            ok, error = validate_document(
                model,
                simulated,
            )

            if not ok:
                target_failures.append(
                    {
                        "scholarship_id": scholarship_id,
                        "error": error,
                    }
                )

        target_passed = (
            len(simulated_docs) - len(target_failures)
        )

        print("Simulated target validation:")
        print(f"Passed: {target_passed}")
        print(f"Failed: {len(target_failures)}")
        print()

        if target_failures:
            print("Simulation failures:")

            for failure in target_failures:
                print(
                    failure["scholarship_id"],
                    failure["error"],
                )

            raise RuntimeError(
                "Simulation validation failed. No writes allowed."
            )

        # ----------------------------------------------------
        # Baseline compatibility
        # ----------------------------------------------------

        baseline_passed, baseline_failed, baseline_failures = (
            validate_baseline(model)
        )

        baseline_compatibility = (
            "PASS" if baseline_failed == 0 else "FAIL"
        )

        print(
            f"Baseline records passed: {baseline_passed}"
        )
        print(
            f"Baseline records failed: {baseline_failed}"
        )
        print(
            f"Baseline compatibility: {baseline_compatibility}"
        )
        print()

        if baseline_failed:
            raise RuntimeError(
                "Baseline compatibility failed."
            )

        targets_report = []

        # ----------------------------------------------------
        # DRY RUN
        # ----------------------------------------------------

        if not args.apply:

            for scholarship_id in TARGET_IDS:

                if scholarship_id in {
                    "sch_hk_001",
                    "sch_kr_001",
                }:
                    fields_changed = [
                        "scholarship_status"
                    ]
                else:
                    fields_changed = [
                        "monthly_allowance",
                        "monthly_allowance_details",
                    ]

                targets_report.append(
                    {
                        "scholarship_id": scholarship_id,
                        "status": "SIMULATED",
                        "fields_changed": fields_changed,
                        "validation": "PASS",
                    }
                )

            report = {
                "step": "152.7C-5C-1C-2C",
                "mode": "DRY_RUN",
                "mongodb_count_before": count_before,
                "mongodb_count_after": count_before,
                "target_validation_passed": target_passed,
                "target_validation_failed": len(
                    target_failures
                ),
                "baseline_compatibility": (
                    baseline_compatibility
                ),
                "mongodb_modified": "NO",
                "research_blocker": BLOCKER_ID,
                "targets": targets_report,
                "status": "READY_TO_APPLY",
            }

            write_outputs(report)

            print("MongoDB modified: NO")
            print()
            print("DRY RUN STATUS:")
            print("READY_TO_APPLY")

            return

        # ----------------------------------------------------
        # APPLY MODE
        # ----------------------------------------------------

        backup_path, backup_count = create_backup(
            collection
        )

        print(f"Backup created: {backup_path}")
        print(f"Backup record count: {backup_count}")
        print()

        if backup_count != 18:
            raise RuntimeError(
                "Backup did not contain exactly 18 records. "
                "Stopping before write."
            )

        updates = {
            "sch_hk_001": {
                "$set": {
                    "scholarship_status": "CLOSED"
                }
            },

            "sch_kr_001": {
                "$set": {
                    "scholarship_status": "CLOSED"
                }
            },

            "sch_tw_001": {
                "$set": {
                    "monthly_allowance": None,
                    "monthly_allowance_details":
                        TAIWAN_ALLOWANCE_DETAILS,
                }
            },
        }

        modified_ids = []

        for scholarship_id, update in updates.items():

            result = collection.update_one(
                {"scholarship_id": scholarship_id},
                update,
            )

            if result.matched_count != 1:
                raise RuntimeError(
                    f"Unexpected matched_count for "
                    f"{scholarship_id}: "
                    f"{result.matched_count}"
                )

            modified_ids.append(scholarship_id)

        # ----------------------------------------------------
        # Verify blocker unchanged
        # ----------------------------------------------------

        blocker_after = collection.find_one(
            {"scholarship_id": BLOCKER_ID}
        )

        blocker_unchanged = (
            blocker_before == blocker_after
        )

        if not blocker_unchanged:
            raise RuntimeError(
                f"{BLOCKER_ID} changed unexpectedly."
            )

        # ----------------------------------------------------
        # Verify counts
        # ----------------------------------------------------

        count_after = collection.count_documents({})

        if count_after != 18:
            raise RuntimeError(
                f"MongoDB count changed unexpectedly: "
                f"{count_after}"
            )

        # ----------------------------------------------------
        # Validate target records after write
        # ----------------------------------------------------

        repaired_passed = 0
        repaired_failures = []

        for scholarship_id in TARGET_IDS:

            doc = collection.find_one(
                {"scholarship_id": scholarship_id}
            )

            ok, error = validate_document(
                model,
                doc,
            )

            if ok:
                repaired_passed += 1
            else:
                repaired_failures.append(
                    {
                        "scholarship_id": scholarship_id,
                        "error": error,
                    }
                )

        # ----------------------------------------------------
        # Validate all 18 records
        # ----------------------------------------------------

        all_records = list(collection.find({}))

        all_passed = 0
        all_failures = []

        for doc in all_records:

            ok, error = validate_document(
                model,
                doc,
            )

            if ok:
                all_passed += 1
            else:
                all_failures.append(
                    {
                        "scholarship_id":
                            doc.get("scholarship_id"),
                        "error": error,
                    }
                )

        print("POST-REPAIR SCHEMA VALIDATION")
        print()

        print(
            f"MongoDB records checked: "
            f"{len(all_records)}"
        )
        print(
            f"MongoDB records passed: {all_passed}"
        )
        print(
            f"MongoDB records failed: "
            f"{len(all_failures)}"
        )
        print()

        print(
            f"Target repaired records passed: "
            f"{repaired_passed}"
        )
        print(
            f"Target repaired records failed: "
            f"{len(repaired_failures)}"
        )
        print()

        print(
            f"{BLOCKER_ID} unchanged: "
            f"{'YES' if blocker_unchanged else 'NO'}"
        )

        # Expected post-repair state:
        # 17 valid + sch_sg_001 research blocker

        remaining_ids = {
            item["scholarship_id"]
            for item in all_failures
        }

        expected_remaining = {BLOCKER_ID}

        if (
            repaired_failures
            or all_passed != 17
            or len(all_failures) != 1
            or remaining_ids != expected_remaining
        ):
            final_status = (
                "POST_REPAIR_VALIDATION_REQUIRES_REVIEW"
            )
        else:
            final_status = (
                "PARTIAL_REPAIR_APPLIED_PENDING_"
                "SINGA_RESOLUTION"
            )

        for scholarship_id in TARGET_IDS:

            if scholarship_id in {
                "sch_hk_001",
                "sch_kr_001",
            }:
                fields_changed = [
                    "scholarship_status"
                ]
            else:
                fields_changed = [
                    "monthly_allowance",
                    "monthly_allowance_details",
                ]

            targets_report.append(
                {
                    "scholarship_id": scholarship_id,
                    "status": "APPLIED",
                    "fields_changed": fields_changed,
                    "validation": (
                        "PASS"
                        if scholarship_id
                        not in {
                            x["scholarship_id"]
                            for x in repaired_failures
                        }
                        else "FAIL"
                    ),
                }
            )

        report = {
            "step": "152.7C-5C-1C-2C",
            "mode": "APPLY",
            "backup_path": str(backup_path),
            "backup_record_count": backup_count,
            "mongodb_count_before": count_before,
            "mongodb_count_after": count_after,
            "modified_ids": modified_ids,
            "research_blocker": BLOCKER_ID,
            "research_blocker_unchanged": (
                blocker_unchanged
            ),
            "target_validation_passed": (
                repaired_passed
            ),
            "target_validation_failed": len(
                repaired_failures
            ),
            "all_records_passed": all_passed,
            "all_records_failed": len(
                all_failures
            ),
            "remaining_failures": all_failures,
            "baseline_compatibility": (
                baseline_compatibility
            ),
            "mongodb_modified": "YES",
            "verified_csv_modified": "NO",
            "baseline_modified": "NO",
            "targets": targets_report,
            "status": final_status,
        }

        write_outputs(report)

        print()
        print(f"MongoDB count before: {count_before}")
        print(f"MongoDB count after: {count_after}")
        print()
        print("MongoDB modified: YES")
        print("Verified CSV modified: NO")
        print("Baseline modified: NO")
        print()
        print(
            "STEP 152.7C-5C-1C-2C STATUS:"
        )
        print(final_status)

    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()