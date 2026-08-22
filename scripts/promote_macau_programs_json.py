import json
import os
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path


CANONICAL = Path(
    "data/cleaned/programs.json"
)

STAGING = Path(
    "data/cleaned/programs_with_macau_staging.json"
)

BACKUP_DIR = Path(
    "data/backups/step_170_2g"
)

EXPECTED_BEFORE = 336
EXPECTED_AFTER = 357
EXPECTED_MACAU = 21


def clean(value):
    return str(value or "").strip()


def prefix(program_id):

    parts = clean(program_id).split("_")

    if len(parts) >= 3:
        return "_".join(parts[:2])

    return "unknown"


print("=" * 110)
print(
    "STEP 170.2G - PROMOTE MACAU STAGING "
    "TO CANONICAL PROGRAMS.JSON"
)
print("=" * 110)


for path in [
    CANONICAL,
    STAGING,
]:

    if not path.exists():
        raise FileNotFoundError(
            f"Required file missing: {path}"
        )


with CANONICAL.open(
    "r",
    encoding="utf-8",
) as file:

    current = json.load(file)


with STAGING.open(
    "r",
    encoding="utf-8",
) as file:

    staging = json.load(file)


if not isinstance(current, list):
    raise ValueError(
        "Canonical programs.json is not a list."
    )


if not isinstance(staging, list):
    raise ValueError(
        "Macau staging JSON is not a list."
    )


current_ids = [
    clean(row.get("program_id"))
    for row in current
]

staging_ids = [
    clean(row.get("program_id"))
    for row in staging
]


print(
    "Current canonical rows            :",
    len(current),
)

print(
    "Staging rows                      :",
    len(staging),
)

print(
    "Current duplicate IDs             :",
    len(current_ids)
    - len(set(current_ids)),
)

print(
    "Staging duplicate IDs             :",
    len(staging_ids)
    - len(set(staging_ids)),
)


if len(current) != EXPECTED_BEFORE:

    raise ValueError(
        f"Expected current canonical count "
        f"{EXPECTED_BEFORE}, found {len(current)}."
    )


if len(staging) != EXPECTED_AFTER:

    raise ValueError(
        f"Expected staging count "
        f"{EXPECTED_AFTER}, found {len(staging)}."
    )


if len(current_ids) != len(set(current_ids)):

    raise ValueError(
        "Current programs.json contains "
        "duplicate IDs."
    )


if len(staging_ids) != len(set(staging_ids)):

    raise ValueError(
        "Staging contains duplicate IDs."
    )


# ------------------------------------------------------------
# Critical preservation check
# ------------------------------------------------------------

existing_preserved = (
    staging[:EXPECTED_BEFORE]
    == current
)


changed_existing = sum(
    staging[index] != current[index]
    for index in range(
        EXPECTED_BEFORE
    )
)


if not existing_preserved:

    raise ValueError(
        "Safety stop: existing 336 canonical "
        "records are not preserved exactly."
    )


macau = [
    row
    for row in staging
    if clean(
        row.get("program_id")
    ).startswith(
        "prog_mo_"
    )
]


statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in macau
)


blank_international_dates = [
    clean(row.get("program_id"))
    for row in macau
    if not clean(
        row.get(
            "international_applicants_last_verified_at"
        )
    )
]


verified_yes_blank_urls = [
    clean(row.get("program_id"))
    for row in macau
    if (
        clean(
            row.get(
                "international_applicants_status"
            )
        ) == "verified_yes"
        and not clean(
            row.get(
                "international_application_url"
            )
        )
    )
]


prefix_counts = Counter(
    prefix(program_id)
    for program_id in staging_ids
)


print()
print("PRE-PROMOTION SAFETY AUDIT")
print("-" * 110)

print(
    "Existing 336 exact-preserved      :",
    existing_preserved,
)

print(
    "Existing records changed          :",
    changed_existing,
)

print(
    "Macau programmes                  :",
    len(macau),
)

print(
    "Macau international statuses      :",
    dict(statuses),
)

print(
    "verified_yes blank URLs           :",
    len(verified_yes_blank_urls),
)

print(
    "Blank international dates         :",
    len(blank_international_dates),
)

print(
    "Programme prefix counts           :",
    dict(prefix_counts),
)


if len(macau) != EXPECTED_MACAU:

    raise ValueError(
        f"Expected {EXPECTED_MACAU} Macau "
        f"programmes, found {len(macau)}."
    )


if statuses != Counter({
    "verified_yes": 20,
    "unknown": 1,
}):

    raise ValueError(
        "Unexpected Macau international statuses."
    )


if verified_yes_blank_urls:

    raise ValueError(
        "verified_yes Macau programme "
        "has blank international URL."
    )


if blank_international_dates:

    raise ValueError(
        "Macau international verification "
        "date missing."
    )


# ------------------------------------------------------------
# Backup canonical BEFORE promotion
# ------------------------------------------------------------

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)


backup_path = BACKUP_DIR / (
    "programs_before_macau_promotion_"
    f"{timestamp}.json"
)


shutil.copy2(
    CANONICAL,
    backup_path,
)


print()
print(
    "Canonical backup                  :",
    backup_path,
)


# ------------------------------------------------------------
# Atomic promotion
# ------------------------------------------------------------

temp_path = CANONICAL.with_name(
    "programs_macau_promotion_temp.json"
)


with temp_path.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        staging,
        file,
        ensure_ascii=False,
        indent=2,
    )


# Validate temp before replacing canonical.
with temp_path.open(
    "r",
    encoding="utf-8",
) as file:

    temp_data = json.load(file)


if temp_data != staging:

    raise ValueError(
        "Temporary promotion file "
        "does not match staging."
    )


os.replace(
    temp_path,
    CANONICAL,
)


# ------------------------------------------------------------
# Post-promotion verification
# ------------------------------------------------------------

with CANONICAL.open(
    "r",
    encoding="utf-8",
) as file:

    promoted = json.load(file)


promoted_ids = [
    clean(
        row.get("program_id")
    )
    for row in promoted
]


promoted_macau = [
    row
    for row in promoted
    if clean(
        row.get("program_id")
    ).startswith(
        "prog_mo_"
    )
]


promoted_prefix_counts = Counter(
    prefix(program_id)
    for program_id in promoted_ids
)


existing_after_promotion = (
    promoted[:EXPECTED_BEFORE]
    == current
)


promoted_statuses = Counter(
    clean(
        row.get(
            "international_applicants_status"
        )
    )
    for row in promoted_macau
)


print()
print("POST-PROMOTION VERIFICATION")
print("-" * 110)

print(
    "Canonical rows                    :",
    len(promoted),
)

print(
    "Duplicate IDs                     :",
    len(promoted_ids)
    - len(set(promoted_ids)),
)

print(
    "Existing 336 exact-preserved      :",
    existing_after_promotion,
)

print(
    "Macau programmes                  :",
    len(promoted_macau),
)

print(
    "Macau international statuses      :",
    dict(promoted_statuses),
)

print(
    "Programme prefix counts           :",
    dict(promoted_prefix_counts),
)


assert len(promoted) == EXPECTED_AFTER

assert (
    len(promoted_ids)
    == len(set(promoted_ids))
)

assert existing_after_promotion

assert len(promoted_macau) == 21

assert promoted_statuses == Counter({
    "verified_yes": 20,
    "unknown": 1,
})


print()
print("=" * 110)

print(
    "STEP 170.2G MACAU CANONICAL "
    "PROMOTION: PASS"
)

print(
    "programs.json TOTAL: 357"
)

print(
    "EXISTING 336 PROGRAMMES "
    "PRESERVED EXACTLY"
)

print(
    "MACAU PROGRAMMES PROMOTED: 21"
)

print(
    "MONGODB WAS NOT MODIFIED"
)

print("=" * 110)
