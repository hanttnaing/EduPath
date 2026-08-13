from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DATA_ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
PLANNING_DIR = PROJECT_ROOT / "planning"

DATA_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
PLANNING_DIR.mkdir(parents=True, exist_ok=True)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ============================================================
# DATABASE CONFIG
# ============================================================

try:
    from recommend_scholarships_final import (
        MONGODB_URI,
        DATABASE_NAME,
    )
except ImportError as error:
    raise RuntimeError(
        "Could not import MongoDB configuration from "
        "scripts/recommend_scholarships_final.py"
    ) from error


# ============================================================
# OUTPUT FILES
# ============================================================

OUTPUT_JSON = (
    DATA_ANALYSIS_DIR
    / "151_2_descriptive_analysis.json"
)

OUTPUT_CSV = (
    PLANNING_DIR
    / "35_descriptive_analysis_summary.csv"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def first_non_empty(
    document: dict[str, Any],
    *keys: str,
) -> Any:
    for key in keys:
        value = document.get(key)

        if value is None:
            continue

        if isinstance(value, str):
            if value.strip():
                return value.strip()
        else:
            return value

    return None


def normalize_label(value: Any) -> str:
    text = clean_text(value)

    if not text:
        return "Unknown"

    return text


def json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            json_safe(item)
            for item in value
        ]

    return value


def safe_percentage(
    count: int,
    total: int,
) -> float:
    if total == 0:
        return 0.0

    return round(
        (count / total) * 100,
        2,
    )


def print_section(title: str) -> None:
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


# ============================================================
# DATA EXTRACTION HELPERS
# ============================================================

def get_program_degree(
    program: dict[str, Any],
) -> str:

    value = first_non_empty(
        program,
        "degree_level",
        "degree",
        "program_level",
    )

    return normalize_label(value)


def get_program_tuition(
    program: dict[str, Any],
) -> float | None:

    raw_value = first_non_empty(
        program,
        "tuition_fee",
        "annual_tuition",
        "tuition",
    )

    if raw_value is None:
        return None

    try:
        tuition = float(raw_value)

        if tuition <= 0:
            return None

        return tuition

    except (TypeError, ValueError):
        return None


def get_university_id(
    university: dict[str, Any],
) -> str:

    value = first_non_empty(
        university,
        "university_id",
        "id",
    )

    return clean_text(value)


def get_university_name(
    university: dict[str, Any],
) -> str:

    value = first_non_empty(
        university,
        "university_name",
        "name",
    )

    return normalize_label(value)


def get_program_university_id(
    program: dict[str, Any],
) -> str:

    value = first_non_empty(
        program,
        "university_id",
        "host_university_id",
    )

    return clean_text(value)


def get_scholarship_funding(
    scholarship: dict[str, Any],
) -> str:

    value = first_non_empty(
        scholarship,
        "funding_type",
        "funding",
        "scholarship_type",
    )

    return normalize_label(value)


def get_scholarship_status(
    scholarship: dict[str, Any],
) -> str:
    """
    IMPORTANT:

    Current EduPath scholarship schema uses
    `scholarship_status`.

    `status` is only kept as a backward-compatible fallback.
    """

    value = first_non_empty(
        scholarship,
        "scholarship_status",
        "status",
    )

    return normalize_label(value)


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main() -> None:

    print("=" * 100)
    print(
        "EduPath - Step 151.2 "
        "Descriptive Data Analysis"
    )
    print("=" * 100)

    print()
    print("Connecting to MongoDB Atlas...")

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:
        client.admin.command("ping")

        print(
            "MongoDB Atlas connection: SUCCESS"
        )
        print(
            f"Database: {DATABASE_NAME}"
        )

        db = client[DATABASE_NAME]

        countries = list(
            db["countries"].find(
                {},
                {"_id": 0},
            )
        )

        universities = list(
            db["universities"].find(
                {},
                {"_id": 0},
            )
        )

        programs = list(
            db["programs"].find(
                {},
                {"_id": 0},
            )
        )

        scholarships = list(
            db["scholarships"].find(
                {},
                {"_id": 0},
            )
        )

        # ====================================================
        # DATASET COUNTS
        # ====================================================

        dataset_counts = {
            "countries": len(countries),
            "universities": len(universities),
            "programs": len(programs),
            "scholarships": len(scholarships),
        }

        print_section(
            "DATASET COUNTS"
        )

        print(
            f"Countries     : "
            f"{dataset_counts['countries']}"
        )
        print(
            f"Universities  : "
            f"{dataset_counts['universities']}"
        )
        print(
            f"Programs      : "
            f"{dataset_counts['programs']}"
        )
        print(
            f"Scholarships  : "
            f"{dataset_counts['scholarships']}"
        )

        # ====================================================
        # PROGRAM DEGREE DISTRIBUTION
        # ====================================================

        degree_counter = Counter(
            get_program_degree(program)
            for program in programs
        )

        print_section(
            "PROGRAM DEGREE DISTRIBUTION"
        )

        degree_distribution: list[
            dict[str, Any]
        ] = []

        for degree, count in degree_counter.most_common():

            percentage = safe_percentage(
                count,
                len(programs),
            )

            print(
                f"{degree:<15} "
                f"{count:>3} program(s) | "
                f"{percentage:>6.2f}%"
            )

            degree_distribution.append(
                {
                    "degree": degree,
                    "count": count,
                    "percentage": percentage,
                }
            )

        # ====================================================
        # PROGRAM TUITION STATISTICS
        # ====================================================

        tuition_values: list[float] = []

        for program in programs:
            tuition = get_program_tuition(
                program
            )

            if tuition is not None:
                tuition_values.append(
                    tuition
                )

        tuition_counter = Counter(
            tuition_values
        )

        tuition_coverage = safe_percentage(
            len(tuition_values),
            len(programs),
        )

        tuition_statistics: dict[str, Any] = {
            "coverage_percentage": tuition_coverage,
            "available_count": len(tuition_values),
            "missing_count": (
                len(programs)
                - len(tuition_values)
            ),
            "distinct_values": len(
                tuition_counter
            ),
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
            "standard_deviation": None,
        }

        if tuition_values:

            tuition_statistics["mean"] = round(
                statistics.mean(
                    tuition_values
                ),
                2,
            )

            tuition_statistics["median"] = round(
                statistics.median(
                    tuition_values
                ),
                2,
            )

            tuition_statistics["minimum"] = min(
                tuition_values
            )

            tuition_statistics["maximum"] = max(
                tuition_values
            )

            if len(tuition_values) > 1:
                tuition_statistics[
                    "standard_deviation"
                ] = round(
                    statistics.stdev(
                        tuition_values
                    ),
                    2,
                )
            else:
                tuition_statistics[
                    "standard_deviation"
                ] = 0.0

        print_section(
            "PROGRAM TUITION STATISTICS"
        )

        print(
            f"Tuition coverage       : "
            f"{tuition_coverage:.1f}%"
        )

        print(
            f"Distinct tuition values: "
            f"{len(tuition_counter)}"
        )

        if tuition_values:

            print(
                f"Mean tuition           : "
                f"{tuition_statistics['mean']:,.2f} JPY"
            )

            print(
                f"Median tuition         : "
                f"{tuition_statistics['median']:,.2f} JPY"
            )

            print(
                f"Minimum tuition        : "
                f"{tuition_statistics['minimum']:,.0f} JPY"
            )

            print(
                f"Maximum tuition        : "
                f"{tuition_statistics['maximum']:,.0f} JPY"
            )

            print(
                f"Standard deviation     : "
                f"{tuition_statistics['standard_deviation']:,.2f} JPY"
            )

        # ====================================================
        # TUITION DISTRIBUTION
        # ====================================================

        print_section(
            "TUITION DISTRIBUTION"
        )

        tuition_distribution: list[
            dict[str, Any]
        ] = []

        for tuition, count in sorted(
            tuition_counter.items()
        ):

            percentage = safe_percentage(
                count,
                len(programs),
            )

            print(
                f"{tuition:>12,.0f} JPY | "
                f"{count:>3} program(s) | "
                f"{percentage:>6.2f}%"
            )

            tuition_distribution.append(
                {
                    "tuition_jpy": tuition,
                    "count": count,
                    "percentage": percentage,
                }
            )

        # ====================================================
        # PROGRAMS BY UNIVERSITY
        # ====================================================

        university_lookup: dict[str, str] = {}

        for university in universities:

            university_id = get_university_id(
                university
            )

            if not university_id:
                continue

            university_lookup[
                university_id
            ] = get_university_name(
                university
            )

        program_university_counter: Counter[
            str
        ] = Counter()

        for program in programs:

            university_id = (
                get_program_university_id(
                    program
                )
            )

            university_name = (
                university_lookup.get(
                    university_id,
                    university_id
                    or "Unknown University",
                )
            )

            program_university_counter[
                university_name
            ] += 1

        print_section(
            "PROGRAMS BY UNIVERSITY"
        )

        programs_by_university: list[
            dict[str, Any]
        ] = []

        for university_name, count in (
            program_university_counter.most_common()
        ):

            print(
                f"{university_name:<45} "
                f"{count:>3} program(s)"
            )

            programs_by_university.append(
                {
                    "university": university_name,
                    "program_count": count,
                }
            )

        # ====================================================
        # SCHOLARSHIP FUNDING DISTRIBUTION
        # ====================================================

        funding_counter = Counter(
            get_scholarship_funding(
                scholarship
            )
            for scholarship in scholarships
        )

        print_section(
            "SCHOLARSHIP FUNDING DISTRIBUTION"
        )

        scholarship_funding_distribution: list[
            dict[str, Any]
        ] = []

        for funding, count in funding_counter.most_common():

            percentage = safe_percentage(
                count,
                len(scholarships),
            )

            print(
                f"{funding:<30} "
                f"{count:>3} | "
                f"{percentage:>6.2f}%"
            )

            scholarship_funding_distribution.append(
                {
                    "funding_type": funding,
                    "count": count,
                    "percentage": percentage,
                }
            )

        # ====================================================
        # SCHOLARSHIP STATUS DISTRIBUTION
        # ====================================================

        scholarship_status_counter = Counter(
            get_scholarship_status(
                scholarship
            )
            for scholarship in scholarships
        )

        print_section(
            "SCHOLARSHIP STATUS DISTRIBUTION"
        )

        scholarship_status_distribution: list[
            dict[str, Any]
        ] = []

        for status, count in (
            scholarship_status_counter.most_common()
        ):

            percentage = safe_percentage(
                count,
                len(scholarships),
            )

            print(
                f"{status:<30} "
                f"{count:>3} | "
                f"{percentage:>6.2f}%"
            )

            scholarship_status_distribution.append(
                {
                    "status": status,
                    "count": count,
                    "percentage": percentage,
                }
            )

        # ====================================================
        # ANALYSIS INTERPRETATION
        # ====================================================

        print_section(
            "ANALYSIS INTERPRETATION NOTES"
        )

        interpretation_notes = [
            (
                "Descriptive statistics were calculated "
                "from the current EduPath dataset."
            ),
            (
                "Tuition analysis uses verified annual "
                "tuition values currently stored in MongoDB."
            ),
            (
                "Degree distributions describe only the "
                "programs currently collected in EduPath."
            ),
            (
                "Scholarship funding and status distributions "
                "describe the current targeted scholarship dataset."
            ),
            (
                "The scholarship status analysis uses the "
                "`scholarship_status` field from the current "
                "EduPath scholarship schema."
            ),
            (
                "These results should not yet be generalised "
                "to all universities, programs, or scholarships "
                "in Japan."
            ),
        ]

        for note in interpretation_notes:
            print(
                f"+ {note}"
            )

        # ====================================================
        # JSON OUTPUT
        # ====================================================

        report = {
            "analysis_step": "151.2",
            "analysis_name": (
                "EduPath Descriptive Data Analysis"
            ),
            "generated_at": datetime.now().isoformat(),
            "database_name": DATABASE_NAME,
            "dataset_counts": dataset_counts,
            "program_degree_distribution": (
                degree_distribution
            ),
            "program_tuition_statistics": (
                tuition_statistics
            ),
            "tuition_distribution": (
                tuition_distribution
            ),
            "programs_by_university": (
                programs_by_university
            ),
            "scholarship_funding_distribution": (
                scholarship_funding_distribution
            ),
            "scholarship_status_distribution": (
                scholarship_status_distribution
            ),
            "interpretation_notes": (
                interpretation_notes
            ),
        }

        with OUTPUT_JSON.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                json_safe(report),
                file,
                ensure_ascii=False,
                indent=2,
            )

        # ====================================================
        # CSV OUTPUT
        # ====================================================

        csv_rows: list[
            dict[str, Any]
        ] = []

        for item in degree_distribution:
            csv_rows.append(
                {
                    "analysis_category":
                        "program_degree_distribution",
                    "metric":
                        item["degree"],
                    "value":
                        item["count"],
                    "percentage":
                        item["percentage"],
                    "unit":
                        "programs",
                }
            )

        for item in tuition_distribution:
            csv_rows.append(
                {
                    "analysis_category":
                        "tuition_distribution",
                    "metric":
                        f"{item['tuition_jpy']:,.0f}",
                    "value":
                        item["count"],
                    "percentage":
                        item["percentage"],
                    "unit":
                        "JPY annual tuition",
                }
            )

        for item in programs_by_university:
            csv_rows.append(
                {
                    "analysis_category":
                        "programs_by_university",
                    "metric":
                        item["university"],
                    "value":
                        item["program_count"],
                    "percentage":
                        "",
                    "unit":
                        "programs",
                }
            )

        for item in scholarship_funding_distribution:
            csv_rows.append(
                {
                    "analysis_category":
                        "scholarship_funding_distribution",
                    "metric":
                        item["funding_type"],
                    "value":
                        item["count"],
                    "percentage":
                        item["percentage"],
                    "unit":
                        "scholarships",
                }
            )

        for item in scholarship_status_distribution:
            csv_rows.append(
                {
                    "analysis_category":
                        "scholarship_status_distribution",
                    "metric":
                        item["status"],
                    "value":
                        item["count"],
                    "percentage":
                        item["percentage"],
                    "unit":
                        "scholarships",
                }
            )

        with OUTPUT_CSV.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "analysis_category",
                    "metric",
                    "value",
                    "percentage",
                    "unit",
                ],
            )

            writer.writeheader()
            writer.writerows(
                csv_rows
            )

        # ====================================================
        # FINAL MESSAGE
        # ====================================================

        print()
        print("=" * 100)
        print(
            "STEP 151.2 DESCRIPTIVE ANALYSIS: COMPLETED"
        )
        print("=" * 100)

        print()
        print(
            f"JSON report: {OUTPUT_JSON}"
        )
        print(
            f"CSV report : {OUTPUT_CSV}"
        )

        print()
        print(
            "MongoDB records modified: NO"
        )

    except PyMongoError as error:
        raise RuntimeError(
            "MongoDB descriptive analysis failed."
        ) from error

    finally:
        client.close()

        print()
        print(
            "MongoDB connection closed safely."
        )


if __name__ == "__main__":
    main()