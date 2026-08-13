"""
OLYMPIAD INTELLIGENCE
HIGH-CONFIDENCE PROBLEM NUMBER MATCHER

Purpose:
    Match MathNet problems against an external contest catalog.

Important design rules:

    MATCHED
        Only very strong evidence.

    REVIEW
        Plausible candidate exists, but evidence is not
        strong enough to trust automatically.

    UNMATCHED
        No reliable match.

The system NEVER invents a problem number.
"""

from pathlib import Path
import re
import unicodedata
from difflib import SequenceMatcher

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

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


# ============================================================
# MATCH THRESHOLDS
# ============================================================

# Very strong match.
MATCH_COMBINED_THRESHOLD = 0.90

# Medium-confidence candidate.
REVIEW_COMBINED_THRESHOLD = 0.68

# Minimum difference between first and second candidates.
MATCH_MARGIN = 0.08

# Exact normalized text is accepted regardless of TF-IDF
# because this is effectively an identity match.
EXACT_SEQUENCE_THRESHOLD = 0.985


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize mathematical problem text.

    We remove:
        - markdown images
        - LaTeX commands
        - formatting noise
        - repeated whitespace

    But preserve:
        - words
        - numbers
        - mathematical content
    """

    if text is None:
        return ""

    text = str(text)

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = (
        text
        .encode(
            "ascii",
            "ignore"
        )
        .decode(
            "ascii"
        )
    )

    text = text.lower()

    # Remove markdown images.
    text = re.sub(
        r"!\[[^\]]*\]\([^)]+\)",
        " ",
        text
    )

    # Remove LaTeX commands.
    text = re.sub(
        r"\\[a-zA-Z]+",
        " ",
        text
    )

    # Remove LaTeX environments.
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

    # Remove common LaTeX formatting characters.
    text = re.sub(
        r"[\{\}\[\]\$]",
        " ",
        text
    )

    # Keep letters and numbers.
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


# ============================================================
# EXACT / SEQUENCE SIMILARITY
# ============================================================

def sequence_similarity(
    first,
    second
):
    """
    Character-level sequence similarity.

    Very useful when two datasets contain essentially
    the exact same problem statement.
    """

    if not first or not second:
        return 0.0

    return SequenceMatcher(
        None,
        first,
        second
    ).ratio()


# ============================================================
# COMPETITION FAMILY
# ============================================================

def get_competition_family(
    competition
):
    """
    Convert MathNet's many competition labels
    into a broad competition family.

    Examples:

        International Mathematical Olympiad
            -> IMO

        IMO 2006 Shortlisted Problems
            -> IMO

        1997-2023 IMO HK TST
            -> IMO
    """

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


# ============================================================
# DOMAIN NORMALIZATION
# ============================================================

def get_primary_domain(
    value
):
    """
    Extract a primary mathematical domain.

    Examples:

        "Algebra | Number Theory"
            -> algebra

        "Geometry"
            -> geometry
    """

    if value is None:
        return None

    value = str(
        value
    ).strip()

    if not value:
        return None

    first = value.split(
        "|"
    )[0].strip().lower()

    if "number theory" in first:
        return "number_theory"

    if "algebra" in first:
        return "algebra"

    if "geometry" in first:
        return "geometry"

    if "discrete" in first:
        return "discrete_mathematics"

    if "combinatorics" in first:
        return "discrete_mathematics"

    if "calculus" in first:
        return "calculus"

    if "statistics" in first:
        return "statistics"

    return first


# ============================================================
# BUILD TITLE
# ============================================================

def build_title(
    competition,
    year,
    problem_number
):
    family = (
        competition
        if competition
        else "Olympiad"
    )

    family = str(
        family
    ).strip()

    # Normalize common IMO variants.
    if "IMO" in family.upper():
        family = "IMO"

    if year is None:
        return family

    try:
        year = int(year)
    except Exception:
        pass

    if problem_number is None:
        return (
            f"{family} {year}"
        )

    return (
        f"{family} {year} "
        f"P{problem_number}"
    )


# ============================================================
# CALCULATE CANDIDATE SCORES
# ============================================================

def calculate_scores(
    query,
    candidates
):
    """
    Calculate three independent similarity signals:

        1. Word TF-IDF
        2. Character TF-IDF
        3. Sequence similarity

    Combined score is deliberately conservative.
    """

    query = normalize_text(
        query
    )

    candidate_texts = [
        normalize_text(text)
        for text in candidates
    ]

    if not query:
        return []

    if not candidate_texts:
        return []

    # --------------------------------------------------------
    # WORD TF-IDF
    # --------------------------------------------------------

    word_vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )

    word_matrix = (
        word_vectorizer.fit_transform(
            [query]
            +
            candidate_texts
        )
    )

    word_scores = cosine_similarity(
        word_matrix[0:1],
        word_matrix[1:]
    )[0]

    # --------------------------------------------------------
    # CHARACTER TF-IDF
    # --------------------------------------------------------

    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=1,
        sublinear_tf=True,
    )

    char_matrix = (
        char_vectorizer.fit_transform(
            [query]
            +
            candidate_texts
        )
    )

    char_scores = cosine_similarity(
        char_matrix[0:1],
        char_matrix[1:]
    )[0]

    # --------------------------------------------------------
    # SEQUENCE
    # --------------------------------------------------------

    sequence_scores = [
        sequence_similarity(
            query,
            text
        )
        for text in candidate_texts
    ]

    # --------------------------------------------------------
    # COMBINED
    # --------------------------------------------------------

    results = []

    for i in range(
        len(candidate_texts)
    ):

        word_score = float(
            word_scores[i]
        )

        char_score = float(
            char_scores[i]
        )

        sequence_score = float(
            sequence_scores[i]
        )

        combined = (
            0.35 * word_score
            +
            0.25 * char_score
            +
            0.40 * sequence_score
        )

        results.append({
            "word_score":
                word_score,

            "char_score":
                char_score,

            "sequence_score":
                sequence_score,

            "combined_score":
                float(
                    combined
                ),
        })

    return results


# ============================================================
# CLASSIFY MATCH
# ============================================================

def classify_match(
    best,
    second_score
):
    """
    Decide:

        MATCHED
        REVIEW
        UNMATCHED
    """

    combined = best[
        "combined_score"
    ]

    sequence = best[
        "sequence_score"
    ]

    margin = (
        combined
        -
        second_score
    )

    # Exact/near-exact statement.
    if (
        sequence
        >= EXACT_SEQUENCE_THRESHOLD
    ):
        return (
            "MATCHED",
            margin
        )

    # Strong independent evidence.
    if (
        combined
        >= MATCH_COMBINED_THRESHOLD
        and
        margin
        >= MATCH_MARGIN
    ):
        return (
            "MATCHED",
            margin
        )

    # Plausible but not safe enough.
    if (
        combined
        >= REVIEW_COMBINED_THRESHOLD
    ):
        return (
            "REVIEW",
            margin
        )

    return (
        "UNMATCHED",
        margin
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 70
    )

    print(
        "OLYMPIAD INTELLIGENCE - "
        "HIGH CONFIDENCE PROBLEM MATCHER"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    if not PROBLEMS_PATH.exists():
        raise FileNotFoundError(
            PROBLEMS_PATH
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            METADATA_PATH
        )

    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            CATALOG_PATH
        )

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

    # --------------------------------------------------------
    # ADD PROBLEM TEXT
    # --------------------------------------------------------

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
        columns=[
            "problem_text"
        ],
        errors="ignore"
    )

    metadata = metadata.merge(
        text_map,
        on="problem_id",
        how="left"
    )

    # --------------------------------------------------------
    # PREPARE DATA TYPES
    # --------------------------------------------------------

    metadata[
        "competition_family"
    ] = metadata[
        "competition"
    ].apply(
        get_competition_family
    )

    metadata[
        "domain_normalized"
    ] = metadata[
        "domain"
    ].apply(
        get_primary_domain
    ) if "domain" in metadata.columns else None

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

    # --------------------------------------------------------
    # FORCE STRING COLUMNS
    # --------------------------------------------------------

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

    # Numeric columns.
    for column in [
        "match_score",
        "metadata_match_margin",
        "word_score",
        "char_score",
        "sequence_score",
    ]:

        if column not in metadata.columns:

            metadata[column] = float(
                "nan"
            )

    # --------------------------------------------------------
    # TARGET COMPETITION:
    # IMO
    # --------------------------------------------------------

    catalog_imo = catalog[
        catalog[
            "competition_family"
        ]
        ==
        "IMO"
    ].copy()

    mathnet_imo = metadata[
        metadata[
            "competition_family"
        ]
        ==
        "IMO"
    ].copy()

    print(
        f"\nIMO catalog problems: "
        f"{len(catalog_imo)}"
    )

    print(
        f"IMO-related MathNet problems: "
        f"{len(mathnet_imo)}"
    )

    # --------------------------------------------------------
    # MATCHING
    # --------------------------------------------------------

    matched_count = 0
    review_count = 0
    unmatched_count = 0

    for index, row in mathnet_imo.iterrows():

        problem_text = row.get(
            "problem_text"
        )

        if not isinstance(
            problem_text,
            str
        ):
            problem_text = ""

        if not problem_text.strip():

            unmatched_count += 1

            metadata.loc[
                index,
                "metadata_status"
            ] = "UNMATCHED"

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

            unmatched_count += 1

            metadata.loc[
                index,
                "metadata_status"
            ] = "UNMATCHED"

            continue

        # ----------------------------------------------------
        # Rank candidates
        # ----------------------------------------------------

        ranked = sorted(
            range(
                len(scores)
            ),
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

        if len(ranked) > 1:

            second_score = scores[
                ranked[1]
            ][
                "combined_score"
            ]

        else:

            second_score = 0.0

        candidate = (
            catalog_imo.iloc[
                best_index
            ]
        )

        status, margin = (
            classify_match(
                best,
                second_score
            )
        )

        # ----------------------------------------------------
        # Save scores regardless of status
        # ----------------------------------------------------

        metadata.loc[
            index,
            "match_score"
        ] = round(
            best[
                "combined_score"
            ],
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
            best[
                "word_score"
            ],
            4
        )

        metadata.loc[
            index,
            "char_score"
        ] = round(
            best[
                "char_score"
            ],
            4
        )

        metadata.loc[
            index,
            "sequence_score"
        ] = round(
            best[
                "sequence_score"
            ],
            4
        )

        metadata.loc[
            index,
            "metadata_status"
        ] = status

        # ----------------------------------------------------
        # MATCHED
        # ----------------------------------------------------

        if status == "MATCHED":

            year = int(
                candidate[
                    "year"
                ]
            )

            number = int(
                candidate[
                    "problem_number"
                ]
            )

            external_id = str(
                candidate[
                    "problem_id_external"
                ]
            )

            title = (
                f"IMO {year} "
                f"P{number}"
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
            ] = external_id

            metadata.loc[
                index,
                "source"
            ] = str(
                candidate[
                    "source"
                ]
            )

            metadata.loc[
                index,
                "source_url"
            ] = str(
                candidate[
                    "source_url"
                ]
            )

            metadata.loc[
                index,
                "match_reason"
            ] = (
                "HIGH_CONFIDENCE_TEXT_MATCH"
            )

            matched_count += 1

            print(
                "\nMATCHED"
            )

            print(
                f"  MathNet: "
                f"{row['problem_id']}"
            )

            print(
                f"  Result: "
                f"{title}"
            )

            print(
                f"  Combined: "
                f"{best['combined_score']:.4f}"
            )

            print(
                f"  Sequence: "
                f"{best['sequence_score']:.4f}"
            )

            print(
                f"  Margin: "
                f"{margin:.4f}"
            )

        # ----------------------------------------------------
        # REVIEW
        # ----------------------------------------------------

        elif status == "REVIEW":

            review_count += 1

            # We store the candidate internally,
            # but DO NOT expose it as the title.
            metadata.loc[
                index,
                "match_reason"
            ] = (
                "CANDIDATE_REQUIRES_REVIEW"
            )

        # ----------------------------------------------------
        # UNMATCHED
        # ----------------------------------------------------

        else:

            unmatched_count += 1

            metadata.loc[
                index,
                "match_reason"
            ] = (
                "NO_SAFE_MATCH"
            )

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    metadata = metadata.drop(
        columns=[
            "competition_family",
            "domain_normalized",
            "problem_text",
        ],
        errors="ignore"
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    metadata.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "MATCHING COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nMATCHED:   "
        f"{matched_count}"
    )

    print(
        f"REVIEW:    "
        f"{review_count}"
    )

    print(
        f"UNMATCHED: "
        f"{unmatched_count}"
    )

    print(
        "\nTrusted problem numbers:"
    )

    trusted = metadata[
        metadata[
            "metadata_status"
        ]
        ==
        "MATCHED"
    ]

    if trusted.empty:

        print(
            "None."
        )

    else:

        print(
            trusted[
                [
                    "problem_id",
                    "competition",
                    "year",
                    "problem_number",
                    "title",
                    "match_score",
                    "sequence_score",
                    "metadata_match_margin",
                ]
            ]
            .to_string(
                index=False
            )
        )

    print(
        f"\nSaved: "
        f"{OUTPUT_PATH}"
    )

    print(
        "\n"
        + "=" * 70
    )


if __name__ == "__main__":
    main()