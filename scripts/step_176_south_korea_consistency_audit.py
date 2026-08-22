import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 120)
print("STEP 176 - SOUTH KOREA MONGODB CONSISTENCY AUDIT")
print("=" * 120)


# --------------------------------------------------
# Load canonical
# --------------------------------------------------

with open(
    "data/cleaned/programs.json",
    encoding="utf-8"
) as f:
    programs = json.load(f)


json_kr = [
    p
    for p in programs
    if str(p.get("program_id","")).startswith("prog_kr_")
]


json_ids = {
    p["program_id"]
    for p in json_kr
}


print()
print("CANONICAL AUDIT")
print("-" * 120)

print("Total programs.json:", len(programs))
print("South Korea JSON:", len(json_kr))


# --------------------------------------------------
# MongoDB
# --------------------------------------------------

db = get_database()

collection = db["programmes"]


mongo_kr_docs = list(
    collection.find(
        {
            "program_id": {
                "$regex": "^prog_kr_"
            }
        },
        {
            "_id":0,
            "program_id":1,
            "country":1,
            "country_code":1
        }
    )
)


mongo_ids = {
    p["program_id"]
    for p in mongo_kr_docs
}


print()
print("MONGODB AUDIT")
print("-" * 120)

print("MongoDB total documents:",
      collection.count_documents({}))

print("South Korea MongoDB:",
      len(mongo_kr_docs))


# --------------------------------------------------
# Compare
# --------------------------------------------------

missing = json_ids - mongo_ids
extra = mongo_ids - json_ids


wrong_country = [
    p
    for p in mongo_kr_docs
    if p.get("country") != "South Korea"
]


print()
print("CONSISTENCY AUDIT")
print("-" * 120)

print(
    "Missing MongoDB IDs:",
    len(missing)
)

print(
    "Extra MongoDB IDs:",
    len(extra)
)

print(
    "Wrong country fields:",
    len(wrong_country)
)


print()
print("=" * 120)

if (
    len(json_kr) == 150
    and len(mongo_kr_docs) == 150
    and len(missing) == 0
    and len(extra) == 0
    and len(wrong_country) == 0
):
    print(
        "STEP 176 SOUTH KOREA CONSISTENCY AUDIT: PASS"
    )
else:
    print(
        "STEP 176 SOUTH KOREA CONSISTENCY AUDIT: FAIL"
    )

print("=" * 120)

