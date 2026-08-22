import json
from pathlib import Path
from collections import Counter, defaultdict

print("=" * 130)
print("STEP 173 - SOUTH KOREA UNIVERSITY CANONICAL VERIFICATION")
print("=" * 130)

program_path = Path("data/cleaned/programs.json")

print()

print("FILE AUDIT")
print("-" * 130)

print(
    f"programs.json exists: "
    f"{'PASS' if program_path.exists() else 'FAIL'}"
)

if not program_path.exists():
    raise SystemExit("programs.json missing")


with open(program_path, encoding="utf-8") as f:
    programs = json.load(f)


print()
print("CANONICAL PROGRAM AUDIT")
print("-" * 130)

print(f"Total programmes: {len(programs)}")


# --------------------------------------------------
# South Korea programmes
# --------------------------------------------------

south_korea = [
    p for p in programs
    if str(p.get("program_id","")).startswith("prog_kr_")
]


print(
    f"South Korea programmes: {len(south_korea)}"
)


# --------------------------------------------------
# University IDs
# --------------------------------------------------

university_ids = [
    p.get("university_id")
    for p in south_korea
]


unique_universities = sorted(
    set(university_ids)
)


print()
print("UNIVERSITY AUDIT")
print("-" * 130)

print(
    f"South Korea universities: {len(unique_universities)}"
)


print(
    f"University ID range: "
    f"{unique_universities[0]} -> {unique_universities[-1]}"
)


expected_universities = {
    f"uni_kr_{i:03d}"
    for i in range(1,51)
}


missing_universities = (
    expected_universities -
    set(unique_universities)
)


print(
    f"Missing university IDs: "
    f"{'PASS | 0' if len(missing_universities)==0 else missing_universities}"
)


# --------------------------------------------------
# Programme distribution
# --------------------------------------------------

print()
print("PROGRAMME DISTRIBUTION AUDIT")
print("-" * 130)

counts = Counter(university_ids)

wrong_distribution = {
    k:v for k,v in counts.items()
    if v != 3
}


print(
    f"Universities with exactly 3 programmes: "
    f"{'PASS | 50/50' if len(wrong_distribution)==0 else 'FAIL'}"
)


if wrong_distribution:
    print(wrong_distribution)


# --------------------------------------------------
# Orphan check
# --------------------------------------------------

print()
print("RELATIONSHIP AUDIT")
print("-" * 130)


orphans = [
    p["program_id"]
    for p in south_korea
    if not p.get("university_id")
]


print(
    f"Orphan programmes: "
    f"{'PASS | 0' if len(orphans)==0 else orphans}"
)


# duplicate pair

pairs = [
    (
        p.get("university_id"),
        p.get("program_id")
    )
    for p in south_korea
]


duplicates = [
    x for x,c in Counter(pairs).items()
    if c > 1
]


print(
    f"Duplicate university-program pairs: "
    f"{'PASS | 0' if len(duplicates)==0 else duplicates}"
)


print()
print("=" * 130)
print("STEP 173 SOUTH KOREA UNIVERSITY CANONICAL VERIFICATION: COMPLETE")
print("=" * 130)

print()
print("FINAL RESULT")
print("-" * 130)

print(f"Canonical programmes       : {len(programs)}")
print(f"South Korea programmes     : {len(south_korea)}")
print(f"South Korea universities   : {len(unique_universities)}")
print(f"Missing universities       : {len(missing_universities)}")
print(f"Orphan programmes          : {len(orphans)}")
print(f"Duplicate relations        : {len(duplicates)}")

