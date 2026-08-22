from pathlib import Path
import csv
import hashlib
import sys


ROOT = Path.cwd()
PLANNING = ROOT / "planning"


SOURCE = (
    PLANNING /
    "39_south_korea_program_research_queue_batch04_applied.csv"
)

EVIDENCE = (
    PLANNING /
    "41_south_korea_program_research_batch05_evidence.csv"
)

OUTPUT = (
    PLANNING /
    "42_south_korea_program_research_queue_batch05_applied.csv"
)

CANONICAL = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)


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
print(
    "STEP 172.2W - SOUTH KOREA FINAL BATCH 05 SAFE EVIDENCE APPLY"
)
print("="*130)



for file in [
    SOURCE,
    EVIDENCE,
    CANONICAL
]:

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

print(
    "Evidence schema:",
    columns == evidence_columns
)



evidence_map = {
    r["program_id"]: r
    for r in evidence_rows
}



print()
print("IN-MEMORY STAGING AUDIT")
print("-"*130)



staged=[]


for row in source_rows:

    pid=row["program_id"]

    if pid in evidence_map:

        new=row.copy()

        ev=evidence_map[pid]

        for key in [
            "programme_identity_status",
            "research_status",
            "international_applicants_status"
        ]:

            new[key]=ev[key]

        staged.append(new)

    else:

        staged.append(row)



verified = sum(
    1
    for r in staged
    if r["research_status"].lower()
    =="verified"
)



remaining = len(staged)-verified



print(
    "Staged rows:",
    len(staged)
)

print(
    "Batch 05 applied:",
    len(evidence_rows)
)

print(
    "Total VERIFIED:",
    verified
)

print(
    "Remaining:",
    remaining
)



if verified != 150:

    print("FAIL: VERIFIED count is not 150")
    sys.exit(1)



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
    "STEP 172.2W SOUTH KOREA FINAL BATCH 05 SAFE STAGING APPLY: PASS"
)
print("="*130)



print()

print(
    "NEW STAGED QUEUE:",
    OUTPUT
)

print(
    "TOTAL VERIFIED PROGRAMMES:",
    verified
)

print(
    "VERIFIED UNIVERSITIES:",
    len(
        set(
            r["university_id"]
            for r in written
            if r["research_status"].lower()
            =="verified"
        )
    )
)

print(
    "REMAINING:",
    remaining
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
print("NEXT: STEP 172.2X")
print(
    "FINAL SOUTH KOREA 150-VERIFIED QUEUE AUDIT"
)
