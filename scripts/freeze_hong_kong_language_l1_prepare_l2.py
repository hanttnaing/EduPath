import csv
import shutil
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


BACKUP_DIR = Path(
    "data/backups/"
    "step_169_2ah"
)


L1_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(1, 16)
}


L2_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(16, 31)
}


def clean(value):
    return str(value or "").strip()


def count_blank(rows, field):
    return sum(
        1
        for row in rows
        if not clean(row.get(field))
    )


def main():

    print("=" * 90)
    print(
        "STEP 169.2AH - HONG KONG "
        "FREEZE L1 + PREPARE L2"
    )
    print("=" * 90)


    if not QUEUE_PATH.exists():
        raise FileNotFoundError(
            f"Missing queue file: {QUEUE_PATH}"
        )


    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    backup_path = (
        BACKUP_DIR /
        "hong_kong_program_language_queue_post_l1_frozen.csv"
    )


    shutil.copy2(
        QUEUE_PATH,
        backup_path
    )


    with QUEUE_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        rows = list(
            csv.DictReader(f)
        )


    l1_rows = [
        row
        for row in rows
        if clean(row["program_id"]) in L1_IDS
    ]


    l2_rows = [
        row
        for row in rows
        if clean(row["program_id"]) in L2_IDS
    ]


    l1_verified = sum(
        1
        for row in l1_rows
        if clean(
            row["language_research_status"]
        ) == "VERIFIED"
    )


    l2_pending = sum(
        1
        for row in l2_rows
        if clean(
            row["language_research_status"]
        ) == "PENDING"
    )


    print()

    print("L1 FROZEN BASELINE")
    print("-" * 90)

    print(
        f"L1 rows                         : {len(l1_rows)}"
    )

    print(
        f"Language VERIFIED               : {l1_verified}"
    )

    print(
        f"Blank language values           : "
        f"{count_blank(l1_rows, 'language_of_instruction')}"
    )

    print(
        f"Blank source names              : "
        f"{count_blank(l1_rows, 'language_source_name')}"
    )

    print(
        f"Blank source URLs               : "
        f"{count_blank(l1_rows, 'language_source_url')}"
    )

    print(
        f"Blank reasons                   : "
        f"{count_blank(l1_rows, 'language_reason')}"
    )

    print(
        f"Blank verified dates            : "
        f"{count_blank(l1_rows, 'verified_at')}"
    )


    print()

    print("L2 READINESS")
    print("-" * 90)

    print(
        f"L2 rows                         : {len(l2_rows)}"
    )

    print(
        f"Language PENDING                : {l2_pending}"
    )

    print(
        f"Pre-filled language values      : "
        f"{sum(1 for row in l2_rows if clean(row.get('language_of_instruction')))}"
    )


    print()

    print(
        f"Frozen snapshot                 : {backup_path}"
    )


    print()

    print("=" * 90)


    if (
        len(l1_rows) == 15
        and l1_verified == 15
        and l2_pending == 15
        and count_blank(l1_rows, "language_of_instruction") == 0
        and count_blank(l1_rows, "language_source_name") == 0
        and count_blank(l1_rows, "language_source_url") == 0
        and count_blank(l1_rows, "language_reason") == 0
        and count_blank(l1_rows, "verified_at") == 0
    ):

        print(
            "STEP 169.2AH HONG KONG "
            "FREEZE L1 + PREPARE L2: PASS"
        )

        print(
            "15 / 15 L1 PROGRAMMES ARE FROZEN"
        )

        print(
            "15 / 15 L2 PROGRAMMES ARE READY"
        )

        print(
            "READY FOR STEP 169.2AI "
            "BATCH L2 LANGUAGE RESEARCH"
        )

    else:

        print(
            "STEP 169.2AH HONG KONG "
            "FREEZE L1 + PREPARE L2: FAIL"
        )


    print("=" * 90)

    print(
        "NO CSV DATA WAS MODIFIED"
    )

    print(
        "NO CLEANED DATASET OR MONGODB WAS MODIFIED"
    )


if __name__ == "__main__":
    main()

