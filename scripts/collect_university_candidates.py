import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://api.ror.org/v2/organizations"

OUTPUT_PATH = Path(
    "data/raw/ror_university_candidates.csv"
)

COUNTRY_TARGETS = {
    "country_jp": {
        "country_name": "Japan",
        "country_code": "JP",
        "target": 12,
    },
    "country_sg": {
        "country_name": "Singapore",
        "country_code": "SG",
        "target": 8,
    },
    "country_my": {
        "country_name": "Malaysia",
        "country_code": "MY",
        "target": 8,
    },
    "country_kr": {
        "country_name": "South Korea",
        "country_code": "KR",
        "target": 7,
    },
    "country_tw": {
        "country_name": "Taiwan",
        "country_code": "TW",
        "target": 5,
    },
    "country_hk": {
        "country_name": "Hong Kong",
        "country_code": "HK",
        "target": 5,
    },
    "country_th": {
        "country_name": "Thailand",
        "country_code": "TH",
        "target": 5,
    },
}

EXTRA_CANDIDATES_PER_COUNTRY = 30


def get_display_name(record: dict) -> str:
    for name in record.get("names", []):
        if "ror_display" in name.get("types", []):
            return name.get("value", "")
    return ""


def get_official_website(record: dict) -> str:
    for link in record.get("links", []):
        if link.get("type") == "website":
            return link.get("value", "")
    return ""


def get_location(record: dict) -> dict:
    locations = record.get("locations", [])

    if not locations:
        return {}

    return locations[0].get(
        "geonames_details",
        {},
    )


def fetch_country_candidates(
    country_id: str,
    country_name: str,
    country_code: str,
    required_count: int,
) -> list[dict]:

    results = []
    seen_ror_ids = set()

    page = 1

    while len(results) < required_count:
        parameters = {
            "query": "University",
            "filter": (
                f"types:education,"
                f"country.country_code:{country_code}"
            ),
            "page": page,
        }

        request_url = (
            f"{API_URL}?{urlencode(parameters)}"
        )

        request = Request(
            request_url,
            headers={
                "User-Agent": (
                    "EduPath-Analytics-University-Project/1.0"
                )
            },
        )

        print(
            f"Fetching {country_name} "
            f"(page {page})..."
        )

        with urlopen(
            request,
            timeout=30,
        ) as response:
            payload = json.load(response)

        items = payload.get("items", [])

        if not items:
            break

        for record in items:
            ror_id = record.get("id", "")

            if not ror_id:
                continue

            if ror_id in seen_ror_ids:
                continue

            if "education" not in record.get(
                "types",
                [],
            ):
                continue

            location = get_location(record)

            results.append(
                {
                    "country_id": country_id,
                    "country_name": country_name,
                    "country_code": country_code,
                    "ror_id": ror_id,
                    "university_name": (
                        get_display_name(record)
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
                    "ror_last_modified": (
                        record
                        .get("admin", {})
                        .get(
                            "last_modified",
                            {},
                        )
                        .get("date", "")
                    ),
                    "collected_at": (
                        datetime.now(
                            timezone.utc
                        )
                        .date()
                        .isoformat()
                    ),
                    "candidate_status": (
                        "To Review"
                    ),
                }
            )

            seen_ror_ids.add(ror_id)

            if len(results) >= required_count:
                break

        page += 1

        if page > 10:
            break

        time.sleep(0.5)

    return results


def main() -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_candidates = []

    for country_id, config in (
        COUNTRY_TARGETS.items()
    ):
        required_count = (
            config["target"]
            + EXTRA_CANDIDATES_PER_COUNTRY
        )

        try:
            candidates = fetch_country_candidates(
                country_id=country_id,
                country_name=(
                    config["country_name"]
                ),
                country_code=(
                    config["country_code"]
                ),
                required_count=required_count,
            )
        except Exception as error:
            print(
                f"ERROR collecting "
                f"{config['country_name']}: "
                f"{error}"
            )
            continue

        all_candidates.extend(candidates)

        print(
            f"{config['country_name']}: "
            f"{len(candidates)} candidates"
        )

    fieldnames = [
        "country_id",
        "country_name",
        "country_code",
        "ror_id",
        "university_name",
        "city",
        "establishment_year",
        "official_website",
        "ror_last_modified",
        "collected_at",
        "candidate_status",
    ]

    with OUTPUT_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(all_candidates)

    print()
    print("=== Collection Complete ===")
    print(
        f"Total candidates: "
        f"{len(all_candidates)}"
    )
    print(
        f"Saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()

