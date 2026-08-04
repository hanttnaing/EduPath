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