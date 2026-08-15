from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# EduPath - Step 152.7C-5
# Post-Import Dataset Synchronisation & API Validation
#
# This script reads MongoDB but never writes to it. The only data
# file it synchronises is the project's existing cleaned scholarship
# dataset. Historical, staging, baseline, and Batch 01 files remain
# untouched.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BASELINE_SCHOLARSHIPS = (
    PROJECT_ROOT / "backups" / "baseline_151_10" / "scholarships.json"
)
CLEANED_SCHOLARSHIPS = (
    PROJECT_ROOT / "data" / "cleaned" / "scholarships.json"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7c5_post_import_sync_report.json"
)

EXPECTED_MONGODB_COUNT = 18
EXPECTED_BASELINE_COUNT = 12
EXPECTED_NEW_COUNT = 6
COLLECTION_NAME = "scholarships"

NEW_IDS = (
    "sch_hk_001",
    "sch_my_001",
    "sch_sg_001",
    "sch_kr_001",
    "sch_tw_001",
    "sch_th_001",
)

NEW_ID_BY_COUNTRY = {
    "country_hk": "sch_hk_001",
    "country_my": "sch_my_001",
    "country_sg": "sch_sg_001",
    "country_kr": "sch_kr_001",
    "country_tw": "sch_tw_001",
    "country_th": "sch_th_001",
}

DEFAULT_API_BASE_URL = os.getenv(
    "EDUPATH_API_BASE_URL",
    "http://127.0.0.1:8002",
).rstrip("/")

DATE_FIELDS = {
    "application_opening_date",
    "application_deadline",
    "collected_at",
    "last_verified_at",
}


def load_json_list(path: Path) -> list[dict[str, Any]]:
    """Load a required JSON list without changing it."""

    if not path.is_file():
        raise FileNotFoundError(f"Required dataset was not found: {path}")

    with path.open("r", encoding="utf-8-sig") as source_file:
        value = json.load(source_file)

    if not isinstance(value, list) or not all(
        isinstance(record, dict) for record in value
    ):
        raise ValueError(f"Expected a JSON list of objects: {path}")

    return value


def json_safe(value: Any) -> Any:
    """Convert BSON-adjacent values to deterministic JSON values."""

    if isinstance(value, dict):
        return {str(key): json_safe(child) for key, child in value.items()}

    if isinstance(value, (list, tuple)):
        return [json_safe(child) for child in value]

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def write_json_atomic(path: Path, value: Any) -> None:
    """Replace a JSON file only after its complete replacement is written."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_name = temporary_file.name
            json.dump(
                json_safe(value),
                temporary_file,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            temporary_file.write("\n")

        os.replace(temporary_name, path)
        temporary_name = None
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


def cleaned_schema(records: list[dict[str, Any]]) -> list[str]:
    """Return the established cleaned scholarship field order."""

    if not records:
        raise ValueError("The existing cleaned scholarship dataset is empty.")

    fields = list(records[0])
    if not fields or "scholarship_id" not in fields:
        raise ValueError("The existing cleaned scholarship schema is invalid.")

    expected = set(fields)
    inconsistent = [
        record.get("scholarship_id", f"row_{index}")
        for index, record in enumerate(records, start=1)
        if set(record) != expected
    ]
    if inconsistent:
        raise ValueError(
            "The existing cleaned scholarship dataset has inconsistent schemas: "
            + ", ".join(map(str, inconsistent))
        )

    return fields


def normalise_date_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        text = value.strip()
        match = re.match(r"^(\d{4}-\d{2}-\d{2})", text)
        return match.group(1) if match else text
    return value


def project_clean_record(
    document: dict[str, Any],
    schema_fields: list[str],
) -> dict[str, Any]:
    """Project a live document onto the established cleaned-data schema."""

    record: dict[str, Any] = {}
    for field in schema_fields:
        value = document.get(field)
        if field in DATE_FIELDS:
            value = normalise_date_value(value)
        record[field] = json_safe(value)
    return record


def canonical(value: Any, field: str | None = None) -> Any:
    """Normalise values used in baseline-preservation comparisons."""

    if field in DATE_FIELDS:
        return normalise_date_value(value)
    if isinstance(value, dict):
        return {key: canonical(child, key) for key, child in value.items()}
    if isinstance(value, list):
        return [canonical(child) for child in value]
    return json_safe(value)


def duplicate_values(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def normalise_name(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().casefold())


def request_json(url: str, timeout: float) -> tuple[int, Any]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "EduPath-Step-152.7C-5-Validator",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return response.status, json.loads(raw) if raw.strip() else None


def api_check(
    base_url: str,
    path: str,
    timeout: float,
) -> tuple[dict[str, Any], Any]:
    url = f"{base_url}{path}"
    try:
        status_code, payload = request_json(url, timeout)
        passed = status_code == 200
        return (
            {
                "endpoint": path,
                "url": url,
                "status": "PASS" if passed else "FAIL",
                "http_status": status_code,
                "message": "Endpoint returned JSON." if passed else "Unexpected HTTP status.",
            },
            payload,
        )
    except Exception as error:
        return (
            {
                "endpoint": path,
                "url": url,
                "status": "FAIL",
                "http_status": getattr(error, "code", None),
                "message": str(error),
            },
            None,
        )


def validate_api(base_url: str, timeout: float) -> dict[str, Any]:
    """Validate the running API, or return SKIPPED if it is unreachable."""

    countries_path = "/api/countries?limit=100"
    first_check, countries_payload = api_check(base_url, countries_path, timeout)

    if first_check["status"] == "FAIL" and first_check["http_status"] is None:
        skipped_paths = [
            countries_path,
            "/api/scholarships?limit=100",
            *[
                f"/api/scholarships?country_id={country_id}&limit=100"
                for country_id in NEW_ID_BY_COUNTRY
            ],
            "/api/analysis/dashboard",
        ]
        return {
            "status": "SKIPPED",
            "base_url": base_url,
            "reason": "Backend API is not reachable; no server was started or stopped.",
            "probe_error": first_check["message"],
            "endpoints": [
                {"endpoint": path, "status": "SKIPPED"} for path in skipped_paths
            ],
        }

    checks = [first_check]
    valid_country_ids = {
        str(item.get("country_id", "")).strip()
        for item in (
            countries_payload.get("items", [])
            if isinstance(countries_payload, dict)
            else []
        )
        if isinstance(item, dict)
    }
    missing_api_countries = sorted(set(NEW_ID_BY_COUNTRY) - valid_country_ids)
    if missing_api_countries:
        first_check["status"] = "FAIL"
        first_check["message"] = (
            "Required countries missing: " + ", ".join(missing_api_countries)
        )

    scholarships_path = "/api/scholarships?limit=100"
    scholarship_check, scholarship_payload = api_check(
        base_url, scholarships_path, timeout
    )
    if scholarship_check["status"] == "PASS":
        total = (
            scholarship_payload.get("total")
            if isinstance(scholarship_payload, dict)
            else None
        )
        items = (
            scholarship_payload.get("items", [])
            if isinstance(scholarship_payload, dict)
            else []
        )
        ids = {
            item.get("scholarship_id")
            for item in items
            if isinstance(item, dict)
        }
        missing_ids = sorted(set(NEW_IDS) - ids)
        if total != EXPECTED_MONGODB_COUNT or missing_ids:
            scholarship_check["status"] = "FAIL"
            scholarship_check["message"] = (
                f"Expected total 18 and all new IDs; total={total}, "
                f"missing_ids={missing_ids}."
            )
        else:
            scholarship_check["record_count"] = len(items)
            scholarship_check["total"] = total
    checks.append(scholarship_check)

    for country_id, expected_id in NEW_ID_BY_COUNTRY.items():
        query = urllib.parse.urlencode({"country_id": country_id, "limit": 100})
        path = f"/api/scholarships?{query}"
        check, payload = api_check(base_url, path, timeout)
        if check["status"] == "PASS":
            items = payload.get("items", []) if isinstance(payload, dict) else []
            ids = {
                item.get("scholarship_id")
                for item in items
                if isinstance(item, dict)
            }
            wrong_countries = [
                item.get("scholarship_id")
                for item in items
                if isinstance(item, dict) and item.get("country_id") != country_id
            ]
            if expected_id not in ids or wrong_countries:
                check["status"] = "FAIL"
                check["message"] = (
                    f"Expected {expected_id}; wrong-country records={wrong_countries}."
                )
            else:
                check["record_count"] = len(items)
                check["expected_id"] = expected_id
        checks.append(check)

    dashboard_path = "/api/analysis/dashboard"
    dashboard_check, dashboard_payload = api_check(
        base_url, dashboard_path, timeout
    )
    if dashboard_check["status"] == "PASS" and not (
        isinstance(dashboard_payload, dict) and dashboard_payload
    ):
        dashboard_check["status"] = "FAIL"
        dashboard_check["message"] = "Dashboard returned an empty or invalid payload."
    checks.append(dashboard_check)

    return {
        "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
        "base_url": base_url,
        "endpoints": checks,
    }


def print_terminal_report(summary: dict[str, Any], api_status: str) -> None:
    print("=" * 72)
    print("STEP 152.7C-5 POST-IMPORT DATASET SYNCHRONISATION")
    print("=" * 72)
    print(f"MongoDB scholarships:       {summary['mongodb_scholarships']}")
    print(f"Cleaned scholarships:       {summary['cleaned_scholarships']}")
    print(f"Baseline scholarships:      {summary['baseline_scholarships']}")
    print(f"New Batch 01 records:       {summary['new_batch_01_records']}")
    print(f"Old records preserved:      {summary['old_records_preserved']}")
    print(f"New IDs found:              {summary['new_ids_found']}")
    print(f"Duplicate IDs:              {summary['duplicate_ids']}")
    print(f"Duplicate names:            {summary['duplicate_names']}")
    print(f"Invalid country references: {summary['invalid_country_references']}")
    print(f"Dataset synchronisation:    {summary['dataset_synchronisation']}")
    print(f"API validation:             {api_status}")
    print(f"Report:                     {REPORT_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synchronise cleaned scholarships from live EduPath MongoDB."
    )
    parser.add_argument(
        "--api-base-url",
        default=DEFAULT_API_BASE_URL,
        help="Running backend base URL (the script never starts the server).",
    )
    parser.add_argument(
        "--api-timeout",
        type=float,
        default=3.0,
        help="Seconds to wait when probing each API endpoint.",
    )
    args = parser.parse_args()

    baseline = load_json_list(BASELINE_SCHOLARSHIPS)
    existing_cleaned = load_json_list(CLEANED_SCHOLARSHIPS)
    schema_fields = cleaned_schema(existing_cleaned)

    if len(baseline) != EXPECTED_BASELINE_COUNT:
        raise RuntimeError(
            f"Immutable baseline must contain 12 scholarships; found {len(baseline)}."
        )

    # Import the project's existing connection configuration only after the
    # project root is importable. No alternate client/database is created.
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from backend.app.database import close_database, get_database, ping_database

    try:
        ping_database()
        database = get_database()
        live_documents = list(database[COLLECTION_NAME].find({}))
        country_documents = list(
            database["countries"].find({}, {"_id": 0, "country_id": 1})
        )

        live_count = len(live_documents)
        if live_count != EXPECTED_MONGODB_COUNT:
            raise RuntimeError(
                f"Live MongoDB must contain exactly 18 scholarships; found {live_count}."
            )

        live_by_id = {
            str(document.get("scholarship_id", "")).strip(): document
            for document in live_documents
        }
        live_ids = [
            str(document.get("scholarship_id", "")).strip()
            for document in live_documents
        ]
        duplicate_ids = duplicate_values(live_ids)
        duplicate_names = duplicate_values(
            [normalise_name(document.get("scholarship_name")) for document in live_documents]
        )
        new_ids_found = sorted(set(NEW_IDS) & set(live_ids))
        missing_new_ids = sorted(set(NEW_IDS) - set(live_ids))

        valid_country_ids = {
            str(document.get("country_id", "")).strip()
            for document in country_documents
            if str(document.get("country_id", "")).strip()
        }
        invalid_country_references = sorted(
            {
                str(document.get("country_id", "")).strip()
                for document in live_documents
                if str(document.get("country_id", "")).strip()
                not in valid_country_ids
            }
        )

        baseline_ids = {
            str(record.get("scholarship_id", "")).strip() for record in baseline
        }
        missing_baseline_ids = sorted(baseline_ids - set(live_ids))
        changed_baseline_ids: list[str] = []
        for baseline_record in baseline:
            scholarship_id = str(baseline_record.get("scholarship_id", "")).strip()
            live_record = live_by_id.get(scholarship_id)
            if live_record is None:
                continue
            if any(
                canonical(baseline_record.get(field), field)
                != canonical(live_record.get(field), field)
                for field in schema_fields
            ):
                changed_baseline_ids.append(scholarship_id)

        old_records_preserved = not missing_baseline_ids and not changed_baseline_ids
        validation_errors: list[str] = []
        if duplicate_ids:
            validation_errors.append(f"Duplicate scholarship IDs: {duplicate_ids}")
        if duplicate_names:
            validation_errors.append(f"Duplicate scholarship names: {duplicate_names}")
        if invalid_country_references:
            validation_errors.append(
                f"Invalid country references: {invalid_country_references}"
            )
        if missing_new_ids:
            validation_errors.append(f"Missing new IDs: {missing_new_ids}")
        if not old_records_preserved:
            validation_errors.append(
                f"Baseline preservation failed; missing={missing_baseline_ids}, "
                f"changed={changed_baseline_ids}"
            )

        if validation_errors:
            raise RuntimeError("; ".join(validation_errors))

        cleaned_records = [
            project_clean_record(document, schema_fields)
            for document in sorted(
                live_documents,
                key=lambda item: str(item.get("scholarship_id", "")),
            )
        ]
        if len(cleaned_records) != EXPECTED_MONGODB_COUNT:
            raise RuntimeError("Projected cleaned scholarship count is not 18.")

        # This is the sole dataset mutation performed by this script.
        write_json_atomic(CLEANED_SCHOLARSHIPS, cleaned_records)

        # Read back the file so the report describes the on-disk result.
        synced_cleaned = load_json_list(CLEANED_SCHOLARSHIPS)
        synced_ids = [str(record.get("scholarship_id", "")).strip() for record in synced_cleaned]
        sync_pass = (
            len(synced_cleaned) == EXPECTED_MONGODB_COUNT
            and synced_cleaned == cleaned_records
            and not duplicate_values(synced_ids)
        )

        api_validation = validate_api(args.api_base_url.rstrip("/"), args.api_timeout)
        summary = {
            "mongodb_scholarships": live_count,
            "cleaned_scholarships": len(synced_cleaned),
            "baseline_scholarships": len(baseline),
            "new_batch_01_records": EXPECTED_NEW_COUNT,
            "old_records_preserved": "PASS" if old_records_preserved else "FAIL",
            "new_ids_found": len(new_ids_found),
            "duplicate_ids": len(duplicate_ids),
            "duplicate_names": len(duplicate_names),
            "invalid_country_references": len(invalid_country_references),
            "dataset_synchronisation": "PASS" if sync_pass else "FAIL",
        }

        report = {
            "step": "152.7C-5",
            "title": "Post-Import Dataset Synchronisation & API Validation",
            "status": "PASS" if sync_pass else "FAIL",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_of_truth": "MongoDB",
            "collection": COLLECTION_NAME,
            "cleaned_dataset": str(CLEANED_SCHOLARSHIPS),
            "immutable_baseline": str(BASELINE_SCHOLARSHIPS),
            "summary": summary,
            "validation": {
                "new_ids_expected": list(NEW_IDS),
                "new_ids_found": new_ids_found,
                "missing_new_ids": missing_new_ids,
                "duplicate_id_values": duplicate_ids,
                "duplicate_name_values": duplicate_names,
                "valid_country_ids_count": len(valid_country_ids),
                "invalid_country_ids": invalid_country_references,
                "baseline_ids_missing": missing_baseline_ids,
                "baseline_ids_changed": changed_baseline_ids,
                "cleaned_schema_fields": schema_fields,
            },
            "api_validation": api_validation,
            "protected_files_modified": False,
            "mongodb_modified": False,
        }
        write_json_atomic(REPORT_PATH, report)
        print_terminal_report(summary, api_validation["status"])

        if not sync_pass:
            raise RuntimeError("Cleaned dataset read-back validation failed.")
    finally:
        close_database()


if __name__ == "__main__":
    main()
