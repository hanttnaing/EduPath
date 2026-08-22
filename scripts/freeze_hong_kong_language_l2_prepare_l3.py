import csv
import shutil
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


BACKUP_DIR = Path(
    "data/backups/"
    "step_169_2ak"
)


L1_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(1,16)
}


L2_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(16,31)
}


L3_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(31,46)
}


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 90)
    print(
        "STEP 169.2AK - HONG KONG FREEZE L2 + PREPARE L3"
    )
    print("=" * 90)


    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    snapshot = (
        BACKUP_DIR /
        "hong_kong_program_language_queue_post_l2_frozen.csv"
    )


    shutil.copy2(
        QUEUE_PATH,
        snapshot
    )


    with QUEUE_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        rows = list(csv.DictReader(f))


    l1_l2_rows = [
        row
        for row in rows
        if (
            row["program_id"] in L1_IDS
            or row["program_id"] in L2_IDS
        )
    ]


    l3_rows = [
        row
        for row in rows
        if row["program_id"] in L3_IDS
    ]


    l1_l2_verified = sum(
        1
        for row in l1_l2_rows
        if clean(
            row["language_research_status"]
        ) == "VERIFIED"
    )


    l3_pending = sum(
        1
        for row in l3_rows
        if clean(
            row["language_research_status"]
        ) == "PENDING"
    )


    l3_prefilled = sum(
        1
        for row in l3_rows
        if clean(
            row["language_of_instruction"]
        )
    )


    print()
    print("FROZEN L1 + L2 BASELINE")
    print("-" * 90)

    print(
        f"L1 + L2 rows               : {len(l1_l2_rows)}"
    )

    print(
        f"Language VERIFIED          : {l1_l2_verified}"
    )


    print()
    print("L3 READINESS")
    print("-" * 90)

    print(
        f"L3 rows                    : {len(l3_rows)}"
    )

    print(
        f"L3 language PENDING        : {l3_pending}"
    )

    print(
        f"L3 pre-filled values       : {l3_prefilled}"
    )


    print()
    print(
        f"Frozen snapshot             : {snapshot}"
    )


    print()
    print("=" * 90)


    if (
        len(l1_l2_rows) == 30
        and l1_l2_verified == 30
        and len(l3_rows) == 15
        and l3_pending == 15
        and l3_prefilled == 0
    ):

        print(
            "STEP 169.2AK HONG KONG FREEZE L2 + PREPARE L3: PASS"
        )

        print(
            "30 / 30 L1 + L2 PROGRAMMES ARE FROZEN"
        )

        print(
            "15 / 15 L3 PROGRAMMES ARE READY"
        )

        print(
            "READY FOR STEP 169.2AL BATCH L3 LANGUAGE RESEARCH"
        )

    else:

        print(
            "STEP 169.2AK: FAIL"
        )


if __name__ == "__main__":
    main()

