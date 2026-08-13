from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi

# ---------------------------------------------------------
# Reuse stable V1 helper functions for this comparison test.
# After V2 is validated, we will consolidate everything
# into the production recommendation module.
# ---------------------------------------------------------

from recommend_scholarships_v1_backup import (
    PROJECT_ROOT,
    ENV_FILE,
    MONGODB_URI,
    DATABASE_NAME,
    USER_ID,
    TOP_K,
    normalise_text,
    datetime_to_iso_date,
    calculate_best_field_similarity,
    contains_generic_nationality,
    evaluate_gpa,
    evaluate_english_requirement,
)


# ---------------------------------------------------------
# Output
# ---------------------------------------------------------

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
)

OUTPUT_JSON = (
    OUTPUT_DIRECTORY
    / "scholarship_recommendations_v2.json"
)


# ---------------------------------------------------------
# V2 Match-score weights
# ---------------------------------------------------------

DEGREE_LEVEL_WEIGHT = 20
COUNTRY_WEIGHT = 15
FIELD_SIMILARITY_WEIGHT = 35
FUNDING_TYPE_WEIGHT = 20
STATUS_WEIGHT = 10

MAXIMUM_MATCH_SCORE = (
    DEGREE_LEVEL_WEIGHT
    + COUNTRY_WEIGHT
    + FIELD_SIMILARITY_WEIGHT
    + FUNDING_TYPE_WEIGHT
    + STATUS_WEIGHT
)


# ---------------------------------------------------------
# Field relevance
# ---------------------------------------------------------

def get_field_relevance(
    similarity: float,
    fields_of_study: list[str],
) -> tuple[str, float]:
    """
    Return:
        relevance label,
        ranking multiplier
    """

    has_structured_fields = bool(
        [
            field
            for field in fields_of_study
            if normalise_text(field)
        ]
    )

    # If structured field information is unavailable,
    # do not treat a low scholarship-name similarity
    # as a confirmed mismatch.
    if not has_structured_fields:
        if similarity >= 0.40:
            return (
                "inferred_good_match",
                0.95,
            )

        return (
            "field_information_unavailable",
            0.85,
        )

    if similarity >= 0.70:
        return (
            "strong_match",
            1.00,
        )

    if similarity >= 0.40:
        return (
            "good_match",
            0.95,
        )

    if similarity >= 0.15:
        return (
            "weak_match",
            0.80,
        )

    return (
        "very_low_relevance",
        0.60,
    )


# ---------------------------------------------------------
# Age eligibility
# ---------------------------------------------------------

def evaluate_age(
    profile: dict[str, Any],
    scholarship: dict[str, Any],
) -> tuple[str, bool | None]:
    """
    True  = known age requirement satisfied
    False = known age requirement failed
    None  = cannot verify
    """

    age_limit = scholarship.get(
        "age_limit"
    )

    if age_limit is None:
        return (
            "Age-limit information is unavailable.",
            None,
        )

    user_age = profile.get("age")

    if user_age is None:
        return (
            "Scholarship has an age requirement, "
            "but the user's age is unavailable.",
            None,
        )

    # For V2 MVP, safely evaluate numeric limits only.
    try:
        maximum_age = float(
            age_limit
        )

        current_age = float(
            user_age
        )

    except (
        TypeError,
        ValueError,
    ):
        return (
            "Age requirement exists but cannot be "
            "evaluated automatically from its current "
            "data format.",
            None,
        )

    if current_age <= maximum_age:
        return (
            "The user's age satisfies the known "
            "age requirement.",
            True,
        )

    return (
        "The user's age exceeds the known "
        "scholarship age limit.",
        False,
    )


# ---------------------------------------------------------
# Deadline eligibility
# ---------------------------------------------------------

def evaluate_deadline(
    scholarship: dict[str, Any],
) -> tuple[str, bool | None]:
    deadline = scholarship.get(
        "application_deadline"
    )

    if deadline is None:
        return (
            "Application deadline is unavailable.",
            None,
        )

    if not isinstance(
        deadline,
        datetime,
    ):
        return (
            "Application deadline exists but cannot "
            "be verified automatically from its "
            "current data format.",
            None,
        )

    today = datetime.now(
        timezone.utc
    ).date()

    deadline_date = deadline.date()

    if deadline_date < today:
        return (
            "The application deadline has passed.",
            False,
        )

    return (
        "Application deadline is "
        f"{deadline_date.isoformat()}.",
        True,
    )


# ---------------------------------------------------------
# Eligibility result helper
# ---------------------------------------------------------

def add_eligibility_check(
    checks: dict[str, dict[str, Any]],
    name: str,
    message: str,
    result: bool | None,
) -> None:
    if result is True:
        status = "PASS"

    elif result is False:
        status = "FAIL"

    else:
        status = "UNKNOWN"

    checks[name] = {
        "status": status,
        "message": message,
    }


def calculate_eligibility_confidence(
    checks: dict[str, dict[str, Any]],
) -> float:
    """
    Confidence means:
    How many eligibility dimensions could be
    verified from currently available data?
    """

    if not checks:
        return 0.0

    known_count = sum(
        1
        for check in checks.values()
        if check["status"]
        in {
            "PASS",
            "FAIL",
        }
    )

    return round(
        (
            known_count
            / len(checks)
        )
        * 100,
        2,
    )


# ---------------------------------------------------------
# Scholarship evaluation V2
# ---------------------------------------------------------

def evaluate_scholarship_v2(
    profile: dict[str, Any],
    scholarship: dict[str, Any],
    country_name: str,
    university_name: str | None,
) -> dict[str, Any] | None:

    reasons: list[str] = []
    gaps: list[str] = []

    eligibility_checks: dict[
        str,
        dict[str, Any],
    ] = {}

    score_breakdown = {
        "degree_level": 0.0,
        "preferred_country": 0.0,
        "field_similarity": 0.0,
        "funding_type": 0.0,
        "scholarship_status": 0.0,
    }

    # =====================================================
    # HARD RULE 1 — Degree
    # =====================================================

    target_degree = normalise_text(
        profile.get(
            "target_degree_level"
        )
    )

    scholarship_degrees = {
        normalise_text(
            degree
        )
        for degree
        in scholarship.get(
            "degree_levels",
            [],
        )
    }

    if (
        not target_degree
        or target_degree
        not in scholarship_degrees
    ):
        return None

    score_breakdown[
        "degree_level"
    ] = DEGREE_LEVEL_WEIGHT

    reasons.append(
        "Target degree level is supported "
        "by the scholarship."
    )

    # =====================================================
    # HARD RULE 2 — Country
    # =====================================================

    preferred_countries = {
        normalise_text(
            country
        )
        for country
        in profile.get(
            "preferred_countries",
            [],
        )
    }

    if (
        preferred_countries
        and normalise_text(
            country_name
        )
        not in preferred_countries
    ):
        return None

    score_breakdown[
        "preferred_country"
    ] = COUNTRY_WEIGHT

    reasons.append(
        "Scholarship is available in "
        f"preferred country: {country_name}."
    )

    # =====================================================
    # HARD RULE 3 — Scholarship status
    # =====================================================

    scholarship_status = normalise_text(
        scholarship.get(
            "scholarship_status"
        )
    )

    if scholarship_status == "closed":
        return None

    if scholarship_status in {
        "open",
        "upcoming",
    }:
        score_breakdown[
            "scholarship_status"
        ] = STATUS_WEIGHT

        reasons.append(
            "Scholarship status is "
            f"'{scholarship_status}'."
        )

    else:
        gaps.append(
            "Scholarship status is unknown."
        )

    # =====================================================
    # Field similarity
    # =====================================================

    preferred_major = str(
        profile.get(
            "preferred_major"
        )
        or ""
    )

    fields_of_study = (
        scholarship.get(
            "fields_of_study"
        )
        or []
    )

    field_similarity = (
        calculate_best_field_similarity(
            preferred_major=
                preferred_major,

            scholarship_name=str(
                scholarship.get(
                    "scholarship_name"
                )
                or ""
            ),

            fields_of_study=
                fields_of_study,
        )
    )

    field_score = (
        field_similarity
        * FIELD_SIMILARITY_WEIGHT
    )

    score_breakdown[
        "field_similarity"
    ] = round(
        field_score,
        2,
    )

    (
        field_relevance,
        field_multiplier,
    ) = get_field_relevance(
        similarity=
            field_similarity,

        fields_of_study=
            fields_of_study,
    )

    reasons.append(
        "Preferred-major and scholarship-field "
        f"similarity is "
        f"{field_similarity * 100:.2f}%."
    )

    if (
        field_relevance
        == "very_low_relevance"
    ):
        gaps.append(
            "Scholarship field information exists, "
            "but it has very low relevance to the "
            "user's preferred major."
        )

    elif (
        field_relevance
        == "weak_match"
    ):
        gaps.append(
            "The scholarship has only a weak "
            "field match with the preferred major."
        )

    elif (
        field_relevance
        == "field_information_unavailable"
    ):
        gaps.append(
            "Structured field-of-study information "
            "is unavailable, so field relevance "
            "cannot be fully confirmed."
        )

    # =====================================================
    # Funding preference
    # =====================================================

    preferred_funding_type = (
        normalise_text(
            profile.get(
                "preferred_funding_type"
            )
        )
    )

    scholarship_funding_type = (
        normalise_text(
            scholarship.get(
                "funding_type"
            )
        )
    )

    if (
        not preferred_funding_type
        or preferred_funding_type
        == "any"
    ):
        score_breakdown[
            "funding_type"
        ] = FUNDING_TYPE_WEIGHT

        reasons.append(
            "The user accepts any scholarship "
            "funding type."
        )

    elif (
        preferred_funding_type
        == scholarship_funding_type
    ):
        score_breakdown[
            "funding_type"
        ] = FUNDING_TYPE_WEIGHT

        reasons.append(
            "Scholarship funding type matches "
            "the user's preference."
        )

    else:
        gaps.append(
            "Scholarship funding type does not "
            "match the user's preferred funding."
        )

    # =====================================================
    # Eligibility — Nationality
    # =====================================================

    eligible_nationalities = (
        scholarship.get(
            "eligible_nationalities"
        )
        or []
    )

    user_nationality = (
        normalise_text(
            profile.get(
                "nationality"
            )
        )
    )

    if not eligible_nationalities:
        nationality_result = None

        nationality_message = (
            "Eligible-nationality information "
            "is unavailable."
        )

    else:
        normalised_nationalities = {
            normalise_text(
                nationality
            )
            for nationality
            in eligible_nationalities
        }

        nationality_result = (
            user_nationality
            in normalised_nationalities
            or contains_generic_nationality(
                eligible_nationalities
            )
        )

        if nationality_result:
            nationality_message = (
                "The user's nationality satisfies "
                "the known nationality requirement."
            )

        else:
            nationality_message = (
                "The user's nationality does not "
                "satisfy the known requirement."
            )

    add_eligibility_check(
        eligibility_checks,
        "nationality",
        nationality_message,
        nationality_result,
    )

    if nationality_result is False:
        return None

    if nationality_result is None:
        gaps.append(
            nationality_message
        )

    else:
        reasons.append(
            nationality_message
        )

    # =====================================================
    # Eligibility — GPA
    # =====================================================

    gpa_message, gpa_result = (
        evaluate_gpa(
            profile=
                profile,

            scholarship=
                scholarship,
        )
    )

    add_eligibility_check(
        eligibility_checks,
        "gpa",
        gpa_message,
        gpa_result,
    )

    if gpa_result is False:
        return None

    if gpa_result is None:
        gaps.append(
            gpa_message
        )

    else:
        reasons.append(
            gpa_message
        )

    # =====================================================
    # Eligibility — English
    # =====================================================

    (
        english_message,
        english_result,
    ) = evaluate_english_requirement(
        profile=
            profile,

        scholarship=
            scholarship,
    )

    add_eligibility_check(
        eligibility_checks,
        "english",
        english_message,
        english_result,
    )

    if english_result is False:
        return None

    if english_result is None:
        gaps.append(
            english_message
        )

    else:
        reasons.append(
            english_message
        )

    # =====================================================
    # Eligibility — Age
    # =====================================================

    age_message, age_result = (
        evaluate_age(
            profile=
                profile,

            scholarship=
                scholarship,
        )
    )

    add_eligibility_check(
        eligibility_checks,
        "age",
        age_message,
        age_result,
    )

    if age_result is False:
        return None

    if age_result is None:
        gaps.append(
            age_message
        )

    else:
        reasons.append(
            age_message
        )

    # =====================================================
    # Eligibility — Deadline
    # =====================================================

    (
        deadline_message,
        deadline_result,
    ) = evaluate_deadline(
        scholarship
    )

    add_eligibility_check(
        eligibility_checks,
        "deadline",
        deadline_message,
        deadline_result,
    )

    if deadline_result is False:
        return None

    if deadline_result is None:
        gaps.append(
            deadline_message
        )

    else:
        reasons.append(
            deadline_message
        )

    # =====================================================
    # Final scoring
    # =====================================================

    base_match_score = round(
        sum(
            score_breakdown.values()
        ),
        2,
    )

    final_match_score = round(
        base_match_score
        * field_multiplier,
        2,
    )

    eligibility_confidence = (
        calculate_eligibility_confidence(
            eligibility_checks
        )
    )

    unknown_eligibility_checks = sum(
        1
        for check
        in eligibility_checks.values()
        if check["status"]
        == "UNKNOWN"
    )

    if unknown_eligibility_checks == 0:
        eligibility_status = (
            "eligible_under_available_rules"
        )

    else:
        eligibility_status = (
            "eligible_under_known_rules_with_gaps"
        )

    # =====================================================
    # Result
    # =====================================================

    return {
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

        "provider_type":
            scholarship.get(
                "provider_type"
            ),

        "country_id":
            scholarship.get(
                "country_id"
            ),

        "country_name":
            country_name,

        "host_university_id":
            scholarship.get(
                "host_university_id"
            ),

        "host_university_name":
            university_name,

        "degree_levels":
            scholarship.get(
                "degree_levels"
            )
            or [],

        "fields_of_study":
            fields_of_study,

        "funding_type":
            scholarship.get(
                "funding_type"
            ),

        "tuition_coverage":
            scholarship.get(
                "tuition_coverage"
            ),

        "monthly_allowance":
            scholarship.get(
                "monthly_allowance"
            ),

        "allowance_currency":
            scholarship.get(
                "allowance_currency"
            ),

        "application_opening_date":
            datetime_to_iso_date(
                scholarship.get(
                    "application_opening_date"
                )
            ),

        "application_deadline":
            datetime_to_iso_date(
                scholarship.get(
                    "application_deadline"
                )
            ),

        "scholarship_status":
            scholarship.get(
                "scholarship_status"
            ),

        "application_cycle":
            scholarship.get(
                "application_cycle"
            ),

        "official_website":
            scholarship.get(
                "official_website"
            ),

        "source_url":
            scholarship.get(
                "source_url"
            ),

        "match_score":
            final_match_score,

        "base_match_score":
            base_match_score,

        "maximum_score":
            MAXIMUM_MATCH_SCORE,

        "field_similarity":
            round(
                field_similarity,
                4,
            ),

        "field_relevance":
            field_relevance,

        "field_relevance_multiplier":
            field_multiplier,

        "score_breakdown":
            score_breakdown,

        "eligibility_status":
            eligibility_status,

        "eligibility_confidence":
            eligibility_confidence,

        "eligibility_checks":
            eligibility_checks,

        "match_reasons":
            reasons,

        "requirement_gaps":
            gaps,
    }


# ---------------------------------------------------------
# Recommendation generation
# ---------------------------------------------------------

def generate_scholarship_recommendations_v2(
    database: Any,
    user_id: str,
    top_k: int,
) -> dict[str, Any]:

    profile = (
        database[
            "user_profiles"
        ]
        .find_one(
            {
                "user_id":
                    user_id
            },
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )
    )

    if profile is None:
        raise ValueError(
            f"User profile '{user_id}' "
            "was not found."
        )

    country_name_by_id = {
        country["country_id"]:
            country["country_name"]

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
        university["university_id"]:
            university["university_name"]

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

    recommendations: list[
        dict[str, Any]
    ] = []

    rejected_by_hard_rules = 0

    skipped_missing_relationship = 0

    for scholarship in scholarships:
        country_id = scholarship.get(
            "country_id"
        )

        country_name = (
            country_name_by_id.get(
                country_id
            )
        )

        if country_name is None:
            skipped_missing_relationship += 1
            continue

        host_university_id = (
            scholarship.get(
                "host_university_id"
            )
        )

        university_name = None

        if host_university_id is not None:
            university_name = (
                university_name_by_id.get(
                    host_university_id
                )
            )

            if university_name is None:
                skipped_missing_relationship += 1
                continue

        recommendation = (
            evaluate_scholarship_v2(
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
            rejected_by_hard_rules += 1
            continue

        recommendations.append(
            recommendation
        )

    # -----------------------------------------------------
    # Ranking
    # -----------------------------------------------------

    recommendations.sort(
        key=lambda item: (
            item[
                "match_score"
            ],

            item[
                "eligibility_confidence"
            ],

            item[
                "field_similarity"
            ],
        ),
        reverse=True,
    )

    top_recommendations = (
        recommendations[
            :top_k
        ]
    )

    return {
        "user_id":
            user_id,

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "algorithm": {
            "name":
                (
                    "EduPath Hybrid Scholarship "
                    "Recommendation v2"
                ),

            "match_score_weights": {
                "degree_level":
                    DEGREE_LEVEL_WEIGHT,

                "preferred_country":
                    COUNTRY_WEIGHT,

                "field_similarity":
                    FIELD_SIMILARITY_WEIGHT,

                "funding_type":
                    FUNDING_TYPE_WEIGHT,

                "scholarship_status":
                    STATUS_WEIGHT,
            },

            "maximum_match_score":
                MAXIMUM_MATCH_SCORE,

            "content_similarity_method":
                "TF-IDF cosine similarity",

            "eligibility_model":
                (
                    "PASS / FAIL / UNKNOWN "
                    "with separate confidence"
                ),

            "field_relevance_adjustment":
                True,
        },

        "user_profile_summary": {
            "nationality":
                profile.get(
                    "nationality"
                ),

            "age":
                profile.get(
                    "age"
                ),

            "target_degree_level":
                profile.get(
                    "target_degree_level"
                ),

            "preferred_major":
                profile.get(
                    "preferred_major"
                ),

            "gpa":
                profile.get(
                    "gpa"
                ),

            "gpa_scale":
                profile.get(
                    "gpa_scale"
                ),

            "ielts_score":
                profile.get(
                    "ielts_score"
                ),

            "toefl_score":
                profile.get(
                    "toefl_score"
                ),

            "preferred_countries":
                profile.get(
                    "preferred_countries"
                ),

            "scholarship_required":
                profile.get(
                    "scholarship_required"
                ),

            "preferred_funding_type":
                profile.get(
                    "preferred_funding_type"
                ),
        },

        "total_scholarship_candidates":
            len(
                scholarships
            ),

        "eligible_candidates":
            len(
                recommendations
            ),

        "rejected_by_hard_rules":
            rejected_by_hard_rules,

        "skipped_missing_relationship":
            skipped_missing_relationship,

        "returned_recommendations":
            len(
                top_recommendations
            ),

        "recommendations":
            top_recommendations,
    }


# ---------------------------------------------------------
# Console output
# ---------------------------------------------------------

def main() -> None:
    print("=" * 72)

    print(
        "EduPath Scholarship Recommendation "
        "Engine V2"
    )

    print("=" * 72)

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

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
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

        result = (
            generate_scholarship_recommendations_v2(
                database=
                    database,

                user_id=
                    USER_ID,

                top_k=
                    TOP_K,
            )
        )

        OUTPUT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        with OUTPUT_JSON.open(
            "w",
            encoding="utf-8",
        ) as output_file:
            json.dump(
                result,
                output_file,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )

        print()
        print(
            "Recommendation summary"
        )

        print(
            "-" * 72
        )

        print(
            "User ID:",
            result[
                "user_id"
            ],
        )

        print(
            "Total scholarship candidates:",
            result[
                "total_scholarship_candidates"
            ],
        )

        print(
            "Eligible candidates:",
            result[
                "eligible_candidates"
            ],
        )

        print(
            "Rejected by hard rules:",
            result[
                "rejected_by_hard_rules"
            ],
        )

        print(
            "Returned recommendations:",
            result[
                "returned_recommendations"
            ],
        )

        print(
            "Output JSON:",
            OUTPUT_JSON,
        )

        print()
        print(
            "Ranked recommendations"
        )

        print(
            "-" * 72
        )

        for rank, recommendation in enumerate(
            result[
                "recommendations"
            ],
            start=1,
        ):
            print(
                f"{rank}. "
                f"{recommendation['scholarship_name']}"
            )

            print(
                "   Match score: "
                f"{recommendation['match_score']}"
                "/100"
            )

            print(
                "   Base score: "
                f"{recommendation['base_match_score']}"
                "/100"
            )

            print(
                "   Field similarity: "
                f"{recommendation['field_similarity'] * 100:.2f}%"
            )

            print(
                "   Field relevance: "
                f"{recommendation['field_relevance']}"
            )

            print(
                "   Eligibility status: "
                f"{recommendation['eligibility_status']}"
            )

            print(
                "   Eligibility confidence: "
                f"{recommendation['eligibility_confidence']}"
                "%"
            )

            print()

        print(
            "V2 recommendation generation "
            "completed successfully."
        )

        print(
            "No MongoDB records were modified."
        )

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