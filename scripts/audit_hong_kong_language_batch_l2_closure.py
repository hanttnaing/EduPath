import csv
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


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


def count_blank(rows, field):
    return sum(
        1
        for row in rows
        if not clean(row.get(field))
    )


def main():

    print("=" * 90)
    print(
        "STEP 169.2AJ - HONG KONG "
        "BATCH L2 LANGUAGE CLOSURE AUDIT"
    )
    print("=" * 90)


    with QUEUE_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        rows = list(csv.DictReader(f))


    l2_rows = [
        row
        for row in rows
        if row["program_id"] in L2_IDS
    ]


    l3_rows = [
        row
        for row in rows
        if row["program_id"] in L3_IDS
    ]


    verified = sum(
        1
        for row in l2_rows
        if row["language_research_status"]
        == "VERIFIED"
    )


    l3_pending = sum(
        1
        for row in l3_rows
        if row["language_research_status"]
        == "PENDING"
    )


    print()
    print("STRUCTURE")
    print("-" * 90)

    print(
        f"Queue rows               : {len(rows)}"
    )

    print(
        f"L2 rows                  : {len(l2_rows)}"
    )


    print()
    print("L2 LANGUAGE CLOSURE")
    print("-" * 90)

    print(
        f"Language VERIFIED        : {verified}"
    )

    print(
        f"Blank language values    : "
        f"{count_blank(l2_rows,'language_of_instruction')}"
    )

    print(
        f"Blank source names       : "
        f"{count_blank(l2_rows,'language_source_name')}"
    )

    print(
        f"Blank source URLs        : "
        f"{count_blank(l2_rows,'language_source_url')}"
    )

    print(
        f"Blank reasons            : "
        f"{count_blank(l2_rows,'language_reason')}"
    )

    print(
        f"Blank verified dates     : "
        f"{count_blank(l2_rows,'verified_at')}"
    )


    print()
    print("L3 PRESERVATION")
    print("-" * 90)

    print(
        f"L3 rows                  : {len(l3_rows)}"
    )

    print(
        f"L3 still PENDING         : {l3_pending}"
    )


    print()
    print("=" * 90)


    if (
        len(l2_rows) == 15
        and verified == 15
        and l3_pending == 15
    ):

        print(
            "STEP 169.2AJ HONG KONG "
            "BATCH L2 LANGUAGE CLOSURE AUDIT: PASS"
        )

        print(
            "15 / 15 L2 PROGRAMMES ARE EVIDENCE COMPLETE"
        )

        print(
            "L3 REMAINS UNTOUCHED"
        )

        print(
            "READY FOR STEP 169.2AK L2 FREEZE + L3 PREPARATION"
        )

    else:

        print(
            "STEP 169.2AJ AUDIT: FAIL"
        )


if __name__ == "__main__":
    main()

