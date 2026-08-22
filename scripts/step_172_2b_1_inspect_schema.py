import csv
from pathlib import Path

ROOT = Path.cwd()

EVIDENCE = ROOT / "planning" / "29_south_korea_program_research_batch01_evidence.csv"
BATCH = ROOT / "planning" / "28_south_korea_program_research_batch01_lock.csv"
QUEUE = ROOT / "planning" / "27_south_korea_program_research_queue.csv"


def load(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def value(row, col):
    if not col:
        return ""
    return str(row.get(col, "") or "").strip()


def find_id_col(columns):
    for name in (
        "program_id",
        "programme_id",
        "id",
    ):
        if name in columns:
            return name
    raise KeyError("No programme ID column found")


e_rows, e_cols = load(EVIDENCE)
b_rows, b_cols = load(BATCH)
q_rows, q_cols = load(QUEUE)

e_id = find_id_col(e_cols)
b_id = find_id_col(b_cols)
q_id = find_id_col(q_cols)

b_map = {
    value(row, b_id): row
    for row in b_rows
}

q_map = {
    value(row, q_id): row
    for row in q_rows
}


print("=" * 120)
print("STEP 172.2B.1 - SOUTH KOREA BATCH 01 EVIDENCE SCHEMA DIAGNOSTIC")
print("=" * 120)

print()
print("EVIDENCE FILE COLUMNS")
print("-" * 120)

for i, col in enumerate(e_cols, 1):
    print(f"{i:02d}. {col}")


print()
print("STATUS / VERIFICATION RELATED EVIDENCE COLUMNS")
print("-" * 120)

status_like = [
    col
    for col in e_cols
    if any(
        token in col.lower()
        for token in (
            "status",
            "verify",
            "verified",
            "identity",
            "research",
            "international",
        )
    )
]

if status_like:
    for col in status_like:
        print(col)
else:
    print("<NONE>")


print()
print("NAME / DEGREE / UNIVERSITY RELATED EVIDENCE COLUMNS")
print("-" * 120)

identity_like = [
    col
    for col in e_cols
    if any(
        token in col.lower()
        for token in (
            "program",
            "programme",
            "name",
            "degree",
            "level",
            "university",
            "institution",
        )
    )
]

for col in identity_like:
    print(col)


print()
print("COMMON COLUMNS: EVIDENCE <-> BATCH LOCK")
print("-" * 120)

common_eb = [
    col for col in e_cols
    if col in b_cols
]

for col in common_eb:
    print(col)


print()
print("FIRST 3 EVIDENCE ROWS - NON-BLANK VALUES")
print("-" * 120)

for row in e_rows[:3]:

    pid = value(row, e_id)

    print()
    print(f"[{pid}]")

    for col in e_cols:

        v = value(row, col)

        if v:
            print(f"  {col}: {v}")


print()
print("FIRST 6 IDS - IDENTITY-RELATED SIDE-BY-SIDE")
print("-" * 120)

comparison_cols = []

all_cols = list(dict.fromkeys(
    e_cols + b_cols + q_cols
))

for col in all_cols:

    low = col.lower()

    if any(
        token in low
        for token in (
            "program_name",
            "programme_name",
            "verified_program",
            "verified_programme",
            "official_program",
            "official_programme",
            "degree_level",
            "verified_degree",
            "official_degree",
            "university_id",
            "institution_id",
        )
    ):
        comparison_cols.append(col)


for e_row in e_rows[:6]:

    pid = value(e_row, e_id)

    b_row = b_map.get(pid, {})
    q_row = q_map.get(pid, {})

    print()
    print("=" * 120)
    print(pid)
    print("=" * 120)

    for col in comparison_cols:

        e_val = value(e_row, col) if col in e_cols else ""
        b_val = value(b_row, col) if col in b_cols else ""
        q_val = value(q_row, col) if col in q_cols else ""

        if e_val or b_val or q_val:

            print(f"{col}")
            print(f"  EVIDENCE : {e_val or '<column absent/blank>'}")
            print(f"  BATCH    : {b_val or '<column absent/blank>'}")
            print(f"  QUEUE    : {q_val or '<column absent/blank>'}")


print()
print("=" * 120)
print("DIAGNOSTIC COMPLETE")
print("NO FILES MODIFIED")
print("NO CANONICAL WRITE")
print("NO MONGODB WRITE")
print("=" * 120)
