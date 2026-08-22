from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


InternationalEligibilityStatus = Literal[
    "verified_yes",
    "verified_no",
    "unknown",
]


class RootResponse(BaseModel):
    """Response shown at the API root URL."""

    message: str
    documentation: str


class HealthResponse(BaseModel):
    """Response returned by the health-check endpoint."""

    status: str
    database: str
    mongodb: str


class UniversityResponse(BaseModel):
    """Public university information returned by the API."""

    model_config = ConfigDict(extra="ignore")

    university_id: str
    university_name: str
    country_id: str
    city: str
    university_type: str | None = None
    official_website: str

    establishment_year: int | None = None
    global_ranking: int | None = None
    ranking_source: str | None = None
    ranking_year: int | None = None

    degree_levels: list[str] | None = None
    scholarship_available: bool | None = None

    # International-student accessibility.
    # Existing/unverified records default to "unknown".
    international_students_status: (
        InternationalEligibilityStatus
    ) = "unknown"

    international_admissions_url: str | None = None
    international_admissions_note: str | None = None

    international_students_last_verified_at: (
        datetime | None
    ) = None

    source_url: str
    collected_at: datetime
    last_verified_at: datetime | None = None
    freshness_status: str

class UniversityListResponse(BaseModel):
    """Response returned for a university list request."""

    total: int
    count: int
    items: list[UniversityResponse]

class ProgramResponse(BaseModel):
    """Public academic programme data returned by the API."""

    model_config = ConfigDict(extra="ignore")

    program_id: str
    university_id: str
    program_name: str
    field_of_study: str
    degree_level: str

    duration_years: int | float | None = None
    study_mode: str | None = None
    language_of_instruction: str

    tuition_fee: int | float | None = None
    tuition_currency: str | None = None
    tuition_period: str | None = None

    tuition_academic_year: int | None = None
    tuition_student_scope: str | None = None
    tuition_source_url: str | None = None
    tuition_last_verified_at: datetime | None = None
    tuition_note: str | None = None
    
    minimum_gpa: int | float | None = None
    gpa_scale: int | float | None = None
    ielts_requirement: int | float | None = None
    toefl_requirement: int | None = None

    intake: list[str] | None = None
    application_deadline: datetime | None = None

    # Programme-level international applicant eligibility.
    # This is separate from university-level accessibility.
    international_applicants_status: (
        InternationalEligibilityStatus
    ) = "unknown"

    international_application_url: str | None = None
    international_requirements_note: str | None = None

    international_applicants_last_verified_at: (
        datetime | None
    ) = None

    program_url: str
    collected_at: datetime
    last_verified_at: datetime
    freshness_status: str


class ProgramListResponse(BaseModel):
    """Response returned for a programme list request."""

    total: int
    count: int
    items: list[ProgramResponse]

class CountryResponse(BaseModel):
    country_id: str
    country_name: str

    region: Optional[str] = None
    capital_city: Optional[str] = None
    currency_code: Optional[str] = None

    # IMPORTANT:
    # MongoDB stores language values as arrays:
    # ["Japanese"]
    # ["Malay"]
    # ["English", "Malay", "Mandarin", "Tamil"]
    main_language: Optional[List[str]] = None

    source_url: Optional[str] = None
    collected_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None

    model_config = ConfigDict(
        extra="ignore"
    )


class CountryListResponse(BaseModel):
    items: List[CountryResponse]
    total: int
    limit: Optional[int] = None

    model_config = ConfigDict(
        extra="ignore"
    )


class AgeRequirement(BaseModel):
    """Optional structured age rule for one scholarship degree level."""

    model_config = ConfigDict(extra="ignore")

    degree_level: str | None = None
    operator: str | None = None
    age: int | None = None
    description: str | None = None


class AllowanceTier(BaseModel):
    """Optional structured scholarship allowance for one degree level."""

    model_config = ConfigDict(extra="ignore")

    degree_level: str | None = None
    amount: float | None = None
    currency: str | None = None
    description: str | None = None


class ScholarshipResponse(BaseModel):
    """Public scholarship data returned by the API."""

    model_config = ConfigDict(extra="ignore")

    scholarship_id: str
    scholarship_name: str

    provider_name: str
    provider_type: str

    country_id: str
    host_university_id: str | None = None

    eligible_nationalities: list[str] | None = None
    degree_levels: list[str]
    fields_of_study: list[str] | None = None

    minimum_gpa: int | float | None = None
    gpa_scale: int | float | None = None

    ielts_requirement: int | float | None = None
    toefl_requirement: int | None = None
    age_limit: int | None = None

    ielts_requirement_text: str | None = None
    toefl_requirement_text: str | None = None
    age_requirement_details: list[AgeRequirement] | None = None

    funding_type: str
    tuition_coverage: str | None = None

    monthly_allowance: int | float | None = None
    allowance_currency: str | None = None
    monthly_allowance_details: list[AllowanceTier] | None = None

    travel_allowance: str | None = None
    accommodation_support: str | None = None
    health_insurance: str | None = None

    required_documents: list[str] | None = None

    application_opening_date: datetime | None = None
    application_deadline: datetime | None = None

    scholarship_status: str
    application_cycle: str

    official_website: str
    source_url: str

    collected_at: datetime
    last_verified_at: datetime

    freshness_status: str
    data_quality_status: str


class ScholarshipListResponse(BaseModel):
    """Response returned for a scholarship list request."""

    total: int
    count: int
    items: list[ScholarshipResponse]

# ---------------------------------------------------------
# User profile schemas
# ---------------------------------------------------------

class UserProfileCreate(BaseModel):
    """Data required to create a new user profile."""

    user_id: str = Field(
        min_length=3,
        max_length=100,
    )

    nationality: str = Field(
        min_length=2,
        max_length=100,
    )

    current_education_level: str = Field(
        min_length=2,
        max_length=50,
    )

    target_degree_level: str = Field(
        min_length=2,
        max_length=50,
    )

    preferred_major: str = Field(
        min_length=2,
        max_length=200,
    )

    gpa: float | None = Field(
        default=None,
        ge=0,
    )

    gpa_scale: float | None = Field(
        default=None,
        gt=0,
    )

    ielts_score: float | None = Field(
        default=None,
        ge=0,
        le=9,
    )

    toefl_score: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    annual_budget: float | None = Field(
        default=None,
        ge=0,
    )

    budget_currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    preferred_countries: list[str] = Field(
        min_length=1,
    )

    scholarship_required: bool

    preferred_funding_type: str | None = Field(
        default=None,
        max_length=100,
    )

    preferred_intake: str | None = Field(
        default=None,
        max_length=100,
    )

class AuthenticatedUserProfileCreate(BaseModel):
    """
    Academic profile data submitted by an authenticated
    student.

    The user_id is intentionally excluded because the
    backend obtains it from the JWT access token.
    """

    model_config = ConfigDict(extra="forbid")

    nationality: str = Field(
        min_length=2,
        max_length=100,
    )

    current_education_level: str = Field(
        min_length=2,
        max_length=50,
    )

    target_degree_level: str = Field(
        min_length=2,
        max_length=50,
    )

    preferred_major: str = Field(
        min_length=2,
        max_length=200,
    )

    gpa: float | None = Field(
        default=None,
        ge=0,
    )

    gpa_scale: float | None = Field(
        default=None,
        gt=0,
    )

    ielts_score: float | None = Field(
        default=None,
        ge=0,
        le=9,
    )

    toefl_score: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    annual_budget: float | None = Field(
        default=None,
        ge=0,
    )

    budget_currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    preferred_countries: list[str] = Field(
        min_length=1,
    )

    scholarship_required: bool

    preferred_funding_type: str | None = Field(
        default=None,
        max_length=100,
    )

    preferred_intake: str | None = Field(
        default=None,
        max_length=100,
    )


class UserProfileUpdate(BaseModel):
    """Optional fields used to update a user profile."""

    nationality: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    current_education_level: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    target_degree_level: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    preferred_major: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    gpa: float | None = Field(
        default=None,
        ge=0,
    )

    gpa_scale: float | None = Field(
        default=None,
        gt=0,
    )

    ielts_score: float | None = Field(
        default=None,
        ge=0,
        le=9,
    )

    toefl_score: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    annual_budget: float | None = Field(
        default=None,
        ge=0,
    )

    budget_currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    preferred_countries: list[str] | None = Field(
        default=None,
        min_length=1,
    )

    scholarship_required: bool | None = None

    preferred_funding_type: str | None = Field(
        default=None,
        max_length=100,
    )

    preferred_intake: str | None = Field(
        default=None,
        max_length=100,
    )



class AuthenticatedUserProfileUpdate(UserProfileUpdate):
    """
    Academic-profile changes submitted by the
    currently authenticated student.

    Unknown fields such as user_id are rejected.
    """

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------
# Authentication schemas
# ---------------------------------------------------------

class AccountRegister(BaseModel):
    """Data required to register a student account."""

    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: str = Field(
        min_length=5,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class AccountLogin(BaseModel):
    """Credentials required to log in."""

    email: str = Field(
        min_length=5,
        max_length=254,
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class AccountResponse(BaseModel):
    """Public account information."""

    user_id: str
    full_name: str
    email: str
    role: str
    is_active: bool
    profile_completed: bool


class TokenResponse(BaseModel):
    """Successful authentication response."""

    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: AccountResponse