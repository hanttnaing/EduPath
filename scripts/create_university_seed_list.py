import csv
from pathlib import Path


OUTPUT_PATH = Path(
    "data/cleaned/university_seed_list.csv"
)


UNIVERSITIES = [
    # Japan - 12
    ("country_jp", "Japan", "The University of Tokyo"),
    ("country_jp", "Japan", "Kyoto University"),
    ("country_jp", "Japan", "Osaka University"),
    ("country_jp", "Japan", "Tohoku University"),
    ("country_jp", "Japan", "Nagoya University"),
    ("country_jp", "Japan", "Kyushu University"),
    ("country_jp", "Japan", "Hokkaido University"),
    ("country_jp", "Japan", "Institute of Science Tokyo"),
    ("country_jp", "Japan", "University of Tsukuba"),
    ("country_jp", "Japan", "Kobe University"),
    ("country_jp", "Japan", "Waseda University"),
    ("country_jp", "Japan", "Keio University"),

    # Singapore - 6
    ("country_sg", "Singapore", "National University of Singapore"),
    ("country_sg", "Singapore", "Nanyang Technological University"),
    ("country_sg", "Singapore", "Singapore Management University"),
    (
        "country_sg",
        "Singapore",
        "Singapore University of Technology and Design",
    ),
    ("country_sg", "Singapore", "Singapore Institute of Technology"),
    (
        "country_sg",
        "Singapore",
        "Singapore University of Social Sciences",
    ),

    # Malaysia - 9
    ("country_my", "Malaysia", "Universiti Malaya"),
    ("country_my", "Malaysia", "Universiti Kebangsaan Malaysia"),
    ("country_my", "Malaysia", "Universiti Putra Malaysia"),
    ("country_my", "Malaysia", "Universiti Sains Malaysia"),
    ("country_my", "Malaysia", "Universiti Teknologi Malaysia"),
    (
        "country_my",
        "Malaysia",
        "International Islamic University Malaysia",
    ),
    (
        "country_my",
        "Malaysia",
        "Universiti Teknologi PETRONAS",
    ),
    ("country_my", "Malaysia", "Taylor's University"),
    ("country_my", "Malaysia", "Sunway University"),

    # South Korea - 8
    (
        "country_kr",
        "South Korea",
        "Seoul National University",
    ),
    (
        "country_kr",
        "South Korea",
        "Korea Advanced Institute of Science and Technology",
    ),
    ("country_kr", "South Korea", "Yonsei University"),
    ("country_kr", "South Korea", "Korea University"),
    (
        "country_kr",
        "South Korea",
        "Sungkyunkwan University",
    ),
    (
        "country_kr",
        "South Korea",
        "Pohang University of Science and Technology",
    ),
    ("country_kr", "South Korea", "Hanyang University"),
    ("country_kr", "South Korea", "Kyung Hee University"),

    # Taiwan - 5
    ("country_tw", "Taiwan", "National Taiwan University"),
    (
        "country_tw",
        "Taiwan",
        "National Tsing Hua University",
    ),
    (
        "country_tw",
        "Taiwan",
        "National Yang Ming Chiao Tung University",
    ),
    (
        "country_tw",
        "Taiwan",
        "National Cheng Kung University",
    ),
    (
        "country_tw",
        "Taiwan",
        "National Taiwan University of Science and Technology",
    ),

    # Hong Kong - 5
    (
        "country_hk",
        "Hong Kong",
        "The University of Hong Kong",
    ),
    (
        "country_hk",
        "Hong Kong",
        "The Chinese University of Hong Kong",
    ),
    (
        "country_hk",
        "Hong Kong",
        "The Hong Kong University of Science and Technology",
    ),
    (
        "country_hk",
        "Hong Kong",
        "The Hong Kong Polytechnic University",
    ),
    (
        "country_hk",
        "Hong Kong",
        "City University of Hong Kong",
    ),

    # Thailand - 5
    ("country_th", "Thailand", "Chulalongkorn University"),
    ("country_th", "Thailand", "Mahidol University"),
    ("country_th", "Thailand", "Chiang Mai University"),
    ("country_th", "Thailand", "Thammasat University"),
    ("country_th", "Thailand", "Kasetsart University"),
]


SOURCE_INFO = {
    "country_jp": (
        "Study in Japan Official Website",
        "https://www.studyinjapan.go.jp/en/search-for-schools/school_search.php",
    ),
    "country_sg": (
        "Singapore Ministry of Education",
        "https://www.moe.gov.sg/post-secondary/overview/autonomous-universities",
    ),
    "country_my": (
        "Education Malaysia",
        "https://educationmalaysia.gov.my/",
    ),
    "country_kr": (
        "Study in Korea",
        "https://www.studyinkorea.go.kr/",
    ),
    "country_tw": (
        "Study in Taiwan",
        "https://www.studyintaiwan.org/how-to-apply/school",
    ),
    "country_hk": (
        "Hong Kong University Grants Committee",
        "https://www.ugc.edu.hk/eng/ugc/site/fund_inst.html",
    ),
    "country_th": (
        "Thailand MHESI / OPS",
        "https://www.ops.go.th/",
    ),
}


def main() -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []

    counters = {}

    for country_id, country_name, university_name in UNIVERSITIES:
        counters[country_id] = counters.get(
            country_id,
            0,
        ) + 1

        source_name, source_url = SOURCE_INFO[
            country_id
        ]

        rows.append(
            {
                "country_id": country_id,
                "country_name": country_name,
                "university_name": university_name,
                "national_source_name": source_name,
                "national_source_url": source_url,
                "selection_status": "Seed Selected",
                "verification_status": (
                    "Official Verification Pending"
                ),
            }
        )

    fieldnames = [
        "country_id",
        "country_name",
        "university_name",
        "national_source_name",
        "national_source_url",
        "selection_status",
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

    print("=== University Seed List Created ===")

    for country_id, count in counters.items():
        print(
            f"{country_id}: {count}"
        )

    print(f"Total: {len(rows)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()