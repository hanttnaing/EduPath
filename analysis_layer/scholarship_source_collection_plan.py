from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# EduPath - Step 152.7B
# Scholarship Source Collection Plan
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INVENTORY_JSON = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7a_scholarship_expansion_inventory.json"
)

OUTPUT_JSON = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "152_7b_scholarship_source_plan.json"
)

OUTPUT_CSV = (
    PROJECT_ROOT
    / "data"
    / "staging"
    / "152_7b_scholarship_source_collection.csv"
)

OUTPUT_GUIDE = (
    PROJECT_ROOT
    / "docs"
    / "152_7b_scholarship_collection_guide.md"
)


CURRENT_SCHOLARSHIP_COUNT = 12
MINIMUM_TARGET = 30
NEW_RECORD_TARGET = 18


# ------------------------------------------------------------
# Expansion strategy
# ------------------------------------------------------------

COUNTRY_TARGETS = [
    {
        "country_id": "country_hk",
        "country_name": "Hong Kong",
        "target": 3,
    },
    {
        "country_id": "country_my",
        "country_name": "Malaysia",
        "target": 3,
    },
    {
        "country_id": "country_sg",
        "country_name": "Singapore",
        "target": 3,
    },
    {
        "country_id": "country_kr",
        "country_name": "South Korea",
        "target": 3,
    },
    {
        "country_id": "country_tw",
        "country_name": "Taiwan",
        "target": 3,
    },
    {
        "country_id": "country_th",
        "country_name": "Thailand",
        "target": 3,
    },
]


# ------------------------------------------------------------
# Fields used ONLY during manual collection.
#
# These are not automatically inserted into MongoDB.
# ------------------------------------------------------------

COLLECTION_METADATA_FIELDS = [
    "collection_slot",
    "target_country_id",
    "target_country_name",
    "official_source_url",
    "official_source_title",
    "source_organisation",
    "source_type",
    "collection_status",
    "verification_status",
    "collected_on",
    "verified_on",
    "collector_notes",
]


def separator() -> None:
    print("=" * 92)


def load_inventory() -> dict[str, Any]:
    if not INVENTORY_JSON.exists():
        raise FileNotFoundError(
            "Step 152.7A inventory JSON was not found:\n"
            f"{INVENTORY_JSON}"
        )

    with INVENTORY_JSON.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def normalise_fields(
    fields: list[str],
) -> list[str]:
    """
    Remove duplicates while preserving order.
    """

    output: list[str] = []
    seen: set[str] = set()

    for field in fields:
        clean_field = str(field).strip()

        if not clean_field:
            continue

        key = clean_field.lower()

        if key in seen:
            continue

        seen.add(key)
        output.append(clean_field)

    return output


def build_collection_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    slot_number = 1

    for country in COUNTRY_TARGETS:

        for local_number in range(
            1,
            country["target"] + 1,
        ):

            rows.append(
                {
                    "collection_slot": (
                        f"SCH_EXP_{slot_number:02d}"
                    ),
                    "target_country_id": (
                        country["country_id"]
                    ),
                    "target_country_name": (
                        country["country_name"]
                    ),
                    "official_source_url": "",
                    "official_source_title": "",
                    "source_organisation": "",
                    "source_type": "",
                    "collection_status": "NOT_COLLECTED",
                    "verification_status": "NOT_VERIFIED",
                    "collected_on": "",
                    "verified_on": "",
                    "collector_notes": (
                        f"Target scholarship "
                        f"{local_number} for "
                        f"{country['country_name']}"
                    ),
                }
            )

            slot_number += 1

    return rows


def save_json_report(
    discovered_fields: list[str],
    rows: list[dict[str, Any]],
) -> None:

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "project": "EduPath Analytics",
        "step": "152.7B",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "purpose": (
            "Plan the collection of verified scholarship "
            "records before MongoDB insertion."
        ),
        "current_scholarship_count": (
            CURRENT_SCHOLARSHIP_COUNT
        ),
        "minimum_target": MINIMUM_TARGET,
        "new_record_target": NEW_RECORD_TARGET,
        "expected_total_after_expansion": (
            CURRENT_SCHOLARSHIP_COUNT
            + NEW_RECORD_TARGET
        ),
        "country_targets": COUNTRY_TARGETS,
        "current_schema_fields": discovered_fields,
        "collection_rows": rows,
        "mongodb_records_modified": False,
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )


def save_collection_csv(
    discovered_fields: list[str],
    rows: list[dict[str, Any]],
) -> None:

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Metadata first, then actual existing MongoDB fields.
    fieldnames = normalise_fields(
        COLLECTION_METADATA_FIELDS
        + discovered_fields
    )

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        for row in rows:

            output_row = {
                field: ""
                for field in fieldnames
            }

            output_row.update(row)

            # If the actual schema already has country_id,
            # prefill it from the target country.
            if "country_id" in output_row:
                output_row["country_id"] = row[
                    "target_country_id"
                ]

            writer.writerow(output_row)


def save_collection_guide(
    discovered_fields: list[str],
) -> None:

    OUTPUT_GUIDE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines: list[str] = []

    lines.append(
        "# EduPath Step 152.7B "
        "Scholarship Collection Guide"
    )
    lines.append("")
    lines.append(
        "This staging dataset is used to collect "
        "verified scholarship records before import."
    )
    lines.append("")

    lines.append("## Expansion Target")
    lines.append("")

    lines.append(
        f"- Current scholarships: "
        f"{CURRENT_SCHOLARSHIP_COUNT}"
    )

    lines.append(
        f"- Minimum target: {MINIMUM_TARGET}"
    )

    lines.append(
        f"- New records required: "
        f"{NEW_RECORD_TARGET}"
    )

    lines.append(
        "- Expected dataset after expansion: "
        f"{CURRENT_SCHOLARSHIP_COUNT + NEW_RECORD_TARGET}"
    )

    lines.append("")

    lines.append("## Country Allocation")
    lines.append("")

    for country in COUNTRY_TARGETS:
        lines.append(
            f"- {country['country_name']}: "
            f"{country['target']} scholarships"
        )

    lines.append("")

    lines.append("## Collection Rules")
    lines.append("")

    lines.append(
        "1. Use official government, university, "
        "or scholarship-provider sources."
    )

    lines.append(
        "2. Do not invent missing GPA, English, "
        "age or nationality requirements."
    )

    lines.append(
        "3. If an official source does not publish "
        "a value, leave the field empty or UNKNOWN "
        "according to the existing schema."
    )

    lines.append(
        "4. Record the official URL used for verification."
    )

    lines.append(
        "5. Do not import staging data into MongoDB "
        "until Step 152.7C validation passes."
    )

    lines.append("")

    lines.append("## Current MongoDB Scholarship Fields")
    lines.append("")

    for field in discovered_fields:
        lines.append(
            f"- `{field}`"
        )

    with OUTPUT_GUIDE.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "\n".join(lines)
        )


def print_country_plan() -> None:

    print()
    separator()
    print("SCHOLARSHIP EXPANSION COUNTRY PLAN")
    separator()
    print()

    total = 0

    for country in COUNTRY_TARGETS:

        target = country["target"]

        total += target

        print(
            f"{country['country_name']:<20}"
            f"{target:>3} new record(s)"
        )

    print("-" * 40)

    print(
        f"{'TOTAL':<20}"
        f"{total:>3} new record(s)"
    )


def main() -> None:

    separator()

    print(
        "EduPath - Step 152.7B "
        "Scholarship Source Collection Plan"
    )

    separator()
    print()

    try:
        inventory = load_inventory()

        discovered_fields = inventory.get(
            "discovered_fields",
            [],
        )

        if not isinstance(
            discovered_fields,
            list,
        ):
            raise ValueError(
                "Invalid discovered_fields "
                "in Step 152.7A report."
            )

        discovered_fields = normalise_fields(
            discovered_fields
        )

        print(
            "Step 152.7A inventory loaded: SUCCESS"
        )

        print(
            f"Current scholarship schema fields: "
            f"{len(discovered_fields)}"
        )

        print(
            f"Current scholarships: "
            f"{CURRENT_SCHOLARSHIP_COUNT}"
        )

        print(
            f"Minimum target: "
            f"{MINIMUM_TARGET}"
        )

        print(
            f"New verified records required: "
            f"{NEW_RECORD_TARGET}"
        )

        rows = build_collection_rows()

        if len(rows) != NEW_RECORD_TARGET:
            raise RuntimeError(
                "Country target allocation does not "
                "equal the required 18 records."
            )

        print_country_plan()

        save_json_report(
            discovered_fields,
            rows,
        )

        save_collection_csv(
            discovered_fields,
            rows,
        )

        save_collection_guide(
            discovered_fields,
        )

        print()
        separator()

        print(
            "STEP 152.7B SCHOLARSHIP "
            "SOURCE COLLECTION PLAN: COMPLETED"
        )

        separator()

        print()

        print(
            f"Collection slots created : "
            f"{len(rows)}"
        )

        print(
            "Current scholarship count: "
            f"{CURRENT_SCHOLARSHIP_COUNT}"
        )

        print(
            "Projected count after verified import: "
            f"{CURRENT_SCHOLARSHIP_COUNT + len(rows)}"
        )

        print()

        print("JSON plan:")
        print(OUTPUT_JSON)

        print()

        print("Collection CSV:")
        print(OUTPUT_CSV)

        print()

        print("Collection guide:")
        print(OUTPUT_GUIDE)

        print()

        print("MongoDB records modified: NO")

        print()

        print(
            "IMPORTANT:"
        )

        print(
            "The 18 rows are collection slots only."
        )

        print(
            "No scholarship information has been "
            "invented and nothing has been imported."
        )

    except Exception as error:

        print()
        print(
            f"ERROR: "
            f"{type(error).__name__}: "
            f"{error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()