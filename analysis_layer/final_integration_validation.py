from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


# ============================================================
# EduPath
# Step 151.10
# Final Integration & Validation
# ============================================================

STEP_NAME = "151.10"
STEP_TITLE = "Final Integration & Validation"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
PLANNING_DIR = PROJECT_ROOT / "planning"
DOCS_DIR = PROJECT_ROOT / "docs"

OUTPUT_JSON = ANALYSIS_DIR / "151_10_final_integration_validation.json"
OUTPUT_CSV = PLANNING_DIR / "39_final_integration_validation.csv"
OUTPUT_MD = DOCS_DIR / "151_10_final_integration_validation_report.md"

FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_SRC = FRONTEND_DIR / "src"

API_JS_FILE = FRONTEND_SRC / "api.js"
APP_FILE = FRONTEND_SRC / "App.jsx"
ANALYSIS_DASHBOARD_FILE = FRONTEND_SRC / "AnalysisDashboard.jsx"
ANALYSIS_MAIN_FILE = FRONTEND_SRC / "analysis-main.jsx"
ANALYSIS_HTML_FILE = FRONTEND_DIR / "analysis.html"

DEFAULT_API_BASE_URL = os.getenv(
    "EDUPATH_API_BASE_URL",
    "http://127.0.0.1:8002",
).rstrip("/")


# Current validated baseline.
# Higher values are allowed later if the dataset expands.
BASELINE_MINIMUMS = {
    "countries": 7,
    "japan_universities": 16,
    "programs": 36,
    "scholarships": 12,
}


# ============================================================
# Utility
# ============================================================

def divider(char: str = "=", width: int = 78) -> str:
    return char * width


def ensure_output_directories() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def make_result(
    name: str,
    status: str,
    message: str,
    evidence: Any = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "message": message,
        "evidence": evidence,
    }


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def extract_items(payload: Any) -> list[Any]:
    """
    Supports:
        [...]
        {"items": [...]}
        {"data": [...]}
        {"results": [...]}
    """

    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    for key in ("items", "data", "results"):
        value = payload.get(key)

        if isinstance(value, list):
            return value

    return []


def extract_total(payload: Any) -> int:
    if isinstance(payload, list):
        return len(payload)

    if isinstance(payload, dict):
        total = payload.get("total")

        if isinstance(total, int):
            return total

        items = extract_items(payload)
        return len(items)

    return 0


def recursively_collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()

    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(recursively_collect_keys(child))

    elif isinstance(value, list):
        for child in value:
            keys.update(recursively_collect_keys(child))

    return keys


# ============================================================
# HTTP
# ============================================================

def request_json(
    url: str,
    timeout: int = 15,
) -> tuple[int, Any, dict[str, str]]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "EduPath-Step-151.10-Validator",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            status_code = response.status
            headers = {
                key.lower(): value
                for key, value in response.headers.items()
            }

            raw = response.read().decode("utf-8")

            if not raw.strip():
                payload = None
            else:
                payload = json.loads(raw)

            return status_code, payload, headers

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {error.code} for {url}\n{body}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Unable to connect to {url}: {error.reason}"
        ) from error

    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Endpoint returned invalid JSON: {url}"
        ) from error


def test_cors(
    base_url: str,
    frontend_origin: str,
) -> dict[str, Any]:

    url = f"{base_url}/api/analysis/dashboard"

    request = urllib.request.Request(
        url,
        method="OPTIONS",
        headers={
            "Origin": frontend_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            headers = {
                key.lower(): value
                for key, value in response.headers.items()
            }

            allowed_origin = headers.get(
                "access-control-allow-origin"
            )

            allowed_methods = headers.get(
                "access-control-allow-methods"
            )

            if not allowed_origin:
                return make_result(
                    "CORS configuration",
                    "WARNING",
                    "API responded, but Access-Control-Allow-Origin was not detected.",
                    {
                        "frontend_origin": frontend_origin,
                        "response_status": response.status,
                    },
                )

            return make_result(
                "CORS configuration",
                "PASS",
                "Backend CORS configuration responded successfully.",
                {
                    "frontend_origin": frontend_origin,
                    "allowed_origin": allowed_origin,
                    "allowed_methods": allowed_methods,
                },
            )

    except Exception as error:
        return make_result(
            "CORS configuration",
            "WARNING",
            f"Unable to verify browser CORS preflight: {error}",
        )


# ============================================================
# API endpoint tests
# ============================================================

def validate_collection_endpoint(
    name: str,
    url: str,
    minimum_count: int,
) -> tuple[dict[str, Any], Any]:

    try:
        status_code, payload, _ = request_json(url)

        count = extract_total(payload)

        if status_code != 200:
            return (
                make_result(
                    name,
                    "FAIL",
                    f"Unexpected HTTP status {status_code}.",
                    {
                        "url": url,
                        "count": count,
                    },
                ),
                payload,
            )

        if count < minimum_count:
            return (
                make_result(
                    name,
                    "FAIL",
                    (
                        f"Endpoint returned {count} records, "
                        f"below validated baseline of {minimum_count}."
                    ),
                    {
                        "url": url,
                        "count": count,
                        "minimum_expected": minimum_count,
                    },
                ),
                payload,
            )

        return (
            make_result(
                name,
                "PASS",
                f"Endpoint returned {count} records.",
                {
                    "url": url,
                    "count": count,
                    "minimum_expected": minimum_count,
                },
            ),
            payload,
        )

    except Exception as error:
        return (
            make_result(
                name,
                "FAIL",
                str(error),
                {"url": url},
            ),
            None,
        )


def validate_countries(
    base_url: str,
) -> tuple[dict[str, Any], Any]:

    result, payload = validate_collection_endpoint(
        "Countries API",
        f"{base_url}/api/countries?limit=100",
        BASELINE_MINIMUMS["countries"],
    )

    if result["status"] != "PASS":
        return result, payload

    items = extract_items(payload)

    japan_found = False

    for item in items:
        if not isinstance(item, dict):
            continue

        country_id = str(
            item.get("country_id", "")
        ).lower()

        country_name = str(
            item.get("country_name", "")
        ).lower()

        if (
            country_id == "country_jp"
            or country_name == "japan"
        ):
            japan_found = True
            break

    if not japan_found:
        return (
            make_result(
                "Countries API",
                "FAIL",
                "Countries endpoint works but Japan was not found.",
                result.get("evidence"),
            ),
            payload,
        )

    result["message"] += " Japan record detected."

    return result, payload


def validate_dashboard_endpoint(
    base_url: str,
) -> tuple[dict[str, Any], Any]:

    url = f"{base_url}/api/analysis/dashboard"

    try:
        status_code, payload, _ = request_json(url)

        if status_code != 200:
            return (
                make_result(
                    "Analysis Dashboard API",
                    "FAIL",
                    f"Unexpected HTTP status {status_code}.",
                    {"url": url},
                ),
                payload,
            )

        if not isinstance(payload, dict):
            return (
                make_result(
                    "Analysis Dashboard API",
                    "FAIL",
                    "Dashboard endpoint did not return a JSON object.",
                    {
                        "url": url,
                        "payload_type": type(payload).__name__,
                    },
                ),
                payload,
            )

        if not payload:
            return (
                make_result(
                    "Analysis Dashboard API",
                    "FAIL",
                    "Dashboard endpoint returned an empty object.",
                    {"url": url},
                ),
                payload,
            )

        keys = recursively_collect_keys(payload)

        concept_groups = {
            "dataset": {
                "dataset",
                "datasets",
                "overview",
                "counts",
                "universities",
                "programs",
                "scholarships",
            },
            "analysis": {
                "analysis",
                "insights",
                "charts",
                "visualizations",
                "kpis",
                "metrics",
            },
            "algorithm": {
                "algorithm",
                "performance",
                "recommendation",
                "validation",
            },
        }

        detected_groups: list[str] = []

        for group_name, candidates in concept_groups.items():
            if keys.intersection(candidates):
                detected_groups.append(group_name)

        status = "PASS"

        message = (
            "Dashboard API returned a non-empty analytical dataset."
        )

        if len(detected_groups) < 2:
            status = "WARNING"
            message += (
                " Payload is valid, but only limited expected "
                "analysis section names were detected."
            )

        return (
            make_result(
                "Analysis Dashboard API",
                status,
                message,
                {
                    "url": url,
                    "detected_groups": detected_groups,
                    "top_level_keys": sorted(
                        list(payload.keys())
                    ),
                },
            ),
            payload,
        )

    except Exception as error:
        return (
            make_result(
                "Analysis Dashboard API",
                "FAIL",
                str(error),
                {"url": url},
            ),
            None,
        )


# ============================================================
# Frontend tests
# ============================================================

def check_required_frontend_files() -> dict[str, Any]:

    required_files = [
        API_JS_FILE,
        APP_FILE,
        ANALYSIS_DASHBOARD_FILE,
        ANALYSIS_MAIN_FILE,
        ANALYSIS_HTML_FILE,
    ]

    missing = [
        str(path.relative_to(PROJECT_ROOT))
        for path in required_files
        if not path.exists()
    ]

    if missing:
        return make_result(
            "Frontend required files",
            "FAIL",
            "One or more required frontend files are missing.",
            {"missing_files": missing},
        )

    return make_result(
        "Frontend required files",
        "PASS",
        "All required EduPath frontend integration files exist.",
        {
            "files": [
                str(path.relative_to(PROJECT_ROOT))
                for path in required_files
            ]
        },
    )


def detect_frontend_api_base() -> str | None:

    if not API_JS_FILE.exists():
        return None

    content = safe_read_text(API_JS_FILE)

    matches = re.findall(
        r"""https?://(?:127\.0\.0\.1|localhost):\d+""",
        content,
        flags=re.IGNORECASE,
    )

    if not matches:
        return None

    return matches[0].rstrip("/")


def validate_frontend_api_alignment(
    expected_base_url: str,
) -> dict[str, Any]:

    detected = detect_frontend_api_base()

    if detected is None:
        return make_result(
            "Frontend API base URL",
            "WARNING",
            (
                "Could not automatically detect a localhost API "
                "URL in frontend/src/api.js."
            ),
            {
                "expected": expected_base_url,
                "file": str(
                    API_JS_FILE.relative_to(PROJECT_ROOT)
                ),
            },
        )

    if detected.rstrip("/") != expected_base_url.rstrip("/"):
        return make_result(
            "Frontend API base URL",
            "FAIL",
            "Frontend API URL does not match the backend being validated.",
            {
                "frontend_api_url": detected,
                "validation_api_url": expected_base_url,
            },
        )

    return make_result(
        "Frontend API base URL",
        "PASS",
        "Frontend and backend are using the same API base URL.",
        {
            "api_base_url": detected,
        },
    )


def validate_dashboard_step_label() -> dict[str, Any]:

    if not ANALYSIS_DASHBOARD_FILE.exists():
        return make_result(
            "Dashboard step label",
            "FAIL",
            "AnalysisDashboard.jsx does not exist.",
        )

    content = safe_read_text(
        ANALYSIS_DASHBOARD_FILE
    )

    if "151.10" in content:
        return make_result(
            "Dashboard step label",
            "PASS",
            "Analysis dashboard already displays Step 151.10.",
        )

    if "151.9" in content:
        return make_result(
            "Dashboard step label",
            "WARNING",
            (
                "Dashboard still displays Step 151.9. "
                "Change it to Step 151.10 after final validation passes."
            ),
        )

    return make_result(
        "Dashboard step label",
        "WARNING",
        (
            "No explicit Step 151.9 or Step 151.10 label "
            "was detected in AnalysisDashboard.jsx."
        ),
    )


# ============================================================
# Python compile validation
# ============================================================

def validate_python_compile() -> dict[str, Any]:

    targets = [
        PROJECT_ROOT / "backend",
        PROJECT_ROOT / "analysis_layer",
    ]

    command = [
        sys.executable,
        "-m",
        "compileall",
        "-q",
    ] + [str(path) for path in targets]

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            return make_result(
                "Python compile validation",
                "FAIL",
                "Python compile check failed.",
                {
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                },
            )

        return make_result(
            "Python compile validation",
            "PASS",
            "Backend and analysis-layer Python files compiled successfully.",
        )

    except Exception as error:
        return make_result(
            "Python compile validation",
            "FAIL",
            f"Unable to run compile validation: {error}",
        )


# ============================================================
# Frontend production build
# ============================================================

def validate_frontend_build() -> dict[str, Any]:

    package_json = FRONTEND_DIR / "package.json"

    if not package_json.exists():
        return make_result(
            "Frontend production build",
            "FAIL",
            "frontend/package.json was not found.",
        )

    npm_command = "npm.cmd" if os.name == "nt" else "npm"

    try:
        result = subprocess.run(
            [
                npm_command,
                "run",
                "build",
            ],
            cwd=FRONTEND_DIR,
            capture_output=True,
            text=True,
            timeout=240,
        )

        if result.returncode != 0:
            return make_result(
                "Frontend production build",
                "FAIL",
                "npm run build failed.",
                {
                    "stdout": result.stdout[-4000:],
                    "stderr": result.stderr[-4000:],
                },
            )

        return make_result(
            "Frontend production build",
            "PASS",
            "Vite production build completed successfully.",
            {
                "output": result.stdout[-2000:],
            },
        )

    except FileNotFoundError:
        return make_result(
            "Frontend production build",
            "FAIL",
            "npm was not found in PATH.",
        )

    except subprocess.TimeoutExpired:
        return make_result(
            "Frontend production build",
            "FAIL",
            "Frontend build exceeded the 240-second timeout.",
        )

    except Exception as error:
        return make_result(
            "Frontend production build",
            "FAIL",
            f"Unable to run frontend build: {error}",
        )


# ============================================================
# Reports
# ============================================================

def save_json_report(report: dict[str, Any]) -> None:

    OUTPUT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )


def save_csv_report(report: dict[str, Any]) -> None:

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "step",
                "check_name",
                "status",
                "message",
            ]
        )

        for result in report["checks"]:
            writer.writerow(
                [
                    STEP_NAME,
                    result["name"],
                    result["status"],
                    result["message"],
                ]
            )


def save_markdown_report(
    report: dict[str, Any],
) -> None:

    lines: list[str] = []

    lines.append(
        "# EduPath Step 151.10 Final Integration & Validation"
    )

    lines.append("")

    lines.append(
        f"- Generated: {report['generated_at']}"
    )

    lines.append(
        f"- API Base URL: `{report['api_base_url']}`"
    )

    lines.append(
        f"- Overall Status: **{report['overall_status']}**"
    )

    lines.append("")

    lines.append("## Validation Results")
    lines.append("")

    for result in report["checks"]:

        lines.append(
            f"### {result['name']}"
        )

        lines.append(
            f"**Status:** {result['status']}"
        )

        lines.append("")

        lines.append(result["message"])
        lines.append("")

    lines.append("## Final Interpretation")
    lines.append("")

    if report["overall_status"] == "PASS":
        lines.append(
            "The EduPath analysis layer, backend APIs, "
            "frontend integration and production build passed "
            "the final integration validation."
        )

        lines.append("")

        lines.append(
            "The project is suitable to use as the current "
            "validated baseline for the teacher demonstration."
        )

    else:
        lines.append(
            "One or more required integration checks failed. "
            "The failed checks should be corrected before the "
            "current version is treated as the final baseline."
        )

    OUTPUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


# ============================================================
# Terminal report
# ============================================================

def print_terminal_report(
    report: dict[str, Any],
) -> None:

    print()
    print(divider())
    print(
        f"EduPath - Step {STEP_NAME} {STEP_TITLE}"
    )
    print(divider())

    print()
    print(f"Project root : {PROJECT_ROOT}")
    print(
        f"API base URL : {report['api_base_url']}"
    )

    print()
    print(divider())
    print("FINAL INTEGRATION CHECKS")
    print(divider())

    for index, result in enumerate(
        report["checks"],
        start=1,
    ):
        print()
        print(
            f"{index}. {result['name']}"
        )

        print(
            f"   Status  : {result['status']}"
        )

        print(
            f"   Result  : {result['message']}"
        )

    print()
    print(divider())

    print(
        f"STEP {STEP_NAME} FINAL STATUS: "
        f"{report['overall_status']}"
    )

    print(divider())

    print()

    print(
        f"Checks passed   : {report['summary']['passed']}"
    )

    print(
        f"Warnings        : {report['summary']['warnings']}"
    )

    print(
        f"Checks failed   : {report['summary']['failed']}"
    )

    print()

    print(f"JSON report     : {OUTPUT_JSON}")
    print(f"CSV report      : {OUTPUT_CSV}")
    print(f"Markdown report : {OUTPUT_MD}")

    print()

    if report["overall_status"] == "PASS":
        print(
            "EduPath final integration baseline is VALID."
        )

        print(
            "You may now update the dashboard pipeline label "
            "from Step 151.9 to Step 151.10."
        )

    else:
        print(
            "Do NOT lock the final baseline yet."
        )

        print(
            "Fix the FAIL items above, then rerun Step 151.10."
        )

    print()


# ============================================================
# Main
# ============================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "EduPath Step 151.10 final integration validator"
        )
    )

    parser.add_argument(
        "--base-url",
        default=DEFAULT_API_BASE_URL,
        help=(
            "Backend API base URL. "
            "Default: http://127.0.0.1:8002"
        ),
    )

    parser.add_argument(
        "--frontend-origin",
        default="http://localhost:5176",
        help=(
            "Frontend origin used for CORS validation."
        ),
    )

    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip npm run build.",
    )

    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    ensure_output_directories()

    print(divider())
    print(
        f"EduPath - Step {STEP_NAME} {STEP_TITLE}"
    )
    print(divider())

    print()
    print("Running final integration validation...")
    print(f"API: {base_url}")
    print()

    checks: list[dict[str, Any]] = []

    # --------------------------------------------------------
    # Static project integration
    # --------------------------------------------------------

    checks.append(
        check_required_frontend_files()
    )

    checks.append(
        validate_frontend_api_alignment(
            base_url
        )
    )

    checks.append(
        validate_python_compile()
    )

    # --------------------------------------------------------
    # API checks
    # --------------------------------------------------------

    countries_result, _ = validate_countries(
        base_url
    )

    checks.append(countries_result)

    universities_result, _ = (
        validate_collection_endpoint(
            "Japan Universities API",
            (
                f"{base_url}"
                "/api/universities"
                "?country_id=country_jp"
                "&limit=100"
            ),
            BASELINE_MINIMUMS[
                "japan_universities"
            ],
        )
    )

    checks.append(universities_result)

    programs_result, _ = (
        validate_collection_endpoint(
            "Programs API",
            (
                f"{base_url}"
                "/api/programs"
                "?limit=100"
            ),
            BASELINE_MINIMUMS[
                "programs"
            ],
        )
    )

    checks.append(programs_result)

    scholarships_result, _ = (
        validate_collection_endpoint(
            "Japan Scholarships API",
            (
                f"{base_url}"
                "/api/scholarships"
                "?country_id=country_jp"
                "&limit=100"
            ),
            BASELINE_MINIMUMS[
                "scholarships"
            ],
        )
    )

    checks.append(scholarships_result)

    dashboard_result, dashboard_payload = (
        validate_dashboard_endpoint(
            base_url
        )
    )

    checks.append(dashboard_result)

    checks.append(
        test_cors(
            base_url,
            args.frontend_origin,
        )
    )

    checks.append(
        validate_dashboard_step_label()
    )

    # --------------------------------------------------------
    # Production build
    # --------------------------------------------------------

    if not args.skip_build:
        checks.append(
            validate_frontend_build()
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    passed = sum(
        1
        for item in checks
        if item["status"] == "PASS"
    )

    warnings = sum(
        1
        for item in checks
        if item["status"] == "WARNING"
    )

    failed = sum(
        1
        for item in checks
        if item["status"] == "FAIL"
    )

    overall_status = (
        "PASS"
        if failed == 0
        else "FAIL"
    )

    report = {
        "step": STEP_NAME,
        "title": STEP_TITLE,
        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "project_root": str(PROJECT_ROOT),
        "api_base_url": base_url,
        "frontend_origin": args.frontend_origin,
        "overall_status": overall_status,
        "summary": {
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "total_checks": len(checks),
        },
        "checks": checks,
        "dashboard_payload_detected": (
            isinstance(
                dashboard_payload,
                dict,
            )
        ),
    }

    save_json_report(report)
    save_csv_report(report)
    save_markdown_report(report)

    print_terminal_report(report)

    if overall_status != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()