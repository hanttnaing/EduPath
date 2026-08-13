from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# Project configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "cleaned"

OUTPUT_JSON = (
    OUTPUT_DIRECTORY
    / "scholarship_recommendations.json"
)

load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)

USER_ID = "user_test_001"
TOP_K = 5


# ---------------------------------------------------------
# Algorithm weights
# ---------------------------------------------------------

DEGREE_LEVEL_WEIGHT = 20
COUNTRY_WEIGHT = 15
FIELD_SIMILARITY_WEIGHT = 20
FUNDING_TYPE_WEIGHT = 20
STATUS_WEIGHT = 10
NATIONALITY_WEIGHT = 5
GPA_WEIGHT = 5
ENGLISH_WEIGHT = 5

MAXIMUM_SCORE = (
    DEGREE_LEVEL_WEIGHT
    + COUNTRY_WEIGHT
    + FIELD_SIMILARITY_WEIGHT
    + FUNDING_TYPE_WEIGHT
    + STATUS_WEIGHT
    + NATIONALITY_WEIGHT
    + GPA_WEIGHT
    + ENGLISH_WEIGHT
)


# ---------------------------------------------------------
# General helper functions
# ---------------------------------------------------------

def normalise_text(value: Any) -> str:
    """Convert a value into clean lowercase text."""

    if value is None:
        return ""

    return " ".join(
        str(value).strip().lower().split()
    )


def datetime_to_iso_date(value: Any) -> str | None:
    """Convert a MongoDB datetime into YYYY-MM-DD text."""

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")

    return str(value)


def calculate_text_similarity(
    first_text: str,
    second_text: str,
) -> float:
    """Return TF-IDF cosine similarity from 0 to 1."""

    first_text = normalise_text(first_text)
    second_text = normalise_text(second_text)

    if not first_text or not second_text:
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    try:
        matrix = vectorizer.fit_transform(
            [
                first_text,
                second_text,
            ]
        )
    except ValueError:
        return 0.0

    similarity = cosine_similarity(
        matrix[0:1],
        matrix[1:2],
    )[0][0]

    return float(similarity)


def calculate_best_field_similarity(
    preferred_major: str,
    scholarship_name: str,
    fields_of_study: list[str],
) -> float:
    """
    Return the highest similarity between the user's major
    and the scholarship's name or individual study fields.
    """

    candidate_texts = [
        scholarship_name,
        *fields_of_study,
    ]

    similarities = [
        calculate_text_similarity(
            preferred_major,
            candidate_text,
        )
        for candidate_text in candidate_texts
        if candidate_text
    ]

    if not similarities:
        return 0.0

    return max(similarities)


def contains_generic_nationality(
    eligible_nationalities: list[str],
) -> bool:
    """Check for values representing broad eligibility."""

    generic_values = {
        "all",
        "all nationalities",
        "any nationality",
        "international students",
        "all international students",
        "all countries",
    }

    normalised_values = {
        normalise_text(value)
        for value in eligible_nationalities
    }

    return bool(
        generic_values.intersection(normalised_values)
    )


# ---------------------------------------------------------
# Eligibility helper functions
# ---------------------------------------------------------

def evaluate_gpa(
    profile: dict[str, Any],
    scholarship: dict[str, Any],
) -> tuple[str, bool | None]:
    """
    Return a message and eligibility result.

    True  = known requirement is satisfied
    False = known requirement is not satisfied
    None  = requirement cannot be verified
    """

    minimum_gpa = scholarship.get("minimum_gpa")
    required_scale = scholarship.get("gpa_scale")

    user_gpa = profile.get("gpa")
    user_scale = profile.get("gpa_scale")

    if minimum_gpa is None or required_scale is None:
        return (
            "Minimum GPA requirement is unavailable.",
            None,
        )

    if user_gpa is None or user_scale is None:
        return (
            "User GPA information is unavailable.",
            None,
        )

    user_ratio = float(user_gpa) / float(user_scale)

    required_ratio = (
        float(minimum_gpa) / float(required_scale)
    )

    if user_ratio >= required_ratio:
        return (
            "The user's GPA satisfies the known "
            "minimum GPA requirement.",
            True,
        )

    return (
        "The user's GPA is below the known "
        "minimum GPA requirement.",
        False,
    )


def evaluate_english_requirement(
    profile: dict[str, Any],
    scholarship: dict[str, Any],
) -> tuple[str, bool | None]:
    """
    Evaluate known IELTS or TOEFL requirements.

    True  = at least one known requirement is satisfied
    False = evaluated score does not meet the requirement
    None  = eligibility cannot be verified
    """

    required_ielts = scholarship.get(
        "ielts_requirement"
    )

    required_toefl = scholarship.get(
        "toefl_requirement"
    )

    user_ielts = profile.get("ielts_score")
    user_toefl = profile.get("toefl_score")

    if (
        required_ielts is None
        and required_toefl is None
    ):
        return (
            "English-score requirement is unavailable.",
            None,
        )

    requirement_was_evaluated = False

    if (
        required_ielts is not None
        and user_ielts is not None
    ):
        requirement_was_evaluated = True

        if float(user_ielts) >= float(required_ielts):
            return (
                "The user's IELTS score satisfies the "
                "known requirement.",
                True,
            )

    if (
        required_toefl is not None
        and user_toefl is not None
    ):
        requirement_was_evaluated = True

        if float(user_toefl) >= float(required_toefl):
            return (
                "The user's TOEFL score satisfies the "
                "known requirement.",
                True,
            )

    if requirement_was_evaluated:
        return (
            "The user's available English score is below "
            "the known requirement.",
            False,
        )

    return (
        "A language requirement exists, but the matching "
        "user test score is unavailable.",
        None,
    )


# ---------------------------------------------------------
# Scholarship evaluation
# ---------------------------------------------------------

def evaluate_scholarship(
    profile: dict[str, Any],
    scholarship: dict[str, Any],
    country_name: str,
    university_name: str | None,
) -> dict[str, Any] | None:
    """
    Evaluate one scholarship against one user.

    None is returned when a known hard rule fails.
    """

    reasons: list[str] = []
    gaps: list[str] = []

    score_breakdown = {
        "degree_level": 0.0,
        "preferred_country": 0.0,
        "field_similarity": 0.0,
        "funding_type": 0.0,
        "scholarship_status": 0.0,
        "nationality": 0.0,
        "gpa": 0.0,
        "english": 0.0,
    }

    # -----------------------------------------------------
    # Hard rule: Degree level
    # -----------------------------------------------------

    target_degree = normalise_text(
        profile.get("target_degree_level")
    )

    scholarship_degrees = {
        normalise_text(degree)
        for degree in scholarship.get(
            "degree_levels",
            [],
        )
    }

    if target_degree not in scholarship_degrees:
        return None

    score_breakdown["degree_level"] = (
        DEGREE_LEVEL_WEIGHT
    )

    reasons.append(
        "Target degree level is supported by "
        "the scholarship."
    )

    # -----------------------------------------------------
    # Hard rule: Preferred country
    # -----------------------------------------------------

    preferred_countries = {
        normalise_text(country)
        for country in profile.get(
            "preferred_countries",
            [],
        )
    }

    if (
        preferred_countries
        and normalise_text(country_name)
        not in preferred_countries
    ):
        return None

    score_breakdown["preferred_country"] = (
        COUNTRY_WEIGHT
    )

    reasons.append(
        f"Scholarship is available in preferred "
        f"country: {country_name}."
    )

    # -----------------------------------------------------
    # Hard rules: Status and deadline
    # -----------------------------------------------------

    scholarship_status = normalise_text(
        scholarship.get("scholarship_status")
    )

    if scholarship_status == "closed":
        return None

    deadline = scholarship.get(
        "application_deadline"
    )

    if (
        isinstance(deadline, datetime)
        and deadline.date()
        < datetime.now(timezone.utc).date()
    ):
        return None

    if scholarship_status in {"open", "upcoming"}:
        score_breakdown["scholarship_status"] = (
            STATUS_WEIGHT
        )

        reasons.append(
            f"Scholarship status is "
            f"'{scholarship_status}'."
        )

    else:
        gaps.append(
            "Scholarship status is unknown."
        )

    # -----------------------------------------------------
    # Field-of-study similarity
    # -----------------------------------------------------

    preferred_major = str(
        profile.get("preferred_major") or ""
    )

    fields_of_study = scholarship.get(
        "fields_of_study"
    ) or []

    field_similarity = (
        calculate_best_field_similarity(
            preferred_major=preferred_major,
            scholarship_name=str(
                scholarship.get(
                    "scholarship_name"
                ) or ""
            ),
            fields_of_study=fields_of_study,
        )
    )

    field_score = (
        field_similarity
        * FIELD_SIMILARITY_WEIGHT
    )

    score_breakdown["field_similarity"] = round(
        field_score,
        2,
    )

    reasons.append(
        "Preferred-major and scholarship-field "
        f"similarity is "
        f"{field_similarity * 100:.2f}%."
    )

    if field_similarity < 0.50:
        gaps.append(
            "The preferred major is not a strong exact "
            "match with the scholarship study fields."
        )

    # -----------------------------------------------------
    # Funding preference
    # -----------------------------------------------------

    preferred_funding_type = normalise_text(
        profile.get("preferred_funding_type")
    )

    scholarship_funding_type = normalise_text(
        scholarship.get("funding_type")
    )

    if (
        not preferred_funding_type
        or preferred_funding_type == "any"
    ):
        score_breakdown["funding_type"] = (
            FUNDING_TYPE_WEIGHT
        )

        reasons.append(
            "The user accepts any scholarship "
            "funding type."
        )

    elif (
        preferred_funding_type
        == scholarship_funding_type
    ):
        score_breakdown["funding_type"] = (
            FUNDING_TYPE_WEIGHT
        )

        reasons.append(
            "Scholarship funding type matches the "
            "user's preference."
        )

    else:
        gaps.append(
            "Scholarship funding type does not match "
            "the user's preferred funding type."
        )

    # -----------------------------------------------------
    # Nationality eligibility
    # -----------------------------------------------------

    eligible_nationalities = scholarship.get(
        "eligible_nationalities"
    ) or []

    user_nationality = normalise_text(
        profile.get("nationality")
    )

    if not eligible_nationalities:
        gaps.append(
            "Eligible-nationality information is "
            "unavailable."
        )

    else:
        normalised_nationalities = {
            normalise_text(nationality)
            for nationality in eligible_nationalities
        }

        nationality_matches = (
            user_nationality
            in normalised_nationalities
            or contains_generic_nationality(
                eligible_nationalities
            )
        )

        if not nationality_matches:
            return None

        score_breakdown["nationality"] = (
            NATIONALITY_WEIGHT
        )

        reasons.append(
            "The user's nationality satisfies the "
            "known nationality requirement."
        )

    # -----------------------------------------------------
    # GPA eligibility
    # -----------------------------------------------------

    gpa_message, gpa_result = evaluate_gpa(
        profile=profile,
        scholarship=scholarship,
    )

    if gpa_result is False:
        return None

    if gpa_result is True:
        score_breakdown["gpa"] = GPA_WEIGHT
        reasons.append(gpa_message)
    else:
        gaps.append(gpa_message)

    # -----------------------------------------------------
    # English eligibility
    # -----------------------------------------------------

    english_message, english_result = (
        evaluate_english_requirement(
            profile=profile,
            scholarship=scholarship,
        )
    )

    if english_result is False:
        return None

    if english_result is True:
        score_breakdown["english"] = (
            ENGLISH_WEIGHT
        )

        reasons.append(english_message)
    else:
        gaps.append(english_message)

    # -----------------------------------------------------
    # Other requirement gaps
    # -----------------------------------------------------

    if scholarship.get("age_limit") is None:
        gaps.append(
            "Age-limit information is unavailable."
        )

    if deadline is None:
        gaps.append(
            "Application deadline is unavailable."
        )
    else:
        reasons.append(
            "Application deadline is "
            f"{datetime_to_iso_date(deadline)}."
        )

    total_score = round(
        sum(score_breakdown.values()),
        2,
    )

    return {
        "scholarship_id": scholarship.get(
            "scholarship_id"
        ),
        "scholarship_name": scholarship.get(
            "scholarship_name"
        ),
        "provider_name": scholarship.get(
            "provider_name"
        ),
        "provider_type": scholarship.get(
            "provider_type"
        ),
        "country_id": scholarship.get("country_id"),
        "country_name": country_name,
        "host_university_id": scholarship.get(
            "host_university_id"
        ),
        "host_university_name": university_name,
        "degree_levels": scholarship.get(
            "degree_levels"
        ) or [],
        "fields_of_study": fields_of_study,
        "funding_type": scholarship.get(
            "funding_type"
        ),
        "tuition_coverage": scholarship.get(
            "tuition_coverage"
        ),
        "monthly_allowance": scholarship.get(
            "monthly_allowance"
        ),
        "allowance_currency": scholarship.get(
            "allowance_currency"
        ),
        "application_opening_date": (
            datetime_to_iso_date(
                scholarship.get(
                    "application_opening_date"
                )
            )
        ),
        "application_deadline": (
            datetime_to_iso_date(deadline)
        ),
        "scholarship_status": scholarship.get(
            "scholarship_status"
        ),
        "application_cycle": scholarship.get(
            "application_cycle"
        ),
        "official_website": scholarship.get(
            "official_website"
        ),
        "source_url": scholarship.get("source_url"),
        "known_eligibility_status": (
            "eligible_under_known_rules"
        ),
        "match_score": total_score,
        "maximum_score": MAXIMUM_SCORE,
        "field_similarity": round(
            field_similarity,
            4,
        ),
        "score_breakdown": score_breakdown,
        "match_reasons": reasons,
        "requirement_gaps": gaps,
    }


# ---------------------------------------------------------
# Recommendation generation
# ---------------------------------------------------------

def generate_scholarship_recommendations(
    database: Any,
    user_id: str,
    top_k: int,
) -> dict[str, Any]:
    """Generate ranked scholarship recommendations."""

    profile = database["user_profiles"].find_one(
        {"user_id": user_id},
        {
            "_id": 0,
            "content_hash": 0,
            "created_at": 0,
            "database_updated_at": 0,
        },
    )

    if profile is None:
        raise ValueError(
            f"User profile '{user_id}' was not found."
        )

    country_name_by_id = {
        country["country_id"]: country["country_name"]
        for country in database["countries"].find(
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
        for university in database["universities"].find(
            {},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
            },
        )
    }

    scholarships = list(
        database["scholarships"].find(
            {},
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )
    )

    recommendations: list[dict[str, Any]] = []

    rejected_by_hard_rules = 0
    skipped_missing_relationship = 0

    for scholarship in scholarships:
        country_id = scholarship.get("country_id")

        country_name = country_name_by_id.get(
            country_id
        )

        if country_name is None:
            skipped_missing_relationship += 1
            continue

        host_university_id = scholarship.get(
            "host_university_id"
        )

        university_name = None

        if host_university_id is not None:
            university_name = university_name_by_id.get(
                host_university_id
            )

            if university_name is None:
                skipped_missing_relationship += 1
                continue

        recommendation = evaluate_scholarship(
            profile=profile,
            scholarship=scholarship,
            country_name=country_name,
            university_name=university_name,
        )

        if recommendation is None:
            rejected_by_hard_rules += 1
            continue

        recommendations.append(recommendation)

    recommendations.sort(
        key=lambda item: (
            item["match_score"],
            item["field_similarity"],
        ),
        reverse=True,
    )

    top_recommendations = recommendations[:top_k]

    return {
        "user_id": user_id,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "algorithm": {
            "name": (
                "EduPath MVP Hybrid Scholarship "
                "Recommendation v1"
            ),
            "hard_filters": [
                "Target degree level",
                "Preferred country",
                "Scholarship status",
                "Application deadline",
                "Known nationality requirement",
                "Known GPA requirement",
                "Known English requirement",
            ],
            "weighted_components": {
                "degree_level": DEGREE_LEVEL_WEIGHT,
                "preferred_country": COUNTRY_WEIGHT,
                "field_similarity": (
                    FIELD_SIMILARITY_WEIGHT
                ),
                "funding_type": FUNDING_TYPE_WEIGHT,
                "scholarship_status": STATUS_WEIGHT,
                "nationality": NATIONALITY_WEIGHT,
                "gpa": GPA_WEIGHT,
                "english": ENGLISH_WEIGHT,
            },
            "content_similarity_method": (
                "TF-IDF cosine similarity"
            ),
            "maximum_score": MAXIMUM_SCORE,
        },
        "user_profile_summary": {
            "nationality": profile.get("nationality"),
            "target_degree_level": profile.get(
                "target_degree_level"
            ),
            "preferred_major": profile.get(
                "preferred_major"
            ),
            "gpa": profile.get("gpa"),
            "gpa_scale": profile.get("gpa_scale"),
            "ielts_score": profile.get(
                "ielts_score"
            ),
            "toefl_score": profile.get(
                "toefl_score"
            ),
            "preferred_countries": profile.get(
                "preferred_countries"
            ),
            "scholarship_required": profile.get(
                "scholarship_required"
            ),
            "preferred_funding_type": profile.get(
                "preferred_funding_type"
            ),
        },
        "total_scholarship_candidates": len(
            scholarships
        ),
        "eligible_candidates": len(
            recommendations
        ),
        "rejected_by_hard_rules": (
            rejected_by_hard_rules
        ),
        "skipped_missing_relationship": (
            skipped_missing_relationship
        ),
        "returned_recommendations": len(
            top_recommendations
        ),
        "recommendations": top_recommendations,
    }


# ---------------------------------------------------------
# Main programme
# ---------------------------------------------------------

def main() -> None:
    """Connect to MongoDB and generate recommendations."""

    print("=" * 65)
    print("EduPath Scholarship Recommendation Engine")
    print("=" * 65)

    if not ENV_FILE.exists():
        raise FileNotFoundError(
            "The .env file was not found.\n"
            f"Expected location: {ENV_FILE}"
        )

    if not MONGODB_URI:
        raise RuntimeError(
            "MONGODB_URI is missing from the .env file."
        )

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:
        print("Connecting to MongoDB Atlas...")

        client.admin.command("ping")

        print("MongoDB Atlas connection: SUCCESS")

        database = client[DATABASE_NAME]

        result = generate_scholarship_recommendations(
            database=database,
            user_id=USER_ID,
            top_k=TOP_K,
        )

        OUTPUT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        with OUTPUT_JSON.open(
            mode="w",
            encoding="utf-8",
        ) as output_file:
            json.dump(
                result,
                output_file,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )

        print("\nRecommendation summary")
        print("-" * 65)
        print(f"User ID: {result['user_id']}")

        print(
            "Total scholarship candidates: "
            f"{result['total_scholarship_candidates']}"
        )

        print(
            "Eligible candidates: "
            f"{result['eligible_candidates']}"
        )

        print(
            "Rejected by hard rules: "
            f"{result['rejected_by_hard_rules']}"
        )

        print(
            "Returned recommendations: "
            f"{result['returned_recommendations']}"
        )

        print(f"Output JSON: {OUTPUT_JSON}")

        print("\nRanked recommendations")
        print("-" * 65)

        if not result["recommendations"]:
            print("No eligible scholarships were found.")

        for rank, recommendation in enumerate(
            result["recommendations"],
            start=1,
        ):
            scholarship_name = recommendation[
                "scholarship_name"
            ]

            match_score = recommendation[
                "match_score"
            ]

            maximum_score = recommendation[
                "maximum_score"
            ]

            known_status = recommendation[
                "known_eligibility_status"
            ]

            print(f"{rank}. {scholarship_name}")

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
                f"{match_score}/{maximum_score}"
            )

            print(
                "   Known eligibility: "
                f"{known_status}"
            )

            print("   Match reasons:")

            for reason in recommendation[
                "match_reasons"
            ]:
                print(f"   - {reason}")

            print("   Requirement gaps:")

            for gap in recommendation[
                "requirement_gaps"
            ]:
                print(f"   - {gap}")

            print()

        print(
            "Scholarship recommendation generation "
            "completed successfully."
        )

    except PyMongoError as error:
        raise RuntimeError(
            "A MongoDB operation failed.\n"
            "Check Atlas connectivity, IP access, "
            "database user, and permissions."
        ) from error

    finally:
        client.close()
        print("MongoDB connection closed safely.")


if __name__ == "__main__":
    main()