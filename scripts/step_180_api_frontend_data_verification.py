import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 120)
print("STEP 180 - API + FRONTEND DATA VERIFICATION")
print("=" * 120)


db = get_database()

collection = db["programmes"]


# --------------------------------------------------
# Total API source audit
# --------------------------------------------------

print()
print("DATABASE SOURCE AUDIT")
print("-" * 120)


total = collection.count_documents({})


print(
    "MongoDB programmes:",
    total
)


# --------------------------------------------------
# South Korea
# --------------------------------------------------

south_korea = collection.count_documents(
    {
        "country": "South Korea"
    }
)


print(
    "South Korea programmes:",
    south_korea
)


# --------------------------------------------------
# Country distribution
# --------------------------------------------------

print()
print("COUNTRY DISTRIBUTION")
print("-" * 120)


countries = collection.aggregate(
    [
        {
            "$group": {
                "_id": "$country",
                "count": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "count": -1
            }
        }
    ]
)


for c in countries:
    print(
        c["_id"],
        ":",
        c["count"]
    )


# --------------------------------------------------
# Sample programme
# --------------------------------------------------

print()
print("PROGRAMME DETAIL TEST")
print("-" * 120)


sample = collection.find_one(
    {
        "program_id": "prog_kr_001"
    },
    {
        "_id":0
    }
)


if sample:

    print(
        "Programme ID:",
        sample.get("program_id")
    )

    print(
        "University:",
        sample.get("university_name")
    )

    print(
        "Country:",
        sample.get("country")
    )

    print(
        "University ID:",
        sample.get("university_id")
    )


# --------------------------------------------------
# Relationship
# --------------------------------------------------

orphans = collection.count_documents(
    {
        "$or": [
            {
                "university_id": {
                    "$exists": False
                }
            },
            {
                "university_id": ""
            },
            {
                "university_id": None
            }
        ]
    }
)


print()
print("RELATIONSHIP TEST")
print("-" * 120)

print(
    "Orphan programmes:",
    orphans
)


# --------------------------------------------------
# Final
# --------------------------------------------------

print()
print("=" * 120)


if (
    total == 750
    and south_korea == 150
    and orphans == 0
):
    print(
        "STEP 180 API DATA VERIFICATION: PASS"
    )
else:
    print(
        "STEP 180 API DATA VERIFICATION: FAIL"
    )


print("=" * 120)

