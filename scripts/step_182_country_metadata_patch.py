import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

from backend.app.database import get_database


print("=" * 120)
print("STEP 182 - COUNTRY METADATA NORMALIZATION PATCH")
print("=" * 120)


db = get_database()

collection = db["programmes"]


mapping = {
    "prog_jp_": ("Japan", "JP"),
    "prog_cn_": ("China", "CN"),
    "prog_tw_": ("Taiwan", "TW"),
    "prog_th_": ("Thailand", "TH"),
    "prog_kr_": ("South Korea", "KR"),
    "prog_hk_": ("Hong Kong", "HK"),
    "prog_id_": ("Indonesia", "ID"),
    "prog_my_": ("Malaysia", "MY"),
    "prog_sg_": ("Singapore", "SG"),
    "prog_vn_": ("Vietnam", "VN"),
    "prog_ph_": ("Philippines", "PH"),
    "prog_br_": ("Brunei", "BN"),
    "prog_kh_": ("Cambodia", "KH"),
    "prog_la_": ("Laos", "LA"),
    "prog_mm_": ("Myanmar", "MM"),
}


print()
print("PRE-PATCH AUDIT")
print("-" * 120)


before_missing = collection.count_documents(
    {
        "$or": [
            {"country": {"$exists": False}},
            {"country": None},
            {"country": ""}
        ]
    }
)


print(
    "Missing country before:",
    before_missing
)


print()
print("PATCH")
print("-" * 120)


total_modified = 0


for prefix, (country, code) in mapping.items():

    result = collection.update_many(
        {
            "program_id": {
                "$regex": "^" + prefix
            }
        },
        {
            "$set": {
                "country": country,
                "country_code": code,
                "country_name": country
            }
        }
    )

    if result.modified_count:
        print(
            prefix,
            "->",
            country,
            ":",
            result.modified_count
        )

    total_modified += result.modified_count


print()
print("POST-PATCH AUDIT")
print("-" * 120)


after_missing = collection.count_documents(
    {
        "$or": [
            {"country": {"$exists": False}},
            {"country": None},
            {"country": ""}
        ]
    }
)


print(
    "Modified total:",
    total_modified
)

print(
    "Missing country after:",
    after_missing
)


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
                "_id": 1
            }
        }
    ]
)


for item in countries:
    print(
        item["_id"],
        ":",
        item["count"]
    )


print()
print("=" * 120)


if after_missing == 0:
    print(
        "STEP 182 COUNTRY NORMALIZATION PATCH: PASS"
    )
else:
    print(
        "STEP 182 COUNTRY NORMALIZATION PATCH: FAIL"
    )

print("=" * 120)

