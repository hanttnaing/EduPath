import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 120)
print("STEP 182B - SYNC SOUTH KOREA INTO API PROGRAMS COLLECTION")
print("=" * 120)


db = get_database()

source = db["programmes"]
target = db["programs"]


print()
print("PRE-SYNC AUDIT")
print("-" * 120)


source_count = source.count_documents(
    {
        "country_id": "country_kr"
    }
)

target_before = target.count_documents({})


print(
    "Source South Korea programmes:",
    source_count
)

print(
    "Target programs before:",
    target_before
)


# --------------------------------------------------
# Load South Korea programmes
# --------------------------------------------------

south_korea_programmes = list(
    source.find(
        {
            "country_id": "country_kr"
        },
        {
            "_id": 0
        }
    )
)


source_ids = [
    p["program_id"]
    for p in south_korea_programmes
]


# --------------------------------------------------
# Collision audit
# --------------------------------------------------

existing = list(
    target.find(
        {
            "program_id": {
                "$in": source_ids
            }
        },
        {
            "_id": 0,
            "program_id": 1
        }
    )
)


collision_ids = [
    x["program_id"]
    for x in existing
]


print()
print("COLLISION AUDIT")
print("-" * 120)

print(
    "Collisions:",
    len(collision_ids)
)


if collision_ids:
    print(
        collision_ids[:10]
    )
    raise SystemExit(
        "STOP: Duplicate program IDs detected"
    )


# --------------------------------------------------
# Insert
# --------------------------------------------------

print()
print("IMPORT")
print("-" * 120)


if south_korea_programmes:

    result = target.insert_many(
        south_korea_programmes
    )

    inserted = len(result.inserted_ids)

else:
    inserted = 0


print(
    "Inserted:",
    inserted
)


# --------------------------------------------------
# Post audit
# --------------------------------------------------

target_after = target.count_documents({})


kr_after = target.count_documents(
    {
        "country_id": "country_kr"
    }
)


print()
print("POST-SYNC AUDIT")
print("-" * 120)

print(
    "Target programs after:",
    target_after
)

print(
    "South Korea in programs:",
    kr_after
)


print()
print("=" * 120)


if (
    inserted == 150
    and target_after == 750
    and kr_after == 150
):
    print(
        "STEP 182B SOUTH KOREA PROGRAM SYNC: PASS"
    )
else:
    print(
        "STEP 182B SOUTH KOREA PROGRAM SYNC: FAIL"
    )


print("=" * 120)

