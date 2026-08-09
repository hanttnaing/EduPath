import csv
from datetime import datetime, timezone
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/university_seed_enriched.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/universities_master_ready.csv"
)


COUNTRY_PREFIXES = {
    "country_jp": "jp",
    "country_sg": "sg",
    "country_my": "my",
    "country_kr": "kr",
    "country_tw": "tw",
    "country_hk": "hk",
    "country_th": "th",
}


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        source_rows = list(reader)

    counters = {}

    output_rows = []

    collected_at = datetime.now(
        timezone.utc
    ).date().isoformat()

    for row in source_rows:
        country_id = row[
            "country_id"
        ].strip()

        prefix = COUNTRY_PREFIXES[
            country_id
        ]

        counters[country_id] = (
            counters.get(country_id, 0)
            + 1
        )

        sequence = counters[
            country_id
        ]

        university_id = (
            f"uni_{prefix}_{sequence:03d}"
        )

        output_rows.append(
            {
                "university_id": university_id,
                "university_name": row[
                    "university_name"
                ].strip(),
                "country_id": country_id,
                "city": row[
                    "city"
                ].strip(),
                "university_type": "",
                "official_website": row[
                    "official_website"
                ].strip(),
                "establishment_year": row[
                    "establishment_year"
                ].strip(),
                "global_ranking": "",
                "ranking_source": "",
                "ranking_year": "",
                "degree_levels": "",
                "scholarship_available": "",
                "source_url": row[
                    "official_website"
                ].strip(),
                "collected_at": collected_at,
                "last_verified_at": "",
                "freshness_status": (
                    "Pending Verification"
                ),
            }
        )

    fieldnames = [
        "university_id",
        "university_name",
        "country_id",
        "city",
        "university_type",
        "official_website",
        "establishment_year",
        "global_ranking",
        "ranking_source",
        "ranking_year",
        "degree_levels",
        "scholarship_available",
        "source_url",
        "collected_at",
        "last_verified_at",
        "freshness_status",
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
        writer.writerows(output_rows)

    print(
        "=== University Master Rows Created ==="
    )

    for country_id, count in (
        counters.items()
    ):
        print(
            f"{country_id}: {count}"
        )

    print(
        f"Total universities: "
        f"{len(output_rows)}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()