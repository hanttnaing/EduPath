import csv
import re
from pathlib import Path
from urllib.parse import urlparse


INPUT_PATH = Path(
    "data/raw/ror_university_candidates.csv"
)

REVIEW_OUTPUT_PATH = Path(
    "data/cleaned/university_selection_review.csv"
)

SELECTED_OUTPUT_PATH = Path(
    "data/cleaned/selected_university_candidates.csv"
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


SUSPICIOUS_PHRASES = [
    "hospital",
    "health system",
    "health service",
    "cancer institute",
    "cancer centre",
    "cancer center",
    "medical centre",
    "medical center",
    "university press",
    "university library",
    "university museum",
]

HARD_EXCLUSIONS = {
    "hong kong virtual university": (
        "Not a standalone university; "
        "it is an HKUST education program."
    ),
    "kundong university": (
        "University is closed."
    ),
    "transworld university": (
        "University is closed."
    ),
    "asian university": (
        "University is closed."
    ),
}

def get_hard_exclusion_reason(
    name: str,
) -> str:
    normalized = normalize_text(name)

    return HARD_EXCLUSIONS.get(
        normalized,
        "",
    )




def normalize_text(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        value.strip().lower(),
    )


def has_valid_website(url: str) -> bool:
    if not url:
        return False

    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )
    except ValueError:
        return False


def contains_university_term(name: str) -> bool:
    normalized = normalize_text(name)

    terms = [
        "university",
        "universiti",
    ]

    return any(
        term in normalized
        for term in terms
    )


def get_suspicious_reason(name: str) -> str:
    normalized = normalize_text(name)

    for phrase in SUSPICIOUS_PHRASES:
        if phrase in normalized:
            return (
                f"Suspicious institution type: "
                f"{phrase}"
            )

    return ""


def calculate_quality_score(
    row: dict,
) -> int:
    score = 0

    name = row.get(
        "university_name",
        "",
    ).strip()

    website = row.get(
        "official_website",
        "",
    ).strip()

    city = row.get(
        "city",
        "",
    ).strip()

    establishment_year = row.get(
        "establishment_year",
        "",
    ).strip()

    ror_last_modified = row.get(
        "ror_last_modified",
        "",
    ).strip()

    if name:
        score += 5

    if contains_university_term(name):
        score += 4

    if has_valid_website(website):
        score += 5

    if city:
        score += 2

    if establishment_year:
        score += 2

    if ror_last_modified:
        score += 1

    suspicious_reason = (
        get_suspicious_reason(name)
    )

    if suspicious_reason:
        score -= 20

    return score


def get_review_status(
    row: dict,
) -> tuple[str, str]:
    name = row.get(
        "university_name",
        "",
    ).strip()

    website = row.get(
        "official_website",
        "",
    ).strip()

    hard_exclusion_reason = (
        get_hard_exclusion_reason(name)
    )

    if hard_exclusion_reason:
        return (
            "Exclude",
            hard_exclusion_reason,
        )

    suspicious_reason = (
        get_suspicious_reason(name)
    )

    if suspicious_reason:
        return (
            "Exclude",
            suspicious_reason,
        )

    if not has_valid_website(website):
        return (
            "Needs Review",
            "Missing or invalid official website",
        )

    if not contains_university_term(name):
        return (
            "Needs Review",
            (
                "Name does not contain "
                "University/Universiti; "
                "may still be a valid "
                "higher-education institution"
            ),
        )

    return (
        "Eligible",
        "",
    )


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    REVIEW_OUTPUT_PATH.parent.mkdir(
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

    processed_rows = []

    seen_ror_ids = set()
    seen_country_names = set()

    for source_order, row in enumerate(
        rows,
        start=1,
    ):
        ror_id = row.get(
            "ror_id",
            "",
        ).strip()

        name = row.get(
            "university_name",
            "",
        ).strip()

        country_id = row.get(
            "country_id",
            "",
        ).strip()

        if not ror_id or not name:
            continue

        duplicate_key = (
            country_id,
            normalize_text(name),
        )

        if ror_id in seen_ror_ids:
            continue

        if duplicate_key in seen_country_names:
            continue

        review_status, review_reason = (
            get_review_status(row)
        )

        row["source_order"] = source_order

        row["quality_score"] = (
            calculate_quality_score(row)
        )

        row["review_status"] = (
            review_status
        )

        row["review_reason"] = (
            review_reason
        )

        row["final_selection_status"] = (
            "Not Selected"
        )

        processed_rows.append(row)

        seen_ror_ids.add(ror_id)
        seen_country_names.add(
            duplicate_key
        )

    selected_rows = []

    for country_id, target in (
        COUNTRY_TARGETS.items()
    ):
        country_rows = [
            row
            for row in processed_rows
            if (
                row.get("country_id")
                == country_id
                and row.get(
                    "review_status"
                )
                != "Exclude"
            )
        ]

        eligible_rows = [
            row
            for row in country_rows
            if (
                row.get("review_status")
                == "Eligible"
            )
        ]

        review_rows = [
            row
            for row in country_rows
            if (
                row.get("review_status")
                == "Needs Review"
            )
        ]

        eligible_rows.sort(
            key=lambda row: (
                -int(
                    row["quality_score"]
                ),
                int(
                    row["source_order"]
                ),
            )
        )

        review_rows.sort(
            key=lambda row: (
                -int(
                    row["quality_score"]
                ),
                int(
                    row["source_order"]
                ),
            )
        )

        selected = eligible_rows[:target]

        if len(selected) < target:
            remaining = (
                target - len(selected)
            )

            selected.extend(
                review_rows[:remaining]
            )

        for row in selected:
            row[
                "final_selection_status"
            ] = (
                "Selected - "
                "Official Verification Required"
            )

        selected_rows.extend(selected)

        print(
            f"{country_id}: "
            f"{len(selected)} / "
            f"{target} selected"
        )

        if len(selected) < target:
            print(
                "  WARNING: "
                "Country target not reached."
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
        "source_order",
        "quality_score",
        "review_status",
        "review_reason",
        "final_selection_status",
    ]

    with REVIEW_OUTPUT_PATH.open(
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
            processed_rows
        )

    with SELECTED_OUTPUT_PATH.open(
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
            selected_rows
        )

    excluded_count = sum(
        1
        for row in processed_rows
        if row["review_status"]
        == "Exclude"
    )

    review_count = sum(
        1
        for row in processed_rows
        if row["review_status"]
        == "Needs Review"
    )

    eligible_count = sum(
        1
        for row in processed_rows
        if row["review_status"]
        == "Eligible"
    )

    print()
    print(
        "=== University Selection "
        "Complete ==="
    )
    print(
        f"Raw candidates: "
        f"{len(rows)}"
    )
    print(
        f"Unique processed: "
        f"{len(processed_rows)}"
    )
    print(
        f"Eligible: "
        f"{eligible_count}"
    )
    print(
        f"Needs review: "
        f"{review_count}"
    )
    print(
        f"Automatically excluded: "
        f"{excluded_count}"
    )
    print(
        f"Final selected: "
        f"{len(selected_rows)}"
    )
    print()
    print(
        f"Review file: "
        f"{REVIEW_OUTPUT_PATH}"
    )
    print(
        f"Selected file: "
        f"{SELECTED_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()