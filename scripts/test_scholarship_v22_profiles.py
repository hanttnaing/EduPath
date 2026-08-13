from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi

from recommend_scholarships_v1_backup import (
    PROJECT_ROOT,
    ENV_FILE,
    MONGODB_URI,
    DATABASE_NAME,
    normalise_text,
)

from recommend_scholarships_v22 import (
    evaluate_scholarship_v22,
)


# =========================================================
# CONFIGURATION
# =========================================================

TOP_K = 5

PLANNING_DIRECTORY = (
    PROJECT_ROOT
    / "planning"
)

DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
)

OUTPUT_CSV = (
    PLANNING_DIRECTORY
    / "31_scholarship_v22_profile_tests.csv"
)

OUTPUT_JSON = (
    DATA_DIRECTORY
    / "scholarship_v22_profile_tests.json"
)


# =========================================================
# TEST PROFILES
# =========================================================
#
# These are temporary test scenarios.
# They are NOT written to MongoDB.
#
# Later, these values will come from:
#
#   Sign Up
#       ↓
#   Student Profile Form
#       ↓
#   MongoDB user_profiles
#       ↓
#   Recommendation Engine
#
# =========================================================

TEST_PROFILES: list[dict[str, Any]] = [

    # -----------------------------------------------------
    # PROFILE A
    # Baseline postgraduate Computer Science student
    # -----------------------------------------------------
    {
        "scenario_id": "PROFILE_A",

        "scenario_name":
            "Master Computer Science - Fully Funded",

        "expected_nonzero_results": True,

        "profile": {
            "user_id":
                "test_profile_a",

            "nationality":
                "Myanmar",

            "age":
                22,

            "target_degree_level":
                "Master",

            "preferred_major":
                "Computer Science",

            "gpa":
                3.50,

            "gpa_scale":
                4.00,

            "ielts_score":
                6.5,

            "toefl_score":
                None,

            "preferred_countries": [
                "Japan",
            ],

            "scholarship_required":
                True,

            "preferred_funding_type":
                "Fully Funded",
        },
    },

    # -----------------------------------------------------
    # PROFILE B
    # Undergraduate student
    # -----------------------------------------------------
    {
        "scenario_id": "PROFILE_B",

        "scenario_name":
            "Bachelor Computer Science - Fully Funded",

        "expected_nonzero_results": True,

        "profile": {
            "user_id":
                "test_profile_b",

            "nationality":
                "Myanmar",

            "age":
                18,

            "target_degree_level":
                "Bachelor",

            "preferred_major":
                "Computer Science",

            "gpa":
                3.40,

            "gpa_scale":
                4.00,

            "ielts_score":
                6.0,

            "toefl_score":
                None,

            "preferred_countries": [
                "Japan",
            ],

            "scholarship_required":
                True,

            "preferred_funding_type":
                "Fully Funded",
        },
    },

    # -----------------------------------------------------
    # PROFILE C
    # AI-focused postgraduate student
    # -----------------------------------------------------
    {
        "scenario_id": "PROFILE_C",

        "scenario_name":
            "Master Artificial Intelligence",

        "expected_nonzero_results": True,

        "profile": {
            "user_id":
                "test_profile_c",

            "nationality":
                "Myanmar",

            "age":
                23,

            "target_degree_level":
                "Master",

            "preferred_major":
                "Artificial Intelligence",

            "gpa":
                3.70,

            "gpa_scale":
                4.00,

            "ielts_score":
                7.0,

            "toefl_score":
                None,

            "preferred_countries": [
                "Japan",
            ],

            "scholarship_required":
                True,

            "preferred_funding_type":
                "Fully Funded",
        },
    },

    # -----------------------------------------------------
    # PROFILE D
    # Same academic preference, different funding
    # -----------------------------------------------------
    {
        "scenario_id": "PROFILE_D",

        "scenario_name":
            "Master Computer Science - Partial Funding Preference",

        "expected_nonzero_results": True,

        "profile": {
            "user_id":
                "test_profile_d",

            "nationality":
                "Myanmar",

            "age":
                22,

            "target_degree_level":
                "Master",

            "preferred_major":
                "Computer Science",

            "gpa":
                3.50,

            "gpa_scale":
                4.00,

            "ielts_score":
                6.5,

            "toefl_score":
                None,

            "preferred_countries": [
                "Japan",
            ],

            "scholarship_required":
                True,

            "preferred_funding_type":
                "Partially Funded",
        },
    },

    # -----------------------------------------------------
    # PROFILE E
    # Different academic field
    # -----------------------------------------------------
    {
        "scenario_id": "PROFILE_E",

        "scenario_name":
            "Master Data Science",

        "expected_nonzero_results": True,

        "profile": {
            "user_id":
                "test_profile_e",

            "nationality":
                "Myanmar",

            "age":
                24,

            "target_degree_level":
                "Master",

            "preferred_major":
                "Data Science",

            "gpa":
                3.20,

            "gpa_scale":
                4.00,

            "ielts_score":
                6.5,

            "toefl_score":
                None,

            "preferred_countries": [
                "Japan",
            ],

            "scholarship_required":
                True,

            "preferred_funding_type":
                "Fully Funded",
        },
    },

    # -----------------------------------------------------
    # PROFILE F
    # Negative country test
    #
    # Current scholarship dataset is Japan.
    # Therefore a South Korea-only preference should
    # produce zero Japan recommendations.
    # -----------------------------------------------------
    {
        "scenario_id": "PROFILE_F",

        "scenario_name":
            "South Korea Country Hard-Rule Test",

        "expected_zero_results": True,

        "profile": {
            "user_id":
                "test_profile_f",

            "nationality":
                "Myanmar",

            "age":
                22,

            "target_degree_level":
                "Master",

            "preferred_major":
                "Computer Science",

            "gpa":
                3.50,

            "gpa_scale":
                4.00,

            "ielts_score":
                6.5,

            "toefl_score":
                None,

            "preferred_countries": [
                "South Korea",
            ],

            "scholarship_required":
                True,

            "preferred_funding_type":
                "Fully Funded",
        },
    },
]


# =========================================================
# DATABASE LOOKUPS
# =========================================================

def load_reference_data(
    database: Any,
) -> tuple[
    list[dict[str, Any]],
    dict[str, str],
    dict[str, str],
]:

    scholarships = list(
        database[
            "scholarships"
        ].find(
            {},
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )
    )

    country_name_by_id = {
        country[
            "country_id"
        ]:
            country[
                "country_name"
            ]

        for country
        in database[
            "countries"
        ].find(
            {},
            {
                "_id": 0,
                "country_id": 1,
                "country_name": 1,
            },
        )
    }

    university_name_by_id = {
        university[
            "university_id"
        ]:
            university[
                "university_name"
            ]

        for university
        in database[
            "universities"
        ].find(
            {},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
            },
        )
    }

    return (
        scholarships,
        country_name_by_id,
        university_name_by_id,
    )


# =========================================================
# RANKING
# =========================================================

def sort_recommendations(
    recommendations: list[
        dict[str, Any]
    ],
) -> None:

    recommendations.sort(
        key=lambda item: (
            item.get(
                "ranking_score",
                0,
            ),

            item.get(
                "fit_score",
                0,
            ),

            item.get(
                "match_data_confidence",
                0,
            ),

            item.get(
                "eligibility_confidence",
                0,
            ),

            item.get(
                "field_similarity",
                0,
            ),

            item.get(
                "name_similarity",
                0,
            ),
        ),
        reverse=True,
    )


# =========================================================
# RUN ONE PROFILE
# =========================================================

def run_profile_test(
    scenario: dict[str, Any],

    scholarships: list[
        dict[str, Any]
    ],

    country_name_by_id:
        dict[str, str],

    university_name_by_id:
        dict[str, str],

) -> dict[str, Any]:

    profile = scenario[
        "profile"
    ]

    recommendations: list[
        dict[str, Any]
    ] = []

    rejected = 0

    skipped_relationship = 0

    for scholarship in scholarships:

        country_id = scholarship.get(
            "country_id"
        )

        country_name = (
            country_name_by_id.get(
                country_id
            )
        )

        if not country_name:
            skipped_relationship += 1
            continue

        host_university_id = (
            scholarship.get(
                "host_university_id"
            )
        )

        university_name = None

        if host_university_id:

            university_name = (
                university_name_by_id.get(
                    host_university_id
                )
            )

            if not university_name:
                skipped_relationship += 1
                continue

        recommendation = (
            evaluate_scholarship_v22(
                profile=
                    profile,

                scholarship=
                    scholarship,

                country_name=
                    country_name,

                university_name=
                    university_name,
            )
        )

        if recommendation is None:
            rejected += 1
            continue

        recommendations.append(
            recommendation
        )

    sort_recommendations(
        recommendations
    )

    top_recommendations = (
        recommendations[
            :TOP_K
        ]
    )

    return {
        "scenario_id":
            scenario[
                "scenario_id"
            ],

        "scenario_name":
            scenario[
                "scenario_name"
            ],

        "profile":
            profile,

        "total_candidates":
            len(
                scholarships
            ),

        "eligible_candidates":
            len(
                recommendations
            ),

        "rejected_candidates":
            rejected,

        "skipped_missing_relationship":
            skipped_relationship,

        "returned_recommendations":
            len(
                top_recommendations
            ),

        "recommendations":
            top_recommendations,
    }


# =========================================================
# VALIDATION
# =========================================================

def validate_scenario(
    scenario: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:

    issues: list[str] = []

    profile = result[
        "profile"
    ]

    recommendations = result[
        "recommendations"
    ]

    target_degree = normalise_text(
        profile.get(
            "target_degree_level"
        )
    )

    preferred_countries = {
        normalise_text(
            country
        )
        for country
        in profile.get(
            "preferred_countries",
            []
        )
    }

    # -----------------------------------------------------
    # Expected result count
    # -----------------------------------------------------

    if scenario.get(
        "expected_nonzero_results"
    ):

        if not recommendations:
            issues.append(
                "Expected one or more recommendations, "
                "but none were returned."
            )

    if scenario.get(
        "expected_zero_results"
    ):

        if recommendations:
            issues.append(
                "Expected zero recommendations, "
                "but recommendations were returned."
            )

    # -----------------------------------------------------
    # TOP_K limit
    # -----------------------------------------------------

    if len(
        recommendations
    ) > TOP_K:

        issues.append(
            "Returned recommendations exceeded TOP_K."
        )

    # -----------------------------------------------------
    # Duplicate IDs
    # -----------------------------------------------------

    scholarship_ids = [
        item.get(
            "scholarship_id"
        )
        for item
        in recommendations
        if item.get(
            "scholarship_id"
        )
    ]

    if len(
        scholarship_ids
    ) != len(
        set(
            scholarship_ids
        )
    ):

        issues.append(
            "Duplicate scholarship IDs detected."
        )

    # -----------------------------------------------------
    # Recommendation-level validation
    # -----------------------------------------------------

    previous_ranking_score = None

    for recommendation in recommendations:

        # Degree validation

        recommendation_degrees = {
            normalise_text(
                degree
            )
            for degree
            in recommendation.get(
                "degree_levels",
                [],
            )
        }

        if (
            target_degree
            and target_degree
            not in recommendation_degrees
        ):
            issues.append(
                "A recommendation does not support "
                f"target degree: {target_degree}."
            )

        # Country validation

        recommendation_country = (
            normalise_text(
                recommendation.get(
                    "country_name"
                )
            )
        )

        if (
            preferred_countries
            and recommendation_country
            not in preferred_countries
        ):

            issues.append(
                "A recommendation is outside the "
                "preferred countries."
            )

        # Closed scholarship validation

        if normalise_text(
            recommendation.get(
                "scholarship_status"
            )
        ) == "closed":

            issues.append(
                "Closed scholarship passed filtering."
            )

        # Score ranges

        fit_score = float(
            recommendation.get(
                "fit_score",
                0,
            )
        )

        ranking_score = float(
            recommendation.get(
                "ranking_score",
                0,
            )
        )

        match_data_confidence = float(
            recommendation.get(
                "match_data_confidence",
                0,
            )
        )

        eligibility_confidence = float(
            recommendation.get(
                "eligibility_confidence",
                0,
            )
        )

        if not (
            0
            <= fit_score
            <= 100
        ):
            issues.append(
                "Fit score is outside 0-100."
            )

        if not (
            0
            <= ranking_score
            <= 100
        ):
            issues.append(
                "Ranking score is outside 0-100."
            )

        if not (
            0
            <= match_data_confidence
            <= 100
        ):
            issues.append(
                "Match Data Confidence "
                "is outside 0-100."
            )

        if not (
            0
            <= eligibility_confidence
            <= 100
        ):
            issues.append(
                "Eligibility Confidence "
                "is outside 0-100."
            )

        # Confidence-aware ranking should not
        # exceed raw fit score.

        if (
            ranking_score
            > fit_score + 0.01
        ):

            issues.append(
                "Ranking score is greater "
                "than Fit Score."
            )

        # Ranking order check

        if previous_ranking_score is not None:

            if (
                ranking_score
                > previous_ranking_score
                + 0.01
            ):

                issues.append(
                    "Recommendations are not sorted "
                    "by descending Ranking Score."
                )

        previous_ranking_score = (
            ranking_score
        )

    validation_status = (
        "PASS"
        if not issues
        else "FAIL"
    )

    return {
        "status":
            validation_status,

        "issues":
            issues,
    }


# =========================================================
# CSV OUTPUT
# =========================================================

def write_csv(
    test_results: list[
        dict[str, Any]
    ],
) -> None:

    PLANNING_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "scenario_id",
        "scenario_name",
        "target_degree",
        "preferred_major",
        "preferred_country",
        "preferred_funding",
        "validation_status",
        "eligible_candidates",
        "rank",
        "scholarship_id",
        "scholarship_name",
        "degree_levels",
        "fit_score",
        "ranking_score",
        "match_data_confidence",
        "eligibility_confidence",
        "field_relevance",
        "structured_field_data_available",
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

        for result in test_results:

            profile = result[
                "profile"
            ]

            validation_status = (
                result[
                    "validation"
                ][
                    "status"
                ]
            )

            recommendations = (
                result[
                    "recommendations"
                ]
            )

            # Write one blank recommendation row
            # when a scenario intentionally returns zero.

            if not recommendations:

                writer.writerow(
                    {
                        "scenario_id":
                            result[
                                "scenario_id"
                            ],

                        "scenario_name":
                            result[
                                "scenario_name"
                            ],

                        "target_degree":
                            profile.get(
                                "target_degree_level"
                            ),

                        "preferred_major":
                            profile.get(
                                "preferred_major"
                            ),

                        "preferred_country":
                            ", ".join(
                                profile.get(
                                    "preferred_countries",
                                    [],
                                )
                            ),

                        "preferred_funding":
                            profile.get(
                                "preferred_funding_type"
                            ),

                        "validation_status":
                            validation_status,

                        "eligible_candidates":
                            result[
                                "eligible_candidates"
                            ],
                    }
                )

                continue

            for (
                rank,
                recommendation,
            ) in enumerate(
                recommendations,
                start=1,
            ):

                writer.writerow(
                    {
                        "scenario_id":
                            result[
                                "scenario_id"
                            ],

                        "scenario_name":
                            result[
                                "scenario_name"
                            ],

                        "target_degree":
                            profile.get(
                                "target_degree_level"
                            ),

                        "preferred_major":
                            profile.get(
                                "preferred_major"
                            ),

                        "preferred_country":
                            ", ".join(
                                profile.get(
                                    "preferred_countries",
                                    [],
                                )
                            ),

                        "preferred_funding":
                            profile.get(
                                "preferred_funding_type"
                            ),

                        "validation_status":
                            validation_status,

                        "eligible_candidates":
                            result[
                                "eligible_candidates"
                            ],

                        "rank":
                            rank,

                        "scholarship_id":
                            recommendation.get(
                                "scholarship_id"
                            ),

                        "scholarship_name":
                            recommendation.get(
                                "scholarship_name"
                            ),

                        "degree_levels":
                            ", ".join(
                                recommendation.get(
                                    "degree_levels",
                                    [],
                                )
                            ),

                        "fit_score":
                            recommendation.get(
                                "fit_score"
                            ),

                        "ranking_score":
                            recommendation.get(
                                "ranking_score"
                            ),

                        "match_data_confidence":
                            recommendation.get(
                                "match_data_confidence"
                            ),

                        "eligibility_confidence":
                            recommendation.get(
                                "eligibility_confidence"
                            ),

                        "field_relevance":
                            recommendation.get(
                                "field_relevance"
                            ),

                        "structured_field_data_available":
                            recommendation.get(
                                "structured_field_data_available"
                            ),
                    }
                )


# =========================================================
# JSON OUTPUT
# =========================================================

def write_json(
    test_results: list[
        dict[str, Any]
    ],
) -> None:

    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "test_name":
            (
                "EduPath Scholarship "
                "Recommendation V2.2 "
                "Multi-Profile Validation"
            ),

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "algorithm":
            "V2.2",

        "profiles_tested":
            len(
                test_results
            ),

        "profiles_passed":
            sum(
                1
                for result
                in test_results
                if result[
                    "validation"
                ][
                    "status"
                ]
                == "PASS"
            ),

        "profiles_failed":
            sum(
                1
                for result
                in test_results
                if result[
                    "validation"
                ][
                    "status"
                ]
                == "FAIL"
            ),

        "results":
            test_results,
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
# MAIN
# =========================================================

def main() -> None:

    print("=" * 96)

    print(
        "EduPath - Scholarship V2.2 "
        "Multiple Student Profile Testing"
    )

    print("=" * 96)

    # -----------------------------------------------------
    # Safety checks
    # -----------------------------------------------------

    if not ENV_FILE.exists():

        raise FileNotFoundError(
            f".env file not found: "
            f"{ENV_FILE}"
        )

    if not MONGODB_URI:

        raise RuntimeError(
            "MONGODB_URI is missing "
            "from the .env file."
        )

    # -----------------------------------------------------
    # Connect MongoDB
    # -----------------------------------------------------

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi(
            "1"
        ),
        serverSelectionTimeoutMS=10000,
    )

    try:

        print(
            "Connecting to MongoDB Atlas..."
        )

        client.admin.command(
            "ping"
        )

        print(
            "MongoDB Atlas connection: SUCCESS"
        )

        database = client[
            DATABASE_NAME
        ]

        (
            scholarships,
            country_name_by_id,
            university_name_by_id,
        ) = load_reference_data(
            database
        )

        print()

        print(
            "Scholarships loaded:",
            len(
                scholarships
            ),
        )

        print(
            "Test profiles:",
            len(
                TEST_PROFILES
            ),
        )

        print()

        # -------------------------------------------------
        # Run scenarios
        # -------------------------------------------------

        all_results = []

        for scenario in TEST_PROFILES:

            print(
                "-" * 96
            )

            print(
                scenario[
                    "scenario_id"
                ],
                "-",
                scenario[
                    "scenario_name"
                ],
            )

            result = run_profile_test(
                scenario=
                    scenario,

                scholarships=
                    scholarships,

                country_name_by_id=
                    country_name_by_id,

                university_name_by_id=
                    university_name_by_id,
            )

            validation = (
                validate_scenario(
                    scenario=
                        scenario,

                    result=
                        result,
                )
            )

            result[
                "validation"
            ] = validation

            all_results.append(
                result
            )

            print(
                "Eligible candidates:",
                result[
                    "eligible_candidates"
                ],
            )

            print(
                "Returned recommendations:",
                result[
                    "returned_recommendations"
                ],
            )

            print(
                "Validation:",
                validation[
                    "status"
                ],
            )

            if validation[
                "issues"
            ]:

                print(
                    "Validation issues:"
                )

                for issue in validation[
                    "issues"
                ]:

                    print(
                        "  -",
                        issue,
                    )

            recommendations = (
                result[
                    "recommendations"
                ]
            )

            if recommendations:

                print()

                print(
                    "Top recommendations:"
                )

                for (
                    rank,
                    recommendation,
                ) in enumerate(
                    recommendations,
                    start=1,
                ):

                    print(
                        f"  {rank}. "
                        f"{recommendation['scholarship_name']}"
                    )

                    print(
                        "     Fit Score:",
                        recommendation[
                            "fit_score"
                        ],
                    )

                    print(
                        "     Ranking Score:",
                        recommendation[
                            "ranking_score"
                        ],
                    )

                    print(
                        "     Match Data Confidence:",
                        str(
                            recommendation[
                                "match_data_confidence"
                            ]
                        )
                        + "%",
                    )

                    print(
                        "     Eligibility Confidence:",
                        str(
                            recommendation[
                                "eligibility_confidence"
                            ]
                        )
                        + "%",
                    )

                    print(
                        "     Field Relevance:",
                        recommendation[
                            "field_relevance"
                        ],
                    )

            else:

                print(
                    "No recommendations returned."
                )

            print()

        # -------------------------------------------------
        # Write reports
        # -------------------------------------------------

        write_csv(
            all_results
        )

        write_json(
            all_results
        )

        passed = sum(
            1
            for result
            in all_results
            if result[
                "validation"
            ][
                "status"
            ]
            == "PASS"
        )

        failed = (
            len(
                all_results
            )
            - passed
        )

        print("=" * 96)

        print(
            "MULTI-PROFILE TEST SUMMARY"
        )

        print("=" * 96)

        print(
            "Profiles tested:",
            len(
                all_results
            ),
        )

        print(
            "Profiles passed:",
            passed,
        )

        print(
            "Profiles failed:",
            failed,
        )

        print()

        print(
            "CSV report :",
            OUTPUT_CSV,
        )

        print(
            "JSON report:",
            OUTPUT_JSON,
        )

        print()

        if failed == 0:

            print(
                "OVERALL VALIDATION: PASSED"
            )

        else:

            print(
                "OVERALL VALIDATION: "
                "REVIEW REQUIRED"
            )

        print()

        print(
            "No MongoDB records were modified."
        )

        print("=" * 96)

    except PyMongoError as error:

        raise RuntimeError(
            "MongoDB operation failed."
        ) from error

    finally:

        client.close()

        print(
            "MongoDB connection closed safely."
        )


if __name__ == "__main__":
    main()