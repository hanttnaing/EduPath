import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "japan_programs_duration_mode_enriched.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "japan_programs_requirements_enriched.csv"
)

AUDIT_PATH = Path(
    "planning/"
    "14_japan_program_requirements_audit.csv"
)

VERIFIED_AT = "2026-08-09"


# -------------------------------------------------
# University-level requirement evidence
# -------------------------------------------------
#
# IMPORTANT:
# These are NOT numeric minimum scores unless
# explicitly stated by the official source.
#
# The master dataset's GPA / IELTS / TOEFL
# columns are reserved for real numeric cutoffs.
# -------------------------------------------------

UNIVERSITY_REQUIREMENTS = {
    "uni_jp_001": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "TOEFL score used in admission"
        ),
        "accepted_tests": "TOEFL",
        "numeric_minimum": (
            "No universal cutoff verified"
        ),
        "source_url": (
            "https://www.i.u-tokyo.ac.jp/"
            "edu/entra/entra_e.shtml"
        ),
        "note": (
            "AY2027 IST admission uses TOEFL "
            "scores. A universal minimum score "
            "is not stored because one has not "
            "been verified for all seed programs."
        ),
    },

    "uni_jp_002": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "English proficiency requirements "
            "depend on admission route"
        ),
        "accepted_tests": (
            "See current admission guide"
        ),
        "numeric_minimum": (
            "No universal cutoff applied"
        ),
        "source_url": (
            "https://www.i.kyoto-u.ac.jp/"
            "en/admission/"
        ),
        "note": (
            "Admission requirements vary by "
            "course and admission route."
        ),
    },

    "uni_jp_003": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "External English test handling "
            "is major/exam specific"
        ),
        "accepted_tests": (
            "TOEFL / TOEIC depending on guide"
        ),
        "numeric_minimum": (
            "No universal cutoff applied"
        ),
        "source_url": (
            "https://www.ist.osaka-u.ac.jp/"
            "english/examinees/admission/"
            "guidelines2027.php"
        ),
        "note": (
            "Use the relevant AY2027 "
            "application guide for each major."
        ),
    },

    "uni_jp_004": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "English score sheet commonly required"
        ),
        "accepted_tests": "TOEFL / TOEIC",
        "numeric_minimum": (
            "No universal cutoff applied"
        ),
        "source_url": (
            "https://www.is.tohoku.ac.jp/"
            "en/news/exam/"
        ),
        "note": (
            "Requirements can differ by "
            "admission schedule and laboratory."
        ),
    },

    "uni_jp_005": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "Program-specific verification required"
        ),
        "accepted_tests": "Needs Review",
        "numeric_minimum": (
            "Not safely verified"
        ),
        "source_url": (
            "https://www.i.nagoya-u.ac.jp/"
            "en/gs/entranceexamination/"
            "admission-en/"
        ),
        "note": (
            "Do not assign numeric GPA or "
            "English cutoffs without the "
            "current program-specific guide."
        ),
    },

    "uni_jp_006": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "English requirement depends "
            "on international program"
        ),
        "accepted_tests": "TOEFL / IELTS",
        "numeric_minimum": (
            "No single cutoff applied to "
            "all three seed programs"
        ),
        "source_url": (
            "https://isc.kyushu-u.ac.jp/"
            "graduate/"
        ),
        "note": (
            "Do not apply a general university "
            "score to every graduate program."
        ),
    },

    "uni_jp_007": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "External English score used "
            "for Master's admission"
        ),
        "accepted_tests": (
            "TOEIC / TOEFL / IELTS"
        ),
        "numeric_minimum": (
            "No universal cutoff verified"
        ),
        "source_url": (
            "https://www.ist.hokudai.ac.jp/"
            "examinfo/"
        ),
        "note": (
            "External English scores are "
            "used in the English examination."
        ),
    },

    "uni_jp_008": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "External English test used "
            "in graduate selection"
        ),
        "accepted_tests": (
            "Check current graduate guide"
        ),
        "numeric_minimum": (
            "No universal cutoff applied"
        ),
        "source_url": (
            "https://admissions.isct.ac.jp/"
            "en/013/graduate"
        ),
        "note": (
            "Requirements differ by school, "
            "major and admission route."
        ),
    },

    "uni_jp_009": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "Program-specific language "
            "evidence required"
        ),
        "accepted_tests": (
            "Program-specific"
        ),
        "numeric_minimum": (
            "No generic cutoff applied"
        ),
        "source_url": (
            "https://www.sie.tsukuba.ac.jp/"
            "eng/"
        ),
        "note": (
            "Special international programs "
            "may have separate language rules. "
            "Do not transfer those cutoffs to "
            "the general Computer Science record."
        ),
    },

    "uni_jp_010": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "Admission-route specific"
        ),
        "accepted_tests": "Needs Review",
        "numeric_minimum": (
            "Not safely verified"
        ),
        "source_url": (
            "https://www.csi.kobe-u.ac.jp/"
            "english/"
        ),
        "note": (
            "Keep numeric requirement fields "
            "blank until a current applicable "
            "admission guide is verified."
        ),
    },

    "uni_jp_011": {
        "gpa_status": (
            "No admission GPA minimum verified"
        ),
        "english_status": (
            "English score may be required; "
            "no minimum cutoff"
        ),
        "accepted_tests": (
            "TOEIC / TOEFL iBT / IELTS Academic"
        ),
        "numeric_minimum": (
            "No minimum; recommended scores only"
        ),
        "source_url": (
            "https://www.waseda.jp/fsci/"
            "en/admissions_gs"
        ),
        "note": (
            "TOEFL 79 and IELTS 6.5 are "
            "recommended values, not minimum "
            "admission cutoffs. Therefore they "
            "must not be stored in numeric "
            "minimum requirement columns."
        ),
    },

    "uni_jp_012": {
        "gpa_status": (
            "No universal numeric minimum verified"
        ),
        "english_status": (
            "Depends on Keio admission pathway"
        ),
        "accepted_tests": "TOEFL / IELTS",
        "numeric_minimum": (
            "IGP Master's has no minimum cutoff"
        ),
        "source_url": (
            "https://www.keio.ac.jp/"
            "en/st/admissions-en/faq/"
        ),
        "note": (
            "IGP Master's accepts TOEFL or IELTS "
            "but sets no minimum score. "
            "IGP Doctoral applicants do not "
            "need English/GRE scores."
        ),
    },
}


# -------------------------------------------------
# Program-specific overrides
# -------------------------------------------------

PROGRAM_OVERRIDES = {
    # Keio International Graduate Program Doctoral
    "prog_jp_035": {
        "english_status": (
            "English test not required"
        ),
        "accepted_tests": "Not Required",
        "numeric_minimum": "Not Applicable",
        "note": (
            "Keio IGP Doctoral applicants "
            "are not required to submit "
            "English or GRE scores."
        ),
    },

    # Keio Double Degree
    "prog_jp_036": {
        "english_status": (
            "TOEFL / IELTS not required"
        ),
        "accepted_tests": "Not Required",
        "numeric_minimum": "Not Applicable",
        "note": (
            "Keio Double Degree applicants "
            "are not required to submit "
            "TOEFL/IELTS or GRE scores."
        ),
    },
}


def get_requirement_info(
    program_id: str,
    university_id: str,
) -> dict:

    base = UNIVERSITY_REQUIREMENTS.get(
        university_id
    )

    if base is None:
        raise ValueError(
            f"No requirement evidence for "
            f"{university_id}"
        )

    result = dict(base)

    override = PROGRAM_OVERRIDES.get(
        program_id
    )

    if override:
        result.update(
            override
        )

    return result


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

        requirement = get_requirement_info(
            program_id,
            university_id,
        )

        # ---------------------------------
        # Numeric minimum fields
        # ---------------------------------
        #
        # Do NOT insert recommended scores,
        # score-submission requirements,
        # scholarship GPA thresholds, or
        # inferred values here.
        #
        # These fields remain blank unless
        # a true program-level numeric
        # minimum is verified.
        # ---------------------------------

        row["minimum_gpa"] = ""
        row["gpa_scale"] = ""
        row["ielts_requirement"] = ""
        row["toefl_requirement"] = ""

        row[
            "last_verified_at"
        ] = VERIFIED_AT

        existing_freshness = row.get(
            "freshness_status",
            "",
        ).strip()

        requirement_flag = (
            "Admission Requirements Reviewed; "
            "No Unverified Numeric Cutoffs Stored"
        )

        if existing_freshness:
            row[
                "freshness_status"
            ] = (
                f"{existing_freshness}; "
                f"{requirement_flag}"
            )
        else:
            row[
                "freshness_status"
            ] = requirement_flag

        audit_rows.append(
            {
                "program_id": program_id,
                "university_id": university_id,
                "program_name": row[
                    "program_name"
                ],
                "degree_level": row[
                    "degree_level"
                ],
                "gpa_status": requirement[
                    "gpa_status"
                ],
                "english_status": requirement[
                    "english_status"
                ],
                "accepted_tests": requirement[
                    "accepted_tests"
                ],
                "numeric_minimum_status": (
                    requirement[
                        "numeric_minimum"
                    ]
                ),
                "minimum_gpa_stored": "",
                "gpa_scale_stored": "",
                "ielts_minimum_stored": "",
                "toefl_minimum_stored": "",
                "source_url": requirement[
                    "source_url"
                ],
                "verified_at": VERIFIED_AT,
                "note": requirement[
                    "note"
                ],
            }
        )

    # ---------------------------------
    # Save dataset
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
        "degree_level",
        "gpa_status",
        "english_status",
        "accepted_tests",
        "numeric_minimum_status",
        "minimum_gpa_stored",
        "gpa_scale_stored",
        "ielts_minimum_stored",
        "toefl_minimum_stored",
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

    print(
        "=== Japan Admission Requirements "
        "Review Complete ==="
    )

    print(
        f"Programs reviewed: "
        f"{len(rows)}"
    )

    print()
    print(
        "Numeric requirement policy:"
    )
    print(
        "  GPA minimum: "
        "blank unless explicitly verified"
    )
    print(
        "  IELTS minimum: "
        "blank unless explicitly verified"
    )
    print(
        "  TOEFL minimum: "
        "blank unless explicitly verified"
    )

    print()
    print(
        f"Dataset: {OUTPUT_PATH}"
    )
    print(
        f"Audit file: {AUDIT_PATH}"
    )

    print()
    print(
        "Verification: no recommended, "
        "scholarship-only or inferred "
        "scores were stored as admission "
        "minimums."
    )


if __name__ == "__main__":
    main()