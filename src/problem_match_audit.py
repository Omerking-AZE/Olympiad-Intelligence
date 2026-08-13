from pathlib import Path
import re
import unicodedata
from difflib import SequenceMatcher

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROBLEMS_PATH = Path(
    "data/processed/mathnet_problems.csv"
)

METADATA_PATH = Path(
    "data/processed/problem_metadata.csv"
)

CATALOG_PATH = Path(
    "data/metadata/external_problem_catalog.csv"
)

OUTPUT_PATH = Path(
    "data/processed/problem_metadata.csv"
)


MATCH_COMBINED_THRESHOLD = 0.90
MATCH_MARGIN = 0.08
EXACT_SEQUENCE_THRESHOLD = 0.985


def normalize_text(text):
    if text is None:
        return ""

    text = str(text)

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = (
        text
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    text = text.lower()

    text = re.sub(
        r"!\[[^\]]*\]\([^)]+\)",
        " ",
        text
    )

    text = re.sub(
        r"\\[a-zA-Z]+",
        " ",
        text
    )

    text = re.sub(
        r"\\begin\{[^}]+\}",
        " ",
        text
    )

    text = re.sub(
        r"\\end\{[^}]+\}",
        " ",
        text
    )

    text = re.sub(
        r"[\{\}\[\]\$]",
        " ",
        text
    )

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def get_competition_family(competition):
    if competition is None:
        return None

    value = str(
        competition
    ).upper()

    if "IMO" in value:
        return "IMO"

    if "EGMO" in value:
        return "EGMO"

    if "APMO" in value:
        return "APMO"

    if "HMMT" in value:
        return "HMMT"

    if "JBMO" in value:
        return "JBMO"

    if "BMO" in value:
        return "BMO"

    if "RMM" in value:
        return "RMM"

    return None


def build_display_title(
    competition,
    year,
    problem_number=None
):
    if competition is None:
        competition = "Olympiad Problem"

    competition = str(
        competition
    ).strip()

    if not competition:
        competition = "Olympiad Problem"

    if "IMO" in competition.upper():
        competition = "IMO"

    if year is not None:
        try:
            year = int(year)
        except (
            TypeError,
            ValueError,
        ):
            year = None

    if (
        problem_number is not None
        and year is not None
    ):
        return (
            f"{competition} "
            f"{year} "
            f"P{problem_number}"
        )

    if year is not None:
        return (
            f"{competition} "
            f"{year}"
        )

    return competition


def calculate_scores(
    query,
    candidates
):
    query = normalize_text(query)

    candidate_texts = [
        normalize_text(text)
        for text in candidates
    ]

    if not query or not candidate_texts:
        return []

    word_vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )

    word_matrix = (
        word_vectorizer.fit_transform(
            [query] + candidate_texts
        )
    )

    word_scores = cosine_similarity(
        word_matrix[0:1],
        word_matrix[1:]
    )[0]

    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=1,
        sublinear_tf=True,
    )

    char_matrix = (
        char_vectorizer.fit_transform(
            [query] + candidate_texts
        )
    )

    char_scores = cosine_similarity(
        char_matrix[0:1],
        char_matrix[1:]
    )[0]

    sequence_scores = [
        SequenceMatcher(
            None,
            query,
            candidate
        ).ratio()
        for candidate in candidate_texts
    ]

    results = []

    for i in range(len(candidate_texts)):
        word = float(
            word_scores[i]
        )

        char = float(
            char_scores[i]
        )

        sequence = float(
            sequence_scores[i]
        )

        combined = (
            0.35 * word
            + 0.25 * char
            + 0.40 * sequence
        )

        results.append({
            "word_score": word,
            "char_score": char,
            "sequence_score": sequence,
            "combined_score": combined,
        })

    return results


def classify_match(
    best,
    second_score
):
    combined = best[
        "combined_score"
    ]

    sequence = best[
        "sequence_score"
    ]

    margin = (
        combined
        - second_score
    )

    if (
        sequence
        >= EXACT_SEQUENCE_THRESHOLD
    ):
        return "MATCHED", margin

    if (
        combined
        >= MATCH_COMBINED_THRESHOLD
        and margin
        >= MATCH_MARGIN
    ):
        return "MATCHED", margin

    if (
        combined >= 0.65
        and margin >= 0.05
    ):
        return "REVIEW", margin

    return "UNMATCHED", margin


def main():
    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "HIGH CONFIDENCE PROBLEM MATCHER"
    )
    print("=" * 70)

    problems = pd.read_csv(
        PROBLEMS_PATH
    )

    metadata = pd.read_csv(
        METADATA_PATH
    )

    catalog = pd.read_csv(
        CATALOG_PATH
    )

    print(
        f"\nMathNet problems: "
        f"{len(problems)}"
    )

    print(
        f"Catalog problems: "
        f"{len(catalog)}"
    )

    text_map = (
        problems[
            [
                "problem_id",
                "problem_text",
            ]
        ]
        .drop_duplicates(
            "problem_id"
        )
    )

    metadata = metadata.drop(
        columns=["problem_text"],
        errors="ignore"
    )

    metadata = metadata.merge(
        text_map,
        on="problem_id",
        how="left"
    )

    metadata[
        "competition_family"
    ] = metadata[
        "competition"
    ].apply(
        get_competition_family
    )

    catalog[
        "competition_family"
    ] = catalog[
        "competition"
    ].apply(
        get_competition_family
    )

    catalog[
        "problem_text"
    ] = catalog[
        "problem_text"
    ].fillna(
        ""
    ).astype(
        str
    )

    string_columns = [
        "problem_number",
        "external_problem_id",
        "source_url",
        "title",
        "source",
        "metadata_status",
        "match_reason",
    ]

    for column in string_columns:
        if column not in metadata.columns:
            metadata[column] = pd.Series(
                [None] * len(metadata),
                dtype="object"
            )
        else:
            metadata[column] = (
                metadata[column]
                .astype("object")
            )

    numeric_columns = [
        "match_score",
        "metadata_match_margin",
        "word_score",
        "char_score",
        "sequence_score",
    ]

    for column in numeric_columns:
        if column not in metadata.columns:
            metadata[column] = float("nan")

    catalog_imo = catalog[
        catalog[
            "competition_family"
        ] == "IMO"
    ].copy()

    mathnet_imo = metadata[
        metadata[
            "competition_family"
        ] == "IMO"
    ].copy()

    print(
        f"\nIMO catalog problems: "
        f"{len(catalog_imo)}"
    )

    print(
        f"IMO-related MathNet problems: "
        f"{len(mathnet_imo)}"
    )

    successful = 0
    review = 0
    unmatched = 0

    for index, row in mathnet_imo.iterrows():
        problem_text = row.get(
            "problem_text"
        )

        if not isinstance(
            problem_text,
            str
        ) or not problem_text.strip():
            unmatched += 1
            continue

        candidate_texts = (
            catalog_imo[
                "problem_text"
            ].tolist()
        )

        scores = calculate_scores(
            problem_text,
            candidate_texts
        )

        if not scores:
            unmatched += 1
            continue

        ranked = sorted(
            range(len(scores)),
            key=lambda i:
                scores[i][
                    "combined_score"
                ],
            reverse=True
        )

        best_index = ranked[0]

        best = scores[
            best_index
        ]

        second_score = (
            scores[
                ranked[1]
            ][
                "combined_score"
            ]
            if len(ranked) > 1
            else 0.0
        )

        candidate = catalog_imo.iloc[
            best_index
        ]

        status, margin = (
            classify_match(
                best,
                second_score
            )
        )

        metadata.loc[
            index,
            "match_score"
        ] = round(
            best["combined_score"],
            4
        )

        metadata.loc[
            index,
            "metadata_match_margin"
        ] = round(
            margin,
            4
        )

        metadata.loc[
            index,
            "word_score"
        ] = round(
            best["word_score"],
            4
        )

        metadata.loc[
            index,
            "char_score"
        ] = round(
            best["char_score"],
            4
        )

        metadata.loc[
            index,
            "sequence_score"
        ] = round(
            best["sequence_score"],
            4
        )

        metadata.loc[
            index,
            "metadata_status"
        ] = status

        if status == "MATCHED":
            year = int(
                candidate["year"]
            )

            number = int(
                candidate[
                    "problem_number"
                ]
            )

            title = (
                f"IMO {year} P{number}"
            )

            metadata.loc[
                index,
                "competition"
            ] = "IMO"

            metadata.loc[
                index,
                "year"
            ] = year

            metadata.loc[
                index,
                "problem_number"
            ] = str(
                number
            )

            metadata.loc[
                index,
                "title"
            ] = title

            metadata.loc[
                index,
                "external_problem_id"
            ] = str(
                candidate[
                    "problem_id_external"
                ]
            )

            metadata.loc[
                index,
                "source"
            ] = str(
                candidate["source"]
            )

            metadata.loc[
                index,
                "source_url"
            ] = str(
                candidate["source_url"]
            )

            metadata.loc[
                index,
                "match_reason"
            ] = (
                "HIGH_CONFIDENCE_TEXT_MATCH"
            )

            successful += 1

        elif status == "REVIEW":
            review += 1

        else:
            unmatched += 1

    # Fallback title for EVERY problem.
    for index, row in metadata.iterrows():
        current_title = row.get(
            "title"
        )

        if (
            current_title is not None
            and not pd.isna(
                current_title
            )
            and str(
                current_title
            ).strip()
        ):
            continue

        metadata.loc[
            index,
            "title"
        ] = build_display_title(
            row.get(
                "competition"
            ),
            row.get(
                "year"
            ),
            row.get(
                "problem_number"
            ),
        )

    metadata = metadata.drop(
        columns=[
            "competition_family",
            "problem_text",
        ],
        errors="ignore"
    )

    metadata.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print("=" * 70)
    print(
        "MATCHING COMPLETE"
    )
    print("=" * 70)

    print(
        f"\nMatched:   {successful}"
    )

    print(
        f"Review:    {review}"
    )

    print(
        f"Unmatched: {unmatched}"
    )

    print(
        "\nDisplay title coverage:",
        metadata["title"]
        .notna()
        .sum(),
        "/",
        len(metadata)
    )

    print(
        f"\nSaved: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()