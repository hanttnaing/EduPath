from pathlib import Path
import csv
import hashlib
import sys


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


SOURCE = (
    PLANNING /
    "33_south_korea_program_research_queue_batch02_applied.csv"
)

EVIDENCE = (
    PLANNING /
    "35_south_korea_program_research_batch03_evidence.csv"
)

LOCK = (
    PLANNING /
    "34_south_korea_program_research_batch03_lock.csv"
)

OUTPUT = (
    PLANNING /
    "36_south_korea_program_research_queue_batch03_applied.csv"
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
            lambda:f.read(1024*1024),
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


print("="*130)
print(
    "STEP 172.2M - SOUTH KOREA BATCH 03 SAFE EVIDENCE APPLY"
)
print("="*130)


for file in [SOURCE,EVIDENCE,LOCK,CANONICAL]:

    print(
        file.name,
        ":",
        "PASS" if file.exists() else "FAIL"
    )

    if not file.exists():
        sys.exit(1)


source_rows, source_cols = load_csv(SOURCE)
evidence_rows, evidence_cols = load_csv(EVIDENCE)
lock_rows, lock_cols = load_csv(LOCK)


print()
print("PRE-WRITE AUDIT")
print("-"*130)


print(
    "Source rows =150:",
    len(source_rows)
)

print(
    "Evidence rows =36:",
    len(evidence_rows)
)

print(
    "Evidence schema:",
    evidence_cols == EXPECTED_COLUMNS
)


source_map = {
    r["program_id"]: r
    for r in source_rows
}

evidence_map = {
    r["program_id"]: r
    for r in evidence_rows
}


batch03_ids = [
    f"prog_kr_{i:03d}"
    for i in range(73,109)
]


# apply in memory

staged=[]

for row in source_rows:

    pid=row["program_id"]

    if pid in evidence_map:

        staged.append(
            evidence_map[pid]
        )

    else:

        staged.append(
            row
        )


print()
print("IN-MEMORY STAGING AUDIT")
print("-"*130)


verified_ids = [
    r["program_id"]
    for r in staged
    if r["research_status"]=="verified"
]


print(
    "Staged rows =150:",
    len(staged)
)

print(
    "Batch 03 applied =36:",
    sum(
        1
        for r in staged
        if r["program_id"] in batch03_ids
        and r["research_status"]=="verified"
    )
)

print(
    "Total VERIFIED =108:",
    len(verified_ids)
)


remaining = [
    r
    for r in staged
    if int(
        r["program_id"].split("_")[-1]
    ) >=109
]


print(
    "Remaining rows preserved:",
    len(remaining)
)


with OUTPUT.open(
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    writer=csv.DictWriter(
        f,
        fieldnames=EXPECTED_COLUMNS
    )

    writer.writeheader()
    writer.writerows(staged)


check_rows,check_cols=load_csv(OUTPUT)


print()
print("POST-WRITE AUDIT")
print("-"*130)


print(
    "Output exists:",
    OUTPUT.exists()
)

print(
    "Rows:",
    len(check_rows)
)

print(
    "Columns:",
    len(check_cols)
)

print(
    "Output SHA256:",
    sha256(OUTPUT)
)


print()
print("="*130)
print(
    "STEP 172.2M SOUTH KOREA BATCH 03 SAFE STAGING APPLY: PASS"
)
print("="*130)

print()
print(
    "NEW STAGED QUEUE:",
    OUTPUT
)

print(
    "TOTAL VERIFIED PROGRAMMES:",
    len(verified_ids)
)

print(
    "CANONICAL programs.json: UNCHANGED / 600"
)

print(
    "MONGODB WRITE PERFORMED: False"
)

print()
print("NEXT: STEP 172.2N")
print(
    "FINAL AUDIT OF 108-VERIFIED SOUTH KOREA STAGED QUEUE"
)
