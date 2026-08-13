from __future__ import annotations

import csv
import json
import os
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# =============================================================================
# EduPath
# Step 151.4 - Analytical Insights & Recommendation Findings
#
# Purpose:
#   1. Read the current MongoDB dataset
#   2. Convert descriptive statistics into analytical findings
#   3. Produce interpretations
#   4. Produce actionable recommendations
#   5. Export JSON, CSV and Markdown reports
#
# IMPORTANT:
#   - This script is READ-ONLY.
#   - No MongoDB records are modified.
#   - Findings describe the CURRENT EduPath dataset only.
# =============================================================================


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

DATA_ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
PLANNING_DIR = PROJECT_ROOT / "planning"
DOCS_DIR = PROJECT_ROOT / "docs"

JSON_OUTPUT = DATA_ANALYSIS_DIR / "151_4_analytical_insights.json"
CSV_OUTPUT = PLANNING_DIR / "36_analytical_insights_summary.csv"
MARKDOWN_OUTPUT = DOCS_DIR / "151_4_analytical_insights_report.md"


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
# Utility functions
# -----------------------------------------------------------------------------

def clean_text(value: Any) -> str:
    """
    Convert a value into a clean display string.
    """
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


def first_value(record: dict, field_names: list[str]) -> Any:
    """
    Return the first non-empty value from multiple possible field names.
    """
    for field_name in field_names:
        value = record.get(field_name)

        if value is not None:
            if isinstance(value, str):
                if value.strip():
                    return value
            elif isinstance(value, (list, tuple, set, dict)):
                if len(value) > 0:
                    return value
            else:
                return value

    return None


def field_present(value: Any) -> bool:
    """
    Determine whether a field should be treated as available.
    """
    if value is None:
        return False

    if isinstance(value, str):
        return clean_text(value) != ""

    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0

    return True


def to_number(value: Any) -> float | None:
    """
    Safely convert tuition-like values to numeric values.
    """
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


def pct(part: int | float, whole: int | float) -> float:
    """
    Safe percentage calculation.
    """
    if not whole:
        return 0.0

    return round((part / whole) * 100, 2)


def round_number(value: float | int | None, digits: int = 2) -> float | None:
    if value is None:
        return None

    return round(float(value), digits)


def format_money(value: float | int | None) -> str:
    if value is None:
        return "N/A"

    return f"{value:,.2f} JPY"


def normalise_label(value: Any, default: str = "Unknown") -> str:
    text = clean_text(value)

    if not text:
        return default

    return text


def get_record_id(record: dict, candidates: list[str]) -> str:
    value = first_value(record, candidates)

    if value is None:
        return ""

    return str(value)


def json_safe(value: Any) -> Any:
    """
    Convert non-JSON-native objects into JSON-safe values.
    """
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
        return [json_safe(item) for item in value]

    if isinstance(value, tuple):
        return [json_safe(item) for item in value]

    return value


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

def create_mongodb_client() -> MongoClient:
    if not MONGODB_URI:
        raise RuntimeError(
            "MongoDB connection string was not found.\n"
            "Please check the MONGODB_URI value in the project .env file."
        )

    return MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
    )


def load_dataset(db) -> dict[str, list[dict]]:
    """
    Load the four core EduPath collections.
    """

    countries = list(
        db["countries"].find({})
    )

    universities = list(
        db["universities"].find({})
    )

    programs = list(
        db["programs"].find({})
    )

    scholarships = list(
        db["scholarships"].find({})
    )

    return {
        "countries": countries,
        "universities": universities,
        "programs": programs,
        "scholarships": scholarships,
    }


# -----------------------------------------------------------------------------
# Lookup maps
# -----------------------------------------------------------------------------

def build_country_map(countries: list[dict]) -> dict[str, dict]:
    result = {}

    for record in countries:
        record_id = get_record_id(
            record,
            [
                "country_id",
                "id",
            ],
        )

        if record_id:
            result[record_id] = record

    return result


def build_university_map(universities: list[dict]) -> dict[str, dict]:
    result = {}

    for record in universities:
        record_id = get_record_id(
            record,
            [
                "university_id",
                "id",
            ],
        )

        if record_id:
            result[record_id] = record

    return result


def get_country_name(country: dict | None) -> str:
    if not country:
        return "Unknown"

    return normalise_label(
        first_value(
            country,
            [
                "country_name",
                "name",
                "display_name",
            ],
        )
    )


def get_university_name(university: dict | None) -> str:
    if not university:
        return "Unknown University"

    return normalise_label(
        first_value(
            university,
            [
                "university_name",
                "name",
            ],
        ),
        default="Unknown University",
    )


# -----------------------------------------------------------------------------
# Programme metrics
# -----------------------------------------------------------------------------

def analyse_programs(
    programs: list[dict],
    university_map: dict[str, dict],
    country_map: dict[str, dict],
) -> dict[str, Any]:

    total_programs = len(programs)

    degree_counter: Counter[str] = Counter()
    tuition_counter: Counter[int] = Counter()
    university_counter: Counter[str] = Counter()
    country_counter: Counter[str] = Counter()

    tuition_values: list[float] = []

    for program in programs:

        degree = normalise_label(
            first_value(
                program,
                [
                    "degree_level",
                    "degree",
                ],
            )
        )

        degree_counter[degree] += 1

        tuition_value = to_number(
            first_value(
                program,
                [
                    "tuition_fee",
                    "annual_tuition",
                    "tuition",
                ],
            )
        )

        if tuition_value is not None and tuition_value >= 0:
            tuition_values.append(tuition_value)

            tuition_counter[
                int(round(tuition_value))
            ] += 1

        university_id = get_record_id(
            program,
            [
                "university_id",
                "host_university_id",
            ],
        )

        university = university_map.get(university_id)

        university_name = get_university_name(
            university
        )

        university_counter[university_name] += 1

        if university:
            country_id = get_record_id(
                university,
                [
                    "country_id",
                ],
            )

            country = country_map.get(country_id)

            country_name = get_country_name(country)

            country_counter[country_name] += 1

    # -------------------------------------------------------------------------
    # Tuition statistics
    # -------------------------------------------------------------------------

    if tuition_values:
        tuition_mean = statistics.mean(
            tuition_values
        )

        tuition_median = statistics.median(
            tuition_values
        )

        tuition_min = min(
            tuition_values
        )

        tuition_max = max(
            tuition_values
        )

        if len(tuition_values) > 1:
            tuition_std = statistics.pstdev(
                tuition_values
            )
        else:
            tuition_std = 0.0

    else:
        tuition_mean = None
        tuition_median = None
        tuition_min = None
        tuition_max = None
        tuition_std = None

    tuition_mode_value = None
    tuition_mode_count = 0

    if tuition_counter:
        tuition_mode_value, tuition_mode_count = (
            tuition_counter.most_common(1)[0]
        )

    # -------------------------------------------------------------------------
    # Degree distribution
    # -------------------------------------------------------------------------

    degree_distribution = []

    for degree, count in degree_counter.most_common():
        degree_distribution.append(
            {
                "degree_level": degree,
                "count": count,
                "percentage": pct(
                    count,
                    total_programs,
                ),
            }
        )

    # -------------------------------------------------------------------------
    # Tuition distribution
    # -------------------------------------------------------------------------

    tuition_distribution = []

    for tuition, count in sorted(
        tuition_counter.items()
    ):
        tuition_distribution.append(
            {
                "tuition_jpy": tuition,
                "count": count,
                "percentage": pct(
                    count,
                    total_programs,
                ),
            }
        )

    # -------------------------------------------------------------------------
    # Programs by university
    # -------------------------------------------------------------------------

    programs_by_university = []

    for university, count in (
        university_counter.most_common()
    ):
        programs_by_university.append(
            {
                "university": university,
                "count": count,
                "percentage": pct(
                    count,
                    total_programs,
                ),
            }
        )

    # -------------------------------------------------------------------------
    # Programs by country
    # -------------------------------------------------------------------------

    programs_by_country = []

    for country, count in (
        country_counter.most_common()
    ):
        programs_by_country.append(
            {
                "country": country,
                "count": count,
                "percentage": pct(
                    count,
                    total_programs,
                ),
            }
        )

    return {
        "total_programs": total_programs,
        "degree_distribution": degree_distribution,
        "tuition": {
            "available_count": len(
                tuition_values
            ),
            "coverage_percentage": pct(
                len(tuition_values),
                total_programs,
            ),
            "distinct_values": len(
                tuition_counter
            ),
            "mean_jpy": round_number(
                tuition_mean
            ),
            "median_jpy": round_number(
                tuition_median
            ),
            "minimum_jpy": round_number(
                tuition_min
            ),
            "maximum_jpy": round_number(
                tuition_max
            ),
            "standard_deviation_jpy": round_number(
                tuition_std
            ),
            "mode_jpy": tuition_mode_value,
            "mode_count": tuition_mode_count,
            "mode_percentage": pct(
                tuition_mode_count,
                total_programs,
            ),
            "distribution": tuition_distribution,
        },
        "programs_by_university": programs_by_university,
        "programs_by_country": programs_by_country,
        "represented_universities": len(
            university_counter
        ),
        "represented_countries": len(
            country_counter
        ),
    }


# -----------------------------------------------------------------------------
# Scholarship metrics
# -----------------------------------------------------------------------------

def analyse_scholarships(
    scholarships: list[dict],
    country_map: dict[str, dict],
) -> dict[str, Any]:

    total_scholarships = len(scholarships)

    funding_counter: Counter[str] = Counter()
    status_counter: Counter[str] = Counter()
    country_counter: Counter[str] = Counter()

    for scholarship in scholarships:

        funding_type = normalise_label(
            first_value(
                scholarship,
                [
                    "funding_type",
                    "funding",
                ],
            )
        )

        status = normalise_label(
            first_value(
                scholarship,
                [
                    "scholarship_status",
                    "status",
                ],
            )
        )

        funding_counter[funding_type] += 1
        status_counter[status] += 1

        country_id = get_record_id(
            scholarship,
            [
                "country_id",
            ],
        )

        country_name = "Unknown"

        if country_id:
            country_name = get_country_name(
                country_map.get(
                    country_id
                )
            )

        country_counter[
            country_name
        ] += 1

    # -------------------------------------------------------------------------
    # Requirement-field completeness
    # -------------------------------------------------------------------------

    requirement_fields = {
        "fields_of_study": [
            "fields_of_study",
            "field_of_study",
        ],
        "eligible_nationalities": [
            "eligible_nationalities",
            "nationality_requirement",
        ],
        "minimum_gpa": [
            "minimum_gpa",
            "gpa_requirement",
        ],
        "english_requirement": [
            "ielts_requirement",
            "toefl_requirement",
            "english_requirement",
        ],
        "age_limit": [
            "age_limit",
        ],
        "application_deadline": [
            "application_deadline",
        ],
    }

    requirement_completeness = {}

    for label, candidate_fields in (
        requirement_fields.items()
    ):

        available = 0

        for scholarship in scholarships:

            found = False

            for field_name in candidate_fields:
                if field_present(
                    scholarship.get(
                        field_name
                    )
                ):
                    found = True
                    break

            if found:
                available += 1

        requirement_completeness[
            label
        ] = {
            "available": available,
            "missing": (
                total_scholarships
                - available
            ),
            "coverage_percentage": pct(
                available,
                total_scholarships,
            ),
        }

    completeness_percentages = [
        details["coverage_percentage"]
        for details in (
            requirement_completeness.values()
        )
    ]

    if completeness_percentages:
        average_requirement_coverage = (
            statistics.mean(
                completeness_percentages
            )
        )
    else:
        average_requirement_coverage = 0

    funding_distribution = []

    for funding, count in (
        funding_counter.most_common()
    ):
        funding_distribution.append(
            {
                "funding_type": funding,
                "count": count,
                "percentage": pct(
                    count,
                    total_scholarships,
                ),
            }
        )

    status_distribution = []

    for status, count in (
        status_counter.most_common()
    ):
        status_distribution.append(
            {
                "status": status,
                "count": count,
                "percentage": pct(
                    count,
                    total_scholarships,
                ),
            }
        )

    scholarships_by_country = []

    for country, count in (
        country_counter.most_common()
    ):
        scholarships_by_country.append(
            {
                "country": country,
                "count": count,
                "percentage": pct(
                    count,
                    total_scholarships,
                ),
            }
        )

    return {
        "total_scholarships": total_scholarships,
        "funding_distribution": funding_distribution,
        "status_distribution": status_distribution,
        "scholarships_by_country": scholarships_by_country,
        "requirement_completeness": requirement_completeness,
        "average_requirement_coverage_percentage": round(
            average_requirement_coverage,
            2,
        ),
        "represented_countries": len(
            country_counter
        ),
    }


# -----------------------------------------------------------------------------
# Insight builder
# -----------------------------------------------------------------------------

def build_insight(
    insight_id: str,
    category: str,
    finding: str,
    evidence: str,
    interpretation: str,
    recommendation: str,
    priority: str,
) -> dict[str, str]:

    return {
        "insight_id": insight_id,
        "category": category,
        "finding": finding,
        "evidence": evidence,
        "interpretation": interpretation,
        "recommendation": recommendation,
        "priority": priority,
    }


def generate_insights(
    program_metrics: dict[str, Any],
    scholarship_metrics: dict[str, Any],
) -> list[dict[str, str]]:

    insights: list[dict[str, str]] = []

    # =========================================================================
    # Insight 1: Degree concentration
    # =========================================================================

    degree_distribution = (
        program_metrics[
            "degree_distribution"
        ]
    )

    if degree_distribution:

        dominant_degree = (
            degree_distribution[0]
        )

        degree_name = dominant_degree[
            "degree_level"
        ]

        degree_count = dominant_degree[
            "count"
        ]

        degree_percentage = (
            dominant_degree[
                "percentage"
            ]
        )

        if degree_percentage >= 70:
            interpretation = (
                "The current program dataset is strongly concentrated "
                f"at the {degree_name} level. This means the current "
                "EduPath program coverage is more representative of "
                f"{degree_name}-level opportunities than of other "
                "degree levels."
            )

            recommendation = (
                "During future data expansion, prioritise underrepresented "
                "degree levels so that recommendation results can support "
                "a broader range of students."
            )

            priority = "HIGH"

        else:
            interpretation = (
                "The current program dataset does not show an extreme "
                "single-degree concentration."
            )

            recommendation = (
                "Continue monitoring degree-level balance as more "
                "programs are added."
            )

            priority = "MEDIUM"

        insights.append(
            build_insight(
                "INSIGHT_01",
                "Program Degree Distribution",
                (
                    f"{degree_name} is the dominant degree level "
                    "in the current EduPath program dataset."
                ),
                (
                    f"{degree_count} of "
                    f"{program_metrics['total_programs']} programs "
                    f"({degree_percentage:.2f}%) are "
                    f"{degree_name} programs."
                ),
                interpretation,
                recommendation,
                priority,
            )
        )

    # =========================================================================
    # Insight 2: Tuition concentration and skew
    # =========================================================================

    tuition = program_metrics[
        "tuition"
    ]

    mean_tuition = tuition[
        "mean_jpy"
    ]

    median_tuition = tuition[
        "median_jpy"
    ]

    maximum_tuition = tuition[
        "maximum_jpy"
    ]

    mode_tuition = tuition[
        "mode_jpy"
    ]

    mode_percentage = tuition[
        "mode_percentage"
    ]

    if (
        mean_tuition is not None
        and median_tuition is not None
    ):

        if median_tuition > 0:
            mean_median_difference_pct = (
                (
                    mean_tuition
                    - median_tuition
                )
                / median_tuition
            ) * 100
        else:
            mean_median_difference_pct = 0

        if mean_median_difference_pct >= 10:

            interpretation = (
                "The mean tuition is noticeably higher than the median. "
                "This indicates that a smaller number of higher-fee "
                "programs are pulling the average upward."
            )

            recommendation = (
                "For affordability analysis, EduPath should display both "
                "median and mean tuition. Median tuition is useful for "
                "describing the typical program, while the mean still "
                "shows the effect of more expensive programs."
            )

            priority = "HIGH"

        else:

            interpretation = (
                "Mean and median tuition are relatively close, so the "
                "current tuition distribution does not appear strongly "
                "skewed."
            )

            recommendation = (
                "Continue using both median and mean tuition as the "
                "program dataset grows."
            )

            priority = "MEDIUM"

        insights.append(
            build_insight(
                "INSIGHT_02",
                "Program Tuition Analysis",
                (
                    "Most current program tuition values are concentrated "
                    "around a common annual tuition level, while some "
                    "programs have substantially higher tuition."
                ),
                (
                    f"Mean tuition = {format_money(mean_tuition)}; "
                    f"median = {format_money(median_tuition)}; "
                    f"maximum = {format_money(maximum_tuition)}; "
                    f"most common tuition = {format_money(mode_tuition)} "
                    f"({mode_percentage:.2f}% of current programs)."
                ),
                interpretation,
                recommendation,
                priority,
            )
        )

    # =========================================================================
    # Insight 3: University representation
    # =========================================================================

    university_distribution = (
        program_metrics[
            "programs_by_university"
        ]
    )

    if university_distribution:

        counts = [
            item["count"]
            for item in university_distribution
        ]

        min_count = min(counts)
        max_count = max(counts)

        represented_universities = (
            program_metrics[
                "represented_universities"
            ]
        )

        if max_count - min_count <= 1:

            interpretation = (
                "Within the universities currently represented in the "
                "program collection, program counts are evenly distributed. "
                "This reduces the risk that one included university "
                "dominates the current program dataset."
            )

            recommendation = (
                "Future expansion should focus more on adding additional "
                "universities and additional degree/program categories "
                "rather than repeatedly adding many records from the "
                "same universities."
            )

            priority = "MEDIUM"

        else:

            interpretation = (
                "Program representation differs noticeably across the "
                "universities currently included."
            )

            recommendation = (
                "Future collection should prioritise universities that "
                "currently have lower representation."
            )

            priority = "HIGH"

        insights.append(
            build_insight(
                "INSIGHT_03",
                "University Representation",
                (
                    "Program coverage across currently represented "
                    "universities was assessed for balance."
                ),
                (
                    f"{represented_universities} universities are represented "
                    f"in the program collection. Program counts range from "
                    f"{min_count} to {max_count} per represented university."
                ),
                interpretation,
                recommendation,
                priority,
            )
        )

    # =========================================================================
    # Insight 4: Scholarship funding concentration
    # =========================================================================

    funding_distribution = (
        scholarship_metrics[
            "funding_distribution"
        ]
    )

    if funding_distribution:

        dominant_funding = (
            funding_distribution[0]
        )

        funding_type = dominant_funding[
            "funding_type"
        ]

        funding_count = dominant_funding[
            "count"
        ]

        funding_percentage = (
            dominant_funding[
                "percentage"
            ]
        )

        if funding_percentage >= 90:

            interpretation = (
                "The current scholarship collection is highly concentrated "
                f"in the '{funding_type}' funding category. This is useful "
                "for fully funded scholarship discovery, but it does not yet "
                "represent the full variety of funding models available."
            )

            recommendation = (
                "During later scholarship-data expansion, add other funding "
                "categories such as partial funding, tuition waivers, "
                "university grants and other relevant scholarship types."
            )

            priority = "MEDIUM"

        else:

            interpretation = (
                "The scholarship collection contains multiple funding "
                "categories."
            )

            recommendation = (
                "Continue preserving funding-type diversity when adding "
                "new scholarship records."
            )

            priority = "MEDIUM"

        insights.append(
            build_insight(
                "INSIGHT_04",
                "Scholarship Funding Distribution",
                (
                    f"{funding_type} is the dominant funding category "
                    "in the current scholarship dataset."
                ),
                (
                    f"{funding_count} of "
                    f"{scholarship_metrics['total_scholarships']} scholarships "
                    f"({funding_percentage:.2f}%) are classified as "
                    f"{funding_type}."
                ),
                interpretation,
                recommendation,
                priority,
            )
        )

    # =========================================================================
    # Insight 5: Scholarship status
    # =========================================================================

    status_distribution = (
        scholarship_metrics[
            "status_distribution"
        ]
    )

    if status_distribution:

        dominant_status = (
            status_distribution[0]
        )

        status_name = dominant_status[
            "status"
        ]

        status_count = dominant_status[
            "count"
        ]

        status_percentage = (
            dominant_status[
                "percentage"
            ]
        )

        if status_percentage >= 90:

            interpretation = (
                "The current scholarship collection is concentrated in a "
                f"single lifecycle status: '{status_name}'. This reflects "
                "the current collection focus rather than the complete "
                "scholarship market."
            )

            recommendation = (
                "When the dataset is expanded, retain status history and "
                "include open, upcoming and closed/archived records where "
                "appropriate. This will support future trend and application "
                "cycle analysis."
            )

        else:

            interpretation = (
                "The scholarship collection currently contains multiple "
                "application lifecycle statuses."
            )

            recommendation = (
                "Continue maintaining scholarship status consistently "
                "because it is important for time-based analysis."
            )

        insights.append(
            build_insight(
                "INSIGHT_05",
                "Scholarship Status Distribution",
                (
                    f"The dominant scholarship status is "
                    f"'{status_name}'."
                ),
                (
                    f"{status_count} of "
                    f"{scholarship_metrics['total_scholarships']} scholarships "
                    f"({status_percentage:.2f}%) have status "
                    f"'{status_name}'."
                ),
                interpretation,
                recommendation,
                "MEDIUM",
            )
        )

    # =========================================================================
    # Insight 6: Scholarship requirement-data completeness
    # =========================================================================

    requirement_completeness = (
        scholarship_metrics[
            "requirement_completeness"
        ]
    )

    average_coverage = (
        scholarship_metrics[
            "average_requirement_coverage_percentage"
        ]
    )

    weak_fields = []

    for field_name, details in (
        requirement_completeness.items()
    ):

        if (
            details[
                "coverage_percentage"
            ]
            < 70
        ):
            weak_fields.append(
                (
                    field_name,
                    details[
                        "coverage_percentage"
                    ],
                )
            )

    if weak_fields:

        weak_fields.sort(
            key=lambda item: item[1]
        )

        weak_fields_text = ", ".join(
            f"{field} ({coverage:.2f}%)"
            for field, coverage in weak_fields
        )

        interpretation = (
            "Several scholarship eligibility fields are incomplete. "
            "The recommendation engine can still treat missing values "
            "as uncertainty, but confidence in eligibility decisions "
            "will improve when these fields are verified."
        )

        recommendation = (
            "Prioritise verification of low-coverage scholarship fields, "
            "especially nationality eligibility, GPA requirements, "
            "English-language requirements, age limits and deadlines."
        )

        priority = "HIGH"

        evidence = (
            f"Average coverage across selected scholarship requirement "
            f"fields is {average_coverage:.2f}%. Low-coverage fields: "
            f"{weak_fields_text}."
        )

    else:

        interpretation = (
            "Core scholarship requirement fields currently have "
            "satisfactory coverage."
        )

        recommendation = (
            "Maintain the same verification standard when adding "
            "new scholarship records."
        )

        priority = "MEDIUM"

        evidence = (
            f"Average requirement-field coverage is "
            f"{average_coverage:.2f}%."
        )

    insights.append(
        build_insight(
            "INSIGHT_06",
            "Scholarship Requirement Data Quality",
            "Eligibility-data completeness was analysed.",
            evidence,
            interpretation,
            recommendation,
            priority,
        )
    )

    # =========================================================================
    # Insight 7: Geographic coverage
    # =========================================================================

    program_country_count = (
        program_metrics[
            "represented_countries"
        ]
    )

    scholarship_country_count = (
        scholarship_metrics[
            "represented_countries"
        ]
    )

    program_country_distribution = (
        program_metrics[
            "programs_by_country"
        ]
    )

    scholarship_country_distribution = (
        scholarship_metrics[
            "scholarships_by_country"
        ]
    )

    program_country_names = [
        item["country"]
        for item in (
            program_country_distribution
        )
    ]

    scholarship_country_names = [
        item["country"]
        for item in (
            scholarship_country_distribution
        )
    ]

    if (
        program_country_count <= 1
        or scholarship_country_count <= 1
    ):

        interpretation = (
            "The current program and scholarship analysis is intentionally "
            "country-focused. Therefore, the current findings are suitable "
            "for analysing the collected EduPath dataset but should not yet "
            "be generalised to all universities or scholarships across "
            "East and Southeast Asia."
        )

        recommendation = (
            "Keep the current Japan dataset as the validated baseline. "
            "Later, expand programs and scholarships country-by-country "
            "using the same verification, relationship-integrity and "
            "analysis pipeline."
        )

        priority = "HIGH"

    else:

        interpretation = (
            "The current dataset already includes multiple geographic "
            "markets for programs and scholarships."
        )

        recommendation = (
            "Future analysis can compare tuition, degree distribution "
            "and scholarship availability across countries."
        )

        priority = "MEDIUM"

    insights.append(
        build_insight(
            "INSIGHT_07",
            "Geographic Coverage",
            (
                "The geographic scope of current program and scholarship "
                "data was assessed."
            ),
            (
                f"Program countries represented: {program_country_count} "
                f"({', '.join(program_country_names) or 'None'}). "
                f"Scholarship countries represented: "
                f"{scholarship_country_count} "
                f"({', '.join(scholarship_country_names) or 'None'})."
            ),
            interpretation,
            recommendation,
            priority,
        )
    )

    return insights


# -----------------------------------------------------------------------------
# Overall conclusions
# -----------------------------------------------------------------------------

def build_overall_conclusion(
    program_metrics: dict[str, Any],
    scholarship_metrics: dict[str, Any],
    insights: list[dict[str, str]],
) -> dict[str, Any]:

    high_priority = [
        item
        for item in insights
        if item["priority"] == "HIGH"
    ]

    medium_priority = [
        item
        for item in insights
        if item["priority"] == "MEDIUM"
    ]

    return {
        "analysis_scope": (
            "Current EduPath dataset only. Results must not yet be "
            "generalised to all universities, programs or scholarships "
            "in Japan or other countries."
        ),
        "current_dataset": {
            "programs": program_metrics[
                "total_programs"
            ],
            "scholarships": scholarship_metrics[
                "total_scholarships"
            ],
            "program_countries": program_metrics[
                "represented_countries"
            ],
            "scholarship_countries": scholarship_metrics[
                "represented_countries"
            ],
        },
        "high_priority_findings": len(
            high_priority
        ),
        "medium_priority_findings": len(
            medium_priority
        ),
        "conclusion": (
            "EduPath now has an analytical layer that goes beyond "
            "descriptive charts. The system identifies dataset patterns, "
            "interprets their meaning and converts them into actionable "
            "recommendations for data expansion and recommendation-system "
            "improvement."
        ),
    }


# -----------------------------------------------------------------------------
# CSV export
# -----------------------------------------------------------------------------

def write_csv(
    insights: list[dict[str, str]]
) -> None:

    PLANNING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "insight_id",
        "category",
        "priority",
        "finding",
        "evidence",
        "interpretation",
        "recommendation",
    ]

    with CSV_OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for insight in insights:
            writer.writerow(
                {
                    field: insight.get(
                        field,
                        "",
                    )
                    for field in fieldnames
                }
            )


# -----------------------------------------------------------------------------
# JSON export
# -----------------------------------------------------------------------------

def write_json(
    report: dict[str, Any]
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
# Markdown export
# -----------------------------------------------------------------------------

def write_markdown(
    report: dict[str, Any]
) -> None:

    DOCS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    program_metrics = report[
        "program_metrics"
    ]

    scholarship_metrics = report[
        "scholarship_metrics"
    ]

    insights = report[
        "insights"
    ]

    lines: list[str] = []

    lines.append(
        "# EduPath Step 151.4 Analytical Insights Report"
    )
    lines.append("")

    lines.append(
        "## Analysis Scope"
    )
    lines.append("")

    lines.append(
        "This report describes the current EduPath dataset only. "
        "The results should not yet be generalised to every university, "
        "program or scholarship in Japan or other countries."
    )
    lines.append("")

    lines.append(
        "## Current Dataset"
    )
    lines.append("")

    lines.append(
        f"- Programs: {program_metrics['total_programs']}"
    )

    lines.append(
        f"- Scholarships: "
        f"{scholarship_metrics['total_scholarships']}"
    )

    lines.append(
        f"- Program countries represented: "
        f"{program_metrics['represented_countries']}"
    )

    lines.append(
        f"- Scholarship countries represented: "
        f"{scholarship_metrics['represented_countries']}"
    )

    lines.append("")

    lines.append(
        "## Key Program Tuition Statistics"
    )
    lines.append("")

    tuition = program_metrics[
        "tuition"
    ]

    lines.append(
        f"- Mean tuition: "
        f"{format_money(tuition['mean_jpy'])}"
    )

    lines.append(
        f"- Median tuition: "
        f"{format_money(tuition['median_jpy'])}"
    )

    lines.append(
        f"- Minimum tuition: "
        f"{format_money(tuition['minimum_jpy'])}"
    )

    lines.append(
        f"- Maximum tuition: "
        f"{format_money(tuition['maximum_jpy'])}"
    )

    lines.append(
        f"- Tuition coverage: "
        f"{tuition['coverage_percentage']:.2f}%"
    )

    lines.append("")

    lines.append(
        "## Analytical Findings"
    )
    lines.append("")

    for index, insight in enumerate(
        insights,
        start=1,
    ):

        lines.append(
            f"### {index}. "
            f"{insight['category']}"
        )

        lines.append("")

        lines.append(
            f"**Priority:** "
            f"{insight['priority']}"
        )

        lines.append("")

        lines.append(
            f"**Finding:** "
            f"{insight['finding']}"
        )

        lines.append("")

        lines.append(
            f"**Evidence:** "
            f"{insight['evidence']}"
        )

        lines.append("")

        lines.append(
            f"**Interpretation:** "
            f"{insight['interpretation']}"
        )

        lines.append("")

        lines.append(
            f"**Recommendation:** "
            f"{insight['recommendation']}"
        )

        lines.append("")

    lines.append(
        "## Overall Conclusion"
    )
    lines.append("")

    lines.append(
        report[
            "overall_conclusion"
        ][
            "conclusion"
        ]
    )

    lines.append("")

    MARKDOWN_OUTPUT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


# -----------------------------------------------------------------------------
# Terminal output
# -----------------------------------------------------------------------------

def print_report(
    report: dict[str, Any]
) -> None:

    insights = report[
        "insights"
    ]

    program_metrics = report[
        "program_metrics"
    ]

    scholarship_metrics = report[
        "scholarship_metrics"
    ]

    print()
    print("=" * 92)
    print(
        "EduPath - Step 151.4 Analytical Insights "
        "& Recommendation Findings"
    )
    print("=" * 92)

    print()
    print("DATASET SUMMARY")
    print("-" * 92)

    print(
        f"Programs      : "
        f"{program_metrics['total_programs']}"
    )

    print(
        f"Scholarships  : "
        f"{scholarship_metrics['total_scholarships']}"
    )

    print(
        f"Program countries represented     : "
        f"{program_metrics['represented_countries']}"
    )

    print(
        f"Scholarship countries represented : "
        f"{scholarship_metrics['represented_countries']}"
    )

    print()
    print("=" * 92)
    print("ANALYTICAL INSIGHTS")
    print("=" * 92)

    for index, insight in enumerate(
        insights,
        start=1,
    ):

        print()
        print(
            f"{index}. {insight['category']}"
        )

        print(
            f"Priority       : "
            f"{insight['priority']}"
        )

        print(
            f"Finding        : "
            f"{insight['finding']}"
        )

        print(
            f"Evidence       : "
            f"{insight['evidence']}"
        )

        print(
            f"Interpretation : "
            f"{insight['interpretation']}"
        )

        print(
            f"Recommendation : "
            f"{insight['recommendation']}"
        )

    print()
    print("=" * 92)
    print(
        "STEP 151.4 ANALYTICAL INSIGHTS: COMPLETED"
    )
    print("=" * 92)

    print()
    print(
        f"Insights generated : "
        f"{len(insights)}"
    )

    print(
        f"JSON report        : "
        f"{JSON_OUTPUT}"
    )

    print(
        f"CSV report         : "
        f"{CSV_OUTPUT}"
    )

    print(
        f"Markdown report    : "
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
        print("=" * 92)
        print(
            "EduPath - Step 151.4 Analytical Insights "
            "& Recommendation Findings"
        )
        print("=" * 92)

        print()
        print(
            f"Project root: {PROJECT_ROOT}"
        )

        print()
        print(
            "Connecting to MongoDB Atlas..."
        )

        client = create_mongodb_client()

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
        # Load current dataset
        # ---------------------------------------------------------------------

        dataset = load_dataset(db)

        countries = dataset[
            "countries"
        ]

        universities = dataset[
            "universities"
        ]

        programs = dataset[
            "programs"
        ]

        scholarships = dataset[
            "scholarships"
        ]

        print()
        print("Records loaded:")
        print(
            f"Countries     : "
            f"{len(countries)}"
        )

        print(
            f"Universities  : "
            f"{len(universities)}"
        )

        print(
            f"Programs      : "
            f"{len(programs)}"
        )

        print(
            f"Scholarships  : "
            f"{len(scholarships)}"
        )

        # ---------------------------------------------------------------------
        # Lookup maps
        # ---------------------------------------------------------------------

        country_map = build_country_map(
            countries
        )

        university_map = (
            build_university_map(
                universities
            )
        )

        # ---------------------------------------------------------------------
        # Analysis
        # ---------------------------------------------------------------------

        program_metrics = analyse_programs(
            programs,
            university_map,
            country_map,
        )

        scholarship_metrics = (
            analyse_scholarships(
                scholarships,
                country_map,
            )
        )

        insights = generate_insights(
            program_metrics,
            scholarship_metrics,
        )

        overall_conclusion = (
            build_overall_conclusion(
                program_metrics,
                scholarship_metrics,
                insights,
            )
        )

        report = {
            "step": "151.4",
            "title": (
                "Analytical Insights & "
                "Recommendation Findings"
            ),
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "database": DATABASE_NAME,
            "analysis_scope": (
                "Current EduPath dataset only"
            ),
            "program_metrics": (
                program_metrics
            ),
            "scholarship_metrics": (
                scholarship_metrics
            ),
            "insights": insights,
            "overall_conclusion": (
                overall_conclusion
            ),
            "mongodb_records_modified": False,
        }

        # ---------------------------------------------------------------------
        # Export
        # ---------------------------------------------------------------------

        write_json(
            report
        )

        write_csv(
            insights
        )

        write_markdown(
            report
        )

        # ---------------------------------------------------------------------
        # Terminal report
        # ---------------------------------------------------------------------

        print_report(
            report
        )

    except PyMongoError as error:

        print()
        print("=" * 92)
        print(
            "STEP 151.4 FAILED - MONGODB ERROR"
        )
        print("=" * 92)

        print(
            str(error)
        )

        raise

    except Exception as error:

        print()
        print("=" * 92)
        print(
            "STEP 151.4 FAILED"
        )
        print("=" * 92)

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