import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/japan_programs_tuition_enriched.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/japan_programs_language_enriched.csv"
)

AUDIT_PATH = Path(
    "planning/12_japan_program_language_audit.csv"
)

VERIFIED_AT = "2026-08-09"


# -------------------------------------------------
# Controlled language classifications
# -------------------------------------------------
#
# English
#   Official source explicitly supports a
#   fully English-taught degree/program.
#
# English Available
#   An official English degree pathway exists,
#   but this seed program is not automatically
#   English-only for every student.
#
# Mixed
#   English courses are available, but a complete
#   English-only degree is not confirmed.
#
# Japanese
#   Official source states the standard program
#   is basically conducted in Japanese.
#
# Unknown
#   Official source was checked, but the language
#   of instruction could not be established safely.
# -------------------------------------------------


ENGLISH_PROGRAMS = {
    # Kyushu University international programs
    "prog_jp_016",
    "prog_jp_017",
    "prog_jp_018",

    # University of Tsukuba
    # Computer Science English Program
    "prog_jp_025",

    # Keio International Graduate Program
    "prog_jp_034",
    "prog_jp_035",
}


ENGLISH_AVAILABLE_PROGRAMS = {
    # UTokyo English Program in IST
    "prog_jp_001",
    "prog_jp_002",
    "prog_jp_003",

    # Kyoto International Program
    "prog_jp_004",
    "prog_jp_005",

    # Science Tokyo International Graduate Program
    "prog_jp_022",
    "prog_jp_023",
    "prog_jp_024",

    # Waseda English-based graduate programs
    "prog_jp_031",
    "prog_jp_032",
    "prog_jp_033",

    # Keio Double Degree pathway
    "prog_jp_036",
}


MIXED_PROGRAMS = {
    # Kyoto Data Science:
    # English courses exist in the graduate school,
    # but the full English International Program
    # is not confirmed for this course.
    "prog_jp_006",

    # Kobe:
    # English courses are confirmed,
    # but a complete English-only degree is
    # not confirmed from the source used.
    "prog_jp_028",
    "prog_jp_029",
    "prog_jp_030",
}


JAPANESE_PROGRAMS = {
    # Osaka regular Master's majors.
    # The official admissions page states that
    # Master's classes other than ITSCE are
    # basically conducted in Japanese.
    "prog_jp_007",
    "prog_jp_008",
    "prog_jp_009",
}


UNKNOWN_PROGRAMS = {
    # Tohoku
    "prog_jp_010",
    "prog_jp_011",
    "prog_jp_012",

    # Nagoya
    "prog_jp_013",
    "prog_jp_014",
    "prog_jp_015",

    # Hokkaido
    "prog_jp_019",
    "prog_jp_020",
    "prog_jp_021",

    # Tsukuba IMIS / Empowerment Informatics
    "prog_jp_026",
    "prog_jp_027",
}


SOURCE_INFO = {
    "uni_jp_001": {
        "source_name": (
            "UTokyo English Program "
            "in Information Science and Technology"
        ),
        "source_url": (
            "https://www.i.u-tokyo.ac.jp/"
            "ist_en/en-course/prg_e.shtml"
        ),
    },

    "uni_jp_002": {
        "source_name": (
            "Kyoto University Graduate School "
            "of Informatics International Program"
        ),
        "source_url": (
            "https://www.i.kyoto-u.ac.jp/"
            "en/education/intl_program/"
        ),
    },

    "uni_jp_003": {
        "source_name": (
            "Osaka University IST "
            "Application Guides 2026"
        ),
        "source_url": (
            "https://www.ist.osaka-u.ac.jp/"
            "english/examinees/admission/"
            "guidelines2026.php"
        ),
    },

    "uni_jp_004": {
        "source_name": (
            "Tohoku University Graduate School "
            "of Information Sciences"
        ),
        "source_url": (
            "https://www.is.tohoku.ac.jp/en/"
        ),
    },

    "uni_jp_005": {
        "source_name": (
            "Nagoya University Graduate School "
            "of Informatics"
        ),
        "source_url": (
            "https://www.i.nagoya-u.ac.jp/"
            "en/gs/entranceexamination/admission-en/"
        ),
    },

    "uni_jp_006": {
        "source_name": (
            "Kyushu University "
            "International Graduate Programs"
        ),
        "source_url": (
            "https://www.isc.kyushu-u.ac.jp/"
            "graduate/"
        ),
    },

    "uni_jp_007": {
        "source_name": (
            "Hokkaido University Graduate School "
            "of Information Science and Technology"
        ),
        "source_url": (
            "https://www.ist.hokudai.ac.jp/eng/"
        ),
    },

    "uni_jp_008": {
        "source_name": (
            "Science Tokyo "
            "International Graduate Programs"
        ),
        "source_url": (
            "https://admissions.isct.ac.jp/en/"
            "013/graduate/programs/"
            "science-and-engineering"
        ),
    },

    "uni_jp_009": {
        "source_name": (
            "University of Tsukuba "
            "Systems and Information Engineering"
        ),
        "source_url": (
            "https://www.sie.tsukuba.ac.jp/eng/"
        ),
    },

    "uni_jp_010": {
        "source_name": (
            "Kobe University Graduate School "
            "of System Informatics"
        ),
        "source_url": (
            "https://www.csi.kobe-u.ac.jp/"
            "assets/files/brochureENG.pdf"
        ),
    },

    "uni_jp_011": {
        "source_name": (
            "Waseda University "
            "English-based Graduate Programs"
        ),
        "source_url": (
            "https://www.waseda.jp/"
            "inst/admission/en/graduate/english"
        ),
    },

    "uni_jp_012": {
        "source_name": (
            "Keio University "
            "Degree Programs Offered in English"
        ),
        "source_url": (
            "https://www.keio.ac.jp/en/"
            "admissions/international-student/"
            "programs-offered-in-english/"
        ),
    },
}


PROGRAM_SOURCE_OVERRIDES = {
    "prog_jp_025": {
        "source_name": (
            "University of Tsukuba "
            "Computer Science English Program"
        ),
        "source_url": (
            "https://www.cs.tsukuba.ac.jp/cse/"
        ),
    },

    "prog_jp_026": {
        "source_name": (
            "University of Tsukuba "
            "Intelligent and Mechanical "
            "Interaction Systems"
        ),
        "source_url": (
            "https://www.sie.tsukuba.ac.jp/"
            "eng/edu/course/imis/"
        ),
    },

    "prog_jp_027": {
        "source_name": (
            "University of Tsukuba "
            "Empowerment Informatics"
        ),
        "source_url": (
            "https://www.emp.tsukuba.ac.jp/english"
        ),
    },
}


def get_language(
    program_id: str,
) -> str:
    if program_id in ENGLISH_PROGRAMS:
        return "English"

    if program_id in ENGLISH_AVAILABLE_PROGRAMS:
        return "English Available"

    if program_id in MIXED_PROGRAMS:
        return "Mixed"

    if program_id in JAPANESE_PROGRAMS:
        return "Japanese"

    if program_id in UNKNOWN_PROGRAMS:
        return "Unknown"

    raise ValueError(
        f"No language classification for "
        f"{program_id}"
    )


def get_source(
    program_id: str,
    university_id: str,
) -> dict:
    if (
        program_id
        in PROGRAM_SOURCE_OVERRIDES
    ):
        return PROGRAM_SOURCE_OVERRIDES[
            program_id
        ]

    source = SOURCE_INFO.get(
        university_id
    )

    if source is None:
        raise ValueError(
            f"No language source for "
            f"{university_id}"
        )

    return source


def get_reason(
    language: str,
) -> str:
    reasons = {
        "English": (
            "Official source explicitly confirms "
            "an English-taught degree/program."
        ),

        "English Available": (
            "Official source confirms an English "
            "degree pathway, but this program "
            "record is not treated as universally "
            "English-only."
        ),

        "Mixed": (
            "Official source confirms English "
            "course availability, but does not "
            "confirm the whole degree as "
            "English-only."
        ),

        "Japanese": (
            "Official source states the regular "
            "program is basically conducted "
            "in Japanese."
        ),

        "Unknown": (
            "Official source was reviewed, but "
            "it does not provide enough evidence "
            "to assign a full language-of-"
            "instruction classification."
        ),
    }

    return reasons[
        language
    ]


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

        university_id = row[
            "university_id"
        ].strip()

        language = get_language(
            program_id
        )

        source = get_source(
            program_id,
            university_id,
        )

        row[
            "language_of_instruction"
        ] = language

        row[
            "last_verified_at"
        ] = VERIFIED_AT

        existing_freshness = row.get(
            "freshness_status",
            "",
        ).strip()

        if language == "Unknown":
            language_freshness = (
                "Language Checked - "
                "Not Fully Verified"
            )
        else:
            language_freshness = (
                "Language Classification Verified"
            )

        if existing_freshness:
            row[
                "freshness_status"
            ] = (
                f"{existing_freshness}; "
                f"{language_freshness}"
            )
        else:
            row[
                "freshness_status"
            ] = language_freshness

        audit_rows.append(
            {
                "program_id": program_id,
                "university_id": (
                    university_id
                ),
                "program_name": row[
                    "program_name"
                ],
                "language_classification": (
                    language
                ),
                "source_name": source[
                    "source_name"
                ],
                "source_url": source[
                    "source_url"
                ],
                "verified_at": (
                    VERIFIED_AT
                ),
                "reason": get_reason(
                    language
                ),
            }
        )

    # ---------------------------------
    # Verify all 36 were classified
    # ---------------------------------

    blank_languages = [
        row["program_id"]
        for row in rows
        if not row[
            "language_of_instruction"
        ].strip()
    ]

    if blank_languages:
        raise ValueError(
            "Missing language for: "
            + ", ".join(
                blank_languages
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
        writer.writerows(rows)

    # ---------------------------------
    # Save audit evidence
    # ---------------------------------

    AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    audit_headers = [
        "program_id",
        "university_id",
        "program_name",
        "language_classification",
        "source_name",
        "source_url",
        "verified_at",
        "reason",
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

    language_counts = {}

    for row in rows:
        language = row[
            "language_of_instruction"
        ]

        language_counts[
            language
        ] = (
            language_counts.get(
                language,
                0,
            )
            + 1
        )

    print(
        "=== Japan Program Language "
        "Enrichment Complete ==="
    )

    print(
        f"Programs checked: "
        f"{len(rows)}"
    )

    print()

    print(
        "Language classification:"
    )

    for language, count in sorted(
        language_counts.items()
    ):
        print(
            f"  {language}: "
            f"{count}"
        )

    print()

    print(
        f"Dataset: {OUTPUT_PATH}"
    )

    print(
        f"Audit file: {AUDIT_PATH}"
    )

    print(
        "Verification: "
        "language_of_instruction "
        "classified for all 36 records."
    )


if __name__ == "__main__":
    main()