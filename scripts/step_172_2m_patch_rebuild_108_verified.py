from pathlib import Path
import csv
import hashlib
import sys


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


BATCH01 = PLANNING / "30_south_korea_program_research_queue_batch01_applied.csv"
BATCH02 = PLANNING / "33_south_korea_program_research_queue_batch02_applied.csv"
BATCH03_EVIDENCE = PLANNING / "35_south_korea_program_research_batch03_evidence.csv"

OUTPUT = PLANNING / "36_south_korea_program_research_queue_batch03_applied.csv"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
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


print("="*130)
print("STEP 172.2M PATCH - REBUILD SOUTH KOREA 108 VERIFIED STAGED QUEUE")
print("="*130)


for f in [BATCH01, BATCH02, BATCH03_EVIDENCE]:

    print(
        f.name,
        ":",
        "PASS" if f.exists() else "FAIL"
    )

    if not f.exists():
        sys.exit(1)


rows01, cols01 = load_csv(BATCH01)
rows02, cols02 = load_csv(BATCH02)
rows03, cols03 = load_csv(BATCH03_EVIDENCE)


print()
print("SOURCE AUDIT")
print("-"*130)

print("Batch 01 rows:", len(rows01))
print("Batch 02 rows:", len(rows02))
print("Batch 03 evidence rows:", len(rows03))


# merge

merged = {}

for row in rows01:
    merged[row["program_id"]] = row

for row in rows02:
    merged[row["program_id"]] = row

for row in rows03:
    merged[row["program_id"]] = row


final_rows = [
    merged[f"prog_kr_{i:03d}"]
    for i in range(1,151)
]


verified = [
    r for r in final_rows
    if r["research_status"] == "verified"
]


remaining = [
    r for r in final_rows
    if r["research_status"] != "verified"
]


print()
print("MERGE AUDIT")
print("-"*130)

print(
    "Final rows:",
    len(final_rows)
)

print(
    "Verified programmes:",
    len(verified)
)

print(
    "Remaining:",
    len(remaining)
)


if len(verified) != 108:
    print("FAIL: VERIFIED count is not 108")
    sys.exit(1)


save_csv(
    OUTPUT,
    final_rows,
    cols01
)


check_rows, check_cols = load_csv(OUTPUT)


print()
print("POST WRITE AUDIT")
print("-"*130)

print(
    "Output rows:",
    len(check_rows)
)

print(
    "Output SHA256:",
    sha256(OUTPUT)
)

print()
print("="*130)
print("STEP 172.2M PATCH REBUILD: PASS")
print("="*130)

print()
print("OUTPUT:")
print(OUTPUT)

print("VERIFIED:")
print(len(verified))

print("REMAINING:")
print(len(remaining))

print()
print("NEXT: STEP 172.2N FINAL AUDIT AGAIN")
