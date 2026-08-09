import csv
import json
import re
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


INPUT_PATH = Path(
    "data/cleaned/university_seed_list.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/university_seed_enriched.csv"
)


ROR_API_URL = (
    "https://api.ror.org/v2/organizations"
)


COUNTRY_CODES = {
    "country_jp": "JP",
    "country_sg": "SG",
    "country_my": "MY",
    "country_kr": "KR",
    "country_tw": "TW",
    "country_hk": "HK",
    "country_th": "TH",
}

ROR_QUERY_ALIASES = {
    "The University of Hong Kong": (
        "University of Hong Kong"
    ),
    "The Chinese University of Hong Kong": (
        "Chinese University of Hong Kong"
    ),
    (
        "The Hong Kong University of "
        "Science and Technology"
    ): (
        "Hong Kong University of "
        "Science and Technology"
    ),
    "The Hong Kong Polytechnic University": (
        "Hong Kong Polytechnic University"
    ),
}


def normalize_name(value: str) -> str:
    value = value.lower().strip()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    return " ".join(
        value.split()
    )


def get_all_names(record: dict) -> list[str]:
    names = []

    for item in record.get(
        "names",
        [],
    ):
        value = item.get(
            "value",
            "",
        ).strip()

        if value:
            names.append(value)

    return names


def get_display_name(record: dict) -> str:
    for item in record.get(
        "names",
        [],
    ):
        if (
            "ror_display"
            in item.get("types", [])
        ):
            return item.get(
                "value",
                "",
            )

    names = get_all_names(record)

    if names:
        return names[0]

    return ""


def get_official_website(
    record: dict,
) -> str:
    for link in record.get(
        "links",
        [],
    ):
        if link.get("type") == "website":
            return link.get(
                "value",
                "",
            )

    return ""


def get_location(record: dict) -> dict:
    locations = record.get(
        "locations",
        [],
    )

    if not locations:
        return {}

    return locations[0].get(
        "geonames_details",
        {},
    )


def is_exact_name_match(
    seed_name: str,
    record: dict,
) -> bool:
    normalized_seed = normalize_name(
        seed_name
    )

    for candidate_name in get_all_names(
        record
    ):
        if (
            normalize_name(candidate_name)
            == normalized_seed
        ):
            return True

    return False


def fetch_ror_matches(
    university_name: str,
    country_code: str,
) -> list[dict]:

    # Exact-name style query.
    query_value = (
        f'"{university_name}"'
    )

    parameters = {
        "query": query_value,
        "filter": (
            f"country.country_code:"
            f"{country_code},"
            f"types:education"
        ),
    }

    url = (
        f"{ROR_API_URL}?"
        f"{urlencode(parameters)}"
    )

    request = Request(
        url,
        headers={
            "User-Agent": (
                "EduPath-Analytics-"
                "University-Project/1.0"
            )
        },
    )

    with urlopen(
        request,
        timeout=30,
    ) as response:
        payload = json.load(response)

    return payload.get(
        "items",
        [],
    )


def select_match(
    seed_name: str,
    matches: list[dict],
) -> tuple[dict | None, str]:

    for record in matches:
        if is_exact_name_match(
            seed_name,
            record,
        ):
            return (
                record,
                "Exact Name Match",
            )

    if len(matches) == 1:
        return (
            matches[0],
            "Single Candidate - Review",
        )

    if matches:
        return (
            matches[0],
            "Multiple Candidates - Review",
        )

    return (
        None,
        "No ROR Match",
    )


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: "
            f"{INPUT_PATH}"
        )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(
            csv_file
        )

        seed_rows = list(reader)

    enriched_rows = []

    exact_count = 0
    review_count = 0
    unmatched_count = 0

    for index, seed in enumerate(
        seed_rows,
        start=1,
    ):
        country_id = seed[
            "country_id"
        ]

        university_name = seed[
            "university_name"
        ]

        ror_query_name = (
            ROR_QUERY_ALIASES.get(
                university_name,
                university_name,
            )
        )

        country_code = (
            COUNTRY_CODES[
                country_id
            ]
        )

        print(
            f"[{index}/{len(seed_rows)}] "
            f"{university_name}"
        )

        try:
            matches = fetch_ror_matches(
                university_name=(
                    ror_query_name
                ),
                country_code=(
                    country_code
                ),
            )

            record, match_status = (
                select_match(
                    ror_query_name,
                    matches,
                )
            )

            if (
                record is not None
                and ror_query_name != university_name
                and match_status == "Exact Name Match"
            ):
                match_status = "Exact Alias Match"

        except Exception as error:
            print(
                f"  ERROR: {error}"
            )

            record = None
            match_status = (
                "API Error - Review"
            )

        if record is None:
            unmatched_count += 1

            enriched_rows.append(
                {
                    **seed,
                    "country_code": (
                        country_code
                    ),
                    "ror_id": "",
                    "ror_display_name": "",
                    "city": "",
                    "establishment_year": "",
                    "official_website": "",
                    "ror_status": "",
                    "ror_types": "",
                    "ror_last_modified": "",
                    "match_status": (
                        match_status
                    ),
                    "metadata_status": (
                        "Needs Review"
                    ),
                }
            )

            print(
                f"  -> {match_status}"
            )

            time.sleep(0.3)
            continue

        if match_status in {
            "Exact Name Match",
            "Exact Alias Match",
        }:
            exact_count += 1
            metadata_status = (
                "ROR Matched"
            )
        else:
            review_count += 1
            metadata_status = (
                "Needs Review"
            )

        location = get_location(
            record
        )

        last_modified = (
            record
            .get("admin", {})
            .get(
                "last_modified",
                {},
            )
            .get("date", "")
        )

        enriched_rows.append(
            {
                **seed,
                "country_code": (
                    country_code
                ),
                "ror_id": record.get(
                    "id",
                    "",
                ),
                "ror_display_name": (
                    get_display_name(
                        record
                    )
                ),
                "city": location.get(
                    "name",
                    "",
                ),
                "establishment_year": (
                    record.get(
                        "established",
                        "",
                    )
                ),
                "official_website": (
                    get_official_website(
                        record
                    )
                ),
                "ror_status": (
                    record.get(
                        "status",
                        "",
                    )
                ),
                "ror_types": "|".join(
                    record.get(
                        "types",
                        [],
                    )
                ),
                "ror_last_modified": (
                    last_modified
                ),
                "match_status": (
                    match_status
                ),
                "metadata_status": (
                    metadata_status
                ),
            }
        )

        print(
            f"  -> {match_status}"
        )

        time.sleep(0.3)

    fieldnames = [
        "country_id",
        "country_name",
        "university_name",
        "national_source_name",
        "national_source_url",
        "selection_status",
        "verification_status",
        "country_code",
        "ror_id",
        "ror_display_name",
        "city",
        "establishment_year",
        "official_website",
        "ror_status",
        "ror_types",
        "ror_last_modified",
        "match_status",
        "metadata_status",
    ]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(
            enriched_rows
        )

    print()
    print(
        "=== University Metadata "
        "Enrichment Complete ==="
    )
    print(
        f"Seed universities: "
        f"{len(seed_rows)}"
    )
    print(
        f"Exact ROR matches: "
        f"{exact_count}"
    )
    print(
        f"Matches needing review: "
        f"{review_count}"
    )
    print(
        f"No match / API error: "
        f"{unmatched_count}"
    )
    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()