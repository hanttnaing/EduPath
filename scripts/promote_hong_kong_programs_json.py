import argparse
import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path


CURRENT_JSON = Path(
    "data/cleaned/programs.json"
)

STAGING_JSON = Path(
    "data/cleaned/"
    "programs_with_hong_kong_staging.json"
)

BACKUP_DIR = Path(
    "data/backups/step_169_3c"
)


EXPECTED_EXISTING = 291
EXPECTED_HK = 45
EXPECTED_TOTAL = 336


EXPECTED_PREFIX_COUNTS = {
    "prog_jp": 36,
    "prog_bn": 12,
    "prog_la": 15,
    "prog_sg": 18,
    "prog_tl": 18,
    "prog_kh": 39,
    "prog_mm": 33,
    "prog_my": 120,
    "prog_hk": 45,
}


EXPECTED_INTL_UNKNOWN = {
    "prog_hk_019",
    "prog_hk_020",
    "prog_hk_021",
    "prog_hk_034",
    "prog_hk_035",
    "prog_hk_036",
}


EXPECTED_LANGUAGE_UNKNOWN = {
    "prog_hk_020",
    "prog_hk_028",
}


INTERNATIONAL_FIELDS = [
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


def clean(value):
    return str(value or "").strip()


def prefix(program_id):

    parts = program_id.split("_")

    if len(parts) >= 3:
        return "_".join(parts[:2])

    return "unknown"


def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Required JSON not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"{path} must contain a JSON list."
        )

    return data


def by_id(records):

    result = {}

    for record in records:

        program_id = clean(
            record.get("program_id")
        )

        if not program_id:
            raise ValueError(
                "Record without program_id detected."
            )

        if program_id in result:
            raise ValueError(
                f"Duplicate program_id: {program_id}"
            )

        result[program_id] = record

    return result


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Promote staging JSON to programs.json "
            "after all validations pass."
        ),
    )

    args = parser.parse_args()


    print("=" * 105)
    print(
        "STEP 169.3C - FINAL PROGRAMS.JSON "
        "GATE + SAFE PROMOTION"
    )
    print("=" * 105)


    current = load_json(
        CURRENT_JSON
    )

    staging = load_json(
        STAGING_JSON
    )


    current_by_id = by_id(
        current
    )

    staging_by_id = by_id(
        staging
    )


    current_ids = set(
        current_by_id
    )

    staging_ids = set(
        staging_by_id
    )


    hk_ids = {
        program_id
        for program_id in staging_ids
        if program_id.startswith(
            "prog_hk_"
        )
    }


    # -------------------------------------------------
    # A. Counts
    # -------------------------------------------------

    print()
    print("A. GLOBAL COUNTS")
    print("-" * 105)

    print(
        "Current programs.json rows       :",
        len(current),
    )

    print(
        "Staging JSON rows                :",
        len(staging),
    )

    print(
        "Hong Kong rows                   :",
        len(hk_ids),
    )

    print(
        "Existing IDs preserved           :",
        len(
            current_ids
            & staging_ids
        ),
    )


    errors = []


    if len(current) != EXPECTED_EXISTING:
        errors.append(
            "Current programs.json is no longer 291 rows."
        )

    if len(staging) != EXPECTED_TOTAL:
        errors.append(
            "Staging JSON must contain 336 rows."
        )

    if len(hk_ids) != EXPECTED_HK:
        errors.append(
            "Expected exactly 45 Hong Kong rows."
        )

    if not current_ids.issubset(
        staging_ids
    ):
        errors.append(
            "One or more existing programme IDs "
            "are missing from staging."
        )


    # -------------------------------------------------
    # B. Exact existing-record preservation
    # -------------------------------------------------

    changed_existing = []


    for program_id in sorted(
        current_ids
    ):

        if (
            current_by_id[program_id]
            != staging_by_id.get(program_id)
        ):
            changed_existing.append(
                program_id
            )


    print()
    print("B. EXISTING RECORD PRESERVATION")
    print("-" * 105)

    print(
        "Existing records changed         :",
        len(changed_existing),
    )


    if changed_existing:

        print(
            "First changed IDs:"
        )

        for program_id in (
            changed_existing[:20]
        ):
            print(
                " ",
                program_id,
            )

        errors.append(
            "Existing 291 records are not "
            "byte-structure equivalent."
        )


    # -------------------------------------------------
    # C. Prefix counts
    # -------------------------------------------------

    prefix_counts = Counter(
        prefix(program_id)
        for program_id in staging_ids
    )


    print()
    print("C. COUNTRY/PREFIX COUNTS")
    print("-" * 105)

    print(
        "Prefix counts                    :",
        dict(prefix_counts),
    )


    if dict(prefix_counts) != (
        EXPECTED_PREFIX_COUNTS
    ):
        errors.append(
            "Programme prefix counts mismatch."
        )


    # -------------------------------------------------
    # D. Hong Kong data quality
    # -------------------------------------------------

    hk_records = [
        staging_by_id[
            program_id
        ]
        for program_id in sorted(
            hk_ids
        )
    ]


    intl_statuses = Counter(
        clean(
            record.get(
                "international_applicants_status"
            )
        )
        for record in hk_records
    )


    missing_intl_fields = []


    for record in hk_records:

        program_id = clean(
            record["program_id"]
        )

        for field in (
            INTERNATIONAL_FIELDS
        ):

            if field not in record:

                missing_intl_fields.append(
                    (
                        program_id,
                        field,
                    )
                )


    intl_unknown = {
        clean(record["program_id"])
        for record in hk_records
        if clean(
            record.get(
                "international_applicants_status"
            )
        ) == "unknown"
    }


    verified_blank_urls = {
        clean(record["program_id"])
        for record in hk_records
        if clean(
            record.get(
                "international_applicants_status"
            )
        ) == "verified_yes"
        and not clean(
            record.get(
                "international_application_url"
            )
        )
    }


    numeric_tuition = sum(
        record.get("tuition_fee")
        is not None
        for record in hk_records
    )


    numeric_toefl = sum(
        record.get(
            "toefl_requirement"
        )
        is not None
        for record in hk_records
    )


    unknown_language = {
        clean(record["program_id"])
        for record in hk_records
        if clean(
            record.get(
                "language_of_instruction"
            )
        ) == "Unknown"
    }


    current_freshness = sum(
        clean(
            record.get(
                "freshness_status"
            )
        ) == "current"
        for record in hk_records
    )


    print()
    print("D. HONG KONG FINAL QUALITY")
    print("-" * 105)

    print(
        "International statuses          :",
        dict(intl_statuses),
    )

    print(
        "Missing international fields    :",
        len(missing_intl_fields),
    )

    print(
        "verified_yes blank URLs         :",
        len(verified_blank_urls),
    )

    print(
        "Numeric tuition rows             :",
        numeric_tuition,
    )

    print(
        "Numeric TOEFL rows               :",
        numeric_toefl,
    )

    print(
        "Unknown language IDs             :",
        ", ".join(
            sorted(
                unknown_language
            )
        ),
    )

    print(
        "freshness_status=current         :",
        current_freshness,
    )


    if intl_statuses != Counter({
        "verified_yes": 39,
        "unknown": 6,
    }):
        errors.append(
            "International eligibility counts mismatch."
        )

    if intl_unknown != (
        EXPECTED_INTL_UNKNOWN
    ):
        errors.append(
            "International unknown ID set mismatch."
        )

    if missing_intl_fields:
        errors.append(
            "One or more HK records lack "
            "international merge fields."
        )

    if verified_blank_urls:
        errors.append(
            "verified_yes HK records contain blank URLs."
        )

    if numeric_tuition != 35:
        errors.append(
            "Expected 35 numeric HK tuition rows."
        )

    if numeric_toefl != 24:
        errors.append(
            "Expected 24 numeric HK TOEFL rows."
        )

    if unknown_language != (
        EXPECTED_LANGUAGE_UNKNOWN
    ):
        errors.append(
            "Unknown language ID set mismatch."
        )

    if current_freshness != 45:
        errors.append(
            "All HK records must have current freshness."
        )


    # -------------------------------------------------
    # E. Result
    # -------------------------------------------------

    print()
    print("=" * 105)


    if errors:

        print(
            "STEP 169.3C FINAL JSON GATE: FAIL"
        )

        for error in errors:
            print(
                "ERROR:",
                error,
            )

        print()
        print(
            "programs.json WAS NOT MODIFIED."
        )

        raise SystemExit(1)


    if not args.apply:

        print(
            "STEP 169.3C FINAL JSON "
            "DRY RUN: PASS"
        )

        print(
            "336-ROW STAGING JSON IS "
            "READY FOR PROMOTION"
        )

        print(
            "ALL EXISTING 291 PROGRAMMES "
            "ARE EXACTLY PRESERVED"
        )

        print(
            "NO FILES OR DATABASE RECORDS "
            "WERE MODIFIED"
        )

        print()
        print(
            "Next command:"
        )

        print(
            "python .\\scripts\\"
            "promote_hong_kong_programs_json.py "
            "--apply"
        )

        print("=" * 105)

        return


    # -------------------------------------------------
    # F. Backup + promotion
    # -------------------------------------------------

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = BACKUP_DIR / (
        "programs_before_hong_kong_"
        f"promotion_{timestamp}.json"
    )


    shutil.copy2(
        CURRENT_JSON,
        backup_path,
    )


    shutil.copy2(
        STAGING_JSON,
        CURRENT_JSON,
    )


    # Re-open promoted file.
    promoted = load_json(
        CURRENT_JSON
    )

    promoted_by_id = by_id(
        promoted
    )


    if len(promoted) != EXPECTED_TOTAL:
        raise ValueError(
            "Post-promotion programs.json "
            "does not contain 336 records."
        )


    if set(
        promoted_by_id
    ) != staging_ids:

        raise ValueError(
            "Post-promotion ID set does not "
            "match staging."
        )


    print(
        "STEP 169.3C PROGRAMS.JSON "
        "PROMOTION: PASS"
    )

    print(
        "Backup:",
        backup_path,
    )

    print(
        "Promoted programs.json rows     :",
        len(promoted),
    )

    print(
        "Existing programmes preserved   :",
        EXPECTED_EXISTING,
    )

    print(
        "Hong Kong programmes added      :",
        EXPECTED_HK,
    )

    print(
        "MONGODB WAS NOT MODIFIED"
    )

    print("=" * 105)


if __name__ == "__main__":
    main()
