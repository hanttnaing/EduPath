import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 120)
print("STEP 179 - FULL DATABASE INTEGRITY VERIFICATION")
print("=" * 120)


# --------------------------------------------------
# Load canonical
# --------------------------------------------------

with open(
    "data/cleaned/programs.json",
    encoding="utf-8"
) as f:
    programs = json.load(f)


json_ids = [
    p["program_id"]
    for p in programs
]


json_id_set = set(json_ids)


# --------------------------------------------------
# JSON audit
# --------------------------------------------------

print()
print("CANONICAL JSON AUDIT")
print("-" * 120)

print("programs.json total:", len(programs))


json_duplicates = [
    k
    for k,v in Counter(json_ids).items()
    if v > 1
]


print(
    "JSON duplicate IDs:",
    len(json_duplicates)
)


# --------------------------------------------------
# MongoDB
# --------------------------------------------------

db = get_database()

collection = db["programs"]


mongo_docs = list(
    collection.find(
        {},
        {
            "_id":0,
            "program_id":1,
            "country":1,
            "university_id":1
        }
    )
)


mongo_ids = [
    p["program_id"]
    for p in mongo_docs
]


mongo_id_set = set(mongo_ids)


print()
print("MONGODB AUDIT")
print("-" * 120)

print(
    "MongoDB total:",
    len(mongo_docs)
)


mongo_duplicates = [
    k
    for k,v in Counter(mongo_ids).items()
    if v > 1
]


print(
    "MongoDB duplicate IDs:",
    len(mongo_duplicates)
)


# --------------------------------------------------
# Compare
# --------------------------------------------------

missing = json_id_set - mongo_id_set

extra = mongo_id_set - json_id_set


print()
print("ID CONSISTENCY AUDIT")
print("-" * 120)

print(
    "Missing MongoDB IDs:",
    len(missing)
)

print(
    "Extra MongoDB IDs:",
    len(extra)
)


# --------------------------------------------------
# South Korea
# --------------------------------------------------

kr_json = [
    p
    for p in programs
    if str(p.get("program_id","")).startswith("prog_kr_")
]


kr_mongo = [
    p
    for p in mongo_docs
    if str(p.get("program_id","")).startswith("prog_kr_")
]


print()
print("SOUTH KOREA AUDIT")
print("-" * 120)

print(
    "South Korea JSON:",
    len(kr_json)
)

print(
    "South Korea MongoDB:",
    len(kr_mongo)
)


# --------------------------------------------------
# Relationship
# --------------------------------------------------

orphan_programmes = [
    p
    for p in mongo_docs
    if not p.get("university_id")
]


print()
print("RELATIONSHIP AUDIT")
print("-" * 120)

print(
    "Orphan programmes:",
    len(orphan_programmes)
)


# --------------------------------------------------
# Final
# --------------------------------------------------

print()
print("=" * 120)


if (
    len(programs) == len(mongo_docs)
    and len(missing) == 0
    and len(extra) == 0
    and len(json_duplicates) == 0
    and len(mongo_duplicates) == 0
    and len(kr_json) == len(kr_mongo)
    and len(orphan_programmes) == 0
):
    print(
        "STEP 179 FULL DATABASE INTEGRITY AUDIT: PASS"
    )
else:
    print(
        "STEP 179 FULL DATABASE INTEGRITY AUDIT: FAIL"
    )

print("=" * 120)

