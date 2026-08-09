import csv
import re
from pathlib import Path


INPUT_PATH = Path(
    "data/raw/ror_university_candidates.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/validated_university_candidates.csv"
)

COUNTRY_TARGETS = {
    "country_jp": 12,
    "country_sg": 8,
    "country_my": 8,
    "country_kr": 7,
    "country_tw": 5,
    "country_hk": 5,
    "country_th": 5,
}


def normalize_name(name: str) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        "",
        name.lower(),
    )


def looks_like_university(name: str) -> bool:
    normalized = name.lower()

    university_terms = [
        "university",
        "universiti",
    ]

    return any(
        term in normalized
        for term in university_terms
    )


def completeness_score(row: dict) -> int:
    score = 0

    if row.get("university_name"):
        score += 2

    if row.get("official_website"):
        score += 3

    if row.get("city"):
        score += 1

    if row.get("establishment_year"):
        score += 2

    if row.get("ror_last_modified"):
        score += 1

    return score


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    unique_rows = []
    seen_ror_ids = set()
    seen_names = set()

    for row in rows:
        ror_id = row.get(
            "ror_id",
            "",
        ).strip()

        university_name = row.get(
            "university_name",
            "",
        ).strip()

        if not ror_id or not university_name:
            continue

        normalized_name = normalize_name(
            university_name
        )

        if ror_id in seen_ror_ids:
            continue

        if normalized_name in seen_names:
            continue

        if not looks_like_university(
            university_name
        ):
            continue

        row["completeness_score"] = (
            completeness_score(row)
        )

        row["validation_status"] = (
            "Candidate Selected"
        )

        unique_rows.append(row)

        seen_ror_ids.add(ror_id)
        seen_names.add(normalized_name)

    selected_rows = []

    for country_id, target in (
        COUNTRY_TARGETS.items()
    ):
        country_rows = [
            row
            for row in unique_rows
            if row.get("country_id")
            == country_id
        ]

        country_rows.sort(
            key=lambda row: (
                -int(
                    row[
                        "completeness_score"
                    ]
                ),
                row[
                    "university_name"
                ].lower(),
            )
        )

        selected = country_rows[:target]

        selected_rows.extend(selected)

        print(
            f"{country_id}: "
            f"{len(selected)} / "
            f"{target} selected"
        )

        if len(selected) < target:
            print(
                "  WARNING: "
                "Target was not reached."
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
        "completeness_score",
        "validation_status",
    ]

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
        writer.writerows(selected_rows)

    print()
    print("=== Validation Complete ===")
    print(
        f"Raw candidates: {len(rows)}"
    )
    print(
        f"Valid unique university "
        f"candidates: {len(unique_rows)}"
    )
    print(
        f"Selected candidates: "
        f"{len(selected_rows)}"
    )
    print(
        f"Saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()