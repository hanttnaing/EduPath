from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


EXPECTED_PROGRAM_COUNT = 36

EXPECTED_CHANGED_IDS = {
    "prog_jp_025",
    "prog_jp_026",
    "prog_jp_027",
}

EXPECTED_TSUKUBA_FEE = 608800


def normalize_text(value: str | None) -> str:
    return str(value or "").strip()


def parse_fee(
    value: str | None,
) -> int | None:
    text = normalize_text(value)

    if not text:
        return None

    text = text.replace(",", "")

    try:
        return int(float(text))
    except ValueError:
        return None


def is_valid_url(
    value: str | None,
) -> bool:
    text = normalize_text(value)

    if not text:
        return False

    try:
        parsed = urlparse(text)

        return (
            parsed.scheme in {
                "http",
                "https",
            }
            and bool(parsed.netloc)
        )

    except Exception:
        return False


def main() -> None:
    print("=" * 92)
    print(
        "EduPath - Final Japan Program "
        "Tuition Context Validation"
    )
    print("=" * 92)

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    input_file = (
        project_root
        / "planning"
        / "29_japan_program_tuition_context_all_verified.csv"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Verified CSV not found:\n"
            f"{input_file}"
        )

    # ==================================================
    # LOAD CSV
    # ==================================================

    with input_file.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        rows = list(reader)

        fieldnames = reader.fieldnames or []

    print()
    print(
        "Rows loaded:",
        len(rows),
    )

    errors: list[str] = []
    warnings: list[str] = []

    # ==================================================
    # REQUIRED COLUMNS
    # ==================================================

    required_columns = {
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

        "previous_tuition_fee",
        "tuition_change_required",
    }

    missing_columns = (
        required_columns
        - set(fieldnames)
    )

    if missing_columns:
        errors.append(
            "Missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    # ==================================================
    # TOTAL ROW COUNT
    # ==================================================

    if len(rows) != EXPECTED_PROGRAM_COUNT:
        errors.append(
            "Expected "
            f"{EXPECTED_PROGRAM_COUNT} rows, "
            f"but found {len(rows)}."
        )

    # ==================================================
    # UNIQUE PROGRAM IDs
    # ==================================================

    program_ids = [
        normalize_text(
            row.get("program_id")
        )
        for row in rows
    ]

    blank_program_ids = [
        index + 1
        for index, program_id
        in enumerate(program_ids)
        if not program_id
    ]

    if blank_program_ids:
        errors.append(
            "Blank program_id found on "
            "CSV row(s): "
            + ", ".join(
                map(
                    str,
                    blank_program_ids,
                )
            )
        )

    duplicate_program_ids = [
        program_id
        for program_id, count
        in Counter(
            program_ids
        ).items()
        if (
            program_id
            and count > 1
        )
    ]

    if duplicate_program_ids:
        errors.append(
            "Duplicate program IDs: "
            + ", ".join(
                sorted(
                    duplicate_program_ids
                )
            )
        )

    # ==================================================
    # RECORD VALIDATION
    # ==================================================

    changed_ids = set()

    tuition_distribution = Counter()

    academic_year_distribution = Counter()

    missing_context_ids = []

    invalid_tuition_ids = []

    invalid_currency_ids = []

    invalid_period_ids = []

    invalid_source_ids = []

    invalid_change_flags = []

    for row in rows:
        program_id = normalize_text(
            row.get("program_id")
        )

        university_name = normalize_text(
            row.get(
                "university_name"
            )
        )

        current_fee = parse_fee(
            row.get(
                "current_tuition_fee"
            )
        )

        previous_fee = parse_fee(
            row.get(
                "previous_tuition_fee"
            )
        )

        currency = normalize_text(
            row.get(
                "current_tuition_currency"
            )
        ).upper()

        period = normalize_text(
            row.get(
                "current_tuition_period"
            )
        )

        academic_year = normalize_text(
            row.get(
                "tuition_academic_year"
            )
        )

        student_scope = normalize_text(
            row.get(
                "tuition_student_scope"
            )
        )

        source_url = normalize_text(
            row.get(
                "tuition_source_url"
            )
        )

        verified_at = normalize_text(
            row.get(
                "tuition_last_verified_at"
            )
        )

        tuition_note = normalize_text(
            row.get(
                "tuition_note"
            )
        )

        change_required = normalize_text(
            row.get(
                "tuition_change_required"
            )
        ).upper()

        # ----------------------------------------------
        # Tuition
        # ----------------------------------------------

        if (
            current_fee is None
            or current_fee <= 0
        ):
            invalid_tuition_ids.append(
                program_id
            )

        else:
            tuition_distribution[
                current_fee
            ] += 1

        # ----------------------------------------------
        # Currency
        # ----------------------------------------------

        if currency != "JPY":
            invalid_currency_ids.append(
                program_id
            )

        # ----------------------------------------------
        # Period
        # ----------------------------------------------

        if period.lower() != "annual":
            invalid_period_ids.append(
                program_id
            )

        # ----------------------------------------------
        # Tuition Context
        # ----------------------------------------------

        missing_fields = []

        if not academic_year:
            missing_fields.append(
                "tuition_academic_year"
            )

        if not student_scope:
            missing_fields.append(
                "tuition_student_scope"
            )

        if not source_url:
            missing_fields.append(
                "tuition_source_url"
            )

        if not verified_at:
            missing_fields.append(
                "tuition_last_verified_at"
            )

        if not tuition_note:
            missing_fields.append(
                "tuition_note"
            )

        if missing_fields:
            missing_context_ids.append(
                (
                    program_id,
                    missing_fields,
                )
            )

        # ----------------------------------------------
        # Source URL
        # ----------------------------------------------

        if (
            source_url
            and not is_valid_url(
                source_url
            )
        ):
            invalid_source_ids.append(
                program_id
            )

        # ----------------------------------------------
        # Academic year
        # ----------------------------------------------

        if academic_year:
            academic_year_distribution[
                academic_year
            ] += 1

        # ----------------------------------------------
        # Change Flag
        # ----------------------------------------------

        if change_required == "YES":
            changed_ids.add(
                program_id
            )

            if (
                previous_fee is None
                or current_fee is None
                or previous_fee
                == current_fee
            ):
                invalid_change_flags.append(
                    program_id
                )

        elif change_required == "NO":
            if (
                previous_fee is not None
                and current_fee is not None
                and previous_fee
                != current_fee
            ):
                invalid_change_flags.append(
                    program_id
                )

        else:
            invalid_change_flags.append(
                program_id
            )

        # ----------------------------------------------
        # Special Tsukuba safety checks
        # ----------------------------------------------

        if program_id in EXPECTED_CHANGED_IDS:
            if (
                university_name
                != "University of Tsukuba"
            ):
                errors.append(
                    f"{program_id}: expected "
                    "University of Tsukuba, "
                    f"found {university_name}."
                )

            if (
                current_fee
                != EXPECTED_TSUKUBA_FEE
            ):
                errors.append(
                    f"{program_id}: expected "
                    f"{EXPECTED_TSUKUBA_FEE} JPY, "
                    f"found {current_fee}."
                )

            if academic_year != "2027":
                errors.append(
                    f"{program_id}: expected "
                    "tuition_academic_year 2027, "
                    f"found {academic_year}."
                )

    # ==================================================
    # COLLECT ERRORS
    # ==================================================

    if invalid_tuition_ids:
        errors.append(
            "Invalid tuition values: "
            + ", ".join(
                sorted(
                    invalid_tuition_ids
                )
            )
        )

    if invalid_currency_ids:
        errors.append(
            "Invalid/non-JPY currency: "
            + ", ".join(
                sorted(
                    invalid_currency_ids
                )
            )
        )

    if invalid_period_ids:
        errors.append(
            "Invalid/non-Annual period: "
            + ", ".join(
                sorted(
                    invalid_period_ids
                )
            )
        )

    if invalid_source_ids:
        errors.append(
            "Invalid tuition source URL: "
            + ", ".join(
                sorted(
                    invalid_source_ids
                )
            )
        )

    if missing_context_ids:
        for (
            program_id,
            missing_fields,
        ) in missing_context_ids:

            errors.append(
                f"{program_id}: missing "
                + ", ".join(
                    missing_fields
                )
            )

    if invalid_change_flags:
        errors.append(
            "Invalid tuition change audit "
            "flags: "
            + ", ".join(
                sorted(
                    set(
                        invalid_change_flags
                    )
                )
            )
        )

    # ==================================================
    # CHANGED RECORDS SAFETY CHECK
    # ==================================================

    if changed_ids != EXPECTED_CHANGED_IDS:
        errors.append(
            "Changed program IDs do not "
            "match expected set.\n"
            f"Expected: "
            f"{sorted(EXPECTED_CHANGED_IDS)}\n"
            f"Found: "
            f"{sorted(changed_ids)}"
        )

    # ==================================================
    # PRINT SUMMARY
    # ==================================================

    print()
    print("-" * 92)

    print(
        "VALIDATION SUMMARY"
    )

    print("-" * 92)

    print(
        "Total program records:",
        len(rows),
    )

    print(
        "Unique program IDs:",
        len(
            set(program_ids)
        ),
    )

    print(
        "Records with complete "
        "tuition context:",
        len(rows)
        - len(
            missing_context_ids
        ),
    )

    print(
        "Records marked "
        "tuition_change_required=YES:",
        len(changed_ids),
    )

    print()

    print(
        "Changed program IDs:"
    )

    for program_id in sorted(
        changed_ids
    ):
        print(
            " -",
            program_id,
        )

    # ==================================================
    # TUITION DISTRIBUTION
    # ==================================================

    print()
    print("-" * 92)

    print(
        "FINAL TUITION DISTRIBUTION"
    )

    print("-" * 92)

    for (
        fee,
        count,
    ) in (
        tuition_distribution
        .most_common()
    ):
        print(
            f"{count:>3} program(s)"
            f"  |  "
            f"{fee:,.0f} JPY / Annual"
        )

    # ==================================================
    # ACADEMIC YEAR DISTRIBUTION
    # ==================================================

    print()
    print("-" * 92)

    print(
        "TUITION ACADEMIC YEAR DISTRIBUTION"
    )

    print("-" * 92)

    for (
        academic_year,
        count,
    ) in sorted(
        academic_year_distribution.items()
    ):
        print(
            f"{academic_year}: "
            f"{count} program(s)"
        )

    # ==================================================
    # WARNINGS
    # ==================================================

    if warnings:
        print()
        print("-" * 92)

        print(
            "WARNINGS"
        )

        print("-" * 92)

        for warning in warnings:
            print(
                "WARNING:",
                warning,
            )

    # ==================================================
    # FINAL RESULT
    # ==================================================

    print()
    print("=" * 92)

    if errors:
        print(
            "FINAL VALIDATION: FAILED"
        )

        print("=" * 92)

        print()

        for index, error in enumerate(
            errors,
            start=1,
        ):
            print(
                f"{index}. {error}"
            )

        raise SystemExit(1)

    print(
        "FINAL VALIDATION: PASSED"
    )

    print()

    print(
        "36 / 36 Japan programs have "
        "complete tuition context."
    )

    print(
        "Exactly 3 Tsukuba AY2027 "
        "international tuition changes "
        "were detected."
    )

    print(
        "Verified CSV is ready for the "
        "controlled MongoDB update step."
    )

    print("=" * 92)


if __name__ == "__main__":
    main()