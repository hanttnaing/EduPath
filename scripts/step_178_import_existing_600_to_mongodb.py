import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 120)
print("STEP 178 - SAFE EXISTING 600 PROGRAMMES MONGODB IMPORT")
print("=" * 120)


with open(
    "data/cleaned/programs.json",
    encoding="utf-8"
) as f:
    programs = json.load(f)


existing = [
    p
    for p in programs
    if not str(p.get("program_id","")).startswith("prog_kr_")
]


print()
print("SOURCE AUDIT")
print("-" * 120)

print("Canonical total:", len(programs))
print("Existing import candidates:", len(existing))


if len(existing) != 600:
    raise SystemExit("Existing programme count mismatch")


ids = [
    p["program_id"]
    for p in existing
]


duplicates = [
    k
    for k,v in Counter(ids).items()
    if v > 1
]


print("Duplicate source IDs:", len(duplicates))


db = get_database()

collection = db["programmes"]


print()
print("MONGODB PRE-IMPORT")
print("-" * 120)


before = collection.count_documents({})


existing_db_ids = set(
    collection.distinct("program_id")
)


collision = (
    existing_db_ids
    &
    set(ids)
)


print("MongoDB before:", before)
print("Collision IDs:", len(collision))


if collision:
    raise SystemExit(
        f"Collision detected: {collision}"
    )


print()
print("IMPORT")
print("-" * 120)


result = collection.insert_many(existing)


print(
    "Inserted:",
    len(result.inserted_ids)
)


after = collection.count_documents({})


kr_count = collection.count_documents(
    {
        "program_id": {
            "$regex": "^prog_kr_"
        }
    }
)


print()
print("POST IMPORT AUDIT")
print("-" * 120)

print("MongoDB total:", after)
print("South Korea preserved:", kr_count)


all_ids = collection.distinct("program_id")


dup_db = [
    k
    for k,v in Counter(all_ids).items()
    if v > 1
]


print("Duplicate IDs:", len(dup_db))


print()
print("=" * 120)

if (
    len(result.inserted_ids) == 600
    and after == 750
    and kr_count == 150
    and len(dup_db) == 0
):
    print("STEP 178 EXISTING 600 MONGODB IMPORT: PASS")
else:
    print("STEP 178 EXISTING 600 MONGODB IMPORT: FAIL")

print("=" * 120)

