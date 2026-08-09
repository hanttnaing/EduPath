import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/japan_programs_language_enriched.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/japan_programs_duration_mode_enriched.csv"
)

AUDIT_PATH = Path(
    "planning/13_japan_program_duration_mode_audit.csv"
)

VERIFIED_AT = "2026-08-09"


# -------------------------------------------------
# Standard duration rules
# -------------------------------------------------

STANDARD_DURATION = {
    "Bachelor": 4,
    "Master": 2,
    "PhD": 3,
}


# -------------------------------------------------
# Program-specific duration exceptions
# -------------------------------------------------

DURATION_OVERRIDES = {
    # University of Tsukuba
    # Empowerment Informatics is a
    # five-year integrated doctoral program.
    "prog_jp_027": 5,
}


# -------------------------------------------------
# Official duration sources
# -------------------------------------------------

GENERAL_BACHELOR_SOURCE = {
    "source_name": (
        "Study in Japan - "
        "Universities Undergraduate"
    ),
    "source_url": (
        "https://www.studyinjapan.go.jp/"
        "en/planning/learn-about-schools/"
        "universities/"
    ),
    "reason": (
        "Undergraduate university programs "
        "generally require four years."
    ),
}


GENERAL_GRADUATE_SOURCE = {
    "source_name": (
        "Study in Japan - Graduate Schools"
    ),
    "source_url": (
        "https://www.studyinjapan.go.jp/"
        "en/planning/learn-about-schools/"
        "graduate-schools/"
    ),
    "reason": (
        "Master's programs generally require "
        "two years. Standard doctoral latter "
        "stages are generally three years."
    ),
}


PROGRAM_SOURCE_OVERRIDES = {
    "prog_jp_027": {
        "source_name": (
            "University of Tsukuba "
            "Empowerment Informatics FAQ"
        ),
        "source_url": (
            "https://www.emp.tsukuba.ac.jp/"
            "faq_en"
        ),
        "reason": (
            "Empowerment Informatics is a "
            "five-year integrated doctoral "
            "degree program."
        ),
    },

    "prog_jp_034": {
        "source_name": (
            "Keio International Graduate "
            "Program Master's"
        ),
        "source_url": (
            "https://www.keio.ac.jp/"
            "en/st/admissions-en/"
            "masters_program/"
        ),
        "reason": (
            "Keio Graduate School of "
            "Science and Technology offers "
            "a two-year Master's program."
        ),
    },

    "prog_jp_035": {
        "source_name": (
            "Keio International Graduate "
            "Program Doctoral"
        ),
        "source_url": (
            "https://www.keio.ac.jp/"
            "en/st/admissions-en/"
            "phd_program/"
        ),
        "reason": (
            "Keio Graduate School of "
            "Science and Technology offers "
            "a three-year doctoral program."
        ),
    },

    "prog_jp_036": {
        "source_name": (
            "Keio Double Degree Program"
        ),
        "source_url": (
            "https://www.keio.ac.jp/"
            "en/st/admissions-en/dd/"
        ),
        "reason": (
            "Completion of the Master's "
            "Program requires at least "
            "two academic years."
        ),
    },
}


def get_duration(
    program_id: str,
    degree_level: str,
) -> int:
    if program_id in DURATION_OVERRIDES:
        return DURATION_OVERRIDES[
            program_id
        ]

    duration = STANDARD_DURATION.get(
        degree_level
    )

    if duration is None:
        raise ValueError(
            f"No duration rule for "
            f"{program_id} / {degree_level}"
        )

    return duration


def get_duration_source(
    program_id: str,
    degree_level: str,
) -> dict:
    if (
        program_id
        in PROGRAM_SOURCE_OVERRIDES
    ):
        return PROGRAM_SOURCE_OVERRIDES[
            program_id
        ]

    if degree_level == "Bachelor":
        return GENERAL_BACHELOR_SOURCE

    if degree_level in {
        "Master",
        "PhD",
    }:
        return GENERAL_GRADUATE_SOURCE

    raise ValueError(
        f"No duration source for "
        f"{program_id}"
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

        fieldnames = reader.fieldnames

        if fieldnames is None:
            raise ValueError(
                "Input CSV has no headers."
            )

        rows = list(reader)

    if len(rows) != 36:
        raise ValueError(
            "Expected exactly 36 "
            "Japan program records."
        )

    audit_rows = []

    for row in rows:
        program_id = row[
            "program_id"
        ].strip()

        degree_level = row[
            "degree_level"
        ].strip()

        university_id = row[
            "university_id"
        ].strip()

        duration = get_duration(
            program_id,
            degree_level,
        )

        source = get_duration_source(
            program_id,
            degree_level,
        )

        # ---------------------------------
        # Verified duration
        # ---------------------------------

        row[
            "duration_years"
        ] = str(duration)

        # ---------------------------------
        # Study mode normalization
        # ---------------------------------
        #
        # This is an EduPath analytical
        # normalization for regular degree
        # programs. It is NOT a claim that
        # the university has no alternative
        # part-time / online pathway.
        # ---------------------------------

        row[
            "study_mode"
        ] = "Full-time"

        row[
            "last_verified_at"
        ] = VERIFIED_AT

        existing_freshness = row.get(
            "freshness_status",
            "",
        ).strip()

        addition = (
            "Duration Verified; "
            "Study Mode Normalized"
        )

        if existing_freshness:
            row[
                "freshness_status"
            ] = (
                f"{existing_freshness}; "
                f"{addition}"
            )
        else:
            row[
                "freshness_status"
            ] = addition

        audit_rows.append(
            {
                "program_id": program_id,
                "university_id": (
                    university_id
                ),
                "program_name": row[
                    "program_name"
                ],
                "degree_level": (
                    degree_level
                ),
                "duration_years": (
                    duration
                ),
                "study_mode": (
                    "Full-time"
                ),
                "duration_source_name": (
                    source[
                        "source_name"
                    ]
                ),
                "duration_source_url": (
                    source[
                        "source_url"
                    ]
                ),
                "duration_reason": (
                    source[
                        "reason"
                    ]
                ),
                "study_mode_basis": (
                    "EduPath normalization "
                    "for regular degree "
                    "program records; "
                    "not an official claim "
                    "that no alternative "
                    "study mode exists."
                ),
                "verified_at": (
                    VERIFIED_AT
                ),
            }
        )

    # ---------------------------------
    # Verify completeness
    # ---------------------------------

    missing_duration = [
        row["program_id"]
        for row in rows
        if not row[
            "duration_years"
        ].strip()
    ]

    missing_mode = [
        row["program_id"]
        for row in rows
        if not row[
            "study_mode"
        ].strip()
    ]

    if missing_duration:
        raise ValueError(
            "Missing duration for: "
            + ", ".join(
                missing_duration
            )
        )

    if missing_mode:
        raise ValueError(
            "Missing study mode for: "
            + ", ".join(
                missing_mode
            )
        )

    # ---------------------------------
    # Save enriched dataset
    # ---------------------------------

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
            rows
        )

    # ---------------------------------
    # Save audit file
    # ---------------------------------

    AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    audit_headers = [
        "program_id",
        "university_id",
        "program_name",
        "degree_level",
        "duration_years",
        "study_mode",
        "duration_source_name",
        "duration_source_url",
        "duration_reason",
        "study_mode_basis",
        "verified_at",
    ]

    with AUDIT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=audit_headers,
        )

        writer.writeheader()
        writer.writerows(
            audit_rows
        )

    # ---------------------------------
    # Summary
    # ---------------------------------

    duration_counts = {}

    for row in rows:
        duration = row[
            "duration_years"
        ]

        duration_counts[
            duration
        ] = (
            duration_counts.get(
                duration,
                0,
            )
            + 1
        )

    print(
        "=== Japan Program Duration + "
        "Mode Enrichment Complete ==="
    )

    print(
        f"Programs enriched: "
        f"{len(rows)}"
    )

    print()

    print("Duration distribution:")

    for duration, count in sorted(
        duration_counts.items(),
        key=lambda item: float(
            item[0]
        ),
    ):
        print(
            f"  {duration} years: "
            f"{count} programs"
        )

    print()

    print(
        "Study mode:"
    )

    print(
        "  Full-time: "
        f"{len(rows)} programs"
    )

    print()

    print(
        f"Dataset: {OUTPUT_PATH}"
    )

    print(
        f"Audit file: {AUDIT_PATH}"
    )

    print(
        "Verification: duration_years "
        "and study_mode complete "
        "for all 36 records."
    )


if __name__ == "__main__":
    main()