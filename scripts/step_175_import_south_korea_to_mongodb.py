import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 130)
print("STEP 175 - SAFE SOUTH KOREA MONGODB IMPORT")
print("=" * 130)


program_path = Path("data/cleaned/programs.json")


# --------------------------------------------------
# Load canonical data
# --------------------------------------------------

print()
print("SOURCE AUDIT")
print("-" * 130)


with open(program_path, encoding="utf-8") as f:
    programs = json.load(f)


south_korea = [
    p
    for p in programs
    if str(p.get("program_id", "")).startswith("prog_kr_")
]


print(f"Canonical programmes: {len(programs)}")
print(f"South Korea import candidates: {len(south_korea)}")


if len(south_korea) != 150:
    raise SystemExit(
        "South Korea programme count mismatch"
    )


# --------------------------------------------------
# MongoDB
# --------------------------------------------------

print()
print("MONGODB PRE-IMPORT AUDIT")
print("-" * 130)


database = get_database()

collection = database["programmes"]


before_count = collection.count_documents({})


existing_ids = set(
    collection.distinct("program_id")
)


south_ids = {
    p["program_id"]
    for p in south_korea
}


collision = existing_ids & south_ids


print(f"MongoDB before count: {before_count}")
print(f"Existing IDs: {len(existing_ids)}")
print(f"Collision IDs: {len(collision)}")


if collision:
    raise SystemExit(
        f"Duplicate program IDs detected: {collision}"
    )


# --------------------------------------------------
# Backup snapshot
# --------------------------------------------------

print()
print("IMPORT")
print("-" * 130)


for p in south_korea:
    p["created_at"] = datetime.utcnow().isoformat()


result = collection.insert_many(
    south_korea
)


print(
    f"Inserted documents: {len(result.inserted_ids)}"
)


# --------------------------------------------------
# Post verify
# --------------------------------------------------

after_count = collection.count_documents({})


inserted_kr = list(
    collection.find(
        {
            "program_id": {
                "$regex": "^prog_kr_"
            }
        },
        {
            "_id":0,
            "program_id":1
        }
    )
)


inserted_ids = sorted(
    x["program_id"]
    for x in inserted_kr
)


duplicates = [
    k
    for k,v in Counter(inserted_ids).items()
    if v > 1
]


print()
print("POST IMPORT AUDIT")
print("-" * 130)

print(f"MongoDB after count: {after_count}")
print(f"South Korea MongoDB count: {len(inserted_ids)}")

print(
    f"ID range: {inserted_ids[0]} -> {inserted_ids[-1]}"
)


print(
    f"Duplicate South Korea IDs: "
    f"{'PASS | 0' if len(duplicates)==0 else duplicates}"
)


print()
print("=" * 130)
print("STEP 175 SOUTH KOREA MONGODB IMPORT: COMPLETE")
print("=" * 130)


print()
print("FINAL RESULT")
print("-" * 130)

print(f"Inserted South Korea programmes : {len(result.inserted_ids)}")
print(f"MongoDB total programmes         : {after_count}")
print(f"South Korea MongoDB programmes   : {len(inserted_ids)}")
print(f"Duplicate IDs                    : {len(duplicates)}")

