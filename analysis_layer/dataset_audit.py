from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# =========================================================
# PROJECT ROOT / IMPORT PATH FIX
# =========================================================
#
# dataset_audit.py lives inside:
#
# EduPath/
# └── analysis_layer/
#     └── dataset_audit.py
#
# Therefore parents[1] = EduPath project root.
#
# This section fixes:
#
# ModuleNotFoundError: No module named 'scripts'
#
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

SCRIPTS_DIRECTORY = (
    PROJECT_ROOT
    / "scripts"
)

# Add project root to Python import path.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

# Also add scripts directory directly.
#
# This is useful because some existing EduPath scripts
# import sibling Python files directly.
if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS_DIRECTORY),
    )


# =========================================================
# IMPORT EXISTING EDUPATH DATABASE CONFIGURATION
# =========================================================
#
# We intentionally reuse the already validated configuration
# from the locked recommendation engine.
#
# No MongoDB records will be modified by this audit.
# =========================================================

try:

    from recommend_scholarships_final import (
        MONGODB_URI,
        DATABASE_NAME,
    )

except ImportError as error:

    raise RuntimeError(
        "Could not import the EduPath MongoDB configuration "
        "from scripts/recommend_scholarships_final.py.\n"
        f"Expected scripts directory:\n{SCRIPTS_DIRECTORY}"
    ) from error


# =========================================================
# OUTPUT PATHS
# =========================================================

ANALYSIS_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "analysis"
)

PLANNING_DIRECTORY = (
    PROJECT_ROOT
    / "planning"
)

OUTPUT_JSON = (
    ANALYSIS_OUTPUT_DIRECTORY
    / "151_1_dataset_audit.json"
)

OUTPUT_CSV = (
    PLANNING_DIRECTORY
    / "33_data_analysis_dataset_audit.csv"
)


# =========================================================
# EXPECTED ANALYTICAL FIELDS
# =========================================================
#
# Some earlier EduPath dataset versions may use slightly
# different names for the same concept.
#
# Therefore each logical field can have multiple aliases.
#
# Example:
#
# university_name
# could also appear as:
# name
#
# =========================================================

FIELD_DEFINITIONS: dict[
    str,
    dict[str, list[str]],
] = {

    # =====================================================
    # COUNTRIES
    # =====================================================

    "countries": {

        "country_id": [
            "country_id",
        ],

        "country_name": [
            "country_name",
            "name",
        ],

        "region": [
            "region",
            "subregion",
        ],
    },

    # =====================================================
    # UNIVERSITIES
    # =====================================================

    "universities": {

        "university_id": [
            "university_id",
        ],

        "university_name": [
            "university_name",
            "name",
        ],

        "country_id": [
            "country_id",
        ],

        "city": [
            "city",
            "location_city",
        ],

        "institution_type": [
            "institution_type",
            "university_type",
            "type",
        ],

        "ranking": [
            "ranking",
            "qs_rank",
            "world_rank",
            "global_rank",
        ],

        "official_website": [
            "official_website",
            "website",
            "university_url",
        ],

        "last_verified_at": [
            "last_verified_at",
        ],
    },

    # =====================================================
    # PROGRAMS
    # =====================================================

    "programs": {

        "program_id": [
            "program_id",
        ],

        "university_id": [
            "university_id",
        ],

        "program_name": [
            "program_name",
            "name",
        ],

        "field_of_study": [
            "field_of_study",
            "field",
        ],

        "degree_level": [
            "degree_level",
            "degree",
        ],

        "duration_years": [
            "duration_years",
            "duration",
        ],

        "study_mode": [
            "study_mode",
        ],

        "language_of_instruction": [
            "language_of_instruction",
            "language",
        ],

        "tuition_fee": [
            "tuition_fee",
            "annual_tuition",
        ],

        "tuition_currency": [
            "tuition_currency",
            "currency",
        ],

        "tuition_period": [
            "tuition_period",
        ],

        "tuition_academic_year": [
            "tuition_academic_year",
        ],

        "tuition_source_url": [
            "tuition_source_url",
        ],

        "minimum_gpa": [
            "minimum_gpa",
        ],

        "gpa_scale": [
            "gpa_scale",
        ],

        "ielts_requirement": [
            "ielts_requirement",
            "minimum_ielts",
        ],

        "toefl_requirement": [
            "toefl_requirement",
            "minimum_toefl",
        ],

        "intake": [
            "intake",
            "intakes",
        ],

        "application_deadline": [
            "application_deadline",
        ],

        "program_url": [
            "program_url",
            "official_website",
        ],

        "last_verified_at": [
            "last_verified_at",
        ],

        "freshness_status": [
            "freshness_status",
        ],
    },

    # =====================================================
    # SCHOLARSHIPS
    # =====================================================

    "scholarships": {

        "scholarship_id": [
            "scholarship_id",
        ],

        "scholarship_name": [
            "scholarship_name",
            "name",
        ],

        "country_id": [
            "country_id",
        ],

        "host_university_id": [
            "host_university_id",
        ],

        "provider_name": [
            "provider_name",
            "provider",
        ],

        "degree_levels": [
            "degree_levels",
            "degree_level",
        ],

        "funding_type": [
            "funding_type",
            "funding",
        ],

        "scholarship_status": [
            "scholarship_status",
            "status",
        ],

        "fields_of_study": [
            "fields_of_study",
            "field_of_study",
        ],

        "eligible_nationalities": [
            "eligible_nationalities",
        ],

        "minimum_gpa": [
            "minimum_gpa",
        ],

        "gpa_scale": [
            "gpa_scale",
        ],

        "ielts_requirement": [
            "ielts_requirement",
            "minimum_ielts",
        ],

        "toefl_requirement": [
            "toefl_requirement",
            "minimum_toefl",
        ],

        "age_limit": [
            "age_limit",
        ],

        "application_cycle": [
            "application_cycle",
        ],

        "application_opening_date": [
            "application_opening_date",
        ],

        "application_deadline": [
            "application_deadline",
        ],

        "official_website": [
            "official_website",
            "scholarship_url",
        ],

        "last_verified_at": [
            "last_verified_at",
        ],

        "freshness_status": [
            "freshness_status",
        ],
    },
}


# =========================================================
# GENERIC HELPERS
# =========================================================

def is_present(
    value: Any,
) -> bool:
    """
    Return True when a field contains meaningful information.
    """

    if value is None:
        return False

    if isinstance(
        value,
        str,
    ):
        return bool(
            value.strip()
        )

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
            dict,
        ),
    ):
        return len(
            value
        ) > 0

    return True


def resolve_value(
    document: dict[str, Any],
    aliases: list[str],
) -> Any:
    """
    Return the first meaningful value found among field aliases.
    """

    for alias in aliases:

        value = document.get(
            alias
        )

        if is_present(
            value
        ):
            return value

    return None


def normalise_text(
    value: Any,
) -> str:
    """
    Convert values to clean display text.
    """

    if value is None:
        return "Unknown"

    text = str(
        value
    ).strip()

    if not text:
        return "Unknown"

    return text


def flatten_distribution_value(
    value: Any,
) -> list[str]:
    """
    Convert both scalar and list values into a list
    suitable for distribution analysis.
    """

    if value is None:

        return [
            "Unknown",
        ]

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):

        values = [
            normalise_text(
                item
            )

            for item
            in value

            if is_present(
                item
            )
        ]

        if values:
            return values

        return [
            "Unknown",
        ]

    return [
        normalise_text(
            value
        ),
    ]


def calculate_percentage(
    numerator: int,
    denominator: int,
) -> float:
    """
    Safe percentage calculation.
    """

    if denominator == 0:
        return 0.0

    return round(
        (
            numerator
            / denominator
        )
        * 100,
        2,
    )


# =========================================================
# LOAD COLLECTION
# =========================================================

def load_collection(
    database: Any,
    collection_name: str,
) -> list[dict[str, Any]]:
    """
    Load collection in read-only mode.
    """

    documents = list(
        database[
            collection_name
        ].find(
            {},
            {
                "_id": 0,
            },
        )
    )

    return documents


# =========================================================
# FIELD COMPLETENESS ANALYSIS
# =========================================================

def analyse_field_completeness(
    collection_name: str,
    documents: list[dict[str, Any]],
) -> dict[str, Any]:

    definitions = (
        FIELD_DEFINITIONS[
            collection_name
        ]
    )

    total_records = len(
        documents
    )

    fields: dict[
        str,
        dict[str, Any],
    ] = {}

    completeness_percentages: list[
        float
    ] = []

    for (
        logical_field,
        aliases,
    ) in definitions.items():

        present_count = 0

        for document in documents:

            value = resolve_value(
                document,
                aliases,
            )

            if is_present(
                value
            ):
                present_count += 1

        missing_count = (
            total_records
            - present_count
        )

        completeness = (
            calculate_percentage(
                present_count,
                total_records,
            )
        )

        completeness_percentages.append(
            completeness
        )

        fields[
            logical_field
        ] = {

            "aliases":
                aliases,

            "present":
                present_count,

            "missing":
                missing_count,

            "completeness_percent":
                completeness,
        }

    if completeness_percentages:

        average_completeness = round(
            sum(
                completeness_percentages
            )
            / len(
                completeness_percentages
            ),
            2,
        )

    else:

        average_completeness = 0.0

    return {

        "total_records":
            total_records,

        "average_field_completeness_percent":
            average_completeness,

        "fields":
            fields,
    }


# =========================================================
# DUPLICATE ID ANALYSIS
# =========================================================

def find_duplicate_ids(
    documents: list[dict[str, Any]],
    id_aliases: list[str],
) -> list[str]:

    ids: list[str] = []

    for document in documents:

        value = resolve_value(
            document,
            id_aliases,
        )

        if is_present(
            value
        ):

            ids.append(
                str(
                    value
                )
            )

    counter = Counter(
        ids
    )

    duplicates = [
        value

        for (
            value,
            count,
        ) in counter.items()

        if count > 1
    ]

    return sorted(
        duplicates
    )


# =========================================================
# RELATIONSHIP INTEGRITY
# =========================================================

def analyse_relationships(
    countries: list[dict[str, Any]],
    universities: list[dict[str, Any]],
    programs: list[dict[str, Any]],
    scholarships: list[dict[str, Any]],
) -> dict[str, Any]:

    country_ids: set[str] = set()

    for country in countries:

        country_id = resolve_value(
            country,
            FIELD_DEFINITIONS[
                "countries"
            ][
                "country_id"
            ],
        )

        if is_present(
            country_id
        ):

            country_ids.add(
                str(
                    country_id
                )
            )

    university_ids: set[str] = set()

    for university in universities:

        university_id = resolve_value(
            university,
            FIELD_DEFINITIONS[
                "universities"
            ][
                "university_id"
            ],
        )

        if is_present(
            university_id
        ):

            university_ids.add(
                str(
                    university_id
                )
            )

    # -----------------------------------------------------
    # University → Country relationship
    # -----------------------------------------------------

    orphan_universities: list[str] = []

    for university in universities:

        university_id = resolve_value(
            university,
            FIELD_DEFINITIONS[
                "universities"
            ][
                "university_id"
            ],
        )

        country_id = resolve_value(
            university,
            FIELD_DEFINITIONS[
                "universities"
            ][
                "country_id"
            ],
        )

        if (
            is_present(
                country_id
            )
            and str(
                country_id
            )
            not in country_ids
        ):

            orphan_universities.append(
                str(
                    university_id
                )
            )

    # -----------------------------------------------------
    # Program → University relationship
    # -----------------------------------------------------

    orphan_programs: list[str] = []

    for program in programs:

        program_id = resolve_value(
            program,
            FIELD_DEFINITIONS[
                "programs"
            ][
                "program_id"
            ],
        )

        university_id = resolve_value(
            program,
            FIELD_DEFINITIONS[
                "programs"
            ][
                "university_id"
            ],
        )

        if (
            not is_present(
                university_id
            )
            or str(
                university_id
            )
            not in university_ids
        ):

            orphan_programs.append(
                str(
                    program_id
                )
            )

    # -----------------------------------------------------
    # Scholarship → Country
    # Scholarship → Host University
    # -----------------------------------------------------

    scholarship_country_errors: list[str] = []

    scholarship_host_university_errors: list[str] = []

    for scholarship in scholarships:

        scholarship_id = resolve_value(
            scholarship,
            FIELD_DEFINITIONS[
                "scholarships"
            ][
                "scholarship_id"
            ],
        )

        country_id = resolve_value(
            scholarship,
            FIELD_DEFINITIONS[
                "scholarships"
            ][
                "country_id"
            ],
        )

        if (
            is_present(
                country_id
            )
            and str(
                country_id
            )
            not in country_ids
        ):

            scholarship_country_errors.append(
                str(
                    scholarship_id
                )
            )

        host_university_id = resolve_value(
            scholarship,
            FIELD_DEFINITIONS[
                "scholarships"
            ][
                "host_university_id"
            ],
        )

        # Some scholarships are government-level and may
        # legitimately have no host university.
        #
        # Therefore NULL host university is not an error.
        if (
            is_present(
                host_university_id
            )
            and str(
                host_university_id
            )
            not in university_ids
        ):

            scholarship_host_university_errors.append(
                str(
                    scholarship_id
                )
            )

    total_relationship_errors = (

        len(
            orphan_universities
        )

        + len(
            orphan_programs
        )

        + len(
            scholarship_country_errors
        )

        + len(
            scholarship_host_university_errors
        )
    )

    status = (
        "PASS"
        if total_relationship_errors == 0
        else "REVIEW_REQUIRED"
    )

    return {

        "status":
            status,

        "total_relationship_errors":
            total_relationship_errors,

        "orphan_university_records":
            orphan_universities,

        "orphan_program_records":
            orphan_programs,

        "invalid_scholarship_country_records":
            scholarship_country_errors,

        "invalid_scholarship_host_university_records":
            scholarship_host_university_errors,
    }


# =========================================================
# DISTRIBUTION ANALYSIS
# =========================================================

def build_distribution(
    documents: list[dict[str, Any]],
    aliases: list[str],
) -> dict[str, int]:

    counter: Counter[str] = Counter()

    for document in documents:

        value = resolve_value(
            document,
            aliases,
        )

        values = flatten_distribution_value(
            value
        )

        for item in values:

            counter[
                item
            ] += 1

    sorted_items = sorted(
        counter.items(),
        key=lambda item: (
            -item[1],
            item[0].lower(),
        ),
    )

    return dict(
        sorted_items
    )


# =========================================================
# PROGRAM TUITION FOUNDATION AUDIT
# =========================================================

def analyse_program_tuition(
    programs: list[dict[str, Any]],
) -> dict[str, Any]:

    tuition_values: list[
        float
    ] = []

    missing_tuition = 0

    invalid_tuition = 0

    for program in programs:

        value = resolve_value(
            program,
            FIELD_DEFINITIONS[
                "programs"
            ][
                "tuition_fee"
            ],
        )

        if not is_present(
            value
        ):

            missing_tuition += 1

            continue

        try:

            numeric_value = float(
                value
            )

            tuition_values.append(
                numeric_value
            )

        except (
            TypeError,
            ValueError,
        ):

            invalid_tuition += 1

    distribution_counter = Counter(
        tuition_values
    )

    tuition_distribution: dict[
        str,
        int,
    ] = {}

    for (
        value,
        count,
    ) in sorted(
        distribution_counter.items()
    ):

        if float(
            value
        ).is_integer():

            display_value = str(
                int(
                    value
                )
            )

        else:

            display_value = str(
                value
            )

        tuition_distribution[
            display_value
        ] = count

    usable_tuition_count = len(
        tuition_values
    )

    return {

        "program_count":
            len(
                programs
            ),

        "tuition_available":
            usable_tuition_count,

        "tuition_missing":
            missing_tuition,

        "tuition_invalid":
            invalid_tuition,

        "tuition_availability_percent":
            calculate_percentage(
                usable_tuition_count,
                len(
                    programs
                ),
            ),

        "distinct_tuition_values":
            len(
                distribution_counter
            ),

        "tuition_value_distribution":
            tuition_distribution,
    }


# =========================================================
# ANALYSIS READINESS ASSESSMENT
# =========================================================

def build_analysis_readiness(
    counts: dict[str, int],
    completeness: dict[str, Any],
    relationships: dict[str, Any],
) -> dict[str, Any]:

    positive_findings: list[str] = []

    coverage_notes: list[str] = []

    program_degree_field = (
        completeness[
            "programs"
        ][
            "fields"
        ][
            "degree_level"
        ]
    )

    program_tuition_field = (
        completeness[
            "programs"
        ][
            "fields"
        ][
            "tuition_fee"
        ]
    )

    scholarship_field_information = (
        completeness[
            "scholarships"
        ][
            "fields"
        ][
            "fields_of_study"
        ]
    )

    scholarship_gpa = (
        completeness[
            "scholarships"
        ][
            "fields"
        ][
            "minimum_gpa"
        ]
    )

    scholarship_nationality = (
        completeness[
            "scholarships"
        ][
            "fields"
        ][
            "eligible_nationalities"
        ]
    )

    scholarship_ielts = (
        completeness[
            "scholarships"
        ][
            "fields"
        ][
            "ielts_requirement"
        ][
            "completeness_percent"
        ]
    )

    scholarship_toefl = (
        completeness[
            "scholarships"
        ][
            "fields"
        ][
            "toefl_requirement"
        ][
            "completeness_percent"
        ]
    )

    scholarship_english = max(
        scholarship_ielts,
        scholarship_toefl,
    )

    # =====================================================
    # POSITIVE FINDINGS
    # =====================================================

    if (
        program_degree_field[
            "completeness_percent"
        ]
        >= 90
    ):

        positive_findings.append(
            "Program degree-level data is sufficiently complete "
            "for degree-distribution analysis."
        )

    if (
        program_tuition_field[
            "completeness_percent"
        ]
        >= 90
    ):

        positive_findings.append(
            "Program tuition data is sufficiently complete "
            "for tuition analysis."
        )

    if (
        relationships[
            "total_relationship_errors"
        ]
        == 0
    ):

        positive_findings.append(
            "Dataset relationships passed integrity checks."
        )

    # =====================================================
    # COVERAGE NOTES
    #
    # We intentionally use 'coverage notes' instead of
    # calling these project weaknesses.
    # =====================================================

    if counts[
        "universities"
    ] < 30:

        coverage_notes.append(
            "The current university collection is a curated "
            "prototype sample. Findings currently describe "
            "the EduPath dataset rather than all Japanese universities."
        )

    if counts[
        "programs"
    ] < 100:

        coverage_notes.append(
            "The current program analysis represents the programs "
            "currently included in EduPath and should not yet be "
            "generalised to every university program in Japan."
        )

    if counts[
        "scholarships"
    ] < 30:

        coverage_notes.append(
            "Scholarship findings are currently dataset-level findings "
            "because the scholarship collection is still targeted."
        )

    # =====================================================
    # STRUCTURED DATA COVERAGE
    # =====================================================

    if (
        scholarship_field_information[
            "completeness_percent"
        ]
        < 70
    ):

        coverage_notes.append(
            "Structured scholarship fields-of-study coverage is still "
            "developing. Missing field information is therefore treated "
            "as uncertainty rather than as a confirmed mismatch."
        )

    if (
        scholarship_gpa[
            "completeness_percent"
        ]
        < 70
    ):

        coverage_notes.append(
            "GPA requirement coverage is not complete for every scholarship; "
            "eligibility confidence accounts for this uncertainty."
        )

    if scholarship_english < 70:

        coverage_notes.append(
            "English requirement coverage is not complete for every "
            "scholarship; unavailable requirements remain UNKNOWN."
        )

    if (
        scholarship_nationality[
            "completeness_percent"
        ]
        < 70
    ):

        coverage_notes.append(
            "Nationality eligibility information is not available for "
            "every scholarship record."
        )

    # =====================================================
    # READINESS DECISION
    # =====================================================

    core_analysis_ready = (

        program_degree_field[
            "completeness_percent"
        ]
        >= 80

        and

        program_tuition_field[
            "completeness_percent"
        ]
        >= 80

        and

        relationships[
            "total_relationship_errors"
        ]
        == 0
    )

    if core_analysis_ready:

        status = (
            "READY_FOR_ANALYSIS"
        )

    else:

        status = (
            "REVIEW_REQUIRED"
        )

    return {

        "status":
            status,

        "positive_findings":
            positive_findings,

        "coverage_notes":
            coverage_notes,
    }


# =========================================================
# CSV OUTPUT
# =========================================================

def write_completeness_csv(
    completeness: dict[str, Any],
) -> None:

    PLANNING_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [

        "collection",
        "field",
        "records",
        "present",
        "missing",
        "completeness_percent",
    ]

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for (
            collection_name,
            analysis,
        ) in completeness.items():

            total_records = (
                analysis[
                    "total_records"
                ]
            )

            for (
                field_name,
                field_result,
            ) in analysis[
                "fields"
            ].items():

                writer.writerow(
                    {

                        "collection":
                            collection_name,

                        "field":
                            field_name,

                        "records":
                            total_records,

                        "present":
                            field_result[
                                "present"
                            ],

                        "missing":
                            field_result[
                                "missing"
                            ],

                        "completeness_percent":
                            field_result[
                                "completeness_percent"
                            ],
                    }
                )


# =========================================================
# JSON OUTPUT
# =========================================================

def write_json_report(
    report: dict[str, Any],
) -> None:

    ANALYSIS_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


# =========================================================
# PRINT DISTRIBUTION HELPER
# =========================================================

def print_distribution(
    title: str,
    distribution: dict[str, int],
) -> None:

    print(
        title
    )

    print(
        "-" * 100
    )

    if not distribution:

        print(
            "No data available."
        )

        print()

        return

    for (
        value,
        count,
    ) in distribution.items():

        print(
            f"{value}: {count}"
        )

    print()


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print(
        "=" * 100
    )

    print(
        "EduPath - Step 151.1 "
        "Data Analysis Readiness & Quality Assessment"
    )

    print(
        "=" * 100
    )

    print()

    print(
        "Project root:"
    )

    print(
        PROJECT_ROOT
    )

    print()

    # =====================================================
    # CONFIG VALIDATION
    # =====================================================

    if not MONGODB_URI:

        raise RuntimeError(
            "MONGODB_URI is unavailable."
        )

    if not DATABASE_NAME:

        raise RuntimeError(
            "DATABASE_NAME is unavailable."
        )

    # =====================================================
    # CONNECT TO MONGODB
    # =====================================================

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi(
            "1"
        ),
        serverSelectionTimeoutMS=10000,
    )

    try:

        print(
            "Connecting to MongoDB Atlas..."
        )

        client.admin.command(
            "ping"
        )

        print(
            "MongoDB Atlas connection: SUCCESS"
        )

        print(
            "Database:",
            DATABASE_NAME,
        )

        print()

        database = client[
            DATABASE_NAME
        ]

        # =================================================
        # LOAD CURRENT DATASET
        # =================================================

        countries = load_collection(
            database,
            "countries",
        )

        universities = load_collection(
            database,
            "universities",
        )

        programs = load_collection(
            database,
            "programs",
        )

        scholarships = load_collection(
            database,
            "scholarships",
        )

        counts = {

            "countries":
                len(
                    countries
                ),

            "universities":
                len(
                    universities
                ),

            "programs":
                len(
                    programs
                ),

            "scholarships":
                len(
                    scholarships
                ),
        }

        # =================================================
        # DATASET COUNTS
        # =================================================

        print(
            "=" * 100
        )

        print(
            "DATASET COUNTS"
        )

        print(
            "=" * 100
        )

        for (
            collection_name,
            count,
        ) in counts.items():

            print(
                f"{collection_name.title():15}: "
                f"{count}"
            )

        print()

        # =================================================
        # COMPLETENESS ANALYSIS
        # =================================================

        completeness = {

            "countries":
                analyse_field_completeness(
                    "countries",
                    countries,
                ),

            "universities":
                analyse_field_completeness(
                    "universities",
                    universities,
                ),

            "programs":
                analyse_field_completeness(
                    "programs",
                    programs,
                ),

            "scholarships":
                analyse_field_completeness(
                    "scholarships",
                    scholarships,
                ),
        }

        print(
            "=" * 100
        )

        print(
            "AVERAGE FIELD COMPLETENESS"
        )

        print(
            "=" * 100
        )

        for (
            collection_name,
            result,
        ) in completeness.items():

            percentage = (
                result[
                    "average_field_completeness_percent"
                ]
            )

            print(
                f"{collection_name.title():15}: "
                f"{percentage:.2f}%"
            )

        print()

        # =================================================
        # DUPLICATE CHECK
        # =================================================

        duplicates = {

            "country_ids":
                find_duplicate_ids(
                    countries,
                    FIELD_DEFINITIONS[
                        "countries"
                    ][
                        "country_id"
                    ],
                ),

            "university_ids":
                find_duplicate_ids(
                    universities,
                    FIELD_DEFINITIONS[
                        "universities"
                    ][
                        "university_id"
                    ],
                ),

            "program_ids":
                find_duplicate_ids(
                    programs,
                    FIELD_DEFINITIONS[
                        "programs"
                    ][
                        "program_id"
                    ],
                ),

            "scholarship_ids":
                find_duplicate_ids(
                    scholarships,
                    FIELD_DEFINITIONS[
                        "scholarships"
                    ][
                        "scholarship_id"
                    ],
                ),
        }

        duplicate_count = sum(
            len(
                values
            )

            for values
            in duplicates.values()
        )

        print(
            "=" * 100
        )

        print(
            "DUPLICATE ID CHECK"
        )

        print(
            "=" * 100
        )

        print(
            "Duplicate IDs detected:",
            duplicate_count,
        )

        if duplicate_count > 0:

            for (
                key,
                values,
            ) in duplicates.items():

                if values:

                    print(
                        f"{key}:",
                        ", ".join(
                            values
                        ),
                    )

        print()

        # =================================================
        # RELATIONSHIP INTEGRITY
        # =================================================

        relationships = (
            analyse_relationships(
                countries=
                    countries,

                universities=
                    universities,

                programs=
                    programs,

                scholarships=
                    scholarships,
            )
        )

        print(
            "=" * 100
        )

        print(
            "RELATIONSHIP INTEGRITY"
        )

        print(
            "=" * 100
        )

        print(
            "Status:",
            relationships[
                "status"
            ],
        )

        print(
            "Relationship errors:",
            relationships[
                "total_relationship_errors"
            ],
        )

        print()

        # =================================================
        # FOUNDATION DISTRIBUTIONS
        # =================================================

        program_degree_distribution = (
            build_distribution(
                programs,
                FIELD_DEFINITIONS[
                    "programs"
                ][
                    "degree_level"
                ],
            )
        )

        program_field_distribution = (
            build_distribution(
                programs,
                FIELD_DEFINITIONS[
                    "programs"
                ][
                    "field_of_study"
                ],
            )
        )

        program_language_distribution = (
            build_distribution(
                programs,
                FIELD_DEFINITIONS[
                    "programs"
                ][
                    "language_of_instruction"
                ],
            )
        )

        scholarship_degree_distribution = (
            build_distribution(
                scholarships,
                FIELD_DEFINITIONS[
                    "scholarships"
                ][
                    "degree_levels"
                ],
            )
        )

        scholarship_funding_distribution = (
            build_distribution(
                scholarships,
                FIELD_DEFINITIONS[
                    "scholarships"
                ][
                    "funding_type"
                ],
            )
        )

        scholarship_status_distribution = (
            build_distribution(
                scholarships,
                FIELD_DEFINITIONS[
                    "scholarships"
                ][
                    "scholarship_status"
                ],
            )
        )

        print_distribution(
            "PROGRAM DEGREE DISTRIBUTION",
            program_degree_distribution,
        )

        print_distribution(
            "SCHOLARSHIP FUNDING DISTRIBUTION",
            scholarship_funding_distribution,
        )

        print_distribution(
            "SCHOLARSHIP STATUS DISTRIBUTION",
            scholarship_status_distribution,
        )

        # =================================================
        # TUITION READINESS
        # =================================================

        tuition_foundation = (
            analyse_program_tuition(
                programs
            )
        )

        print(
            "=" * 100
        )

        print(
            "PROGRAM TUITION READINESS"
        )

        print(
            "=" * 100
        )

        print(
            "Programs:",
            tuition_foundation[
                "program_count"
            ],
        )

        print(
            "Tuition available:",
            tuition_foundation[
                "tuition_available"
            ],
        )

        print(
            "Tuition missing:",
            tuition_foundation[
                "tuition_missing"
            ],
        )

        print(
            "Tuition invalid:",
            tuition_foundation[
                "tuition_invalid"
            ],
        )

        print(
            "Tuition availability:",
            (
                str(
                    tuition_foundation[
                        "tuition_availability_percent"
                    ]
                )
                + "%"
            ),
        )

        print(
            "Distinct tuition values:",
            tuition_foundation[
                "distinct_tuition_values"
            ],
        )

        print()

        print(
            "Tuition value distribution:"
        )

        for (
            tuition,
            count,
        ) in tuition_foundation[
            "tuition_value_distribution"
        ].items():

            print(
                f"  {tuition} JPY: "
                f"{count} program(s)"
            )

        print()

        # =================================================
        # ANALYSIS READINESS
        # =================================================

        readiness = (
            build_analysis_readiness(
                counts=
                    counts,

                completeness=
                    completeness,

                relationships=
                    relationships,
            )
        )

        print(
            "=" * 100
        )

        print(
            "ANALYSIS READINESS"
        )

        print(
            "=" * 100
        )

        print(
            "Status:",
            readiness[
                "status"
            ],
        )

        print()

        print(
            "Data quality findings:"
        )

        if readiness[
            "positive_findings"
        ]:

            for finding in readiness[
                "positive_findings"
            ]:

                print(
                    " +",
                    finding,
                )

        else:

            print(
                " + No major positive findings "
                "were automatically generated."
            )

        print()

        print(
            "Coverage notes:"
        )

        if readiness[
            "coverage_notes"
        ]:

            for note in readiness[
                "coverage_notes"
            ]:

                print(
                    " -",
                    note,
                )

        else:

            print(
                " - No major coverage notes."
            )

        print()

        # =================================================
        # FINAL ANALYSIS REPORT
        # =================================================

        report = {

            "project":
                "EduPath Analytics",

            "analysis_layer":
                True,

            "analysis_step":
                "151.1",

            "analysis_name":
                (
                    "Data Analysis Readiness "
                    "and Quality Assessment"
                ),

            "generated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "database":
                DATABASE_NAME,

            "database_modified":
                False,

            "dataset_counts":
                counts,

            "field_completeness":
                completeness,

            "duplicate_id_analysis":
                duplicates,

            "duplicate_id_count":
                duplicate_count,

            "relationship_integrity":
                relationships,

            "foundation_distributions": {

                "program_degree":
                    program_degree_distribution,

                "program_field":
                    program_field_distribution,

                "program_language":
                    program_language_distribution,

                "scholarship_degree":
                    scholarship_degree_distribution,

                "scholarship_funding":
                    scholarship_funding_distribution,

                "scholarship_status":
                    scholarship_status_distribution,
            },

            "tuition_foundation":
                tuition_foundation,

            "analysis_readiness":
                readiness,

            "scope_note":
                (
                    "Analytical results currently describe "
                    "the curated EduPath dataset. "
                    "The system architecture supports future "
                    "expansion to additional universities, "
                    "programs and scholarships."
                ),

            "methodology_note":
                (
                    "Missing data is measured explicitly "
                    "instead of silently replacing unknown values. "
                    "This supports transparent and confidence-aware "
                    "analysis."
                ),
        }

        # =================================================
        # WRITE OUTPUT
        # =================================================

        write_json_report(
            report
        )

        write_completeness_csv(
            completeness
        )

        # =================================================
        # FINAL SUMMARY
        # =================================================

        print(
            "=" * 100
        )

        print(
            "STEP 151.1 DATA ANALYSIS READINESS AUDIT: COMPLETED"
        )

        print(
            "=" * 100
        )

        print()

        print(
            "Analysis status:",
            readiness[
                "status"
            ],
        )

        print(
            "Duplicate IDs:",
            duplicate_count,
        )

        print(
            "Relationship errors:",
            relationships[
                "total_relationship_errors"
            ],
        )

        print(
            "Program tuition coverage:",
            (
                str(
                    tuition_foundation[
                        "tuition_availability_percent"
                    ]
                )
                + "%"
            ),
        )

        print()

        print(
            "JSON report:"
        )

        print(
            OUTPUT_JSON
        )

        print()

        print(
            "CSV report:"
        )

        print(
            OUTPUT_CSV
        )

        print()

        print(
            "MongoDB records modified: NO"
        )

        print(
            "=" * 100
        )

    except PyMongoError as error:

        raise RuntimeError(
            "MongoDB dataset audit failed."
        ) from error

    finally:

        client.close()

        print(
            "MongoDB connection closed safely."
        )


if __name__ == "__main__":
    main()