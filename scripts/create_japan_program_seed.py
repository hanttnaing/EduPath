import csv
from pathlib import Path


OUTPUT_PATH = Path(
    "data/raw/japan_program_seed.csv"
)


PROGRAMS = [
    # -------------------------------------------------
    # The University of Tokyo
    # -------------------------------------------------
    (
        "uni_jp_001",
        "The University of Tokyo",
        1,
        "Computer Science",
        "Master",
        "https://www.i.u-tokyo.ac.jp/index_e.shtml",
    ),
    (
        "uni_jp_001",
        "The University of Tokyo",
        2,
        "Mathematical Informatics",
        "Master",
        "https://www.i.u-tokyo.ac.jp/index_e.shtml",
    ),
    (
        "uni_jp_001",
        "The University of Tokyo",
        3,
        "Information Physics & Computing",
        "Master",
        "https://www.i.u-tokyo.ac.jp/index_e.shtml",
    ),

    # -------------------------------------------------
    # Kyoto University
    # -------------------------------------------------
    (
        "uni_jp_002",
        "Kyoto University",
        1,
        "Intelligence Science and Technology",
        "Master",
        "https://www.i.kyoto-u.ac.jp/en/course/",
    ),
    (
        "uni_jp_002",
        "Kyoto University",
        2,
        "Communications and Computer Engineering",
        "Master",
        "https://www.i.kyoto-u.ac.jp/en/course/",
    ),
    (
        "uni_jp_002",
        "Kyoto University",
        3,
        "Data Science",
        "Master",
        "https://www.i.kyoto-u.ac.jp/en/course/",
    ),

    # -------------------------------------------------
    # Osaka University
    # -------------------------------------------------
    (
        "uni_jp_003",
        "Osaka University",
        1,
        "Computer Science",
        "Master",
        "https://www.ist.osaka-u.ac.jp/english/",
    ),
    (
        "uni_jp_003",
        "Osaka University",
        2,
        "Information Networking",
        "Master",
        "https://www.ist.osaka-u.ac.jp/english/majors/nw.php",
    ),
    (
        "uni_jp_003",
        "Osaka University",
        3,
        "Multimedia Engineering",
        "Master",
        "https://www.ist.osaka-u.ac.jp/english/majors/mm.php",
    ),

    # -------------------------------------------------
    # Tohoku University
    # -------------------------------------------------
    (
        "uni_jp_004",
        "Tohoku University",
        1,
        "Computer and Mathematical Sciences",
        "Master",
        "https://www.is.tohoku.ac.jp/en/",
    ),
    (
        "uni_jp_004",
        "Tohoku University",
        2,
        "System Information Sciences",
        "Master",
        "https://www.is.tohoku.ac.jp/en/",
    ),
    (
        "uni_jp_004",
        "Tohoku University",
        3,
        "Applied Information Sciences",
        "Master",
        "https://www.is.tohoku.ac.jp/en/",
    ),

    # -------------------------------------------------
    # Nagoya University
    # -------------------------------------------------
    (
        "uni_jp_005",
        "Nagoya University",
        1,
        "Mathematical Informatics",
        "Master",
        "https://www.i.nagoya-u.ac.jp/en/graduate-school-of-informatics/",
    ),
    (
        "uni_jp_005",
        "Nagoya University",
        2,
        "Computing and Software Systems",
        "Master",
        "https://www.i.nagoya-u.ac.jp/en/graduate-school-of-informatics/",
    ),
    (
        "uni_jp_005",
        "Nagoya University",
        3,
        "Intelligent Systems",
        "Master",
        "https://www.i.nagoya-u.ac.jp/en/graduate-school-of-informatics/",
    ),

    # -------------------------------------------------
    # Kyushu University
    # -------------------------------------------------
    (
        "uni_jp_006",
        "Kyushu University",
        1,
        "International Master's/Doctoral Program in Information Science and Technology",
        "Master",
        "https://www.isc.kyushu-u.ac.jp/graduate/",
    ),
    (
        "uni_jp_006",
        "Kyushu University",
        2,
        "International Master's/Doctoral Program in Electrical and Electronic Engineering",
        "Master",
        "https://www.isc.kyushu-u.ac.jp/graduate/",
    ),
    (
        "uni_jp_006",
        "Kyushu University",
        3,
        "Master's Program in the Department of Design (Acoustic Design Course)",
        "Master",
        "https://www.isc.kyushu-u.ac.jp/graduate/",
    ),

    # -------------------------------------------------
    # Hokkaido University
    # -------------------------------------------------
    (
        "uni_jp_007",
        "Hokkaido University",
        1,
        "Computer Science and Information Technology",
        "Master",
        "https://www.ist.hokudai.ac.jp/eng/divisions/",
    ),
    (
        "uni_jp_007",
        "Hokkaido University",
        2,
        "Media and Network Technologies",
        "Master",
        "https://www.ist.hokudai.ac.jp/eng/divisions/",
    ),
    (
        "uni_jp_007",
        "Hokkaido University",
        3,
        "Systems Science and Informatics",
        "Master",
        "https://www.ist.hokudai.ac.jp/eng/divisions/",
    ),

    # -------------------------------------------------
    # Institute of Science Tokyo
    # -------------------------------------------------
    (
        "uni_jp_008",
        "Institute of Science Tokyo",
        1,
        "Graduate major in Computer Science",
        "Master",
        "https://www.isct.ac.jp/en/001/about/organizations/school-of-computing",
    ),
    (
        "uni_jp_008",
        "Institute of Science Tokyo",
        2,
        "Graduate major in Mathematical and Computing Science",
        "Master",
        "https://www.isct.ac.jp/en/001/about/organizations/school-of-computing",
    ),
    (
        "uni_jp_008",
        "Institute of Science Tokyo",
        3,
        "Graduate major in Artificial Intelligence",
        "Master",
        "https://www.isct.ac.jp/en/001/about/organizations/school-of-computing",
    ),

    # -------------------------------------------------
    # University of Tsukuba
    # -------------------------------------------------
    (
        "uni_jp_009",
        "University of Tsukuba",
        1,
        "Computer Science",
        "Master",
        "https://www.sie.tsukuba.ac.jp/eng/edu/course/cs/",
    ),
    (
        "uni_jp_009",
        "University of Tsukuba",
        2,
        "Intelligent and Mechanical Interaction Systems",
        "Master",
        "https://www.sie.tsukuba.ac.jp/eng/",
    ),
    (
        "uni_jp_009",
        "University of Tsukuba",
        3,
        "Empowerment Informatics",
        "PhD",
        "https://www.emp.tsukuba.ac.jp/english",
    ),

    # -------------------------------------------------
    # Kobe University
    # -------------------------------------------------
    (
        "uni_jp_010",
        "Kobe University",
        1,
        "Computer Science and Systems Engineering",
        "Bachelor",
        "https://www.csi.kobe-u.ac.jp/english/",
    ),
    (
        "uni_jp_010",
        "Kobe University",
        2,
        "System Informatics",
        "Master",
        "https://www.csi.kobe-u.ac.jp/english/",
    ),
    (
        "uni_jp_010",
        "Kobe University",
        3,
        "System Informatics",
        "PhD",
        "https://www.csi.kobe-u.ac.jp/english/",
    ),

    # -------------------------------------------------
    # Waseda University
    # -------------------------------------------------
    (
        "uni_jp_011",
        "Waseda University",
        1,
        "Pure and Applied Mathematics",
        "Master",
        "https://www.waseda.jp/fsci/en/about/departments",
    ),
    (
        "uni_jp_011",
        "Waseda University",
        2,
        "Computer Science and Communications Engineering",
        "Master",
        "https://www.waseda.jp/fsci/en/about/departments",
    ),
    (
        "uni_jp_011",
        "Waseda University",
        3,
        "Intermedia Studies",
        "Master",
        "https://www.waseda.jp/fsci/en/about/departments",
    ),

    # -------------------------------------------------
    # Keio University
    # -------------------------------------------------
    (
        "uni_jp_012",
        "Keio University",
        1,
        "International Graduate Program",
        "Master",
        "https://www.keio.ac.jp/en/st/admissions-en/masters_program/",
    ),
    (
        "uni_jp_012",
        "Keio University",
        2,
        "International Graduate Program",
        "PhD",
        "https://www.keio.ac.jp/en/st/admissions-en/phd_program/",
    ),
    (
        "uni_jp_012",
        "Keio University",
        3,
        "Double Degree Program",
        "Master",
        "https://www.keio.ac.jp/en/st/admissions-en/dd/",
    ),
]


def main() -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []

    for (
        university_id,
        university_name,
        program_slot,
        program_name,
        degree_level_hint,
        source_url,
    ) in PROGRAMS:

        rows.append(
            {
                "university_id": university_id,
                "university_name": university_name,
                "country_id": "country_jp",
                "program_slot": program_slot,
                "program_name": program_name,
                "degree_level_hint": degree_level_hint,
                "official_source_url": source_url,
                "collection_status": (
                    "Program Identity Collected"
                ),
                "verification_status": (
                    "Official Source Identified"
                ),
            }
        )

    fieldnames = [
        "university_id",
        "university_name",
        "country_id",
        "program_slot",
        "program_name",
        "degree_level_hint",
        "official_source_url",
        "collection_status",
        "verification_status",
    ]

    with OUTPUT_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    unique_universities = {
        row["university_id"]
        for row in rows
    }

    print(
        "=== Japan Program Seed Created ==="
    )
    print(
        f"Universities: "
        f"{len(unique_universities)}"
    )
    print(
        f"Program identities: "
        f"{len(rows)}"
    )
    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()