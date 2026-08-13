from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# =========================================================
# PROJECT PATH
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

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS_DIRECTORY),
    )


# =========================================================
# EDUPATH CONFIG
# =========================================================

from recommend_scholarships_final import (
    MONGODB_URI,
    DATABASE_NAME,
)


# =========================================================
# OUTPUT PATHS
# =========================================================

ANALYSIS_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "analysis"
)

PLANNING_DIRECTORY = (
    PROJECT_ROOT
    / "planning"
)

OUTPUT_JSON = (
    ANALYSIS_DIRECTORY
    / "151_1b_relationship_integrity_diagnostic.json"
)

OUTPUT_CSV = (
    PLANNING_DIRECTORY
    / "34_relationship_integrity_diagnostic.csv"
)


# =========================================================
# HELPERS
# =========================================================

def is_present(
    value: Any,
) -> bool:

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


def first_value(
    document: dict[str, Any],
    names: list[str],
) -> Any:

    for name in names:

        value = document.get(
            name
        )

        if is_present(
            value
        ):
            return value

    return None


def clean(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(
        value
    ).strip()


def load_collection(
    database: Any,
    collection_name: str,
) -> list[dict[str, Any]]:

    return list(
        database[
            collection_name
        ].find(
            {},
            {
                "_id": 0,
            },
        )
    )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print(
        "=" * 105
    )

    print(
        "EduPath - Step 151.1B "
        "Relationship Integrity Diagnosis"
    )

    print(
        "=" * 105
    )

    if not MONGODB_URI:

        raise RuntimeError(
            "MONGODB_URI is unavailable."
        )

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi(
            "1"
        ),
        serverSelectionTimeoutMS=10000,
    )

    try:

        print()
        print(
            "Connecting to MongoDB Atlas..."
        )

        client.admin.command(
            "ping"
        )

        print(
            "MongoDB Atlas connection: SUCCESS"
        )

        database = client[
            DATABASE_NAME
        ]

        # =================================================
        # LOAD COLLECTIONS
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

        print()
        print(
            "Records loaded:"
        )

        print(
            f"Countries     : {len(countries)}"
        )

        print(
            f"Universities  : {len(universities)}"
        )

        print(
            f"Programs      : {len(programs)}"
        )

        print(
            f"Scholarships  : {len(scholarships)}"
        )

        # =================================================
        # BUILD VALID ID SETS
        # =================================================

        country_ids = set()

        for country in countries:

            country_id = first_value(
                country,
                [
                    "country_id",
                ],
            )

            if is_present(
                country_id
            ):

                country_ids.add(
                    clean(
                        country_id
                    )
                )

        university_ids = set()

        for university in universities:

            university_id = first_value(
                university,
                [
                    "university_id",
                ],
            )

            if is_present(
                university_id
            ):

                university_ids.add(
                    clean(
                        university_id
                    )
                )

        # =================================================
        # DIAGNOSTIC ROWS
        # =================================================

        diagnostic_rows: list[
            dict[str, Any]
        ] = []

        category_counts = {
            "university_country":
                0,

            "program_university":
                0,

            "scholarship_country":
                0,

            "scholarship_host_university":
                0,
        }

        # =================================================
        # 1. UNIVERSITY → COUNTRY
        # =================================================

        for university in universities:

            university_id = first_value(
                university,
                [
                    "university_id",
                ],
            )

            university_name = first_value(
                university,
                [
                    "university_name",
                    "name",
                ],
            )

            country_id = first_value(
                university,
                [
                    "country_id",
                ],
            )

            if not is_present(
                country_id
            ):

                category_counts[
                    "university_country"
                ] += 1

                diagnostic_rows.append(
                    {
                        "relationship_type":
                            "University -> Country",

                        "record_type":
                            "university",

                        "record_id":
                            clean(
                                university_id
                            ),

                        "record_name":
                            clean(
                                university_name
                            ),

                        "reference_field":
                            "country_id",

                        "reference_value":
                            "",

                        "issue":
                            "Missing country_id",
                    }
                )

            elif clean(
                country_id
            ) not in country_ids:

                category_counts[
                    "university_country"
                ] += 1

                diagnostic_rows.append(
                    {
                        "relationship_type":
                            "University -> Country",

                        "record_type":
                            "university",

                        "record_id":
                            clean(
                                university_id
                            ),

                        "record_name":
                            clean(
                                university_name
                            ),

                        "reference_field":
                            "country_id",

                        "reference_value":
                            clean(
                                country_id
                            ),

                        "issue":
                            (
                                "country_id does not match "
                                "any countries record"
                            ),
                    }
                )

        # =================================================
        # 2. PROGRAM → UNIVERSITY
        # =================================================

        for program in programs:

            program_id = first_value(
                program,
                [
                    "program_id",
                ],
            )

            program_name = first_value(
                program,
                [
                    "program_name",
                    "name",
                ],
            )

            university_id = first_value(
                program,
                [
                    "university_id",
                ],
            )

            if not is_present(
                university_id
            ):

                category_counts[
                    "program_university"
                ] += 1

                diagnostic_rows.append(
                    {
                        "relationship_type":
                            "Program -> University",

                        "record_type":
                            "program",

                        "record_id":
                            clean(
                                program_id
                            ),

                        "record_name":
                            clean(
                                program_name
                            ),

                        "reference_field":
                            "university_id",

                        "reference_value":
                            "",

                        "issue":
                            "Missing university_id",
                    }
                )

            elif clean(
                university_id
            ) not in university_ids:

                category_counts[
                    "program_university"
                ] += 1

                diagnostic_rows.append(
                    {
                        "relationship_type":
                            "Program -> University",

                        "record_type":
                            "program",

                        "record_id":
                            clean(
                                program_id
                            ),

                        "record_name":
                            clean(
                                program_name
                            ),

                        "reference_field":
                            "university_id",

                        "reference_value":
                            clean(
                                university_id
                            ),

                        "issue":
                            (
                                "university_id does not match "
                                "any universities record"
                            ),
                    }
                )

        # =================================================
        # 3. SCHOLARSHIP → COUNTRY
        # =================================================

        for scholarship in scholarships:

            scholarship_id = first_value(
                scholarship,
                [
                    "scholarship_id",
                ],
            )

            scholarship_name = first_value(
                scholarship,
                [
                    "scholarship_name",
                    "name",
                ],
            )

            country_id = first_value(
                scholarship,
                [
                    "country_id",
                ],
            )

            # Missing country is also diagnostically useful.
            if not is_present(
                country_id
            ):

                category_counts[
                    "scholarship_country"
                ] += 1

                diagnostic_rows.append(
                    {
                        "relationship_type":
                            "Scholarship -> Country",

                        "record_type":
                            "scholarship",

                        "record_id":
                            clean(
                                scholarship_id
                            ),

                        "record_name":
                            clean(
                                scholarship_name
                            ),

                        "reference_field":
                            "country_id",

                        "reference_value":
                            "",

                        "issue":
                            "Missing country_id",
                    }
                )

            elif clean(
                country_id
            ) not in country_ids:

                category_counts[
                    "scholarship_country"
                ] += 1

                diagnostic_rows.append(
                    {
                        "relationship_type":
                            "Scholarship -> Country",

                        "record_type":
                            "scholarship",

                        "record_id":
                            clean(
                                scholarship_id
                            ),

                        "record_name":
                            clean(
                                scholarship_name
                            ),

                        "reference_field":
                            "country_id",

                        "reference_value":
                            clean(
                                country_id
                            ),

                        "issue":
                            (
                                "country_id does not match "
                                "any countries record"
                            ),
                    }
                )

        # =================================================
        # 4. SCHOLARSHIP → HOST UNIVERSITY
        #
        # NULL is allowed because national/government
        # scholarships do not always belong to one university.
        # =================================================

        for scholarship in scholarships:

            scholarship_id = first_value(
                scholarship,
                [
                    "scholarship_id",
                ],
            )

            scholarship_name = first_value(
                scholarship,
                [
                    "scholarship_name",
                    "name",
                ],
            )

            host_university_id = first_value(
                scholarship,
                [
                    "host_university_id",
                ],
            )

            if (
                is_present(
                    host_university_id
                )
                and clean(
                    host_university_id
                )
                not in university_ids
            ):

                category_counts[
                    "scholarship_host_university"
                ] += 1

                diagnostic_rows.append(
                    {
                        "relationship_type":
                            "Scholarship -> Host University",

                        "record_type":
                            "scholarship",

                        "record_id":
                            clean(
                                scholarship_id
                            ),

                        "record_name":
                            clean(
                                scholarship_name
                            ),

                        "reference_field":
                            "host_university_id",

                        "reference_value":
                            clean(
                                host_university_id
                            ),

                        "issue":
                            (
                                "host_university_id does not match "
                                "any universities record"
                            ),
                    }
                )

        # =================================================
        # SUMMARY
        # =================================================

        total_errors = len(
            diagnostic_rows
        )

        print()
        print(
            "=" * 105
        )

        print(
            "RELATIONSHIP DIAGNOSTIC SUMMARY"
        )

        print(
            "=" * 105
        )

        print(
            "University -> Country errors:",
            category_counts[
                "university_country"
            ],
        )

        print(
            "Program -> University errors:",
            category_counts[
                "program_university"
            ],
        )

        print(
            "Scholarship -> Country errors:",
            category_counts[
                "scholarship_country"
            ],
        )

        print(
            "Scholarship -> Host University errors:",
            category_counts[
                "scholarship_host_university"
            ],
        )

        print()

        print(
            "Total relationship issues:",
            total_errors,
        )

        print()

        # =================================================
        # PRINT ALL PROBLEM RECORDS
        # =================================================

        if diagnostic_rows:

            print(
                "=" * 105
            )

            print(
                "RECORDS REQUIRING RELATIONSHIP REVIEW"
            )

            print(
                "=" * 105
            )

            for index, row in enumerate(
                diagnostic_rows,
                start=1,
            ):

                print()

                print(
                    f"{index:02d}. "
                    f"{row['relationship_type']}"
                )

                print(
                    "Record ID      :",
                    row[
                        "record_id"
                    ],
                )

                print(
                    "Record Name    :",
                    row[
                        "record_name"
                    ],
                )

                print(
                    "Reference Field:",
                    row[
                        "reference_field"
                    ],
                )

                print(
                    "Reference Value:",
                    (
                        row[
                            "reference_value"
                        ]
                        or "(missing)"
                    ),
                )

                print(
                    "Issue          :",
                    row[
                        "issue"
                    ],
                )

        else:

            print(
                "No relationship problems detected."
            )

        # =================================================
        # SAVE CSV
        # =================================================

        PLANNING_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        with OUTPUT_CSV.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            fieldnames = [
                "relationship_type",
                "record_type",
                "record_id",
                "record_name",
                "reference_field",
                "reference_value",
                "issue",
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for row in diagnostic_rows:

                writer.writerow(
                    row
                )

        # =================================================
        # SAVE JSON
        # =================================================

        ANALYSIS_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = {
            "project":
                "EduPath Analytics",

            "analysis_step":
                "151.1B",

            "analysis_name":
                "Relationship Integrity Diagnosis",

            "generated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "database_modified":
                False,

            "dataset_counts": {
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
            },

            "relationship_summary":
                category_counts,

            "total_relationship_issues":
                total_errors,

            "problem_records":
                diagnostic_rows,
        }

        with OUTPUT_JSON.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                ensure_ascii=False,
                indent=2,
            )

        # =================================================
        # FINAL
        # =================================================

        print()
        print()

        print(
            "=" * 105
        )

        print(
            "STEP 151.1B RELATIONSHIP DIAGNOSIS: COMPLETED"
        )

        print(
            "=" * 105
        )

        print(
            "Total issues:",
            total_errors,
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
            "JSON report:"
        )

        print(
            OUTPUT_JSON
        )

        print()

        print(
            "MongoDB records modified: NO"
        )

        print(
            "=" * 105
        )

    except PyMongoError as error:

        raise RuntimeError(
            "MongoDB relationship diagnosis failed."
        ) from error

    finally:

        client.close()

        print(
            "MongoDB connection closed safely."
        )


if __name__ == "__main__":
    main()