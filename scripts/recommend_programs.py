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
    / "program_recommendations.json"
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

DEGREE_LEVEL_WEIGHT = 25
COUNTRY_WEIGHT = 20
MAJOR_SIMILARITY_WEIGHT = 25
BUDGET_WEIGHT = 20
INTAKE_WEIGHT = 10

MAXIMUM_SCORE = (
    DEGREE_LEVEL_WEIGHT
    + COUNTRY_WEIGHT
    + MAJOR_SIMILARITY_WEIGHT
    + BUDGET_WEIGHT
    + INTAKE_WEIGHT
)


# ---------------------------------------------------------
# Text helper functions
# ---------------------------------------------------------

def normalise_text(value: Any) -> str:
    """Convert a value into clean lowercase text."""

    if value is None:
        return ""

    return " ".join(
        str(value).strip().lower().split()
    )

def normalise_degree_level(value: object) -> str:
    """
    Convert different degree-level labels into one canonical value.

    Examples:
    Master's / Master / Masters -> master
    Bachelor's / Bachelor -> bachelor
    PhD / Doctoral / Doctorate -> doctorate
    """

    text = normalise_text(value)

    if not text:
        return ""

    master_aliases = {
        "master",
        "masters",
        "master's",
        "master degree",
        "masters degree",
        "master's degree",
    }

    bachelor_aliases = {
        "bachelor",
        "bachelors",
        "bachelor's",
        "undergraduate",
        "bachelor degree",
        "bachelor's degree",
    }

    doctorate_aliases = {
        "phd",
        "ph.d",
        "ph.d.",
        "doctoral",
        "doctorate",
        "doctoral degree",
        "doctorate degree",
    }

    if text in master_aliases:
        return "master"

    if text in bachelor_aliases:
        return "bachelor"

    if text in doctorate_aliases:
        return "doctorate"

    if "master" in text:
        return "master"

    if "bachelor" in text:
        return "bachelor"

    if (
        "phd" in text
        or "doctoral" in text
        or "doctorate" in text
    ):
        return "doctorate"

    return text


def calculate_text_similarity(
    user_major: str,
    program_text: str,
) -> float:
    """
    Calculate TF-IDF cosine similarity between two texts.

    The returned value is between 0 and 1.
    """

    user_text = normalise_text(user_major)
    opportunity_text = normalise_text(program_text)

    if not user_text or not opportunity_text:
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(
            [
                user_text,
                opportunity_text,
            ]
        )
    except ValueError:
        return 0.0

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2],
    )[0][0]

    return float(similarity)


# ---------------------------------------------------------
# Programme evaluation
# ---------------------------------------------------------

def evaluate_program(
    profile: dict[str, Any],
    program: dict[str, Any],
    university: dict[str, Any],
    country_name: str,
) -> dict[str, Any] | None:
    """
    Evaluate one programme against one user profile.

    Returns None when the programme fails a hard rule.
    """

    reasons: list[str] = []
    gaps: list[str] = []

    score_breakdown = {
        "degree_level": 0.0,
        "preferred_country": 0.0,
        "major_similarity": 0.0,
        "budget": 0.0,
        "preferred_intake": 0.0,
    }

    # -----------------------------------------------------
    # Hard rule 1: Degree-level eligibility
    # -----------------------------------------------------

    target_degree = normalise_degree_level(
        profile.get("target_degree_level")
    )

    program_degree = normalise_degree_level(
        program.get("degree_level")
    )

    if target_degree != program_degree:
        return None

    score_breakdown["degree_level"] = (
        DEGREE_LEVEL_WEIGHT
    )

    reasons.append(
        "Target degree level matches the programme."
    )

    # -----------------------------------------------------
    # Hard rule 2: Preferred country
    # -----------------------------------------------------

    preferred_countries = {
        normalise_text(country)
        for country in profile.get(
            "preferred_countries",
            [],
        )
    }

    normalised_country_name = normalise_text(
        country_name
    )

    if (
        preferred_countries
        and normalised_country_name
        not in preferred_countries
    ):
        return None

    score_breakdown["preferred_country"] = (
        COUNTRY_WEIGHT
    )

    reasons.append(
        f"Programme is located in preferred country: "
        f"{country_name}."
    )

    # -----------------------------------------------------
    # Content-based major similarity
    # -----------------------------------------------------

    user_major = profile.get(
        "preferred_major",
        "",
    )

    program_text = " ".join(
        [
            str(program.get("program_name") or ""),
            str(program.get("field_of_study") or ""),
        ]
    )

    major_similarity = calculate_text_similarity(
        user_major=user_major,
        program_text=program_text,
    )

    major_score = (
        major_similarity
        * MAJOR_SIMILARITY_WEIGHT
    )

    score_breakdown["major_similarity"] = round(
        major_score,
        2,
    )

    reasons.append(
        "Preferred-major text similarity is "
        f"{major_similarity * 100:.2f}%."
    )

    if major_similarity < 0.50:
        gaps.append(
            "The preferred major and programme field are "
            "not an exact match; academic-content review "
            "is recommended."
        )

    # -----------------------------------------------------
    # Budget matching
    # -----------------------------------------------------

    annual_budget = profile.get("annual_budget")
    budget_currency = profile.get("budget_currency")

    tuition_fee = program.get("tuition_fee")
    tuition_currency = program.get(
        "tuition_currency"
    )

    if annual_budget is None:
        gaps.append(
            "The user has no annual budget value."
        )

    elif tuition_fee is None:
        gaps.append(
            "The programme tuition fee is unavailable."
        )

    elif not budget_currency or not tuition_currency:
        gaps.append(
            "Budget or tuition currency is unavailable."
        )

    elif normalise_text(
        budget_currency
    ) != normalise_text(tuition_currency):
        gaps.append(
            "Budget and tuition currencies are different; "
            "currency conversion is not implemented yet."
        )

    elif tuition_fee <= annual_budget:
        score_breakdown["budget"] = BUDGET_WEIGHT

        reasons.append(
            f"Annual tuition {tuition_fee} "
            f"{tuition_currency} is within the user's "
            f"budget of {annual_budget} {budget_currency}."
        )

    else:
        gaps.append(
            f"Annual tuition exceeds the user's budget by "
            f"{tuition_fee - annual_budget} "
            f"{tuition_currency}."
        )

    # -----------------------------------------------------
    # Preferred-intake matching
    # -----------------------------------------------------

    preferred_intake = normalise_text(
        profile.get("preferred_intake")
    )

    available_intakes = [
        normalise_text(intake)
        for intake in program.get("intake") or []
    ]

    if not preferred_intake:
        gaps.append(
            "The user has no preferred intake."
        )

    elif not available_intakes:
        gaps.append(
            "The programme intake information is unavailable."
        )

    elif preferred_intake in available_intakes:
        score_breakdown["preferred_intake"] = (
            INTAKE_WEIGHT
        )

        reasons.append(
            f"Preferred intake "
            f"'{profile.get('preferred_intake')}' "
            "is available."
        )

    else:
        gaps.append(
            f"Preferred intake "
            f"'{profile.get('preferred_intake')}' "
            "is not listed for this programme."
        )

    # -----------------------------------------------------
    # Requirement-gap information
    # -----------------------------------------------------

    if program.get("minimum_gpa") is None:
        gaps.append(
            "Minimum GPA requirement is unavailable; "
            "GPA eligibility cannot be fully verified."
        )

    if (
        program.get("ielts_requirement") is None
        and program.get("toefl_requirement") is None
    ):
        gaps.append(
            "English-score requirement is unavailable; "
            "language eligibility requires manual checking."
        )

    if program.get("application_deadline") is None:
        gaps.append(
            "Application deadline is unavailable."
        )

    if profile.get("scholarship_required") is True:
        gaps.append(
            "The user requires a scholarship; scholarship "
            "matching will be evaluated separately."
        )

    total_score = round(
        sum(score_breakdown.values()),
        2,
    )

    return {
        "program_id": program.get("program_id"),
        "program_name": program.get("program_name"),
        "university_id": university.get(
            "university_id"
        ),
        "university_name": university.get(
            "university_name"
        ),
        "country_id": university.get("country_id"),
        "country_name": country_name,
        "degree_level": program.get("degree_level"),
        "field_of_study": program.get(
            "field_of_study"
        ),
        "language_of_instruction": program.get(
            "language_of_instruction"
        ),
        "tuition_fee": tuition_fee,
        "tuition_currency": tuition_currency,
        "intake": program.get("intake") or [],
        "program_url": program.get("program_url"),
        "known_eligibility_status": (
            "eligible_under_known_rules"
        ),
        "match_score": total_score,
        "maximum_score": MAXIMUM_SCORE,
        "major_similarity": round(
            major_similarity,
            4,
        ),
        "score_breakdown": score_breakdown,
        "match_reasons": reasons,
        "requirement_gaps": gaps,
    }


# ---------------------------------------------------------
# Recommendation process
# ---------------------------------------------------------

def generate_recommendations(
    database: Any,
    user_id: str,
    top_k: int,
) -> dict[str, Any]:
    """Generate ranked programme recommendations."""

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

    university_by_id = {
        university["university_id"]: university
        for university in database["universities"].find(
            {},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
                "country_id": 1,
                "official_website": 1,
            },
        )
    }

    programs = list(
        database["programs"].find(
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

    skipped_missing_relationship = 0
    rejected_by_hard_rules = 0

    for program in programs:
        university_id = program.get("university_id")

        university = university_by_id.get(
            university_id
        )

        if university is None:
            skipped_missing_relationship += 1
            continue

        country_name = country_name_by_id.get(
            university.get("country_id")
        )

        if country_name is None:
            skipped_missing_relationship += 1
            continue

        recommendation = evaluate_program(
            profile=profile,
            program=program,
            university=university,
            country_name=country_name,
        )

        if recommendation is None:
            rejected_by_hard_rules += 1
            continue

        recommendations.append(recommendation)

    recommendations.sort(
        key=lambda item: (
            item["match_score"],
            item["major_similarity"],
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
                "EduPath MVP Hybrid Programme "
                "Recommendation v1"
            ),
            "hard_filters": [
                "Target degree level",
                "Preferred country",
            ],
            "weighted_components": {
                "degree_level": DEGREE_LEVEL_WEIGHT,
                "preferred_country": COUNTRY_WEIGHT,
                "major_similarity": (
                    MAJOR_SIMILARITY_WEIGHT
                ),
                "budget": BUDGET_WEIGHT,
                "preferred_intake": INTAKE_WEIGHT,
            },
            "content_similarity_method": (
                "TF-IDF cosine similarity"
            ),
            "maximum_score": MAXIMUM_SCORE,
        },
        "user_profile_summary": {
            "target_degree_level": profile.get(
                "target_degree_level"
            ),
            "preferred_major": profile.get(
                "preferred_major"
            ),
            "annual_budget": profile.get(
                "annual_budget"
            ),
            "budget_currency": profile.get(
                "budget_currency"
            ),
            "preferred_countries": profile.get(
                "preferred_countries"
            ),
            "preferred_intake": profile.get(
                "preferred_intake"
            ),
            "scholarship_required": profile.get(
                "scholarship_required"
            ),
        },
        "total_program_candidates": len(programs),
        "eligible_candidates": len(recommendations),
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
    print("EduPath Programme Recommendation Engine")
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

        result = generate_recommendations(
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
            "Total programme candidates: "
            f"{result['total_program_candidates']}"
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
            print("No eligible programmes were found.")

        for rank, recommendation in enumerate(
            result["recommendations"],
            start=1,
        ):
            print(
                f"{rank}. "
                f"{recommendation['program_name']}"
            )

            print(
                "   University: "
                f"{recommendation['university_name']}"
            )

            print(
                "   Country: "
                f"{recommendation['country_name']}"
            )

            print(
                "   Match score: "
                f"{recommendation['match_score']}"
                f"/{recommendation['maximum_score']}"
            )

            known_eligibility = recommendation[
                "known_eligibility_status"
            ]

            print(
                f"   Known eligibility: {known_eligibility}"
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
            "Programme recommendation generation "
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