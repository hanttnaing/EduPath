from __future__ import annotations

import json
from collections import Counter, defaultdict
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
    all_items: list[dict] = []

    skip = 0

    while True:
        request_params = dict(
            params or {}
        )

        request_params["skip"] = skip
        request_params["limit"] = PAGE_SIZE

        data = get_json(
            path,
            request_params,
        )

        batch = data.get(
            "items",
            [],
        )

        all_items.extend(batch)

        total = data.get(
            "total",
            len(all_items),
        )

        if (
            not batch
            or len(all_items) >= total
        ):
            break

        skip += PAGE_SIZE

    return all_items


def format_tuition(
    program: dict,
) -> str:
    fee = program.get(
        "tuition_fee"
    )

    currency = (
        program.get(
            "tuition_currency"
        )
        or "?"
    )

    period = (
        program.get(
            "tuition_period"
        )
        or "?"
    )

    if fee is None:
        return "MISSING"

    if isinstance(
        fee,
        (int, float),
    ):
        fee_text = f"{fee:,.0f}"
    else:
        fee_text = str(fee)

    return (
        f"{fee_text} "
        f"{currency} / {period}"
    )


def main() -> None:
    print("=" * 90)
    print(
        "EduPath - Japan Programme Tuition Audit"
    )
    print("=" * 90)

    # --------------------------------------------------
    # Load Japan universities
    # --------------------------------------------------

    japan_universities = fetch_all(
        "/api/universities",
        {
            "country_id":
                JAPAN_COUNTRY_ID
        },
    )

    university_by_id = {
        university.get(
            "university_id"
        ): university
        for university
        in japan_universities
    }

    japan_university_ids = set(
        university_by_id.keys()
    )

    # --------------------------------------------------
    # Load all programmes
    # --------------------------------------------------

    all_programs = fetch_all(
        "/api/programs"
    )

    japan_programs = [
        program
        for program in all_programs
        if program.get(
            "university_id"
        )
        in japan_university_ids
    ]

    # --------------------------------------------------
    # Basic summary
    # --------------------------------------------------

    print()
    print(
        "Japan universities loaded:",
        len(japan_universities),
    )

    print(
        "Japan programmes found:",
        len(japan_programs),
    )

    missing_tuition = [
        program
        for program in japan_programs
        if program.get(
            "tuition_fee"
        )
        is None
    ]

    print(
        "Programmes missing tuition:",
        len(missing_tuition),
    )

    # --------------------------------------------------
    # Tuition distribution
    # --------------------------------------------------

    tuition_counter = Counter()

    for program in japan_programs:
        key = (
            program.get(
                "tuition_fee"
            ),
            program.get(
                "tuition_currency"
            ),
            program.get(
                "tuition_period"
            ),
        )

        tuition_counter[key] += 1

    print()
    print("-" * 90)
    print("TUITION DISTRIBUTION")
    print("-" * 90)

    for (
        fee,
        currency,
        period,
    ), count in tuition_counter.most_common():

        if isinstance(
            fee,
            (int, float),
        ):
            fee_text = (
                f"{fee:,.0f}"
            )
        else:
            fee_text = str(fee)

        print(
            f"{count:>3} programmes"
            f"  |  {fee_text}"
            f" {currency}"
            f" / {period}"
        )

    # --------------------------------------------------
    # Degree-level distribution
    # --------------------------------------------------

    tuition_by_degree = defaultdict(
        Counter
    )

    for program in japan_programs:
        degree = (
            program.get(
                "degree_level"
            )
            or "Unknown"
        )

        fee = program.get(
            "tuition_fee"
        )

        currency = program.get(
            "tuition_currency"
        )

        tuition_by_degree[
            degree
        ][
            (
                fee,
                currency,
            )
        ] += 1

    print()
    print("-" * 90)
    print("TUITION BY DEGREE LEVEL")
    print("-" * 90)

    for degree in sorted(
        tuition_by_degree
    ):
        print()
        print(
            f"[{degree}]"
        )

        for (
            fee,
            currency,
        ), count in (
            tuition_by_degree[
                degree
            ].most_common()
        ):
            if isinstance(
                fee,
                (int, float),
            ):
                fee_text = (
                    f"{fee:,.0f}"
                )
            else:
                fee_text = str(
                    fee
                )

            print(
                f"  {count:>3}"
                f" programme(s)"
                f" -> {fee_text}"
                f" {currency}"
            )

    # --------------------------------------------------
    # Record-by-record audit
    # --------------------------------------------------

    print()
    print("=" * 90)
    print("PROGRAMME RECORDS")
    print("=" * 90)

    sorted_programs = sorted(
        japan_programs,
        key=lambda program: (
            university_by_id.get(
                program.get(
                    "university_id"
                ),
                {},
            ).get(
                "university_name",
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

    for index, program in enumerate(
        sorted_programs,
        start=1,
    ):
        university = (
            university_by_id.get(
                program.get(
                    "university_id"
                ),
                {},
            )
        )

        university_name = (
            university.get(
                "university_name"
            )
            or program.get(
                "university_id"
            )
            or "Unknown University"
        )

        print()
        print(
            f"{index:02}. "
            f"{program.get('program_id')}"
        )

        print(
            "    University :",
            university_name,
        )

        print(
            "    Programme  :",
            program.get(
                "program_name"
            ),
        )

        print(
            "    Degree     :",
            program.get(
                "degree_level"
            ),
        )

        print(
            "    Tuition    :",
            format_tuition(
                program
            ),
        )

        print(
            "    Verified   :",
            program.get(
                "last_verified_at"
            ),
        )

        print(
            "    URL        :",
            program.get(
                "program_url"
            ),
        )

    # --------------------------------------------------
    # Warnings
    # --------------------------------------------------

    print()
    print("=" * 90)
    print("AUDIT WARNINGS")
    print("=" * 90)

    non_null_tuition_keys = {
        (
            program.get(
                "tuition_fee"
            ),
            program.get(
                "tuition_currency"
            ),
            program.get(
                "tuition_period"
            ),
        )
        for program in japan_programs
        if program.get(
            "tuition_fee"
        )
        is not None
    }

    if (
        japan_programs
        and len(
            non_null_tuition_keys
        ) == 1
    ):
        print(
            "WARNING:"
        )

        print(
            "All non-null Japan programme "
            "records use the same tuition value."
        )

        print(
            "This is NOT automatically wrong, "
            "but every programme should be "
            "verified against its official source."
        )

    else:
        print(
            "Tuition values are not all identical."
        )

    if missing_tuition:
        print()
        print(
            "WARNING:"
        )

        print(
            f"{len(missing_tuition)} "
            "programme(s) have missing tuition."
        )

    missing_url = [
        program
        for program in japan_programs
        if not program.get(
            "program_url"
        )
    ]

    if missing_url:
        print()
        print(
            "WARNING:"
        )

        print(
            f"{len(missing_url)} "
            "programme(s) have no program URL."
        )

    missing_verified = [
        program
        for program in japan_programs
        if not program.get(
            "last_verified_at"
        )
    ]

    if missing_verified:
        print()
        print(
            "WARNING:"
        )

        print(
            f"{len(missing_verified)} "
            "programme(s) have no "
            "last_verified_at value."
        )

    print()
    print("=" * 90)
    print(
        "AUDIT COMPLETE - "
        "NO DATABASE RECORDS WERE MODIFIED"
    )
    print("=" * 90)


if __name__ == "__main__":
    main()