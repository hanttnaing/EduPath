from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
)

PLANNING_DIRECTORY = (
    PROJECT_ROOT
    / "planning"
)


# =========================================================
# INPUT FILES
# =========================================================

VERSION_FILES = {
    "V1": (
        DATA_DIRECTORY
        / "scholarship_recommendations.json"
    ),

    "V2": (
        DATA_DIRECTORY
        / "scholarship_recommendations_v2.json"
    ),

    "V2.1": (
        DATA_DIRECTORY
        / "scholarship_recommendations_v21.json"
    ),

    "V2.2": (
        DATA_DIRECTORY
        / "scholarship_recommendations_v22.json"
    ),
}


# =========================================================
# OUTPUT FILES
# =========================================================

OUTPUT_CSV = (
    PLANNING_DIRECTORY
    / "30_scholarship_algorithm_comparison.csv"
)

OUTPUT_JSON = (
    DATA_DIRECTORY
    / "scholarship_algorithm_comparison.json"
)


# =========================================================
# SAFE CONVERSION HELPERS
# =========================================================

def safe_float(
    value: Any,
) -> float | None:
    if value is None:
        return None

    try:
        return round(
            float(value),
            2,
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def safe_percent(
    value: Any,
) -> float | None:
    value = safe_float(
        value
    )

    if value is None:
        return None

    return round(
        value,
        2,
    )


# =========================================================
# LOAD JSON
# =========================================================

def load_json(
    path: Path,
) -> dict[str, Any]:

    if not path.exists():
        raise FileNotFoundError(
            "Required recommendation output "
            f"does not exist:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(
            file
        )

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            f"Invalid JSON structure: {path}"
        )

    return data


# =========================================================
# VERSION-AWARE SCORE EXTRACTION
# =========================================================

def extract_metrics(
    version: str,
    recommendation: dict[str, Any],
) -> dict[str, Any]:

    # -----------------------------------------------------
    # V1
    # -----------------------------------------------------

    if version == "V1":
        fit_score = safe_float(
            recommendation.get(
                "match_score"
            )
        )

        ranking_score = fit_score

        match_data_confidence = None

        eligibility_confidence = None

    # -----------------------------------------------------
    # V2
    # -----------------------------------------------------

    elif version == "V2":
        fit_score = safe_float(
            recommendation.get(
                "base_match_score"
            )
        )

        ranking_score = safe_float(
            recommendation.get(
                "match_score"
            )
        )

        match_data_confidence = None

        eligibility_confidence = safe_percent(
            recommendation.get(
                "eligibility_confidence"
            )
        )

    # -----------------------------------------------------
    # V2.1
    # -----------------------------------------------------

    elif version == "V2.1":
        fit_score = safe_float(
            recommendation.get(
                "base_match_score"
            )
        )

        ranking_score = safe_float(
            recommendation.get(
                "match_score"
            )
        )

        match_data_confidence = None

        eligibility_confidence = safe_percent(
            recommendation.get(
                "eligibility_confidence"
            )
        )

    # -----------------------------------------------------
    # V2.2
    # -----------------------------------------------------

    elif version == "V2.2":
        fit_score = safe_float(
            recommendation.get(
                "fit_score"
            )
        )

        ranking_score = safe_float(
            recommendation.get(
                "ranking_score"
            )
        )

        match_data_confidence = safe_percent(
            recommendation.get(
                "match_data_confidence"
            )
        )

        eligibility_confidence = safe_percent(
            recommendation.get(
                "eligibility_confidence"
            )
        )

    else:
        raise ValueError(
            f"Unsupported version: {version}"
        )

    field_similarity = safe_float(
        recommendation.get(
            "field_similarity"
        )
    )

    if field_similarity is not None:
        field_similarity_percent = round(
            field_similarity * 100,
            2,
        )

    else:
        field_similarity_percent = None

    name_similarity = safe_float(
        recommendation.get(
            "name_similarity"
        )
    )

    if name_similarity is not None:
        name_similarity_percent = round(
            name_similarity * 100,
            2,
        )

    else:
        name_similarity_percent = None

    return {
        "fit_score":
            fit_score,

        "ranking_score":
            ranking_score,

        "match_data_confidence":
            match_data_confidence,

        "eligibility_confidence":
            eligibility_confidence,

        "field_similarity_percent":
            field_similarity_percent,

        "name_similarity_percent":
            name_similarity_percent,

        "field_relevance":
            recommendation.get(
                "field_relevance"
            ),

        "structured_field_data_available":
            recommendation.get(
                "structured_field_data_available"
            ),
    }


# =========================================================
# NORMALISE VERSION RESULTS
# =========================================================

def normalise_version_result(
    version: str,
    data: dict[str, Any],
) -> dict[str, Any]:

    recommendations = data.get(
        "recommendations",
        [],
    )

    if not isinstance(
        recommendations,
        list,
    ):
        raise ValueError(
            f"{version}: recommendations "
            "must be a list."
        )

    normalised_recommendations = []

    for rank, recommendation in enumerate(
        recommendations,
        start=1,
    ):

        if not isinstance(
            recommendation,
            dict,
        ):
            continue

        scholarship_id = (
            recommendation.get(
                "scholarship_id"
            )
        )

        scholarship_name = (
            recommendation.get(
                "scholarship_name"
            )
        )

        metrics = extract_metrics(
            version=
                version,

            recommendation=
                recommendation,
        )

        normalised_recommendations.append(
            {
                "version":
                    version,

                "rank":
                    rank,

                "scholarship_id":
                    scholarship_id,

                "scholarship_name":
                    scholarship_name,

                "provider_name":
                    recommendation.get(
                        "provider_name"
                    ),

                "country_name":
                    recommendation.get(
                        "country_name"
                    ),

                **metrics,
            }
        )

    return {
        "version":
            version,

        "user_id":
            data.get(
                "user_id"
            ),

        "total_candidates":
            data.get(
                "total_scholarship_candidates"
            ),

        "eligible_candidates":
            data.get(
                "eligible_candidates"
            ),

        "rejected_by_hard_rules":
            data.get(
                "rejected_by_hard_rules"
            ),

        "returned_recommendations":
            data.get(
                "returned_recommendations"
            ),

        "recommendations":
            normalised_recommendations,
    }


# =========================================================
# BUILD MASTER SCHOLARSHIP MAP
# =========================================================

def build_comparison_rows(
    version_results: dict[
        str,
        dict[str, Any],
    ],
) -> list[dict[str, Any]]:

    scholarship_map: dict[
        str,
        dict[str, Any],
    ] = {}

    for version, result in (
        version_results.items()
    ):

        for recommendation in result[
            "recommendations"
        ]:

            scholarship_id = (
                recommendation.get(
                    "scholarship_id"
                )
            )

            scholarship_name = (
                recommendation.get(
                    "scholarship_name"
                )
            )

            if scholarship_id:
                key = str(
                    scholarship_id
                )

            else:
                key = (
                    "NAME::"
                    + str(
                        scholarship_name
                        or "UNKNOWN"
                    )
                )

            if key not in scholarship_map:
                scholarship_map[
                    key
                ] = {
                    "scholarship_id":
                        scholarship_id,

                    "scholarship_name":
                        scholarship_name,

                    "provider_name":
                        recommendation.get(
                            "provider_name"
                        ),

                    "country_name":
                        recommendation.get(
                            "country_name"
                        ),
                }

            scholarship_map[
                key
            ][
                version
            ] = recommendation

    rows = []

    for scholarship in (
        scholarship_map.values()
    ):

        row: dict[str, Any] = {
            "scholarship_id":
                scholarship.get(
                    "scholarship_id"
                ),

            "scholarship_name":
                scholarship.get(
                    "scholarship_name"
                ),

            "provider_name":
                scholarship.get(
                    "provider_name"
                ),

            "country_name":
                scholarship.get(
                    "country_name"
                ),
        }

        for version in [
            "V1",
            "V2",
            "V2.1",
            "V2.2",
        ]:

            result = scholarship.get(
                version
            )

            prefix = version.replace(
                ".",
                "_",
            )

            if result is None:
                row[
                    f"{prefix}_rank"
                ] = None

                row[
                    f"{prefix}_fit_score"
                ] = None

                row[
                    f"{prefix}_ranking_score"
                ] = None

                row[
                    f"{prefix}_match_data_confidence"
                ] = None

                row[
                    f"{prefix}_eligibility_confidence"
                ] = None

                continue

            row[
                f"{prefix}_rank"
            ] = result.get(
                "rank"
            )

            row[
                f"{prefix}_fit_score"
            ] = result.get(
                "fit_score"
            )

            row[
                f"{prefix}_ranking_score"
            ] = result.get(
                "ranking_score"
            )

            row[
                f"{prefix}_match_data_confidence"
            ] = result.get(
                "match_data_confidence"
            )

            row[
                f"{prefix}_eligibility_confidence"
            ] = result.get(
                "eligibility_confidence"
            )

        rows.append(
            row
        )

    rows.sort(
        key=lambda item: (
            item.get(
                "V2_2_rank"
            )
            if item.get(
                "V2_2_rank"
            )
            is not None
            else 9999
        )
    )

    return rows


# =========================================================
# CHECK VERSION CONSISTENCY
# =========================================================

def analyse_versions(
    version_results: dict[
        str,
        dict[str, Any],
    ],
) -> dict[str, Any]:

    versions = [
        "V1",
        "V2",
        "V2.1",
        "V2.2",
    ]

    user_ids = {
        version:
            version_results[
                version
            ].get(
                "user_id"
            )
        for version
        in versions
    }

    candidate_counts = {
        version:
            version_results[
                version
            ].get(
                "total_candidates"
            )
        for version
        in versions
    }

    eligible_counts = {
        version:
            version_results[
                version
            ].get(
                "eligible_candidates"
            )
        for version
        in versions
    }

    rejected_counts = {
        version:
            version_results[
                version
            ].get(
                "rejected_by_hard_rules"
            )
        for version
        in versions
    }

    top_names = {
        version:
            [
                item.get(
                    "scholarship_name"
                )
                for item
                in version_results[
                    version
                ][
                    "recommendations"
                ]
            ]
        for version
        in versions
    }

    same_user = (
        len(
            set(
                user_ids.values()
            )
        )
        == 1
    )

    same_candidate_count = (
        len(
            set(
                candidate_counts.values()
            )
        )
        == 1
    )

    same_eligible_count = (
        len(
            set(
                eligible_counts.values()
            )
        )
        == 1
    )

    same_rejected_count = (
        len(
            set(
                rejected_counts.values()
            )
        )
        == 1
    )

    v22_top_name = (
        top_names[
            "V2.2"
        ][0]
        if top_names[
            "V2.2"
        ]
        else None
    )

    v22_top_stable = all(
        (
            names
            and names[0]
            == v22_top_name
        )
        for names
        in top_names.values()
    )

    return {
        "same_user":
            same_user,

        "same_candidate_count":
            same_candidate_count,

        "same_eligible_count":
            same_eligible_count,

        "same_rejected_count":
            same_rejected_count,

        "top_recommendation_stable":
            v22_top_stable,

        "user_ids":
            user_ids,

        "candidate_counts":
            candidate_counts,

        "eligible_counts":
            eligible_counts,

        "rejected_counts":
            rejected_counts,

        "top_recommendations":
            {
                version:
                    (
                        names[0]
                        if names
                        else None
                    )
                for version, names
                in top_names.items()
            },
    }


# =========================================================
# CSV OUTPUT
# =========================================================

def write_csv(
    rows: list[dict[str, Any]],
) -> None:

    PLANNING_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "scholarship_id",
        "scholarship_name",
        "provider_name",
        "country_name",

        "V1_rank",
        "V1_fit_score",
        "V1_ranking_score",
        "V1_match_data_confidence",
        "V1_eligibility_confidence",

        "V2_rank",
        "V2_fit_score",
        "V2_ranking_score",
        "V2_match_data_confidence",
        "V2_eligibility_confidence",

        "V2_1_rank",
        "V2_1_fit_score",
        "V2_1_ranking_score",
        "V2_1_match_data_confidence",
        "V2_1_eligibility_confidence",

        "V2_2_rank",
        "V2_2_fit_score",
        "V2_2_ranking_score",
        "V2_2_match_data_confidence",
        "V2_2_eligibility_confidence",
    ]

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    field:
                        row.get(
                            field
                        )
                    for field
                    in fieldnames
                }
            )


# =========================================================
# JSON OUTPUT
# =========================================================

def write_json(
    version_results: dict[
        str,
        dict[str, Any],
    ],
    comparison_rows: list[
        dict[str, Any]
    ],
    analysis: dict[str, Any],
) -> None:

    payload = {
        "comparison_name":
            (
                "EduPath Scholarship "
                "Recommendation Algorithm "
                "Version Comparison"
            ),

        "versions_compared": [
            "V1",
            "V2",
            "V2.1",
            "V2.2",
        ],

        "validation":
            analysis,

        "version_summaries": {
            version: {
                "user_id":
                    result.get(
                        "user_id"
                    ),

                "total_candidates":
                    result.get(
                        "total_candidates"
                    ),

                "eligible_candidates":
                    result.get(
                        "eligible_candidates"
                    ),

                "rejected_by_hard_rules":
                    result.get(
                        "rejected_by_hard_rules"
                    ),

                "returned_recommendations":
                    result.get(
                        "returned_recommendations"
                    ),
            }

            for version, result
            in version_results.items()
        },

        "comparison_rows":
            comparison_rows,
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


# =========================================================
# CONSOLE TABLE
# =========================================================

def print_score(
    value: Any,
) -> str:

    if value is None:
        return "-"

    try:
        return (
            f"{float(value):.2f}"
        )

    except (
        TypeError,
        ValueError,
    ):
        return str(
            value
        )


def main() -> None:

    print("=" * 100)

    print(
        "EduPath - Scholarship Algorithm "
        "Comparison: V1 vs V2 vs V2.1 vs V2.2"
    )

    print("=" * 100)

    # =====================================================
    # Load all version files
    # =====================================================

    version_results: dict[
        str,
        dict[str, Any],
    ] = {}

    for (
        version,
        path,
    ) in VERSION_FILES.items():

        print(
            f"Loading {version}: "
            f"{path.name}"
        )

        data = load_json(
            path
        )

        version_results[
            version
        ] = normalise_version_result(
            version=
                version,

            data=
                data,
        )

    print()

    # =====================================================
    # Validation
    # =====================================================

    analysis = analyse_versions(
        version_results
    )

    print(
        "VERSION CONSISTENCY CHECK"
    )

    print(
        "-" * 100
    )

    print(
        "Same user profile:",
        analysis[
            "same_user"
        ],
    )

    print(
        "Same total candidate count:",
        analysis[
            "same_candidate_count"
        ],
    )

    print(
        "Same eligible candidate count:",
        analysis[
            "same_eligible_count"
        ],
    )

    print(
        "Same hard-rule rejection count:",
        analysis[
            "same_rejected_count"
        ],
    )

    print(
        "Top recommendation stable:",
        analysis[
            "top_recommendation_stable"
        ],
    )

    print()

    # =====================================================
    # Version summaries
    # =====================================================

    print(
        "VERSION SUMMARY"
    )

    print(
        "-" * 100
    )

    for version in [
        "V1",
        "V2",
        "V2.1",
        "V2.2",
    ]:

        result = version_results[
            version
        ]

        print(
            f"{version:5} | "
            f"Candidates: "
            f"{result['total_candidates']} | "
            f"Eligible: "
            f"{result['eligible_candidates']} | "
            f"Rejected: "
            f"{result['rejected_by_hard_rules']} | "
            f"Returned: "
            f"{result['returned_recommendations']}"
        )

    print()

    # =====================================================
    # Comparison rows
    # =====================================================

    rows = build_comparison_rows(
        version_results
    )

    print(
        "TOP RECOMMENDATION SCORE COMPARISON"
    )

    print(
        "-" * 100
    )

    for row in rows:

        name = str(
            row.get(
                "scholarship_name"
            )
            or "Unknown Scholarship"
        )

        print()

        print(
            name
        )

        print(
            f"   V1   "
            f"Rank: {row.get('V1_rank')} | "
            f"Score: "
            f"{print_score(row.get('V1_ranking_score'))}"
        )

        print(
            f"   V2   "
            f"Rank: {row.get('V2_rank')} | "
            f"Fit: "
            f"{print_score(row.get('V2_fit_score'))} | "
            f"Rank Score: "
            f"{print_score(row.get('V2_ranking_score'))}"
        )

        print(
            f"   V2.1 "
            f"Rank: {row.get('V2_1_rank')} | "
            f"Fit: "
            f"{print_score(row.get('V2_1_fit_score'))} | "
            f"Rank Score: "
            f"{print_score(row.get('V2_1_ranking_score'))}"
        )

        print(
            f"   V2.2 "
            f"Rank: {row.get('V2_2_rank')} | "
            f"Fit: "
            f"{print_score(row.get('V2_2_fit_score'))} | "
            f"Rank Score: "
            f"{print_score(row.get('V2_2_ranking_score'))} | "
            f"Data Confidence: "
            f"{print_score(row.get('V2_2_match_data_confidence'))}%"
        )

    # =====================================================
    # Save outputs
    # =====================================================

    write_csv(
        rows
    )

    write_json(
        version_results=
            version_results,

        comparison_rows=
            rows,

        analysis=
            analysis,
    )

    print()

    print("=" * 100)

    print(
        "COMPARISON COMPLETE"
    )

    print(
        f"CSV report : {OUTPUT_CSV}"
    )

    print(
        f"JSON report: {OUTPUT_JSON}"
    )

    print()

    print(
        "No MongoDB records were modified."
    )

    print("=" * 100)


if __name__ == "__main__":
    main()