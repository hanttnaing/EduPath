from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException


# =============================================================================
# EduPath
# Step 151.8 - Data Analysis Backend API Integration
#
# Purpose:
#   Expose the consolidated analysis dashboard dataset through FastAPI.
#
# Source:
#   data/analysis/analysis_dashboard.json
#
# IMPORTANT:
#   - Read-only API
#   - MongoDB is NOT modified
#   - Recommendation algorithm is NOT modified
# =============================================================================


# -----------------------------------------------------------------------------
# Router
# -----------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/analysis",
    tags=["Data Analysis"],
)


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"

DASHBOARD_FILE = ANALYSIS_DIR / "analysis_dashboard.json"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def load_dashboard_data() -> dict[str, Any]:
    """
    Load the latest consolidated dashboard JSON.

    The file is read on each request so analysis results can be regenerated
    without restarting the FastAPI application.
    """

    if not DASHBOARD_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "Analysis dashboard dataset is not available. "
                "Run Step 151.7 first."
            ),
        )

    try:
        with DASHBOARD_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis dashboard JSON is invalid."
            ),
        ) from error

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis dashboard file could not be read."
            ),
        ) from error

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis dashboard dataset has an invalid structure."
            ),
        )

    return data


def get_section(
    data: dict[str, Any],
    key: str,
    default: Any,
) -> Any:
    """
    Safely read a dashboard section.
    """

    value = data.get(key)

    if value is None:
        return default

    return value


# -----------------------------------------------------------------------------
# API Health
# -----------------------------------------------------------------------------

@router.get("/health")
def analysis_health() -> dict[str, Any]:
    """
    Check whether the analysis API and dashboard file are available.
    """

    exists = DASHBOARD_FILE.exists()

    return {
        "service": "EduPath Data Analysis API",
        "status": (
            "ready"
            if exists
            else "dashboard_file_missing"
        ),
        "dashboard_file_exists": exists,
        "dashboard_file": str(DASHBOARD_FILE),
        "mongodb_modified": False,
    }


# -----------------------------------------------------------------------------
# Complete Dashboard
# -----------------------------------------------------------------------------

@router.get("/dashboard")
def get_analysis_dashboard() -> dict[str, Any]:
    """
    Return the complete Step 151.7 analysis dashboard dataset.
    """

    return load_dashboard_data()


# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

@router.get("/summary")
def get_analysis_summary() -> dict[str, Any]:
    """
    Return high-level KPI and data-quality information.
    """

    data = load_dashboard_data()

    return {
        "title": data.get(
            "title",
            "EduPath Data Analysis Dashboard",
        ),
        "generated_at": data.get(
            "generated_at"
        ),
        "dataset_scope": get_section(
            data,
            "dataset_scope",
            {},
        ),
        "headline_kpis": get_section(
            data,
            "headline_kpis",
            [],
        ),
        "dataset_overview": get_section(
            data,
            "dataset_overview",
            {},
        ),
        "data_quality": get_section(
            data,
            "data_quality",
            {},
        ),
        "dashboard_metadata": get_section(
            data,
            "dashboard_metadata",
            {},
        ),
    }


# -----------------------------------------------------------------------------
# Programs Analysis
# -----------------------------------------------------------------------------

@router.get("/programs")
def get_program_analysis() -> dict[str, Any]:
    """
    Return program-level analytical statistics.
    """

    data = load_dashboard_data()

    return {
        "dataset_overview": get_section(
            data,
            "dataset_overview",
            {},
        ),
        "program_analysis": get_section(
            data,
            "program_analysis",
            {},
        ),
    }


# -----------------------------------------------------------------------------
# Tuition Analysis
# -----------------------------------------------------------------------------

@router.get("/tuition")
def get_tuition_analysis() -> dict[str, Any]:
    """
    Return tuition statistics, distribution and affordability segments.
    """

    data = load_dashboard_data()

    return {
        "tuition_analysis": get_section(
            data,
            "tuition_analysis",
            {},
        ),
        "scope": get_section(
            data,
            "dataset_scope",
            {},
        ),
    }


# -----------------------------------------------------------------------------
# Scholarship Analysis
# -----------------------------------------------------------------------------

@router.get("/scholarships")
def get_scholarship_analysis() -> dict[str, Any]:
    """
    Return scholarship dataset analysis.
    """

    data = load_dashboard_data()

    return {
        "scholarship_analysis": get_section(
            data,
            "scholarship_analysis",
            {},
        ),
        "scope": get_section(
            data,
            "dataset_scope",
            {},
        ),
    }


# -----------------------------------------------------------------------------
# Recommendation Algorithm Performance
# -----------------------------------------------------------------------------

@router.get("/algorithm")
def get_algorithm_performance() -> dict[str, Any]:
    """
    Return recommendation algorithm performance and validation results.
    """

    data = load_dashboard_data()

    algorithm = get_section(
        data,
        "algorithm_performance",
        {},
    )

    return {
        "algorithm_performance": algorithm,
        "interpretation_note": (
            "Functional validation represents scenario-based functional "
            "testing. It is not a supervised machine-learning accuracy claim."
        ),
    }


# -----------------------------------------------------------------------------
# Analytical Insights
# -----------------------------------------------------------------------------

@router.get("/insights")
def get_analytical_insights() -> dict[str, Any]:
    """
    Return generated evidence-based analytical insights.
    """

    data = load_dashboard_data()

    insights = get_section(
        data,
        "analytical_insights",
        [],
    )

    return {
        "insight_count": len(insights),
        "insights": insights,
    }


# -----------------------------------------------------------------------------
# Chart Registry
# -----------------------------------------------------------------------------

@router.get("/charts")
def get_chart_registry() -> dict[str, Any]:
    """
    Return metadata for charts generated during Step 151.3.
    """

    data = load_dashboard_data()

    charts = get_section(
        data,
        "charts",
        [],
    )

    return {
        "chart_count": len(charts),
        "charts": charts,
    }


# -----------------------------------------------------------------------------
# Data Quality
# -----------------------------------------------------------------------------

@router.get("/quality")
def get_data_quality() -> dict[str, Any]:
    """
    Return dataset quality and readiness information.
    """

    data = load_dashboard_data()

    return {
        "data_quality": get_section(
            data,
            "data_quality",
            {},
        ),
        "dataset_overview": get_section(
            data,
            "dataset_overview",
            {},
        ),
        "source_status": get_section(
            data,
            "source_status",
            {},
        ),
    }