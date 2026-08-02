from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


# ---------------------------------------------------------
# Shared FastAPI test client
# ---------------------------------------------------------

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Start the FastAPI application once for this test module.

    Using TestClient as a context manager runs the application's
    startup and shutdown lifespan events correctly.
    """

    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------
# General API tests
# ---------------------------------------------------------

def test_root_endpoint(client: TestClient) -> None:
    """The root endpoint should confirm that the API is running."""

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "EduPath API is running.",
        "documentation": "/docs",
    }


def test_health_endpoint(client: TestClient) -> None:
    """The health endpoint should confirm MongoDB connectivity."""

    response = client.get("/api/health")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status"] == "healthy"
    assert response_data["database"] == "edupath_db"
    assert response_data["mongodb"] == "connected"


# ---------------------------------------------------------
# University list tests
# ---------------------------------------------------------

def test_list_universities(client: TestClient) -> None:
    """The university list should contain the prototype record."""

    response = client.get("/api/universities")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["total"] >= 1
    assert response_data["count"] >= 1
    assert isinstance(response_data["items"], list)

    university_ids = [
        university["university_id"]
        for university in response_data["items"]
    ]

    assert "uni_jp_001" in university_ids


def test_filter_universities_by_country(
    client: TestClient,
) -> None:
    """Country filtering should return only Japanese universities."""

    response = client.get(
        "/api/universities",
        params={"country_id": "country_jp"},
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for university in response_data["items"]:
        assert university["country_id"] == "country_jp"


def test_filter_universities_by_scholarship(
    client: TestClient,
) -> None:
    """Scholarship filtering should return only matching records."""

    response = client.get(
        "/api/universities",
        params={"scholarship_available": True},
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for university in response_data["items"]:
        assert university["scholarship_available"] is True


def test_filter_universities_by_degree_level(
    client: TestClient,
) -> None:
    """Degree filtering should return universities offering Master."""

    response = client.get(
        "/api/universities",
        params={"degree_level": "Master"},
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for university in response_data["items"]:
        assert "Master" in university["degree_levels"]


def test_combined_university_filters(
    client: TestClient,
) -> None:
    """Multiple university filters should work together."""

    response = client.get(
        "/api/universities",
        params={
            "country_id": "country_jp",
            "scholarship_available": True,
            "degree_level": "Master",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for university in response_data["items"]:
        assert university["country_id"] == "country_jp"
        assert university["scholarship_available"] is True
        assert "Master" in university["degree_levels"]


# ---------------------------------------------------------
# Individual university tests
# ---------------------------------------------------------

def test_get_existing_university(
    client: TestClient,
) -> None:
    """An existing university ID should return its document."""

    response = client.get(
        "/api/universities/uni_jp_001"
    )

    assert response.status_code == 200

    university = response.json()

    assert university["university_id"] == "uni_jp_001"
    assert (
        university["university_name"]
        == "The University of Tokyo"
    )
    assert university["country_id"] == "country_jp"
    assert university["city"] == "Tokyo"
    assert university["scholarship_available"] is True


def test_get_nonexistent_university(
    client: TestClient,
) -> None:
    """An unknown university ID should return HTTP 404."""

    response = client.get(
        "/api/universities/uni_jp_999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "University not found."
    }

# ---------------------------------------------------------
# Programme API tests
# ---------------------------------------------------------

def test_list_programs(client: TestClient) -> None:
    """The programme list should contain the pilot record."""

    response = client.get("/api/programs")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["total"] >= 1
    assert response_data["count"] >= 1
    assert isinstance(response_data["items"], list)

    program_ids = [
        program["program_id"]
        for program in response_data["items"]
    ]

    assert "prog_jp_001" in program_ids


def test_get_existing_program(
    client: TestClient,
) -> None:
    """An existing programme ID should return its record."""

    response = client.get(
        "/api/programs/prog_jp_001"
    )

    assert response.status_code == 200

    program = response.json()

    assert program["program_id"] == "prog_jp_001"
    assert program["university_id"] == "uni_jp_001"

    assert (
        program["program_name"]
        == "English Program in Information Science and Technology"
    )

    assert (
        program["field_of_study"]
        == "Information Science and Technology"
    )

    assert program["degree_level"] == "Master"
    assert program["language_of_instruction"] == "English"
    assert program["tuition_fee"] == 535800
    assert program["tuition_currency"] == "JPY"
    assert "April" in program["intake"]
    assert "October" in program["intake"]


def test_get_nonexistent_program(
    client: TestClient,
) -> None:
    """An unknown programme ID should return HTTP 404."""

    response = client.get(
        "/api/programs/prog_jp_999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Programme not found."
    }


def test_filter_programs_by_university(
    client: TestClient,
) -> None:
    """University filtering should return linked programmes."""

    response = client.get(
        "/api/programs",
        params={
            "university_id": "uni_jp_001",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for program in response_data["items"]:
        assert program["university_id"] == "uni_jp_001"


def test_filter_programs_by_degree_level(
    client: TestClient,
) -> None:
    """Degree-level filtering should return Master programmes."""

    response = client.get(
        "/api/programs",
        params={
            "degree_level": "Master",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for program in response_data["items"]:
        assert program["degree_level"] == "Master"


def test_filter_programs_by_language(
    client: TestClient,
) -> None:
    """Language filtering should return English programmes."""

    response = client.get(
        "/api/programs",
        params={
            "language": "English",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for program in response_data["items"]:
        assert (
            program["language_of_instruction"]
            == "English"
        )


def test_filter_programs_by_intake(
    client: TestClient,
) -> None:
    """Intake filtering should match an item in the intake array."""

    response = client.get(
        "/api/programs",
        params={
            "intake": "October",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for program in response_data["items"]:
        assert "October" in program["intake"]


def test_filter_programs_by_maximum_tuition(
    client: TestClient,
) -> None:
    """Tuition filtering should return affordable programmes."""

    response = client.get(
        "/api/programs",
        params={
            "max_tuition_fee": 600000,
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for program in response_data["items"]:
        assert program["tuition_fee"] is not None
        assert program["tuition_fee"] <= 600000


def test_program_tuition_filter_with_no_results(
    client: TestClient,
) -> None:
    """A tuition limit below the pilot fee should return no results."""

    response = client.get(
        "/api/programs",
        params={
            "max_tuition_fee": 500000,
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["total"] == 0
    assert response_data["count"] == 0
    assert response_data["items"] == []


def test_combined_program_filters(
    client: TestClient,
) -> None:
    """Multiple programme filters should work together."""

    response = client.get(
        "/api/programs",
        params={
            "university_id": "uni_jp_001",
            "degree_level": "Master",
            "language": "English",
            "intake": "October",
            "max_tuition_fee": 600000,
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for program in response_data["items"]:
        assert program["university_id"] == "uni_jp_001"
        assert program["degree_level"] == "Master"

        assert (
            program["language_of_instruction"]
            == "English"
        )

        assert "October" in program["intake"]

        assert program["tuition_fee"] is not None
        assert program["tuition_fee"] <= 600000

# ---------------------------------------------------------
# Country API tests
# ---------------------------------------------------------

def test_list_countries(
    client: TestClient,
) -> None:
    """The country list should contain all MVP countries."""

    response = client.get("/api/countries")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["total"] >= 3
    assert response_data["count"] >= 3
    assert isinstance(response_data["items"], list)

    country_ids = {
        country["country_id"]
        for country in response_data["items"]
    }

    expected_country_ids = {
        "country_jp",
        "country_sg",
        "country_my",
    }

    assert expected_country_ids.issubset(country_ids)


def test_get_existing_country(
    client: TestClient,
) -> None:
    """An existing country ID should return its record."""

    response = client.get(
        "/api/countries/country_jp"
    )

    assert response.status_code == 200

    country = response.json()

    assert country["country_id"] == "country_jp"
    assert country["country_name"] == "Japan"
    assert country["region"] == "East Asia"
    assert country["capital_city"] == "Tokyo"
    assert country["currency_code"] == "JPY"
    assert "Japanese" in country["main_language"]

    assert country["estimated_living_cost"] is None
    assert country["cost_currency"] is None


def test_get_nonexistent_country(
    client: TestClient,
) -> None:
    """An unknown country ID should return HTTP 404."""

    response = client.get(
        "/api/countries/country_xx"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Country not found."
    }


def test_filter_countries_by_region(
    client: TestClient,
) -> None:
    """Region filtering should return Southeast Asian countries."""

    response = client.get(
        "/api/countries",
        params={
            "region": "Southeast Asia",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 2

    country_ids = {
        country["country_id"]
        for country in response_data["items"]
    }

    assert {
        "country_sg",
        "country_my",
    }.issubset(country_ids)

    for country in response_data["items"]:
        assert country["region"] == "Southeast Asia"


def test_filter_countries_by_currency(
    client: TestClient,
) -> None:
    """Currency filtering should return Japan for JPY."""

    response = client.get(
        "/api/countries",
        params={
            "currency_code": "JPY",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for country in response_data["items"]:
        assert country["currency_code"] == "JPY"

    country_ids = {
        country["country_id"]
        for country in response_data["items"]
    }

    assert "country_jp" in country_ids


def test_lowercase_currency_filter(
    client: TestClient,
) -> None:
    """Lowercase currency input should be converted to uppercase."""

    response = client.get(
        "/api/countries",
        params={
            "currency_code": "jpy",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    country_ids = {
        country["country_id"]
        for country in response_data["items"]
    }

    assert "country_jp" in country_ids

    for country in response_data["items"]:
        assert country["currency_code"] == "JPY"


def test_filter_countries_by_language(
    client: TestClient,
) -> None:
    """Malay filtering should match Malaysia and Singapore."""

    response = client.get(
        "/api/countries",
        params={
            "language": "Malay",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 2

    country_ids = {
        country["country_id"]
        for country in response_data["items"]
    }

    assert {
        "country_my",
        "country_sg",
    }.issubset(country_ids)

    for country in response_data["items"]:
        assert "Malay" in country["main_language"]


def test_combined_country_filters(
    client: TestClient,
) -> None:
    """Multiple country filters should return Singapore."""

    response = client.get(
        "/api/countries",
        params={
            "region": "Southeast Asia",
            "currency_code": "SGD",
            "language": "English",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    country_ids = {
        country["country_id"]
        for country in response_data["items"]
    }

    assert "country_sg" in country_ids

    for country in response_data["items"]:
        assert country["region"] == "Southeast Asia"
        assert country["currency_code"] == "SGD"
        assert "English" in country["main_language"]


def test_country_filter_with_no_results(
    client: TestClient,
) -> None:
    """A region outside the MVP scope should return no results."""

    response = client.get(
        "/api/countries",
        params={
            "region": "Europe",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["total"] == 0
    assert response_data["count"] == 0
    assert response_data["items"] == []


def test_invalid_currency_code_length(
    client: TestClient,
) -> None:
    """A currency code shorter than three letters should fail."""

    response = client.get(
        "/api/countries",
        params={
            "currency_code": "JP",
        },
    )

    assert response.status_code == 422

