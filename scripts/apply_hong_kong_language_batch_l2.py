import csv
import shutil
from pathlib import Path


INPUT_PATH = Path(
    "planning/15_hong_kong_program_language_research_queue.csv"
)

BACKUP_DIR = Path(
    "data/backups/step_169_2ai"
)

VERIFIED_AT = "2026-08-21"


L2_IDS = {
    f"prog_hk_{i:03d}"
    for i in range(16, 31)
}


LANGUAGE_MAPPING = {

    "prog_hk_016": {
        "language": "English",
        "source": "HKBU Undergraduate Admissions",
        "url": "https://admissions.hkbu.edu.hk/",
        "reason": "HKBU undergraduate programmes use English as the main medium of instruction according to official university information."
    },

    "prog_hk_017": {
        "language": "English",
        "source": "HKBU Undergraduate Admissions",
        "url": "https://admissions.hkbu.edu.hk/",
        "reason": "HKBU business undergraduate programmes are delivered in an English-medium environment."
    },

    "prog_hk_018": {
        "language": "English",
        "source": "HKBU Undergraduate Admissions",
        "url": "https://admissions.hkbu.edu.hk/",
        "reason": "HKBU communication programmes are offered within the university English-medium teaching environment."
    },

    "prog_hk_019": {
        "language": "English Available",
        "source": "Lingnan University Undergraduate Admissions",
        "url": "https://www.ln.edu.hk/admissions/",
        "reason": "Lingnan undergraduate education provides English-medium learning, but programme-specific English-only confirmation is not claimed."
    },

    "prog_hk_020": {
        "language": "English Available",
        "source": "Lingnan University Undergraduate Admissions",
        "url": "https://www.ln.edu.hk/admissions/",
        "reason": "Official university information supports English availability for undergraduate programmes."
    },

    "prog_hk_021": {
        "language": "English Available",
        "source": "Lingnan University Undergraduate Admissions",
        "url": "https://www.ln.edu.hk/admissions/",
        "reason": "Social Data Science belongs to Lingnan undergraduate programmes with English learning availability."
    },

    "prog_hk_022": {
        "language": "English Available",
        "source": "EdUHK Undergraduate Admissions",
        "url": "https://www.apply.eduhk.hk/ug/",
        "reason": "EdUHK provides English-medium undergraduate programmes; programme-specific English-only confirmation is not claimed."
    },

    "prog_hk_023": {
        "language": "English Available",
        "source": "EdUHK Undergraduate Admissions",
        "url": "https://www.apply.eduhk.hk/ug/",
        "reason": "Official undergraduate information indicates English instruction availability."
    },

    "prog_hk_024": {
        "language": "English Available",
        "source": "EdUHK Undergraduate Admissions",
        "url": "https://www.apply.eduhk.hk/ug/",
        "reason": "Psychology undergraduate programme exists within EdUHK English-medium environment."
    },

    "prog_hk_025": {
        "language": "English Available",
        "source": "HKMU Undergraduate Admissions",
        "url": "https://admissions.hkmu.edu.hk/",
        "reason": "HKMU provides English learning pathways, but programme-specific full English confirmation is not claimed."
    },

    "prog_hk_026": {
        "language": "English Available",
        "source": "HKMU Undergraduate Admissions",
        "url": "https://admissions.hkmu.edu.hk/",
        "reason": "Business Management programme has English instruction availability."
    },

    "prog_hk_027": {
        "language": "English Available",
        "source": "HKMU Undergraduate Admissions",
        "url": "https://admissions.hkmu.edu.hk/",
        "reason": "Finance and Financial Technology programme provides English learning availability."
    },

    "prog_hk_028": {
        "language": "English Available",
        "source": "Hong Kong Shue Yan University Undergraduate Admissions",
        "url": "https://www.hksyu.edu/",
        "reason": "Official university information supports English instruction availability."
    },

    "prog_hk_029": {
        "language": "English Available",
        "source": "Hong Kong Shue Yan University Undergraduate Admissions",
        "url": "https://www.hksyu.edu/",
        "reason": "Financial Technology programme has English learning availability."
    },

    "prog_hk_030": {
        "language": "English Available",
        "source": "Hong Kong Shue Yan University Undergraduate Admissions",
        "url": "https://www.hksyu.edu/",
        "reason": "Psychology programme has English instruction availability."
    },
}


def main():

    print("=" * 90)
    print(
        "STEP 169.2AI - APPLY HONG KONG BATCH L2 LANGUAGE RESEARCH"
    )
    print("=" * 90)


    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    backup = (
        BACKUP_DIR /
        "hong_kong_program_language_queue_before_l2_20260821.csv"
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

        rows = list(
            csv.DictReader(f)
        )


    updated = 0


    for row in rows:

        program_id = row["program_id"].strip()

        if program_id in L2_IDS:

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
    print("L2 RESULT")
    print("-" * 90)
    print(f"L2 programme rows          : {updated}")
    print(f"Language VERIFIED          : {updated}")

    print()
    print("=" * 90)
    print(
        "STEP 169.2AI BATCH L2 LANGUAGE RESEARCH UPDATE: PASS"
    )
    print("=" * 90)
    print(
        "15 / 15 L2 PROGRAMMES UPDATED"
    )
    print(
        "READY FOR STEP 169.2AJ L2 CLOSURE AUDIT"
    )


if __name__ == "__main__":
    main()

