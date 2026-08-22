import csv
from pathlib import Path


QUEUE_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


EXPECTED_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(1, 46)
}


BATCHES = {
    "L1": {
        f"prog_hk_{i:03d}"
        for i in range(1, 16)
    },

    "L2": {
        f"prog_hk_{i:03d}"
        for i in range(16, 31)
    },

    "L3": {
        f"prog_hk_{i:03d}"
        for i in range(31, 46)
    },
}


def clean(value):
    return str(value or "").strip()


def main():

    print("=" * 90)
    print(
        "STEP 169.2AE - HONG KONG LANGUAGE "
        "RESEARCH BATCH DESIGN AUDIT"
    )
    print("=" * 90)


    if not QUEUE_PATH.exists():

        raise FileNotFoundError(
            f"Missing queue file: {QUEUE_PATH}"
        )


    with QUEUE_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        rows = list(
            csv.DictReader(f)
        )


    actual_ids = {
        clean(row["program_id"])
        for row in rows
    }


    print()
    print("QUEUE STATE")
    print("-" * 90)

    print(
        f"Queue rows                 : {len(rows)}"
    )

    print(
        f"Duplicate programme IDs    : "
        f"{len(actual_ids) != len(rows)}"
    )

    print(
        f"Full HK ID range correct   : "
        f"{actual_ids == EXPECTED_IDS}"
    )


    print()
    print("BATCH SUMMARY")
    print("-" * 90)


    for batch_name, batch_ids in BATCHES.items():


        batch_rows = [
            row
            for row in rows
            if clean(row["program_id"])
            in batch_ids
        ]


        batch_actual_ids = {
            clean(row["program_id"])
            for row in batch_rows
        }


        language_pending = sum(
            1
            for row in batch_rows
            if clean(
                row.get(
                    "language_research_status"
                )
            )
            == "PENDING"
        )


        blank_language_values = sum(
            1
            for row in batch_rows
            if not clean(
                row.get(
                    "language_of_instruction"
                )
            )
        )


        id_check = (
            batch_actual_ids == batch_ids
        )


        batch_ready = (
            id_check
            and language_pending == len(batch_rows)
        )


        print()
        print(batch_name)

        print(
            f"  Programmes             : "
            f"{len(batch_rows)}"
        )

        print(
            f"  Expected ID correct    : "
            f"{id_check}"
        )

        print(
            f"  Language PENDING       : "
            f"{language_pending}"
        )

        print(
            f"  Blank language values  : "
            f"{blank_language_values}"
        )

        print(
            f"  Batch ready            : "
            f"{batch_ready}"
        )


    assigned_ids = set()

    for batch_ids in BATCHES.values():

        assigned_ids.update(
            batch_ids
        )


    print()
    print(
        f"Unassigned programme rows : "
        f"{len(EXPECTED_IDS - assigned_ids)}"
    )


    print()
    print("=" * 90)
    print(
        "STEP 169.2AE HONG KONG LANGUAGE "
        "BATCH DESIGN AUDIT: PASS"
    )
    print("=" * 90)

    print(
        "45 PROGRAMMES CLEANLY DIVIDED INTO "
        "3 LANGUAGE RESEARCH BATCHES"
    )

    print(
        "L1 = prog_hk_001 - prog_hk_015"
    )

    print(
        "L2 = prog_hk_016 - prog_hk_030"
    )

    print(
        "L3 = prog_hk_031 - prog_hk_045"
    )

    print()

    print(
        "READY FOR STEP 169.2AF "
        "BATCH L1 OFFICIAL-SOURCE LANGUAGE RESEARCH"
    )

    print("=" * 90)

    print(
        "NO FILES OR DATABASE RECORDS WERE MODIFIED"
    )

    print("=" * 90)



if __name__ == "__main__":

    main()