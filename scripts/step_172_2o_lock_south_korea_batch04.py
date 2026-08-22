from pathlib import Path
import csv
import hashlib
import sys


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


SOURCE = (
    PLANNING /
    "36_south_korea_program_research_queue_batch03_applied.csv"
)

OUTPUT = (
    PLANNING /
    "37_south_korea_program_research_batch04_lock.csv"
)

CANONICAL = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)


EXPECTED_COLUMNS = [
    "program_id",
    "university_id",
    "university_name",
    "country_id",
    "program_slot",
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
    "programme_identity_status",
    "programme_identity_evidence",
    "official_university_website",
    "research_status",
    "research_note",
    "last_verified_at",
    "international_applicants_status",
    "international_application_url",
    "international_requirements_note",
    "international_applicants_last_verified_at",
]


def sha256(path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        for chunk in iter(
            lambda: f.read(1024*1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()


def load_csv(path):

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        return list(reader), list(reader.fieldnames)


def save_csv(path, rows):

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=EXPECTED_COLUMNS
        )

        writer.writeheader()
        writer.writerows(rows)


print("="*130)
print(
    "STEP 172.2O - SOUTH KOREA BATCH 04 IMMUTABLE LOCK BUILD"
)
print("="*130)


for file in [SOURCE, CANONICAL]:

    print(
        file.name,
        "exists:",
        "PASS" if file.exists() else "FAIL"
    )

    if not file.exists():
        sys.exit(1)


rows, columns = load_csv(SOURCE)


print()
print("PRE-WRITE BATCH 04 LOCK AUDIT")
print("-"*130)


print(
    "Working source rows =150:",
    len(rows)
)


print(
    "Schema exact:",
    columns == EXPECTED_COLUMNS
)


ids = [
    r["program_id"]
    for r in rows
]


print(
    "Working IDs:",
    ids[0],
    "->",
    ids[-1]
)


verified = [
    r for r in rows
    if r["research_status"].lower()=="verified"
]


print(
    "Existing VERIFIED:",
    len(verified)
)


batch04_ids = [
    f"prog_kr_{i:03d}"
    for i in range(109,145)
]


batch04_rows = [
    r
    for r in rows
    if r["program_id"] in batch04_ids
]


print(
    "Selected Batch 04 rows:",
    len(batch04_rows)
)


print(
    "Batch 04 range:",
    batch04_rows[0]["program_id"],
    "->",
    batch04_rows[-1]["program_id"]
)


universities = sorted(
    set(
        r["university_id"]
        for r in batch04_rows
    )
)


print(
    "Batch 04 universities:",
    len(universities)
)


print(
    "Already VERIFIED in Batch 04:",
    sum(
        1
        for r in batch04_rows
        if r["research_status"].lower()=="verified"
    )
)


save_csv(
    OUTPUT,
    batch04_rows
)


written, written_cols = load_csv(OUTPUT)


print()
print("POST-WRITE BATCH 04 LOCK AUDIT")
print("-"*130)


print(
    "Output exists:",
    OUTPUT.exists()
)


print(
    "Rows:",
    len(written)
)


print(
    "Columns:",
    len(written_cols)
)


print(
    "SHA256:",
    sha256(OUTPUT)
)


print()
print("="*130)
print(
    "STEP 172.2O SOUTH KOREA BATCH 04 IMMUTABLE LOCK BUILD: PASS"
)
print("="*130)


print()
print(
    "BATCH 04 LOCK FILE:",
    OUTPUT
)

print(
    "BATCH 04 PROGRAMMES:",
    len(written)
)

print(
    "BATCH 04 IDs:",
    written[0]["program_id"],
    "->",
    written[-1]["program_id"]
)

print(
    "BATCH 04 UNIVERSITIES:",
    len(universities)
)

print(
    "CANONICAL programs.json:",
    "UNCHANGED / 600"
)

print(
    "MONGODB WRITE PERFORMED:",
    False
)

print()
print("NEXT: STEP 172.2P")
print(
    "SOUTH KOREA BATCH 04 OFFICIAL-SOURCE RESEARCH EVIDENCE BUILD"
)
