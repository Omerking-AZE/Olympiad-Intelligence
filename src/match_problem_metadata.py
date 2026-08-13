from pathlib import Path
import re
import pandas as pd


PROBLEMS_PATH = Path(
    "data/processed/mathnet_problems.csv"
)

OUTPUT_PATH = Path(
    "data/processed/problem_metadata.csv"
)


YEAR_PATTERN = re.compile(
    r"(?:19|20)\d{2}"
)


def extract_year(competition):
    if competition is None:
        return None

    matches = YEAR_PATTERN.findall(
        str(competition)
    )

    if not matches:
        return None

    return int(matches[-1])


def clean_competition_name(
    competition
):
    """
    Remove year-like tokens from a competition
    name while preserving the actual competition text.
    """

    if competition is None:
        return None

    value = str(
        competition
    ).strip()

    if not value:
        return None

    value = YEAR_PATTERN.sub(
        "",
        value
    )

    # Remove leftover separators.
    value = re.sub(
        r"[-_/]+",
        " ",
        value
    )

    # Normalize whitespace.
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def build_title(
    competition,
    year,
    problem_number=None
):
    competition_name = (
        clean_competition_name(
            competition
        )
    )

    if not competition_name:
        competition_name = (
            "Olympiad Problem"
        )

    if year is not None:
        year_text = str(
            int(year)
        )
    else:
        year_text = None

    if problem_number not in (
        None,
        "",
    ):
        if year_text:
            return (
                f"{competition_name} "
                f"{year_text} "
                f"P{problem_number}"
            )

        return (
            f"{competition_name} "
            f"P{problem_number}"
        )

    if year_text:
        return (
            f"{competition_name} "
            f"{year_text}"
        )

    return competition_name


def main():

    print("=" * 70)

    print(
        "OLYMPIAD INTELLIGENCE - "
        "CONTEST METADATA"
    )

    print("=" * 70)

    if not PROBLEMS_PATH.exists():
        raise FileNotFoundError(
            f"Missing: {PROBLEMS_PATH}"
        )

    df = pd.read_csv(
        PROBLEMS_PATH
    )

    records = []

    for _, row in df.iterrows():

        competition = row.get(
            "competition"
        )

        year = extract_year(
            competition
        )

        clean_name = (
            clean_competition_name(
                competition
            )
        )

        # We intentionally do NOT guess
        # the problem number yet.
        problem_number = None

        title = build_title(
            competition,
            year,
            problem_number
        )

        records.append({
            "problem_id":
                row.get("problem_id"),

            "competition_raw":
                competition,

            "competition":
                clean_name,

            "year":
                year,

            "problem_number":
                problem_number,

            "section":
                None,

            "title":
                title,

            "source":
                "MathNet",

            "metadata_status":
                (
                    "YEAR_ONLY"
                    if year is not None
                    else "COMPETITION_ONLY"
                ),
        })

    result = pd.DataFrame(
        records
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"\nProblems: {len(result)}"
    )

    print(
        "Years found:",
        result["year"].notna().sum()
    )

    print(
        "Problem numbers:",
        result["problem_number"].notna().sum()
    )

    print(
        "\nExamples:"
    )

    print(
        result[
            result["year"].notna()
        ][
            [
                "problem_id",
                "competition_raw",
                "competition",
                "year",
                "title",
            ]
        ]
        .head(25)
        .to_string(
            index=False
        )
    )

    print(
        "\nSaved:"
    )

    print(
        OUTPUT_PATH
    )

    print(
        "\n" + "=" * 70
    )


if __name__ == "__main__":
    main()