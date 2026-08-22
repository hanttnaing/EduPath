from pathlib import Path
import csv
import hashlib


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


SOURCE = PLANNING / "27_south_korea_program_research_queue.csv"

EVIDENCE_FILES = [
    PLANNING / "29_south_korea_program_research_batch01_evidence.csv",
    PLANNING / "32_south_korea_program_research_batch02_evidence.csv",
    PLANNING / "35_south_korea_program_research_batch03_evidence.csv",
]

OUTPUT = PLANNING / "36_south_korea_program_research_queue_batch03_applied.csv"


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


def normalize_status(row):

    if row.get("research_status"):
        row["research_status"] = (
            row["research_status"]
            .strip()
            .lower()
        )

    if row.get("programme_identity_status"):
        row["programme_identity_status"] = (
            row["programme_identity_status"]
            .strip()
            .lower()
        )

    return row


print("="*120)
print("STEP 172.2M PATCH 2 - REBUILD 108 VERIFIED QUEUE")
print("="*120)


source_rows, columns = load_csv(SOURCE)

merged = {
    r["program_id"]: r
    for r in source_rows
}


for file in EVIDENCE_FILES:

    rows, _ = load_csv(file)

    print(
        file.name,
        "rows:",
        len(rows)
    )

    for row in rows:

        row = normalize_status(row)

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
print("FINAL AUDIT")
print("-"*120)

print(
    "Rows:",
    len(final_rows)
)

print(
    "Verified:",
    len(verified)
)

print(
    "Remaining:",
    len(remaining)
)


if len(verified) != 108:
    raise Exception(
        f"Expected 108 verified but got {len(verified)}"
    )


save_csv(
    OUTPUT,
    final_rows,
    columns
)


print()
print("OUTPUT CREATED")
print(
    OUTPUT
)

print()
print("="*120)
print("STEP 172.2M PATCH 2: PASS")
print("="*120)

print()
print("NEXT: STEP 172.2N FINAL AUDIT")
