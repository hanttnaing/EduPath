from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.app.schemas import ScholarshipResponse


CLEANED_FILE = ROOT / "data" / "cleaned" / "scholarships.json"

BASELINE_FILE = (
    ROOT
    / "backups"
    / "baseline_151_10"
    / "scholarships.json"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "analysis"
    / "152_7c5c1c2d_post_repair_sync_report.json"
)

DOC_FILE = (
    ROOT
    / "docs"
    / "152_7c5c1c2d_post_repair_sync.md"
)

TARGET_IDS = [
    "sch_hk_001",
    "sch_kr_001",
    "sch_tw_001",
]

BLOCKER_ID = "sch_sg_001"


def validate_record(record: dict[str, Any]) -> tuple[bool, str | None]:
    try:
        if hasattr(ScholarshipResponse, "model_validate"):
            ScholarshipResponse.model_validate(record)
        else:
            ScholarshipResponse.parse_obj(record)

        return True, None

    except Exception as exc:
        return False, str(exc)


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise RuntimeError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise RuntimeError(f"{path} must contain a JSON list.")

    return data


def index_records(records):
    index = {}

    for record in records:
        scholarship_id = record.get("scholarship_id")

        if not scholarship_id:
            raise RuntimeError(
                "Record missing scholarship_id."
            )

        if scholarship_id in index:
            raise RuntimeError(
                f"Duplicate scholarship_id: {scholarship_id}"
            )

        index[scholarship_id] = record

    return index


def connect_mongodb():
    load_dotenv(ROOT / ".env", override=True)

    uri = os.getenv("MONGODB_URI")

    if not uri:
        raise RuntimeError(
            "MONGODB_URI missing from .env"
        )

    database_name = (
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
        raise RuntimeError(
            "MongoDB ping failed."
        )

    return client, client[database_name]


def clean_mongo_doc(doc):
    result = deepcopy(doc)
    result.pop("_id", None)
    return result


def patch_repaired_fields(
    cleaned_record,
    mongo_record,
):
    scholarship_id = cleaned_record["scholarship_id"]

    updated = deepcopy(cleaned_record)

    if scholarship_id in {
        "sch_hk_001",
        "sch_kr_001",
    }:
        updated["scholarship_status"] = (
            mongo_record.get("scholarship_status")
        )

    elif scholarship_id == "sch_tw_001":

        updated["monthly_allowance"] = (
            mongo_record.get("monthly_allowance")
        )

        updated["monthly_allowance_details"] = (
            deepcopy(
                mongo_record.get(
                    "monthly_allowance_details"
                )
            )
        )

    else:
        raise RuntimeError(
            f"Unexpected repair target: {scholarship_id}"
        )

    return updated


def validate_collection(records):
    passed = 0
    failures = []

    for record in records:

        ok, error = validate_record(record)

        if ok:
            passed += 1
        else:
            failures.append(
                {
                    "scholarship_id":
                        record.get("scholarship_id"),
                    "error": error,
                }
            )

    return passed, failures


def write_report(report):
    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    DOC_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    md = f"""# Step 152.7C-5C-1C-2D

## Post-Repair Dataset Sync

Mode: {report["mode"]}

Cleaned scholarship count:
{report["cleaned_count"]}

MongoDB scholarship count:
{report["mongodb_count"]}

Records synchronized:
{report["records_synchronized"]}

Schema validation passed:
{report["schema_passed"]}

Schema validation failed:
{report["schema_failed"]}

Remaining blocker:
{report["remaining_blocker"]}

Baseline compatibility:
{report["baseline_compatibility"]}

Cleaned dataset modified:
{report["cleaned_modified"]}

MongoDB modified:
NO

Status:
{report["status"]}
"""

    DOC_FILE.write_text(
        md,
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
    )

    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY_RUN"

    print()
    print(
        "STEP 152.7C-5C-1C-2D "
        "POST-REPAIR DATASET SYNC"
    )
    print()
    print(f"Mode: {mode}")
    print()

    client = None

    try:
        cleaned = load_json_list(
            CLEANED_FILE
        )

        baseline = load_json_list(
            BASELINE_FILE
        )

        if len(cleaned) != 18:
            raise RuntimeError(
                "Expected canonical cleaned dataset "
                f"to contain 18 records, found {len(cleaned)}."
            )

        cleaned_index = index_records(cleaned)

        for scholarship_id in (
            TARGET_IDS + [BLOCKER_ID]
        ):
            if scholarship_id not in cleaned_index:
                raise RuntimeError(
                    f"{scholarship_id} missing "
                    "from cleaned dataset."
                )

        blocker_before = deepcopy(
            cleaned_index[BLOCKER_ID]
        )

        client, db = connect_mongodb()

        collection = db["scholarships"]

        mongodb_count = (
            collection.count_documents({})
        )

        print(
            f"MongoDB scholarship count: "
            f"{mongodb_count}"
        )

        if mongodb_count != 18:
            raise RuntimeError(
                f"Expected 18 MongoDB scholarships, "
                f"found {mongodb_count}."
            )

        mongo_targets = {}

        for scholarship_id in TARGET_IDS:

            docs = list(
                collection.find(
                    {
                        "scholarship_id":
                            scholarship_id
                    }
                )
            )

            if len(docs) != 1:
                raise RuntimeError(
                    f"{scholarship_id} expected once "
                    f"in MongoDB, found {len(docs)}."
                )

            mongo_targets[
                scholarship_id
            ] = clean_mongo_doc(
                docs[0]
            )

        simulated = deepcopy(cleaned)
        simulated_index = index_records(
            simulated
        )

        changes = []

        for scholarship_id in TARGET_IDS:

            old_record = deepcopy(
                simulated_index[
                    scholarship_id
                ]
            )

            new_record = patch_repaired_fields(
                old_record,
                mongo_targets[
                    scholarship_id
                ],
            )

            simulated_index[
                scholarship_id
            ].clear()

            simulated_index[
                scholarship_id
            ].update(new_record)

            if scholarship_id in {
                "sch_hk_001",
                "sch_kr_001",
            }:
                changes.append(
                    {
                        "scholarship_id":
                            scholarship_id,
                        "field":
                            "scholarship_status",
                        "old_value":
                            old_record.get(
                                "scholarship_status"
                            ),
                        "new_value":
                            new_record.get(
                                "scholarship_status"
                            ),
                    }
                )

            else:
                changes.append(
                    {
                        "scholarship_id":
                            scholarship_id,
                        "field":
                            "monthly_allowance",
                        "old_value":
                            old_record.get(
                                "monthly_allowance"
                            ),
                        "new_value":
                            new_record.get(
                                "monthly_allowance"
                            ),
                    }
                )

                changes.append(
                    {
                        "scholarship_id":
                            scholarship_id,
                        "field":
                            "monthly_allowance_details",
                        "old_value":
                            old_record.get(
                                "monthly_allowance_details"
                            ),
                        "new_value":
                            new_record.get(
                                "monthly_allowance_details"
                            ),
                    }
                )

        blocker_after = (
            simulated_index[
                BLOCKER_ID
            ]
        )

        if blocker_before != blocker_after:
            raise RuntimeError(
                "sch_sg_001 changed unexpectedly."
            )

        passed, failures = (
            validate_collection(simulated)
        )

        print()
        print("SIMULATED CLEANED DATASET")
        print()
        print(
            f"Records checked: "
            f"{len(simulated)}"
        )
        print(
            f"Schema passed: {passed}"
        )
        print(
            f"Schema failed: "
            f"{len(failures)}"
        )

        failure_ids = {
            item["scholarship_id"]
            for item in failures
        }

        if (
            passed != 17
            or len(failures) != 1
            or failure_ids != {BLOCKER_ID}
        ):
            raise RuntimeError(
                "Unexpected schema validation "
                "result after simulation."
            )

        baseline_passed, baseline_failures = (
            validate_collection(baseline)
        )

        baseline_status = (
            "PASS"
            if baseline_passed == 12
            and not baseline_failures
            else "FAIL"
        )

        print(
            f"Baseline compatibility: "
            f"{baseline_status}"
        )

        if baseline_status != "PASS":
            raise RuntimeError(
                "Baseline compatibility failed."
            )

        backup_path = None

        if args.apply:

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            backup_dir = (
                ROOT
                / "backups"
                / f"pre_152_7c5c1c2d_{timestamp}"
            )

            backup_dir.mkdir(
                parents=True,
                exist_ok=False,
            )

            backup_path = (
                backup_dir
                / "scholarships_cleaned_before_sync.json"
            )

            shutil.copy2(
                CLEANED_FILE,
                backup_path,
            )

            CLEANED_FILE.write_text(
                json.dumps(
                    simulated,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            cleaned_modified = "YES"

            status = (
                "SYNC_APPLIED_API_VALIDATION_REQUIRED"
            )

        else:

            cleaned_modified = "NO"

            status = "READY_TO_SYNC"

        report = {
            "step":
                "152.7C-5C-1C-2D",
            "mode":
                mode,
            "cleaned_count":
                len(cleaned),
            "mongodb_count":
                mongodb_count,
            "records_synchronized":
                3,
            "changes":
                changes,
            "schema_passed":
                passed,
            "schema_failed":
                len(failures),
            "schema_failures":
                failures,
            "remaining_blocker":
                BLOCKER_ID,
            "blocker_unchanged":
                True,
            "baseline_compatibility":
                baseline_status,
            "backup_path":
                str(backup_path)
                if backup_path
                else None,
            "cleaned_modified":
                cleaned_modified,
            "mongodb_modified":
                "NO",
            "status":
                status,
        }

        write_report(report)

        print()
        print(
            f"sch_sg_001 unchanged: YES"
        )
        print(
            f"Cleaned dataset modified: "
            f"{cleaned_modified}"
        )
        print(
            "MongoDB modified: NO"
        )
        print()
        print("STEP STATUS:")
        print(status)

    finally:

        if client is not None:
            client.close()


if __name__ == "__main__":
    main()