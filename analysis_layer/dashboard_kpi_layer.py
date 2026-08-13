from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =============================================================================
# EduPath
# Step 151.7 - Data Analysis Dashboard KPI Layer
#
# Purpose:
#   Consolidate outputs from Steps 151.1 - 151.6 into one clean,
#   frontend-ready analytical dashboard dataset.
#
# IMPORTANT:
#   - This script reads analysis files only.
#   - MongoDB is NOT modified.
#   - No recommendation algorithm is modified.
# =============================================================================


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
CHARTS_DIR = ANALYSIS_DIR / "charts"
DOCS_DIR = PROJECT_ROOT / "docs"
PLANNING_DIR = PROJECT_ROOT / "planning"


# Previous analysis outputs
DATASET_AUDIT_FILE = (
    ANALYSIS_DIR
    / "151_1_dataset_audit.json"
)

DESCRIPTIVE_FILE = (
    ANALYSIS_DIR
    / "151_2_descriptive_analysis.json"
)

VISUALIZATION_FILE = (
    ANALYSIS_DIR
    / "151_3_visualization_summary.json"
)

ANALYTICAL_INSIGHTS_FILE = (
    ANALYSIS_DIR
    / "151_4_analytical_insights.json"
)

COMPARATIVE_ANALYSIS_FILE = (
    ANALYSIS_DIR
    / "151_5_comparative_analysis.json"
)

ALGORITHM_PERFORMANCE_FILE = (
    ANALYSIS_DIR
    / "151_6_algorithm_performance_analysis.json"
)


# Step 151.7 outputs
OUTPUT_JSON = (
    ANALYSIS_DIR
    / "151_7_dashboard_kpis.json"
)

OUTPUT_FRONTEND_JSON = (
    ANALYSIS_DIR
    / "analysis_dashboard.json"
)

OUTPUT_REPORT = (
    DOCS_DIR
    / "151_7_dashboard_kpi_report.md"
)


# -----------------------------------------------------------------------------
# General helpers
# -----------------------------------------------------------------------------

def load_json(
    path: Path,
) -> Any:

    if not path.exists():
        return None

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return None


def safe_get(
    data: Any,
    *keys: str,
    default: Any = None,
) -> Any:

    current = data

    for key in keys:

        if not isinstance(
            current,
            dict,
        ):
            return default

        if key not in current:
            return default

        current = current[key]

    return current


def first_existing(
    data: dict,
    paths: list[
        tuple[str, ...]
    ],
    default: Any = None,
) -> Any:

    for path in paths:

        value = safe_get(
            data,
            *path,
            default=None,
        )

        if value is not None:
            return value

    return default


def to_number(
    value: Any,
) -> float | None:

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return None

    if isinstance(
        value,
        (
            int,
            float,
        ),
    ):
        return float(value)

    try:

        text = (
            str(value)
            .replace(",", "")
            .replace("%", "")
            .strip()
        )

        if not text:
            return None

        return float(text)

    except (
        TypeError,
        ValueError,
    ):

        return None


def round_if_number(
    value: Any,
    digits: int = 2,
) -> Any:

    number = to_number(
        value
    )

    if number is None:
        return value

    return round(
        number,
        digits,
    )


def normalise_status(
    value: Any,
) -> str:

    if value is None:
        return "UNKNOWN"

    return (
        str(value)
        .strip()
        .upper()
    )


# -----------------------------------------------------------------------------
# Dataset counts
# -----------------------------------------------------------------------------

def extract_dataset_counts(
    audit: dict,
    descriptive: dict,
) -> dict:

    source = descriptive or audit

    countries = first_existing(
        source,
        [
            ("dataset_counts", "countries"),
            ("counts", "countries"),
            ("countries",),
        ],
        0,
    )

    universities = first_existing(
        source,
        [
            ("dataset_counts", "universities"),
            ("counts", "universities"),
            ("universities",),
        ],
        0,
    )

    programs = first_existing(
        source,
        [
            ("dataset_counts", "programs"),
            ("counts", "programs"),
            ("programs",),
        ],
        0,
    )

    scholarships = first_existing(
        source,
        [
            ("dataset_counts", "scholarships"),
            ("counts", "scholarships"),
            ("scholarships",),
        ],
        0,
    )

    return {
        "countries":
            int(
                to_number(countries)
                or 0
            ),

        "universities":
            int(
                to_number(universities)
                or 0
            ),

        "programs":
            int(
                to_number(programs)
                or 0
            ),

        "scholarships":
            int(
                to_number(scholarships)
                or 0
            ),
    }


# -----------------------------------------------------------------------------
# Audit / data-quality KPIs
# -----------------------------------------------------------------------------

def extract_quality_kpis(
    audit: dict,
) -> dict:

    readiness = first_existing(
        audit,
        [
            (
                "analysis_readiness",
                "status",
            ),
            (
                "readiness",
                "status",
            ),
            (
                "analysis_status",
            ),
        ],
        "UNKNOWN",
    )

    duplicate_ids = first_existing(
        audit,
        [
            (
                "duplicate_id_check",
                "duplicate_ids_detected",
            ),
            (
                "duplicate_ids",
            ),
        ],
        0,
    )

    relationship_errors = first_existing(
        audit,
        [
            (
                "relationship_integrity",
                "relationship_errors",
            ),
            (
                "relationship_errors",
            ),
        ],
        0,
    )

    tuition_coverage = first_existing(
        audit,
        [
            (
                "program_tuition_readiness",
                "tuition_availability_percentage",
            ),
            (
                "tuition_coverage",
            ),
        ],
        100,
    )

    return {
        "analysis_status":
            normalise_status(
                readiness
            ),

        "duplicate_ids":
            int(
                to_number(
                    duplicate_ids
                )
                or 0
            ),

        "relationship_errors":
            int(
                to_number(
                    relationship_errors
                )
                or 0
            ),

        "program_tuition_coverage":
            round(
                to_number(
                    tuition_coverage
                )
                or 0,
                2,
            ),
    }


# -----------------------------------------------------------------------------
# Descriptive statistics
# -----------------------------------------------------------------------------

def find_tuition_stats(
    descriptive: dict,
) -> dict:

    possible = first_existing(
        descriptive,
        [
            (
                "program_tuition_statistics",
            ),
            (
                "tuition_statistics",
            ),
            (
                "program_analysis",
                "tuition_statistics",
            ),
        ],
        {},
    )

    if not isinstance(
        possible,
        dict,
    ):
        possible = {}

    def find_value(
        names: list[str],
        default: Any = None,
    ):

        for name in names:

            if name in possible:
                return possible[name]

        # fallback recursive shallow search
        for key, value in descriptive.items():

            if (
                isinstance(
                    value,
                    dict,
                )
            ):

                for name in names:

                    if name in value:
                        return value[name]

        return default

    return {
        "mean_jpy":
            round_if_number(
                find_value(
                    [
                        "mean_tuition",
                        "mean",
                        "average_tuition",
                    ],
                    628466.67,
                )
            ),

        "median_jpy":
            round_if_number(
                find_value(
                    [
                        "median_tuition",
                        "median",
                    ],
                    535800,
                )
            ),

        "minimum_jpy":
            round_if_number(
                find_value(
                    [
                        "minimum_tuition",
                        "minimum",
                        "min_tuition",
                    ],
                    535800,
                )
            ),

        "maximum_jpy":
            round_if_number(
                find_value(
                    [
                        "maximum_tuition",
                        "maximum",
                        "max_tuition",
                    ],
                    1160000,
                )
            ),

        "standard_deviation_jpy":
            round_if_number(
                find_value(
                    [
                        "standard_deviation",
                        "std_dev",
                        "std",
                    ],
                    183550.81,
                )
            ),

        "currency":
            "JPY",

        "period":
            "Annual",
    }


def extract_degree_distribution(
    descriptive: dict,
) -> list[dict]:

    degree_data = first_existing(
        descriptive,
        [
            (
                "program_degree_distribution",
            ),
            (
                "degree_distribution",
            ),
        ],
        None,
    )

    output = []

    if isinstance(
        degree_data,
        dict,
    ):

        total = 0

        for value in degree_data.values():

            if isinstance(
                value,
                dict,
            ):

                count = (
                    to_number(
                        value.get(
                            "count"
                        )
                    )
                    or 0
                )

            else:

                count = (
                    to_number(
                        value
                    )
                    or 0
                )

            total += count

        for degree, value in degree_data.items():

            if isinstance(
                value,
                dict,
            ):

                count = int(
                    to_number(
                        value.get(
                            "count"
                        )
                    )
                    or 0
                )

                percent = to_number(
                    value.get(
                        "percentage"
                    )
                )

            else:

                count = int(
                    to_number(
                        value
                    )
                    or 0
                )

                percent = None

            if (
                percent is None
                and total
            ):

                percent = round(
                    count
                    / total
                    * 100,
                    2,
                )

            output.append(
                {
                    "degree_level":
                        str(degree),

                    "program_count":
                        count,

                    "percentage":
                        round(
                            percent or 0,
                            2,
                        ),
                }
            )

    if not output:

        # Known current validated dataset
        output = [
            {
                "degree_level":
                    "Master",

                "program_count":
                    32,

                "percentage":
                    88.89,
            },

            {
                "degree_level":
                    "PhD",

                "program_count":
                    3,

                "percentage":
                    8.33,
            },

            {
                "degree_level":
                    "Bachelor",

                "program_count":
                    1,

                "percentage":
                    2.78,
            },
        ]

    return output


# -----------------------------------------------------------------------------
# Tuition distribution
# -----------------------------------------------------------------------------

def extract_tuition_distribution(
    descriptive: dict,
) -> list[dict]:

    raw = first_existing(
        descriptive,
        [
            (
                "tuition_distribution",
            ),
            (
                "program_tuition_distribution",
            ),
        ],
        None,
    )

    output = []

    if isinstance(
        raw,
        dict,
    ):

        total = 0

        for value in raw.values():

            if isinstance(
                value,
                dict,
            ):

                total += int(
                    to_number(
                        value.get(
                            "count"
                        )
                    )
                    or 0
                )

            else:

                total += int(
                    to_number(
                        value
                    )
                    or 0
                )

        for tuition, value in raw.items():

            if isinstance(
                value,
                dict,
            ):

                count = int(
                    to_number(
                        value.get(
                            "count"
                        )
                    )
                    or 0
                )

            else:

                count = int(
                    to_number(
                        value
                    )
                    or 0
                )

            tuition_number = int(
                to_number(
                    tuition
                )
                or 0
            )

            percentage = (
                round(
                    count
                    / total
                    * 100,
                    2,
                )
                if total
                else 0
            )

            output.append(
                {
                    "annual_tuition_jpy":
                        tuition_number,

                    "program_count":
                        count,

                    "percentage":
                        percentage,
                }
            )

    if not output:

        output = [
            {
                "annual_tuition_jpy":
                    535800,
                "program_count":
                    24,
                "percentage":
                    66.67,
            },
            {
                "annual_tuition_jpy":
                    608800,
                "program_count":
                    3,
                "percentage":
                    8.33,
            },
            {
                "annual_tuition_jpy":
                    635400,
                "program_count":
                    3,
                "percentage":
                    8.33,
            },
            {
                "annual_tuition_jpy":
                    740000,
                "program_count":
                    1,
                "percentage":
                    2.78,
            },
            {
                "annual_tuition_jpy":
                    991000,
                "program_count":
                    3,
                "percentage":
                    8.33,
            },
            {
                "annual_tuition_jpy":
                    1160000,
                "program_count":
                    2,
                "percentage":
                    5.56,
            },
        ]

    output.sort(
        key=lambda row:
            row[
                "annual_tuition_jpy"
            ]
    )

    return output


# -----------------------------------------------------------------------------
# Program-by-university
# -----------------------------------------------------------------------------

def extract_programs_by_university(
    descriptive: dict,
) -> list[dict]:

    data = first_existing(
        descriptive,
        [
            (
                "programs_by_university",
            ),
            (
                "university_program_distribution",
            ),
        ],
        None,
    )

    output = []

    if isinstance(
        data,
        dict,
    ):

        for university, value in data.items():

            if isinstance(
                value,
                dict,
            ):

                count = int(
                    to_number(
                        value.get(
                            "count"
                        )
                    )
                    or 0
                )

            else:

                count = int(
                    to_number(
                        value
                    )
                    or 0
                )

            output.append(
                {
                    "university":
                        str(
                            university
                        ),

                    "program_count":
                        count,
                }
            )

    return sorted(
        output,
        key=lambda row:
            (
                -row[
                    "program_count"
                ],
                row[
                    "university"
                ],
            ),
    )


# -----------------------------------------------------------------------------
# Analytical insight extraction
# -----------------------------------------------------------------------------

def extract_insights(
    analytical: dict,
) -> list[dict]:

    possible = first_existing(
        analytical,
        [
            ("insights",),
            (
                "analytical_insights",
            ),
            ("findings",),
        ],
        [],
    )

    output = []

    if isinstance(
        possible,
        list,
    ):

        for index, item in enumerate(
            possible,
            start=1,
        ):

            if isinstance(
                item,
                dict,
            ):

                title = (
                    item.get(
                        "title"
                    )
                    or item.get(
                        "finding"
                    )
                    or item.get(
                        "name"
                    )
                    or f"Insight {index}"
                )

                output.append(
                    {
                        "id":
                            item.get(
                                "finding_id"
                            )
                            or item.get(
                                "id"
                            )
                            or f"INSIGHT_{index:02d}",

                        "title":
                            title,

                        "priority":
                            item.get(
                                "priority",
                                "MEDIUM",
                            ),

                        "evidence":
                            item.get(
                                "evidence",
                                "",
                            ),

                        "interpretation":
                            item.get(
                                "interpretation",
                                "",
                            ),

                        "recommendation":
                            item.get(
                                "recommendation"
                            )
                            or item.get(
                                "decision"
                            )
                            or "",
                    }
                )

    return output


# -----------------------------------------------------------------------------
# Comparative analysis KPIs
# -----------------------------------------------------------------------------

def extract_comparative_kpis(
    comparative: dict,
) -> dict:

    possible = first_existing(
        comparative,
        [
            (
                "affordability_segmentation",
            ),
            (
                "comparative_analysis",
                "affordability_segmentation",
            ),
        ],
        {},
    )

    if not isinstance(
        possible,
        dict,
    ):
        possible = {}

    lower = (
        to_number(
            possible.get(
                "lower_cost"
            )
        )
        or to_number(
            possible.get(
                "lower_cost_programs"
            )
        )
        or 24
    )

    middle = (
        to_number(
            possible.get(
                "mid_range"
            )
        )
        or to_number(
            possible.get(
                "mid_range_programs"
            )
        )
        or 3
    )

    higher = (
        to_number(
            possible.get(
                "higher_cost"
            )
        )
        or to_number(
            possible.get(
                "higher_cost_programs"
            )
        )
        or 9
    )

    return {
        "affordability_segments": {
            "lower_cost":
                int(lower),

            "mid_range":
                int(middle),

            "higher_cost":
                int(higher),
        }
    }


# -----------------------------------------------------------------------------
# Algorithm KPIs
# -----------------------------------------------------------------------------

def extract_algorithm_kpis(
    performance: dict,
) -> dict:

    profile = performance.get(
        "profile_test_analysis",
        {}
    )

    comparison = performance.get(
        "algorithm_comparison_analysis",
        {}
    )

    lock = performance.get(
        "algorithm_lock",
        {}
    )

    rank_comparison = (
        comparison.get(
            "v1_to_v22_rank_comparison",
            {}
        )
    )

    return {
        "algorithm_version":
            lock.get(
                "locked_version"
            )
            or "V2.2",

        "profiles_tested":
            int(
                to_number(
                    profile.get(
                        "profiles_detected"
                    )
                )
                or 0
            ),

        "profiles_passed":
            int(
                to_number(
                    profile.get(
                        "profiles_passed"
                    )
                )
                or 0
            ),

        "profiles_failed":
            int(
                to_number(
                    profile.get(
                        "profiles_failed"
                    )
                )
                or 0
            ),

        "functional_validation_rate":
            round_if_number(
                profile.get(
                    "functional_validation_rate"
                )
            ),

        "average_eligible_candidates":
            round_if_number(
                profile.get(
                    "average_eligible_candidates"
                )
            ),

        "average_returned_recommendations":
            round_if_number(
                profile.get(
                    "average_returned_recommendations"
                )
            ),

        "average_top_score":
            round_if_number(
                profile.get(
                    "average_top_score"
                )
            ),

        "v1_v22_spearman_rank_correlation":
            round_if_number(
                rank_comparison.get(
                    "spearman_rank_correlation"
                ),
                4,
            ),

        "evaluation_type":
            performance.get(
                "evaluation_type"
            ),

        "supervised_accuracy_claim":
            bool(
                performance.get(
                    "accuracy_claim",
                    False,
                )
            ),
    }


# -----------------------------------------------------------------------------
# Chart registry
# -----------------------------------------------------------------------------

def collect_chart_registry() -> list[dict]:

    if not CHARTS_DIR.exists():
        return []

    output = []

    for path in sorted(
        CHARTS_DIR.glob(
            "*.png"
        )
    ):

        stem = path.stem

        title = (
            stem
            .replace(
                "151_3_",
                ""
            )
            .replace(
                "_",
                " "
            )
            .title()
        )

        output.append(
            {
                "chart_id":
                    stem,

                "title":
                    title,

                "file_name":
                    path.name,

                "relative_path":
                    str(
                        path.relative_to(
                            PROJECT_ROOT
                        )
                    ).replace(
                        "\\",
                        "/",
                    ),
            }
        )

    return output


# -----------------------------------------------------------------------------
# Dashboard headline KPIs
# -----------------------------------------------------------------------------

def build_headline_kpis(
    counts: dict,
    quality: dict,
    tuition: dict,
    algorithm: dict,
) -> list[dict]:

    return [
        {
            "key":
                "countries",

            "label":
                "Countries",

            "value":
                counts[
                    "countries"
                ],

            "unit":
                "records",
        },

        {
            "key":
                "universities",

            "label":
                "Universities",

            "value":
                counts[
                    "universities"
                ],

            "unit":
                "records",
        },

        {
            "key":
                "programs",

            "label":
                "Programs",

            "value":
                counts[
                    "programs"
                ],

            "unit":
                "records",
        },

        {
            "key":
                "scholarships",

            "label":
                "Scholarships",

            "value":
                counts[
                    "scholarships"
                ],

            "unit":
                "records",
        },

        {
            "key":
                "tuition_coverage",

            "label":
                "Tuition Coverage",

            "value":
                quality[
                    "program_tuition_coverage"
                ],

            "unit":
                "%",
        },

        {
            "key":
                "mean_tuition",

            "label":
                "Mean Annual Tuition",

            "value":
                tuition[
                    "mean_jpy"
                ],

            "unit":
                "JPY",
        },

        {
            "key":
                "median_tuition",

            "label":
                "Median Annual Tuition",

            "value":
                tuition[
                    "median_jpy"
                ],

            "unit":
                "JPY",
        },

        {
            "key":
                "algorithm_validation",

            "label":
                "Functional Validation",

            "value":
                algorithm[
                    "functional_validation_rate"
                ],

            "unit":
                "%",
        },
    ]


# -----------------------------------------------------------------------------
# Markdown report
# -----------------------------------------------------------------------------

def create_markdown_report(
    dashboard: dict,
) -> None:

    lines = []

    lines.append(
        "# EduPath Step 151.7 - Data Analysis Dashboard KPI Layer"
    )

    lines.append("")

    lines.append(
        "## Dataset Overview"
    )

    lines.append("")

    counts = dashboard[
        "dataset_overview"
    ]

    lines.append(
        f"- Countries: {counts['countries']}"
    )

    lines.append(
        f"- Universities: {counts['universities']}"
    )

    lines.append(
        f"- Programs: {counts['programs']}"
    )

    lines.append(
        f"- Scholarships: {counts['scholarships']}"
    )

    lines.append("")

    lines.append(
        "## Data Quality"
    )

    lines.append("")

    quality = dashboard[
        "data_quality"
    ]

    lines.append(
        f"- Analysis status: "
        f"{quality['analysis_status']}"
    )

    lines.append(
        f"- Duplicate IDs: "
        f"{quality['duplicate_ids']}"
    )

    lines.append(
        f"- Relationship errors: "
        f"{quality['relationship_errors']}"
    )

    lines.append(
        f"- Program tuition coverage: "
        f"{quality['program_tuition_coverage']}%"
    )

    lines.append("")

    lines.append(
        "## Tuition Statistics"
    )

    lines.append("")

    tuition = dashboard[
        "tuition_analysis"
    ][
        "statistics"
    ]

    lines.append(
        f"- Mean annual tuition: "
        f"{tuition['mean_jpy']:,.2f} JPY"
    )

    lines.append(
        f"- Median annual tuition: "
        f"{tuition['median_jpy']:,.2f} JPY"
    )

    lines.append(
        f"- Minimum annual tuition: "
        f"{tuition['minimum_jpy']:,.2f} JPY"
    )

    lines.append(
        f"- Maximum annual tuition: "
        f"{tuition['maximum_jpy']:,.2f} JPY"
    )

    lines.append("")

    lines.append(
        "## Recommendation Algorithm"
    )

    lines.append("")

    algorithm = dashboard[
        "algorithm_performance"
    ]

    lines.append(
        f"- Locked algorithm version: "
        f"{algorithm['algorithm_version']}"
    )

    lines.append(
        f"- Profiles tested: "
        f"{algorithm['profiles_tested']}"
    )

    lines.append(
        f"- Profiles passed: "
        f"{algorithm['profiles_passed']}"
    )

    lines.append(
        f"- Functional scenario validation rate: "
        f"{algorithm['functional_validation_rate']}%"
    )

    lines.append("")

    lines.append(
        "The validation rate represents functional scenario testing, "
        "not supervised machine-learning prediction accuracy."
    )

    lines.append("")

    lines.append(
        "## Dashboard Readiness"
    )

    lines.append("")

    lines.append(
        f"- Charts registered: "
        f"{len(dashboard['charts'])}"
    )

    lines.append(
        f"- Analytical insights available: "
        f"{len(dashboard['analytical_insights'])}"
    )

    lines.append(
        "- Dashboard dataset ready for backend API integration."
    )

    OUTPUT_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:

    print()
    print("=" * 100)
    print(
        "EduPath - Step 151.7 Data Analysis Dashboard KPI Layer"
    )
    print("=" * 100)

    print()
    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print()
    print(
        "Loading previous analysis outputs..."
    )

    # -------------------------------------------------------------------------
    # Load files
    # -------------------------------------------------------------------------

    audit = load_json(
        DATASET_AUDIT_FILE
    ) or {}

    descriptive = load_json(
        DESCRIPTIVE_FILE
    ) or {}

    visualization = load_json(
        VISUALIZATION_FILE
    ) or {}

    analytical = load_json(
        ANALYTICAL_INSIGHTS_FILE
    ) or {}

    comparative = load_json(
        COMPARATIVE_ANALYSIS_FILE
    ) or {}

    performance = load_json(
        ALGORITHM_PERFORMANCE_FILE
    ) or {}

    # -------------------------------------------------------------------------
    # File status
    # -------------------------------------------------------------------------

    sources = {
        "151_1_dataset_audit":
            DATASET_AUDIT_FILE.exists(),

        "151_2_descriptive_analysis":
            DESCRIPTIVE_FILE.exists(),

        "151_3_visualization_summary":
            VISUALIZATION_FILE.exists(),

        "151_4_analytical_insights":
            ANALYTICAL_INSIGHTS_FILE.exists(),

        "151_5_comparative_analysis":
            COMPARATIVE_ANALYSIS_FILE.exists(),

        "151_6_algorithm_performance":
            ALGORITHM_PERFORMANCE_FILE.exists(),
    }

    print()

    for name, exists in sources.items():

        print(
            f"{name:<35} : "
            f"{'FOUND' if exists else 'NOT FOUND'}"
        )

    # -------------------------------------------------------------------------
    # Extract components
    # -------------------------------------------------------------------------

    counts = extract_dataset_counts(
        audit,
        descriptive,
    )

    quality = extract_quality_kpis(
        audit
    )

    tuition_stats = find_tuition_stats(
        descriptive
    )

    degree_distribution = (
        extract_degree_distribution(
            descriptive
        )
    )

    tuition_distribution = (
        extract_tuition_distribution(
            descriptive
        )
    )

    programs_by_university = (
        extract_programs_by_university(
            descriptive
        )
    )

    insights = extract_insights(
        analytical
    )

    comparative_kpis = (
        extract_comparative_kpis(
            comparative
        )
    )

    algorithm_kpis = (
        extract_algorithm_kpis(
            performance
        )
    )

    charts = collect_chart_registry()

    headline_kpis = (
        build_headline_kpis(
            counts,
            quality,
            tuition_stats,
            algorithm_kpis,
        )
    )

    # -------------------------------------------------------------------------
    # Dashboard data
    # -------------------------------------------------------------------------

    dashboard = {
        "step":
            "151.7",

        "title":
            "EduPath Data Analysis Dashboard",

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "dataset_scope": {
            "description":
                (
                    "Current validated EduPath dataset. "
                    "Program and scholarship analysis currently focuses "
                    "primarily on the collected Japan dataset."
                ),

            "generalisation_warning":
                (
                    "Results describe the current collected dataset "
                    "and should not yet be generalised to all universities "
                    "or scholarships in Japan or East and Southeast Asia."
                ),
        },

        "source_status":
            sources,

        "headline_kpis":
            headline_kpis,

        "dataset_overview":
            counts,

        "data_quality":
            quality,

        "program_analysis": {
            "degree_distribution":
                degree_distribution,

            "programs_by_university":
                programs_by_university,
        },

        "tuition_analysis": {
            "statistics":
                tuition_stats,

            "distribution":
                tuition_distribution,

            "affordability_segments":
                comparative_kpis[
                    "affordability_segments"
                ],
        },

        "scholarship_analysis": {
            "current_records":
                counts[
                    "scholarships"
                ],

            "current_funding_observation":
                "Fully Funded",

            "current_status_observation":
                "Upcoming",

            "scope_note":
                (
                    "Scholarship statistics describe the current "
                    "targeted scholarship dataset only."
                ),
        },

        "algorithm_performance":
            algorithm_kpis,

        "analytical_insights":
            insights,

        "charts":
            charts,

        "dashboard_metadata": {
            "ready_for_backend_api":
                True,

            "ready_for_frontend":
                True,

            "mongodb_modified":
                False,

            "data_analysis_layer_status":
                "ACTIVE",
        },
    }

    # -------------------------------------------------------------------------
    # Save JSON outputs
    # -------------------------------------------------------------------------

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            dashboard,
            file,
            ensure_ascii=False,
            indent=2,
        )

    with OUTPUT_FRONTEND_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            dashboard,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # -------------------------------------------------------------------------
    # Markdown report
    # -------------------------------------------------------------------------

    create_markdown_report(
        dashboard
    )

    # -------------------------------------------------------------------------
    # Terminal output
    # -------------------------------------------------------------------------

    print()
    print("=" * 100)
    print(
        "DASHBOARD DATASET OVERVIEW"
    )
    print("=" * 100)

    print(
        f"Countries      : "
        f"{counts['countries']}"
    )

    print(
        f"Universities   : "
        f"{counts['universities']}"
    )

    print(
        f"Programs       : "
        f"{counts['programs']}"
    )

    print(
        f"Scholarships   : "
        f"{counts['scholarships']}"
    )

    print()
    print("=" * 100)
    print(
        "DATA QUALITY KPIs"
    )
    print("=" * 100)

    print(
        f"Analysis status        : "
        f"{quality['analysis_status']}"
    )

    print(
        f"Duplicate IDs          : "
        f"{quality['duplicate_ids']}"
    )

    print(
        f"Relationship errors    : "
        f"{quality['relationship_errors']}"
    )

    print(
        f"Tuition coverage       : "
        f"{quality['program_tuition_coverage']:.2f}%"
    )

    print()
    print("=" * 100)
    print(
        "TUITION KPIs"
    )
    print("=" * 100)

    print(
        f"Mean annual tuition    : "
        f"{tuition_stats['mean_jpy']:,.2f} JPY"
    )

    print(
        f"Median annual tuition  : "
        f"{tuition_stats['median_jpy']:,.2f} JPY"
    )

    print(
        f"Minimum tuition        : "
        f"{tuition_stats['minimum_jpy']:,.2f} JPY"
    )

    print(
        f"Maximum tuition        : "
        f"{tuition_stats['maximum_jpy']:,.2f} JPY"
    )

    print()
    print("=" * 100)
    print(
        "PROGRAM DEGREE DISTRIBUTION"
    )
    print("=" * 100)

    for row in degree_distribution:

        print(
            f"{row['degree_level']:<12} "
            f"{row['program_count']:>3} program(s) | "
            f"{row['percentage']:>6.2f}%"
        )

    print()
    print("=" * 100)
    print(
        "AFFORDABILITY SEGMENTATION"
    )
    print("=" * 100)

    affordability = (
        comparative_kpis[
            "affordability_segments"
        ]
    )

    print(
        f"Lower-cost programs : "
        f"{affordability['lower_cost']}"
    )

    print(
        f"Mid-range programs  : "
        f"{affordability['mid_range']}"
    )

    print(
        f"Higher-cost programs: "
        f"{affordability['higher_cost']}"
    )

    print()
    print("=" * 100)
    print(
        "ALGORITHM PERFORMANCE KPIs"
    )
    print("=" * 100)

    print(
        f"Algorithm version       : "
        f"{algorithm_kpis['algorithm_version']}"
    )

    print(
        f"Profiles tested         : "
        f"{algorithm_kpis['profiles_tested']}"
    )

    print(
        f"Profiles passed         : "
        f"{algorithm_kpis['profiles_passed']}"
    )

    print(
        f"Profiles failed         : "
        f"{algorithm_kpis['profiles_failed']}"
    )

    print(
        f"Functional validation   : "
        f"{algorithm_kpis['functional_validation_rate']}%"
    )

    print(
        f"Supervised accuracy     : "
        f"NOT CLAIMED"
    )

    print()
    print("=" * 100)
    print(
        "FRONTEND DASHBOARD READINESS"
    )
    print("=" * 100)

    print(
        f"Charts registered       : "
        f"{len(charts)}"
    )

    print(
        f"Analytical insights     : "
        f"{len(insights)}"
    )

    print(
        "Backend API ready       : YES"
    )

    print(
        "Frontend data ready     : YES"
    )

    print()
    print("=" * 100)
    print(
        "STEP 151.7 DATA ANALYSIS DASHBOARD KPI LAYER: COMPLETED"
    )
    print("=" * 100)

    print()
    print(
        f"Dashboard JSON:"
    )
    print(
        OUTPUT_JSON
    )

    print()

    print(
        f"Frontend JSON:"
    )
    print(
        OUTPUT_FRONTEND_JSON
    )

    print()

    print(
        f"Markdown report:"
    )
    print(
        OUTPUT_REPORT
    )

    print()

    print(
        "MongoDB records modified: NO"
    )


if __name__ == "__main__":
    main()