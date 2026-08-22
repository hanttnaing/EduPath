import csv
from collections import Counter
from pathlib import Path


REQ_INPUT = Path(
    "planning/"
    "16_hong_kong_program_requirements_research_queue.csv"
)

LANG_INPUT = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)

FINAL_INPUT = Path(
    "data/cleaned/"
    "hong_kong_programs_intake_deadline_enriched.csv"
)


REQ_OUTPUT = Path(
    "planning/"
    "16_hong_kong_program_requirements_research_queue_corrected.csv"
)

LANG_OUTPUT = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue_corrected.csv"
)

FINAL_OUTPUT = Path(
    "data/cleaned/"
    "hong_kong_programs_preimport_corrected.csv"
)

AUDIT_OUTPUT = Path(
    "planning/"
    "19_hong_kong_targeted_quality_corrections.csv"
)


VERIFIED_AT = "2026-08-21"


CUHK_IDS = {
    "prog_hk_004",
    "prog_hk_005",
    "prog_hk_006",
}


LANGUAGE_CONFIG = {

    # -------------------------------------------------
    # HKUST
    # Explicit university-wide official MOI policy.
    # -------------------------------------------------

    "prog_hk_007": {
        "language": "English",
        "status": "VERIFIED",
        "source_name": (
            "HKUST Undergraduate Admissions FAQ"
        ),
        "source_url": (
            "https://join.hkust.edu.hk/faq"
        ),
        "reason": (
            "HKUST's official undergraduate admissions "
            "FAQ explicitly states that lectures, course "
            "materials and work are conducted in English, "
            "except language courses and a small number "
            "of courses requiring Chinese."
        ),
    },

    "prog_hk_008": {
        "language": "English",
        "status": "VERIFIED",
        "source_name": (
            "HKUST Undergraduate Admissions FAQ"
        ),
        "source_url": (
            "https://join.hkust.edu.hk/faq"
        ),
        "reason": (
            "HKUST's official undergraduate admissions "
            "FAQ explicitly states that lectures, course "
            "materials and work are conducted in English, "
            "except language courses and a small number "
            "of courses requiring Chinese."
        ),
    },

    "prog_hk_009": {
        "language": "English",
        "status": "VERIFIED",
        "source_name": (
            "HKUST Undergraduate Admissions FAQ"
        ),
        "source_url": (
            "https://join.hkust.edu.hk/faq"
        ),
        "reason": (
            "HKUST's official undergraduate admissions "
            "FAQ explicitly states that lectures, course "
            "materials and work are conducted in English, "
            "except language courses and a small number "
            "of courses requiring Chinese."
        ),
    },


    # -------------------------------------------------
    # HKBU
    # Programme-specific official pages.
    # -------------------------------------------------

    "prog_hk_016": {
        "language": "English",
        "status": "VERIFIED",
        "source_name": (
            "HKBU BSc Business Computing and "
            "Data Analytics Programme"
        ),
        "source_url": (
            "https://admissions.hkbu.edu.hk/"
            "programmes/faculty-of-science/"
            "bachelor-of-science-hons-in-business-"
            "computing-and-data-analytics-year1.html"
        ),
        "reason": (
            "The official programme page explicitly "
            "states that classroom teaching is in "
            "English except courses granted exemption."
        ),
    },

    "prog_hk_018": {
        "language": "English",
        "status": "VERIFIED",
        "source_name": (
            "HKBU Bachelor of Communication "
            "Programme"
        ),
        "source_url": (
            "https://admissions.hkbu.edu.hk/"
            "programmes/school-of-communication/"
            "bachelor-of-communication-hons-"
            "journalism-and-digital-media-public-"
            "relations-and-advertising-year1.html"
        ),
        "reason": (
            "The official programme page explicitly "
            "states that classroom teaching is in "
            "English except courses granted exemption."
        ),
    },


    # -------------------------------------------------
    # Lingnan
    # Current evidence does not safely establish
    # whole-programme MOI.
    # -------------------------------------------------

    "prog_hk_020": {
        "language": "Unknown",
        "status": "REVIEWED_UNRESOLVED",
        "source_name": (
            "Lingnan University Department of "
            "Government and International Affairs"
        ),
        "source_url": (
            "https://www.ln.edu.hk/gia/"
        ),
        "reason": (
            "Current official materials confirm the "
            "Government and International Affairs "
            "programme and its courses, but this review "
            "did not retrieve a sufficiently explicit "
            "whole-programme undergraduate medium-of-"
            "instruction statement. The previous "
            "'English Available' value is therefore "
            "replaced with Unknown rather than inferred."
        ),
    },


    # -------------------------------------------------
    # HKSYU
    # Programme page confirms programme structure,
    # but does not explicitly state whole-program MOI.
    # -------------------------------------------------

    "prog_hk_028": {
        "language": "Unknown",
        "status": "REVIEWED_UNRESOLVED",
        "source_name": (
            "HKSYU Applied Data Science "
            "Programme Structure"
        ),
        "source_url": (
            "https://adsci.hksyu.edu/"
            "programme/BSc-ADS/programme-structure"
        ),
        "reason": (
            "The current official programme page "
            "confirms the Applied Data Science "
            "programme, curriculum, duration and "
            "study mode, but does not explicitly state "
            "the whole-programme medium of instruction. "
            "English language courses alone are not "
            "treated as proof that all programme "
            "instruction is in English. The previous "
            "'English Available' value is replaced "
            "with Unknown."
        ),
    },
}


def clean(value):
    return str(value or "").strip()


def read_csv(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Missing input: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        return (
            reader.fieldnames or [],
            list(reader),
        )


def write_csv(path, headers, rows):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=headers,
        )

        writer.writeheader()
        writer.writerows(rows)


def main():

    print("=" * 110)
    print(
        "STEP 169.2BS - BUILD HONG KONG "
        "TARGETED-CORRECTED PRE-IMPORT DATA"
    )
    print("=" * 110)


    outputs = [
        REQ_OUTPUT,
        LANG_OUTPUT,
        FINAL_OUTPUT,
        AUDIT_OUTPUT,
    ]

    existing = [
        str(path)
        for path in outputs
        if path.exists()
    ]

    if existing:
        raise FileExistsError(
            "Safety stop: corrected output already "
            "exists:\n"
            + "\n".join(existing)
        )


    req_headers, req_rows = read_csv(
        REQ_INPUT
    )

    lang_headers, lang_rows = read_csv(
        LANG_INPUT
    )

    final_headers, final_rows = read_csv(
        FINAL_INPUT
    )


    if len(req_rows) != 45:
        raise ValueError(
            "Requirements queue must contain 45 rows."
        )

    if len(lang_rows) != 45:
        raise ValueError(
            "Language queue must contain 45 rows."
        )

    if len(final_rows) != 45:
        raise ValueError(
            "Final programme dataset must "
            "contain 45 rows."
        )


    required_language_columns = {
        "program_id",
        "program_name",
        "language_of_instruction",
        "language_research_status",
        "language_source_name",
        "language_source_url",
        "language_reason",
        "verified_at",
    }

    missing_language_columns = (
        required_language_columns
        - set(lang_headers)
    )

    if missing_language_columns:
        raise ValueError(
            "Language queue missing columns: "
            + ", ".join(
                sorted(
                    missing_language_columns
                )
            )
        )


    req_by_id = {
        clean(row["program_id"]): row
        for row in req_rows
    }

    lang_by_id = {
        clean(row["program_id"]): row
        for row in lang_rows
    }

    final_by_id = {
        clean(row["program_id"]): row
        for row in final_rows
    }


    correction_rows = []


    # =================================================
    # A. CUHK TOEFL 2027 SAFETY CORRECTION
    # =================================================

    cuhk_source = (
        "https://admission.cuhk.edu.hk/"
        "application/non-jupas/"
        "language-requirements/"
    )


    for program_id in sorted(
        CUHK_IDS
    ):

        req = req_by_id[
            program_id
        ]

        final = final_by_id[
            program_id
        ]

        old_req_value = clean(
            req["toefl_requirement"]
        )

        old_final_value = clean(
            final["toefl_requirement"]
        )


        if old_req_value != "80":
            raise ValueError(
                f"{program_id}: expected requirements "
                f"TOEFL 80 before correction, found "
                f"{old_req_value!r}."
            )

        if old_final_value != "80":
            raise ValueError(
                f"{program_id}: expected final TOEFL "
                f"80 before correction, found "
                f"{old_final_value!r}."
            )


        req["toefl_requirement"] = ""

        req[
            "english_status"
        ] = (
            "IELTS numeric minimum verified. "
            "TOEFL accepted, but a single numeric "
            "2027/28 minimum is unresolved."
        )

        req[
            "numeric_minimum_status"
        ] = (
            "IELTS 6.0 verified. TOEFL numeric "
            "minimum not stored for 2027/28 because "
            "CUHK documents the 2026 score-scale "
            "transition and states that requirements "
            "for 2027 Entry onwards are subject "
            "to review."
        )

        req[
            "requirements_source_name"
        ] = (
            "CUHK Undergraduate Admissions - "
            "Language Requirements"
        )

        req[
            "requirements_source_url"
        ] = cuhk_source

        req[
            "requirements_reason"
        ] = (
            "CUHK officially verifies IELTS Academic "
            "6.0. Its TOEFL requirements use different "
            "reporting formats around 21 January 2026, "
            "and the official page states that TOEFL "
            "requirements are subject to review for "
            "2027 Entry and onwards. EduPath therefore "
            "does not store a single TOEFL numeric "
            "minimum for the 2027/28 target cycle."
        )

        req["verified_at"] = VERIFIED_AT


        final["toefl_requirement"] = ""


        correction_rows.append(
            {
                "program_id": program_id,
                "correction_type": (
                    "TOEFL_2027_SCALE_SAFETY"
                ),
                "field_name": (
                    "toefl_requirement"
                ),
                "old_value": "80",
                "new_value": "",
                "result_status": (
                    "CORRECTED_EVIDENCE_CLOSED"
                ),
                "source_name": (
                    "CUHK Undergraduate Admissions - "
                    "Language Requirements"
                ),
                "source_url": cuhk_source,
                "correction_reason": (
                    "2027 Entry onwards is subject "
                    "to review; a single 80 value is "
                    "not safely representative of the "
                    "target admission cycle."
                ),
                "verified_at": VERIFIED_AT,
            }
        )


    # =================================================
    # B. LANGUAGE EVIDENCE CORRECTIONS
    # =================================================

    for program_id, config in (
        LANGUAGE_CONFIG.items()
    ):

        lang = lang_by_id[
            program_id
        ]

        final = final_by_id[
            program_id
        ]


        old_language = clean(
            lang["language_of_instruction"]
        )

        old_status = clean(
            lang["language_research_status"]
        )


        lang[
            "language_of_instruction"
        ] = config["language"]

        lang[
            "language_research_status"
        ] = config["status"]

        lang[
            "language_source_name"
        ] = config["source_name"]

        lang[
            "language_source_url"
        ] = config["source_url"]

        lang[
            "language_reason"
        ] = config["reason"]

        lang["verified_at"] = VERIFIED_AT


        if program_id in {
            "prog_hk_020",
            "prog_hk_028",
        }:

            expected_old = "English Available"

            if clean(
                final[
                    "language_of_instruction"
                ]
            ) != expected_old:

                raise ValueError(
                    f"{program_id}: expected final "
                    f"language {expected_old!r} before "
                    "correction."
                )

            final[
                "language_of_instruction"
            ] = "Unknown"


        correction_rows.append(
            {
                "program_id": program_id,
                "correction_type": (
                    "LANGUAGE_EVIDENCE_RECHECK"
                ),
                "field_name": (
                    "language_of_instruction / evidence"
                ),
                "old_value": (
                    f"{old_language} | {old_status}"
                ),
                "new_value": (
                    f"{config['language']} | "
                    f"{config['status']}"
                ),
                "result_status": (
                    "CORRECTED_EVIDENCE_CLOSED"
                ),
                "source_name": (
                    config["source_name"]
                ),
                "source_url": (
                    config["source_url"]
                ),
                "correction_reason": (
                    config["reason"]
                ),
                "verified_at": VERIFIED_AT,
            }
        )


    # =================================================
    # WRITE CORRECTED COPIES
    # =================================================

    write_csv(
        REQ_OUTPUT,
        req_headers,
        req_rows,
    )

    write_csv(
        LANG_OUTPUT,
        lang_headers,
        lang_rows,
    )

    write_csv(
        FINAL_OUTPUT,
        final_headers,
        final_rows,
    )


    audit_headers = [
        "program_id",
        "correction_type",
        "field_name",
        "old_value",
        "new_value",
        "result_status",
        "source_name",
        "source_url",
        "correction_reason",
        "verified_at",
    ]


    write_csv(
        AUDIT_OUTPUT,
        audit_headers,
        correction_rows,
    )


    # =================================================
    # POST-BUILD VALIDATION
    # =================================================

    corrected_toefl = sum(
        bool(
            clean(
                row["toefl_requirement"]
            )
        )
        for row in final_rows
    )

    unknown_language_ids = {
        clean(row["program_id"])
        for row in final_rows
        if clean(
            row["language_of_instruction"]
        ) == "Unknown"
    }


    language_statuses = Counter(
        clean(
            row[
                "language_research_status"
            ]
        )
        for row in lang_rows
    )


    cuhk_final_values = {
        program_id: clean(
            final_by_id[
                program_id
            ]["toefl_requirement"]
        )
        for program_id in CUHK_IDS
    }


    print()
    print(
        "Corrected final rows             :",
        len(final_rows),
    )

    print(
        "Numeric TOEFL rows after fix     :",
        corrected_toefl,
    )

    print(
        "CUHK TOEFL values after fix      :",
        cuhk_final_values,
    )

    print(
        "Unknown language IDs             :",
        ", ".join(
            sorted(
                unknown_language_ids
            )
        ),
    )

    print(
        "Language research statuses       :",
        dict(language_statuses),
    )

    print(
        "Correction audit rows            :",
        len(correction_rows),
    )


    if corrected_toefl != 24:
        raise ValueError(
            "Expected 24 numeric TOEFL rows "
            "after CUHK correction."
        )

    if unknown_language_ids != {
        "prog_hk_020",
        "prog_hk_028",
    }:
        raise ValueError(
            "Unexpected Unknown language set."
        )

    if language_statuses.get(
        "VERIFIED",
        0,
    ) != 43:
        raise ValueError(
            "Expected 43 VERIFIED language rows."
        )

    if language_statuses.get(
        "REVIEWED_UNRESOLVED",
        0,
    ) != 2:
        raise ValueError(
            "Expected 2 unresolved language rows."
        )

    if any(
        cuhk_final_values.values()
    ):
        raise ValueError(
            "CUHK 004-006 TOEFL must be blank."
        )

    if len(correction_rows) != 10:
        raise ValueError(
            "Expected exactly 10 correction "
            "audit records."
        )


    print()
    print(
        "Corrected requirements queue:",
        REQ_OUTPUT,
    )

    print(
        "Corrected language queue    :",
        LANG_OUTPUT,
    )

    print(
        "Corrected final dataset     :",
        FINAL_OUTPUT,
    )

    print(
        "Correction audit            :",
        AUDIT_OUTPUT,
    )

    print()
    print("=" * 110)

    print(
        "STEP 169.2BS TARGETED QUALITY "
        "CORRECTION BUILD: PASS"
    )

    print(
        "ORIGINAL FROZEN RESEARCH QUEUES "
        "WERE NOT OVERWRITTEN"
    )

    print(
        "WORKBOOK AND MONGODB WERE NOT MODIFIED"
    )

    print("=" * 110)


if __name__ == "__main__":
    main()
