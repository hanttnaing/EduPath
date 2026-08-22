import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.app.database import get_database

sys.path.insert(0, str(Path('.').resolve()))
from backend.app.database import get_database


db = get_database()

collection = db["programs"]


kr_programs = list(
    collection.find(
        {
            "country_id":"country_kr"
        }
    )
)


modified = 0


for p in kr_programs:

    update = {}

    numeric_fields = [
        "duration_years",
        "tuition_fee",
        "minimum_gpa",
        "gpa_scale",
        "ielts_requirement",
        "toefl_requirement",
    ]


    for field in numeric_fields:
        if p.get(field) == "":
            update[field] = None


    list_fields = [
        "intake"
    ]

    for field in list_fields:
        if p.get(field) == "":
            update[field] = []


    date_fields = [
        "application_deadline",
        "last_verified_at",
        "international_applicants_last_verified_at",
    ]

    for field in date_fields:
        if p.get(field) == "":
            update[field] = None


    if "collected_at" not in p:
        update["collected_at"] = "2026-08-22T00:00:00"


    if "freshness_status" not in p:
        update["freshness_status"] = "verified"


    if update:
        collection.update_one(
            {
                "_id":p["_id"]
            },
            {
                "$set":update
            }
        )

        modified += 1


print("="*100)
print("STEP 182C SOUTH KOREA API SCHEMA NORMALIZATION")
print("="*100)

print("Matched:", len(kr_programs))
print("Modified:", modified)

print("="*100)
