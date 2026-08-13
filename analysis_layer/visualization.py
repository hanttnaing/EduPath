from __future__ import annotations

import csv
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from pymongo import MongoClient
    from pymongo.server_api import ServerApi
except ImportError:
    MongoClient = None
    ServerApi = None


# ============================================================
# EduPath - Step 151.3 Data Visualization Layer
# ============================================================
#
# Purpose:
#   Convert descriptive analysis results into presentation-ready
#   charts for the EduPath Data Analysis project.
#
# Primary input:
#   data/analysis/151_2_descriptive_analysis.json
#
# Fallback:
#   Read MongoDB data in READ-ONLY mode if required.
#
# MongoDB records modified:
#   NO
#
# ============================================================


# ------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
CHART_DIR = ANALYSIS_DIR / "charts"
PLANNING_DIR = PROJECT_ROOT / "planning"

INPUT_JSON = ANALYSIS_DIR / "151_2_descriptive_analysis.json"

OUTPUT_JSON = ANALYSIS_DIR / "151_3_visualization_summary.json"
OUTPUT_CSV = PLANNING_DIR / "36_visualization_manifest.csv"

CHART_DIR.mkdir(parents=True, exist_ok=True)
PLANNING_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# OUTPUT CHART PATHS
# ------------------------------------------------------------

DEGREE_CHART = CHART_DIR / "151_3_01_program_degree_distribution.png"
TUITION_CHART = CHART_DIR / "151_3_02_annual_tuition_distribution.png"
UNIVERSITY_CHART = CHART_DIR / "151_3_03_programs_by_university.png"
DATASET_CHART = CHART_DIR / "151_3_04_dataset_composition.png"


# ------------------------------------------------------------
# GENERAL HELPERS
# ------------------------------------------------------------

def separator(character: str = "=", width: int = 92) -> None:
    print(character * width)


def safe_number(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default

    if isinstance(value, bool):
        return float(value)

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if not text:
        return default

    text = (
        text.replace(",", "")
        .replace("JPY", "")
        .replace("%", "")
        .strip()
    )

    try:
        return float(text)
    except ValueError:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    return int(round(safe_number(value, default)))


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def get_first_existing(
    dictionary: dict[str, Any],
    keys: list[str],
    default: Any = None,
) -> Any:
    for key in keys:
        if key in dictionary:
            return dictionary[key]

    return default


def recursively_find_key(
    data: Any,
    candidate_keys: set[str],
) -> Any:
    """
    Search nested JSON for the first matching key.
    """

    if isinstance(data, dict):
        for key, value in data.items():
            if key in candidate_keys:
                return value

        for value in data.values():
            result = recursively_find_key(value, candidate_keys)

            if result is not None:
                return result

    elif isinstance(data, list):
        for item in data:
            result = recursively_find_key(item, candidate_keys)

            if result is not None:
                return result

    return None


# ------------------------------------------------------------
# LOAD STEP 151.2 JSON
# ------------------------------------------------------------

def load_descriptive_analysis_json() -> dict[str, Any] | None:
    if not INPUT_JSON.exists():
        return None

    try:
        with INPUT_JSON.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return None

        return data

    except (json.JSONDecodeError, OSError):
        return None


# ------------------------------------------------------------
# NORMALIZE DISTRIBUTION STRUCTURES
# ------------------------------------------------------------

def normalize_distribution(
    raw_data: Any,
) -> dict[str, int]:
    """
    Supports several JSON forms:

    {
        "Master": 32,
        "PhD": 3
    }

    {
        "Master": {
            "count": 32,
            "percentage": 88.89
        }
    }

    [
        {
            "label": "Master",
            "count": 32
        }
    ]
    """

    result: dict[str, int] = {}

    if raw_data is None:
        return result

    if isinstance(raw_data, dict):

        for key, value in raw_data.items():

            label = normalize_text(key)

            if isinstance(value, dict):

                count = get_first_existing(
                    value,
                    [
                        "count",
                        "program_count",
                        "total",
                        "records",
                        "frequency",
                        "value",
                    ],
                    0,
                )

                count = safe_int(count)

            else:
                count = safe_int(value)

            if label and count >= 0:
                result[label] = count

        return result

    if isinstance(raw_data, list):

        for row in raw_data:

            if not isinstance(row, dict):
                continue

            label = get_first_existing(
                row,
                [
                    "label",
                    "name",
                    "degree",
                    "degree_level",
                    "university",
                    "university_name",
                    "tuition",
                    "tuition_fee",
                    "value",
                    "category",
                ],
            )

            count = get_first_existing(
                row,
                [
                    "count",
                    "program_count",
                    "total",
                    "records",
                    "frequency",
                ],
                0,
            )

            label = normalize_text(label)
            count = safe_int(count)

            if label:
                result[label] = count

    return result


# ------------------------------------------------------------
# EXTRACT ANALYSIS DATA FROM JSON
# ------------------------------------------------------------

def extract_dataset_counts(
    data: dict[str, Any],
) -> dict[str, int]:

    raw = recursively_find_key(
        data,
        {
            "dataset_counts",
            "record_counts",
            "counts",
            "dataset_size",
        },
    )

    result = {
        "Countries": 0,
        "Universities": 0,
        "Programs": 0,
        "Scholarships": 0,
    }

    if isinstance(raw, dict):

        mapping = {
            "Countries": [
                "countries",
                "country_count",
                "total_countries",
            ],
            "Universities": [
                "universities",
                "university_count",
                "total_universities",
            ],
            "Programs": [
                "programs",
                "program_count",
                "total_programs",
            ],
            "Scholarships": [
                "scholarships",
                "scholarship_count",
                "total_scholarships",
            ],
        }

        for output_key, possible_keys in mapping.items():

            value = get_first_existing(
                raw,
                possible_keys,
            )

            if value is not None:
                result[output_key] = safe_int(value)

    # Try direct recursive search if necessary.

    if result["Countries"] == 0:
        value = recursively_find_key(
            data,
            {
                "country_count",
                "total_countries",
            },
        )

        if value is not None:
            result["Countries"] = safe_int(value)

    if result["Universities"] == 0:
        value = recursively_find_key(
            data,
            {
                "university_count",
                "total_universities",
            },
        )

        if value is not None:
            result["Universities"] = safe_int(value)

    if result["Programs"] == 0:
        value = recursively_find_key(
            data,
            {
                "program_count",
                "total_programs",
            },
        )

        if value is not None:
            result["Programs"] = safe_int(value)

    if result["Scholarships"] == 0:
        value = recursively_find_key(
            data,
            {
                "scholarship_count",
                "total_scholarships",
            },
        )

        if value is not None:
            result["Scholarships"] = safe_int(value)

    return result


def extract_degree_distribution(
    data: dict[str, Any],
) -> dict[str, int]:

    raw = recursively_find_key(
        data,
        {
            "program_degree_distribution",
            "degree_distribution",
            "programs_by_degree",
            "degree_level_distribution",
        },
    )

    result = normalize_distribution(raw)

    clean_result: dict[str, int] = {}

    for key, value in result.items():
        degree = key.strip()

        if degree.lower() == "master":
            degree = "Master"

        elif degree.lower() in {"phd", "ph.d", "doctor", "doctoral"}:
            degree = "PhD"

        elif degree.lower() in {"bachelor", "undergraduate"}:
            degree = "Bachelor"

        clean_result[degree] = value

    return clean_result


def extract_tuition_distribution(
    data: dict[str, Any],
) -> dict[int, int]:

    raw = recursively_find_key(
        data,
        {
            "tuition_distribution",
            "program_tuition_distribution",
            "annual_tuition_distribution",
        },
    )

    normalized = normalize_distribution(raw)

    result: dict[int, int] = {}

    for tuition_label, count in normalized.items():

        tuition_value = safe_int(tuition_label)

        if tuition_value > 0:
            result[tuition_value] = count

    return result


def extract_programs_by_university(
    data: dict[str, Any],
) -> dict[str, int]:

    raw = recursively_find_key(
        data,
        {
            "programs_by_university",
            "university_program_distribution",
            "program_distribution_by_university",
        },
    )

    return normalize_distribution(raw)


# ------------------------------------------------------------
# MONGODB FALLBACK
# ------------------------------------------------------------

def load_mongodb_fallback() -> dict[str, Any]:
    """
    Used only when some data cannot be extracted from
    Step 151.2 JSON.

    MongoDB is read-only in this script.
    """

    if load_dotenv is not None:
        load_dotenv(PROJECT_ROOT / ".env")

    if MongoClient is None:
        raise RuntimeError(
            "Step 151.2 JSON does not contain enough data and "
            "pymongo is unavailable for fallback."
        )

    mongodb_uri = (
        os.getenv("MONGODB_URI")
        or os.getenv("MONGO_URI")
        or os.getenv("MONGODB_URL")
    )

    database_name = (
        os.getenv("MONGODB_DATABASE")
        or os.getenv("MONGO_DATABASE")
        or os.getenv("DATABASE_NAME")
        or "edupath_db"
    )

    if not mongodb_uri:
        raise RuntimeError(
            "MongoDB fallback was required, but MONGODB_URI "
            "was not found in the .env file."
        )

    print()
    print(
        "Some Step 151.2 visualization data could not be "
        "read from JSON."
    )
    print("Using MongoDB READ-ONLY fallback...")

    client_kwargs: dict[str, Any] = {
        "serverSelectionTimeoutMS": 10000,
    }

    if ServerApi is not None:
        client_kwargs["server_api"] = ServerApi("1")

    client = MongoClient(
        mongodb_uri,
        **client_kwargs,
    )

    try:
        client.admin.command("ping")

        database = client[database_name]

        countries_collection = database["countries"]
        universities_collection = database["universities"]
        programs_collection = database["programs"]
        scholarships_collection = database["scholarships"]

        countries_count = countries_collection.count_documents({})
        universities_count = universities_collection.count_documents({})
        programs_count = programs_collection.count_documents({})
        scholarships_count = scholarships_collection.count_documents({})

        programs = list(
            programs_collection.find(
                {},
                {
                    "_id": 0,
                    "degree_level": 1,
                    "tuition_fee": 1,
                    "university_id": 1,
                },
            )
        )

        universities = list(
            universities_collection.find(
                {},
                {
                    "_id": 0,
                    "university_id": 1,
                    "university_name": 1,
                    "name": 1,
                },
            )
        )

        degree_counter: Counter[str] = Counter()
        tuition_counter: Counter[int] = Counter()
        university_counter: Counter[str] = Counter()

        university_name_map: dict[str, str] = {}

        for university in universities:

            university_id = normalize_text(
                university.get("university_id")
            )

            university_name = normalize_text(
                university.get("university_name")
                or university.get("name")
            )

            if university_id:
                university_name_map[university_id] = (
                    university_name or university_id
                )

        for program in programs:

            degree = normalize_text(
                program.get("degree_level")
            )

            if degree:
                degree_counter[degree] += 1

            tuition = safe_int(
                program.get("tuition_fee")
            )

            if tuition > 0:
                tuition_counter[tuition] += 1

            university_id = normalize_text(
                program.get("university_id")
            )

            university_name = university_name_map.get(
                university_id,
                university_id or "Unknown University",
            )

            university_counter[university_name] += 1

        return {
            "dataset_counts": {
                "Countries": countries_count,
                "Universities": universities_count,
                "Programs": programs_count,
                "Scholarships": scholarships_count,
            },
            "degree_distribution": dict(degree_counter),
            "tuition_distribution": dict(tuition_counter),
            "programs_by_university": dict(university_counter),
        }

    finally:
        client.close()


# ------------------------------------------------------------
# PREPARE VISUALIZATION DATA
# ------------------------------------------------------------

def prepare_visualization_data() -> dict[str, Any]:

    source_json = load_descriptive_analysis_json()

    dataset_counts: dict[str, int] = {}
    degree_distribution: dict[str, int] = {}
    tuition_distribution: dict[int, int] = {}
    programs_by_university: dict[str, int] = {}

    source_type = "Step 151.2 descriptive analysis JSON"

    if source_json:

        dataset_counts = extract_dataset_counts(source_json)
        degree_distribution = extract_degree_distribution(source_json)
        tuition_distribution = extract_tuition_distribution(source_json)
        programs_by_university = extract_programs_by_university(source_json)

    fallback_required = (
        not dataset_counts
        or not degree_distribution
        or not tuition_distribution
        or not programs_by_university
        or dataset_counts.get("Programs", 0) == 0
    )

    if fallback_required:

        fallback = load_mongodb_fallback()

        source_type = (
            "Step 151.2 JSON with MongoDB read-only fallback"
        )

        if (
            not dataset_counts
            or dataset_counts.get("Programs", 0) == 0
        ):
            dataset_counts = fallback["dataset_counts"]

        if not degree_distribution:
            degree_distribution = fallback[
                "degree_distribution"
            ]

        if not tuition_distribution:
            tuition_distribution = fallback[
                "tuition_distribution"
            ]

        if not programs_by_university:
            programs_by_university = fallback[
                "programs_by_university"
            ]

    return {
        "source": source_type,
        "dataset_counts": dataset_counts,
        "degree_distribution": degree_distribution,
        "tuition_distribution": tuition_distribution,
        "programs_by_university": programs_by_university,
    }


# ------------------------------------------------------------
# MATPLOTLIB HELPERS
# ------------------------------------------------------------

def apply_chart_defaults() -> None:
    plt.rcParams.update(
        {
            "figure.figsize": (10, 6),
            "figure.dpi": 120,
            "savefig.dpi": 200,
            "font.size": 11,
            "axes.titlesize": 16,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )


def add_vertical_bar_labels(
    axes: Any,
    bars: Any,
) -> None:

    for bar in bars:

        height = bar.get_height()

        axes.annotate(
            f"{int(height)}",
            xy=(
                bar.get_x() + bar.get_width() / 2,
                height,
            ),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )


# ------------------------------------------------------------
# CHART 1 - PROGRAM DEGREE DISTRIBUTION
# ------------------------------------------------------------

def create_degree_distribution_chart(
    distribution: dict[str, int],
) -> None:

    preferred_order = [
        "Master",
        "PhD",
        "Bachelor",
    ]

    labels = [
        label
        for label in preferred_order
        if label in distribution
    ]

    remaining = sorted(
        [
            label
            for label in distribution
            if label not in preferred_order
        ]
    )

    labels.extend(remaining)

    values = [
        distribution[label]
        for label in labels
    ]

    total = sum(values)

    figure, axes = plt.subplots(
        figsize=(9, 6)
    )

    bars = axes.bar(
        labels,
        values,
    )

    axes.set_title(
        "Program Degree Distribution"
    )

    axes.set_xlabel(
        "Degree Level"
    )

    axes.set_ylabel(
        "Number of Programs"
    )

    axes.set_ylim(
        0,
        max(values) * 1.18 if values else 1,
    )

    add_vertical_bar_labels(
        axes,
        bars,
    )

    if total > 0:

        for bar, value in zip(
            bars,
            values,
        ):
            percentage = (
                value / total
            ) * 100

            axes.text(
                bar.get_x()
                + bar.get_width() / 2,
                value * 0.5,
                f"{percentage:.1f}%",
                ha="center",
                va="center",
                fontsize=10,
            )

    axes.grid(
        axis="y",
        alpha=0.25,
    )

    figure.tight_layout()

    figure.savefig(
        DEGREE_CHART,
        bbox_inches="tight",
    )

    plt.close(figure)


# ------------------------------------------------------------
# CHART 2 - ANNUAL TUITION DISTRIBUTION
# ------------------------------------------------------------

def create_tuition_distribution_chart(
    distribution: dict[int, int],
) -> None:

    sorted_items = sorted(
        distribution.items(),
        key=lambda item: item[0],
    )

    tuition_values = [
        item[0]
        for item in sorted_items
    ]

    counts = [
        item[1]
        for item in sorted_items
    ]

    labels = [
        f"{value:,}"
        for value in tuition_values
    ]

    figure, axes = plt.subplots(
        figsize=(11, 6)
    )

    bars = axes.bar(
        labels,
        counts,
    )

    axes.set_title(
        "Annual Tuition Distribution"
    )

    axes.set_xlabel(
        "Annual Tuition (JPY)"
    )

    axes.set_ylabel(
        "Number of Programs"
    )

    axes.set_ylim(
        0,
        max(counts) * 1.18 if counts else 1,
    )

    axes.tick_params(
        axis="x",
        rotation=30,
    )

    add_vertical_bar_labels(
        axes,
        bars,
    )

    axes.grid(
        axis="y",
        alpha=0.25,
    )

    figure.tight_layout()

    figure.savefig(
        TUITION_CHART,
        bbox_inches="tight",
    )

    plt.close(figure)


# ------------------------------------------------------------
# CHART 3 - PROGRAMS BY UNIVERSITY
# ------------------------------------------------------------

def create_programs_by_university_chart(
    distribution: dict[str, int],
) -> None:

    sorted_items = sorted(
        distribution.items(),
        key=lambda item: (
            item[1],
            item[0].lower(),
        ),
    )

    universities = [
        item[0]
        for item in sorted_items
    ]

    counts = [
        item[1]
        for item in sorted_items
    ]

    chart_height = max(
        6.5,
        len(universities) * 0.43,
    )

    figure, axes = plt.subplots(
        figsize=(11, chart_height)
    )

    bars = axes.barh(
        universities,
        counts,
    )

    axes.set_title(
        "Programs by University"
    )

    axes.set_xlabel(
        "Number of Programs"
    )

    axes.set_ylabel(
        "University"
    )

    axes.set_xlim(
        0,
        max(counts) * 1.22 if counts else 1,
    )

    for bar in bars:

        width = bar.get_width()

        axes.text(
            width + 0.04,
            bar.get_y()
            + bar.get_height() / 2,
            f"{int(width)}",
            va="center",
            fontsize=10,
        )

    axes.grid(
        axis="x",
        alpha=0.25,
    )

    figure.tight_layout()

    figure.savefig(
        UNIVERSITY_CHART,
        bbox_inches="tight",
    )

    plt.close(figure)


# ------------------------------------------------------------
# CHART 4 - DATASET COMPOSITION
# ------------------------------------------------------------

def create_dataset_composition_chart(
    counts: dict[str, int],
) -> None:

    preferred_order = [
        "Countries",
        "Universities",
        "Programs",
        "Scholarships",
    ]

    labels = [
        label
        for label in preferred_order
        if label in counts
    ]

    values = [
        safe_int(
            counts[label]
        )
        for label in labels
    ]

    figure, axes = plt.subplots(
        figsize=(9, 6)
    )

    bars = axes.bar(
        labels,
        values,
    )

    axes.set_title(
        "EduPath Dataset Composition"
    )

    axes.set_xlabel(
        "Dataset Entity"
    )

    axes.set_ylabel(
        "Record Count"
    )

    axes.set_ylim(
        0,
        max(values) * 1.18 if values else 1,
    )

    add_vertical_bar_labels(
        axes,
        bars,
    )

    axes.grid(
        axis="y",
        alpha=0.25,
    )

    figure.tight_layout()

    figure.savefig(
        DATASET_CHART,
        bbox_inches="tight",
    )

    plt.close(figure)


# ------------------------------------------------------------
# SAVE VISUALIZATION SUMMARY
# ------------------------------------------------------------

def save_summary_json(
    visualization_data: dict[str, Any],
) -> None:

    payload = {
        "step": "151.3",
        "title": "Data Visualization Layer",
        "status": "COMPLETED",
        "source": visualization_data["source"],
        "charts": [
            {
                "chart_id": "151_3_01",
                "title": "Program Degree Distribution",
                "file": str(DEGREE_CHART),
                "purpose": (
                    "Compare the number and percentage of "
                    "programs by degree level."
                ),
            },
            {
                "chart_id": "151_3_02",
                "title": "Annual Tuition Distribution",
                "file": str(TUITION_CHART),
                "purpose": (
                    "Show how verified annual tuition values "
                    "are distributed across current programs."
                ),
            },
            {
                "chart_id": "151_3_03",
                "title": "Programs by University",
                "file": str(UNIVERSITY_CHART),
                "purpose": (
                    "Compare current EduPath program coverage "
                    "across universities."
                ),
            },
            {
                "chart_id": "151_3_04",
                "title": "Dataset Composition",
                "file": str(DATASET_CHART),
                "purpose": (
                    "Summarize the current number of countries, "
                    "universities, programs and scholarships."
                ),
            },
        ],
        "analysis_scope_note": (
            "Visualizations describe only the records currently "
            "included in the EduPath dataset. They should not yet "
            "be generalized to all universities, programs or "
            "scholarships in Japan."
        ),
        "mongodb_records_modified": False,
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )


def save_manifest_csv() -> None:

    rows = [
        {
            "chart_id": "151_3_01",
            "chart_title": "Program Degree Distribution",
            "chart_file": str(DEGREE_CHART),
            "analysis_type": "Descriptive",
        },
        {
            "chart_id": "151_3_02",
            "chart_title": "Annual Tuition Distribution",
            "chart_file": str(TUITION_CHART),
            "analysis_type": "Descriptive",
        },
        {
            "chart_id": "151_3_03",
            "chart_title": "Programs by University",
            "chart_file": str(UNIVERSITY_CHART),
            "analysis_type": "Descriptive",
        },
        {
            "chart_id": "151_3_04",
            "chart_title": "Dataset Composition",
            "chart_file": str(DATASET_CHART),
            "analysis_type": "Descriptive",
        },
    ]

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "chart_id",
                "chart_title",
                "chart_file",
                "analysis_type",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)


# ------------------------------------------------------------
# PRINT VISUALIZATION DATA
# ------------------------------------------------------------

def print_input_summary(
    data: dict[str, Any],
) -> None:

    print()
    separator()
    print("VISUALIZATION INPUT SUMMARY")
    separator()

    print(
        f"Source              : {data['source']}"
    )

    print()

    print("Dataset counts:")

    for key, value in data[
        "dataset_counts"
    ].items():
        print(
            f"  {key:<14}: {value}"
        )

    print()

    print("Degree distribution:")

    for key, value in data[
        "degree_distribution"
    ].items():
        print(
            f"  {key:<14}: {value}"
        )

    print()

    print("Tuition distribution:")

    for tuition, count in sorted(
        data["tuition_distribution"].items()
    ):
        print(
            f"  {tuition:>10,} JPY : "
            f"{count} program(s)"
        )

    print()

    print("Programs by university:")

    for university, count in sorted(
        data["programs_by_university"].items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    ):
        print(
            f"  {university:<40} "
            f"{count} program(s)"
        )


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main() -> None:

    separator()
    print(
        "EduPath - Step 151.3 Data Visualization Layer"
    )
    separator()

    print()
    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print(
        "Loading descriptive analysis results..."
    )

    apply_chart_defaults()

    visualization_data = (
        prepare_visualization_data()
    )

    print_input_summary(
        visualization_data
    )

    print()
    separator()
    print("GENERATING CHARTS")
    separator()

    create_degree_distribution_chart(
        visualization_data[
            "degree_distribution"
        ]
    )

    print(
        "[1/4] Program Degree Distribution "
        "........ CREATED"
    )

    create_tuition_distribution_chart(
        visualization_data[
            "tuition_distribution"
        ]
    )

    print(
        "[2/4] Annual Tuition Distribution "
        "........ CREATED"
    )

    create_programs_by_university_chart(
        visualization_data[
            "programs_by_university"
        ]
    )

    print(
        "[3/4] Programs by University "
        "............. CREATED"
    )

    create_dataset_composition_chart(
        visualization_data[
            "dataset_counts"
        ]
    )

    print(
        "[4/4] Dataset Composition "
        "................ CREATED"
    )

    save_summary_json(
        visualization_data
    )

    save_manifest_csv()

    print()
    separator()
    print(
        "STEP 151.3 DATA VISUALIZATION: COMPLETED"
    )
    separator()

    print()

    print("Charts created:")

    print(
        f"1. {DEGREE_CHART}"
    )

    print(
        f"2. {TUITION_CHART}"
    )

    print(
        f"3. {UNIVERSITY_CHART}"
    )

    print(
        f"4. {DATASET_CHART}"
    )

    print()

    print(
        f"Visualization JSON report: {OUTPUT_JSON}"
    )

    print(
        f"Visualization CSV manifest: {OUTPUT_CSV}"
    )

    print()

    print(
        "MongoDB records modified: NO"
    )

    print()

    print(
        "Important analysis scope:"
    )

    print(
        "- Charts describe the current EduPath dataset."
    )

    print(
        "- Results must not yet be generalized to all "
        "Japanese universities or programs."
    )

    print(
        "- Tuition figures use the verified tuition data "
        "currently stored for the collected programs."
    )

    separator()


if __name__ == "__main__":
    main()