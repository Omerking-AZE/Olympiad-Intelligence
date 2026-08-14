import json
import math
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

VERIFICATION_PATH = Path(
    "data/feedback/edit_verification.json"
)

PROBLEMS_PATH = Path(
    "data/processed/mathnet_problems.csv"
)

CATALOG_PATH = Path(
    "data/metadata/external_problem_catalog.csv"
)

OUTPUT_PATH = Path(
    "data/feedback/external_verification.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

WORD_WEIGHT = 0.40
CHAR_WEIGHT = 0.35
SEQUENCE_WEIGHT = 0.25

STRONG_MATCH_THRESHOLD = 0.88
REVIEW_MATCH_THRESHOLD = 0.68

TOP_CANDIDATES = 5

AUTO_VERIFY_REPORT_THRESHOLD = 5


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    if text is None:
        return ""

    try:
        if pd.isna(text):
            return ""
    except (
        TypeError,
        ValueError,
    ):
        pass

    text = str(text)

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = (
        text
        .encode(
            "ascii",
            "ignore",
        )
        .decode(
            "ascii",
        )
    )

    text = text.lower()

    text = re.sub(
        r"!\[[^\]]*\]\([^)]+\)",
        " ",
        text,
    )

    text = re.sub(
        r"\\[a-zA-Z]+",
        " ",
        text,
    )

    text = re.sub(
        r"\\begin\{[^}]+\}",
        " ",
        text,
    )

    text = re.sub(
        r"\\end\{[^}]+\}",
        " ",
        text,
    )

    text = re.sub(
        r"[{}\[\]$]",
        " ",
        text,
    )

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# JSON SAFE
# ============================================================

def json_safe(value):
    if value is None:
        return None

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

        return value

    if hasattr(value, "item"):
        try:
            value = value.item()
        except (
            ValueError,
            TypeError,
        ):
            pass

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

        return value

    if isinstance(value, dict):
        return {
            str(key): json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            json_safe(item)
            for item in value
        ]

    try:
        if pd.isna(value):
            return None
    except (
        TypeError,
        ValueError,
    ):
        pass

    return value


# ============================================================
# LOAD JSON
# ============================================================

def load_json(path):
    if not path.exists():
        return []

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return []


# ============================================================
# LOAD MATHNET PROBLEMS
# ============================================================

def load_problem_map():
    if not PROBLEMS_PATH.exists():
        return {}

    df = pd.read_csv(
        PROBLEMS_PATH
    )

    if "problem_id" not in df.columns:
        return {}

    result = {}

    for _, row in df.iterrows():
        problem_id = (
            str(
                row.get(
                    "problem_id",
                    "",
                )
            )
            .strip()
            .lower()
        )

        if not problem_id:
            continue

        result[problem_id] = {
            "problem_text":
                row.get(
                    "problem_text",
                    "",
                ),

            "competition":
                row.get(
                    "competition"
                ),

            "domain":
                row.get(
                    "domain"
                ),
        }

    return result


# ============================================================
# LOAD EXTERNAL CATALOG
# ============================================================

def load_catalog():
    if not CATALOG_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(
        CATALOG_PATH
    )

    expected = [
        "title",
        "problem_id_external",
        "source_url",
        "year",
        "problem_number",
        "competition",
        "problem_text",
    ]

    for column in expected:
        if column not in df.columns:
            df[column] = None

    df = df[
        expected
    ].copy()

    df["problem_text"] = (
        df["problem_text"]
        .fillna("")
        .astype(str)
    )

    df["normalized_text"] = (
        df["problem_text"]
        .apply(normalize_text)
    )

    return df


# ============================================================
# PARSE SUGGESTION
# ============================================================

def parse_suggestion(
    suggestion,
):
    if not suggestion:
        return {
            "family": None,
            "year": None,
            "problem_number": None,
        }

    value = str(
        suggestion
    ).strip().upper()

    family = None

    if "IMO" in value:
        family = "IMO"

    year_match = re.search(
        r"\b(19|20)\d{2}\b",
        value,
    )

    number_match = re.search(
        r"\bP\s*([1-9]\d?)\b",
        value,
    )

    year = None

    if year_match:
        year = int(
            year_match.group(0)
        )

    problem_number = None

    if number_match:
        problem_number = int(
            number_match.group(1)
        )

    return {
        "family": family,
        "year": year,
        "problem_number": problem_number,
    }


# ============================================================
# CATALOG METADATA MATCH
# ============================================================

def find_exact_suggestion(
    suggestion,
    catalog,
):
    """
    Look up what the user explicitly suggested.

    IMPORTANT:
    This lookup is ONLY used to see whether the
    suggested metadata exists.

    It is NOT used to choose the text-match candidate.
    """

    parsed = parse_suggestion(
        suggestion
    )

    if (
        parsed["family"] != "IMO"
        or parsed["year"] is None
        or parsed["problem_number"] is None
    ):
        return None

    years = pd.to_numeric(
        catalog["year"],
        errors="coerce",
    )

    numbers = pd.to_numeric(
        catalog["problem_number"],
        errors="coerce",
    )

    mask = (
        (years == parsed["year"])
        &
        (numbers == parsed["problem_number"])
    )

    matches = catalog[
        mask
    ]

    if matches.empty:
        return None

    row = matches.iloc[0]

    return {
        "title": json_safe(
            row["title"]
        ),

        "problem_id_external":
            json_safe(
                row[
                    "problem_id_external"
                ]
            ),

        "source_url":
            json_safe(
                row["source_url"]
            ),

        "year":
            json_safe(
                row["year"]
            ),

        "problem_number":
            json_safe(
                row["problem_number"]
            ),

        "competition":
            json_safe(
                row["competition"]
            ),
    }


# ============================================================
# MULTI-SIGNAL TEXT SCORE
# ============================================================

def score_all_candidates(
    original_text,
    catalog,
):
    if catalog.empty:
        return []

    query = normalize_text(
        original_text
    )

    if not query:
        return []

    candidate_texts = (
        catalog[
            "normalized_text"
        ]
        .fillna("")
        .astype(str)
        .tolist()
    )

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
        word_matrix[1:],
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
        char_matrix[1:],
    )[0]

    # --------------------------------------------------------
    # SEQUENCE
    # --------------------------------------------------------

    sequence_scores = []

    for candidate_text in candidate_texts:
        sequence_scores.append(
            SequenceMatcher(
                None,
                query,
                candidate_text,
                autojunk=False,
            ).ratio()
        )

    # --------------------------------------------------------
    # COMBINE
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

        combined_score = (
            WORD_WEIGHT * word_score
            +
            CHAR_WEIGHT * char_score
            +
            SEQUENCE_WEIGHT * sequence_score
        )

        row = catalog.iloc[i]

        results.append(
            {
                "title":
                    json_safe(
                        row["title"]
                    ),

                "problem_id_external":
                    json_safe(
                        row[
                            "problem_id_external"
                        ]
                    ),

                "source_url":
                    json_safe(
                        row["source_url"]
                    ),

                "year":
                    json_safe(
                        row["year"]
                    ),

                "problem_number":
                    json_safe(
                        row[
                            "problem_number"
                        ]
                    ),

                "competition":
                    json_safe(
                        row[
                            "competition"
                        ]
                    ),

                "word_similarity":
                    round(
                        word_score,
                        4,
                    ),

                "char_similarity":
                    round(
                        char_score,
                        4,
                    ),

                "sequence_similarity":
                    round(
                        sequence_score,
                        4,
                    ),

                "combined_similarity":
                    round(
                        combined_score,
                        4,
                    ),
            }
        )

    results.sort(
        key=lambda item:
            item[
                "combined_similarity"
            ],
        reverse=True,
    )

    return results


# ============================================================
# COMPARE SUGGESTED CANDIDATE WITH BEST TEXT MATCH
# ============================================================

def compare_candidates(
    suggested_candidate,
    best_text_candidate,
):
    if (
        suggested_candidate is None
        or best_text_candidate is None
    ):
        return False

    return (
        str(
            suggested_candidate[
                "problem_id_external"
            ]
        )
        ==
        str(
            best_text_candidate[
                "problem_id_external"
            ]
        )
    )


# ============================================================
# CLASSIFY
# ============================================================

def classify(
    report_count,
    best_text_candidate,
    suggested_candidate,
):
    if best_text_candidate is None:
        return {
            "status":
                "NO_EXTERNAL_MATCH",

            "confidence":
                "LOW",

            "reason":
                "No external problem candidate could be identified.",
        }

    best_score = float(
        best_text_candidate[
            "combined_similarity"
        ]
    )

    suggested_is_best = compare_candidates(
        suggested_candidate,
        best_text_candidate,
    )

    # --------------------------------------------------------
    # Strong exact relation
    # --------------------------------------------------------

    if (
        suggested_is_best
        and
        best_score
        >= STRONG_MATCH_THRESHOLD
        and
        report_count
        >= AUTO_VERIFY_REPORT_THRESHOLD
    ):
        return {
            "status":
                "AUTO_VERIFY_CANDIDATE",

            "confidence":
                "HIGH",

            "reason":
                "The suggested external problem is also the strongest text match and has enough independent reports.",
        }

    # --------------------------------------------------------
    # Strong external candidate, but not enough reports
    # --------------------------------------------------------

    if (
        suggested_is_best
        and
        best_score
        >= STRONG_MATCH_THRESHOLD
    ):
        return {
            "status":
                "EXTERNAL_CONFIRMED",

            "confidence":
                "HIGH",

            "reason":
                "The suggested problem is the strongest text match, but the report threshold for automatic application has not been reached.",
        }

    # --------------------------------------------------------
    # Candidate exists but not the best text match
    # --------------------------------------------------------

    if not suggested_is_best:
        if best_score >= REVIEW_MATCH_THRESHOLD:
            return {
                "status":
                    "CONFLICTING_EVIDENCE",

                "confidence":
                    "MEDIUM",

                "reason":
                    "The suggested problem exists, but another external problem matches the MathNet text more strongly.",
            }

        return {
            "status":
                "SUGGESTION_UNSUPPORTED",

            "confidence":
                "LOW",

            "reason":
                "The suggested external problem does not match the MathNet problem text.",
        }

    # --------------------------------------------------------
    # Weak suggested match
    # --------------------------------------------------------

    if (
        suggested_is_best
        and
        best_score
        >= REVIEW_MATCH_THRESHOLD
    ):
        return {
            "status":
                "EXTERNAL_REVIEW",

            "confidence":
                "MEDIUM",

            "reason":
                "The suggested problem is the best candidate, but text similarity is not strong enough for automatic confirmation.",
        }

    return {
        "status":
            "EXTERNAL_UNCONFIRMED",

        "confidence":
            "LOW",

        "reason":
            "The suggested problem has insufficient text similarity.",
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "OLYMPIAD INTELLIGENCE - "
        "EXTERNAL METADATA VERIFIER"
    )

    print("=" * 70)

    verification = load_json(
        VERIFICATION_PATH
    )

    problems = load_problem_map()

    catalog = load_catalog()

    print(
        f"\nVerification suggestions: "
        f"{len(verification)}"
    )

    print(
        f"MathNet problems: "
        f"{len(problems)}"
    )

    print(
        f"External catalog rows: "
        f"{len(catalog)}"
    )

    results = []

    for item in verification:

        problem_id = (
            str(
                item.get(
                    "problem_id",
                    "",
                )
            )
            .strip()
            .lower()
        )

        suggested_value = (
            str(
                item.get(
                    "suggested_value",
                    "",
                )
            )
            .strip()
        )

        issue_type = (
            str(
                item.get(
                    "issue_type",
                    "",
                )
            )
            .strip()
            .lower()
        )

        report_count = int(
            item.get(
                "report_count",
                0,
            )
        )

        problem = problems.get(
            problem_id,
            {},
        )

        original_text = problem.get(
            "problem_text",
            "",
        )

        # ----------------------------------------------------
        # 1. Find the user-suggested problem.
        # ----------------------------------------------------

        suggested_candidate = (
            find_exact_suggestion(
                suggestion=
                    suggested_value,
                catalog=catalog,
            )
        )

        # ----------------------------------------------------
        # 2. Independently find the best
        #    text match across the ENTIRE catalog.
        # ----------------------------------------------------

        all_candidates = (
            score_all_candidates(
                original_text=
                    original_text,
                catalog=catalog,
            )
        )

        top_candidates = (
            all_candidates[
                :TOP_CANDIDATES
            ]
        )

        best_text_candidate = (
            all_candidates[0]
            if all_candidates
            else None
        )

        # ----------------------------------------------------
        # 3. Verify.
        # ----------------------------------------------------

        verification_result = classify(
            report_count=
                report_count,

            best_text_candidate=
                best_text_candidate,

            suggested_candidate=
                suggested_candidate,
        )

        # ----------------------------------------------------
        # 4. Compare explicit suggestion.
        # ----------------------------------------------------

        suggested_is_best = (
            compare_candidates(
                suggested_candidate,
                best_text_candidate,
            )
        )

        # ----------------------------------------------------
        # 5. Build result.
        # ----------------------------------------------------

        results.append(
            {
                "problem_id":
                    problem_id,

                "issue_type":
                    issue_type,

                "suggested_value":
                    suggested_value,

                "report_count":
                    report_count,

                "current_problem": {
                    "competition":
                        json_safe(
                            problem.get(
                                "competition"
                            )
                        ),

                    "domain":
                        json_safe(
                            problem.get(
                                "domain"
                            )
                        ),

                    "problem_text_length":
                        len(
                            normalize_text(
                                original_text
                            )
                        ),
                },

                "suggested_candidate":
                    suggested_candidate,

                "suggested_is_best_text_match":
                    suggested_is_best,

                "best_text_candidate":
                    best_text_candidate,

                "top_text_candidates":
                    top_candidates,

                "verification":
                    verification_result,

                "auto_apply_eligible":
                    (
                        verification_result[
                            "status"
                        ]
                        ==
                        "AUTO_VERIFY_CANDIDATE"
                    ),
            }
        )

    results = json_safe(
        results
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    # --------------------------------------------------------
    # Validate.
    # --------------------------------------------------------

    with open(
        OUTPUT_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        json.load(file)

    print(
        "\nJSON validation passed."
    )

    print(
        "\nExternal verification:"
    )

    if not results:
        print(
            "  None"
        )

    for result in results:

        verification_result = (
            result[
                "verification"
            ]
        )

        print(
            f"  "
            f"{result['problem_id']} | "
            f"{result['suggested_value']} | "
            f"{verification_result['status']} | "
            f"{verification_result['confidence']}"
        )

        suggested = result[
            "suggested_candidate"
        ]

        best = result[
            "best_text_candidate"
        ]

        print(
            f"    Suggested exists: "
            f"{suggested is not None}"
        )

        print(
            f"    Suggested is best text match: "
            f"{result['suggested_is_best_text_match']}"
        )

        if suggested:
            print(
                f"    Suggested catalog: "
                f"{suggested['title']}"
            )

        if best:
            print(
                f"    Best text match: "
                f"{best['title']} | "
                f"combined="
                f"{best['combined_similarity']}"
            )

        print(
            f"    Auto apply eligible: "
            f"{result['auto_apply_eligible']}"
        )

    print(
        f"\nSaved: "
        f"{OUTPUT_PATH}"
    )

    print(
        "\nIMPORTANT: "
        "No metadata was changed."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()