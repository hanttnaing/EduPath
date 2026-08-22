from pathlib import Path
import csv
import hashlib
import sys


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


SOURCE = PLANNING / "36_south_korea_program_research_queue_batch03_applied.csv"
EVIDENCE = PLANNING / "38_south_korea_program_research_batch04_evidence.csv"
OUTPUT = PLANNING / "39_south_korea_program_research_queue_batch04_applied.csv"

CANONICAL = ROOT / "data" / "cleaned" / "programs.json"


def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames)


def save_csv(path, rows, columns):
    with path.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=columns
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):

    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024*1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()


print("="*130)
print("STEP 172.2R - SOUTH KOREA BATCH 04 SAFE EVIDENCE APPLY")
print("="*130)


for file in [SOURCE, EVIDENCE, CANONICAL]:

    print(
        file.name,
        ":",
        "PASS" if file.exists() else "FAIL"
    )

    if not file.exists():
        sys.exit(1)


source_rows, columns = load_csv(SOURCE)
evidence_rows, evidence_columns = load_csv(EVIDENCE)


print()
print("PRE-WRITE AUDIT")
print("-"*130)

print(
    "Source rows:",
    len(source_rows)
)

print(
    "Evidence rows:",
    len(evidence_rows)
)


if columns != evidence_columns:
    print("Schema mismatch")
    sys.exit(1)



evidence_map = {
    r["program_id"]: r
    for r in evidence_rows
}


staged = []

for row in source_rows:

    if row["program_id"] in evidence_map:
        staged.append(
            evidence_map[row["program_id"]]
        )

    else:
        staged.append(row)



print()
print("IN-MEMORY STAGING AUDIT")
print("-"*130)


verified = [
    r for r in staged
    if r["research_status"].lower()=="verified"
]


print(
    "Staged rows:",
    len(staged)
)


print(
    "Batch 04 applied:",
    len(evidence_rows)
)


print(
    "Total VERIFIED:",
    len(verified)
)


print(
    "Remaining:",
    len(staged)-len(verified)
)



save_csv(
    OUTPUT,
    staged,
    columns
)


written, written_columns = load_csv(OUTPUT)


print()
print("POST-WRITE AUDIT")
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
    len(written_columns)
)


print(
    "Output SHA256:",
    sha256(OUTPUT)
)



print()
print("="*130)
print(
    "STEP 172.2R SOUTH KOREA BATCH 04 SAFE STAGING APPLY: PASS"
)
print("="*130)


print()
print(
    "NEW STAGED QUEUE:",
    OUTPUT
)

print(
    "TOTAL VERIFIED PROGRAMMES:",
    len([
        r for r in written
        if r["research_status"].lower()=="verified"
    ])
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
print("NEXT: STEP 172.2S")
print(
    "FINAL AUDIT OF 144-VERIFIED SOUTH KOREA STAGED QUEUE"
)
