import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 100)
print("STEP 184 - FIX SOUTH KOREA DURATION YEARS SCHEMA")
print("=" * 100)


db = get_database()

collection = db["programs"]


result = collection.update_many(
    {
        "country_id": "country_kr"
    },
    {
        "$set": {
            "duration_years": None
        }
    }
)


print()
print("Modified:", result.modified_count)


doc = collection.find_one(
    {
        "country_id": "country_kr"
    }
)


print()
print("VERIFY")
print(
    "duration_years:",
    doc.get("duration_years")
)


print("=" * 100)
print("STEP 184 COMPLETE")
print("=" * 100)