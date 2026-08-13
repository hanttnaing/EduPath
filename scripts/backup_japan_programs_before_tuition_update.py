from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


API_BASE_URL = "http://127.0.0.1:8000"

JAPAN_COUNTRY_ID = "country_jp"

PAGE_SIZE = 100


def get_json(
    path: str,
    params: dict | None = None,
) -> dict:
    url = f"{API_BASE_URL}{path}"

    if params:
        url = f"{url}?{urlencode(params)}"

    with urlopen(
        url,
        timeout=20,
    ) as response:
        return json.load(response)


def fetch_all(
    path: str,
    params: dict | None = None,
) -> list[dict]:
    items: list[dict] = []

    skip = 0

    while True:
        request_params = dict(params or {})

        request_params["skip"] = skip
        request_params["limit"] = PAGE_SIZE

        data = get_json(
            path,
            request_params,
        )

        batch = data.get(
            "items",
            [],
        )

        items.extend(batch)

        total = data.get(
            "total",
            len(items),
        )

        if (
            not batch
            or len(items) >= total
        ):
            break

        skip += PAGE_SIZE

    return items


def main() -> None:
    print("=" * 80)
    print(
        "EduPath - Backup Japan Programs "
        "Before Tuition Update"
    )
    print("=" * 80)

    # ---------------------------------------
    # Load Japan universities
    # ---------------------------------------

    japan_universities = fetch_all(
        "/api/universities",
        {
            "country_id":
                JAPAN_COUNTRY_ID
        },
    )

    japan_university_ids = {
        university.get(
            "university_id"
        )
        for university
        in japan_universities
    }

    # ---------------------------------------
    # Load all programs
    # ---------------------------------------

    all_programs = fetch_all(
        "/api/programs"
    )

    japan_programs = [
        program
        for program in all_programs
        if program.get(
            "university_id"
        )
        in japan_university_ids
    ]

    # ---------------------------------------
    # Safety checks
    # ---------------------------------------

    print()
    print(
        "Japan universities found:",
        len(japan_universities),
    )

    print(
        "Japan programs found:",
        len(japan_programs),
    )

    if not japan_programs:
        raise RuntimeError(
            "No Japan programs found. "
            "Backup cancelled."
        )

    # ---------------------------------------
    # Backup folder
    # ---------------------------------------

    project_root = Path(
        __file__
    ).resolve().parent.parent

    backup_folder = (
        project_root
        / "planning"
        / "backups"
    )

    backup_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    backup_file = (
        backup_folder
        / "japan_programs_before_tuition_context_update.json"
    )

    # ---------------------------------------
    # Backup content
    # ---------------------------------------

    backup_data = {
        "backup_type":
            "Japan programs before tuition context update",

        "created_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "country_id":
            JAPAN_COUNTRY_ID,

        "university_count":
            len(japan_universities),

        "program_count":
            len(japan_programs),

        "programs":
            japan_programs,
    }

    with backup_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            backup_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # ---------------------------------------
    # Final check
    # ---------------------------------------

    print()
    print(
        "Backup created successfully."
    )

    print(
        "Programs backed up:",
        len(japan_programs),
    )

    print(
        "Backup file:"
    )

    print(
        backup_file
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "No database records were modified."
    )

    print("=" * 80)


if __name__ == "__main__":
    main()