import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 120)
print("STEP 181 - COUNTRY METADATA NORMALIZATION AUDIT")
print("=" * 120)


# --------------------------------------------------
# Load canonical
# --------------------------------------------------

with open(
    "data/cleaned/programs.json",
    encoding="utf-8"
) as f:
    programs = json.load(f)


print()
print("CANONICAL COUNTRY AUDIT")
print("-" * 120)


json_country = Counter(
    str(
        p.get(
            "country",
            p.get("country_name", "MISSING")
        )
    )
    for p in programs
)


for country, count in json_country.items():
    print(country, ":", count)


# --------------------------------------------------
# MongoDB
# --------------------------------------------------

db = get_database()

collection = db["programmes"]


print()
print("MONGODB COUNTRY AUDIT")
print("-" * 120)


mongo_docs = list(
    collection.find(
        {},
        {
            "_id":0,
            "program_id":1,
            "country":1,
            "country_id":1,
            "university_id":1
        }
    )
)


mongo_country = Counter(
    str(
        p.get(
            "country",
            "MISSING"
        )
    )
    for p in mongo_docs
)


for country, count in mongo_country.items():
    print(country, ":", count)


# --------------------------------------------------
# Missing country
# --------------------------------------------------

missing_country = [
    p
    for p in mongo_docs
    if not p.get("country")
]


print()
print("MISSING COUNTRY FIELD AUDIT")
print("-" * 120)

print(
    "Missing country records:",
    len(missing_country)
)


# --------------------------------------------------
# Sample missing
# --------------------------------------------------

print()

for p in missing_country[:10]:
    print(
        p.get("program_id"),
        "|",
        p.get("country_id"),
        "|",
        p.get("university_id")
    )


print()
print("=" * 120)

if len(missing_country) > 0:
    print(
        "STEP 181 COUNTRY NORMALIZATION REQUIRED"
    )
else:
    print(
        "STEP 181 COUNTRY NORMALIZATION NOT REQUIRED"
    )

print("=" * 120)

