from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# REUSE STABLE V1 HELPERS / CONFIGURATION
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
    / "scholarship_recommendations_v21.json"
)


# =========================================================
# V2.1 MATCH SCORE WEIGHTS
# =========================================================
#
# Match Score measures:
# "How well does this scholarship fit the user's
# academic and funding preferences?"
#
# Eligibility is NOT mixed into this score.
# =========================================================

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


# =========================================================
# FIELD-UNCERTAINTY SETTINGS
# =========================================================
#
# Important rule:
#
# Missing field information != Field mismatch
#
# If structured fields_of_study exist:
#     use actual TF-IDF similarity.
#
# If structured fields_of_study are missing:
#     give neutral 50% of field points
#     and allow scholarship-name similarity
#     to provide limited additional evidence.
#
# A small multiplier is then applied because
# the recommendation has lower field certainty.
# =========================================================

UNKNOWN_FIELD_BASE_CREDIT = 0.50

UNKNOWN_FIELD_MULTIPLIER = 0.90


# =========================================================
# TEXT SIMILARITY
# =========================================================

def calculate_text_similarity(
    left_text: str,
    right_text: str,
) -> float:
    """
    Calculate TF-IDF cosine similarity
    between two pieces of text.

    Returns:
        float between 0.0 and 1.0
    """

    left_text = str(
        left_text or ""
    ).strip()

    right_text = str(
        right_text or ""
    ).strip()

    if (
        not left_text
        or not right_text
    ):
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )

        matrix = vectorizer.fit_transform(
            [
                left_text,
                right_text,
            ]
        )

        similarity = cosine_similarity(
            matrix[0:1],
            matrix[1:2],
        )[0][0]

        return float(
            max(
                0.0,
                min(
                    1.0,
                    similarity,
                ),
            )
        )

    except ValueError:
        return 0.0


# =========================================================
# STRUCTURED FIELD SIMILARITY
# =========================================================

def calculate_structured_field_similarity(
    preferred_major: str,
    fields_of_study: list[str],
) -> float:
    """
    Compare preferred_major ONLY against
    structured fields_of_study.

    This prevents the scholarship title
    from incorrectly dominating a known
    field-of-study mismatch.
    """

    preferred_major = str(
        preferred_major or ""
    ).strip()

    valid_fields = [
        str(field).strip()
        for field in fields_of_study
        if str(
            field or ""
        ).strip()
    ]

    if (
        not preferred_major
        or not valid_fields
    ):
        return 0.0

    similarities = [
        calculate_text_similarity(
            preferred_major,
            field,
        )
        for field in valid_fields
    ]

    if not similarities:
        return 0.0

    return max(
        similarities
    )


# =========================================================
# SCHOLARSHIP-NAME SIMILARITY
# =========================================================

def calculate_name_similarity(
    preferred_major: str,
    scholarship_name: str,
) -> float:
    """
    Used only as weak supporting evidence
    when structured fields_of_study are
    unavailable.
    """

    return calculate_text_similarity(
        preferred_major,
        scholarship_name,
    )


# =========================================================
# FIELD RELEVANCE
# =========================================================

def get_field_relevance(
    field_similarity: float,
    has_structured_fields: bool,
) -> tuple[str, float]:
    """
    Returns:
        field relevance label,
        field relevance multiplier
    """

    if not has_structured_fields:
        return (
            "field_information_unavailable",
            UNKNOWN_FIELD_MULTIPLIER,
        )

    if field_similarity >= 0.70:
        return (
            "strong_match",
            1.00,
        )

    if field_similarity >= 0.40:
        return (
            "good_match",
            0.95,
        )

    if field_similarity >= 0.15:
        return (
            "weak_match",
            0.80,
        )

    return (
        "very_low_relevance",
        0.60,
    )


# =========================================================
# FIELD SCORE CALCULATION
# =========================================================

def calculate_field_score(
    preferred_major: str,
    scholarship_name: str,
    fields_of_study: list[str],
) -> dict[str, Any]:
    """
    V2.1 field scoring.

    Case A:
        Structured field data exists.

        -> Real field similarity controls
           the full 35 points.

    Case B:
        Structured field data is missing.

        -> Missing data is NOT considered
           a confirmed mismatch.

        -> Give neutral half-credit.

        -> Scholarship title similarity
           provides limited extra evidence.

        -> Apply a small uncertainty
           multiplier later.
    """

    structured_fields = [
        str(field).strip()
        for field in (
            fields_of_study
            or []
        )
        if str(
            field or ""
        ).strip()
    ]

    has_structured_fields = bool(
        structured_fields
    )

    if has_structured_fields:
        field_similarity = (
            calculate_structured_field_similarity(
                preferred_major=
                    preferred_major,

                fields_of_study=
                    structured_fields,
            )
        )

        name_similarity = (
            calculate_name_similarity(
                preferred_major=
                    preferred_major,

                scholarship_name=
                    scholarship_name,
            )
        )

        field_score = (
            field_similarity
            * FIELD_SIMILARITY_WEIGHT
        )

        field_score_method = (
            "structured_field_similarity"
        )

    else:
        field_similarity = 0.0

        name_similarity = (
            calculate_name_similarity(
                preferred_major=
                    preferred_major,

                scholarship_name=
                    scholarship_name,
            )
        )

        neutral_points = (
            FIELD_SIMILARITY_WEIGHT
            * UNKNOWN_FIELD_BASE_CREDIT
        )

        remaining_points = (
            FIELD_SIMILARITY_WEIGHT
            - neutral_points
        )

        field_score = (
            neutral_points
            + (
                name_similarity
                * remaining_points
            )
        )

        field_score_method = (
            "neutral_credit_with_name_evidence"
        )

    (
        field_relevance,
        field_multiplier,
    ) = get_field_relevance(
        field_similarity=
            field_similarity,

        has_structured_fields=
            has_structured_fields,
    )

    return {
        "field_similarity":
            round(
                field_similarity,
                4,
            ),

        "name_similarity":
            round(
                name_similarity,
                4,
            ),

        "field_score":
            round(
                field_score,
                2,
            ),

        "field_relevance":
            field_relevance,

        "field_relevance_multiplier":
            field_multiplier,

        "field_score_method":
            field_score_method,

        "has_structured_fields":
            has_structured_fields,

        "structured_fields":
            structured_fields,
    }


# =========================================================
# AGE ELIGIBILITY
# =========================================================

def evaluate_age(
    profile: dict[str, Any],
    scholarship: dict[str, Any],
) -> tuple[str, bool | None]:
    """
    Return:
        message,
        True  -> requirement satisfied
        False -> requirement failed
        None  -> unknown / cannot verify
    """

    age_limit = scholarship.get(
        "age_limit"
    )

    if age_limit is None:
        return (
            "Age-limit information is unavailable.",
            None,
        )

    user_age = profile.get(
        "age"
    )

    if user_age is None:
        return (
            "Scholarship has an age requirement, "
            "but the user's age is unavailable.",
            None,
        )

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
            "evaluated automatically from its "
            "current data format.",
            None,
        )

    if current_age <= maximum_age:
        return (
            "The user's age satisfies the "
            "known age requirement.",
            True,
        )

    return (
        "The user's age exceeds the known "
        "scholarship age limit.",
        False,
    )


# =========================================================
# DEADLINE ELIGIBILITY
# =========================================================

def evaluate_deadline(
    scholarship: dict[str, Any],
) -> tuple[str, bool | None]:
    """
    Evaluate application deadline.

    True:
        deadline is still valid

    False:
        deadline has already passed

    None:
        deadline unavailable or cannot
        be interpreted automatically
    """

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
            "Application deadline exists but "
            "cannot be evaluated automatically "
            "from its current data format.",
            None,
        )

    today = datetime.now(
        timezone.utc
    ).date()

    deadline_date = (
        deadline.date()
    )

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


# =========================================================
# ELIGIBILITY CHECK HELPER
# =========================================================

def add_eligibility_check(
    checks: dict[str, dict[str, Any]],
    name: str,
    message: str,
    result: bool | None,
) -> None:
    """
    Convert boolean/unknown eligibility result
    into PASS / FAIL / UNKNOWN.
    """

    if result is True:
        status = "PASS"

    elif result is False:
        status = "FAIL"

    else:
        status = "UNKNOWN"

    checks[name] = {
        "status":
            status,

        "message":
            message,
    }


# =========================================================
# ELIGIBILITY CONFIDENCE
# =========================================================

def calculate_eligibility_confidence(
    checks: dict[str, dict[str, Any]],
) -> float:
    """
    Eligibility Confidence does NOT mean
    probability of winning a scholarship.

    It means:

    How many eligibility dimensions can
    currently be verified from available data?
    """

    if not checks:
        return 0.0

    known_count = sum(
        1
        for check
        in checks.values()
        if check[
            "status"
        ]
        in {
            "PASS",
            "FAIL",
        }
    )

    confidence = (
        known_count
        / len(checks)
    ) * 100

    return round(
        confidence,
        2,
    )


# =========================================================
# SCHOLARSHIP EVALUATION — V2.1
# =========================================================

def evaluate_scholarship_v21(
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
    # HARD RULE 3 — SCHOLARSHIP STATUS
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

    field_multiplier = (
        field_result[
            "field_relevance_multiplier"
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
    # Field explanation
    # -----------------------------------------------------

    if has_structured_fields:
        reasons.append(
            "Structured scholarship field data "
            "is available."
        )

        reasons.append(
            "Preferred-major and structured "
            "scholarship-field similarity is "
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
            "confirmed field mismatch."
        )

        reasons.append(
            "Scholarship-name similarity provides "
            f"{name_similarity * 100:.2f}% "
            "supporting field evidence."
        )

    if field_relevance == "very_low_relevance":
        gaps.append(
            "Structured scholarship field data "
            "has very low relevance to the "
            "user's preferred major."
        )

    elif field_relevance == "weak_match":
        gaps.append(
            "The scholarship has only a weak "
            "field match with the preferred major."
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
    # BASE MATCH SCORE
    # =====================================================

    base_match_score = round(
        sum(
            score_breakdown.values()
        ),
        2,
    )

    # =====================================================
    # FIELD RELEVANCE ADJUSTMENT
    # =====================================================

    final_match_score = round(
        base_match_score
        * field_multiplier,
        2,
    )

    final_match_score = max(
        0.0,
        min(
            100.0,
            final_match_score,
        ),
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
    # RETURN RESULT
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
        # V2.1 scoring outputs
        # -------------------------------------------------

        "match_score":
            final_match_score,

        "base_match_score":
            base_match_score,

        "maximum_score":
            MAXIMUM_MATCH_SCORE,

        "score_breakdown":
            score_breakdown,

        # -------------------------------------------------
        # Field evidence
        # -------------------------------------------------

        "field_similarity":
            field_similarity,

        "name_similarity":
            name_similarity,

        "field_relevance":
            field_relevance,

        "field_relevance_multiplier":
            field_multiplier,

        "field_score_method":
            field_score_method,

        "structured_field_data_available":
            has_structured_fields,

        # -------------------------------------------------
        # Eligibility
        # -------------------------------------------------

        "eligibility_status":
            eligibility_status,

        "eligibility_confidence":
            eligibility_confidence,

        "eligibility_checks":
            eligibility_checks,

        # -------------------------------------------------
        # Explanations
        # -------------------------------------------------

        "match_reasons":
            reasons,

        "requirement_gaps":
            gaps,
    }


# =========================================================
# GENERATE RECOMMENDATIONS
# =========================================================

def generate_scholarship_recommendations_v21(
    database: Any,
    user_id: str,
    top_k: int,
) -> dict[str, Any]:

    # -----------------------------------------------------
    # USER PROFILE
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
    # COUNTRY LOOKUP
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
    # UNIVERSITY LOOKUP
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
    # SCHOLARSHIPS
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
    # EVALUATE EACH SCHOLARSHIP
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
            evaluate_scholarship_v21(
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
    # RANKING
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

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

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
                    "Recommendation v2.1"
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

            "structured_field_method":
                "TF-IDF cosine similarity",

            "missing_field_strategy":
                (
                    "50% neutral field credit "
                    "+ limited scholarship-name "
                    "similarity evidence"
                ),

            "unknown_field_base_credit":
                UNKNOWN_FIELD_BASE_CREDIT,

            "unknown_field_multiplier":
                UNKNOWN_FIELD_MULTIPLIER,

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


# =========================================================
# CONSOLE OUTPUT
# =========================================================

def main() -> None:
    print("=" * 78)

    print(
        "EduPath Scholarship Recommendation "
        "Engine V2.1"
    )

    print("=" * 78)

    # -----------------------------------------------------
    # ENVIRONMENT SAFETY CHECKS
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
    # CONNECT
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
        # GENERATE RECOMMENDATIONS
        # -------------------------------------------------

        result = (
            generate_scholarship_recommendations_v21(
                database=
                    database,

                user_id=
                    USER_ID,

                top_k=
                    TOP_K,
            )
        )

        # -------------------------------------------------
        # WRITE OUTPUT JSON
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
        # SUMMARY
        # -------------------------------------------------

        print()

        print(
            "Recommendation summary"
        )

        print(
            "-" * 78
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
        # RANKED RESULTS
        # -------------------------------------------------

        print()

        print(
            "Ranked recommendations"
        )

        print(
            "-" * 78
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
                "   Field score: "
                f"{recommendation['score_breakdown']['field_similarity']}"
                f"/{FIELD_SIMILARITY_WEIGHT}"
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
                "   Structured field data: "
                f"{recommendation['structured_field_data_available']}"
            )

            print(
                "   Field score method: "
                f"{recommendation['field_score_method']}"
            )

            print(
                "   Field relevance: "
                f"{recommendation['field_relevance']}"
            )

            print(
                "   Field multiplier: "
                f"{recommendation['field_relevance_multiplier']}"
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
        # SUCCESS
        # -------------------------------------------------

        print()

        print("=" * 78)

        print(
            "V2.1 recommendation generation "
            "completed successfully."
        )

        print(
            "No MongoDB records were modified."
        )

        print("=" * 78)

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