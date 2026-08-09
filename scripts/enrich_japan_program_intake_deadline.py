import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/"
    "japan_programs_requirements_enriched.csv"
)

OUTPUT_PATH = Path(
    "data/cleaned/"
    "japan_programs_intake_deadline_enriched.csv"
)

AUDIT_PATH = Path(
    "planning/"
    "15_japan_program_intake_deadline_audit.csv"
)

VERIFIED_AT = "2026-08-09"


# -------------------------------------------------
# Directly storable schedules
# -------------------------------------------------
#
# Only store values when the currently published
# official admission information can be linked
# safely to the seed program / admission route.
#
# We do NOT force a single deadline into the
# master dataset when multiple admission rounds
# or department-specific schedules exist.
# -------------------------------------------------

DIRECT_RULES = {
    # ---------------------------------------------
    # Tohoku University
    # Graduate School of Information Sciences
    # AY2027 Two-Year Master's Program
    # ---------------------------------------------
    "prog_jp_010": {
        "intake": "April 2027",
        "deadline": "2026-07-08",
        "source_name": (
            "Tohoku University GSIS "
            "2027 Two-Year Master's Admission"
        ),
        "source_url": (
            "https://www.math.is.tohoku.ac.jp/"
            "english/admission/index.html"
        ),
        "note": (
            "AY2027 Master's application period "
            "was June 26 to July 8, 2026."
        ),
    },
    "prog_jp_011": {
        "intake": "April 2027",
        "deadline": "2026-07-08",
        "source_name": (
            "Tohoku University GSIS "
            "2027 Two-Year Master's Admission"
        ),
        "source_url": (
            "https://www.math.is.tohoku.ac.jp/"
            "english/admission/index.html"
        ),
        "note": (
            "AY2027 Master's application period "
            "was June 26 to July 8, 2026."
        ),
    },
    "prog_jp_012": {
        "intake": "April 2027",
        "deadline": "2026-07-08",
        "source_name": (
            "Tohoku University GSIS "
            "2027 Two-Year Master's Admission"
        ),
        "source_url": (
            "https://www.math.is.tohoku.ac.jp/"
            "english/admission/index.html"
        ),
        "note": (
            "AY2027 Master's application period "
            "was June 26 to July 8, 2026."
        ),
    },

    # ---------------------------------------------
    # Nagoya University
    # Mathematical Informatics
    # ---------------------------------------------
    "prog_jp_013": {
        "intake": "April 2027",
        "deadline": "2026-06-18",
        "source_name": (
            "Nagoya University Graduate School "
            "of Informatics 2027 Master's Admission"
        ),
        "source_url": (
            "https://www.i.nagoya-u.ac.jp/"
            "en/gs/entranceexamination/"
        ),
        "note": (
            "First calling for Mathematical "
            "Informatics accepted applications "
            "June 12-18, 2026."
        ),
    },

    # ---------------------------------------------
    # Science Tokyo IGP(C)
    # Spring 2027
    # ---------------------------------------------
    "prog_jp_022": {
        "intake": "Spring 2027",
        "deadline": "2026-10-11",
        "source_name": (
            "Science Tokyo IGP(C) "
            "Spring 2027"
        ),
        "source_url": (
            "https://admissions.isct.ac.jp/"
            "en/013/graduate/programs/"
            "science-and-engineering/igp-c"
        ),
        "note": (
            "Computer Science participates in "
            "IGP(C). Application deadline is "
            "October 11, 2026 at 23:59 JST."
        ),
    },
    "prog_jp_023": {
        "intake": "Spring 2027",
        "deadline": "2026-10-11",
        "source_name": (
            "Science Tokyo IGP(C) "
            "Spring 2027"
        ),
        "source_url": (
            "https://admissions.isct.ac.jp/"
            "en/013/graduate/programs/"
            "science-and-engineering/igp-c"
        ),
        "note": (
            "Mathematical and Computing Science "
            "participates in IGP(C). Application "
            "deadline is October 11, 2026."
        ),
    },

    # ---------------------------------------------
    # Waseda English-based Graduate Program
    # April 2027
    # ---------------------------------------------
    "prog_jp_031": {
        "intake": "April 2027",
        "deadline": "2026-10-22",
        "source_name": (
            "Waseda English-based Graduate "
            "Program April 2027"
        ),
        "source_url": (
            "https://www.waseda.jp/fsci/"
            "assets/uploads/2025/12/"
            "ApplicationGuidelines_20251119.pdf"
        ),
        "note": (
            "April 2027 AO admission application "
            "period ends October 22, 2026."
        ),
    },
    "prog_jp_032": {
        "intake": "April 2027",
        "deadline": "2026-10-22",
        "source_name": (
            "Waseda English-based Graduate "
            "Program April 2027"
        ),
        "source_url": (
            "https://www.waseda.jp/fsci/"
            "assets/uploads/2025/12/"
            "ApplicationGuidelines_20251119.pdf"
        ),
        "note": (
            "April 2027 AO admission application "
            "period ends October 22, 2026."
        ),
    },
    "prog_jp_033": {
        "intake": "April 2027",
        "deadline": "2026-10-22",
        "source_name": (
            "Waseda English-based Graduate "
            "Program April 2027"
        ),
        "source_url": (
            "https://www.waseda.jp/fsci/"
            "assets/uploads/2025/12/"
            "ApplicationGuidelines_20251119.pdf"
        ),
        "note": (
            "April 2027 AO admission application "
            "period ends October 22, 2026."
        ),
    },
}


# -------------------------------------------------
# Complex / route-dependent schedules
# -------------------------------------------------

COMPLEX_SOURCES = {
    "uni_jp_001": {
        "source_name": (
            "UTokyo IST AY2027 Admissions"
        ),
        "source_url": (
            "https://www.i.u-tokyo.ac.jp/"
            "edu/entra/entra_e.shtml"
        ),
        "evidence": (
            "Summer applications: "
            "May 29-June 4, 2026; "
            "Winter applications: "
            "November 11-17, 2026."
        ),
        "reason": (
            "Entry timing and available "
            "examination cycle depend on "
            "department. A single deadline "
            "would be misleading."
        ),
    },

    "uni_jp_002": {
        "source_name": (
            "Kyoto University Informatics "
            "2027 Admission Schedule"
        ),
        "source_url": (
            "https://www.i.kyoto-u.ac.jp/"
            "en/admission/guide/"
            "schedule_master/"
        ),
        "evidence": (
            "April and October admission "
            "options exist, with different "
            "exam schedules by course."
        ),
        "reason": (
            "Course and admission-round "
            "schedules differ, so no single "
            "deadline is stored."
        ),
    },

    "uni_jp_003": {
        "source_name": (
            "University of Osaka IST "
            "2027 Application Guides"
        ),
        "source_url": (
            "https://www.ist.osaka-u.ac.jp/"
            "english/examinees/admission/"
            "guidelines2027.php"
        ),
        "evidence": (
            "April 2027 international "
            "selection schedules are published."
        ),
        "reason": (
            "The graduate school is undergoing "
            "a planned April 2027 reorganization; "
            "do not attach one route-specific "
            "deadline to every seed major."
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
        "evidence": (
            "Program-level admission information "
            "is available through individual "
            "graduate schools."
        ),
        "reason": (
            "A common current deadline for all "
            "three seed programs was not safely "
            "verified."
        ),
    },

    "uni_jp_007": {
        "source_name": (
            "Hokkaido University IST Admissions"
        ),
        "source_url": (
            "https://www.ist.hokudai.ac.jp/"
            "examinfo/"
        ),
        "evidence": (
            "Graduate admission information "
            "is published by examination cycle."
        ),
        "reason": (
            "No single program-level deadline "
            "is applied without current "
            "route-specific verification."
        ),
    },

    "uni_jp_009": {
        "source_name": (
            "University of Tsukuba "
            "Graduate Admissions"
        ),
        "source_url": (
            "https://www.sie.tsukuba.ac.jp/"
            "eng/exam/applicants/entra/"
        ),
        "evidence": (
            "Multiple selection processes "
            "exist, including general and "
            "special international selections."
        ),
        "reason": (
            "Programs can have different "
            "selection routes and schedules."
        ),
    },

    "uni_jp_010": {
        "source_name": (
            "Kobe University System "
            "Informatics Admissions"
        ),
        "source_url": (
            "https://www.csi.kobe-u.ac.jp/"
        ),
        "evidence": (
            "Multiple April/October admission "
            "rounds are published."
        ),
        "reason": (
            "Multiple rounds mean one deadline "
            "cannot safely represent the "
            "whole program."
        ),
    },

    "uni_jp_012": {
        "source_name": (
            "Keio Science and Technology "
            "Graduate Admissions"
        ),
        "source_url": (
            "https://www.keio.ac.jp/"
            "en/st/admissions-en/"
        ),
        "evidence": (
            "IGP and Double Degree pathways "
            "use different application routes."
        ),
        "reason": (
            "Do not apply one deadline across "
            "IGP Master's, IGP Doctoral and "
            "Double Degree records."
        ),
    },
}


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

    stored_count = 0
    complex_count = 0

    for row in rows:
        program_id = row[
            "program_id"
        ].strip()

        university_id = row[
            "university_id"
        ].strip()

        direct_rule = DIRECT_RULES.get(
            program_id
        )

        if direct_rule:
            row["intake"] = direct_rule[
                "intake"
            ]

            row[
                "application_deadline"
            ] = direct_rule[
                "deadline"
            ]

            schedule_status = (
                "Stored - Directly Verified"
            )

            source_name = direct_rule[
                "source_name"
            ]

            source_url = direct_rule[
                "source_url"
            ]

            evidence = direct_rule[
                "note"
            ]

            storage_reason = (
                "Current official schedule "
                "maps safely to this seed "
                "program/admission route."
            )

            stored_count += 1

        else:
            # ---------------------------------
            # Keep blank when one value would
            # misrepresent multiple rounds.
            # ---------------------------------

            row["intake"] = ""
            row[
                "application_deadline"
            ] = ""

            complex_info = (
                COMPLEX_SOURCES.get(
                    university_id
                )
            )

            if complex_info:
                schedule_status = (
                    "Reviewed - "
                    "Route Dependent"
                )

                source_name = complex_info[
                    "source_name"
                ]

                source_url = complex_info[
                    "source_url"
                ]

                evidence = complex_info[
                    "evidence"
                ]

                storage_reason = complex_info[
                    "reason"
                ]

            else:
                schedule_status = (
                    "Reviewed - "
                    "Exact Deadline Not Stored"
                )

                source_name = (
                    "Existing official "
                    "program source"
                )

                source_url = row.get(
                    "program_url",
                    "",
                )

                evidence = (
                    "Program source retained."
                )

                storage_reason = (
                    "No single current "
                    "program-level intake and "
                    "deadline pair was safely "
                    "verified in this step."
                )

            complex_count += 1

        row[
            "last_verified_at"
        ] = VERIFIED_AT

        existing_freshness = row.get(
            "freshness_status",
            "",
        ).strip()

        schedule_flag = (
            "Intake/Deadline Reviewed"
        )

        if direct_rule:
            schedule_flag += (
                " - Direct Schedule Stored"
            )
        else:
            schedule_flag += (
                " - Complex Schedule "
                "Kept Unstated"
            )

        if existing_freshness:
            row[
                "freshness_status"
            ] = (
                f"{existing_freshness}; "
                f"{schedule_flag}"
            )
        else:
            row[
                "freshness_status"
            ] = schedule_flag

        audit_rows.append(
            {
                "program_id": program_id,
                "university_id": (
                    university_id
                ),
                "program_name": row[
                    "program_name"
                ],
                "degree_level": row[
                    "degree_level"
                ],
                "schedule_status": (
                    schedule_status
                ),
                "stored_intake": row[
                    "intake"
                ],
                "stored_application_deadline": (
                    row[
                        "application_deadline"
                    ]
                ),
                "source_name": (
                    source_name
                ),
                "source_url": (
                    source_url
                ),
                "schedule_evidence": (
                    evidence
                ),
                "storage_reason": (
                    storage_reason
                ),
                "verified_at": (
                    VERIFIED_AT
                ),
            }
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
        "degree_level",
        "schedule_status",
        "stored_intake",
        "stored_application_deadline",
        "source_name",
        "source_url",
        "schedule_evidence",
        "storage_reason",
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

    print(
        "=== Japan Intake + Deadline "
        "Review Complete ==="
    )

    print(
        f"Programs reviewed: "
        f"{len(rows)}"
    )

    print(
        f"Direct schedules stored: "
        f"{stored_count}"
    )

    print(
        f"Complex/route-dependent "
        f"schedules kept blank: "
        f"{complex_count}"
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
        "Verification: no single "
        "deadline was forced into "
        "records with multiple or "
        "route-dependent schedules."
    )


if __name__ == "__main__":
    main()