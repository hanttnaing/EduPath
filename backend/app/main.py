from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from pymongo import ASCENDING
from pymongo.errors import PyMongoError

from backend.app.database import (
    DATABASE_NAME,
    close_database,
    get_database,
    ping_database,
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
            .sort(
                [
                    ("application_deadline", ASCENDING),
                    ("scholarship_name", ASCENDING),
                ]
            )
            .skip(skip)
            .limit(limit)
        )

        scholarships = list(cursor)

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

    return scholarship