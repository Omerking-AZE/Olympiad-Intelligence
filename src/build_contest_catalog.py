from pathlib import Path
import re

import pandas as pd
from datasets import load_dataset


# ============================================================
# CONFIG
# ============================================================

OUTPUT_PATH = Path(
    "data/metadata/external_problem_catalog.csv"
)

DATASET_NAME = "kylemontgomery/imo"


# ============================================================
# PARSE IMO ID
# ============================================================

def parse_imo_id(value):
    """
    IMO-2023-2 ->

        year = 2023
        problem_number = 2
    """

    match = re.fullmatch(
        r"IMO-(\d{4})-(\d+)",
        str(value).strip()
    )

    if not match:
        return None, None

    return (
        int(match.group(1)),
        int(match.group(2)),
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "IMO CONTEST CATALOG"
    )
    print("=" * 70)

    print(
        f"\nLoading: {DATASET_NAME}"
    )

    dataset = load_dataset(
        DATASET_NAME,
        split="train",
    )

    print(
        f"Loaded {len(dataset)} rows."
    )

    df = dataset.to_pandas()

    print(
        "\nAvailable columns:"
    )

    print(
        df.columns.tolist()
    )

    records = []

    for _, row in df.iterrows():

        source_id = row.get(
            "id"
        )

        year, problem_number = (
            parse_imo_id(
                source_id
            )
        )

        if year is None:
            continue

        problem_text = row.get(
            "problem"
        )

        source_url = row.get(
            "source"
        )

        if pd.isna(
            problem_text
        ):
            problem_text = ""

        if pd.isna(
            source_url
        ):
            source_url = ""

        records.append({
            "competition":
                "IMO",

            "year":
                year,

            "problem_number":
                problem_number,

            "title":
                f"IMO {year} "
                f"P{problem_number}",

            "problem_id_external":
                source_id,

            "problem_text":
                str(
                    problem_text
                ),

            "source":
                "AoPS",

            "source_url":
                str(
                    source_url
                ),
        })

    result = pd.DataFrame(
        records
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "CATALOG COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nRows: {len(result)}"
    )

    print(
        f"Saved: {OUTPUT_PATH}"
    )

    print(
        "\n2023 IMO:"
    )

    print(
        result[
            result["year"] == 2023
        ][
            [
                "title",
                "problem_id_external",
                "source_url",
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()