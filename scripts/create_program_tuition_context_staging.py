from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


API_BASE_URL = "http://127.0.0.1:8000"

JAPAN_COUNTRY_ID = "country_jp"

PAGE_SIZE = 100


def get_json(
    path: str,
    params: dict | None = None,
) -> dict:
    url = f"{API_BASE_URL}{path}"

    if params:
        url = f"{url}?{urlencode(params)}"

    with urlopen(
        url,
        timeout=20,
    ) as response:
        return json.load(response)


def fetch_all(
    path: str,
    params: dict | None = None,
) -> list[dict]:
    items: list[dict] = []

    skip = 0

    while True:
        request_params = dict(params or {})

        request_params["skip"] = skip
        request_params["limit"] = PAGE_SIZE

        data = get_json(
            path,
            request_params,
        )

        batch = data.get("items", [])

        items.extend(batch)

        total = data.get(
            "total",
            len(items),
        )

        if (
            not batch
            or len(items) >= total
        ):
            break

        skip += PAGE_SIZE

    return items


def main() -> None:
    print("=" * 85)
    print(
        "EduPath - Create Japan Program "
        "Tuition Context Staging CSV"
    )
    print("=" * 85)

    # --------------------------------------------------
    # Load Japan universities
    # --------------------------------------------------

    universities = fetch_all(
        "/api/universities",
        {
            "country_id":
                JAPAN_COUNTRY_ID
        },
    )

    university_by_id = {
        university.get("university_id"):
            university.get("university_name")
        for university in universities
    }

    japan_university_ids = set(
        university_by_id.keys()
    )

    # --------------------------------------------------
    # Load programs
    # --------------------------------------------------

    programs = fetch_all(
        "/api/programs"
    )

    japan_programs = [
        program
        for program in programs
        if program.get("university_id")
        in japan_university_ids
    ]

    print()
    print(
        "Japan universities found:",
        len(universities),
    )

    print(
        "Japan programs found:",
        len(japan_programs),
    )

    if not japan_programs:
        raise RuntimeError(
            "No Japan programs found."
        )

    # --------------------------------------------------
    # Output path
    # --------------------------------------------------

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    output_file = (
        project_root
        / "planning"
        / "25_japan_program_tuition_context_staging.csv"
    )

    # --------------------------------------------------
    # CSV columns
    # --------------------------------------------------

    fieldnames = [
        "program_id",
        "university_id",
        "university_name",
        "program_name",
        "degree_level",

        "current_tuition_fee",
        "current_tuition_currency",
        "current_tuition_period",

        "tuition_academic_year",
        "tuition_student_scope",
        "tuition_source_url",
        "tuition_last_verified_at",
        "tuition_note",

        "current_program_url",
        "current_last_verified_at",
    ]

    # --------------------------------------------------
    # Write staging file
    # --------------------------------------------------

    sorted_programs = sorted(
        japan_programs,
        key=lambda program: (
            university_by_id.get(
                program.get("university_id"),
                "",
            ),
            program.get(
                "degree_level",
                "",
            ),
            program.get(
                "program_name",
                "",
            ),
        ),
    )

    with output_file.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for program in sorted_programs:
            university_id = (
                program.get(
                    "university_id"
                )
            )

            writer.writerow(
                {
                    "program_id":
                        program.get(
                            "program_id"
                        ),

                    "university_id":
                        university_id,

                    "university_name":
                        university_by_id.get(
                            university_id,
                            "",
                        ),

                    "program_name":
                        program.get(
                            "program_name"
                        ),

                    "degree_level":
                        program.get(
                            "degree_level"
                        ),

                    "current_tuition_fee":
                        program.get(
                            "tuition_fee"
                        ),

                    "current_tuition_currency":
                        program.get(
                            "tuition_currency"
                        ),

                    "current_tuition_period":
                        program.get(
                            "tuition_period"
                        ),

                    # Intentionally blank.
                    # We will fill these only
                    # after official verification.

                    "tuition_academic_year":
                        "",

                    "tuition_student_scope":
                        "",

                    "tuition_source_url":
                        "",

                    "tuition_last_verified_at":
                        "",

                    "tuition_note":
                        "",

                    "current_program_url":
                        program.get(
                            "program_url"
                        ),

                    "current_last_verified_at":
                        program.get(
                            "last_verified_at"
                        ),
                }
            )

    print()
    print(
        "Staging CSV created successfully."
    )

    print(
        "Programs exported:",
        len(sorted_programs),
    )

    print()
    print(
        "Output file:"
    )

    print(output_file)

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "No MongoDB records were modified."
    )

    print(
        "New tuition context fields were "
        "left blank intentionally."
    )

    print("=" * 85)


if __name__ == "__main__":
    main()