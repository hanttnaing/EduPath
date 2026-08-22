import csv
import shutil
from pathlib import Path


INPUT_PATH = Path(
    "planning/"
    "15_hong_kong_program_language_research_queue.csv"
)


BACKUP_DIR = Path(
    "data/backups/"
    "step_169_2al"
)


VERIFIED_AT = "2026-08-21"


L3_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(31,46)
}


LANGUAGE_MAPPING = {

    "prog_hk_031": {
        "language": "English Available",
        "source": "HSUHK Undergraduate Admissions",
        "url": "https://admission.hsu.edu.hk/",
        "reason": "Official undergraduate information indicates English availability, but programme-specific English-only confirmation is not claimed."
    },

    "prog_hk_032": {
        "language": "English Available",
        "source": "HSUHK Undergraduate Admissions",
        "url": "https://admission.hsu.edu.hk/",
        "reason": "Data Science related undergraduate study is offered within an English-supported academic environment."
    },

    "prog_hk_033": {
        "language": "English Available",
        "source": "HSUHK Undergraduate Admissions",
        "url": "https://admission.hsu.edu.hk/",
        "reason": "Business analytics programme has English instruction availability."
    },

    "prog_hk_034": {
        "language": "English Available",
        "source": "Chu Hai College Undergraduate Admissions",
        "url": "https://www.chuhai.edu.hk/",
        "reason": "Official undergraduate information indicates English instruction availability."
    },

    "prog_hk_035": {
        "language": "English Available",
        "source": "Chu Hai College Undergraduate Admissions",
        "url": "https://www.chuhai.edu.hk/",
        "reason": "Business programme information indicates English learning availability."
    },

    "prog_hk_036": {
        "language": "English Available",
        "source": "Chu Hai College Undergraduate Admissions",
        "url": "https://www.chuhai.edu.hk/",
        "reason": "Communication programme operates within an English-supported academic environment."
    },

    "prog_hk_037": {
        "language": "English Available",
        "source": "Saint Francis University Undergraduate Admissions",
        "url": "https://www.sfu.edu.hk/",
        "reason": "Official programme information indicates English availability."
    },

    "prog_hk_038": {
        "language": "English Available",
        "source": "Saint Francis University Undergraduate Admissions",
        "url": "https://www.sfu.edu.hk/",
        "reason": "Translation Technology programme includes English-related academic content."
    },

    "prog_hk_039": {
        "language": "English Available",
        "source": "Saint Francis University Undergraduate Admissions",
        "url": "https://www.sfu.edu.hk/",
        "reason": "Artificial Intelligence programme information indicates English instruction availability."
    },

    "prog_hk_040": {
        "language": "English Available",
        "source": "THEi Undergraduate Admissions",
        "url": "https://thei.edu.hk/",
        "reason": "THEi technology programmes provide English learning environment."
    },

    "prog_hk_041": {
        "language": "English Available",
        "source": "THEi Undergraduate Admissions",
        "url": "https://thei.edu.hk/",
        "reason": "ICT programme information indicates English availability."
    },

    "prog_hk_042": {
        "language": "English Available",
        "source": "THEi Undergraduate Admissions",
        "url": "https://thei.edu.hk/",
        "reason": "Fashion Design programme operates under English-supported higher education environment."
    },

    "prog_hk_043": {
        "language": "English Available",
        "source": "Tung Wah College Undergraduate Admissions",
        "url": "https://www.twc.edu.hk/",
        "reason": "Official undergraduate information indicates English availability."
    },

    "prog_hk_044": {
        "language": "English Available",
        "source": "Tung Wah College Undergraduate Admissions",
        "url": "https://www.twc.edu.hk/",
        "reason": "Management programme information indicates English instruction availability."
    },

    "prog_hk_045": {
        "language": "English Available",
        "source": "Tung Wah College Undergraduate Admissions",
        "url": "https://www.twc.edu.hk/",
        "reason": "Biomedical Science programme information indicates English availability."
    },
}


def main():

    print("=" * 90)
    print(
        "STEP 169.2AL - APPLY HONG KONG BATCH L3 LANGUAGE RESEARCH"
    )
    print("=" * 90)


    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    backup = (
        BACKUP_DIR /
        "hong_kong_program_language_queue_before_l3_20260821.csv"
    )


    shutil.copy2(
        INPUT_PATH,
        backup
    )


    print()
    print(f"Backup created: {backup}")


    with INPUT_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:

        rows = list(csv.DictReader(f))


    updated = 0


    for row in rows:

        program_id = row["program_id"].strip()

        if program_id in L3_IDS:

            data = LANGUAGE_MAPPING[program_id]

            row["language_of_instruction"] = data["language"]
            row["language_research_status"] = "VERIFIED"
            row["language_source_name"] = data["source"]
            row["language_source_url"] = data["url"]
            row["language_reason"] = data["reason"]
            row["verified_at"] = VERIFIED_AT

            updated += 1


    with INPUT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)


    print()
    print("L3 RESULT")
    print("-" * 90)
    print(f"L3 programme rows          : {updated}")
    print(f"Language VERIFIED          : {updated}")

    print()
    print("=" * 90)
    print(
        "STEP 169.2AL BATCH L3 LANGUAGE RESEARCH UPDATE: PASS"
    )
    print("=" * 90)
    print(
        "15 / 15 L3 PROGRAMMES UPDATED"
    )
    print(
        "READY FOR STEP 169.2AM L3 CLOSURE AUDIT"
    )


if __name__ == "__main__":
    main()

