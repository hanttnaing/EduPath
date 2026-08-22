import csv
from collections import Counter, defaultdict
from pathlib import Path


FINAL_DATASET = Path(
    "data/cleaned/"
    "hong_kong_programs_intake_deadline_enriched.csv"
)

LANGUAGE_QUEUE = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)

REQUIREMENTS_QUEUE = Path(
    "planning/"
    "16_hong_kong_program_requirements_research_queue.csv"
)

TUITION_QUEUE = Path(
    "planning/"
    "17_hong_kong_program_tuition_research_queue.csv"
)

SCHEDULE_QUEUE = Path(
    "planning/"
    "18_hong_kong_program_intake_deadline_research_queue.csv"
)

INTERNATIONAL_QUEUE = Path(
    "data/raw/"
    "hong_kong_program_international_research_queue.csv"
)


EXPECTED_HEADERS = [
    "program_id",
    "university_id",
    "program_name",
    "field_of_study",
    "degree_level",
    "duration_years",
    "study_mode",
    "language_of_instruction",
    "tuition_fee",
    "tuition_currency",
    "tuition_period",
    "minimum_gpa",
    "gpa_scale",
    "ielts_requirement",
    "toefl_requirement",
    "intake",
    "application_deadline",
    "program_url",
    "collected_at",
    "last_verified_at",
    "freshness_status",
]


IDENTITY_RECHECK_IDS = {
    "prog_hk_025",
    "prog_hk_034",
    "prog_hk_035",
    "prog_hk_036",
}


def clean(value):
    return str(value or "").strip()


def read_csv(path):

    if not path.exists():
        return [], []

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


def find_column(headers, candidates):

    lower_map = {
        header.lower(): header
        for header in headers
    }

    for candidate in candidates:

        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]

    return None


print("=" * 110)
print(
    "STEP 169.2BQ - HONG KONG FINAL "
    "PRE-IMPORT QUALITY GATE"
)
print("=" * 110)


# =====================================================
# 1. FINAL DATASET
# =====================================================

final_headers, final_rows = read_csv(
    FINAL_DATASET
)

if not final_rows:
    raise FileNotFoundError(
        f"Final dataset missing or empty: {FINAL_DATASET}"
    )


final_ids = [
    clean(row["program_id"])
    for row in final_rows
]


print()
print("A. FINAL 21-COLUMN DATASET")
print("-" * 110)

print(
    "Rows                              :",
    len(final_rows),
)

print(
    "Columns                           :",
    len(final_headers),
)

print(
    "Exact 21-column contract          :",
    final_headers == EXPECTED_HEADERS,
)

print(
    "Duplicate program IDs             :",
    len(final_ids) - len(set(final_ids)),
)


core_fields = [
    "program_id",
    "university_id",
    "program_name",
    "field_of_study",
    "degree_level",
    "duration_years",
    "study_mode",
    "language_of_instruction",
    "program_url",
]


for field in core_fields:

    blanks = sum(
        not clean(row[field])
        for row in final_rows
    )

    print(
        f"Blank {field:<26}: {blanks}"
    )


print(
    "Numeric tuition rows              :",
    sum(
        bool(clean(row["tuition_fee"]))
        for row in final_rows
    ),
)

print(
    "Blank tuition rows                :",
    sum(
        not clean(row["tuition_fee"])
        for row in final_rows
    ),
)

print(
    "IELTS rows                        :",
    sum(
        bool(clean(row["ielts_requirement"]))
        for row in final_rows
    ),
)

print(
    "TOEFL rows                        :",
    sum(
        bool(clean(row["toefl_requirement"]))
        for row in final_rows
    ),
)

print(
    "Stored intake rows                :",
    sum(
        bool(clean(row["intake"]))
        for row in final_rows
    ),
)

print(
    "Stored deadline rows              :",
    sum(
        bool(clean(row["application_deadline"]))
        for row in final_rows
    ),
)


freshness_counts = Counter(
    clean(row["freshness_status"])
    for row in final_rows
)


print(
    "Freshness distinct values         :",
    len(freshness_counts),
)

for value, count in freshness_counts.items():
    print(
        "  ",
        repr(value),
        ":",
        count,
    )


# =====================================================
# 2. REQUIREMENTS / TOEFL
# =====================================================

req_headers, req_rows = read_csv(
    REQUIREMENTS_QUEUE
)


print()
print("B. REQUIREMENTS / TOEFL SAFETY")
print("-" * 110)

print(
    "Requirements rows                 :",
    len(req_rows),
)


toefl_scale_keywords = [
    "21 jan 2026",
    "january 21 2026",
    "new scale",
    "score scale",
    "scale transition",
    "after 21 jan",
    "before 21 jan",
    "reporting scale",
]


toefl_scale_flags = []


for row in req_rows:

    program_id = clean(
        row.get("program_id")
    )

    toefl = clean(
        row.get("toefl_requirement")
    )

    text = " ".join(
        clean(row.get(field))
        for field in [
            "requirements_reason",
            "numeric_minimum_status",
            "accepted_tests",
            "english_status",
        ]
    ).lower()


    if (
        toefl
        and any(
            keyword in text
            for keyword in toefl_scale_keywords
        )
    ):
        toefl_scale_flags.append(
            (
                program_id,
                toefl,
                clean(
                    row.get(
                        "requirements_source_name"
                    )
                ),
            )
        )


print(
    "Numeric TOEFL rows                :",
    sum(
        bool(
            clean(
                row.get("toefl_requirement")
            )
        )
        for row in req_rows
    ),
)

print(
    "TOEFL scale-consistency flags     :",
    len(toefl_scale_flags),
)


for (
    program_id,
    toefl,
    source_name,
) in toefl_scale_flags:

    print(
        "  FLAG",
        program_id,
        "| stored TOEFL:",
        toefl,
        "|",
        source_name,
    )


# =====================================================
# 3. LANGUAGE QUALITY SIGNALS
# =====================================================

lang_headers, lang_rows = read_csv(
    LANGUAGE_QUEUE
)


print()
print("C. LANGUAGE EVIDENCE QUALITY")
print("-" * 110)

print(
    "Language research rows            :",
    len(lang_rows),
)

print(
    "Language queue columns            :",
    len(lang_headers),
)


status_col = find_column(
    lang_headers,
    [
        "language_research_status",
        "research_status",
        "status",
    ],
)

source_url_col = find_column(
    lang_headers,
    [
        "language_source_url",
        "source_url",
        "requirements_source_url",
    ],
)

source_name_col = find_column(
    lang_headers,
    [
        "language_source_name",
        "source_name",
    ],
)

reason_col = find_column(
    lang_headers,
    [
        "language_reason",
        "reason",
        "note",
        "evidence",
    ],
)


if status_col:

    print(
        "Language statuses                :",
        dict(
            Counter(
                clean(row.get(status_col))
                for row in lang_rows
            )
        ),
    )

else:
    print(
        "Language status column           :",
        "NOT DETECTED",
    )


if source_url_col:

    blank_urls = sum(
        not clean(row.get(source_url_col))
        for row in lang_rows
    )

    print(
        "Blank language source URLs       :",
        blank_urls,
    )


    url_groups = defaultdict(list)

    for row in lang_rows:

        url = clean(
            row.get(source_url_col)
        )

        if url:
            url_groups[url].append(
                clean(row.get("program_id"))
            )


    heavily_reused = {
        url: ids
        for url, ids in url_groups.items()
        if len(ids) >= 3
    }


    print(
        "Source URLs reused for >=3 rows  :",
        len(heavily_reused),
    )


    for url, ids in sorted(
        heavily_reused.items(),
        key=lambda item: (
            -len(item[1]),
            item[0],
        ),
    ):

        print(
            "  REUSE",
            len(ids),
            "rows |",
            ", ".join(ids),
        )

        print(
            "       ",
            url,
        )

else:

    print(
        "Language source URL column       :",
        "NOT DETECTED",
    )


if reason_col:

    generic_terms = [
        "university",
        "medium of instruction",
        "english is the medium",
        "english medium",
        "programmes are taught in english",
    ]

    generic_flags = []

    for row in lang_rows:

        reason = clean(
            row.get(reason_col)
        ).lower()

        if reason and any(
            term in reason
            for term in generic_terms
        ):

            generic_flags.append(
                clean(row.get("program_id"))
            )


    print(
        "Generic-language evidence flags  :",
        len(generic_flags),
    )

else:

    print(
        "Language evidence text column    :",
        "NOT DETECTED",
    )


# =====================================================
# 4. IDENTITY RECHECK
# =====================================================

int_headers, int_rows = read_csv(
    INTERNATIONAL_QUEUE
)


print()
print("D. IDENTITY FRESHNESS RECHECK SET")
print("-" * 110)


final_by_id = {
    clean(row["program_id"]): row
    for row in final_rows
}

international_by_id = {
    clean(row.get("program_id")): row
    for row in int_rows
}


for program_id in sorted(
    IDENTITY_RECHECK_IDS
):

    final_row = final_by_id.get(
        program_id,
        {},
    )

    research_row = international_by_id.get(
        program_id,
        {},
    )

    print()
    print(program_id)

    print(
        "  Final dataset name :",
        clean(
            final_row.get("program_name")
        ),
    )

    print(
        "  Research queue name:",
        clean(
            research_row.get("program_name")
        ),
    )

    print(
        "  Program URL        :",
        clean(
            final_row.get("program_url")
        ),
    )


# =====================================================
# 5. TUITION CLOSURE
# =====================================================

tuition_headers, tuition_rows = read_csv(
    TUITION_QUEUE
)


print()
print("E. TUITION CLOSURE")
print("-" * 110)


tuition_statuses = Counter(
    clean(
        row.get("tuition_research_status")
    )
    for row in tuition_rows
)


print(
    "Tuition statuses                  :",
    dict(tuition_statuses),
)


unresolved_tuition_ids = [
    clean(row.get("program_id"))
    for row in tuition_rows
    if clean(
        row.get("tuition_research_status")
    )
    == "REVIEWED_UNRESOLVED"
]


print(
    "Tuition unresolved rows           :",
    len(unresolved_tuition_ids),
)

print(
    "  ",
    ", ".join(
        unresolved_tuition_ids
    ),
)


# =====================================================
# 6. SCHEDULE CLOSURE
# =====================================================

schedule_headers, schedule_rows = read_csv(
    SCHEDULE_QUEUE
)


print()
print("F. INTAKE / DEADLINE CLOSURE")
print("-" * 110)


schedule_statuses = Counter(
    clean(
        row.get("schedule_research_status")
    )
    for row in schedule_rows
)


print(
    "Schedule statuses                 :",
    dict(schedule_statuses),
)

print(
    "Schedule intake values            :",
    sum(
        bool(clean(row.get("intake")))
        for row in schedule_rows
    ),
)

print(
    "Schedule deadline values          :",
    sum(
        bool(
            clean(
                row.get("application_deadline")
            )
        )
        for row in schedule_rows
    ),
)


# =====================================================
# 7. INTERNATIONAL ELIGIBILITY
# =====================================================

print()
print("G. INTERNATIONAL ELIGIBILITY")
print("-" * 110)


intl_status_col = find_column(
    int_headers,
    [
        "international_applicants_status",
        "program_international_status",
        "international_status",
        "eligibility_status",
    ],
)


if intl_status_col:

    intl_statuses = Counter(
        clean(
            row.get(intl_status_col)
        )
        for row in int_rows
    )

    print(
        "International statuses           :",
        dict(intl_statuses),
    )

else:

    print(
        "International status column      :",
        "NOT AUTO-DETECTED",
    )

    print(
        "International queue headers      :",
        ", ".join(int_headers),
    )


# =====================================================
# FINAL GATE SUMMARY
# =====================================================

errors = []


if len(final_rows) != 45:
    errors.append(
        "Final dataset does not contain 45 rows."
    )

if final_headers != EXPECTED_HEADERS:
    errors.append(
        "Final dataset is not the exact 21-column contract."
    )

if len(final_ids) != len(set(final_ids)):
    errors.append(
        "Duplicate programme IDs exist."
    )

if any(
    not clean(row[field])
    for row in final_rows
    for field in core_fields
):
    errors.append(
        "Core programme fields contain blanks."
    )

if len(req_rows) != 45:
    errors.append(
        "Requirements queue does not contain 45 rows."
    )

if len(tuition_rows) != 45:
    errors.append(
        "Tuition queue does not contain 45 rows."
    )

if len(schedule_rows) != 45:
    errors.append(
        "Schedule queue does not contain 45 rows."
    )

if schedule_statuses.get(
    "REVIEWED_UNRESOLVED",
    0,
) != 45:
    errors.append(
        "Schedule research is not closed for all 45 rows."
    )


print()
print("=" * 110)


if errors:

    print(
        "STEP 169.2BQ STRUCTURAL QUALITY GATE: FAIL"
    )

    for error in errors:
        print(
            "ERROR:",
            error,
        )

    raise SystemExit(1)


print(
    "STEP 169.2BQ STRUCTURAL QUALITY GATE: PASS"
)

print()

print(
    "IMPORTANT:"
)

print(
    "PASS here means the dataset is structurally "
    "ready for targeted quality re-checks."
)

print(
    "It does NOT yet authorize workbook or MongoDB import."
)

print("=" * 110)
