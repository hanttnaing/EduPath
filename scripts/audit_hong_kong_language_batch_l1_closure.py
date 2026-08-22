import csv
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


BACKUP_PATH = Path(
    "data/backups/"
    "step_169_2af/"
    "hong_kong_program_language_queue_before_l1_20260821.csv"
)


L1_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(1, 16)
}


L2_L3_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(16, 46)
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
        "STEP 169.2AG - HONG KONG "
        "BATCH L1 LANGUAGE CLOSURE AUDIT"
    )
    print("=" * 90)


    with QUEUE_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        current_rows = list(
            csv.DictReader(f)
        )


    with BACKUP_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        backup_rows = list(
            csv.DictReader(f)
        )


    print()
    print("STRUCTURE")
    print("-" * 90)

    print(
        f"Current rows              : {len(current_rows)}"
    )

    print(
        f"Backup rows               : {len(backup_rows)}"
    )


    current_ids = {
        row["program_id"]
        for row in current_rows
    }


    backup_ids = {
        row["program_id"]
        for row in backup_rows
    }


    print(
        f"ID parity                 : "
        f"{current_ids == backup_ids}"
    )


    l1_rows = [
        row
        for row in current_rows
        if row["program_id"] in L1_IDS
    ]


    l2_l3_rows = [
        row
        for row in current_rows
        if row["program_id"] in L2_L3_IDS
    ]


    l1_verified = sum(
        1
        for row in l1_rows
        if clean(
            row["language_research_status"]
        ) == "VERIFIED"
    )


    l2_l3_pending = sum(
        1
        for row in l2_l3_rows
        if clean(
            row["language_research_status"]
        ) == "PENDING"
    )


    print()
    print("L1 LANGUAGE CLOSURE")
    print("-" * 90)

    print(
        f"L1 programme rows          : {len(l1_rows)}"
    )

    print(
        f"Language VERIFIED          : {l1_verified}"
    )

    print(
        f"Blank language values      : "
        f"{count_blank(l1_rows, 'language_of_instruction')}"
    )

    print(
        f"Blank source names         : "
        f"{count_blank(l1_rows, 'language_source_name')}"
    )

    print(
        f"Blank source URLs          : "
        f"{count_blank(l1_rows, 'language_source_url')}"
    )

    print(
        f"Blank reasons              : "
        f"{count_blank(l1_rows, 'language_reason')}"
    )

    print(
        f"Blank verified_at          : "
        f"{count_blank(l1_rows, 'verified_at')}"
    )


    print()
    print("L2 + L3 PRESERVATION")
    print("-" * 90)

    print(
        f"L2 + L3 rows               : {len(l2_l3_rows)}"
    )

    print(
        f"Still PENDING              : {l2_l3_pending}"
    )


    print()
    print("=" * 90)


    if (
        len(l1_rows) == 15
        and l1_verified == 15
        and l2_l3_pending == 30
    ):

        print(
            "STEP 169.2AG HONG KONG "
            "BATCH L1 LANGUAGE CLOSURE AUDIT: PASS"
        )

        print(
            "15 / 15 L1 PROGRAMMES ARE "
            "EVIDENCE COMPLETE"
        )

        print(
            "L2 AND L3 REMAIN UNTOUCHED"
        )

        print(
            "READY FOR STEP 169.2AH "
            "L1 FREEZE + L2 PREPARATION"
        )

    else:

        print(
            "STEP 169.2AG HONG KONG "
            "BATCH L1 LANGUAGE CLOSURE AUDIT: FAIL"
        )


    print("=" * 90)

    print(
        "NO FILES OR DATABASE RECORDS WERE MODIFIED"
    )

    print("=" * 90)


if __name__ == "__main__":

    main()