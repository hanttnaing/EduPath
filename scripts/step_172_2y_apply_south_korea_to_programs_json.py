from pathlib import Path
import json
import shutil
import hashlib
import sys
from datetime import datetime


ROOT = Path.cwd()

QUEUE = (
    ROOT /
    "planning" /
    "42_south_korea_program_research_queue_batch05_applied.csv"
)

PROGRAMS = (
    ROOT /
    "data" /
    "cleaned" /
    "programs.json"
)

BACKUP_DIR = (
    ROOT /
    "data" /
    "cleaned" /
    "backup"
)



def sha256(path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        for chunk in iter(
            lambda:f.read(1024*1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()



print("="*130)
print(
    "STEP 172.2Y - APPLY SOUTH KOREA 150 VERIFIED PROGRAMMES TO programs.json"
)
print("="*130)



for file in [QUEUE, PROGRAMS]:

    print(
        file.name,
        "exists:",
        "PASS" if file.exists() else "FAIL"
    )

    if not file.exists():
        sys.exit(1)



print()
print("PRE-MERGE AUDIT")
print("-"*130)



with PROGRAMS.open(
    "r",
    encoding="utf-8"
) as f:

    existing = json.load(f)



print(
    "Existing programs:",
    len(existing)
)



existing_ids = {
    p["program_id"]
    for p in existing
}



print(
    "Existing duplicate IDs:",
    "PASS"
    if len(existing_ids)==len(existing)
    else "FAIL"
)



# backup

BACKUP_DIR.mkdir(
    exist_ok=True
)


backup_file = (
    BACKUP_DIR /
    f"programs_before_south_korea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
)


shutil.copy2(
    PROGRAMS,
    backup_file
)



print(
    "Backup created:",
    backup_file
)



# load staged queue

import csv


with QUEUE.open(
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    reader = csv.DictReader(f)

    staged = list(reader)



south_korea = [
    p
    for p in staged
    if p["program_id"].startswith("prog_kr_")
]


print()
print("SOUTH KOREA AUDIT")
print("-"*130)


print(
    "South Korea staged programmes:",
    len(south_korea)
)



if len(south_korea) != 150:

    print("FAIL: South Korea count incorrect")
    sys.exit(1)



duplicates = (
    existing_ids
    &
    {
        p["program_id"]
        for p in south_korea
    }
)


print(
    "South Korea duplicate IDs:",
    len(duplicates)
)



if duplicates:

    print(
        "Duplicate IDs:",
        duplicates
    )

    sys.exit(1)



# merge

merged = existing + south_korea



print()
print("MERGE AUDIT")
print("-"*130)



print(
    "Before:",
    len(existing)
)


print(
    "Added:",
    len(south_korea)
)


print(
    "After:",
    len(merged)
)



if len(merged) != 750:

    print("FAIL: Final count not 750")
    sys.exit(1)



all_ids = [
    p["program_id"]
    for p in merged
]


print(
    "Final duplicate IDs:",
    "PASS"
    if len(all_ids)==len(set(all_ids))
    else "FAIL"
)



# write

with PROGRAMS.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        merged,
        f,
        ensure_ascii=False,
        indent=2
    )



print()
print("POST-WRITE AUDIT")
print("-"*130)



with PROGRAMS.open(
    "r",
    encoding="utf-8"
) as f:

    final = json.load(f)



print(
    "Final programs.json:",
    len(final)
)



print(
    "SHA256:",
    sha256(PROGRAMS)
)



print()
print("="*130)
print(
    "STEP 172.2Y APPLY SOUTH KOREA PROGRAMMES: PASS"
)
print("="*130)



print()

print(
    "Programs before:",
    len(existing)
)

print(
    "South Korea added:",
    len(south_korea)
)

print(
    "Programs after:",
    len(final)
)

print(
    "Backup:",
    backup_file
)

print(
    "MongoDB WRITE PERFORMED:",
    False
)


print()
print("NEXT: STEP 172.2Z")
print(
    "FINAL SOUTH KOREA CANONICAL + DATABASE VERIFICATION"
)