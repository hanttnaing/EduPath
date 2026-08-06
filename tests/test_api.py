from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

from backend.app.database import get_database

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

# ---------------------------------------------------------
# Scholarship API tests
# ---------------------------------------------------------

def test_list_scholarships(
    client: TestClient,
) -> None:
    """The scholarship list should contain the pilot record."""

    response = client.get("/api/scholarships")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["total"] >= 1
    assert response_data["count"] >= 1
    assert isinstance(response_data["items"], list)

    scholarship_ids = {
        scholarship["scholarship_id"]
        for scholarship in response_data["items"]
    }

    assert "sch_jp_001" in scholarship_ids


def test_get_existing_scholarship(
    client: TestClient,
) -> None:
    """An existing scholarship ID should return its record."""

    response = client.get(
        "/api/scholarships/sch_jp_001"
    )

    assert response.status_code == 200

    scholarship = response.json()

    assert scholarship["scholarship_id"] == "sch_jp_001"
    assert scholarship["country_id"] == "country_jp"

    assert (
        scholarship["host_university_id"]
        == "uni_jp_001"
    )

    assert scholarship["provider_type"] == "Government"
    assert scholarship["funding_type"] == "Fully Funded"

    assert scholarship["monthly_allowance"] == 143000
    assert scholarship["allowance_currency"] == "JPY"

    assert "Master" in scholarship["degree_levels"]
    assert "PhD" in scholarship["degree_levels"]

    assert (
        "Computer Science"
        in scholarship["fields_of_study"]
    )

    assert scholarship["scholarship_status"] == "upcoming"
    assert scholarship["application_cycle"] == "2027"

    assert scholarship[
        "application_opening_date"
    ].startswith("2026-10-19")

    assert scholarship[
        "application_deadline"
    ].startswith("2026-10-30")


def test_get_nonexistent_scholarship(
    client: TestClient,
) -> None:
    """An unknown scholarship ID should return HTTP 404."""

    response = client.get(
        "/api/scholarships/sch_jp_999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Scholarship not found."
    }


def test_filter_scholarships_by_country_and_university(
    client: TestClient,
) -> None:
    """Country and host-university filters should work together."""

    response = client.get(
        "/api/scholarships",
        params={
            "country_id": "country_jp",
            "host_university_id": "uni_jp_001",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for scholarship in response_data["items"]:
        assert scholarship["country_id"] == "country_jp"

        assert (
            scholarship["host_university_id"]
            == "uni_jp_001"
        )


def test_filter_scholarships_by_degree_level(
    client: TestClient,
) -> None:
    """Degree-level filtering should match an array value."""

    response = client.get(
        "/api/scholarships",
        params={
            "degree_level": "Master",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for scholarship in response_data["items"]:
        assert "Master" in scholarship["degree_levels"]


def test_filter_scholarships_by_field_of_study(
    client: TestClient,
) -> None:
    """Field filtering should match Computer Science."""

    response = client.get(
        "/api/scholarships",
        params={
            "field_of_study": "Computer Science",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for scholarship in response_data["items"]:
        assert (
            "Computer Science"
            in scholarship["fields_of_study"]
        )


def test_filter_scholarships_by_funding_type(
    client: TestClient,
) -> None:
    """Funding filtering should return fully funded records."""

    response = client.get(
        "/api/scholarships",
        params={
            "funding_type": "Fully Funded",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for scholarship in response_data["items"]:
        assert (
            scholarship["funding_type"]
            == "Fully Funded"
        )


def test_case_insensitive_scholarship_status_filter(
    client: TestClient,
) -> None:
    """Uppercase status input should be converted to lowercase."""

    response = client.get(
        "/api/scholarships",
        params={
            "scholarship_status": "UPCOMING",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for scholarship in response_data["items"]:
        assert (
            scholarship["scholarship_status"]
            == "upcoming"
        )


def test_filter_scholarships_by_application_cycle(
    client: TestClient,
) -> None:
    """Application-cycle filtering should return 2027 records."""

    response = client.get(
        "/api/scholarships",
        params={
            "application_cycle": "2027",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    for scholarship in response_data["items"]:
        assert scholarship["application_cycle"] == "2027"


def test_scholarship_allowance_thresholds(
    client: TestClient,
) -> None:
    """Allowance filtering should support result and no-result cases."""

    affordable_response = client.get(
        "/api/scholarships",
        params={
            "min_monthly_allowance": 100000,
        },
    )

    assert affordable_response.status_code == 200

    affordable_data = affordable_response.json()

    assert affordable_data["count"] >= 1

    for scholarship in affordable_data["items"]:
        assert scholarship["monthly_allowance"] is not None

        assert (
            scholarship["monthly_allowance"]
            >= 100000
        )

    high_allowance_response = client.get(
        "/api/scholarships",
        params={
            "min_monthly_allowance": 150000,
        },
    )

    assert high_allowance_response.status_code == 200

    high_allowance_data = high_allowance_response.json()

    assert high_allowance_data["total"] == 0
    assert high_allowance_data["count"] == 0
    assert high_allowance_data["items"] == []


def test_combined_scholarship_filters(
    client: TestClient,
) -> None:
    """All scholarship filters should work together."""

    response = client.get(
        "/api/scholarships",
        params={
            "country_id": "country_jp",
            "host_university_id": "uni_jp_001",
            "degree_level": "Master",
            "field_of_study": "Computer Science",
            "funding_type": "Fully Funded",
            "scholarship_status": "upcoming",
            "application_cycle": "2027",
            "min_monthly_allowance": 100000,
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["count"] >= 1

    scholarship_ids = {
        scholarship["scholarship_id"]
        for scholarship in response_data["items"]
    }

    assert "sch_jp_001" in scholarship_ids

    for scholarship in response_data["items"]:
        assert scholarship["country_id"] == "country_jp"

        assert (
            scholarship["host_university_id"]
            == "uni_jp_001"
        )

        assert "Master" in scholarship["degree_levels"]

        assert (
            "Computer Science"
            in scholarship["fields_of_study"]
        )

        assert (
            scholarship["funding_type"]
            == "Fully Funded"
        )

        assert (
            scholarship["scholarship_status"]
            == "upcoming"
        )

        assert scholarship["application_cycle"] == "2027"

        assert scholarship["monthly_allowance"] is not None

        assert (
            scholarship["monthly_allowance"]
            >= 100000
        )


def test_negative_monthly_allowance_validation(
    client: TestClient,
) -> None:
    """A negative allowance value should return HTTP 422."""

    response = client.get(
        "/api/scholarships",
        params={
            "min_monthly_allowance": -1,
        },
    )

    assert response.status_code == 422

# ---------------------------------------------------------
# Programme recommendation API tests
# ---------------------------------------------------------

def test_program_recommendations_for_existing_user(
    client: TestClient,
) -> None:
    """A valid user should receive ranked recommendations."""

    response = client.get(
        "/api/recommendations/programs/user_test_001"
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["user_id"] == "user_test_001"
    assert response_data["total_program_candidates"] >= 1
    assert response_data["eligible_candidates"] >= 1
    assert response_data["returned_recommendations"] >= 1

    assert isinstance(
        response_data["recommendations"],
        list,
    )

    program_ids = {
        recommendation["program_id"]
        for recommendation
        in response_data["recommendations"]
    }

    assert "prog_jp_001" in program_ids


def test_program_recommendation_explainability(
    client: TestClient,
) -> None:
    """Recommendations should include scores and explanations."""

    response = client.get(
        "/api/recommendations/programs/user_test_001",
        params={"top_k": 5},
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    pilot_recommendation = next(
        recommendation
        for recommendation in recommendations
        if recommendation["program_id"] == "prog_jp_001"
    )

    assert (
        pilot_recommendation["university_id"]
        == "uni_jp_001"
    )

    assert (
        pilot_recommendation["university_name"]
        == "The University of Tokyo"
    )

    assert pilot_recommendation["country_name"] == "Japan"

    assert (
        pilot_recommendation["known_eligibility_status"]
        == "eligible_under_known_rules"
    )

    assert 0 <= pilot_recommendation["match_score"] <= 100

    assert pilot_recommendation["maximum_score"] == 100

    assert isinstance(
        pilot_recommendation["score_breakdown"],
        dict,
    )

    assert isinstance(
        pilot_recommendation["match_reasons"],
        list,
    )

    assert len(
        pilot_recommendation["match_reasons"]
    ) >= 1

    assert isinstance(
        pilot_recommendation["requirement_gaps"],
        list,
    )


def test_program_recommendation_top_k(
    client: TestClient,
) -> None:
    """The API should respect the top_k limit."""

    response = client.get(
        "/api/recommendations/programs/user_test_001",
        params={"top_k": 1},
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["returned_recommendations"] <= 1

    assert len(
        response_data["recommendations"]
    ) <= 1


def test_program_recommendations_for_unknown_user(
    client: TestClient,
) -> None:
    """An unknown user ID should return HTTP 404."""

    response = client.get(
        "/api/recommendations/programs/user_test_999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile 'user_test_999' was not found."
        )
    }


def test_invalid_program_recommendation_top_k(
    client: TestClient,
) -> None:
    """Values outside the allowed top_k range should fail."""

    zero_response = client.get(
        "/api/recommendations/programs/user_test_001",
        params={"top_k": 0},
    )

    assert zero_response.status_code == 422

    excessive_response = client.get(
        "/api/recommendations/programs/user_test_001",
        params={"top_k": 21},
    )

    assert excessive_response.status_code == 422

# ---------------------------------------------------------
# Scholarship recommendation API tests
# ---------------------------------------------------------

def test_scholarship_recommendations_for_existing_user(
    client: TestClient,
) -> None:
    """A valid user should receive scholarship recommendations."""

    response = client.get(
        "/api/recommendations/scholarships/user_test_001"
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["user_id"] == "user_test_001"

    assert (
        response_data["total_scholarship_candidates"]
        >= 1
    )

    assert response_data["eligible_candidates"] >= 1

    assert (
        response_data["returned_recommendations"]
        >= 1
    )

    assert isinstance(
        response_data["recommendations"],
        list,
    )

    scholarship_ids = {
        recommendation["scholarship_id"]
        for recommendation
        in response_data["recommendations"]
    }

    assert "sch_jp_001" in scholarship_ids


def test_scholarship_recommendation_explainability(
    client: TestClient,
) -> None:
    """Scholarship results should include explanations."""

    response = client.get(
        "/api/recommendations/scholarships/user_test_001",
        params={"top_k": 5},
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    pilot_recommendation = next(
        recommendation
        for recommendation in recommendations
        if recommendation["scholarship_id"]
        == "sch_jp_001"
    )

    assert pilot_recommendation["country_name"] == "Japan"

    assert (
        pilot_recommendation["host_university_id"]
        == "uni_jp_001"
    )

    assert (
        pilot_recommendation["funding_type"]
        == "Fully Funded"
    )

    assert (
        pilot_recommendation["known_eligibility_status"]
        == "eligible_under_known_rules"
    )

    assert 0 <= pilot_recommendation["match_score"] <= 100

    assert pilot_recommendation["maximum_score"] == 100

    assert isinstance(
        pilot_recommendation["score_breakdown"],
        dict,
    )

    assert isinstance(
        pilot_recommendation["match_reasons"],
        list,
    )

    assert len(
        pilot_recommendation["match_reasons"]
    ) >= 1

    assert isinstance(
        pilot_recommendation["requirement_gaps"],
        list,
    )


def test_scholarship_recommendation_top_k(
    client: TestClient,
) -> None:
    """The scholarship API should respect top_k."""

    response = client.get(
        "/api/recommendations/scholarships/user_test_001",
        params={"top_k": 1},
    )

    assert response.status_code == 200

    response_data = response.json()

    assert (
        response_data["returned_recommendations"]
        <= 1
    )

    assert len(
        response_data["recommendations"]
    ) <= 1


def test_scholarship_recommendations_for_unknown_user(
    client: TestClient,
) -> None:
    """An unknown user should return HTTP 404."""

    response = client.get(
        "/api/recommendations/scholarships/user_test_999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile 'user_test_999' was not found."
        )
    }


def test_invalid_scholarship_recommendation_top_k(
    client: TestClient,
) -> None:
    """Invalid top_k values should return HTTP 422."""

    zero_response = client.get(
        "/api/recommendations/scholarships/user_test_001",
        params={"top_k": 0},
    )

    assert zero_response.status_code == 422

    excessive_response = client.get(
        "/api/recommendations/scholarships/user_test_001",
        params={"top_k": 21},
    )

    assert excessive_response.status_code == 422

# ---------------------------------------------------------
# User profile read API tests
# ---------------------------------------------------------

def test_list_user_profiles(
    client: TestClient,
) -> None:
    """The API should return the pilot user profile."""

    response = client.get("/api/user-profiles")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["returned_profiles"] >= 1

    assert isinstance(
        response_data["profiles"],
        list,
    )

    pilot_profile = next(
        profile
        for profile in response_data["profiles"]
        if profile["user_id"] == "user_test_001"
    )

    assert pilot_profile["nationality"] == "Myanmar"

    assert (
        pilot_profile["target_degree_level"]
        == "Master"
    )

    assert (
        pilot_profile["preferred_major"]
        == "Computer Science"
    )

    assert "Japan" in pilot_profile[
        "preferred_countries"
    ]

    assert pilot_profile["scholarship_required"] is True

    # Internal MongoDB and ETL fields must not be exposed.
    assert "_id" not in pilot_profile
    assert "content_hash" not in pilot_profile
    assert "created_at" not in pilot_profile
    assert "database_updated_at" not in pilot_profile


def test_get_existing_user_profile(
    client: TestClient,
) -> None:
    """The detail endpoint should return one profile."""

    response = client.get(
        "/api/user-profiles/user_test_001"
    )

    assert response.status_code == 200

    profile = response.json()

    assert profile["user_id"] == "user_test_001"
    assert profile["nationality"] == "Myanmar"

    assert (
        profile["current_education_level"]
        == "Bachelor"
    )

    assert profile["target_degree_level"] == "Master"

    assert profile["preferred_major"] == "Computer Science"

    assert profile["gpa"] == 3.5
    assert profile["gpa_scale"] == 4
    assert profile["ielts_score"] == 6.5
    assert profile["toefl_score"] is None

    assert profile["annual_budget"] == 600000
    assert profile["budget_currency"] == "JPY"

    assert profile["preferred_countries"] == [
        "Japan"
    ]

    assert profile["scholarship_required"] is True

    assert (
        profile["preferred_funding_type"]
        == "Fully Funded"
    )

    assert profile["preferred_intake"] == "October"

    assert isinstance(
        profile["saved_universities"],
        list,
    )

    assert isinstance(
        profile["saved_scholarships"],
        list,
    )

    assert isinstance(
        profile["recommendation_history"],
        list,
    )

    assert "_id" not in profile
    assert "content_hash" not in profile
    assert "created_at" not in profile
    assert "database_updated_at" not in profile


def test_user_profile_nationality_and_degree_filters(
    client: TestClient,
) -> None:
    """Nationality and degree filters should work."""

    response = client.get(
        "/api/user-profiles",
        params={
            "nationality": "Myanmar",
            "target_degree_level": "Master",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["returned_profiles"] >= 1

    for profile in response_data["profiles"]:
        assert profile["nationality"] == "Myanmar"

        assert (
            profile["target_degree_level"]
            == "Master"
        )


def test_user_profile_country_and_scholarship_filters(
    client: TestClient,
) -> None:
    """Country and scholarship filters should work."""

    response = client.get(
        "/api/user-profiles",
        params={
            "preferred_country": "Japan",
            "scholarship_required": "true",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["returned_profiles"] >= 1

    pilot_user_ids = {
        profile["user_id"]
        for profile in response_data["profiles"]
    }

    assert "user_test_001" in pilot_user_ids

    for profile in response_data["profiles"]:
        assert "Japan" in profile[
            "preferred_countries"
        ]

        assert profile["scholarship_required"] is True


def test_get_unknown_user_profile(
    client: TestClient,
) -> None:
    """An unknown user ID should return HTTP 404."""

    response = client.get(
        "/api/user-profiles/user_test_999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile 'user_test_999' was not found."
        )
    }


def test_invalid_user_profile_limit(
    client: TestClient,
) -> None:
    """Values outside the limit range should fail."""

    zero_response = client.get(
        "/api/user-profiles",
        params={"limit": 0},
    )

    assert zero_response.status_code == 422

    excessive_response = client.get(
        "/api/user-profiles",
        params={"limit": 101},
    )

    assert excessive_response.status_code == 422

# ---------------------------------------------------------
# User profile create API tests
# ---------------------------------------------------------

CREATE_TEST_USER_ID = "user_api_create_test_001"


def delete_create_test_user() -> None:
    """Remove the temporary profile used by create tests."""

    database = get_database()

    database["user_profiles"].delete_many(
        {"user_id": CREATE_TEST_USER_ID}
    )


def build_valid_create_profile() -> dict:
    """Return a valid profile request body."""

    return {
        "user_id": CREATE_TEST_USER_ID,
        "nationality": "Myanmar",
        "current_education_level": "Bachelor",
        "target_degree_level": "Master",
        "preferred_major": (
            "Information Science and Technology"
        ),
        "gpa": 3.3,
        "gpa_scale": 4.0,
        "ielts_score": 6.5,
        "toefl_score": None,
        "annual_budget": 700000,
        "budget_currency": "JPY",
        "preferred_countries": [
            "Japan"
        ],
        "scholarship_required": True,
        "preferred_funding_type": "Fully Funded",
        "preferred_intake": "October",
    }


def test_create_user_profile_successfully(
    client: TestClient,
) -> None:
    """A valid profile should be created with HTTP 201."""

    delete_create_test_user()

    try:
        request_data = build_valid_create_profile()

        response = client.post(
            "/api/user-profiles",
            json=request_data,
        )

        assert response.status_code == 201

        response_data = response.json()

        assert (
            response_data["message"]
            == "User profile created successfully."
        )

        profile = response_data["profile"]

        assert profile["user_id"] == CREATE_TEST_USER_ID
        assert profile["nationality"] == "Myanmar"

        assert (
            profile["target_degree_level"]
            == "Master"
        )

        assert (
            profile["preferred_major"]
            == "Information Science and Technology"
        )

        assert profile["gpa"] == 3.3
        assert profile["gpa_scale"] == 4.0
        assert profile["ielts_score"] == 6.5
        assert profile["annual_budget"] == 700000
        assert profile["budget_currency"] == "JPY"

        assert profile["preferred_countries"] == [
            "Japan"
        ]

        assert profile["scholarship_required"] is True

        assert (
            profile["preferred_funding_type"]
            == "Fully Funded"
        )

        assert profile["saved_universities"] == []
        assert profile["saved_scholarships"] == []
        assert profile["recommendation_history"] == []

        # Internal database fields must not be exposed.
        assert "_id" not in profile
        assert "content_hash" not in profile
        assert "created_at" not in profile
        assert "database_updated_at" not in profile

        detail_response = client.get(
            f"/api/user-profiles/{CREATE_TEST_USER_ID}"
        )

        assert detail_response.status_code == 200

    finally:
        delete_create_test_user()


def test_create_duplicate_user_profile(
    client: TestClient,
) -> None:
    """Creating the same user ID twice should return 409."""

    delete_create_test_user()

    try:
        request_data = build_valid_create_profile()

        first_response = client.post(
            "/api/user-profiles",
            json=request_data,
        )

        assert first_response.status_code == 201

        duplicate_response = client.post(
            "/api/user-profiles",
            json=request_data,
        )

        assert duplicate_response.status_code == 409

        assert duplicate_response.json() == {
            "detail": (
                f"User profile '{CREATE_TEST_USER_ID}' "
                "already exists."
            )
        }

    finally:
        delete_create_test_user()


def test_create_profile_with_invalid_country(
    client: TestClient,
) -> None:
    """An unknown preferred country should return 422."""

    delete_create_test_user()

    request_data = build_valid_create_profile()

    request_data["preferred_countries"] = [
        "Unknown Country"
    ]

    response = client.post(
        "/api/user-profiles",
        json=request_data,
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "The following preferred countries "
            "do not exist: Unknown Country"
        )
    }

    detail_response = client.get(
        f"/api/user-profiles/{CREATE_TEST_USER_ID}"
    )

    assert detail_response.status_code == 404


def test_create_profile_with_invalid_gpa(
    client: TestClient,
) -> None:
    """GPA must not be greater than the GPA scale."""

    delete_create_test_user()

    request_data = build_valid_create_profile()

    request_data["gpa"] = 4.5
    request_data["gpa_scale"] = 4.0

    response = client.post(
        "/api/user-profiles",
        json=request_data,
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "GPA cannot be greater than GPA scale."
        )
    }


def test_create_profile_budget_requires_currency(
    client: TestClient,
) -> None:
    """A budget value should require a currency code."""

    delete_create_test_user()

    request_data = build_valid_create_profile()

    request_data["annual_budget"] = 700000
    request_data["budget_currency"] = None

    response = client.post(
        "/api/user-profiles",
        json=request_data,
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "Field 'budget_currency' is required "
            "when annual budget is provided."
        )
    }


def test_create_profile_scholarship_requires_funding_type(
    client: TestClient,
) -> None:
    """
    A scholarship-seeking user should provide a
    preferred funding type.
    """

    delete_create_test_user()

    request_data = build_valid_create_profile()

    request_data["scholarship_required"] = True
    request_data["preferred_funding_type"] = None

    response = client.post(
        "/api/user-profiles",
        json=request_data,
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "Field 'preferred_funding_type' "
            "is required when scholarship_required "
            "is true."
        )
    }

# ---------------------------------------------------------
# User profile update API tests
# ---------------------------------------------------------

UPDATE_TEST_USER_ID = "user_api_update_test_001"


def delete_update_test_user() -> None:
    """Remove the temporary profile used by update tests."""

    database = get_database()

    database["user_profiles"].delete_many(
        {"user_id": UPDATE_TEST_USER_ID}
    )


def build_valid_update_test_profile() -> dict:
    """Return a valid request body for an update-test user."""

    return {
        "user_id": UPDATE_TEST_USER_ID,
        "nationality": "Myanmar",
        "current_education_level": "Bachelor",
        "target_degree_level": "Master",
        "preferred_major": "Computer Science",
        "gpa": 3.2,
        "gpa_scale": 4.0,
        "ielts_score": 6.5,
        "toefl_score": None,
        "annual_budget": 650000,
        "budget_currency": "JPY",
        "preferred_countries": [
            "Japan"
        ],
        "scholarship_required": True,
        "preferred_funding_type": "Fully Funded",
        "preferred_intake": "October",
    }


def create_update_test_user(
    client: TestClient,
) -> None:
    """Create a fresh temporary profile for update tests."""

    delete_update_test_user()

    response = client.post(
        "/api/user-profiles",
        json=build_valid_update_test_profile(),
    )

    assert response.status_code == 201


def test_update_user_profile_successfully(
    client: TestClient,
) -> None:
    """PATCH should update only the submitted fields."""

    create_update_test_user(client)

    try:
        response = client.patch(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}",
            json={
                "annual_budget": 750000,
                "preferred_intake": "April",
            },
        )

        assert response.status_code == 200

        response_data = response.json()

        assert (
            response_data["message"]
            == "User profile updated successfully."
        )

        profile = response_data["profile"]

        assert profile["user_id"] == UPDATE_TEST_USER_ID
        assert profile["annual_budget"] == 750000
        assert profile["preferred_intake"] == "April"

        # Fields not included in PATCH must remain unchanged.
        assert profile["nationality"] == "Myanmar"

        assert (
            profile["current_education_level"]
            == "Bachelor"
        )

        assert profile["target_degree_level"] == "Master"
        assert profile["preferred_major"] == "Computer Science"
        assert profile["gpa"] == 3.2
        assert profile["gpa_scale"] == 4.0
        assert profile["budget_currency"] == "JPY"

        assert profile["preferred_countries"] == [
            "Japan"
        ]

        assert profile["scholarship_required"] is True

        assert (
            profile["preferred_funding_type"]
            == "Fully Funded"
        )

        assert profile["saved_universities"] == []
        assert profile["saved_scholarships"] == []
        assert profile["recommendation_history"] == []

        # Internal fields must not be returned.
        assert "_id" not in profile
        assert "content_hash" not in profile
        assert "created_at" not in profile
        assert "database_updated_at" not in profile

        detail_response = client.get(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}"
        )

        assert detail_response.status_code == 200

        saved_profile = detail_response.json()

        assert saved_profile["annual_budget"] == 750000
        assert saved_profile["preferred_intake"] == "April"

    finally:
        delete_update_test_user()


def test_update_unknown_user_profile(
    client: TestClient,
) -> None:
    """Updating an unknown user should return HTTP 404."""

    response = client.patch(
        "/api/user-profiles/user_update_unknown_999",
        json={
            "annual_budget": 750000,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile "
            "'user_update_unknown_999' was not found."
        )
    }


def test_update_profile_with_empty_request(
    client: TestClient,
) -> None:
    """An empty PATCH body should return HTTP 422."""

    create_update_test_user(client)

    try:
        response = client.patch(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}",
            json={},
        )

        assert response.status_code == 422

        assert response.json() == {
            "detail": (
                "At least one profile field "
                "must be provided."
            )
        }

    finally:
        delete_update_test_user()


def test_update_profile_with_invalid_gpa(
    client: TestClient,
) -> None:
    """GPA must not exceed the GPA scale."""

    create_update_test_user(client)

    try:
        response = client.patch(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}",
            json={
                "gpa": 5.0,
                "gpa_scale": 4.0,
            },
        )

        assert response.status_code == 422

        assert response.json() == {
            "detail": (
                "GPA cannot be greater than GPA scale."
            )
        }

        # Failed validation must not modify stored data.
        detail_response = client.get(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}"
        )

        assert detail_response.status_code == 200
        assert detail_response.json()["gpa"] == 3.2
        assert detail_response.json()["gpa_scale"] == 4.0

    finally:
        delete_update_test_user()


def test_update_profile_with_invalid_country(
    client: TestClient,
) -> None:
    """An unknown preferred country should return HTTP 422."""

    create_update_test_user(client)

    try:
        response = client.patch(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}",
            json={
                "preferred_countries": [
                    "Unknown Country"
                ]
            },
        )

        assert response.status_code == 422

        assert response.json() == {
            "detail": (
                "The following preferred countries "
                "do not exist: Unknown Country"
            )
        }

        detail_response = client.get(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}"
        )

        assert detail_response.status_code == 200

        assert detail_response.json()[
            "preferred_countries"
        ] == ["Japan"]

    finally:
        delete_update_test_user()


def test_update_profile_budget_requires_currency(
    client: TestClient,
) -> None:
    """An existing budget cannot keep a null currency."""

    create_update_test_user(client)

    try:
        response = client.patch(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}",
            json={
                "budget_currency": None,
            },
        )

        assert response.status_code == 422

        assert response.json() == {
            "detail": (
                "Field 'budget_currency' is required "
                "when annual budget is provided."
            )
        }

        detail_response = client.get(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}"
        )

        assert detail_response.status_code == 200
        assert detail_response.json()[
            "budget_currency"
        ] == "JPY"

    finally:
        delete_update_test_user()


def test_update_profile_scholarship_requires_funding_type(
    client: TestClient,
) -> None:
    """
    A scholarship-seeking profile must retain a
    preferred funding type.
    """

    create_update_test_user(client)

    try:
        response = client.patch(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}",
            json={
                "preferred_funding_type": None,
            },
        )

        assert response.status_code == 422

        assert response.json() == {
            "detail": (
                "Field 'preferred_funding_type' "
                "is required when scholarship_required "
                "is true."
            )
        }

        detail_response = client.get(
            f"/api/user-profiles/{UPDATE_TEST_USER_ID}"
        )

        assert detail_response.status_code == 200

        assert (
            detail_response.json()[
                "preferred_funding_type"
            ]
            == "Fully Funded"
        )

    finally:
        delete_update_test_user()

# ---------------------------------------------------------
# Save university API tests
# ---------------------------------------------------------

SAVE_UNIVERSITY_TEST_USER_ID = (
    "user_api_save_university_test_001"
)

PILOT_UNIVERSITY_ID = "uni_jp_001"


def delete_save_university_test_user() -> None:
    """Remove the temporary save-university test profile."""

    database = get_database()

    database["user_profiles"].delete_many(
        {
            "user_id": (
                SAVE_UNIVERSITY_TEST_USER_ID
            )
        }
    )


def build_save_university_test_profile() -> dict:
    """Return valid data for the temporary test user."""

    return {
        "user_id": SAVE_UNIVERSITY_TEST_USER_ID,
        "nationality": "Myanmar",
        "current_education_level": "Bachelor",
        "target_degree_level": "Master",
        "preferred_major": "Computer Science",
        "gpa": 3.4,
        "gpa_scale": 4.0,
        "ielts_score": 6.5,
        "toefl_score": None,
        "annual_budget": 700000,
        "budget_currency": "JPY",
        "preferred_countries": [
            "Japan"
        ],
        "scholarship_required": True,
        "preferred_funding_type": "Fully Funded",
        "preferred_intake": "October",
    }


def create_save_university_test_user(
    client: TestClient,
) -> None:
    """Create a fresh profile for save-university tests."""

    delete_save_university_test_user()

    response = client.post(
        "/api/user-profiles",
        json=build_save_university_test_profile(),
    )

    assert response.status_code == 201


def test_save_university_successfully(
    client: TestClient,
) -> None:
    """A valid university should be saved successfully."""

    create_save_university_test_user(client)

    try:
        response = client.post(
            (
                f"/api/user-profiles/"
                f"{SAVE_UNIVERSITY_TEST_USER_ID}"
                f"/saved-universities/"
                f"{PILOT_UNIVERSITY_ID}"
            )
        )

        assert response.status_code == 200

        response_data = response.json()

        assert (
            response_data["message"]
            == "University saved successfully."
        )

        university = response_data["university"]

        assert (
            university["university_id"]
            == PILOT_UNIVERSITY_ID
        )

        assert (
            university["university_name"]
            == "The University of Tokyo"
        )

        assert university["country_id"] == "country_jp"
        assert university["city"] == "Tokyo"

        assert (
            university["university_type"]
            == "Public"
        )

        assert response_data["saved_universities"] == [
            PILOT_UNIVERSITY_ID
        ]

    finally:
        delete_save_university_test_user()


def test_saved_university_is_stored_in_profile(
    client: TestClient,
) -> None:
    """The saved university should persist in MongoDB."""

    create_save_university_test_user(client)

    try:
        save_response = client.post(
            (
                f"/api/user-profiles/"
                f"{SAVE_UNIVERSITY_TEST_USER_ID}"
                f"/saved-universities/"
                f"{PILOT_UNIVERSITY_ID}"
            )
        )

        assert save_response.status_code == 200

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{SAVE_UNIVERSITY_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        profile = profile_response.json()

        assert profile["saved_universities"] == [
            PILOT_UNIVERSITY_ID
        ]

        # Other runtime fields must remain unchanged.
        assert profile["saved_scholarships"] == []
        assert profile["recommendation_history"] == []

    finally:
        delete_save_university_test_user()


def test_save_same_university_without_duplicate(
    client: TestClient,
) -> None:
    """Saving the same university twice must not duplicate it."""

    create_save_university_test_user(client)

    try:
        endpoint = (
            f"/api/user-profiles/"
            f"{SAVE_UNIVERSITY_TEST_USER_ID}"
            f"/saved-universities/"
            f"{PILOT_UNIVERSITY_ID}"
        )

        first_response = client.post(endpoint)

        assert first_response.status_code == 200

        second_response = client.post(endpoint)

        assert second_response.status_code == 200

        second_data = second_response.json()

        assert (
            second_data["message"]
            == "University is already saved."
        )

        assert second_data["saved_universities"] == [
            PILOT_UNIVERSITY_ID
        ]

        assert (
            second_data["saved_universities"].count(
                PILOT_UNIVERSITY_ID
            )
            == 1
        )

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{SAVE_UNIVERSITY_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        saved_universities = profile_response.json()[
            "saved_universities"
        ]

        assert saved_universities == [
            PILOT_UNIVERSITY_ID
        ]

        assert (
            saved_universities.count(
                PILOT_UNIVERSITY_ID
            )
            == 1
        )

    finally:
        delete_save_university_test_user()


def test_save_university_for_unknown_user(
    client: TestClient,
) -> None:
    """An unknown user should return HTTP 404."""

    response = client.post(
        (
            "/api/user-profiles/"
            "user_save_unknown_999"
            "/saved-universities/"
            f"{PILOT_UNIVERSITY_ID}"
        )
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile 'user_save_unknown_999' "
            "was not found."
        )
    }


def test_save_unknown_university(
    client: TestClient,
) -> None:
    """An unknown university should not be saved."""

    create_save_university_test_user(client)

    try:
        response = client.post(
            (
                f"/api/user-profiles/"
                f"{SAVE_UNIVERSITY_TEST_USER_ID}"
                "/saved-universities/"
                "uni_unknown_999"
            )
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": (
                "University 'uni_unknown_999' "
                "was not found."
            )
        }

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{SAVE_UNIVERSITY_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        assert profile_response.json()[
            "saved_universities"
        ] == []

    finally:
        delete_save_university_test_user()

# ---------------------------------------------------------
# Unsave university API tests
# ---------------------------------------------------------

UNSAVE_UNIVERSITY_TEST_USER_ID = (
    "user_api_unsave_university_test_001"
)

UNSAVE_PILOT_UNIVERSITY_ID = "uni_jp_001"


def delete_unsave_university_test_user() -> None:
    """Remove the temporary unsave-university test user."""

    database = get_database()

    database["user_profiles"].delete_many(
        {
            "user_id": (
                UNSAVE_UNIVERSITY_TEST_USER_ID
            )
        }
    )


def build_unsave_university_test_profile() -> dict:
    """Return valid data for the temporary test profile."""

    return {
        "user_id": UNSAVE_UNIVERSITY_TEST_USER_ID,
        "nationality": "Myanmar",
        "current_education_level": "Bachelor",
        "target_degree_level": "Master",
        "preferred_major": "Computer Science",
        "gpa": 3.4,
        "gpa_scale": 4.0,
        "ielts_score": 6.5,
        "toefl_score": None,
        "annual_budget": 700000,
        "budget_currency": "JPY",
        "preferred_countries": [
            "Japan"
        ],
        "scholarship_required": True,
        "preferred_funding_type": "Fully Funded",
        "preferred_intake": "October",
    }


def create_unsave_university_test_user(
    client: TestClient,
) -> None:
    """Create a fresh profile for unsave tests."""

    delete_unsave_university_test_user()

    response = client.post(
        "/api/user-profiles",
        json=build_unsave_university_test_profile(),
    )

    assert response.status_code == 201


def save_pilot_university_for_unsave_test(
    client: TestClient,
) -> None:
    """Save the pilot university before removing it."""

    response = client.post(
        (
            f"/api/user-profiles/"
            f"{UNSAVE_UNIVERSITY_TEST_USER_ID}"
            f"/saved-universities/"
            f"{UNSAVE_PILOT_UNIVERSITY_ID}"
        )
    )

    assert response.status_code == 200


def test_unsave_university_successfully(
    client: TestClient,
) -> None:
    """A saved university should be removed successfully."""

    create_unsave_university_test_user(client)

    try:
        save_pilot_university_for_unsave_test(client)

        response = client.delete(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_UNIVERSITY_TEST_USER_ID}"
                f"/saved-universities/"
                f"{UNSAVE_PILOT_UNIVERSITY_ID}"
            )
        )

        assert response.status_code == 200

        response_data = response.json()

        assert (
            response_data["message"]
            == (
                "University removed from saved list "
                "successfully."
            )
        )

        university = response_data["university"]

        assert (
            university["university_id"]
            == UNSAVE_PILOT_UNIVERSITY_ID
        )

        assert (
            university["university_name"]
            == "The University of Tokyo"
        )

        assert university["country_id"] == "country_jp"
        assert university["city"] == "Tokyo"

        assert (
            university["university_type"]
            == "Public"
        )

        assert response_data["saved_universities"] == []

    finally:
        delete_unsave_university_test_user()


def test_unsaved_university_is_removed_from_profile(
    client: TestClient,
) -> None:
    """The saved university should disappear from MongoDB."""

    create_unsave_university_test_user(client)

    try:
        save_pilot_university_for_unsave_test(client)

        delete_response = client.delete(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_UNIVERSITY_TEST_USER_ID}"
                f"/saved-universities/"
                f"{UNSAVE_PILOT_UNIVERSITY_ID}"
            )
        )

        assert delete_response.status_code == 200

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_UNIVERSITY_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        profile = profile_response.json()

        assert profile["saved_universities"] == []

        # Other runtime data should remain unchanged.
        assert profile["saved_scholarships"] == []
        assert profile["recommendation_history"] == []

        # Other profile fields must remain unchanged.
        assert profile["nationality"] == "Myanmar"

        assert (
            profile["preferred_major"]
            == "Computer Science"
        )

        assert profile["annual_budget"] == 700000

    finally:
        delete_unsave_university_test_user()


def test_unsave_university_that_is_not_saved(
    client: TestClient,
) -> None:
    """
    Removing an unsaved university should return safely
    without creating an error.
    """

    create_unsave_university_test_user(client)

    try:
        response = client.delete(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_UNIVERSITY_TEST_USER_ID}"
                f"/saved-universities/"
                f"{UNSAVE_PILOT_UNIVERSITY_ID}"
            )
        )

        assert response.status_code == 200

        response_data = response.json()

        assert (
            response_data["message"]
            == "University is not currently saved."
        )

        assert response_data["saved_universities"] == []

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_UNIVERSITY_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        assert profile_response.json()[
            "saved_universities"
        ] == []

    finally:
        delete_unsave_university_test_user()


def test_unsave_university_for_unknown_user(
    client: TestClient,
) -> None:
    """An unknown user should return HTTP 404."""

    response = client.delete(
        (
            "/api/user-profiles/"
            "user_unsave_unknown_999"
            "/saved-universities/"
            f"{UNSAVE_PILOT_UNIVERSITY_ID}"
        )
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile 'user_unsave_unknown_999' "
            "was not found."
        )
    }


def test_unsave_unknown_university(
    client: TestClient,
) -> None:
    """An unknown university should return HTTP 404."""

    create_unsave_university_test_user(client)

    try:
        response = client.delete(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_UNIVERSITY_TEST_USER_ID}"
                "/saved-universities/"
                "uni_unknown_999"
            )
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": (
                "University 'uni_unknown_999' "
                "was not found."
            )
        }

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_UNIVERSITY_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        assert profile_response.json()[
            "saved_universities"
        ] == []

    finally:
        delete_unsave_university_test_user()

# ---------------------------------------------------------
# Save scholarship API tests
# ---------------------------------------------------------

SAVE_SCHOLARSHIP_TEST_USER_ID = (
    "user_api_save_scholarship_test_001"
)

PILOT_SCHOLARSHIP_ID = "sch_jp_001"


def delete_save_scholarship_test_user() -> None:
    """Remove the temporary save-scholarship test user."""

    database = get_database()

    database["user_profiles"].delete_many(
        {
            "user_id": (
                SAVE_SCHOLARSHIP_TEST_USER_ID
            )
        }
    )


def build_save_scholarship_test_profile() -> dict:
    """Return valid data for the temporary test user."""

    return {
        "user_id": SAVE_SCHOLARSHIP_TEST_USER_ID,
        "nationality": "Myanmar",
        "current_education_level": "Bachelor",
        "target_degree_level": "Master",
        "preferred_major": "Computer Science",
        "gpa": 3.4,
        "gpa_scale": 4.0,
        "ielts_score": 6.5,
        "toefl_score": None,
        "annual_budget": 700000,
        "budget_currency": "JPY",
        "preferred_countries": [
            "Japan"
        ],
        "scholarship_required": True,
        "preferred_funding_type": "Fully Funded",
        "preferred_intake": "October",
    }


def create_save_scholarship_test_user(
    client: TestClient,
) -> None:
    """Create a fresh profile for scholarship-save tests."""

    delete_save_scholarship_test_user()

    response = client.post(
        "/api/user-profiles",
        json=build_save_scholarship_test_profile(),
    )

    assert response.status_code == 201


def test_save_scholarship_successfully(
    client: TestClient,
) -> None:
    """A valid scholarship should be saved successfully."""

    create_save_scholarship_test_user(client)

    try:
        response = client.post(
            (
                f"/api/user-profiles/"
                f"{SAVE_SCHOLARSHIP_TEST_USER_ID}"
                f"/saved-scholarships/"
                f"{PILOT_SCHOLARSHIP_ID}"
            )
        )

        assert response.status_code == 200

        response_data = response.json()

        assert (
            response_data["message"]
            == "Scholarship saved successfully."
        )

        scholarship = response_data["scholarship"]

        assert (
            scholarship["scholarship_id"]
            == PILOT_SCHOLARSHIP_ID
        )

        assert response_data["saved_scholarships"] == [
            PILOT_SCHOLARSHIP_ID
        ]

    finally:
        delete_save_scholarship_test_user()


def test_saved_scholarship_is_stored_in_profile(
    client: TestClient,
) -> None:
    """The scholarship ID should persist in MongoDB."""

    create_save_scholarship_test_user(client)

    try:
        save_response = client.post(
            (
                f"/api/user-profiles/"
                f"{SAVE_SCHOLARSHIP_TEST_USER_ID}"
                f"/saved-scholarships/"
                f"{PILOT_SCHOLARSHIP_ID}"
            )
        )

        assert save_response.status_code == 200

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{SAVE_SCHOLARSHIP_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        profile = profile_response.json()

        assert profile["saved_scholarships"] == [
            PILOT_SCHOLARSHIP_ID
        ]

        # Other runtime fields must remain unchanged.
        assert profile["saved_universities"] == []
        assert profile["recommendation_history"] == []

        # Important profile data must remain unchanged.
        assert profile["nationality"] == "Myanmar"

        assert (
            profile["preferred_major"]
            == "Computer Science"
        )

        assert profile["annual_budget"] == 700000

    finally:
        delete_save_scholarship_test_user()


def test_save_same_scholarship_without_duplicate(
    client: TestClient,
) -> None:
    """Saving the same scholarship twice must not duplicate it."""

    create_save_scholarship_test_user(client)

    try:
        endpoint = (
            f"/api/user-profiles/"
            f"{SAVE_SCHOLARSHIP_TEST_USER_ID}"
            f"/saved-scholarships/"
            f"{PILOT_SCHOLARSHIP_ID}"
        )

        first_response = client.post(endpoint)

        assert first_response.status_code == 200

        second_response = client.post(endpoint)

        assert second_response.status_code == 200

        second_data = second_response.json()

        assert (
            second_data["message"]
            == "Scholarship is already saved."
        )

        assert second_data["saved_scholarships"] == [
            PILOT_SCHOLARSHIP_ID
        ]

        assert (
            second_data["saved_scholarships"].count(
                PILOT_SCHOLARSHIP_ID
            )
            == 1
        )

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{SAVE_SCHOLARSHIP_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        saved_scholarships = profile_response.json()[
            "saved_scholarships"
        ]

        assert saved_scholarships == [
            PILOT_SCHOLARSHIP_ID
        ]

        assert (
            saved_scholarships.count(
                PILOT_SCHOLARSHIP_ID
            )
            == 1
        )

    finally:
        delete_save_scholarship_test_user()


def test_save_scholarship_for_unknown_user(
    client: TestClient,
) -> None:
    """An unknown user should return HTTP 404."""

    response = client.post(
        (
            "/api/user-profiles/"
            "user_save_scholarship_unknown_999"
            "/saved-scholarships/"
            f"{PILOT_SCHOLARSHIP_ID}"
        )
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile "
            "'user_save_scholarship_unknown_999' "
            "was not found."
        )
    }


def test_save_unknown_scholarship(
    client: TestClient,
) -> None:
    """An unknown scholarship should not be saved."""

    create_save_scholarship_test_user(client)

    try:
        response = client.post(
            (
                f"/api/user-profiles/"
                f"{SAVE_SCHOLARSHIP_TEST_USER_ID}"
                "/saved-scholarships/"
                "sch_unknown_999"
            )
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": (
                "Scholarship 'sch_unknown_999' "
                "was not found."
            )
        }

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{SAVE_SCHOLARSHIP_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        profile = profile_response.json()

        assert profile["saved_scholarships"] == []

    finally:
        delete_save_scholarship_test_user()

# ---------------------------------------------------------
# Unsave scholarship API tests
# ---------------------------------------------------------

UNSAVE_SCHOLARSHIP_TEST_USER_ID = (
    "user_api_unsave_scholarship_test_001"
)

UNSAVE_PILOT_SCHOLARSHIP_ID = "sch_jp_001"


def delete_unsave_scholarship_test_user() -> None:
    """Remove the temporary unsave-scholarship test user."""

    database = get_database()

    database["user_profiles"].delete_many(
        {
            "user_id": (
                UNSAVE_SCHOLARSHIP_TEST_USER_ID
            )
        }
    )


def build_unsave_scholarship_test_profile() -> dict:
    """Return valid data for the temporary test profile."""

    return {
        "user_id": UNSAVE_SCHOLARSHIP_TEST_USER_ID,
        "nationality": "Myanmar",
        "current_education_level": "Bachelor",
        "target_degree_level": "Master",
        "preferred_major": "Computer Science",
        "gpa": 3.4,
        "gpa_scale": 4.0,
        "ielts_score": 6.5,
        "toefl_score": None,
        "annual_budget": 700000,
        "budget_currency": "JPY",
        "preferred_countries": [
            "Japan"
        ],
        "scholarship_required": True,
        "preferred_funding_type": "Fully Funded",
        "preferred_intake": "October",
    }


def create_unsave_scholarship_test_user(
    client: TestClient,
) -> None:
    """Create a fresh profile for unsave-scholarship tests."""

    delete_unsave_scholarship_test_user()

    response = client.post(
        "/api/user-profiles",
        json=build_unsave_scholarship_test_profile(),
    )

    assert response.status_code == 201


def save_pilot_scholarship_for_unsave_test(
    client: TestClient,
) -> None:
    """Save the pilot scholarship before removing it."""

    response = client.post(
        (
            f"/api/user-profiles/"
            f"{UNSAVE_SCHOLARSHIP_TEST_USER_ID}"
            f"/saved-scholarships/"
            f"{UNSAVE_PILOT_SCHOLARSHIP_ID}"
        )
    )

    assert response.status_code == 200


def test_unsave_scholarship_successfully(
    client: TestClient,
) -> None:
    """A saved scholarship should be removed successfully."""

    create_unsave_scholarship_test_user(client)

    try:
        save_pilot_scholarship_for_unsave_test(client)

        response = client.delete(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_SCHOLARSHIP_TEST_USER_ID}"
                f"/saved-scholarships/"
                f"{UNSAVE_PILOT_SCHOLARSHIP_ID}"
            )
        )

        assert response.status_code == 200

        response_data = response.json()

        assert (
            response_data["message"]
            == (
                "Scholarship removed from saved list "
                "successfully."
            )
        )

        scholarship = response_data["scholarship"]

        assert (
            scholarship["scholarship_id"]
            == UNSAVE_PILOT_SCHOLARSHIP_ID
        )

        assert response_data["saved_scholarships"] == []

    finally:
        delete_unsave_scholarship_test_user()


def test_unsaved_scholarship_is_removed_from_profile(
    client: TestClient,
) -> None:
    """The scholarship ID should disappear from MongoDB."""

    create_unsave_scholarship_test_user(client)

    try:
        save_pilot_scholarship_for_unsave_test(client)

        delete_response = client.delete(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_SCHOLARSHIP_TEST_USER_ID}"
                f"/saved-scholarships/"
                f"{UNSAVE_PILOT_SCHOLARSHIP_ID}"
            )
        )

        assert delete_response.status_code == 200

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_SCHOLARSHIP_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        profile = profile_response.json()

        assert profile["saved_scholarships"] == []

        # Other runtime fields should remain unchanged.
        assert profile["saved_universities"] == []
        assert profile["recommendation_history"] == []

        # Important profile information must remain unchanged.
        assert profile["nationality"] == "Myanmar"

        assert (
            profile["preferred_major"]
            == "Computer Science"
        )

        assert profile["annual_budget"] == 700000

    finally:
        delete_unsave_scholarship_test_user()


def test_unsave_scholarship_that_is_not_saved(
    client: TestClient,
) -> None:
    """
    Removing an unsaved scholarship should return safely
    without creating an error.
    """

    create_unsave_scholarship_test_user(client)

    try:
        response = client.delete(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_SCHOLARSHIP_TEST_USER_ID}"
                f"/saved-scholarships/"
                f"{UNSAVE_PILOT_SCHOLARSHIP_ID}"
            )
        )

        assert response.status_code == 200

        response_data = response.json()

        assert (
            response_data["message"]
            == "Scholarship is not currently saved."
        )

        assert response_data["saved_scholarships"] == []

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_SCHOLARSHIP_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        assert profile_response.json()[
            "saved_scholarships"
        ] == []

    finally:
        delete_unsave_scholarship_test_user()


def test_unsave_scholarship_for_unknown_user(
    client: TestClient,
) -> None:
    """An unknown user should return HTTP 404."""

    response = client.delete(
        (
            "/api/user-profiles/"
            "user_unsave_scholarship_unknown_999"
            "/saved-scholarships/"
            f"{UNSAVE_PILOT_SCHOLARSHIP_ID}"
        )
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile "
            "'user_unsave_scholarship_unknown_999' "
            "was not found."
        )
    }


def test_unsave_unknown_scholarship(
    client: TestClient,
) -> None:
    """An unknown scholarship should return HTTP 404."""

    create_unsave_scholarship_test_user(client)

    try:
        response = client.delete(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_SCHOLARSHIP_TEST_USER_ID}"
                "/saved-scholarships/"
                "sch_unknown_999"
            )
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": (
                "Scholarship 'sch_unknown_999' "
                "was not found."
            )
        }

        profile_response = client.get(
            (
                f"/api/user-profiles/"
                f"{UNSAVE_SCHOLARSHIP_TEST_USER_ID}"
            )
        )

        assert profile_response.status_code == 200

        assert profile_response.json()[
            "saved_scholarships"
        ] == []

    finally:
        delete_unsave_scholarship_test_user()

# ---------------------------------------------------------
# Saved opportunities detail API tests
# ---------------------------------------------------------

SAVED_OPPORTUNITIES_TEST_USER_ID = (
    "user_api_saved_opportunities_test_001"
)

SAVED_OPPORTUNITIES_UNIVERSITY_ID = "uni_jp_001"
SAVED_OPPORTUNITIES_SCHOLARSHIP_ID = "sch_jp_001"


def delete_saved_opportunities_test_user() -> None:
    """Remove the temporary saved-opportunities test user."""

    database = get_database()

    database["user_profiles"].delete_many(
        {
            "user_id": (
                SAVED_OPPORTUNITIES_TEST_USER_ID
            )
        }
    )


def build_saved_opportunities_test_profile() -> dict:
    """Return valid data for the temporary test profile."""

    return {
        "user_id": SAVED_OPPORTUNITIES_TEST_USER_ID,
        "nationality": "Myanmar",
        "current_education_level": "Bachelor",
        "target_degree_level": "Master",
        "preferred_major": "Computer Science",
        "gpa": 3.4,
        "gpa_scale": 4.0,
        "ielts_score": 6.5,
        "toefl_score": None,
        "annual_budget": 700000,
        "budget_currency": "JPY",
        "preferred_countries": [
            "Japan"
        ],
        "scholarship_required": True,
        "preferred_funding_type": "Fully Funded",
        "preferred_intake": "October",
    }


def create_saved_opportunities_test_user(
    client: TestClient,
) -> None:
    """Create a fresh temporary profile."""

    delete_saved_opportunities_test_user()

    response = client.post(
        "/api/user-profiles",
        json=build_saved_opportunities_test_profile(),
    )

    assert response.status_code == 201


def save_university_for_saved_opportunities_test(
    client: TestClient,
) -> None:
    """Save the pilot university for the temporary user."""

    response = client.post(
        (
            f"/api/user-profiles/"
            f"{SAVED_OPPORTUNITIES_TEST_USER_ID}"
            f"/saved-universities/"
            f"{SAVED_OPPORTUNITIES_UNIVERSITY_ID}"
        )
    )

    assert response.status_code == 200


def save_scholarship_for_saved_opportunities_test(
    client: TestClient,
) -> None:
    """Save the pilot scholarship for the temporary user."""

    response = client.post(
        (
            f"/api/user-profiles/"
            f"{SAVED_OPPORTUNITIES_TEST_USER_ID}"
            f"/saved-scholarships/"
            f"{SAVED_OPPORTUNITIES_SCHOLARSHIP_ID}"
        )
    )

    assert response.status_code == 200


def get_saved_opportunities_test_endpoint() -> str:
    """Return the saved-opportunities endpoint."""

    return (
        f"/api/user-profiles/"
        f"{SAVED_OPPORTUNITIES_TEST_USER_ID}"
        "/saved-opportunities"
    )


def test_get_saved_opportunities_with_both_types(
    client: TestClient,
) -> None:
    """
    Saved university and scholarship details should both
    be returned.
    """

    create_saved_opportunities_test_user(client)

    try:
        save_university_for_saved_opportunities_test(client)
        save_scholarship_for_saved_opportunities_test(client)

        response = client.get(
            get_saved_opportunities_test_endpoint()
        )

        assert response.status_code == 200

        response_data = response.json()

        assert (
            response_data["user_id"]
            == SAVED_OPPORTUNITIES_TEST_USER_ID
        )

        assert response_data["saved_university_count"] == 1
        assert response_data["saved_scholarship_count"] == 1

        assert len(response_data["saved_universities"]) == 1
        assert len(response_data["saved_scholarships"]) == 1

        university = response_data["saved_universities"][0]

        assert (
            university["university_id"]
            == SAVED_OPPORTUNITIES_UNIVERSITY_ID
        )

        assert (
            university["university_name"]
            == "The University of Tokyo"
        )

        assert university["country_id"] == "country_jp"
        assert university["city"] == "Tokyo"
        assert university["university_type"] == "Public"
        assert university["established_year"] == 1877

        assert university["degrees_offered"] == [
            "Bachelor",
            "Master",
            "PhD",
        ]

        assert university["scholarship_available"] is True

        scholarship = response_data[
            "saved_scholarships"
        ][0]

        assert (
            scholarship["scholarship_id"]
            == SAVED_OPPORTUNITIES_SCHOLARSHIP_ID
        )

        assert scholarship["country_id"] == "country_jp"

        assert (
            scholarship["university_id"]
            == SAVED_OPPORTUNITIES_UNIVERSITY_ID
        )

        assert scholarship["funding_type"] == "Fully Funded"

        assert scholarship["degree_levels"] == [
            "Master",
            "PhD",
        ]

    finally:
        delete_saved_opportunities_test_user()


def test_get_saved_opportunities_with_empty_lists(
    client: TestClient,
) -> None:
    """A new user should receive two empty saved lists."""

    create_saved_opportunities_test_user(client)

    try:
        response = client.get(
            get_saved_opportunities_test_endpoint()
        )

        assert response.status_code == 200

        response_data = response.json()

        assert response_data["saved_university_count"] == 0
        assert response_data["saved_scholarship_count"] == 0
        assert response_data["saved_universities"] == []
        assert response_data["saved_scholarships"] == []

    finally:
        delete_saved_opportunities_test_user()


def test_get_saved_opportunities_with_university_only(
    client: TestClient,
) -> None:
    """A user may have only a saved university."""

    create_saved_opportunities_test_user(client)

    try:
        save_university_for_saved_opportunities_test(client)

        response = client.get(
            get_saved_opportunities_test_endpoint()
        )

        assert response.status_code == 200

        response_data = response.json()

        assert response_data["saved_university_count"] == 1
        assert response_data["saved_scholarship_count"] == 0

        assert response_data["saved_universities"][0][
            "university_id"
        ] == SAVED_OPPORTUNITIES_UNIVERSITY_ID

        assert response_data["saved_scholarships"] == []

    finally:
        delete_saved_opportunities_test_user()


def test_get_saved_opportunities_with_scholarship_only(
    client: TestClient,
) -> None:
    """A user may have only a saved scholarship."""

    create_saved_opportunities_test_user(client)

    try:
        save_scholarship_for_saved_opportunities_test(client)

        response = client.get(
            get_saved_opportunities_test_endpoint()
        )

        assert response.status_code == 200

        response_data = response.json()

        assert response_data["saved_university_count"] == 0
        assert response_data["saved_scholarship_count"] == 1

        assert response_data["saved_universities"] == []

        assert response_data["saved_scholarships"][0][
            "scholarship_id"
        ] == SAVED_OPPORTUNITIES_SCHOLARSHIP_ID

    finally:
        delete_saved_opportunities_test_user()


def test_get_saved_opportunities_for_unknown_user(
    client: TestClient,
) -> None:
    """An unknown user should return HTTP 404."""

    response = client.get(
        (
            "/api/user-profiles/"
            "user_saved_opportunities_unknown_999"
            "/saved-opportunities"
        )
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "User profile "
            "'user_saved_opportunities_unknown_999' "
            "was not found."
        )
    }

