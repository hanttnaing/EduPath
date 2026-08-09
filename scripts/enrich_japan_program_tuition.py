import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/japan_programs_fields_enriched.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/japan_programs_tuition_enriched.csv"
)

AUDIT_PATH = Path(
    "planning/11_japan_program_tuition_audit.csv"
)

VERIFIED_AT = "2026-08-09"


TUITION_CONFIG = {
    "uni_jp_001": {
        "default": 535800,
        "PhD": 520800,
        "source_name": "The University of Tokyo Tuition Fee",
        "source_url": (
            "https://www.u-tokyo.ac.jp/"
            "en/prospective-students/tuition_fees.html"
        ),
        "note": "Current published graduate tuition.",
    },

    "uni_jp_002": {
        "default": 535800,
        "source_name": "Kyoto University Tuition and Fees",
        "source_url": (
            "https://www.kyoto-u.ac.jp/"
            "en/current/how-to/tuition/tuition-and-fees"
        ),
        "note": "Current graduate annual tuition.",
    },

    "uni_jp_003": {
        "default": 535800,
        "source_name": "The University of Osaka Tuition Fees",
        "source_url": (
            "https://www.osaka-u.ac.jp/"
            "en/campus/tuition/tuition.html"
        ),
        "note": "Current graduate annual tuition.",
    },

    "uni_jp_004": {
        "default": 535800,
        "source_name": "Tohoku University Fees and Expenses",
        "source_url": (
            "https://www.tohoku.ac.jp/"
            "en/admissions/tutition_fees.html"
        ),
        "note": "Current graduate annual tuition.",
    },

    "uni_jp_005": {
        "default": 535800,
        "source_name": "Nagoya University Tuition Fees",
        "source_url": (
            "https://en.nagoya-u.ac.jp/"
            "admissions/financial/tuition/"
        ),
        "note": "Current graduate annual tuition.",
    },

    "uni_jp_006": {
        "default": 535800,
        "source_name": "Kyushu University Tuition Payment",
        "source_url": (
            "https://www.kyushu-u.ac.jp/"
            "en/admission/fees/payment/"
        ),
        "note": "Graduate tuition is 267900 JPY per semester.",
    },

    "uni_jp_007": {
        "default": 535800,
        "source_name": "Hokkaido University Tuition",
        "source_url": (
            "https://intl-student-handbook.oia."
            "hokudai.ac.jp/en/campus_life-en/tuition"
        ),
        "note": "AY2026 graduate annual tuition.",
    },

    "uni_jp_008": {
        "default": 635400,
        "source_name": "Science Tokyo Tuition and Fees",
        "source_url": (
            "https://www.titech.ac.jp/"
            "english/student/students/tuition/tuition"
        ),
        "note": (
            "Science and Engineering master's and "
            "doctoral entrants from Sep 2019 onward."
        ),
    },

    "uni_jp_009": {
        "default": 535800,
        "source_name": "University of Tsukuba Tuition",
        "source_url": (
            "https://informatics.tsukuba.ac.jp/"
            "en/admission-information-en/admission/fees/"
        ),
        "note": (
            "AY2026 tuition. AY2027 tuition revision "
            "has been announced; refresh required."
        ),
    },

    "uni_jp_010": {
        "default": 535800,
        "source_name": "Kobe University Tuition",
        "source_url": (
            "https://www.kobe-u.ac.jp/"
            "en/campus-life/tuition/about/"
        ),
        "note": (
            "Current undergraduate and graduate "
            "annual tuition."
        ),
    },

    "uni_jp_011": {
        "default": 991000,
        "source_name": (
            "Waseda University AY2026 "
            "Master's Expenses"
        ),
        "source_url": (
            "https://www.waseda.jp/inst/admission/"
            "assets/uploads/2025/06/"
            "Masters-Professional-Expenses-AY2026.pdf"
        ),
        "note": (
            "Graduate School of Fundamental "
            "Science and Engineering tuition only."
        ),
    },

    "uni_jp_012": {
        "Master": 1160000,
        "PhD": 740000,
        "source_name": (
            "Keio University AY2026 "
            "Graduate Academic Fees"
        ),
        "source_url": (
            "https://www.keio.ac.jp/"
            "en/admissions/fee/grad/"
        ),
        "note": (
            "Graduate School of Science and Technology."
        ),
    },
}


def get_tuition(
    university_id: str,
    degree_level: str,
) -> int:
    config = TUITION_CONFIG.get(
        university_id
    )

    if config is None:
        raise ValueError(
            f"No tuition configuration for "
            f"{university_id}"
        )

    if degree_level in config:
        return int(
            config[degree_level]
        )

    if "default" in config:
        return int(
            config["default"]
        )

    raise ValueError(
        f"No tuition rule for "
        f"{university_id} / {degree_level}"
    )


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

        university_id = row[
            "university_id"
        ].strip()

        degree_level = row[
            "degree_level"
        ].strip()

        tuition_fee = get_tuition(
            university_id,
            degree_level,
        )

        config = TUITION_CONFIG[
            university_id
        ]

        row["tuition_fee"] = str(
            tuition_fee
        )

        row["tuition_currency"] = "JPY"

        row["tuition_period"] = "Annual"

        row[
            "last_verified_at"
        ] = VERIFIED_AT

        if university_id == "uni_jp_009":
            row[
                "freshness_status"
            ] = (
                "Partial - AY2026 Tuition Verified; "
                "AY2027 Change Announced"
            )
        else:
            row[
                "freshness_status"
            ] = (
                "Partial - Tuition Verified"
            )

        audit_rows.append(
            {
                "program_id": program_id,
                "university_id": university_id,
                "program_name": row[
                    "program_name"
                ],
                "degree_level": degree_level,
                "tuition_fee": tuition_fee,
                "tuition_currency": "JPY",
                "tuition_period": "Annual",
                "source_name": config[
                    "source_name"
                ],
                "source_url": config[
                    "source_url"
                ],
                "verified_at": VERIFIED_AT,
                "note": config[
                    "note"
                ],
            }
        )

    missing_tuition = [
        row["program_id"]
        for row in rows
        if not row[
            "tuition_fee"
        ].strip()
    ]

    if missing_tuition:
        raise ValueError(
            "Missing tuition for: "
            + ", ".join(
                missing_tuition
            )
        )

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
        writer.writerows(rows)

    AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    audit_headers = [
        "program_id",
        "university_id",
        "program_name",
        "degree_level",
        "tuition_fee",
        "tuition_currency",
        "tuition_period",
        "source_name",
        "source_url",
        "verified_at",
        "note",
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

    tuition_counts = {}

    for row in rows:
        fee = row[
            "tuition_fee"
        ]

        tuition_counts[fee] = (
            tuition_counts.get(
                fee,
                0,
            )
            + 1
        )

    print(
        "=== Japan Tuition Enrichment Complete ==="
    )

    print(
        f"Programs enriched: {len(rows)}"
    )

    print(
        f"Programs with tuition: "
        f"{len(rows) - len(missing_tuition)}"
    )

    print()

    print("Tuition distribution:")

    for fee, count in sorted(
        tuition_counts.items(),
        key=lambda item: int(
            item[0]
        ),
    ):
        print(
            f"  {fee} JPY/year: "
            f"{count} programs"
        )

    print()

    print(
        f"Dataset: {OUTPUT_PATH}"
    )

    print(
        f"Audit file: {AUDIT_PATH}"
    )

    print(
        "Verification: tuition_fee, "
        "tuition_currency and "
        "tuition_period complete "
        "for all 36 records."
    )


if __name__ == "__main__":
    main()