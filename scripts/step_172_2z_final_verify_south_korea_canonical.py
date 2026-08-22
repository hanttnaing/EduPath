import json
import hashlib
from pathlib import Path
from collections import Counter

print("=" * 130)
print("STEP 172.2Z - FINAL SOUTH KOREA CANONICAL + DATABASE VERIFICATION")
print("=" * 130)

program_path = Path("data/cleaned/programs.json")

queue_path = Path(
    "planning/42_south_korea_program_research_queue_batch05_applied.csv"
)

print()

# --------------------------------------------------
# FILE EXISTENCE
# --------------------------------------------------

print("FILE AUDIT")
print("-" * 130)

print(
    f"programs.json exists: "
    f"{'PASS' if program_path.exists() else 'FAIL'}"
)

print(
    f"South Korea final queue exists: "
    f"{'PASS' if queue_path.exists() else 'FAIL'}"
)

if not program_path.exists():
    raise SystemExit("programs.json missing")

if not queue_path.exists():
    raise SystemExit("South Korea queue missing")


# --------------------------------------------------
# HASH
# --------------------------------------------------

sha = hashlib.sha256(
    program_path.read_bytes()
).hexdigest()

print()
print("HASH AUDIT")
print("-" * 130)

print(f"programs.json SHA256: {sha}")


# --------------------------------------------------
# LOAD
# --------------------------------------------------

with open(program_path, encoding="utf-8") as f:
    programs = json.load(f)


print()
print("CANONICAL AUDIT")
print("-" * 130)


print(f"Total programmes: {len(programs)}")


ids = [
    p.get("program_id")
    for p in programs
]


duplicates = [
    k for k,v in Counter(ids).items()
    if v > 1
]


print(
    f"Duplicate programme IDs: "
    f"{'PASS | 0' if len(duplicates)==0 else 'FAIL'}"
)


# --------------------------------------------------
# SOUTH KOREA
# --------------------------------------------------

south_korea = [
    p
    for p in programs
    if str(p.get("program_id","")).startswith("prog_kr_")
]


print()
print("SOUTH KOREA AUDIT")
print("-" * 130)

print(
    f"South Korea programmes: {len(south_korea)}"
)


kr_ids = sorted(
    p["program_id"]
    for p in south_korea
)


print(
    f"South Korea ID range: "
    f"{kr_ids[0]} -> {kr_ids[-1]}"
)


print(
    f"South Korea duplicate IDs: "
    f"{'PASS' if len(set(kr_ids))==150 else 'FAIL'}"
)


# --------------------------------------------------
# PRESERVATION
# --------------------------------------------------

print()
print("FINAL STATUS")
print("-" * 130)

print(
    f"Expected canonical total 750: "
    f"{'PASS' if len(programs)==750 else 'FAIL'}"
)

print(
    f"Expected South Korea 150: "
    f"{'PASS' if len(south_korea)==150 else 'FAIL'}"
)


print()
print("=" * 130)
print("STEP 172.2Z SOUTH KOREA FINAL CANONICAL VERIFICATION: COMPLETE")
print("=" * 130)

print()
print("FINAL RESULT")
print("-" * 130)
print(f"programs.json programmes        : {len(programs)}")
print(f"South Korea programmes          : {len(south_korea)}")
print(f"Duplicate programme IDs         : {len(duplicates)}")
print(f"MongoDB write                   : NOT PERFORMED")
print(f"SHA256                          : {sha}")

