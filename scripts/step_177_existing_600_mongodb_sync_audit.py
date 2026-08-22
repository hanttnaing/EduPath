import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 120)
print("STEP 177 - EXISTING 600 PROGRAMMES MONGODB SYNC PREPARATION AUDIT")
print("=" * 120)


# --------------------------------------------------
# Load canonical
# --------------------------------------------------

with open(
    "data/cleaned/programs.json",
    encoding="utf-8"
) as f:
    programs = json.load(f)


south_korea = [
    p for p in programs
    if str(p.get("program_id","")).startswith("prog_kr_")
]


existing_600 = [
    p for p in programs
    if not str(p.get("program_id","")).startswith("prog_kr_")
]


canonical_ids = {
    p["program_id"]
    for p in existing_600
}


print()
print("CANONICAL AUDIT")
print("-" * 120)

print("Total programs.json:", len(programs))
print("South Korea programmes:", len(south_korea))
print("Existing 600 programmes:", len(existing_600))


# --------------------------------------------------
# Duplicate check
# --------------------------------------------------

from collections import Counter

id_counts = Counter(
    p["program_id"]
    for p in existing_600
)

duplicates = [
    k
    for k,v in id_counts.items()
    if v > 1
]


print()
print("DUPLICATE AUDIT")
print("-" * 120)

print(
    "Existing duplicate IDs:",
    len(duplicates)
)


# --------------------------------------------------
# MongoDB
# --------------------------------------------------

print()
print("MONGODB AUDIT")
print("-" * 120)


db = get_database()

collection = db["programmes"]


mongo_count = collection.count_documents({})


mongo_ids = set(
    collection.distinct("program_id")
)


collision = canonical_ids & mongo_ids


missing_from_mongo = canonical_ids - mongo_ids


print(
    "MongoDB current programmes:",
    mongo_count
)

print(
    "Existing canonical IDs:",
    len(canonical_ids)
)

print(
    "Already in MongoDB:",
    len(canonical_ids & mongo_ids)
)

print(
    "Missing from MongoDB:",
    len(missing_from_mongo)
)

print(
    "Collision IDs:",
    len(collision)
)


print()
print("=" * 120)

if len(collision) == 0:
    print(
        "STEP 177 EXISTING PROGRAMMES SYNC PREPARATION: PASS"
    )
else:
    print(
        "STEP 177 EXISTING PROGRAMMES SYNC PREPARATION: FAIL"
    )

print("=" * 120)


print()
print("FINAL RESULT")
print("-" * 120)

print("Canonical total:", len(programs))
print("South Korea:", len(south_korea))
print("Existing 600:", len(existing_600))
print("MongoDB current:", mongo_count)
print("Ready to insert:", len(missing_from_mongo))

