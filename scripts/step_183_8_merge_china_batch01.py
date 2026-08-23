import json
from pathlib import Path


CANONICAL = Path(
    "data/cleaned/programs.json"
)

STAGING = Path(
    "data/staging/china_batch_01/china_programme_batch01_verified.json"
)


print("=" * 80)
print("STEP 183.8 CHINA BATCH 01 CANONICAL MERGE")
print("=" * 80)


# Load canonical

with open(
    CANONICAL,
    encoding="utf-8"
) as f:
    programs = json.load(f)


# Load China staging

with open(
    STAGING,
    encoding="utf-8"
) as f:
    china_programmes = json.load(f)


existing_ids = {
    p["program_id"]
    for p in programs
}


duplicates = [
    p["program_id"]
    for p in china_programmes
    if p["program_id"] in existing_ids
]


print()
print("Existing programmes:")
print(len(programs))

print(
    "China staging programmes:"
    ,
    len(china_programmes)
)

print(
    "Duplicate IDs:",
    len(duplicates)
)


if duplicates:
    print(
        "Merge stopped because duplicate IDs exist."
    )
    exit(1)


# Merge

programs.extend(
    china_programmes
)


with open(
    CANONICAL,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        programs,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("Added:")
print(len(china_programmes))

print("After merge:")
print(len(programs))

print()
print("=" * 80)
print(
    "STEP 183.8 CHINA BATCH 01 MERGE COMPLETE"
)
print("=" * 80)