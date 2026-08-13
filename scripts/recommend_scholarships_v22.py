from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# =========================================================
# REUSE VERIFIED PROJECT CONFIG + V2.1 HELPERS
# =========================================================

from recommend_scholarships_v1_backup import (
    PROJECT_ROOT,
    ENV_FILE,
    MONGODB_URI,
    DATABASE_NAME,
    USER_ID,
    TOP_K,
    normalise_text,
    datetime_to_iso_date,
    contains_generic_nationality,
    evaluate_gpa,
    evaluate_english_requirement,
)

from recommend_scholarships_v21 import (
    calculate_field_score,
    evaluate_age,
    evaluate_deadline,
    add_eligibility_check,
    calculate_eligibility_confidence,
)


# =========================================================
# OUTPUT
# =========================================================

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
)

OUTPUT_JSON = (
    OUTPUT_DIRECTORY
    / "scholarship_recommendations_v22.json"
)


# =========================================================
# MATCH / FIT SCORE WEIGHTS
# =========================================================
#
# Fit Score answers:
#
# "How well does this scholarship fit the user's
# academic and funding preferences?"
#
# Eligibility is kept separate.
# =========================================================

DEGREE_LEVEL_WEIGHT = 20
COUNTRY_WEIGHT = 15
FIELD_SIMILARITY_WEIGHT = 35
FUNDING_TYPE_WEIGHT = 20
STATUS_WEIGHT = 10


MAXIMUM_FIT_SCORE = (
    DEGREE_LEVEL_WEIGHT
    + COUNTRY_WEIGHT
    + FIELD_SIMILARITY_WEIGHT
    + FUNDING_TYPE_WEIGHT
    + STATUS_WEIGHT
)


# =========================================================
# CONFIDENCE-AWARE RANKING
# =========================================================
#
# The Fit Score itself is NOT reduced simply because
# some information is missing.
#
# Instead:
#
#   1. Calculate Fit Score.
#   2. Calculate Match Data Confidence.
#   3. Produce a confidence-aware Ranking Score.
#
# Ranking factor:
#
#   0.70 + (0.30 × match_data_confidence_ratio)
#
# This means:
#
#   100% confidence -> factor 1.00
#    65% confidence -> factor 0.895
#     0% confidence -> factor 0.70
#
# Therefore missing data can lower ranking confidence,
# but does NOT automatically mean the scholarship
# is a mismatch.
# =========================================================

MINIMUM_CONFIDENCE_FACTOR = 0.70
CONFIDENCE_ADJUSTMENT_RANGE = 0.30


# =========================================================
# HELPER — SAFE TEXT LIST
# =========================================================

def normalise_list(
    values: Any,
) -> list[str]:
    if not isinstance(
        values,
        list,
    ):
        return []

    result = []

    for value in values:
        text = str(
            value or ""
        ).strip()

        if text:
            result.append(
                text
            )

    return result


# =========================================================
# MATCH DATA CONFIDENCE
# =========================================================

def calculate_match_data_confidence(
    profile: dict[str, Any],
    scholarship: dict[str, Any],
    field_result: dict[str, Any],
    country_name: str,
) -> dict[str, Any]:
    """
    Calculate how much evidence is available for
    the preference-matching dimensions.

    This is separate from eligibility confidence.

    Maximum evidence weight = 100.
    """

    evidence_breakdown = {
        "degree_level": {
            "weight":
                DEGREE_LEVEL_WEIGHT,

            "known":
                False,
        },

        "preferred_country": {
            "weight":
                COUNTRY_WEIGHT,

            "known":
                False,
        },

        "field_information": {
            "weight":
                FIELD_SIMILARITY_WEIGHT,

            "known":
                False,
        },

        "funding_type": {
            "weight":
                FUNDING_TYPE_WEIGHT,

            "known":
                False,
        },

        "scholarship_status": {
            "weight":
                STATUS_WEIGHT,

            "known":
                False,
        },
    }

    # -----------------------------------------------------
    # Degree evidence
    # -----------------------------------------------------

    target_degree = normalise_text(
        profile.get(
            "target_degree_level"
        )
    )

    scholarship_degrees = normalise_list(
        scholarship.get(
            "degree_levels"
        )
    )

    if (
        target_degree
        and scholarship_degrees
    ):
        evidence_breakdown[
            "degree_level"
        ][
            "known"
        ] = True

    # -----------------------------------------------------
    # Country evidence
    # -----------------------------------------------------

    if str(
        country_name or ""
    ).strip():
        evidence_breakdown[
            "preferred_country"
        ][
            "known"
        ] = True

    # -----------------------------------------------------
    # Field evidence
    # -----------------------------------------------------

    if field_result[
        "has_structured_fields"
    ]:
        evidence_breakdown[
            "field_information"
        ][
            "known"
        ] = True

    # -----------------------------------------------------
    # Funding evidence
    # -----------------------------------------------------

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

    # If the user accepts any funding,
    # no additional scholarship evidence is needed
    # for this preference dimension.
    if (
        not preferred_funding_type
        or preferred_funding_type
        == "any"
    ):
        evidence_breakdown[
            "funding_type"
        ][
            "known"
        ] = True

    elif scholarship_funding_type:
        evidence_breakdown[
            "funding_type"
        ][
            "known"
        ] = True

    # -----------------------------------------------------
    # Status evidence
    # -----------------------------------------------------

    scholarship_status = normalise_text(
        scholarship.get(
            "scholarship_status"
        )
    )

    if scholarship_status in {
        "open",
        "upcoming",
        "closed",
    }:
        evidence_breakdown[
            "scholarship_status"
        ][
            "known"
        ] = True

    # -----------------------------------------------------
    # Calculate known evidence weight
    # -----------------------------------------------------

    known_weight = sum(
        item[
            "weight"
        ]
        for item
        in evidence_breakdown.values()
        if item[
            "known"
        ]
    )

    confidence = (
        known_weight
        / MAXIMUM_FIT_SCORE
    ) * 100

    return {
        "confidence":
            round(
                confidence,
                2,
            ),

        "known_weight":
            known_weight,

        "maximum_weight":
            MAXIMUM_FIT_SCORE,

        "evidence_breakdown":
            evidence_breakdown,
    }


# =========================================================
# CONFIDENCE-AWARE RANKING SCORE
# =========================================================

def calculate_ranking_score(
    fit_score: float,
    match_data_confidence: float,
) -> tuple[float, float]:
    """
    Return:
        ranking_score,
        confidence_factor
    """

    confidence_ratio = (
        max(
            0.0,
            min(
                100.0,
                match_data_confidence,
            ),
        )
        / 100.0
    )

    confidence_factor = (
        MINIMUM_CONFIDENCE_FACTOR
        + (
            CONFIDENCE_ADJUSTMENT_RANGE
            * confidence_ratio
        )
    )

    ranking_score = (
        fit_score
        * confidence_factor
    )

    ranking_score = max(
        0.0,
        min(
            100.0,
            ranking_score,
        ),
    )

    return (
        round(
            ranking_score,
            2,
        ),

        round(
            confidence_factor,
            4,
        ),
    )


# =========================================================
# SCHOLARSHIP EVALUATION — V2.2
# =========================================================

def evaluate_scholarship_v22(
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
    # HARD RULE 1 — DEGREE LEVEL
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
    # HARD RULE 2 — COUNTRY
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
    # HARD RULE 3 — STATUS
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
    # FIELD / MAJOR MATCH
    # =====================================================

    preferred_major = str(
        profile.get(
            "preferred_major"
        )
        or ""
    ).strip()

    scholarship_name = str(
        scholarship.get(
            "scholarship_name"
        )
        or ""
    ).strip()

    fields_of_study = (
        scholarship.get(
            "fields_of_study"
        )
        or []
    )

    field_result = (
        calculate_field_score(
            preferred_major=
                preferred_major,

            scholarship_name=
                scholarship_name,

            fields_of_study=
                fields_of_study,
        )
    )

    field_similarity = (
        field_result[
            "field_similarity"
        ]
    )

    name_similarity = (
        field_result[
            "name_similarity"
        ]
    )

    field_score = (
        field_result[
            "field_score"
        ]
    )

    field_relevance = (
        field_result[
            "field_relevance"
        ]
    )

    field_score_method = (
        field_result[
            "field_score_method"
        ]
    )

    has_structured_fields = (
        field_result[
            "has_structured_fields"
        ]
    )

    score_breakdown[
        "field_similarity"
    ] = field_score

    # -----------------------------------------------------
    # Field explanations
    # -----------------------------------------------------

    if has_structured_fields:
        reasons.append(
            "Structured scholarship "
            "field-of-study data is available."
        )

        reasons.append(
            "Preferred-major and structured "
            "field similarity is "
            f"{field_similarity * 100:.2f}%."
        )

    else:
        gaps.append(
            "Structured fields-of-study information "
            "is unavailable."
        )

        reasons.append(
            "Missing field information was treated "
            "as uncertainty rather than as a "
            "confirmed mismatch."
        )

        reasons.append(
            "A neutral field credit was used, "
            "with scholarship-name similarity "
            "providing limited supporting evidence."
        )

        reasons.append(
            "Scholarship-name similarity is "
            f"{name_similarity * 100:.2f}%."
        )

    if field_relevance == "very_low_relevance":
        gaps.append(
            "Known structured field information "
            "has very low relevance to the "
            "preferred major."
        )

    elif field_relevance == "weak_match":
        gaps.append(
            "The known structured field match "
            "is weak."
        )

    elif (
        field_relevance
        == "field_information_unavailable"
    ):
        gaps.append(
            "Field relevance cannot be fully "
            "confirmed because structured field "
            "information is unavailable."
        )

    # =====================================================
    # FUNDING PREFERENCE
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

    elif not scholarship_funding_type:
        gaps.append(
            "Scholarship funding type is unavailable."
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
    # ELIGIBILITY — NATIONALITY
    # =====================================================

    eligible_nationalities = (
        scholarship.get(
            "eligible_nationalities"
        )
        or []
    )

    user_nationality = normalise_text(
        profile.get(
            "nationality"
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
                "satisfy the known nationality "
                "requirement."
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
    # ELIGIBILITY — GPA
    # =====================================================

    (
        gpa_message,
        gpa_result,
    ) = evaluate_gpa(
        profile=
            profile,

        scholarship=
            scholarship,
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
    # ELIGIBILITY — ENGLISH
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
    # ELIGIBILITY — AGE
    # =====================================================

    (
        age_message,
        age_result,
    ) = evaluate_age(
        profile=
            profile,

        scholarship=
            scholarship,
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
    # ELIGIBILITY — DEADLINE
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
    # FIT SCORE
    # =====================================================

    fit_score = round(
        sum(
            score_breakdown.values()
        ),
        2,
    )

    fit_score = max(
        0.0,
        min(
            100.0,
            fit_score,
        ),
    )

    # =====================================================
    # MATCH DATA CONFIDENCE
    # =====================================================

    match_data_result = (
        calculate_match_data_confidence(
            profile=
                profile,

            scholarship=
                scholarship,

            field_result=
                field_result,

            country_name=
                country_name,
        )
    )

    match_data_confidence = (
        match_data_result[
            "confidence"
        ]
    )

    # =====================================================
    # RANKING SCORE
    # =====================================================

    (
        ranking_score,
        confidence_factor,
    ) = calculate_ranking_score(
        fit_score=
            fit_score,

        match_data_confidence=
            match_data_confidence,
    )

    # =====================================================
    # ELIGIBILITY CONFIDENCE
    # =====================================================

    eligibility_confidence = (
        calculate_eligibility_confidence(
            eligibility_checks
        )
    )

    unknown_eligibility_checks = sum(
        1
        for check
        in eligibility_checks.values()
        if check[
            "status"
        ]
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
    # RESULT
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

        # -------------------------------------------------
        # V2.2 MATCH METRICS
        # -------------------------------------------------

        "fit_score":
            fit_score,

        # Backward-compatible alias.
        "base_match_score":
            fit_score,

        "ranking_score":
            ranking_score,

        # Backward-compatible recommendation score.
        "match_score":
            ranking_score,

        "maximum_score":
            MAXIMUM_FIT_SCORE,

        "confidence_factor":
            confidence_factor,

        "score_breakdown":
            score_breakdown,

        # -------------------------------------------------
        # FIELD EVIDENCE
        # -------------------------------------------------

        "field_similarity":
            field_similarity,

        "name_similarity":
            name_similarity,

        "field_relevance":
            field_relevance,

        "field_score_method":
            field_score_method,

        "structured_field_data_available":
            has_structured_fields,

        # -------------------------------------------------
        # MATCH DATA CONFIDENCE
        # -------------------------------------------------

        "match_data_confidence":
            match_data_confidence,

        "match_data_known_weight":
            match_data_result[
                "known_weight"
            ],

        "match_data_maximum_weight":
            match_data_result[
                "maximum_weight"
            ],

        "match_data_evidence":
            match_data_result[
                "evidence_breakdown"
            ],

        # -------------------------------------------------
        # ELIGIBILITY
        # -------------------------------------------------

        "eligibility_status":
            eligibility_status,

        "eligibility_confidence":
            eligibility_confidence,

        "eligibility_checks":
            eligibility_checks,

        # -------------------------------------------------
        # EXPLANATION
        # -------------------------------------------------

        "match_reasons":
            reasons,

        "requirement_gaps":
            gaps,
    }


# =========================================================
# GENERATE RECOMMENDATIONS
# =========================================================

def generate_scholarship_recommendations_v22(
    database: Any,
    user_id: str,
    top_k: int,
) -> dict[str, Any]:

    # -----------------------------------------------------
    # Load user profile
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Country lookup
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # University lookup
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Load scholarships
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Evaluate
    # -----------------------------------------------------

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
            rejected_by_hard_rules += 1
            continue

        recommendations.append(
            recommendation
        )

    # =====================================================
    # RANKING
    # =====================================================

    recommendations.sort(
        key=lambda item: (
            item[
                "ranking_score"
            ],

            item[
                "fit_score"
            ],

            item[
                "match_data_confidence"
            ],

            item[
                "eligibility_confidence"
            ],

            item[
                "field_similarity"
            ],

            item[
                "name_similarity"
            ],
        ),
        reverse=True,
    )

    top_recommendations = (
        recommendations[
            :top_k
        ]
    )

    # =====================================================
    # FINAL PAYLOAD
    # =====================================================

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
                    "Recommendation v2.2"
                ),

            "fit_score_weights": {
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

            "maximum_fit_score":
                MAXIMUM_FIT_SCORE,

            "field_similarity_method":
                "TF-IDF cosine similarity",

            "missing_field_strategy":
                (
                    "Neutral field credit plus "
                    "limited scholarship-name "
                    "evidence"
                ),

            "eligibility_model":
                (
                    "PASS / FAIL / UNKNOWN "
                    "with separate eligibility "
                    "confidence"
                ),

            "match_data_confidence_model":
                (
                    "Known preference-evidence "
                    "weight divided by total "
                    "preference weight"
                ),

            "ranking_formula": (
                "FitScore * "
                "(0.70 + 0.30 * "
                "MatchDataConfidenceRatio)"
            ),

            "minimum_confidence_factor":
                MINIMUM_CONFIDENCE_FACTOR,

            "confidence_adjustment_range":
                CONFIDENCE_ADJUSTMENT_RANGE,
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


# =========================================================
# CONSOLE OUTPUT
# =========================================================

def main() -> None:
    print("=" * 84)

    print(
        "EduPath Scholarship Recommendation "
        "Engine V2.2"
    )

    print("=" * 84)

    # -----------------------------------------------------
    # Environment safety
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
    # MongoDB connection
    # -----------------------------------------------------

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

        # -------------------------------------------------
        # Generate
        # -------------------------------------------------

        result = (
            generate_scholarship_recommendations_v22(
                database=
                    database,

                user_id=
                    USER_ID,

                top_k=
                    TOP_K,
            )
        )

        # -------------------------------------------------
        # Output JSON
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        print()

        print(
            "Recommendation summary"
        )

        print(
            "-" * 84
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
            "Skipped missing relationship:",
            result[
                "skipped_missing_relationship"
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

        # -------------------------------------------------
        # Ranked output
        # -------------------------------------------------

        print()

        print(
            "Ranked recommendations"
        )

        print(
            "-" * 84
        )

        for (
            rank,
            recommendation,
        ) in enumerate(
            result[
                "recommendations"
            ],
            start=1,
        ):

            print()

            print(
                f"{rank}. "
                f"{recommendation['scholarship_name']}"
            )

            print(
                "   Provider: "
                f"{recommendation['provider_name']}"
            )

            print(
                "   Country: "
                f"{recommendation['country_name']}"
            )

            print()

            print(
                "   Fit score: "
                f"{recommendation['fit_score']}"
                "/100"
            )

            print(
                "   Ranking score: "
                f"{recommendation['ranking_score']}"
                "/100"
            )

            print(
                "   Match data confidence: "
                f"{recommendation['match_data_confidence']}"
                "%"
            )

            print(
                "   Confidence factor: "
                f"{recommendation['confidence_factor']}"
            )

            print(
                "   Eligibility confidence: "
                f"{recommendation['eligibility_confidence']}"
                "%"
            )

            print(
                "   Eligibility status: "
                f"{recommendation['eligibility_status']}"
            )

            print()

            print(
                "   Field score: "
                f"{recommendation['score_breakdown']['field_similarity']}"
                f"/{FIELD_SIMILARITY_WEIGHT}"
            )

            print(
                "   Structured field data: "
                f"{recommendation['structured_field_data_available']}"
            )

            print(
                "   Structured field similarity: "
                f"{recommendation['field_similarity'] * 100:.2f}%"
            )

            print(
                "   Scholarship-name similarity: "
                f"{recommendation['name_similarity'] * 100:.2f}%"
            )

            print(
                "   Field relevance: "
                f"{recommendation['field_relevance']}"
            )

            print(
                "   Field score method: "
                f"{recommendation['field_score_method']}"
            )

            print()

            print(
                "   Score breakdown:"
            )

            for (
                score_name,
                score_value,
            ) in recommendation[
                "score_breakdown"
            ].items():

                print(
                    f"      - {score_name}: "
                    f"{score_value}"
                )

            print()

            print(
                "   Match data evidence:"
            )

            for (
                evidence_name,
                evidence,
            ) in recommendation[
                "match_data_evidence"
            ].items():

                status = (
                    "KNOWN"
                    if evidence[
                        "known"
                    ]
                    else "UNKNOWN"
                )

                print(
                    f"      - {evidence_name}: "
                    f"{status} "
                    f"({evidence['weight']} pts)"
                )

            print()

            print(
                "   Eligibility checks:"
            )

            for (
                check_name,
                check,
            ) in recommendation[
                "eligibility_checks"
            ].items():

                print(
                    f"      - {check_name}: "
                    f"{check['status']}"
                )

            print()

            print(
                "   Match reasons:"
            )

            for reason in recommendation[
                "match_reasons"
            ]:
                print(
                    f"      + {reason}"
                )

            if recommendation[
                "requirement_gaps"
            ]:

                print()

                print(
                    "   Requirement gaps:"
                )

                for gap in recommendation[
                    "requirement_gaps"
                ]:
                    print(
                        f"      ? {gap}"
                    )

        # -------------------------------------------------
        # Complete
        # -------------------------------------------------

        print()

        print("=" * 84)

        print(
            "V2.2 recommendation generation "
            "completed successfully."
        )

        print(
            "No MongoDB records were modified."
        )

        print("=" * 84)

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