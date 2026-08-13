from __future__ import annotations

import csv
import json
import os
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# =============================================================================
# EduPath
# Step 151.5 - Comparative & Decision-Oriented Analysis
#
# Purpose:
#   1. Compare tuition across degree levels
#   2. Compare tuition across universities
#   3. Build affordability bands
#   4. Identify lower-cost / higher-cost program groups
#   5. Convert analysis into student-oriented decision findings
#
# IMPORTANT:
#   - READ ONLY
#   - MongoDB records are NOT modified
#   - Results describe only the current EduPath dataset
# =============================================================================


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

DATA_ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
PLANNING_DIR = PROJECT_ROOT / "planning"
DOCS_DIR = PROJECT_ROOT / "docs"

JSON_OUTPUT = (
    DATA_ANALYSIS_DIR
    / "151_5_comparative_analysis.json"
)

CSV_OUTPUT = (
    PLANNING_DIR
    / "37_comparative_analysis_summary.csv"
)

MARKDOWN_OUTPUT = (
    DOCS_DIR
    / "151_5_comparative_analysis_report.md"
)


# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

load_dotenv(ENV_FILE)

MONGODB_URI = (
    os.getenv("MONGODB_URI")
    or os.getenv("MONGO_URI")
    or os.getenv("MONGO_URL")
)

DATABASE_NAME = (
    os.getenv("MONGODB_DB")
    or os.getenv("MONGODB_DATABASE")
    or os.getenv("DB_NAME")
    or "edupath_db"
)


# -----------------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------------

def clean_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in {
        "",
        "none",
        "null",
        "unknown",
        "n/a",
        "na",
        "not available",
        "not_available",
    }:
        return ""

    return text


def first_value(
    record: dict,
    field_names: list[str],
) -> Any:

    for name in field_names:
        value = record.get(name)

        if value is None:
            continue

        if isinstance(value, str):
            if value.strip():
                return value

        elif isinstance(
            value,
            (list, tuple, set, dict),
        ):
            if len(value) > 0:
                return value

        else:
            return value

    return None


def to_number(value: Any) -> float | None:

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if not text:
        return None

    text = (
        text.replace(",", "")
        .replace("JPY", "")
        .replace("¥", "")
        .strip()
    )

    try:
        return float(text)

    except ValueError:
        return None


def pct(
    part: float | int,
    whole: float | int,
) -> float:

    if not whole:
        return 0.0

    return round(
        (part / whole) * 100,
        2,
    )


def safe_mean(
    values: list[float],
) -> float | None:

    if not values:
        return None

    return round(
        statistics.mean(values),
        2,
    )


def safe_median(
    values: list[float],
) -> float | None:

    if not values:
        return None

    return round(
        statistics.median(values),
        2,
    )


def safe_min(
    values: list[float],
) -> float | None:

    if not values:
        return None

    return round(
        min(values),
        2,
    )


def safe_max(
    values: list[float],
) -> float | None:

    if not values:
        return None

    return round(
        max(values),
        2,
    )


def format_money(
    value: float | int | None,
) -> str:

    if value is None:
        return "N/A"

    return f"{value:,.0f} JPY"


def get_program_id(
    record: dict,
) -> str:

    value = first_value(
        record,
        [
            "program_id",
            "id",
        ],
    )

    return str(value) if value else ""


def get_program_name(
    record: dict,
) -> str:

    value = first_value(
        record,
        [
            "program_name",
            "name",
        ],
    )

    return (
        clean_text(value)
        or "Unknown Program"
    )


def get_degree(
    record: dict,
) -> str:

    value = first_value(
        record,
        [
            "degree_level",
            "degree",
        ],
    )

    return (
        clean_text(value)
        or "Unknown"
    )


def get_university_id(
    record: dict,
) -> str:

    value = first_value(
        record,
        [
            "university_id",
            "host_university_id",
        ],
    )

    return str(value) if value else ""


def get_tuition(
    record: dict,
) -> float | None:

    return to_number(
        first_value(
            record,
            [
                "tuition_fee",
                "annual_tuition",
                "tuition",
            ],
        )
    )


def json_safe(
    value: Any,
) -> Any:

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

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

    if isinstance(value, tuple):
        return [
            json_safe(item)
            for item in value
        ]

    return value


# -----------------------------------------------------------------------------
# MongoDB
# -----------------------------------------------------------------------------

def create_client() -> MongoClient:

    if not MONGODB_URI:
        raise RuntimeError(
            "MONGODB_URI was not found in .env"
        )

    return MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
    )


def load_data(
    db,
) -> tuple[list[dict], list[dict], list[dict]]:

    programs = list(
        db["programs"].find({})
    )

    universities = list(
        db["universities"].find({})
    )

    scholarships = list(
        db["scholarships"].find({})
    )

    return (
        programs,
        universities,
        scholarships,
    )


# -----------------------------------------------------------------------------
# University map
# -----------------------------------------------------------------------------

def build_university_map(
    universities: list[dict],
) -> dict[str, dict]:

    result = {}

    for university in universities:

        university_id = first_value(
            university,
            [
                "university_id",
                "id",
            ],
        )

        if university_id:
            result[str(university_id)] = university

    return result


def university_name(
    university: dict | None,
) -> str:

    if not university:
        return "Unknown University"

    value = first_value(
        university,
        [
            "university_name",
            "name",
        ],
    )

    return (
        clean_text(value)
        or "Unknown University"
    )


# -----------------------------------------------------------------------------
# Prepare usable program rows
# -----------------------------------------------------------------------------

def prepare_program_rows(
    programs: list[dict],
    university_map: dict[str, dict],
) -> list[dict]:

    rows = []

    for program in programs:

        tuition = get_tuition(program)

        if tuition is None:
            continue

        university_id = (
            get_university_id(program)
        )

        university = university_map.get(
            university_id
        )

        rows.append(
            {
                "program_id": get_program_id(
                    program
                ),
                "program_name": get_program_name(
                    program
                ),
                "degree_level": get_degree(
                    program
                ),
                "university_id": university_id,
                "university_name": university_name(
                    university
                ),
                "tuition_jpy": tuition,
            }
        )

    return rows


# -----------------------------------------------------------------------------
# Overall tuition statistics
# -----------------------------------------------------------------------------

def overall_tuition_statistics(
    rows: list[dict],
) -> dict[str, Any]:

    values = [
        row["tuition_jpy"]
        for row in rows
    ]

    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
            "standard_deviation": None,
            "q1": None,
            "q3": None,
        }

    mean_value = statistics.mean(values)
    median_value = statistics.median(values)

    if len(values) > 1:
        std_value = statistics.pstdev(
            values
        )
    else:
        std_value = 0

    sorted_values = sorted(values)

    # Tukey-style quartile approximation
    if len(sorted_values) >= 4:

        quartiles = statistics.quantiles(
            sorted_values,
            n=4,
            method="inclusive",
        )

        q1 = quartiles[0]
        q3 = quartiles[2]

    else:
        q1 = min(sorted_values)
        q3 = max(sorted_values)

    return {
        "count": len(values),
        "mean": round(
            mean_value,
            2,
        ),
        "median": round(
            median_value,
            2,
        ),
        "minimum": round(
            min(values),
            2,
        ),
        "maximum": round(
            max(values),
            2,
        ),
        "standard_deviation": round(
            std_value,
            2,
        ),
        "q1": round(
            q1,
            2,
        ),
        "q3": round(
            q3,
            2,
        ),
    }


# -----------------------------------------------------------------------------
# Degree tuition comparison
# -----------------------------------------------------------------------------

def degree_level_comparison(
    rows: list[dict],
) -> list[dict]:

    grouped: dict[
        str,
        list[float],
    ] = defaultdict(list)

    for row in rows:
        grouped[
            row["degree_level"]
        ].append(
            row["tuition_jpy"]
        )

    result = []

    for degree, values in grouped.items():

        result.append(
            {
                "degree_level": degree,
                "program_count": len(values),
                "mean_tuition_jpy": safe_mean(
                    values
                ),
                "median_tuition_jpy": safe_median(
                    values
                ),
                "minimum_tuition_jpy": safe_min(
                    values
                ),
                "maximum_tuition_jpy": safe_max(
                    values
                ),
            }
        )

    result.sort(
        key=lambda item: (
            item["mean_tuition_jpy"]
            if item["mean_tuition_jpy"]
            is not None
            else float("inf")
        )
    )

    return result


# -----------------------------------------------------------------------------
# University tuition comparison
# -----------------------------------------------------------------------------

def university_comparison(
    rows: list[dict],
) -> list[dict]:

    grouped: dict[
        str,
        list[float],
    ] = defaultdict(list)

    for row in rows:
        grouped[
            row["university_name"]
        ].append(
            row["tuition_jpy"]
        )

    result = []

    for university, values in grouped.items():

        result.append(
            {
                "university": university,
                "program_count": len(values),
                "mean_tuition_jpy": safe_mean(
                    values
                ),
                "median_tuition_jpy": safe_median(
                    values
                ),
                "minimum_tuition_jpy": safe_min(
                    values
                ),
                "maximum_tuition_jpy": safe_max(
                    values
                ),
            }
        )

    result.sort(
        key=lambda item: (
            item["mean_tuition_jpy"]
            if item["mean_tuition_jpy"]
            is not None
            else float("inf")
        )
    )

    return result


# -----------------------------------------------------------------------------
# Affordability classification
# -----------------------------------------------------------------------------

def classify_affordability(
    tuition: float,
    q1: float,
    q3: float,
) -> str:

    if tuition <= q1:
        return "Lower-cost"

    if tuition >= q3:
        return "Higher-cost"

    return "Mid-range"


def affordability_analysis(
    rows: list[dict],
    overall_stats: dict[str, Any],
) -> dict[str, Any]:

    q1 = overall_stats["q1"]
    q3 = overall_stats["q3"]

    if q1 is None or q3 is None:
        return {
            "bands": [],
            "programs": [],
        }

    counter = Counter()

    classified_programs = []

    for row in rows:

        band = classify_affordability(
            row["tuition_jpy"],
            q1,
            q3,
        )

        counter[band] += 1

        classified_programs.append(
            {
                **row,
                "affordability_band": band,
            }
        )

    total = len(classified_programs)

    bands = []

    for band in [
        "Lower-cost",
        "Mid-range",
        "Higher-cost",
    ]:

        count = counter.get(
            band,
            0,
        )

        bands.append(
            {
                "band": band,
                "count": count,
                "percentage": pct(
                    count,
                    total,
                ),
            }
        )

    classified_programs.sort(
        key=lambda item: (
            item["tuition_jpy"],
            item["program_name"],
        )
    )

    return {
        "q1_threshold_jpy": q1,
        "q3_threshold_jpy": q3,
        "bands": bands,
        "programs": classified_programs,
    }


# -----------------------------------------------------------------------------
# Scholarship overview
# -----------------------------------------------------------------------------

def scholarship_overview(
    scholarships: list[dict],
) -> dict[str, Any]:

    total = len(scholarships)

    funding_counter = Counter()
    status_counter = Counter()

    for scholarship in scholarships:

        funding = clean_text(
            first_value(
                scholarship,
                [
                    "funding_type",
                    "funding",
                ],
            )
        ) or "Unknown"

        status = clean_text(
            first_value(
                scholarship,
                [
                    "scholarship_status",
                    "status",
                ],
            )
        ) or "Unknown"

        funding_counter[funding] += 1
        status_counter[status] += 1

    funding_distribution = []

    for label, count in (
        funding_counter.most_common()
    ):
        funding_distribution.append(
            {
                "funding_type": label,
                "count": count,
                "percentage": pct(
                    count,
                    total,
                ),
            }
        )

    status_distribution = []

    for label, count in (
        status_counter.most_common()
    ):
        status_distribution.append(
            {
                "status": label,
                "count": count,
                "percentage": pct(
                    count,
                    total,
                ),
            }
        )

    return {
        "total": total,
        "funding_distribution": (
            funding_distribution
        ),
        "status_distribution": (
            status_distribution
        ),
    }


# -----------------------------------------------------------------------------
# Decision findings
# -----------------------------------------------------------------------------

def build_decision_findings(
    overall_stats: dict[str, Any],
    degree_comparison: list[dict],
    university_stats: list[dict],
    affordability: dict[str, Any],
    scholarship_stats: dict[str, Any],
) -> list[dict]:

    findings = []

    # -------------------------------------------------------------------------
    # 1. Typical tuition
    # -------------------------------------------------------------------------

    findings.append(
        {
            "finding_id": "DECISION_01",
            "title": "Typical Annual Tuition Baseline",
            "evidence": (
                f"Current median annual tuition is "
                f"{format_money(overall_stats['median'])}, "
                f"while mean tuition is "
                f"{format_money(overall_stats['mean'])}."
            ),
            "interpretation": (
                "The median provides a useful baseline for describing "
                "the typical tuition in the current EduPath program dataset."
            ),
            "decision_use": (
                "Students can compare an individual program's tuition "
                "against the dataset median to identify whether it is "
                "relatively lower-cost or higher-cost."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # 2. Tuition range
    # -------------------------------------------------------------------------

    findings.append(
        {
            "finding_id": "DECISION_02",
            "title": "Tuition Cost Range",
            "evidence": (
                f"Annual tuition currently ranges from "
                f"{format_money(overall_stats['minimum'])} "
                f"to {format_money(overall_stats['maximum'])}."
            ),
            "interpretation": (
                "Students may face substantially different tuition costs "
                "depending on institution and program."
            ),
            "decision_use": (
                "Budget should therefore be included as a meaningful "
                "feature in future program recommendation scoring."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # 3. Degree comparison
    # -------------------------------------------------------------------------

    if degree_comparison:

        valid = [
            item
            for item in degree_comparison
            if item["mean_tuition_jpy"]
            is not None
        ]

        if valid:

            cheapest_degree = min(
                valid,
                key=lambda item: (
                    item[
                        "mean_tuition_jpy"
                    ]
                ),
            )

            highest_degree = max(
                valid,
                key=lambda item: (
                    item[
                        "mean_tuition_jpy"
                    ]
                ),
            )

            findings.append(
                {
                    "finding_id": "DECISION_03",
                    "title": "Degree-Level Tuition Comparison",
                    "evidence": (
                        f"The lowest current mean tuition by degree is "
                        f"{cheapest_degree['degree_level']} at "
                        f"{format_money(cheapest_degree['mean_tuition_jpy'])}. "
                        f"The highest is "
                        f"{highest_degree['degree_level']} at "
                        f"{format_money(highest_degree['mean_tuition_jpy'])}."
                    ),
                    "interpretation": (
                        "Degree-level tuition differs within the current "
                        "dataset, but sample sizes are uneven."
                    ),
                    "decision_use": (
                        "Degree-level averages can support exploration, "
                        "but should not be treated as national-level averages "
                        "until more programs are collected."
                    ),
                }
            )

    # -------------------------------------------------------------------------
    # 4. University comparison
    # -------------------------------------------------------------------------

    if university_stats:

        lowest_uni = university_stats[0]
        highest_uni = university_stats[-1]

        findings.append(
            {
                "finding_id": "DECISION_04",
                "title": "University Tuition Comparison",
                "evidence": (
                    f"Among universities represented in the current program "
                    f"dataset, the lowest mean tuition is "
                    f"{lowest_uni['university']} "
                    f"({format_money(lowest_uni['mean_tuition_jpy'])}), "
                    f"while the highest mean is "
                    f"{highest_uni['university']} "
                    f"({format_money(highest_uni['mean_tuition_jpy'])})."
                ),
                "interpretation": (
                    "Institution choice can materially affect tuition cost."
                ),
                "decision_use": (
                    "University-level tuition comparison can be presented "
                    "as one component of student affordability analysis."
                ),
            }
        )

    # -------------------------------------------------------------------------
    # 5. Affordability bands
    # -------------------------------------------------------------------------

    bands = {
        item["band"]: item
        for item in affordability.get(
            "bands",
            [],
        )
    }

    if bands:

        low = bands.get(
            "Lower-cost",
            {},
        )

        mid = bands.get(
            "Mid-range",
            {},
        )

        high = bands.get(
            "Higher-cost",
            {},
        )

        findings.append(
            {
                "finding_id": "DECISION_05",
                "title": "Affordability Segmentation",
                "evidence": (
                    f"Lower-cost: {low.get('count', 0)} program(s); "
                    f"Mid-range: {mid.get('count', 0)} program(s); "
                    f"Higher-cost: {high.get('count', 0)} program(s)."
                ),
                "interpretation": (
                    "Programs can be grouped into relative affordability "
                    "bands using current tuition quartiles."
                ),
                "decision_use": (
                    "Later, users can choose a preferred budget range and "
                    "EduPath can use this information as a recommendation "
                    "feature rather than only showing raw tuition values."
                ),
            }
        )

    # -------------------------------------------------------------------------
    # 6. Scholarship decision support
    # -------------------------------------------------------------------------

    funding_distribution = (
        scholarship_stats[
            "funding_distribution"
        ]
    )

    if funding_distribution:

        dominant = funding_distribution[0]

        findings.append(
            {
                "finding_id": "DECISION_06",
                "title": "Scholarship Financial Opportunity",
                "evidence": (
                    f"{dominant['count']} of "
                    f"{scholarship_stats['total']} current scholarship "
                    f"records are classified as "
                    f"{dominant['funding_type']}."
                ),
                "interpretation": (
                    "Scholarship availability can significantly change "
                    "the student's effective education cost."
                ),
                "decision_use": (
                    "Program tuition and scholarship matching should be "
                    "combined later so users can evaluate both listed tuition "
                    "and possible funding opportunities. A scholarship should "
                    "not be assumed to apply to every program unless eligibility "
                    "and host-program relationships are verified."
                ),
            }
        )

    return findings


# -----------------------------------------------------------------------------
# CSV export
# -----------------------------------------------------------------------------

def write_csv(
    degree_comparison: list[dict],
    university_comparison_data: list[dict],
) -> None:

    PLANNING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with CSV_OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        fieldnames = [
            "comparison_type",
            "name",
            "program_count",
            "mean_tuition_jpy",
            "median_tuition_jpy",
            "minimum_tuition_jpy",
            "maximum_tuition_jpy",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in degree_comparison:

            writer.writerow(
                {
                    "comparison_type":
                        "degree_level",
                    "name":
                        row["degree_level"],
                    "program_count":
                        row["program_count"],
                    "mean_tuition_jpy":
                        row[
                            "mean_tuition_jpy"
                        ],
                    "median_tuition_jpy":
                        row[
                            "median_tuition_jpy"
                        ],
                    "minimum_tuition_jpy":
                        row[
                            "minimum_tuition_jpy"
                        ],
                    "maximum_tuition_jpy":
                        row[
                            "maximum_tuition_jpy"
                        ],
                }
            )

        for row in university_comparison_data:

            writer.writerow(
                {
                    "comparison_type":
                        "university",
                    "name":
                        row["university"],
                    "program_count":
                        row["program_count"],
                    "mean_tuition_jpy":
                        row[
                            "mean_tuition_jpy"
                        ],
                    "median_tuition_jpy":
                        row[
                            "median_tuition_jpy"
                        ],
                    "minimum_tuition_jpy":
                        row[
                            "minimum_tuition_jpy"
                        ],
                    "maximum_tuition_jpy":
                        row[
                            "maximum_tuition_jpy"
                        ],
                }
            )


# -----------------------------------------------------------------------------
# Markdown
# -----------------------------------------------------------------------------

def write_markdown(
    report: dict,
) -> None:

    DOCS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stats = report[
        "overall_tuition_statistics"
    ]

    lines = []

    lines.append(
        "# EduPath Step 151.5 Comparative & Decision-Oriented Analysis"
    )
    lines.append("")

    lines.append(
        "## Scope"
    )
    lines.append("")

    lines.append(
        "This analysis describes only the programs and scholarships "
        "currently collected in EduPath. It should not yet be interpreted "
        "as a national-level statistical representation of all programs "
        "or scholarships in Japan."
    )
    lines.append("")

    lines.append(
        "## Overall Tuition Statistics"
    )
    lines.append("")

    lines.append(
        f"- Programs analysed: {stats['count']}"
    )

    lines.append(
        f"- Mean annual tuition: "
        f"{format_money(stats['mean'])}"
    )

    lines.append(
        f"- Median annual tuition: "
        f"{format_money(stats['median'])}"
    )

    lines.append(
        f"- Minimum annual tuition: "
        f"{format_money(stats['minimum'])}"
    )

    lines.append(
        f"- Maximum annual tuition: "
        f"{format_money(stats['maximum'])}"
    )

    lines.append(
        f"- Q1 tuition threshold: "
        f"{format_money(stats['q1'])}"
    )

    lines.append(
        f"- Q3 tuition threshold: "
        f"{format_money(stats['q3'])}"
    )

    lines.append("")

    lines.append(
        "## Degree-Level Comparison"
    )
    lines.append("")

    for row in report[
        "degree_comparison"
    ]:

        lines.append(
            f"- {row['degree_level']}: "
            f"{row['program_count']} program(s), "
            f"mean {format_money(row['mean_tuition_jpy'])}, "
            f"median {format_money(row['median_tuition_jpy'])}"
        )

    lines.append("")

    lines.append(
        "## University Comparison"
    )
    lines.append("")

    for row in report[
        "university_comparison"
    ]:

        lines.append(
            f"- {row['university']}: "
            f"{row['program_count']} program(s), "
            f"mean {format_money(row['mean_tuition_jpy'])}"
        )

    lines.append("")

    lines.append(
        "## Decision-Oriented Findings"
    )
    lines.append("")

    for index, finding in enumerate(
        report["decision_findings"],
        start=1,
    ):

        lines.append(
            f"### {index}. "
            f"{finding['title']}"
        )
        lines.append("")

        lines.append(
            f"**Evidence:** "
            f"{finding['evidence']}"
        )
        lines.append("")

        lines.append(
            f"**Interpretation:** "
            f"{finding['interpretation']}"
        )
        lines.append("")

        lines.append(
            f"**Decision Use:** "
            f"{finding['decision_use']}"
        )
        lines.append("")

    MARKDOWN_OUTPUT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


# -----------------------------------------------------------------------------
# JSON
# -----------------------------------------------------------------------------

def write_json(
    report: dict,
) -> None:

    DATA_ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with JSON_OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            json_safe(report),
            file,
            indent=2,
            ensure_ascii=False,
        )


# -----------------------------------------------------------------------------
# Terminal print
# -----------------------------------------------------------------------------

def print_report(
    report: dict,
) -> None:

    overall = report[
        "overall_tuition_statistics"
    ]

    print()
    print("=" * 96)
    print(
        "EduPath - Step 151.5 Comparative "
        "& Decision-Oriented Analysis"
    )
    print("=" * 96)

    print()
    print("OVERALL TUITION COMPARISON")
    print("-" * 96)

    print(
        f"Programs analysed      : "
        f"{overall['count']}"
    )

    print(
        f"Mean tuition           : "
        f"{format_money(overall['mean'])}"
    )

    print(
        f"Median tuition         : "
        f"{format_money(overall['median'])}"
    )

    print(
        f"Minimum tuition        : "
        f"{format_money(overall['minimum'])}"
    )

    print(
        f"Maximum tuition        : "
        f"{format_money(overall['maximum'])}"
    )

    print(
        f"Q1                     : "
        f"{format_money(overall['q1'])}"
    )

    print(
        f"Q3                     : "
        f"{format_money(overall['q3'])}"
    )

    print()
    print("=" * 96)
    print("DEGREE-LEVEL TUITION COMPARISON")
    print("=" * 96)

    for row in report[
        "degree_comparison"
    ]:

        print()
        print(
            f"{row['degree_level']}"
        )

        print(
            f"  Programs : "
            f"{row['program_count']}"
        )

        print(
            f"  Mean     : "
            f"{format_money(row['mean_tuition_jpy'])}"
        )

        print(
            f"  Median   : "
            f"{format_money(row['median_tuition_jpy'])}"
        )

        print(
            f"  Range    : "
            f"{format_money(row['minimum_tuition_jpy'])}"
            f" - "
            f"{format_money(row['maximum_tuition_jpy'])}"
        )

    print()
    print("=" * 96)
    print("UNIVERSITY TUITION COMPARISON")
    print("=" * 96)

    for row in report[
        "university_comparison"
    ]:

        print(
            f"{row['university']:<45} "
            f"{row['program_count']:>2} program(s) | "
            f"Mean: "
            f"{format_money(row['mean_tuition_jpy'])}"
        )

    print()
    print("=" * 96)
    print("AFFORDABILITY SEGMENTATION")
    print("=" * 96)

    for band in report[
        "affordability_analysis"
    ][
        "bands"
    ]:

        print(
            f"{band['band']:<15} : "
            f"{band['count']} program(s) | "
            f"{band['percentage']:.2f}%"
        )

    print()
    print("=" * 96)
    print("DECISION-ORIENTED FINDINGS")
    print("=" * 96)

    for index, finding in enumerate(
        report[
            "decision_findings"
        ],
        start=1,
    ):

        print()
        print(
            f"{index}. {finding['title']}"
        )

        print(
            f"Evidence       : "
            f"{finding['evidence']}"
        )

        print(
            f"Interpretation : "
            f"{finding['interpretation']}"
        )

        print(
            f"Decision Use   : "
            f"{finding['decision_use']}"
        )

    print()
    print("=" * 96)
    print(
        "STEP 151.5 COMPARATIVE & "
        "DECISION-ORIENTED ANALYSIS: COMPLETED"
    )
    print("=" * 96)

    print()

    print(
        f"JSON report     : "
        f"{JSON_OUTPUT}"
    )

    print(
        f"CSV report      : "
        f"{CSV_OUTPUT}"
    )

    print(
        f"Markdown report : "
        f"{MARKDOWN_OUTPUT}"
    )

    print()
    print(
        "MongoDB records modified: NO"
    )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:

    client = None

    try:

        print()
        print("=" * 96)
        print(
            "EduPath - Step 151.5 Comparative "
            "& Decision-Oriented Analysis"
        )
        print("=" * 96)

        print()
        print(
            f"Project root: {PROJECT_ROOT}"
        )

        print()
        print(
            "Connecting to MongoDB Atlas..."
        )

        client = create_client()

        client.admin.command("ping")

        print(
            "MongoDB Atlas connection: SUCCESS"
        )

        db = client[
            DATABASE_NAME
        ]

        print(
            f"Database: {DATABASE_NAME}"
        )

        # ---------------------------------------------------------------------
        # Load
        # ---------------------------------------------------------------------

        (
            programs,
            universities,
            scholarships,
        ) = load_data(db)

        print()
        print("Records loaded:")
        print(
            f"Programs      : "
            f"{len(programs)}"
        )
        print(
            f"Universities  : "
            f"{len(universities)}"
        )
        print(
            f"Scholarships  : "
            f"{len(scholarships)}"
        )

        # ---------------------------------------------------------------------
        # Prepare
        # ---------------------------------------------------------------------

        university_map = (
            build_university_map(
                universities
            )
        )

        rows = prepare_program_rows(
            programs,
            university_map,
        )

        # ---------------------------------------------------------------------
        # Analysis
        # ---------------------------------------------------------------------

        overall_stats = (
            overall_tuition_statistics(
                rows
            )
        )

        degree_comparison_data = (
            degree_level_comparison(
                rows
            )
        )

        university_comparison_data = (
            university_comparison(
                rows
            )
        )

        affordability = (
            affordability_analysis(
                rows,
                overall_stats,
            )
        )

        scholarship_stats = (
            scholarship_overview(
                scholarships
            )
        )

        decision_findings = (
            build_decision_findings(
                overall_stats,
                degree_comparison_data,
                university_comparison_data,
                affordability,
                scholarship_stats,
            )
        )

        # ---------------------------------------------------------------------
        # Report
        # ---------------------------------------------------------------------

        report = {
            "step": "151.5",
            "title": (
                "Comparative & "
                "Decision-Oriented Analysis"
            ),
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "database": DATABASE_NAME,
            "analysis_scope": (
                "Current EduPath dataset only"
            ),
            "dataset_counts": {
                "programs": len(programs),
                "universities": len(
                    universities
                ),
                "scholarships": len(
                    scholarships
                ),
                "programs_with_tuition": len(
                    rows
                ),
            },
            "overall_tuition_statistics":
                overall_stats,
            "degree_comparison":
                degree_comparison_data,
            "university_comparison":
                university_comparison_data,
            "affordability_analysis":
                affordability,
            "scholarship_overview":
                scholarship_stats,
            "decision_findings":
                decision_findings,
            "mongodb_records_modified":
                False,
        }

        # ---------------------------------------------------------------------
        # Export
        # ---------------------------------------------------------------------

        write_json(
            report
        )

        write_csv(
            degree_comparison_data,
            university_comparison_data,
        )

        write_markdown(
            report
        )

        # ---------------------------------------------------------------------
        # Print
        # ---------------------------------------------------------------------

        print_report(
            report
        )

    except PyMongoError as error:

        print()
        print("=" * 96)
        print(
            "STEP 151.5 FAILED - "
            "MONGODB ERROR"
        )
        print("=" * 96)

        print(error)

        raise

    except Exception as error:

        print()
        print("=" * 96)
        print(
            "STEP 151.5 FAILED"
        )
        print("=" * 96)

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )

        raise

    finally:

        if client is not None:

            client.close()

            print()
            print(
                "MongoDB connection closed safely."
            )


if __name__ == "__main__":
    main()