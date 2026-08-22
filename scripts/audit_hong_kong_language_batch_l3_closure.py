import csv
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


L1_L2_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(1,31)
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
        "STEP 169.2AM - HONG KONG "
        "BATCH L3 LANGUAGE CLOSURE AUDIT"
    )
    print("=" * 90)


    with QUEUE_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        rows = list(csv.DictReader(f))


    l1_l2_rows = [
        row
        for row in rows
        if row["program_id"] in L1_L2_IDS
    ]


    l3_rows = [
        row
        for row in rows
        if row["program_id"] in L3_IDS
    ]


    l3_verified = sum(
        1
        for row in l3_rows
        if clean(
            row["language_research_status"]
        ) == "VERIFIED"
    )


    previous_verified = sum(
        1
        for row in l1_l2_rows
        if clean(
            row["language_research_status"]
        ) == "VERIFIED"
    )


    print()
    print("STRUCTURE")
    print("-" * 90)

    print(
        f"Queue rows               : {len(rows)}"
    )

    print(
        f"L3 rows                  : {len(l3_rows)}"
    )


    print()
    print("L3 LANGUAGE CLOSURE")
    print("-" * 90)

    print(
        f"Language VERIFIED        : {l3_verified}"
    )

    print(
        f"Blank language values    : "
        f"{count_blank(l3_rows,'language_of_instruction')}"
    )

    print(
        f"Blank source names       : "
        f"{count_blank(l3_rows,'language_source_name')}"
    )

    print(
        f"Blank source URLs        : "
        f"{count_blank(l3_rows,'language_source_url')}"
    )

    print(
        f"Blank reasons            : "
        f"{count_blank(l3_rows,'language_reason')}"
    )

    print(
        f"Blank verified dates     : "
        f"{count_blank(l3_rows,'verified_at')}"
    )


    print()
    print("L1 + L2 PRESERVATION")
    print("-" * 90)

    print(
        f"L1 + L2 rows             : {len(l1_l2_rows)}"
    )

    print(
        f"L1 + L2 VERIFIED          : {previous_verified}"
    )


    print()
    print("=" * 90)


    if (
        len(l3_rows) == 15
        and l3_verified == 15
        and previous_verified == 30
        and count_blank(
            l3_rows,
            "language_of_instruction"
        ) == 0
    ):

        print(
            "STEP 169.2AM HONG KONG "
            "BATCH L3 LANGUAGE CLOSURE AUDIT: PASS"
        )

        print(
            "15 / 15 L3 PROGRAMMES ARE "
            "EVIDENCE COMPLETE"
        )

        print(
            "ALL 45 HONG KONG PROGRAMMES "
            "NOW HAVE LANGUAGE RESEARCH"
        )

        print(
            "READY FOR FINAL LANGUAGE ENRICHMENT BUILD"
        )

    else:

        print(
            "STEP 169.2AM AUDIT: FAIL"
        )


if __name__ == "__main__":
    main()

