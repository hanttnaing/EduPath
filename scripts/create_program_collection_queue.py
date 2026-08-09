import csv
from pathlib import Path


INPUT_PATH = Path(
    "data/cleaned/universities_master_ready.csv"
)

OUTPUT_PATH = Path(
    "data/raw/program_collection_queue.csv"
)

PROGRAMS_PER_UNIVERSITY = 3


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        universities = list(reader)

    queue_rows = []

    for university in universities:
        for slot in range(
            1,
            PROGRAMS_PER_UNIVERSITY + 1,
        ):
            queue_rows.append(
                {
                    "university_id": university[
                        "university_id"
                    ],
                    "university_name": university[
                        "university_name"
                    ],
                    "country_id": university[
                        "country_id"
                    ],
                    "official_website": university[
                        "official_website"
                    ],
                    "program_slot": slot,
                    "program_name": "",
                    "program_url": "",
                    "collection_status": (
                        "Pending Collection"
                    ),
                    "verification_status": (
                        "Not Verified"
                    ),
                }
            )

    fieldnames = [
        "university_id",
        "university_name",
        "country_id",
        "official_website",
        "program_slot",
        "program_name",
        "program_url",
        "collection_status",
        "verification_status",
    ]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(queue_rows)

    print(
        "=== Program Collection Queue Created ==="
    )
    print(
        f"Universities: {len(universities)}"
    )
    print(
        f"Programs per university: "
        f"{PROGRAMS_PER_UNIVERSITY}"
    )
    print(
        f"Target program records: "
        f"{len(queue_rows)}"
    )
    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()