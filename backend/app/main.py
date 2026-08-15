from __future__ import annotations
from .analysis_routes import router as analysis_router
from .auth_routes import router as auth_router
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pymongo import ASCENDING
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)
from datetime import datetime, timezone

from backend.app.schemas import (
    AuthenticatedUserProfileCreate,
    UserProfileCreate,
    UserProfileUpdate,
)

from backend.app.auth_dependencies import (
    get_current_account,
)

from backend.app.database import (
    DATABASE_NAME,
    close_database,
    get_database,
    ping_database,
)

from scripts.recommend_programs import generate_recommendations
from scripts.recommend_scholarships import (
    generate_scholarship_recommendations,
)

from backend.app.schemas import (
    CountryListResponse,
    CountryResponse,
    HealthResponse,
    ProgramListResponse,
    ProgramResponse,
    RootResponse,
    ScholarshipListResponse,
    ScholarshipResponse,
    UniversityListResponse,
    UniversityResponse,
)

# ---------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Check MongoDB when the API starts and close it
    safely when the API stops.
    """

    try:
        ping_database()
        print("MongoDB Atlas connection: SUCCESS")
    except PyMongoError as error:
        close_database()

        raise RuntimeError(
            "FastAPI could not connect to MongoDB Atlas."
        ) from error

    yield

    close_database()
    print("MongoDB connection closed safely.")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="EduPath API",
    description=(
        "MVP backend API for university and scholarship "
        "recommendations."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(analysis_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        "http://localhost:5174",
        "http://127.0.0.1:5174",

        "http://localhost:5175",
        "http://127.0.0.1:5175",

        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get(
    "/",
    response_model=RootResponse,
    tags=["General"],
)
def read_root() -> dict[str, str]:
    """Return basic information about the API."""

    return {
        "message": "EduPath API is running.",
        "documentation": "/docs",
    }


# ---------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------

@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["General"],
)
def health_check() -> dict[str, str]:
    """Check whether FastAPI and MongoDB are available."""

    try:
        ping_database()
    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB Atlas is unavailable.",
        ) from error

    return {
        "status": "healthy",
        "database": DATABASE_NAME,
        "mongodb": "connected",
    }


# ---------------------------------------------------------
# List and filter universities
# ---------------------------------------------------------

@app.get(
    "/api/universities",
    response_model=UniversityListResponse,
    tags=["Universities"],
)
def list_universities(
    country_id: str | None = Query(
        default=None,
        description="Filter by country ID.",
        examples=["country_jp"],
    ),
    scholarship_available: bool | None = Query(
        default=None,
        description="Filter by scholarship availability.",
    ),
    degree_level: str | None = Query(
        default=None,
        description="Filter by degree level.",
        examples=["Master"],
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return.",
    ),
) -> dict[str, Any]:
    """Return university records using optional filters."""

    query: dict[str, Any] = {}

    if country_id is not None:
        query["country_id"] = country_id

    if scholarship_available is not None:
        query["scholarship_available"] = (
            scholarship_available
        )

    if degree_level is not None:
        query["degree_levels"] = degree_level

    database = get_database()
    collection = database["universities"]

    try:
        total = collection.count_documents(query)

        cursor = (
            collection
            .find(
                query,
                {
                    "_id": 0,
                    "database_updated_at": 0,
                },
            )
            .sort("university_name", ASCENDING)
            .skip(skip)
            .limit(limit)
        )

        universities = list(cursor)

    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve university records.",
        ) from error

    return {
        "total": total,
        "count": len(universities),
        "items": universities,
    }


# ---------------------------------------------------------
# Find one university
# ---------------------------------------------------------

@app.get(
    "/api/universities/{university_id}",
    response_model=UniversityResponse,
    tags=["Universities"],
)
def get_university(
    university_id: str,
) -> dict[str, Any]:
    """Return one university using its unique ID."""

    database = get_database()
    collection = database["universities"]

    try:
        university = collection.find_one(
            {"university_id": university_id},
            {
                "_id": 0,
                "database_updated_at": 0,
            },
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve the university.",
        ) from error

    if university is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found.",
        )

    return university

# ---------------------------------------------------------
# List and filter programmes
# ---------------------------------------------------------

@app.get(
    "/api/programs",
    response_model=ProgramListResponse,
    tags=["Programs"],
)
def list_programs(
    university_id: str | None = Query(
        default=None,
        description="Filter programmes by university ID.",
        examples=["uni_jp_001"],
    ),
    degree_level: str | None = Query(
        default=None,
        description="Filter programmes by degree level.",
        examples=["Master"],
    ),
    field_of_study: str | None = Query(
        default=None,
        description="Filter programmes by field of study.",
        examples=["Information Science and Technology"],
    ),
    language: str | None = Query(
        default=None,
        description="Filter by language of instruction.",
        examples=["English"],
    ),
    intake: str | None = Query(
        default=None,
        description="Filter by available intake.",
        examples=["October"],
    ),
    max_tuition_fee: float | None = Query(
        default=None,
        ge=0,
        description=(
            "Return programmes whose tuition fee is less "
            "than or equal to this value."
        ),
        examples=[600000],
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return.",
    ),
) -> dict[str, Any]:
    """Return academic programmes using optional filters."""

    query: dict[str, Any] = {}

    if university_id is not None:
        query["university_id"] = university_id

    if degree_level is not None:
        query["degree_level"] = degree_level

    if field_of_study is not None:
        query["field_of_study"] = field_of_study

    if language is not None:
        query["language_of_instruction"] = language

    if intake is not None:
        query["intake"] = intake

    if max_tuition_fee is not None:
        query["tuition_fee"] = {
            "$ne": None,
            "$lte": max_tuition_fee,
        }

    database = get_database()
    collection = database["programs"]

    try:
        total = collection.count_documents(query)

        cursor = (
            collection
            .find(
                query,
                {
                    "_id": 0,
                    "content_hash": 0,
                    "created_at": 0,
                    "database_updated_at": 0,
                },
            )
            .sort("program_name", ASCENDING)
            .skip(skip)
            .limit(limit)
        )

        programs = list(cursor)

    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve programme records.",
        ) from error

    return {
        "total": total,
        "count": len(programs),
        "items": programs,
    }


# ---------------------------------------------------------
# Find one programme
# ---------------------------------------------------------

@app.get(
    "/api/programs/{program_id}",
    response_model=ProgramResponse,
    tags=["Programs"],
)
def get_program(
    program_id: str,
) -> dict[str, Any]:
    """Return one academic programme using its unique ID."""

    database = get_database()
    collection = database["programs"]

    try:
        program = collection.find_one(
            {"program_id": program_id},
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve the programme.",
        ) from error

    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programme not found.",
        )

    return program

# ---------------------------------------------------------
# List and filter countries
# ---------------------------------------------------------

@app.get(
    "/api/countries",
    response_model=CountryListResponse,
    tags=["Countries"],
)
def list_countries(
    region: str | None = Query(
        default=None,
        description="Filter countries by region.",
        examples=["Southeast Asia"],
    ),
    currency_code: str | None = Query(
        default=None,
        min_length=3,
        max_length=3,
        description="Filter countries by currency code.",
        examples=["SGD"],
    ),
    language: str | None = Query(
        default=None,
        description="Filter by a main language.",
        examples=["English"],
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of country records to skip.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of countries to return.",
    ),
) -> dict[str, Any]:
    """Return country records using optional filters."""

    query: dict[str, Any] = {}

    if region is not None:
        query["region"] = region

    if currency_code is not None:
        query["currency_code"] = currency_code.upper()

    if language is not None:
        query["main_language"] = language

    database = get_database()
    collection = database["countries"]

    try:
        total = collection.count_documents(query)

        cursor = (
            collection
            .find(
                query,
                {
                    "_id": 0,
                    "content_hash": 0,
                    "created_at": 0,
                    "database_updated_at": 0,
                },
            )
            .sort("country_name", ASCENDING)
            .skip(skip)
            .limit(limit)
        )

        countries = list(cursor)

    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve country records.",
        ) from error

    return {
        "total": total,
        "count": len(countries),
        "items": countries,
    }


# ---------------------------------------------------------
# Find one country
# ---------------------------------------------------------

@app.get(
    "/api/countries/{country_id}",
    response_model=CountryResponse,
    tags=["Countries"],
)
def get_country(
    country_id: str,
) -> dict[str, Any]:
    """Return one country using its unique ID."""

    database = get_database()
    collection = database["countries"]

    try:
        country = collection.find_one(
            {"country_id": country_id},
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve the country.",
        ) from error

    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found.",
        )

    return country

# ---------------------------------------------------------
# List and filter scholarships
# ---------------------------------------------------------

@app.get(
    "/api/scholarships",
    response_model=ScholarshipListResponse,
    tags=["Scholarships"],
)
def list_scholarships(
    country_id: str | None = Query(
        default=None,
        description="Filter scholarships by country ID.",
        examples=["country_jp"],
    ),
    host_university_id: str | None = Query(
        default=None,
        description=(
            "Filter scholarships by host university ID."
        ),
        examples=["uni_jp_001"],
    ),
    degree_level: str | None = Query(
        default=None,
        description="Filter by an eligible degree level.",
        examples=["Master"],
    ),
    field_of_study: str | None = Query(
        default=None,
        description="Filter by an eligible field of study.",
        examples=["Computer Science"],
    ),
    funding_type: str | None = Query(
        default=None,
        description="Filter by scholarship funding type.",
        examples=["Fully Funded"],
    ),
    scholarship_status: str | None = Query(
        default=None,
        description="Filter by scholarship status.",
        examples=["upcoming"],
    ),
    application_cycle: str | None = Query(
        default=None,
        description="Filter by application cycle.",
        examples=["2027"],
    ),
    min_monthly_allowance: float | None = Query(
        default=None,
        ge=0,
        description=(
            "Return scholarships whose monthly allowance "
            "is greater than or equal to this value."
        ),
        examples=[100000],
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of scholarship records to skip.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description=(
            "Maximum number of scholarship records "
            "to return."
        ),
    ),
) -> dict[str, Any]:
    """Return scholarships using optional search filters."""

    query: dict[str, Any] = {}

    if country_id is not None:
        query["country_id"] = country_id

    if host_university_id is not None:
        query["host_university_id"] = host_university_id

    if degree_level is not None:
        query["degree_levels"] = degree_level

    if field_of_study is not None:
        query["fields_of_study"] = field_of_study

    if funding_type is not None:
        query["funding_type"] = funding_type

    if scholarship_status is not None:
        query["scholarship_status"] = (
            scholarship_status.lower()
        )

    if application_cycle is not None:
        query["application_cycle"] = application_cycle

    if min_monthly_allowance is not None:
        query["monthly_allowance"] = {
            "$ne": None,
            "$gte": min_monthly_allowance,
        }

    database = get_database()
    collection = database["scholarships"]

    try:
        cursor = (
            collection
            .find(
                query,
                {
                    "_id": 0,
                    "content_hash": 0,
                    "database_updated_at": 0,
                },
            )
            .sort(
                [
                    ("application_deadline", ASCENDING),
                    ("scholarship_name", ASCENDING),
                ]
            )
        )

        raw_scholarships = list(cursor)

        valid_scholarships: list[dict[str, Any]] = []

        for scholarship in raw_scholarships:
            try:
                validated = ScholarshipResponse.model_validate(
                    scholarship
                )

                valid_scholarships.append(
                    validated.model_dump()
                )

            except Exception:
                # Research-blocked or schema-invalid scholarship records
                # remain stored in MongoDB but are not exposed through the
                # normal public candidate pool.
                continue

        total = len(valid_scholarships)

        scholarships = valid_scholarships[
            skip : skip + limit
        ]

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to retrieve scholarship records."
            ),
        ) from error

    return {
        "total": total,
        "count": len(scholarships),
        "items": scholarships,
    }


# ---------------------------------------------------------
# Find one scholarship
# ---------------------------------------------------------

@app.get(
    "/api/scholarships/{scholarship_id}",
    response_model=ScholarshipResponse,
    tags=["Scholarships"],
)
def get_scholarship(
    scholarship_id: str,
) -> dict[str, Any]:
    """Return one scholarship using its unique ID."""

    database = get_database()
    collection = database["scholarships"]

    try:
        scholarship = collection.find_one(
            {"scholarship_id": scholarship_id},
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to retrieve the scholarship.",
        ) from error

    if scholarship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scholarship not found.",
        )

    try:
        ScholarshipResponse.model_validate(
            scholarship
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Scholarship record is currently unavailable "
                "because its verification is incomplete."
            ),
        )
    return scholarship

# ---------------------------------------------------------
# Programme recommendations
# ---------------------------------------------------------

@app.get(
    "/api/recommendations/programs/{user_id}",
    tags=["Recommendations"],
)
def get_program_recommendations(
    user_id: str,
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
        description=(
            "Maximum number of programme recommendations "
            "to return."
        ),
    ),
) -> dict[str, Any]:
    """
    Generate ranked programme recommendations for one user.

    The recommendation engine applies:
    - hard eligibility filtering,
    - weighted scoring,
    - TF-IDF cosine similarity,
    - match reasons,
    - requirement gaps.
    """

    database = get_database()

    try:
        recommendation_result = generate_recommendations(
            database=database,
            user_id=user_id,
            top_k=top_k,
        )

        recommendations = recommendation_result.get(
            "recommendations",
            [],
        )

        recommended_program_ids = [
            recommendation["program_id"]
            for recommendation in recommendations
            if (
                isinstance(recommendation, dict)
                and isinstance(
                    recommendation.get("program_id"),
                    str,
                )
            )
        ]

        append_recommendation_history(
            user_id=user_id,
            recommendation_type="program",
            recommended_ids=recommended_program_ids,
        )

        return recommendation_result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to generate programme "
                "recommendations."
            ),
        ) from error

# ---------------------------------------------------------
# Scholarship recommendations
# ---------------------------------------------------------

@app.get(
    "/api/recommendations/scholarships/{user_id}",
    tags=["Recommendations"],
)
def get_scholarship_recommendations(
    user_id: str,
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
        description=(
            "Maximum number of scholarship recommendations "
            "to return."
        ),
    ),
) -> dict[str, Any]:
    """
    Generate ranked scholarship recommendations for one user.

    The recommendation engine applies:
    - hard eligibility filtering,
    - weighted scoring,
    - TF-IDF cosine similarity,
    - match reasons,
    - requirement gaps.
    """

    database = get_database()

    try:
        recommendation_result = (
            generate_scholarship_recommendations(
                database=database,
                user_id=user_id,
                top_k=top_k,
            )
        )

        recommendations = recommendation_result.get(
            "recommendations",
            [],
        )

        recommended_scholarship_ids = [
            recommendation["scholarship_id"]
            for recommendation in recommendations
            if (
                isinstance(recommendation, dict)
                and isinstance(
                    recommendation.get("scholarship_id"),
                    str,
                )
            )
        ]

        append_recommendation_history(
            user_id=user_id,
            recommendation_type="scholarship",
            recommended_ids=recommended_scholarship_ids,
        )

        return recommendation_result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to generate scholarship "
                "recommendations."
            ),
        ) from error

# ---------------------------------------------------------
# User profiles
# ---------------------------------------------------------

@app.get(
    "/api/user-profiles",
    tags=["User Profiles"],
)
def list_user_profiles(
    nationality: str | None = Query(
        default=None,
        description="Filter profiles by nationality.",
    ),
    target_degree_level: str | None = Query(
        default=None,
        description="Filter by target degree level.",
    ),
    preferred_country: str | None = Query(
        default=None,
        description="Filter by preferred country.",
    ),
    scholarship_required: bool | None = Query(
        default=None,
        description="Filter by scholarship requirement.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
) -> dict[str, Any]:
    """Return user profiles with optional filters."""

    database = get_database()

    query: dict[str, Any] = {}

    if nationality:
        query["nationality"] = nationality

    if target_degree_level:
        query["target_degree_level"] = (
            target_degree_level
        )

    if preferred_country:
        query["preferred_countries"] = preferred_country

    if scholarship_required is not None:
        query["scholarship_required"] = (
            scholarship_required
        )

    try:
        profiles = list(
            database["user_profiles"]
            .find(
                query,
                {
                    "_id": 0,
                    "content_hash": 0,
                    "created_at": 0,
                    "database_updated_at": 0,
                },
            )
            .limit(limit)
        )

        return {
            "returned_profiles": len(profiles),
            "profiles": profiles,
        }

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to retrieve user profiles.",
        ) from error


@app.get(
    "/api/user-profiles/{user_id}",
    tags=["User Profiles"],
)
def get_user_profile(
    user_id: str,
) -> dict[str, Any]:
    """Return one user profile by user ID."""

    database = get_database()

    try:
        profile = database["user_profiles"].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to retrieve the user profile.",
        ) from error

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"User profile '{user_id}' was not found."
            ),
        )

    return profile

# ---------------------------------------------------------
# Create user profile
# ---------------------------------------------------------

@app.post(
    "/api/user-profiles",
    status_code=status.HTTP_201_CREATED,
    tags=["User Profiles"],
)
def create_user_profile(
    payload: UserProfileCreate,
) -> dict[str, Any]:
    """Create a new user profile in MongoDB."""

    database = get_database()

    profile = payload.model_dump()

    # -----------------------------------------------------
    # Clean required text fields
    # -----------------------------------------------------

    required_text_fields = [
        "user_id",
        "nationality",
        "current_education_level",
        "target_degree_level",
        "preferred_major",
    ]

    for field_name in required_text_fields:
        cleaned_value = str(
            profile[field_name]
        ).strip()

        if not cleaned_value:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    f"Field '{field_name}' "
                    "cannot be blank."
                ),
            )

        profile[field_name] = cleaned_value

    # -----------------------------------------------------
    # Clean optional text fields
    # -----------------------------------------------------

    optional_text_fields = [
        "preferred_funding_type",
        "preferred_intake",
    ]

    for field_name in optional_text_fields:
        value = profile.get(field_name)

        if value is not None:
            cleaned_value = str(value).strip()

            profile[field_name] = (
                cleaned_value
                if cleaned_value
                else None
            )

    # -----------------------------------------------------
    # GPA validation
    # -----------------------------------------------------

    gpa = profile.get("gpa")
    gpa_scale = profile.get("gpa_scale")

    if gpa is not None and gpa_scale is None:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'gpa_scale' is required "
                "when GPA is provided."
            ),
        )

    if gpa is None and gpa_scale is not None:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'gpa' is required "
                "when GPA scale is provided."
            ),
        )

    if (
        gpa is not None
        and gpa_scale is not None
        and gpa > gpa_scale
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "GPA cannot be greater than GPA scale."
            ),
        )

    # -----------------------------------------------------
    # Budget validation
    # -----------------------------------------------------

    annual_budget = profile.get("annual_budget")
    budget_currency = profile.get(
        "budget_currency"
    )

    if (
        annual_budget is not None
        and budget_currency is None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'budget_currency' is required "
                "when annual budget is provided."
            ),
        )

    if (
        annual_budget is None
        and budget_currency is not None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'annual_budget' is required "
                "when budget currency is provided."
            ),
        )

    if budget_currency is not None:
        profile["budget_currency"] = (
            budget_currency.strip().upper()
        )

    # -----------------------------------------------------
    # Scholarship preference validation
    # -----------------------------------------------------

    if (
        profile["scholarship_required"] is True
        and profile.get("preferred_funding_type")
        is None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'preferred_funding_type' "
                "is required when scholarship_required "
                "is true."
            ),
        )

    # -----------------------------------------------------
    # Preferred-country cleaning
    # -----------------------------------------------------

    cleaned_preferred_countries = [
        country.strip()
        for country in profile[
            "preferred_countries"
        ]
        if country.strip()
    ]

    cleaned_preferred_countries = list(
        dict.fromkeys(cleaned_preferred_countries)
    )

    if not cleaned_preferred_countries:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "At least one preferred country "
                "is required."
            ),
        )

    profile["preferred_countries"] = (
        cleaned_preferred_countries
    )

    try:
        # -------------------------------------------------
        # Validate preferred countries against MongoDB
        # -------------------------------------------------

        country_documents = database[
            "countries"
        ].find(
            {
                "country_name": {
                    "$in": cleaned_preferred_countries
                }
            },
            {
                "_id": 0,
                "country_name": 1,
            },
        )

        existing_country_names = {
            country["country_name"]
            for country in country_documents
        }

        missing_country_names = sorted(
            set(cleaned_preferred_countries)
            - existing_country_names
        )

        if missing_country_names:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "The following preferred countries "
                    "do not exist: "
                    + ", ".join(missing_country_names)
                ),
            )

        # -------------------------------------------------
        # Prepare runtime fields
        # -------------------------------------------------

        current_time = datetime.now(timezone.utc)

        profile["saved_universities"] = []
        profile["saved_scholarships"] = []
        profile["recommendation_history"] = []
        profile["created_at"] = current_time
        profile["database_updated_at"] = (
            current_time
        )

        database["user_profiles"].insert_one(
            profile
        )

    except DuplicateKeyError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"User profile '{profile['user_id']}' "
                "already exists."
            ),
        ) from error

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to create the user profile.",
        ) from error

    # Do not expose internal database fields.
    public_profile = {
        key: value
        for key, value in profile.items()
        if key
        not in {
            "_id",
            "content_hash",
            "created_at",
            "database_updated_at",
        }
    }

    return {
        "message": (
            "User profile created successfully."
        ),
        "profile": public_profile,
    }


# ---------------------------------------------------------
# Create profile for current authenticated student
# ---------------------------------------------------------

@app.post(
    "/api/me/profile",
    status_code=status.HTTP_201_CREATED,
    tags=["My Profile"],
)
def create_current_user_profile(
    payload: AuthenticatedUserProfileCreate,
    current_account: dict[str, Any] = Depends(
        get_current_account
    ),
) -> dict[str, Any]:
    """
    Create the academic profile belonging to the
    currently authenticated student.
    """

    database = get_database()

    user_id = current_account["user_id"]

    # -----------------------------------------------------
    # Prevent multiple academic profiles for one account
    # -----------------------------------------------------

    try:
        existing_profile = database[
            "user_profiles"
        ].find_one(
            {"user_id": user_id},
            {
                "_id": 1,
            },
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to check the academic profile."
            ),
        ) from error

    if existing_profile is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An academic profile already exists "
                "for this account."
            ),
        )

    # -----------------------------------------------------
    # Inject trusted user_id from the JWT account
    # -----------------------------------------------------

    profile_payload = UserProfileCreate(
        user_id=user_id,
        **payload.model_dump(),
    )

    # -----------------------------------------------------
    # Reuse the existing validated profile-creation logic
    # -----------------------------------------------------

    result = create_user_profile(
        profile_payload
    )

    # -----------------------------------------------------
    # Mark the linked account as profile-complete
    # -----------------------------------------------------

    try:
        update_result = database["accounts"].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "profile_completed": True,
                    "database_updated_at": (
                        datetime.now(timezone.utc)
                    ),
                }
            },
        )

        if update_result.matched_count != 1:
            # Extremely defensive rollback.
            database["user_profiles"].delete_one(
                {"user_id": user_id}
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Unable to link the academic "
                    "profile to the account."
                ),
            )

    except HTTPException:
        raise

    except PyMongoError as error:
        # Keep account/profile state consistent when
        # the account update fails.
        try:
            database["user_profiles"].delete_one(
                {"user_id": user_id}
            )
        except PyMongoError:
            pass

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to complete academic "
                "profile setup."
            ),
        ) from error

    return {
        "message": (
            "Academic profile created successfully."
        ),
        "profile_completed": True,
        "profile": result["profile"],
    }


# ---------------------------------------------------------
# Update user profile
# ---------------------------------------------------------

@app.patch(
    "/api/user-profiles/{user_id}",
    tags=["User Profiles"],
)
def update_user_profile(
    user_id: str,
    payload: UserProfileUpdate,
) -> dict[str, Any]:
    """Update selected fields of an existing user profile."""

    database = get_database()

    updates = payload.model_dump(
        exclude_unset=True,
    )

    if not updates:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "At least one profile field "
                "must be provided."
            ),
        )

    try:
        existing_profile = database[
            "user_profiles"
        ].find_one(
            {"user_id": user_id}
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to retrieve the user profile."
            ),
        ) from error

    if existing_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"User profile '{user_id}' "
                "was not found."
            ),
        )

    # -----------------------------------------------------
    # Clean required text fields
    # -----------------------------------------------------

    required_text_fields = [
        "nationality",
        "current_education_level",
        "target_degree_level",
        "preferred_major",
    ]

    for field_name in required_text_fields:
        if field_name not in updates:
            continue

        value = updates[field_name]

        if value is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    f"Field '{field_name}' "
                    "cannot be null."
                ),
            )

        cleaned_value = str(value).strip()

        if not cleaned_value:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    f"Field '{field_name}' "
                    "cannot be blank."
                ),
            )

        updates[field_name] = cleaned_value

    # -----------------------------------------------------
    # Clean optional text fields
    # -----------------------------------------------------

    optional_text_fields = [
        "preferred_funding_type",
        "preferred_intake",
    ]

    for field_name in optional_text_fields:
        if field_name not in updates:
            continue

        value = updates[field_name]

        if value is not None:
            cleaned_value = str(value).strip()

            updates[field_name] = (
                cleaned_value
                if cleaned_value
                else None
            )

    # -----------------------------------------------------
    # Clean budget currency
    # -----------------------------------------------------

    if (
        "budget_currency" in updates
        and updates["budget_currency"] is not None
    ):
        updates["budget_currency"] = str(
            updates["budget_currency"]
        ).strip().upper()

    # -----------------------------------------------------
    # Clean preferred countries
    # -----------------------------------------------------

    if "preferred_countries" in updates:
        preferred_countries = updates[
            "preferred_countries"
        ]

        if preferred_countries is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "Field 'preferred_countries' "
                    "cannot be null."
                ),
            )

        cleaned_countries = [
            country.strip()
            for country in preferred_countries
            if country.strip()
        ]

        cleaned_countries = list(
            dict.fromkeys(cleaned_countries)
        )

        if not cleaned_countries:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "At least one preferred country "
                    "is required."
                ),
            )

        updates["preferred_countries"] = (
            cleaned_countries
        )

    # -----------------------------------------------------
    # Merge existing data with incoming changes
    # -----------------------------------------------------

    merged_profile = {
        **existing_profile,
        **updates,
    }

    # -----------------------------------------------------
    # GPA validation
    # -----------------------------------------------------

    gpa = merged_profile.get("gpa")
    gpa_scale = merged_profile.get("gpa_scale")

    if gpa is not None and gpa_scale is None:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'gpa_scale' is required "
                "when GPA is provided."
            ),
        )

    if gpa is None and gpa_scale is not None:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'gpa' is required "
                "when GPA scale is provided."
            ),
        )

    if (
        gpa is not None
        and gpa_scale is not None
        and gpa > gpa_scale
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "GPA cannot be greater than GPA scale."
            ),
        )

    # -----------------------------------------------------
    # Budget validation
    # -----------------------------------------------------

    annual_budget = merged_profile.get(
        "annual_budget"
    )

    budget_currency = merged_profile.get(
        "budget_currency"
    )

    if (
        annual_budget is not None
        and budget_currency is None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'budget_currency' is required "
                "when annual budget is provided."
            ),
        )

    if (
        annual_budget is None
        and budget_currency is not None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'annual_budget' is required "
                "when budget currency is provided."
            ),
        )

    # -----------------------------------------------------
    # Scholarship preference validation
    # -----------------------------------------------------

    if (
        merged_profile.get("scholarship_required")
        is True
        and not merged_profile.get(
            "preferred_funding_type"
        )
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Field 'preferred_funding_type' "
                "is required when scholarship_required "
                "is true."
            ),
        )

    try:
        # -------------------------------------------------
        # Country relationship validation
        # -------------------------------------------------

        if "preferred_countries" in updates:
            country_documents = database[
                "countries"
            ].find(
                {
                    "country_name": {
                        "$in": updates[
                            "preferred_countries"
                        ]
                    }
                },
                {
                    "_id": 0,
                    "country_name": 1,
                },
            )

            existing_country_names = {
                country["country_name"]
                for country in country_documents
            }

            missing_country_names = sorted(
                set(
                    updates["preferred_countries"]
                )
                - existing_country_names
            )

            if missing_country_names:
                raise HTTPException(
                    status_code=(
                        status.HTTP_422_UNPROCESSABLE_ENTITY
                    ),
                    detail=(
                        "The following preferred countries "
                        "do not exist: "
                        + ", ".join(
                            missing_country_names
                        )
                    ),
                )

        updates["database_updated_at"] = (
            datetime.now(timezone.utc)
        )

        database["user_profiles"].update_one(
            {"user_id": user_id},
            {
                "$set": updates,
            },
        )

        updated_profile = database[
            "user_profiles"
        ].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "content_hash": 0,
                "created_at": 0,
                "database_updated_at": 0,
            },
        )

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to update the user profile."
            ),
        ) from error

    if updated_profile is None:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The updated user profile "
                "could not be retrieved."
            ),
        )

    return {
        "message": (
            "User profile updated successfully."
        ),
        "profile": updated_profile,
    }

# ---------------------------------------------------------
# Save university
# ---------------------------------------------------------

@app.post(
    (
        "/api/user-profiles/{user_id}"
        "/saved-universities/{university_id}"
    ),
    tags=["Saved Opportunities"],
)
def save_university_for_user(
    user_id: str,
    university_id: str,
) -> dict[str, Any]:
    """Save one university to a user's profile."""

    database = get_database()

    try:
        # -------------------------------------------------
        # Check whether the user profile exists
        # -------------------------------------------------

        profile = database["user_profiles"].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "user_id": 1,
                "saved_universities": 1,
            },
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User profile '{user_id}' "
                    "was not found."
                ),
            )

        # -------------------------------------------------
        # Check whether the university exists
        # -------------------------------------------------

        university = database["universities"].find_one(
            {"university_id": university_id},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
                "country_id": 1,
                "city": 1,
                "university_type": 1,
            },
        )

        if university is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"University '{university_id}' "
                    "was not found."
                ),
            )

        existing_saved_universities = (
            profile.get("saved_universities") or []
        )

        # -------------------------------------------------
        # Return safely when it is already saved
        # -------------------------------------------------

        if university_id in existing_saved_universities:
            return {
                "message": (
                    "University is already saved."
                ),
                "university": university,
                "saved_universities": (
                    existing_saved_universities
                ),
            }

        # -------------------------------------------------
        # Save without creating duplicates
        # -------------------------------------------------

        database["user_profiles"].update_one(
            {"user_id": user_id},
            {
                "$addToSet": {
                    "saved_universities": university_id,
                },
                "$set": {
                    "database_updated_at": (
                        datetime.now(timezone.utc)
                    ),
                },
            },
        )

        updated_profile = database[
            "user_profiles"
        ].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "saved_universities": 1,
            },
        )

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to save the university.",
        ) from error

    if updated_profile is None:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The updated user profile "
                "could not be retrieved."
            ),
        )

    return {
        "message": (
            "University saved successfully."
        ),
        "university": university,
        "saved_universities": (
            updated_profile.get(
                "saved_universities",
                [],
            )
        ),
    }

# ---------------------------------------------------------
# Unsave university
# ---------------------------------------------------------

@app.delete(
    (
        "/api/user-profiles/{user_id}"
        "/saved-universities/{university_id}"
    ),
    tags=["Saved Opportunities"],
)
def unsave_university_for_user(
    user_id: str,
    university_id: str,
) -> dict[str, Any]:
    """Remove one university from a user's saved list."""

    database = get_database()

    try:
        # -------------------------------------------------
        # Check whether the user profile exists
        # -------------------------------------------------

        profile = database["user_profiles"].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "user_id": 1,
                "saved_universities": 1,
            },
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User profile '{user_id}' "
                    "was not found."
                ),
            )

        # -------------------------------------------------
        # Check whether the university exists
        # -------------------------------------------------

        university = database["universities"].find_one(
            {"university_id": university_id},
            {
                "_id": 0,
                "university_id": 1,
                "university_name": 1,
                "country_id": 1,
                "city": 1,
                "university_type": 1,
            },
        )

        if university is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"University '{university_id}' "
                    "was not found."
                ),
            )

        existing_saved_universities = (
            profile.get("saved_universities") or []
        )

        # -------------------------------------------------
        # Return safely when it is not currently saved
        # -------------------------------------------------

        if university_id not in existing_saved_universities:
            return {
                "message": (
                    "University is not currently saved."
                ),
                "university": university,
                "saved_universities": (
                    existing_saved_universities
                ),
            }

        # -------------------------------------------------
        # Remove the university ID from the array
        # -------------------------------------------------

        database["user_profiles"].update_one(
            {"user_id": user_id},
            {
                "$pull": {
                    "saved_universities": university_id,
                },
                "$set": {
                    "database_updated_at": (
                        datetime.now(timezone.utc)
                    ),
                },
            },
        )

        updated_profile = database[
            "user_profiles"
        ].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "saved_universities": 1,
            },
        )

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to remove the saved university."
            ),
        ) from error

    if updated_profile is None:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The updated user profile "
                "could not be retrieved."
            ),
        )

    return {
        "message": (
            "University removed from saved list "
            "successfully."
        ),
        "university": university,
        "saved_universities": (
            updated_profile.get(
                "saved_universities",
                [],
            )
        ),
    }

# ---------------------------------------------------------
# Save scholarship
# ---------------------------------------------------------

@app.post(
    (
        "/api/user-profiles/{user_id}"
        "/saved-scholarships/{scholarship_id}"
    ),
    tags=["Saved Opportunities"],
)
def save_scholarship_for_user(
    user_id: str,
    scholarship_id: str,
) -> dict[str, Any]:
    """Save one scholarship to a user's profile."""

    database = get_database()

    try:
        # -------------------------------------------------
        # Check whether the user profile exists
        # -------------------------------------------------

        profile = database["user_profiles"].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "user_id": 1,
                "saved_scholarships": 1,
            },
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User profile '{user_id}' "
                    "was not found."
                ),
            )

        # -------------------------------------------------
        # Check whether the scholarship exists
        # -------------------------------------------------

        scholarship = database["scholarships"].find_one(
            {"scholarship_id": scholarship_id},
            {
                "_id": 0,
                "scholarship_id": 1,
                "scholarship_name": 1,
                "provider_name": 1,
                "provider_type": 1,
                "country_id": 1,
                "university_id": 1,
                "degree_levels": 1,
                "funding_type": 1,
                "application_status": 1,
                "application_deadline": 1,
            },
        )

        if scholarship is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Scholarship '{scholarship_id}' "
                    "was not found."
                ),
            )

        existing_saved_scholarships = (
            profile.get("saved_scholarships") or []
        )

        # -------------------------------------------------
        # Prevent duplicate scholarship IDs
        # -------------------------------------------------

        if scholarship_id in existing_saved_scholarships:
            return {
                "message": "Scholarship is already saved.",
                "scholarship": scholarship,
                "saved_scholarships": (
                    existing_saved_scholarships
                ),
            }

        # -------------------------------------------------
        # Add the scholarship ID to the saved list
        # -------------------------------------------------

        database["user_profiles"].update_one(
            {"user_id": user_id},
            {
                "$addToSet": {
                    "saved_scholarships": scholarship_id,
                },
                "$set": {
                    "database_updated_at": (
                        datetime.now(timezone.utc)
                    ),
                },
            },
        )

        updated_profile = database[
            "user_profiles"
        ].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "saved_scholarships": 1,
            },
        )

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to save the scholarship.",
        ) from error

    if updated_profile is None:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The updated user profile "
                "could not be retrieved."
            ),
        )

    return {
        "message": "Scholarship saved successfully.",
        "scholarship": scholarship,
        "saved_scholarships": (
            updated_profile.get(
                "saved_scholarships",
                [],
            )
        ),
    }

# ---------------------------------------------------------
# Unsave scholarship
# ---------------------------------------------------------

@app.delete(
    (
        "/api/user-profiles/{user_id}"
        "/saved-scholarships/{scholarship_id}"
    ),
    tags=["Saved Opportunities"],
)
def unsave_scholarship_for_user(
    user_id: str,
    scholarship_id: str,
) -> dict[str, Any]:
    """Remove one scholarship from a user's saved list."""

    database = get_database()

    try:
        # -------------------------------------------------
        # Check whether the user profile exists
        # -------------------------------------------------

        profile = database["user_profiles"].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "user_id": 1,
                "saved_scholarships": 1,
            },
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User profile '{user_id}' "
                    "was not found."
                ),
            )

        # -------------------------------------------------
        # Check whether the scholarship exists
        # -------------------------------------------------

        scholarship = database["scholarships"].find_one(
            {"scholarship_id": scholarship_id},
            {
                "_id": 0,
                "scholarship_id": 1,
                "scholarship_name": 1,
                "provider_name": 1,
                "provider_type": 1,
                "country_id": 1,
                "university_id": 1,
                "degree_levels": 1,
                "funding_type": 1,
                "application_status": 1,
                "application_deadline": 1,
            },
        )

        if scholarship is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Scholarship '{scholarship_id}' "
                    "was not found."
                ),
            )

        existing_saved_scholarships = (
            profile.get("saved_scholarships") or []
        )

        # -------------------------------------------------
        # Return safely when it is not currently saved
        # -------------------------------------------------

        if scholarship_id not in existing_saved_scholarships:
            return {
                "message": (
                    "Scholarship is not currently saved."
                ),
                "scholarship": scholarship,
                "saved_scholarships": (
                    existing_saved_scholarships
                ),
            }

        # -------------------------------------------------
        # Remove the scholarship ID from the saved list
        # -------------------------------------------------

        database["user_profiles"].update_one(
            {"user_id": user_id},
            {
                "$pull": {
                    "saved_scholarships": scholarship_id,
                },
                "$set": {
                    "database_updated_at": (
                        datetime.now(timezone.utc)
                    ),
                },
            },
        )

        updated_profile = database[
            "user_profiles"
        ].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "saved_scholarships": 1,
            },
        )

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to remove the saved scholarship."
            ),
        ) from error

    if updated_profile is None:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The updated user profile "
                "could not be retrieved."
            ),
        )

    return {
        "message": (
            "Scholarship removed from saved list "
            "successfully."
        ),
        "scholarship": scholarship,
        "saved_scholarships": (
            updated_profile.get(
                "saved_scholarships",
                [],
            )
        ),
    }

# ---------------------------------------------------------
# Get saved opportunities
# ---------------------------------------------------------

@app.get(
    (
        "/api/user-profiles/{user_id}"
        "/saved-opportunities"
    ),
    tags=["Saved Opportunities"],
)
def get_saved_opportunities(
    user_id: str,
) -> dict[str, Any]:
    """
    Return the university and scholarship details saved
    by one user.
    """

    database = get_database()

    try:
        # -------------------------------------------------
        # Find the user profile
        # -------------------------------------------------

        profile = database["user_profiles"].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "user_id": 1,
                "saved_universities": 1,
                "saved_scholarships": 1,
            },
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User profile '{user_id}' "
                    "was not found."
                ),
            )

        saved_university_ids = (
            profile.get("saved_universities") or []
        )

        saved_scholarship_ids = (
            profile.get("saved_scholarships") or []
        )

        # -------------------------------------------------
        # Retrieve saved university documents
        # -------------------------------------------------

        university_documents = list(
            database["universities"].find(
                {
                    "university_id": {
                        "$in": saved_university_ids
                    }
                },
                {
                    "_id": 0,
                    "university_id": 1,
                    "university_name": 1,
                    "country_id": 1,
                    "city": 1,
                    "university_type": 1,
                    "establishment_year": 1,
                    "degree_levels": 1,
                    "scholarship_available": 1,
                },
            )
        )

        university_by_id = {
            university["university_id"]: university
            for university in university_documents
        }

        saved_universities = [
            university_by_id[university_id]
            for university_id in saved_university_ids
            if university_id in university_by_id
        ]
    

        # -------------------------------------------------
        # Retrieve saved scholarship documents
        # -------------------------------------------------

        scholarship_documents = list(
            database["scholarships"].find(
                {
                    "scholarship_id": {
                        "$in": saved_scholarship_ids
                    }
                },
                {
                    "_id": 0,
                    "scholarship_id": 1,
                    "scholarship_name": 1,
                    "provider_name": 1,
                    "provider_type": 1,
                    "country_id": 1,
                    "host_university_id": 1,
                    "degree_levels": 1,
                    "funding_type": 1,
                    "scholarship_status": 1,
                    "application_opening_date": 1,
                    "application_deadline": 1,
                }
            )
        )

        scholarship_by_id = {
            scholarship["scholarship_id"]: scholarship
            for scholarship in scholarship_documents
        }

        # Preserve the order in the user's saved list.
        saved_scholarships = [
            scholarship_by_id[scholarship_id]
            for scholarship_id in saved_scholarship_ids
            if scholarship_id in scholarship_by_id
        ]

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to retrieve saved opportunities."
            ),
        ) from error

    return {
        "user_id": user_id,
        "saved_university_count": len(
            saved_universities
        ),
        "saved_scholarship_count": len(
            saved_scholarships
        ),
        "saved_universities": saved_universities,
        "saved_scholarships": saved_scholarships,
    }

# ---------------------------------------------------------
# Get recommendation history
# ---------------------------------------------------------

@app.get(
    (
        "/api/user-profiles/{user_id}"
        "/recommendation-history"
    ),
    tags=["Recommendation History"],
)
def get_recommendation_history(
    user_id: str,
) -> dict[str, Any]:
    """Return the recommendation history of one user."""

    database = get_database()

    try:
        profile = database["user_profiles"].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "user_id": 1,
                "recommendation_history": 1,
            },
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User profile '{user_id}' "
                    "was not found."
                ),
            )

        recommendation_history = (
            profile.get("recommendation_history") or []
        )

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to retrieve "
                "recommendation history."
            ),
        ) from error

    return {
        "user_id": user_id,
        "recommendation_history_count": len(
            recommendation_history
        ),
        "recommendation_history": (
            recommendation_history
        ),
    }

# ---------------------------------------------------------
# Recommendation history helper
# ---------------------------------------------------------

MAX_RECOMMENDATION_HISTORY_ITEMS = 50


def append_recommendation_history(
    user_id: str,
    recommendation_type: str,
    recommended_ids: list[str],
) -> dict[str, Any]:
    """
    Append one recommendation run to a user's history.

    Only the latest 50 history records are retained.
    """

    cleaned_recommended_ids = list(
        dict.fromkeys(
            recommendation_id.strip()
            for recommendation_id in recommended_ids
            if (
                isinstance(recommendation_id, str)
                and recommendation_id.strip()
            )
        )
    )

    current_time = datetime.now(timezone.utc)

    history_item = {
        "history_id": f"history_{uuid4().hex}",
        "recommendation_type": recommendation_type,
        "created_at": current_time,
        "result_count": len(cleaned_recommended_ids),
        "recommended_ids": cleaned_recommended_ids,
    }

    database = get_database()

    try:
        update_result = database[
            "user_profiles"
        ].update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "recommendation_history": {
                        "$each": [history_item],
                        "$slice": (
                            -MAX_RECOMMENDATION_HISTORY_ITEMS
                        ),
                    }
                },
                "$set": {
                    "database_updated_at": current_time,
                },
            },
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to save recommendation history."
            ),
        ) from error

    if update_result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"User profile '{user_id}' "
                "was not found."
            ),
        )

    return history_item

# ---------------------------------------------------------
# Delete user profile
# ---------------------------------------------------------

@app.delete(
    "/api/user-profiles/{user_id}",
    tags=["User Profiles"],
)
def delete_user_profile(
    user_id: str,
) -> dict[str, Any]:
    """Delete one user profile permanently."""

    database = get_database()

    try:
        profile = database["user_profiles"].find_one(
            {"user_id": user_id},
            {
                "_id": 0,
                "user_id": 1,
            },
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User profile '{user_id}' "
                    "was not found."
                ),
            )

        delete_result = database[
            "user_profiles"
        ].delete_one(
            {"user_id": user_id}
        )

    except HTTPException:
        raise

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to delete the user profile.",
        ) from error

    if delete_result.deleted_count != 1:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The user profile could not be deleted."
            ),
        )

    return {
        "message": "User profile deleted successfully.",
        "deleted_user_id": user_id,
    }

