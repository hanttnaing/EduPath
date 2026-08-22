import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 100)
print("STEP 183 - SOUTH KOREA PROGRAM DISPLAY COMPATIBILITY PATCH")
print("=" * 100)


db = get_database()

collection = db["programs"]


query = {
    "country_id": "country_kr"
}


programs = list(collection.find(query))


print()
print("MATCHED:", len(programs))


modified = 0


for program in programs:

    update = {}

    if not program.get("study_mode"):
        update["study_mode"] = "Full-time"

    if not program.get("language_of_instruction"):
        update["language_of_instruction"] = "English / Korean"

    if not program.get("duration_years"):
        update["duration_years"] = "Not specified"

    if not program.get("tuition_currency"):
        update["tuition_currency"] = "KRW"

    if not program.get("tuition_period"):
        update["tuition_period"] = "Annual"

    if not program.get("tuition_academic_year"):
        update["tuition_academic_year"] = 2026

    if not program.get("intake"):
        update["intake"] = ["Spring", "Fall"]


    if update:
        collection.update_one(
            {
                "program_id": program["program_id"]
            },
            {
                "$set": update
            }
        )

        modified += 1


print()
print("MODIFIED:", modified)


remaining = collection.count_documents(
    {
        "country_id": "country_kr",
        "study_mode": "",
    }
)


print()
print("VERIFY")
print("Remaining empty study_mode:", remaining)


print("=" * 100)
print("STEP 183 SOUTH KOREA DISPLAY COMPATIBILITY PATCH COMPLETE")
print("=" * 100)