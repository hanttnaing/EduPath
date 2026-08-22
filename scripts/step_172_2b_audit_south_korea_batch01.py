from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path.cwd()
PLANNING = ROOT / "planning"

EVIDENCE = (
    PLANNING
    / "29_south_korea_program_research_batch01_evidence.csv"
)

QUEUE_SHA = (
    "94657aa0d191c4b483cdc5e170f142266"
    "b96b2fecae4e3a0c8cf4367c28848dc"
)

BATCH_SHA = (
    "904a187bbda3225aac522c7cc07368b1"
    "f2a257b6695d965a44e066e0b61a53ab"
)

EVIDENCE_SHA = (
    "cbe859fc5259f51889f949222fd48d58"
    "be85225782b8126dc7f359a2689fa708"
)

EXPECTED_IDS = [
    f"prog_kr_{i:03d}"
    for i in range(1, 37)
]

EXPECTED_UNKNOWN = {
    "prog_kr_028",
    "prog_kr_029",
    "prog_kr_030",
}

EXPECTED_PARENTS = {
    f"uni_kr_{i:03d}"
    for i in range(1, 13)
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}

checks = []


def add(label, ok, detail=""):
    checks.append(
        (label, bool(ok), str(detail))
    )


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def files_under(base):
    if not base.exists():
        return []

    result = []

    for path in base.rglob("*"):
        if not path.is_file():
            continue

        if any(
            part in SKIP_DIRS
            for part in path.parts
        ):
            continue

        result.append(path)

    return result


def find_by_hash(expected_hash):
    hits = []

    for path in files_under(PLANNING):
        try:
            if sha256(path) == expected_hash:
                hits.append(path)
        except OSError:
            pass

    return sorted(
        hits,
        key=lambda p: (
            len(str(p)),
            str(p).lower(),
        ),
    )


def load_rows(path):
    suffix = path.suffix.lower()

    if suffix == ".csv":
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as f:
            reader = csv.DictReader(f)

            rows = list(reader)
            columns = list(
                reader.fieldnames or []
            )

        return rows, columns

    if suffix == ".json":
        with path.open(
            "r",
            encoding="utf-8-sig",
        ) as f:
            data = json.load(f)

        if isinstance(data, list):
            rows = data

        elif isinstance(data, dict):
            rows = None

            possible_keys = (
                "rows",
                "programs",
                "programmes",
                "data",
                "items",
                "batch",
                "batch_rows",
                "selected_rows",
            )

            for key in possible_keys:
                value = data.get(key)

                if isinstance(value, list):
                    rows = value
                    break

            if rows is None:
                raise ValueError(
                    "No row list found "
                    "inside JSON object"
                )

        else:
            raise ValueError(
                "Unsupported JSON structure"
            )

        rows = [
            row
            for row in rows
            if isinstance(row, dict)
        ]

        columns = sorted({
            key
            for row in rows
            for key in row.keys()
        })

        return rows, columns

    raise ValueError(
        f"Unsupported file type: {suffix}"
    )


def text(value):
    if value is None:
        return ""

    return str(value).strip()


def norm(value):
    return re.sub(
        r"\s+",
        " ",
        text(value),
    ).strip().lower()


def find_column(
    columns,
    aliases,
    required=True,
):
    lookup = {
        column.lower(): column
        for column in columns
    }

    for alias in aliases:
        key = alias.lower()

        if key in lookup:
            return lookup[key]

    if required:
        raise KeyError(
            "Missing column. Tried: "
            + ", ".join(aliases)
        )

    return None


ID_ALIASES = (
    "programme_id",
    "program_id",
    "id",
)

UNIVERSITY_ALIASES = (
    "university_id",
    "parent_university_id",
    "institution_id",
)

NAME_ALIASES = (
    "programme_name",
    "program_name",
    "name",
    "title",
)

DEGREE_ALIASES = (
    "degree_level",
    "level",
    "study_level",
)


def valid_url(value):
    if not value:
        return True

    try:
        parsed = urlparse(value)

        return (
            parsed.scheme
            in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


def compare_identity(
    left_rows,
    left_columns,
    right_rows,
    right_columns,
    label,
):
    left_id = find_column(
        left_columns,
        ID_ALIASES,
    )

    right_id = find_column(
        right_columns,
        ID_ALIASES,
    )

    left_map = {
        text(row.get(left_id)): row
        for row in left_rows
    }

    right_map = {
        text(row.get(right_id)): row
        for row in right_rows
    }

    comparable = []

    for logical, aliases in (
        (
            "university_id",
            UNIVERSITY_ALIASES,
        ),
        (
            "programme_name",
            NAME_ALIASES,
        ),
        (
            "degree_level",
            DEGREE_ALIASES,
        ),
    ):
        left_col = find_column(
            left_columns,
            aliases,
            required=False,
        )

        right_col = find_column(
            right_columns,
            aliases,
            required=False,
        )

        if left_col and right_col:
            comparable.append(
                (
                    logical,
                    left_col,
                    right_col,
                )
            )

    mismatches = []

    for programme_id in EXPECTED_IDS:

        if programme_id not in left_map:
            mismatches.append(
                programme_id
                + ":missing-left"
            )
            continue

        if programme_id not in right_map:
            mismatches.append(
                programme_id
                + ":missing-right"
            )
            continue

        for (
            logical,
            left_col,
            right_col,
        ) in comparable:

            left_value = norm(
                left_map[
                    programme_id
                ].get(left_col)
            )

            right_value = norm(
                right_map[
                    programme_id
                ].get(right_col)
            )

            if left_value != right_value:
                mismatches.append(
                    f"{programme_id}:"
                    f"{logical}"
                )

    add(
        label,
        not mismatches,
        (
            "fields="
            + (
                ",".join(
                    item[0]
                    for item in comparable
                )
                or "ID only"
            )
            + "; mismatches="
            + (
                ",".join(
                    mismatches[:12]
                )
                or "0"
            )
        ),
    )


print(
    "=" * 138
)

print(
    "STEP 172.2B - SOUTH KOREA "
    "BATCH 01 EVIDENCE PRE-APPLY AUDIT"
)

print(
    "=" * 138
)


# ================================================================
# SOURCE LOCK VERIFICATION
# ================================================================

queue_hits = find_by_hash(
    QUEUE_SHA
)

batch_hits = find_by_hash(
    BATCH_SHA
)

queue_path = (
    queue_hits[0]
    if queue_hits
    else None
)

batch_path = (
    batch_hits[0]
    if batch_hits
    else None
)

add(
    "Queue SHA256 lock match",
    bool(queue_hits),
    (
        ", ".join(
            str(
                p.relative_to(ROOT)
            )
            for p in queue_hits
        )
        or "NOT FOUND"
    ),
)

add(
    "Batch SHA256 lock match",
    bool(batch_hits),
    (
        ", ".join(
            str(
                p.relative_to(ROOT)
            )
            for p in batch_hits
        )
        or "NOT FOUND"
    ),
)

add(
    "Evidence file exists",
    EVIDENCE.exists(),
    (
        str(
            EVIDENCE.relative_to(ROOT)
        )
    ),
)


# ================================================================
# EVIDENCE FILE AUDIT
# ================================================================

evidence_rows = []
evidence_columns = []

if EVIDENCE.exists():

    actual_evidence_sha = sha256(
        EVIDENCE
    )

    add(
        "Evidence SHA256 exact",
        (
            actual_evidence_sha
            == EVIDENCE_SHA
        ),
        actual_evidence_sha,
    )

    try:
        (
            evidence_rows,
            evidence_columns,
        ) = load_rows(EVIDENCE)

        id_col = find_column(
            evidence_columns,
            ID_ALIASES,
        )

        university_col = find_column(
            evidence_columns,
            UNIVERSITY_ALIASES,
        )

        name_col = find_column(
            evidence_columns,
            NAME_ALIASES,
        )

        degree_col = find_column(
            evidence_columns,
            DEGREE_ALIASES,
        )

        identity_col = find_column(
            evidence_columns,
            (
                "identity_status",
            ),
        )

        research_col = find_column(
            evidence_columns,
            (
                "research_status",
            ),
        )

        international_col = find_column(
            evidence_columns,
            (
                "international_status",
                "international_student_status",
            ),
        )

        language_col = find_column(
            evidence_columns,
            (
                "language_of_instruction",
                "instruction_language",
                "language",
            ),
            required=False,
        )

        tuition_col = find_column(
            evidence_columns,
            (
                "tuition_fee",
                "tuition",
                "annual_tuition_fee",
            ),
            required=False,
        )

        international_url_col = (
            find_column(
                evidence_columns,
                (
                    "international_url",
                    "international_source_url",
                    "international_evidence_url",
                    "international_students_url",
                    "international_admissions_url",
                ),
                required=False,
            )
        )

        if not international_url_col:
            international_url_col = next(
                (
                    column
                    for column
                    in evidence_columns
                    if (
                        "international"
                        in column.lower()
                        and "url"
                        in column.lower()
                    )
                ),
                None,
            )

        programme_ids = [
            text(
                row.get(id_col)
            )
            for row
            in evidence_rows
        ]

        duplicate_ids = sorted(
            programme_id
            for (
                programme_id,
                count,
            )
            in Counter(
                programme_ids
            ).items()
            if count > 1
        )

        parent_counts = Counter(
            text(
                row.get(
                    university_col
                )
            )
            for row
            in evidence_rows
        )

        identity_counts = Counter(
            norm(
                row.get(
                    identity_col
                )
            )
            for row
            in evidence_rows
        )

        research_counts = Counter(
            norm(
                row.get(
                    research_col
                )
            )
            for row
            in evidence_rows
        )

        international_counts = Counter(
            norm(
                row.get(
                    international_col
                )
            )
            for row
            in evidence_rows
        )

        degree_counts = Counter(
            norm(
                row.get(
                    degree_col
                )
            )
            for row
            in evidence_rows
        )

        unknown_ids = {
            text(
                row.get(id_col)
            )
            for row
            in evidence_rows
            if (
                norm(
                    row.get(
                        international_col
                    )
                )
                == "unknown"
            )
        }

        add(
            "Evidence rows = 36",
            len(evidence_rows) == 36,
            len(evidence_rows),
        )

        add(
            "Evidence columns = 31",
            len(evidence_columns)
            == 31,
            len(evidence_columns),
        )

        add(
            "Duplicate programme IDs = 0",
            not duplicate_ids,
            (
                ", ".join(
                    duplicate_ids
                )
                or "0"
            ),
        )

        add(
            "Programme IDs exact/order exact",
            (
                programme_ids
                == EXPECTED_IDS
            ),
            (
                (
                    programme_ids[0]
                    if programme_ids
                    else "-"
                )
                + " -> "
                + (
                    programme_ids[-1]
                    if programme_ids
                    else "-"
                )
            ),
        )

        add(
            "Parent universities exact 12",
            (
                set(parent_counts)
                == EXPECTED_PARENTS
            ),
            len(parent_counts),
        )

        add(
            "Exactly 3 programmes per parent",
            (
                set(parent_counts)
                == EXPECTED_PARENTS
                and all(
                    parent_counts[
                        parent
                    ]
                    == 3
                    for parent
                    in EXPECTED_PARENTS
                )
            ),
            " / ".join(
                f"{parent}:"
                f"{parent_counts[parent]}"
                for parent
                in sorted(
                    parent_counts
                )
            ),
        )

        add(
            "Identity VERIFIED = 36",
            identity_counts
            == Counter({
                "verified": 36
            }),
            dict(
                identity_counts
            ),
        )

        add(
            "Research VERIFIED = 36",
            research_counts
            == Counter({
                "verified": 36
            }),
            dict(
                research_counts
            ),
        )

        add(
            (
                "International = "
                "33 verified_yes / "
                "3 unknown"
            ),
            international_counts
            == Counter({
                "verified_yes": 33,
                "unknown": 3,
            }),
            dict(
                international_counts
            ),
        )

        add(
            "Unknown IDs exact",
            (
                unknown_ids
                == EXPECTED_UNKNOWN
            ),
            ", ".join(
                sorted(
                    unknown_ids
                )
            ),
        )

        add(
            (
                "Degree = "
                "27 Bachelor / "
                "9 Master"
            ),
            degree_counts
            == Counter({
                "bachelor": 27,
                "master": 9,
            }),
            dict(
                degree_counts
            ),
        )

        if language_col:

            language_counts = Counter(
                (
                    norm(
                        row.get(
                            language_col
                        )
                    )
                    if text(
                        row.get(
                            language_col
                        )
                    )
                    else "<blank>"
                )
                for row
                in evidence_rows
            )

            add(
                (
                    "Language = "
                    "30 blank / "
                    "5 English / "
                    "1 Korean"
                ),
                language_counts
                == Counter({
                    "<blank>": 30,
                    "english": 5,
                    "korean": 1,
                }),
                dict(
                    language_counts
                ),
            )

        else:
            add(
                "Language column located",
                False,
                "NOT FOUND",
            )

        url_columns = [
            column
            for column
            in evidence_columns
            if "url"
            in column.lower()
        ]

        invalid_urls = []

        for row in evidence_rows:

            programme_id = text(
                row.get(id_col)
            )

            for column in url_columns:

                value = text(
                    row.get(column)
                )

                if (
                    value
                    and not valid_url(
                        value
                    )
                ):
                    invalid_urls.append(
                        f"{programme_id}:"
                        f"{column}"
                    )

        add(
            "Invalid populated URLs = 0",
            not invalid_urls,
            (
                ", ".join(
                    invalid_urls[:10]
                )
                or "0"
            ),
        )

        if international_url_col:

            missing_verified_url = []
            unknown_with_url = []

            for row in evidence_rows:

                programme_id = text(
                    row.get(id_col)
                )

                status = norm(
                    row.get(
                        international_col
                    )
                )

                url = text(
                    row.get(
                        international_url_col
                    )
                )

                if (
                    status
                    == "verified_yes"
                    and not url
                ):
                    missing_verified_url.append(
                        programme_id
                    )

                if (
                    status
                    == "unknown"
                    and url
                ):
                    unknown_with_url.append(
                        programme_id
                    )

            add(
                (
                    "verified_yes missing "
                    "intl URL = 0"
                ),
                not missing_verified_url,
                (
                    ", ".join(
                        missing_verified_url
                    )
                    or "0"
                ),
            )

            add(
                (
                    "unknown with "
                    "intl URL = 0"
                ),
                not unknown_with_url,
                (
                    ", ".join(
                        unknown_with_url
                    )
                    or "0"
                ),
            )

        else:
            add(
                (
                    "International URL "
                    "column located"
                ),
                False,
                "NOT FOUND",
            )

        if tuition_col:

            tuition_ids = [
                text(
                    row.get(id_col)
                )
                for row
                in evidence_rows
                if text(
                    row.get(
                        tuition_col
                    )
                )
            ]

            add(
                (
                    "Tuition populated "
                    "= 3 / 36"
                ),
                len(
                    tuition_ids
                )
                == 3,
                (
                    ", ".join(
                        tuition_ids
                    )
                    or "0"
                ),
            )

        else:
            add(
                "Tuition column located",
                False,
                "NOT FOUND",
            )

        required_columns = [
            id_col,
            university_col,
            name_col,
            degree_col,
            identity_col,
            research_col,
            international_col,
        ]

        required_blanks = []

        for row in evidence_rows:

            programme_id = text(
                row.get(id_col)
            )

            for column in required_columns:

                if not text(
                    row.get(column)
                ):
                    required_blanks.append(
                        f"{programme_id}:"
                        f"{column}"
                    )

        add(
            (
                "Required core "
                "evidence blanks = 0"
            ),
            not required_blanks,
            (
                ", ".join(
                    required_blanks[:10]
                )
                or "0"
            ),
        )

    except Exception as exc:

        add(
            "Evidence structure audit",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

else:

    add(
        "Evidence SHA256 exact",
        False,
        "FILE MISSING",
    )


# ================================================================
# BATCH LOCK CONTENT AUDIT
# ================================================================

batch_rows = []
batch_columns = []

if batch_path:

    try:
        (
            batch_rows,
            batch_columns,
        ) = load_rows(
            batch_path
        )

        batch_id_col = find_column(
            batch_columns,
            ID_ALIASES,
        )

        batch_ids = [
            text(
                row.get(
                    batch_id_col
                )
            )
            for row
            in batch_rows
        ]

        add(
            "Batch lock rows = 36",
            len(batch_rows) == 36,
            len(batch_rows),
        )

        add(
            (
                "Batch lock IDs "
                "exact/order exact"
            ),
            batch_ids
            == EXPECTED_IDS,
            (
                (
                    batch_ids[0]
                    if batch_ids
                    else "-"
                )
                + " -> "
                + (
                    batch_ids[-1]
                    if batch_ids
                    else "-"
                )
            ),
        )

        if evidence_rows:

            compare_identity(
                evidence_rows,
                evidence_columns,
                batch_rows,
                batch_columns,
                (
                    "Evidence identity "
                    "matches Batch 01 lock"
                ),
            )

    except Exception as exc:

        add(
            "Batch lock content audit",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )


# ================================================================
# SOURCE 150-ROW QUEUE AUDIT
# ================================================================

if queue_path:

    try:
        (
            queue_rows,
            queue_columns,
        ) = load_rows(
            queue_path
        )

        queue_id_col = find_column(
            queue_columns,
            ID_ALIASES,
        )

        queue_ids = [
            text(
                row.get(
                    queue_id_col
                )
            )
            for row
            in queue_rows
        ]

        queue_id_set = set(
            queue_ids
        )

        add(
            "Source queue rows = 150",
            len(queue_rows) == 150,
            len(queue_rows),
        )

        batch_ids_found = sum(
            programme_id
            in queue_id_set
            for programme_id
            in EXPECTED_IDS
        )

        add(
            (
                "Source queue contains "
                "Batch 01 IDs"
            ),
            batch_ids_found == 36,
            f"{batch_ids_found} / 36",
        )

        if batch_rows:

            compare_identity(
                batch_rows,
                batch_columns,
                queue_rows,
                queue_columns,
                (
                    "Batch lock identity "
                    "matches source queue"
                ),
            )

        if evidence_rows:

            compare_identity(
                evidence_rows,
                evidence_columns,
                queue_rows,
                queue_columns,
                (
                    "Evidence identity "
                    "matches source queue"
                ),
            )

    except Exception as exc:

        add(
            "Source queue content audit",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )


# ================================================================
# CANONICAL SEMANTIC LOCK
# ================================================================

canonical_candidates = []

for path in files_under(ROOT):

    if (
        path.name.lower()
        != "programs.json"
    ):
        continue

    try:
        (
            rows,
            columns,
        ) = load_rows(path)

        if len(rows) == 600:
            canonical_candidates.append(
                (
                    path,
                    rows,
                    columns,
                )
            )

    except Exception:
        pass


add(
    (
        "Canonical programs.json "
        "with 600 rows located"
    ),
    bool(
        canonical_candidates
    ),
    (
        ", ".join(
            str(
                item[0].relative_to(
                    ROOT
                )
            )
            for item
            in canonical_candidates
        )
        or "NOT FOUND"
    ),
)


if canonical_candidates:

    (
        canonical_path,
        canonical_rows,
        canonical_columns,
    ) = canonical_candidates[0]

    canonical_id_col = find_column(
        canonical_columns,
        ID_ALIASES,
        required=False,
    )

    if canonical_id_col:

        south_korea_ids = [
            text(
                row.get(
                    canonical_id_col
                )
            )
            for row
            in canonical_rows
            if text(
                row.get(
                    canonical_id_col
                )
            ).startswith(
                "prog_kr_"
            )
        ]

        add(
            (
                "Canonical South Korea "
                "programmes = 0"
            ),
            len(
                south_korea_ids
            )
            == 0,
            len(
                south_korea_ids
            ),
        )

    else:

        add(
            (
                "Canonical programme "
                "ID column located"
            ),
            False,
            "NOT FOUND",
        )


# ================================================================
# FINAL REPORT
# ================================================================

print()

print(
    "AUDIT RESULTS"
)

print(
    "-" * 138
)

for (
    label,
    passed,
    detail,
) in checks:

    print(
        f"{label:<55}: "
        f"{'PASS' if passed else 'FAIL'}"
        + (
            f" | {detail}"
            if detail
            else ""
        )
    )


failed = [
    (
        label,
        detail,
    )
    for (
        label,
        passed,
        detail,
    )
    in checks
    if not passed
]


print()

print(
    "=" * 138
)


if failed:

    print(
        "STEP 172.2B SOUTH KOREA "
        "BATCH 01 EVIDENCE "
        "PRE-APPLY AUDIT: FAIL"
    )

    print(
        f"FAILED CHECKS: "
        f"{len(failed)}"
    )

    for (
        label,
        detail,
    ) in failed:

        print(
            f" - {label}: "
            f"{detail}"
        )

    print()

    print(
        "STOP: DO NOT APPLY "
        "EVIDENCE TO THE QUEUE"
    )

    print(
        "DO NOT WRITE "
        "programs.json"
    )

    print(
        "DO NOT WRITE MONGODB"
    )

    print(
        "=" * 138
    )

    sys.exit(1)


print(
    "STEP 172.2B SOUTH KOREA "
    "BATCH 01 EVIDENCE "
    "PRE-APPLY AUDIT: PASS"
)

print()

print(
    "EVIDENCE ROWS                    : 36"
)

print(
    "BATCH 01 PROGRAMME IDS           : VERIFIED"
)

print(
    "BATCH 01 PARENT MAPPING          : VERIFIED"
)

print(
    "EVIDENCE VS BATCH LOCK           : VERIFIED"
)

print(
    "EVIDENCE VS 150-ROW QUEUE        : VERIFIED"
)

print(
    "QUEUE SHA256 LOCK                : VERIFIED"
)

print(
    "BATCH SHA256 LOCK                : VERIFIED"
)

print(
    "EVIDENCE SHA256                  : VERIFIED"
)

print(
    "CANONICAL programs.json          : 600 / UNCHANGED BY THIS AUDIT"
)

print(
    "SOUTH KOREA CANONICAL PROGRAMMES : 0"
)

print(
    "MONGODB WRITE PERFORMED          : False"
)

print()

print(
    "NEXT: STEP 172.2C"
)

print(
    "APPLY BATCH 01 EVIDENCE TO "
    "A STAGED COPY OF THE "
    "150-ROW SOUTH KOREA QUEUE"
)

print(
    "=" * 138
)
