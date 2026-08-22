import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from collections import Counter
from pymongo import MongoClient

print("=" * 130)
print("STEP 174 - SOUTH KOREA MONGODB SYNC PREPARATION DRY-RUN AUDIT")
print("=" * 130)


# --------------------------------------------------
# FILES
# --------------------------------------------------

program_path = Path("data/cleaned/programs.json")


print()
print("FILE AUDIT")
print("-" * 130)

print(
    f"programs.json exists: "
    f"{'PASS' if program_path.exists() else 'FAIL'}"
)


if not program_path.exists():
    raise SystemExit("programs.json missing")


# --------------------------------------------------
# LOAD JSON
# --------------------------------------------------

with open(program_path, encoding="utf-8") as f:
    programs = json.load(f)


south_korea = [
    p for p in programs
    if str(p.get("program_id","")).startswith("prog_kr_")
]


print()
print("CANONICAL AUDIT")
print("-" * 130)

print(f"Canonical programmes: {len(programs)}")
print(f"South Korea programmes: {len(south_korea)}")


# --------------------------------------------------
# DUPLICATE CHECK
# --------------------------------------------------

ids = [
    p.get("program_id")
    for p in programs
]


duplicates = [
    k for k,v in Counter(ids).items()
    if v > 1
]


print(
    f"Canonical duplicate IDs: "
    f"{'PASS | 0' if len(duplicates)==0 else duplicates}"
)


# --------------------------------------------------
# MONGODB CONNECTION
# --------------------------------------------------

print()
print("MONGODB CONNECTION AUDIT")
print("-" * 130)


try:

    from backend.app.database import get_database

    database = get_database()
    collection = database["programmes"]

    mongo_count = collection.count_documents({})

    print("MongoDB connection: PASS")
    print(f"Current MongoDB programmes: {mongo_count}")


except Exception as e:

    print("MongoDB connection: FAIL")
    print(e)

    raise SystemExit()


# --------------------------------------------------
# EXISTING IDS
# --------------------------------------------------

existing_ids = set(
    collection.distinct("program_id")
)


south_ids = {
    p["program_id"]
    for p in south_korea
}


collision = (
    existing_ids &
    south_ids
)


print()
print("COLLISION AUDIT")
print("-" * 130)

print(
    f"Existing MongoDB IDs: {len(existing_ids)}"
)

print(
    f"South Korea IDs ready: {len(south_ids)}"
)


print(
    f"Program ID collisions: "
    f"{'PASS | 0' if len(collision)==0 else collision}"
)


# --------------------------------------------------
# DRY RUN
# --------------------------------------------------

print()
print("DRY-RUN IMPORT AUDIT")
print("-" * 130)


print(
    f"Would insert: {len(south_korea)} programmes"
)


print(
    f"MongoDB after import estimate: "
    f"{mongo_count + len(south_korea)}"
)


print()
print("=" * 130)
print("STEP 174 SOUTH KOREA MONGODB SYNC PREPARATION: COMPLETE")
print("=" * 130)


print()
print("FINAL RESULT")
print("-" * 130)

print(f"JSON programmes          : {len(programs)}")
print(f"South Korea ready        : {len(south_korea)}")
print(f"MongoDB current          : {mongo_count}")
print(f"Collisions               : {len(collision)}")
print("WRITE PERFORMED          : False")

