from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
    university_type: str
    official_website: str

    establishment_year: int | None = None
    global_ranking: int | None = None
    ranking_source: str | None = None
    ranking_year: int | None = None

    degree_levels: list[str] = Field(default_factory=list)
    scholarship_available: bool

    source_url: str
    collected_at: datetime
    last_verified_at: datetime
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

    minimum_gpa: int | float | None = None
    gpa_scale: int | float | None = None
    ielts_requirement: int | float | None = None
    toefl_requirement: int | None = None

    intake: list[str] | None = None
    application_deadline: datetime | None = None

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
    """Public country data returned by the API."""

    model_config = ConfigDict(extra="ignore")

    country_id: str
    country_name: str
    region: str
    capital_city: str
    currency_code: str
    main_language: list[str]

    estimated_living_cost: int | float | None = None
    cost_currency: str | None = None

    source_url: str
    collected_at: datetime
    last_verified_at: datetime


class CountryListResponse(BaseModel):
    """Response returned for a country list request."""

    total: int
    count: int
    items: list[CountryResponse]