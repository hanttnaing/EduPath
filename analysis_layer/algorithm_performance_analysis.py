from __future__ import annotations

import csv
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =============================================================================
# EduPath
# Step 151.6 - Scholarship Recommendation Algorithm Performance Analysis
#
# This analysis uses outputs already produced by:
#
#   Step 150.x / V2.2 recommendation development
#   Step 150.x algorithm comparison
#   Step 150.x multi-profile scenario testing
#   Step 150.x final algorithm lock
#
# IMPORTANT:
#   - This is an ANALYSIS layer.
#   - MongoDB is NOT modified.
#   - "Validation pass rate" is NOT claimed as ML prediction accuracy.
#   - There is currently no labelled human relevance ground-truth dataset.
# =============================================================================


# -----------------------------------------------------------------------------
# Project paths
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PLANNING_DIR = PROJECT_ROOT / "planning"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
DOCS_DIR = PROJECT_ROOT / "docs"


# Existing reports from previous completed steps
ALGORITHM_COMPARISON_CSV = (
    PLANNING_DIR
    / "30_scholarship_algorithm_comparison.csv"
)

ALGORITHM_COMPARISON_JSON = (
    CLEANED_DIR
    / "scholarship_algorithm_comparison.json"
)

PROFILE_TEST_CSV = (
    PLANNING_DIR
    / "31_scholarship_v22_profile_tests.csv"
)

PROFILE_TEST_JSON = (
    CLEANED_DIR
    / "scholarship_v22_profile_tests.json"
)

ALGORITHM_LOCK_JSON = (
    PLANNING_DIR
    / "32_scholarship_algorithm_lock_v22.json"
)


# New Step 151.6 outputs
OUTPUT_JSON = (
    ANALYSIS_DIR
    / "151_6_algorithm_performance_analysis.json"
)

OUTPUT_CSV = (
    PLANNING_DIR
    / "38_algorithm_performance_analysis.csv"
)

OUTPUT_MD = (
    DOCS_DIR
    / "151_6_algorithm_performance_report.md"
)


# -----------------------------------------------------------------------------
# General helpers
# -----------------------------------------------------------------------------

def normalize_key(value: Any) -> str:
    """
    Convert column / dictionary keys into a comparison-friendly format.
    Example:
        "V2.2 Ranking Score"
        -> "v22rankingscore"
    """

    if value is None:
        return ""

    return re.sub(
        r"[^a-z0-9]+",
        "",
        str(value).lower(),
    )


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def to_float(value: Any) -> float | None:
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
        text
        .replace("%", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(text)

    except ValueError:
        return None


def to_int(value: Any) -> int | None:
    number = to_float(value)

    if number is None:
        return None

    return int(number)


def percentage(
    part: int | float,
    whole: int | float,
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


def parse_pass(value: Any) -> bool | None:
    """
    Convert PASS / TRUE / SUCCESS etc. into Boolean.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return value

    text = normalize_key(value)

    if text in {
        "pass",
        "passed",
        "true",
        "success",
        "successful",
        "ok",
        "valid",
        "1",
    }:
        return True

    if text in {
        "fail",
        "failed",
        "false",
        "error",
        "invalid",
        "0",
    }:
        return False

    return None


def get_value(
    row: dict,
    aliases: list[str],
) -> Any:
    """
    Flexible field lookup.
    """

    normalized_aliases = {
        normalize_key(alias)
        for alias in aliases
    }

    for key, value in row.items():

        if normalize_key(key) in normalized_aliases:
            return value

    return None


# -----------------------------------------------------------------------------
# Load reports
# -----------------------------------------------------------------------------

def read_csv_file(
    path: Path,
) -> list[dict]:

    if not path.exists():
        return []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


def read_json_file(
    path: Path,
) -> Any:

    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# -----------------------------------------------------------------------------
# Profile-test analysis
# -----------------------------------------------------------------------------

PROFILE_ALIASES = [
    "profile_id",
    "profile",
    "profile_code",
    "profile_name",
    "test_profile",
    "test_case",
]

PASS_ALIASES = [
    "validation",
    "validation_status",
    "validation_result",
    "passed",
    "pass",
    "result",
]

ELIGIBLE_ALIASES = [
    "eligible_candidates",
    "eligible_candidate_count",
    "eligible_count",
]

RECOMMENDATION_ALIASES = [
    "returned_recommendations",
    "recommendations_returned",
    "recommendation_count",
    "returned_count",
    "recommendations",
]

TOP_SCORE_ALIASES = [
    "top_ranking_score",
    "top_match_score",
    "top_score",
    "ranking_score",
    "match_score",
]


def analyse_profile_tests(
    rows: list[dict],
) -> dict[str, Any]:

    profiles: dict[str, dict] = {}

    for index, row in enumerate(
        rows,
        start=1,
    ):

        profile_value = get_value(
            row,
            PROFILE_ALIASES,
        )

        profile_id = (
            clean_text(profile_value)
            or f"profile_row_{index:03d}"
        )

        if profile_id not in profiles:

            profiles[profile_id] = {
                "profile_id": profile_id,
                "pass_values": [],
                "eligible_candidates": [],
                "returned_recommendations": [],
                "scores": [],
            }

        record = profiles[profile_id]

        pass_value = parse_pass(
            get_value(
                row,
                PASS_ALIASES,
            )
        )

        if pass_value is not None:
            record["pass_values"].append(
                pass_value
            )

        eligible = to_int(
            get_value(
                row,
                ELIGIBLE_ALIASES,
            )
        )

        if eligible is not None:
            record[
                "eligible_candidates"
            ].append(
                eligible
            )

        recommendations = to_int(
            get_value(
                row,
                RECOMMENDATION_ALIASES,
            )
        )

        if recommendations is not None:
            record[
                "returned_recommendations"
            ].append(
                recommendations
            )

        score = to_float(
            get_value(
                row,
                TOP_SCORE_ALIASES,
            )
        )

        if score is not None:
            record["scores"].append(
                score
            )

    final_profiles = []

    passed_count = 0
    failed_count = 0
    unknown_count = 0

    recommendation_counts = []
    eligible_counts = []
    top_scores = []

    for profile_id, values in profiles.items():

        passes = values[
            "pass_values"
        ]

        if passes:

            profile_passed = all(
                passes
            )

        else:
            profile_passed = None

        if profile_passed is True:
            passed_count += 1

        elif profile_passed is False:
            failed_count += 1

        else:
            unknown_count += 1

        eligible = (
            max(
                values[
                    "eligible_candidates"
                ]
            )
            if values[
                "eligible_candidates"
            ]
            else None
        )

        recommendations = (
            max(
                values[
                    "returned_recommendations"
                ]
            )
            if values[
                "returned_recommendations"
            ]
            else None
        )

        top_score = (
            max(
                values["scores"]
            )
            if values["scores"]
            else None
        )

        if eligible is not None:
            eligible_counts.append(
                float(eligible)
            )

        if recommendations is not None:
            recommendation_counts.append(
                float(recommendations)
            )

        if top_score is not None:
            top_scores.append(
                top_score
            )

        final_profiles.append(
            {
                "profile_id":
                    profile_id,
                "validation_passed":
                    profile_passed,
                "eligible_candidates":
                    eligible,
                "returned_recommendations":
                    recommendations,
                "top_score":
                    top_score,
            }
        )

    total_profiles = len(
        final_profiles
    )

    explicit_results = (
        passed_count
        + failed_count
    )

    return {
        "profiles_detected":
            total_profiles,
        "profiles_passed":
            passed_count,
        "profiles_failed":
            failed_count,
        "profiles_validation_unknown":
            unknown_count,

        "functional_validation_rate":
            (
                percentage(
                    passed_count,
                    explicit_results,
                )
                if explicit_results
                else None
            ),

        "average_eligible_candidates":
            safe_mean(
                eligible_counts
            ),

        "average_returned_recommendations":
            safe_mean(
                recommendation_counts
            ),

        "average_top_score":
            safe_mean(
                top_scores
            ),

        "minimum_top_score":
            safe_min(
                top_scores
            ),

        "maximum_top_score":
            safe_max(
                top_scores
            ),

        "profiles":
            final_profiles,
    }


# -----------------------------------------------------------------------------
# Algorithm comparison analysis
# -----------------------------------------------------------------------------

def detect_version(
    column_name: str,
) -> str | None:

    key = normalize_key(
        column_name
    )

    if "v22" in key:
        return "V2.2"

    if "v21" in key:
        return "V2.1"

    if key.startswith("v2"):
        return "V2"

    if key.startswith("v1"):
        return "V1"

    return None


def detect_metric(
    column_name: str,
) -> str | None:

    key = normalize_key(
        column_name
    )

    if "dataconfidence" in key:
        return "data_confidence"

    if "eligibilityconfidence" in key:
        return "eligibility_confidence"

    if "rankingscore" in key:
        return "ranking_score"

    if "fitscore" in key:
        return "fit_score"

    if (
        key.endswith("rank")
        or "rankposition" in key
    ):
        return "rank"

    if "score" in key:
        return "score"

    return None


def numeric_column_values(
    rows: list[dict],
    column: str,
) -> list[float]:

    values = []

    for row in rows:

        number = to_float(
            row.get(
                column
            )
        )

        if number is not None:
            values.append(
                number
            )

    return values


def find_version_columns(
    rows: list[dict],
) -> dict[str, dict[str, str]]:

    if not rows:
        return {}

    headers = list(
        rows[0].keys()
    )

    result: dict[
        str,
        dict[str, str],
    ] = {}

    for header in headers:

        version = detect_version(
            header
        )

        metric = detect_metric(
            header
        )

        if not version or not metric:
            continue

        result.setdefault(
            version,
            {},
        )

        result[
            version
        ][
            metric
        ] = header

    return result


def spearman_rank_correlation(
    x: list[float],
    y: list[float],
) -> float | None:
    """
    Spearman correlation for rank-position data.
    Suitable here because algorithm comparison rows are already ranked.
    """

    if len(x) != len(y):
        return None

    n = len(x)

    if n < 2:
        return None

    differences_squared = sum(
        (a - b) ** 2
        for a, b in zip(
            x,
            y,
        )
    )

    denominator = (
        n
        * (
            n ** 2 - 1
        )
    )

    if denominator == 0:
        return None

    rho = (
        1
        - (
            6
            * differences_squared
            / denominator
        )
    )

    return round(
        rho,
        4,
    )


def analyse_algorithm_comparison(
    rows: list[dict],
) -> dict[str, Any]:

    columns = find_version_columns(
        rows
    )

    versions = {}

    for version, metrics in columns.items():

        version_result = {}

        for metric, column in metrics.items():

            values = (
                numeric_column_values(
                    rows,
                    column,
                )
            )

            version_result[
                metric
            ] = {
                "column":
                    column,
                "count":
                    len(values),
                "mean":
                    safe_mean(
                        values
                    ),
                "minimum":
                    safe_min(
                        values
                    ),
                "maximum":
                    safe_max(
                        values
                    ),
            }

        versions[
            version
        ] = version_result

    # -------------------------------------------------------------------------
    # Ranking stability between V1 and V2.2
    # -------------------------------------------------------------------------

    rank_correlation = None
    compared_rank_rows = 0

    v1_rank_col = (
        columns
        .get(
            "V1",
            {},
        )
        .get(
            "rank"
        )
    )

    v22_rank_col = (
        columns
        .get(
            "V2.2",
            {},
        )
        .get(
            "rank"
        )
    )

    if (
        v1_rank_col
        and v22_rank_col
    ):

        v1_ranks = []
        v22_ranks = []

        for row in rows:

            old_rank = to_float(
                row.get(
                    v1_rank_col
                )
            )

            new_rank = to_float(
                row.get(
                    v22_rank_col
                )
            )

            if (
                old_rank is not None
                and new_rank is not None
            ):

                v1_ranks.append(
                    old_rank
                )

                v22_ranks.append(
                    new_rank
                )

        compared_rank_rows = len(
            v1_ranks
        )

        rank_correlation = (
            spearman_rank_correlation(
                v1_ranks,
                v22_ranks,
            )
        )

    return {
        "comparison_rows":
            len(rows),

        "detected_columns":
            columns,

        "version_statistics":
            versions,

        "v1_to_v22_rank_comparison": {
            "rows_compared":
                compared_rank_rows,
            "spearman_rank_correlation":
                rank_correlation,
        },
    }


# -----------------------------------------------------------------------------
# Locked version information
# -----------------------------------------------------------------------------

def analyse_lock_manifest(
    lock_data: Any,
) -> dict[str, Any]:

    if not isinstance(
        lock_data,
        dict,
    ):

        return {
            "available": False,
            "locked_version": None,
            "sha256": None,
        }

    locked_version = None
    sha256_value = None

    for key, value in lock_data.items():

        normalized = normalize_key(
            key
        )

        if (
            "version" in normalized
            and locked_version is None
        ):
            locked_version = value

        if (
            "sha256" in normalized
            or "hash" in normalized
        ):
            sha256_value = value

    return {
        "available": True,
        "locked_version":
            locked_version
            or "V2.2",
        "sha256":
            sha256_value,
    }


# -----------------------------------------------------------------------------
# Interpretation
# -----------------------------------------------------------------------------

def build_findings(
    profile_analysis: dict,
    comparison_analysis: dict,
    lock_analysis: dict,
) -> list[dict]:

    findings = []

    # -------------------------------------------------------------------------
    # 1. Multi-profile functional robustness
    # -------------------------------------------------------------------------

    pass_rate = profile_analysis.get(
        "functional_validation_rate"
    )

    passed = profile_analysis.get(
        "profiles_passed",
        0,
    )

    failed = profile_analysis.get(
        "profiles_failed",
        0,
    )

    total = profile_analysis.get(
        "profiles_detected",
        0,
    )

    if pass_rate is not None:

        evidence = (
            f"{passed} of {passed + failed} profiles with explicit "
            f"validation results passed "
            f"({pass_rate:.2f}% functional scenario validation rate)."
        )

    else:

        evidence = (
            f"{total} profile record(s) were detected, but an explicit "
            f"PASS/FAIL field could not be identified in the report."
        )

    findings.append(
        {
            "finding_id":
                "ALG_01",

            "title":
                "Multi-Profile Functional Robustness",

            "evidence":
                evidence,

            "interpretation":
                (
                    "The recommendation engine has been tested across "
                    "multiple user-profile scenarios rather than only "
                    "one manually selected profile."
                ),

            "decision":
                (
                    "Use V2.2 as the current validated recommendation "
                    "baseline while continuing to add more test profiles "
                    "as the dataset grows."
                ),
        }
    )

    # -------------------------------------------------------------------------
    # 2. Hard-rule behavior
    # -------------------------------------------------------------------------

    zero_return_profiles = [
        row
        for row in profile_analysis.get(
            "profiles",
            [],
        )
        if row.get(
            "returned_recommendations"
        ) == 0
    ]

    findings.append(
        {
            "finding_id":
                "ALG_02",

            "title":
                "Hard-Rule Rejection Behaviour",

            "evidence":
                (
                    f"{len(zero_return_profiles)} detected test profile(s) "
                    f"returned zero recommendations."
                ),

            "interpretation":
                (
                    "Returning zero recommendations can be correct when "
                    "a profile fails hard eligibility or country rules. "
                    "The system is therefore not designed to force a "
                    "recommendation for every user."
                ),

            "decision":
                (
                    "Keep hard eligibility checks separate from soft "
                    "ranking scores so ineligible scholarships cannot "
                    "rank highly simply because of field similarity."
                ),
        }
    )

    # -------------------------------------------------------------------------
    # 3. Ranking evolution
    # -------------------------------------------------------------------------

    rank_info = comparison_analysis.get(
        "v1_to_v22_rank_comparison",
        {},
    )

    rho = rank_info.get(
        "spearman_rank_correlation"
    )

    rows_compared = rank_info.get(
        "rows_compared",
        0,
    )

    if rho is None:

        ranking_evidence = (
            "V1-to-V2.2 rank correlation could not be calculated "
            "from the available comparison columns."
        )

    else:

        ranking_evidence = (
            f"V1 and V2.2 ranking positions were compared across "
            f"{rows_compared} scholarship record(s). "
            f"Spearman rank correlation = {rho:.4f}."
        )

    findings.append(
        {
            "finding_id":
                "ALG_03",

            "title":
                "Ranking Evolution Across Algorithm Versions",

            "evidence":
                ranking_evidence,

            "interpretation":
                (
                    "Rank correlation describes how much the ordering "
                    "changed after confidence-aware and structured-field "
                    "improvements. It does not by itself measure whether "
                    "one version is objectively more accurate."
                ),

            "decision":
                (
                    "Retain the comparison report as evidence of algorithm "
                    "evolution and continue validating ranking quality "
                    "using realistic student profiles."
                ),
        }
    )

    # -------------------------------------------------------------------------
    # 4. Data confidence
    # -------------------------------------------------------------------------

    v22_stats = (
        comparison_analysis
        .get(
            "version_statistics",
            {},
        )
        .get(
            "V2.2",
            {},
        )
    )

    confidence_stats = (
        v22_stats.get(
            "data_confidence"
        )
    )

    if confidence_stats:

        average_confidence = (
            confidence_stats.get(
                "mean"
            )
        )

        confidence_evidence = (
            f"Mean V2.2 match-data confidence in the comparison report "
            f"is {average_confidence:.2f}%."
            if average_confidence is not None
            else
            "V2.2 data-confidence records were detected."
        )

    else:

        confidence_evidence = (
            "No directly parseable V2.2 data-confidence column "
            "was found in the comparison CSV."
        )

    findings.append(
        {
            "finding_id":
                "ALG_04",

            "title":
                "Confidence-Aware Recommendation Scoring",

            "evidence":
                confidence_evidence,

            "interpretation":
                (
                    "V2.2 distinguishes recommendation fit from the "
                    "completeness of the evidence used to calculate that fit."
                ),

            "decision":
                (
                    "Continue displaying fit and data confidence separately. "
                    "A high match score with incomplete eligibility evidence "
                    "should not be presented as guaranteed eligibility."
                ),
        }
    )

    # -------------------------------------------------------------------------
    # 5. Locked algorithm
    # -------------------------------------------------------------------------

    findings.append(
        {
            "finding_id":
                "ALG_05",

            "title":
                "Reproducible Algorithm Baseline",

            "evidence":
                (
                    f"Algorithm lock manifest available: "
                    f"{lock_analysis.get('available')}. "
                    f"Locked version: "
                    f"{lock_analysis.get('locked_version') or 'V2.2'}."
                ),

            "interpretation":
                (
                    "Locking the validated algorithm version prevents "
                    "uncontrolled scoring changes while the analysis "
                    "and frontend layers are being developed."
                ),

            "decision":
                (
                    "Use the locked V2.2 implementation as the project's "
                    "current baseline until a future version is intentionally "
                    "tested, compared and approved."
                ),
        }
    )

    # -------------------------------------------------------------------------
    # 6. Academic evaluation limitation
    # -------------------------------------------------------------------------

    findings.append(
        {
            "finding_id":
                "ALG_06",

            "title":
                "Evaluation Scope and Accuracy Limitation",

            "evidence":
                (
                    "Current validation is based on rule checks, "
                    "scenario testing, score inspection and version "
                    "comparison. A labelled dataset containing human-rated "
                    "relevant / irrelevant scholarship outcomes is not "
                    "currently available."
                ),

            "interpretation":
                (
                    "Therefore, the project should not report the profile "
                    "test pass rate as machine-learning prediction accuracy."
                ),

            "decision":
                (
                    "Present the current metric as functional scenario "
                    "validation. In a future expansion, collect user feedback "
                    "or expert relevance labels and then calculate ranking "
                    "metrics such as Precision@K, Recall@K or NDCG."
                ),
        }
    )

    return findings


# -----------------------------------------------------------------------------
# CSV output
# -----------------------------------------------------------------------------

def write_output_csv(
    findings: list[dict],
) -> None:

    PLANNING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        fieldnames = [
            "finding_id",
            "title",
            "evidence",
            "interpretation",
            "decision",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in findings:
            writer.writerow(row)


# -----------------------------------------------------------------------------
# JSON output
# -----------------------------------------------------------------------------

def write_output_json(
    report: dict,
) -> None:

    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )


# -----------------------------------------------------------------------------
# Markdown output
# -----------------------------------------------------------------------------

def write_markdown_report(
    report: dict,
) -> None:

    DOCS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    profile = report[
        "profile_test_analysis"
    ]

    comparison = report[
        "algorithm_comparison_analysis"
    ]

    lines = []

    lines.append(
        "# EduPath Step 151.6 - Recommendation Algorithm Performance Analysis"
    )
    lines.append("")

    lines.append(
        "## Evaluation Scope"
    )
    lines.append("")

    lines.append(
        "This analysis evaluates the behaviour and robustness of the "
        "current scholarship recommendation engine using previously "
        "generated multi-profile tests and algorithm-version comparisons."
    )
    lines.append("")

    lines.append(
        "The reported profile validation rate is a functional scenario "
        "validation metric, not supervised machine-learning prediction accuracy."
    )
    lines.append("")

    lines.append(
        "## Multi-Profile Validation"
    )
    lines.append("")

    lines.append(
        f"- Profiles detected: {profile['profiles_detected']}"
    )

    lines.append(
        f"- Profiles passed: {profile['profiles_passed']}"
    )

    lines.append(
        f"- Profiles failed: {profile['profiles_failed']}"
    )

    rate = profile.get(
        "functional_validation_rate"
    )

    if rate is not None:
        lines.append(
            f"- Functional scenario validation rate: {rate:.2f}%"
        )

    lines.append("")

    lines.append(
        "## Algorithm Version Comparison"
    )
    lines.append("")

    lines.append(
        f"- Comparison rows: {comparison['comparison_rows']}"
    )

    rank_info = comparison[
        "v1_to_v22_rank_comparison"
    ]

    lines.append(
        f"- V1 to V2.2 rows compared: "
        f"{rank_info['rows_compared']}"
    )

    lines.append(
        f"- Spearman ranking correlation: "
        f"{rank_info['spearman_rank_correlation']}"
    )

    lines.append("")

    lines.append(
        "## Analytical Findings"
    )
    lines.append("")

    for index, finding in enumerate(
        report["findings"],
        start=1,
    ):

        lines.append(
            f"### {index}. {finding['title']}"
        )
        lines.append("")

        lines.append(
            f"**Evidence:** {finding['evidence']}"
        )
        lines.append("")

        lines.append(
            f"**Interpretation:** {finding['interpretation']}"
        )
        lines.append("")

        lines.append(
            f"**Decision:** {finding['decision']}"
        )
        lines.append("")

    lines.append(
        "## Important Academic Note"
    )
    lines.append("")

    lines.append(
        "The recommendation engine is currently evaluated through "
        "rule validation, scenario testing, ranking analysis, confidence "
        "analysis and algorithm-version comparison. Because a labelled "
        "human relevance dataset is not yet available, the project does "
        "not claim supervised recommendation accuracy."
    )

    OUTPUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


# -----------------------------------------------------------------------------
# Terminal report
# -----------------------------------------------------------------------------

def print_terminal_report(
    report: dict,
) -> None:

    profile = report[
        "profile_test_analysis"
    ]

    comparison = report[
        "algorithm_comparison_analysis"
    ]

    lock_info = report[
        "algorithm_lock"
    ]

    print()
    print("=" * 100)
    print(
        "EduPath - Step 151.6 Recommendation Algorithm Performance Analysis"
    )
    print("=" * 100)

    print()
    print("SOURCE REPORTS")
    print("-" * 100)

    for name, info in report[
        "source_reports"
    ].items():

        print(
            f"{name:<30} : "
            f"{'FOUND' if info['exists'] else 'MISSING'}"
        )

    print()
    print("=" * 100)
    print("MULTI-PROFILE FUNCTIONAL VALIDATION")
    print("=" * 100)

    print(
        f"Profiles detected             : "
        f"{profile['profiles_detected']}"
    )

    print(
        f"Profiles passed               : "
        f"{profile['profiles_passed']}"
    )

    print(
        f"Profiles failed               : "
        f"{profile['profiles_failed']}"
    )

    print(
        f"Validation unknown            : "
        f"{profile['profiles_validation_unknown']}"
    )

    validation_rate = profile.get(
        "functional_validation_rate"
    )

    if validation_rate is not None:

        print(
            f"Functional validation rate    : "
            f"{validation_rate:.2f}%"
        )

    else:

        print(
            "Functional validation rate    : N/A"
        )

    if (
        profile[
            "average_eligible_candidates"
        ]
        is not None
    ):

        print(
            f"Average eligible candidates   : "
            f"{profile['average_eligible_candidates']:.2f}"
        )

    if (
        profile[
            "average_returned_recommendations"
        ]
        is not None
    ):

        print(
            f"Average recommendations       : "
            f"{profile['average_returned_recommendations']:.2f}"
        )

    if (
        profile[
            "average_top_score"
        ]
        is not None
    ):

        print(
            f"Average top score             : "
            f"{profile['average_top_score']:.2f}"
        )

    print()
    print("=" * 100)
    print("ALGORITHM VERSION COMPARISON")
    print("=" * 100)

    print(
        f"Comparison rows               : "
        f"{comparison['comparison_rows']}"
    )

    versions = (
        comparison[
            "version_statistics"
        ]
    )

    for version in [
        "V1",
        "V2",
        "V2.1",
        "V2.2",
    ]:

        if version not in versions:
            continue

        print()
        print(version)

        for metric, stats in (
            versions[
                version
            ].items()
        ):

            print(
                f"  {metric:<24} "
                f"mean={stats['mean']} "
                f"min={stats['minimum']} "
                f"max={stats['maximum']}"
            )

    rank_info = (
        comparison[
            "v1_to_v22_rank_comparison"
        ]
    )

    print()
    print(
        f"V1 -> V2.2 rank rows compared : "
        f"{rank_info['rows_compared']}"
    )

    print(
        f"Spearman rank correlation     : "
        f"{rank_info['spearman_rank_correlation']}"
    )

    print()
    print("=" * 100)
    print("ALGORITHM LOCK")
    print("=" * 100)

    print(
        f"Manifest available            : "
        f"{lock_info['available']}"
    )

    print(
        f"Locked version                : "
        f"{lock_info['locked_version']}"
    )

    if lock_info.get(
        "sha256"
    ):

        print(
            f"SHA256                        : "
            f"{lock_info['sha256']}"
        )

    print()
    print("=" * 100)
    print("ANALYTICAL FINDINGS")
    print("=" * 100)

    for index, finding in enumerate(
        report["findings"],
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
            f"Decision       : "
            f"{finding['decision']}"
        )

    print()
    print("=" * 100)
    print(
        "STEP 151.6 RECOMMENDATION ALGORITHM PERFORMANCE ANALYSIS: COMPLETED"
    )
    print("=" * 100)

    print()

    print(
        f"JSON report     : {OUTPUT_JSON}"
    )

    print(
        f"CSV report      : {OUTPUT_CSV}"
    )

    print(
        f"Markdown report : {OUTPUT_MD}"
    )

    print()

    print(
        "MongoDB records modified: NO"
    )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:

    print()
    print("=" * 100)
    print(
        "EduPath - Step 151.6 Recommendation Algorithm Performance Analysis"
    )
    print("=" * 100)

    print()
    print(
        f"Project root: {PROJECT_ROOT}"
    )

    # -------------------------------------------------------------------------
    # Check source files
    # -------------------------------------------------------------------------

    source_reports = {
        "algorithm_comparison_csv": {
            "path":
                str(
                    ALGORITHM_COMPARISON_CSV
                ),
            "exists":
                ALGORITHM_COMPARISON_CSV.exists(),
        },

        "algorithm_comparison_json": {
            "path":
                str(
                    ALGORITHM_COMPARISON_JSON
                ),
            "exists":
                ALGORITHM_COMPARISON_JSON.exists(),
        },

        "profile_test_csv": {
            "path":
                str(
                    PROFILE_TEST_CSV
                ),
            "exists":
                PROFILE_TEST_CSV.exists(),
        },

        "profile_test_json": {
            "path":
                str(
                    PROFILE_TEST_JSON
                ),
            "exists":
                PROFILE_TEST_JSON.exists(),
        },

        "algorithm_lock_json": {
            "path":
                str(
                    ALGORITHM_LOCK_JSON
                ),
            "exists":
                ALGORITHM_LOCK_JSON.exists(),
        },
    }

    # -------------------------------------------------------------------------
    # Required CSV reports
    # -------------------------------------------------------------------------

    if not ALGORITHM_COMPARISON_CSV.exists():

        raise FileNotFoundError(
            "Missing algorithm comparison CSV:\n"
            f"{ALGORITHM_COMPARISON_CSV}\n\n"
            "Run the previous algorithm comparison step first."
        )

    if not PROFILE_TEST_CSV.exists():

        raise FileNotFoundError(
            "Missing V2.2 profile test CSV:\n"
            f"{PROFILE_TEST_CSV}\n\n"
            "Run the previous multi-profile test step first."
        )

    # -------------------------------------------------------------------------
    # Load data
    # -------------------------------------------------------------------------

    comparison_rows = read_csv_file(
        ALGORITHM_COMPARISON_CSV
    )

    profile_rows = read_csv_file(
        PROFILE_TEST_CSV
    )

    lock_data = read_json_file(
        ALGORITHM_LOCK_JSON
    )

    print()
    print("Analysis source data loaded:")
    print(
        f"Algorithm comparison rows : "
        f"{len(comparison_rows)}"
    )

    print(
        f"Profile-test rows         : "
        f"{len(profile_rows)}"
    )

    # -------------------------------------------------------------------------
    # Analysis
    # -------------------------------------------------------------------------

    profile_analysis = (
        analyse_profile_tests(
            profile_rows
        )
    )

    comparison_analysis = (
        analyse_algorithm_comparison(
            comparison_rows
        )
    )

    lock_analysis = (
        analyse_lock_manifest(
            lock_data
        )
    )

    findings = build_findings(
        profile_analysis,
        comparison_analysis,
        lock_analysis,
    )

    # -------------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------------

    report = {
        "step":
            "151.6",

        "title":
            (
                "Recommendation Algorithm "
                "Performance Analysis"
            ),

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "evaluation_type":
            (
                "Functional scenario validation "
                "and ranking-behaviour analysis"
            ),

        "accuracy_claim":
            False,

        "accuracy_note":
            (
                "No labelled human relevance ground-truth dataset "
                "is currently available; therefore the project does "
                "not claim supervised recommendation accuracy."
            ),

        "source_reports":
            source_reports,

        "profile_test_analysis":
            profile_analysis,

        "algorithm_comparison_analysis":
            comparison_analysis,

        "algorithm_lock":
            lock_analysis,

        "findings":
            findings,

        "mongodb_records_modified":
            False,
    }

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------

    write_output_json(
        report
    )

    write_output_csv(
        findings
    )

    write_markdown_report(
        report
    )

    # -------------------------------------------------------------------------
    # Print
    # -------------------------------------------------------------------------

    print_terminal_report(
        report
    )


if __name__ == "__main__":
    main()