from __future__ import annotations

import hashlib
import json
import py_compile
import shutil
from datetime import datetime, timezone
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

SCRIPTS_DIRECTORY = (
    PROJECT_ROOT
    / "scripts"
)

PLANNING_DIRECTORY = (
    PROJECT_ROOT
    / "planning"
)

DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
)


# =========================================================
# SOURCE / FINAL ALGORITHM FILES
# =========================================================

SOURCE_ALGORITHM = (
    SCRIPTS_DIRECTORY
    / "recommend_scholarships_v22.py"
)

FINAL_ALGORITHM = (
    SCRIPTS_DIRECTORY
    / "recommend_scholarships_final.py"
)


# =========================================================
# VALIDATION INPUT FILES
# =========================================================

COMPARISON_JSON = (
    DATA_DIRECTORY
    / "scholarship_algorithm_comparison.json"
)

PROFILE_TEST_JSON = (
    DATA_DIRECTORY
    / "scholarship_v22_profile_tests.json"
)

V22_RESULT_JSON = (
    DATA_DIRECTORY
    / "scholarship_recommendations_v22.json"
)


# =========================================================
# FINAL MANIFEST
# =========================================================

OUTPUT_MANIFEST = (
    PLANNING_DIRECTORY
    / "32_scholarship_algorithm_lock_v22.json"
)


# =========================================================
# HELPERS
# =========================================================

def load_json(
    path: Path,
) -> dict[str, Any]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{path}"
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
            f"Expected JSON object in:\n{path}"
        )

    return data


def calculate_sha256(
    path: Path,
) -> str:

    sha256 = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# =========================================================
# VALIDATE VERSION COMPARISON
# =========================================================

def validate_algorithm_comparison(
    comparison_data: dict[str, Any],
) -> list[str]:

    issues: list[str] = []

    validation = comparison_data.get(
        "validation",
        {},
    )

    required_checks = {
        "same_user":
            True,

        "same_candidate_count":
            True,

        "same_eligible_count":
            True,

        "same_rejected_count":
            True,

        "top_recommendation_stable":
            True,
    }

    for (
        check_name,
        expected_value,
    ) in required_checks.items():

        actual_value = validation.get(
            check_name
        )

        if actual_value != expected_value:

            issues.append(
                f"Comparison check failed: "
                f"{check_name} = {actual_value}"
            )

    return issues


# =========================================================
# VALIDATE MULTI-PROFILE TEST
# =========================================================

def validate_profile_tests(
    profile_test_data: dict[str, Any],
) -> list[str]:

    issues: list[str] = []

    profiles_tested = int(
        profile_test_data.get(
            "profiles_tested",
            0,
        )
    )

    profiles_passed = int(
        profile_test_data.get(
            "profiles_passed",
            0,
        )
    )

    profiles_failed = int(
        profile_test_data.get(
            "profiles_failed",
            0,
        )
    )

    if profiles_tested < 6:

        issues.append(
            "Fewer than 6 profiles were tested."
        )

    if profiles_failed != 0:

        issues.append(
            f"{profiles_failed} profile test(s) failed."
        )

    if profiles_passed != profiles_tested:

        issues.append(
            "Not all tested profiles passed."
        )

    results = profile_test_data.get(
        "results",
        [],
    )

    if not isinstance(
        results,
        list,
    ):

        issues.append(
            "Profile-test results are invalid."
        )

        return issues

    scenario_ids = {
        result.get(
            "scenario_id"
        )
        for result
        in results
        if isinstance(
            result,
            dict,
        )
    }

    expected_scenarios = {
        "PROFILE_A",
        "PROFILE_B",
        "PROFILE_C",
        "PROFILE_D",
        "PROFILE_E",
        "PROFILE_F",
    }

    missing_scenarios = (
        expected_scenarios
        - scenario_ids
    )

    if missing_scenarios:

        issues.append(
            "Missing profile scenarios: "
            + ", ".join(
                sorted(
                    missing_scenarios
                )
            )
        )

    # -----------------------------------------------------
    # Validate South Korea negative test
    # -----------------------------------------------------

    profile_f = next(
        (
            result
            for result
            in results
            if result.get(
                "scenario_id"
            )
            == "PROFILE_F"
        ),
        None,
    )

    if profile_f is None:

        issues.append(
            "PROFILE_F could not be found."
        )

    else:

        eligible_candidates = int(
            profile_f.get(
                "eligible_candidates",
                -1,
            )
        )

        validation = profile_f.get(
            "validation",
            {},
        )

        validation_status = (
            validation.get(
                "status"
            )
        )

        if eligible_candidates != 0:

            issues.append(
                "PROFILE_F should return "
                "0 eligible Japan scholarships."
            )

        if validation_status != "PASS":

            issues.append(
                "PROFILE_F negative-country "
                "test did not pass."
            )

    return issues


# =========================================================
# VALIDATE V2.2 RESULT
# =========================================================

def validate_v22_result(
    result_data: dict[str, Any],
) -> list[str]:

    issues: list[str] = []

    recommendations = result_data.get(
        "recommendations",
        [],
    )

    if not isinstance(
        recommendations,
        list,
    ):

        return [
            "V2.2 recommendation list is invalid."
        ]

    if not recommendations:

        return [
            "V2.2 produced no recommendations."
        ]

    first_result = recommendations[
        0
    ]

    required_metrics = [
        "fit_score",
        "ranking_score",
        "match_data_confidence",
        "eligibility_confidence",
        "score_breakdown",
        "match_data_evidence",
        "eligibility_checks",
    ]

    for metric in required_metrics:

        if metric not in first_result:

            issues.append(
                "Missing V2.2 metric: "
                f"{metric}"
            )

    fit_score = float(
        first_result.get(
            "fit_score",
            0,
        )
    )

    ranking_score = float(
        first_result.get(
            "ranking_score",
            0,
        )
    )

    confidence = float(
        first_result.get(
            "match_data_confidence",
            0,
        )
    )

    if not (
        0
        <= fit_score
        <= 100
    ):

        issues.append(
            "Top Fit Score is outside 0-100."
        )

    if not (
        0
        <= ranking_score
        <= 100
    ):

        issues.append(
            "Top Ranking Score is outside 0-100."
        )

    if not (
        0
        <= confidence
        <= 100
    ):

        issues.append(
            "Top Match Data Confidence "
            "is outside 0-100."
        )

    if ranking_score > fit_score + 0.01:

        issues.append(
            "Ranking Score is greater "
            "than Fit Score."
        )

    return issues


# =========================================================
# CREATE FINAL SNAPSHOT
# =========================================================

def create_final_algorithm_snapshot() -> dict[str, str]:

    if not SOURCE_ALGORITHM.exists():

        raise FileNotFoundError(
            "V2.2 algorithm source file "
            f"not found:\n{SOURCE_ALGORITHM}"
        )

    # Compile source before copying.
    py_compile.compile(
        str(
            SOURCE_ALGORITHM
        ),
        doraise=True,
    )

    source_hash = calculate_sha256(
        SOURCE_ALGORITHM
    )

    # Preserve an old final snapshot if one exists.
    if FINAL_ALGORITHM.exists():

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_file = (
            PLANNING_DIRECTORY
            / "backups"
            / (
                "recommend_scholarships_final_"
                f"before_v22_lock_{timestamp}.py"
            )
        )

        backup_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            FINAL_ALGORITHM,
            backup_file,
        )

        print(
            "Existing final algorithm backed up:"
        )

        print(
            backup_file
        )

    shutil.copy2(
        SOURCE_ALGORITHM,
        FINAL_ALGORITHM,
    )

    # Compile final snapshot.
    py_compile.compile(
        str(
            FINAL_ALGORITHM
        ),
        doraise=True,
    )

    final_hash = calculate_sha256(
        FINAL_ALGORITHM
    )

    if source_hash != final_hash:

        raise RuntimeError(
            "Final algorithm snapshot "
            "does not match V2.2 source."
        )

    return {
        "source_sha256":
            source_hash,

        "final_sha256":
            final_hash,
    }


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print("=" * 96)

    print(
        "EduPath - Final Scholarship "
        "Recommendation Algorithm Lock"
    )

    print("=" * 96)

    PLANNING_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # Load evidence
    # -----------------------------------------------------

    print(
        "Loading validation evidence..."
    )

    comparison_data = load_json(
        COMPARISON_JSON
    )

    profile_test_data = load_json(
        PROFILE_TEST_JSON
    )

    v22_result_data = load_json(
        V22_RESULT_JSON
    )

    # -----------------------------------------------------
    # Validate evidence
    # -----------------------------------------------------

    comparison_issues = (
        validate_algorithm_comparison(
            comparison_data
        )
    )

    profile_test_issues = (
        validate_profile_tests(
            profile_test_data
        )
    )

    result_issues = (
        validate_v22_result(
            v22_result_data
        )
    )

    all_issues = (
        comparison_issues
        + profile_test_issues
        + result_issues
    )

    print()

    print(
        "VALIDATION RESULTS"
    )

    print(
        "-" * 96
    )

    print(
        "Algorithm comparison:",
        (
            "PASS"
            if not comparison_issues
            else "FAIL"
        ),
    )

    print(
        "Multi-profile testing:",
        (
            "PASS"
            if not profile_test_issues
            else "FAIL"
        ),
    )

    print(
        "V2.2 output validation:",
        (
            "PASS"
            if not result_issues
            else "FAIL"
        ),
    )

    if all_issues:

        print()

        print(
            "FINAL LOCK BLOCKED"
        )

        print(
            "-" * 96
        )

        for issue in all_issues:

            print(
                " -",
                issue,
            )

        raise RuntimeError(
            "V2.2 cannot be locked "
            "until all validation issues "
            "are resolved."
        )

    # -----------------------------------------------------
    # Create immutable-style final snapshot
    # -----------------------------------------------------

    print()

    print(
        "Creating final V2.2 snapshot..."
    )

    hashes = (
        create_final_algorithm_snapshot()
    )

    # -----------------------------------------------------
    # Collect summary information
    # -----------------------------------------------------

    profile_count = int(
        profile_test_data.get(
            "profiles_tested",
            0,
        )
    )

    profile_passed = int(
        profile_test_data.get(
            "profiles_passed",
            0,
        )
    )

    recommendations = (
        v22_result_data.get(
            "recommendations",
            []
        )
    )

    top_recommendation = (
        recommendations[
            0
        ]
        if recommendations
        else {}
    )

    # -----------------------------------------------------
    # Algorithm manifest
    # -----------------------------------------------------

    manifest = {
        "project":
            "EduPath Analytics",

        "component":
            (
                "Scholarship Recommendation "
                "Algorithm"
            ),

        "locked_version":
            "V2.2",

        "lock_status":
            "LOCKED",

        "locked_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "source_file":
            str(
                SOURCE_ALGORITHM
            ),

        "final_snapshot_file":
            str(
                FINAL_ALGORITHM
            ),

        "source_sha256":
            hashes[
                "source_sha256"
            ],

        "final_sha256":
            hashes[
                "final_sha256"
            ],

        "algorithm_type":
            (
                "Hybrid recommendation system"
            ),

        "methods": [
            "Rule-based filtering",
            "TF-IDF vectorization",
            "Cosine similarity",
            "Weighted preference scoring",
            "Missing-data uncertainty handling",
            "Confidence-aware ranking",
            "Eligibility confidence analysis",
        ],

        "fit_score_weights": {
            "degree_level":
                20,

            "preferred_country":
                15,

            "field_similarity":
                35,

            "funding_type":
                20,

            "scholarship_status":
                10,
        },

        "fit_score_total":
            100,

        "ranking_formula": (
            "RankingScore = FitScore * "
            "(0.70 + 0.30 * "
            "MatchDataConfidenceRatio)"
        ),

        "missing_field_strategy": (
            "Missing field data is treated "
            "as uncertainty rather than "
            "as a confirmed mismatch."
        ),

        "eligibility_dimensions": [
            "nationality",
            "gpa",
            "english",
            "age",
            "deadline",
        ],

        "validation_evidence": {
            "algorithm_version_comparison":
                "PASSED",

            "multi_profile_test":
                "PASSED",

            "profiles_tested":
                profile_count,

            "profiles_passed":
                profile_passed,

            "profiles_failed":
                int(
                    profile_test_data.get(
                        "profiles_failed",
                        0,
                    )
                ),

            "negative_country_hard_rule_test":
                "PASSED",
        },

        "reference_run": {
            "user_id":
                v22_result_data.get(
                    "user_id"
                ),

            "total_candidates":
                v22_result_data.get(
                    "total_scholarship_candidates"
                ),

            "eligible_candidates":
                v22_result_data.get(
                    "eligible_candidates"
                ),

            "rejected_by_hard_rules":
                v22_result_data.get(
                    "rejected_by_hard_rules"
                ),

            "top_recommendation":
                top_recommendation.get(
                    "scholarship_name"
                ),

            "top_fit_score":
                top_recommendation.get(
                    "fit_score"
                ),

            "top_ranking_score":
                top_recommendation.get(
                    "ranking_score"
                ),

            "top_match_data_confidence":
                top_recommendation.get(
                    "match_data_confidence"
                ),

            "top_eligibility_confidence":
                top_recommendation.get(
                    "eligibility_confidence"
                ),
        },

        "important_note": (
            "Weights are interpretable "
            "heuristic design weights, "
            "not machine-learned weights. "
            "They were validated using "
            "multi-scenario testing."
        ),

        "database_modified":
            False,
    }

    with OUTPUT_MANIFEST.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            manifest,
            file,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    # -----------------------------------------------------
    # Console summary
    # -----------------------------------------------------

    print()

    print("=" * 96)

    print(
        "FINAL ALGORITHM LOCK: PASSED"
    )

    print("=" * 96)

    print(
        "Locked version: V2.2"
    )

    print(
        "Profiles tested:",
        profile_count,
    )

    print(
        "Profiles passed:",
        profile_passed,
    )

    print()

    print(
        "Final snapshot:"
    )

    print(
        FINAL_ALGORITHM
    )

    print()

    print(
        "Algorithm manifest:"
    )

    print(
        OUTPUT_MANIFEST
    )

    print()

    print(
        "SHA256:"
    )

    print(
        hashes[
            "final_sha256"
        ]
    )

    print()

    print(
        "No MongoDB records were modified."
    )

    print("=" * 96)


if __name__ == "__main__":
    main()