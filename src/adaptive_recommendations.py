"""
OLYMPIAD INTELLIGENCE
Adaptive Recommendation Engine

Pipeline:

    Student profile
        +
    Weakness profile
        +
    Difficulty data
        +
    Problem metadata
        в†“
    Adaptive recommendations
        в†“
    CSV + valid JSON

Important:
    - Existing OVR / skill logic is preserved.
    - Metadata only enriches recommendations.
    - Every recommendation gets a user-facing title.
    - NaN / Infinity are converted to JSON null.
"""

from pathlib import Path
import json
import math

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROFILE_PATH = Path(
    "data/processed/student_profile.json"
)

WEAKNESS_PATH = Path(
    "data/processed/student_weaknesses.json"
)

PROBLEMS_PATH = Path(
    "data/processed/mathnet_difficulty.csv"
)

METADATA_PATH = Path(
    "data/processed/problem_metadata.csv"
)

OUTPUT_CSV = Path(
    "data/processed/adaptive_recommendations.csv"
)

OUTPUT_JSON = Path(
    "data/processed/adaptive_recommendations.json"
)


# ============================================================
# CONFIG
# ============================================================

NEUTRAL_SKILL = 55

TOP_RECOMMENDATIONS = 15

DOMAIN_MAP = {
    "Algebra": "algebra",
    "Geometry": "geometry",
    "Number Theory": "number_theory",
    "Discrete Mathematics": "discrete_mathematics",
}


# ============================================================
# JSON LOADER
# ============================================================

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ============================================================
# SAFE NUMERIC HELPERS
# ============================================================

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default

        if pd.isna(value):
            return default

        value = float(value)

        if not math.isfinite(value):
            return default

        return value

    except (
        TypeError,
        ValueError,
    ):
        return default


def safe_int(value):
    try:
        if value is None:
            return None

        if pd.isna(value):
            return None

        return int(float(value))

    except (
        TypeError,
        ValueError,
    ):
        return None


# ============================================================
# PROBLEM TEXT
# ============================================================

PROBLEM_TEXT_CANDIDATES = [
    "problem_text",
    "problem_statement",
    "statement",
    "text",
    "problem",
    "description",
]


def normalize_problem_text_column(problems):
    """
    Normalize whichever problem-statement field exists in the
    source dataset to a single frontend-facing `problem_text`
    column.

    No text is invented. If the dataset has no statement field,
    the output keeps `problem_text` as null.
    """

    if "problem_text" in problems.columns:
        problems["problem_text"] = problems[
            "problem_text"
        ].where(
            problems["problem_text"].notna(),
            None,
        )

        print(
            "Problem text source column: problem_text"
        )

        return problems

    for candidate in PROBLEM_TEXT_CANDIDATES[1:]:
        if candidate not in problems.columns:
            continue

        problems["problem_text"] = problems[
            candidate
        ].where(
            problems[candidate].notna(),
            None,
        )

        print(
            f"Problem text source column: {candidate}"
        )

        return problems

    problems["problem_text"] = None

    print(
        "Warning: no problem-text column found in "
        "mathnet_difficulty.csv. "
        "View Problem will show an unavailable-state "
        "message until statement data is exported."
    )

    return problems


# ============================================================
# DIFFICULTY FIT
# ============================================================

def calculate_difficulty_fit(
    difficulty,
    skill,
):
    target = skill + 6

    distance = abs(
        difficulty - target
    )

    return max(
        0.0,
        50.0 - distance * 2.0,
    )


# ============================================================
# ADAPTIVE SCORE
# ============================================================

def calculate_adaptive_score(
    difficulty,
    skill,
    weakness_priority,
):
    difficulty_fit = (
        calculate_difficulty_fit(
            difficulty,
            skill,
        )
    )

    score = (
        weakness_priority * 0.60
        +
        difficulty_fit * 0.40
    )

    return round(
        score,
        2,
    )


# ============================================================
# DOMAIN RECOMMENDATIONS
# ============================================================

def recommend_domain(
    problems,
    domain_name,
    student_skill,
    recommendation_skill,
    weakness_priority,
    weakness_classification,
    weakness_confidence,
    skill_unknown,
    count=5,
):
    domain_series = (
        problems["domain"]
        .fillna("")
        .astype(str)
    )

    mask = domain_series.str.contains(
        domain_name,
        case=False,
        na=False,
        regex=False,
    )

    domain_problems = problems[
        mask
    ].copy()

    if domain_problems.empty:
        return pd.DataFrame()

    domain_problems[
        "student_skill"
    ] = student_skill

    domain_problems[
        "recommendation_skill"
    ] = recommendation_skill

    domain_problems[
        "weakness_priority"
    ] = weakness_priority

    domain_problems[
        "weakness_classification"
    ] = weakness_classification

    domain_problems[
        "weakness_confidence"
    ] = weakness_confidence

    domain_problems[
        "skill_unknown"
    ] = skill_unknown

    # Difficulty gap
    domain_problems[
        "difficulty_gap"
    ] = (
        domain_problems[
            "difficulty_score"
        ]
        .apply(safe_float)
        -
        recommendation_skill
    )

    # Difficulty fit
    domain_problems[
        "difficulty_fit"
    ] = domain_problems[
        "difficulty_score"
    ].apply(
        lambda value:
            calculate_difficulty_fit(
                safe_float(value),
                recommendation_skill,
            )
    )

    # Adaptive score
    domain_problems[
        "adaptive_score"
    ] = domain_problems[
        "difficulty_score"
    ].apply(
        lambda value:
            calculate_adaptive_score(
                safe_float(value),
                recommendation_skill,
                weakness_priority,
            )
    )

    # Training zone
    domain_problems[
        "training_zone"
    ] = (
        (
            domain_problems[
                "difficulty_gap"
            ]
            >= 3
        )
        &
        (
            domain_problems[
                "difficulty_gap"
            ]
            <= 10
        )
    )

    domain_problems[
        "target_domain"
    ] = domain_name

    return (
        domain_problems
        .sort_values(
            [
                "training_zone",
                "adaptive_score",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .head(count)
    )


# ============================================================
# BUILD RECOMMENDATIONS
# ============================================================

def build_recommendations(
    profile,
    weaknesses,
    problems,
):
    results = []

    for domain_name, skill_key in DOMAIN_MAP.items():

        student_skill = safe_float(
            profile.get(
                skill_key,
                0,
            )
        )

        weakness = weaknesses.get(
            skill_key,
            {},
        )

        weakness_priority = safe_float(
            weakness.get(
                "priority",
                0,
            )
        )

        weakness_classification = (
            weakness.get(
                "classification",
                "NONE",
            )
        )

        weakness_confidence = safe_float(
            weakness.get(
                "confidence",
                0,
            )
        )

        skill_unknown = (
            weakness_classification
            == "NOT_ENOUGH_DATA"
            or student_skill == 0
        )

        if skill_unknown:
            recommendation_skill = (
                NEUTRAL_SKILL
            )

            recommendation_priority = (
                20.0
            )

        else:
            recommendation_skill = (
                student_skill
            )

            recommendation_priority = (
                weakness_priority
            )

        selected = recommend_domain(
            problems=problems,
            domain_name=domain_name,
            student_skill=student_skill,
            recommendation_skill=recommendation_skill,
            weakness_priority=recommendation_priority,
            weakness_classification=weakness_classification,
            weakness_confidence=weakness_confidence,
            skill_unknown=skill_unknown,
            count=5,
        )

        if selected.empty:
            continue

        results.append(
            selected
        )

    if not results:
        return pd.DataFrame()

    result = pd.concat(
        results,
        ignore_index=True,
    )

    return (
        result
        .sort_values(
            "adaptive_score",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# LOAD METADATA
# ============================================================

def load_metadata():
    if not METADATA_PATH.exists():
        print(
            "\nWarning: metadata file not found."
        )

        return pd.DataFrame(
            columns=[
                "problem_id",
                "title",
                "competition",
                "year",
                "problem_number",
                "section",
                "metadata_status",
                "match_score",
                "source",
                "source_url",
            ]
        )

    metadata = pd.read_csv(
        METADATA_PATH
    )

    expected_columns = [
        "problem_id",
        "title",
        "competition",
        "year",
        "problem_number",
        "section",
        "problem_text",
        "metadata_status",
        "match_score",
        "source",
        "source_url",
    ]

    for column in expected_columns:
        if column not in metadata.columns:
            metadata[column] = None

    return metadata[
        expected_columns
    ].copy()


# ============================================================
# USER-FACING TITLE
# ============================================================

def build_fallback_title(row):
    """
    Always return a human-readable title.

    Priority:

        1. title
        2. competition + year + problem number
        3. competition + year
        4. competition
        5. Olympiad Problem

    Never expose MATHNET IDs here.
    """

    title = row.get(
        "title"
    )

    if (
        title is not None
        and not pd.isna(title)
        and str(title).strip()
    ):
        return str(
            title
        ).strip()

    competition = row.get(
        "competition"
    )

    year = row.get(
        "year"
    )

    problem_number = row.get(
        "problem_number"
    )

    if competition is None:
        competition = ""

    elif pd.isna(competition):
        competition = ""

    else:
        competition = str(
            competition
        ).strip()

    parsed_year = safe_int(
        year
    )

    parsed_problem_number = (
        safe_int(
            problem_number
        )
    )

    if (
        "IMO" in competition.upper()
    ):
        competition = "IMO"

    if (
        competition
        and parsed_year is not None
        and parsed_problem_number is not None
    ):
        return (
            f"{competition} "
            f"{parsed_year} "
            f"P{parsed_problem_number}"
        )

    if (
        competition
        and parsed_year is not None
    ):
        return (
            f"{competition} "
            f"{parsed_year}"
        )

    if competition:
        return competition

    return "Olympiad Problem"


# ============================================================
# ENRICH RECOMMENDATIONS
# ============================================================

def enrich_recommendations(
    recommendations,
    metadata,
):
    if recommendations.empty:
        return recommendations

    # Preserve any problem text already attached to the
    # difficulty dataset before metadata enrichment.
    recommendation_problem_text = None

    if "problem_text" in recommendations.columns:
        recommendation_problem_text = (
            recommendations["problem_text"]
        )

    if metadata.empty:
        recommendations[
            "title"
        ] = recommendations.apply(
            build_fallback_title,
            axis=1,
        )

        return recommendations

    metadata = (
        metadata
        .drop_duplicates(
            subset=[
                "problem_id"
            ],
            keep="last",
        )
    )

    metadata_fields = [
        "title",
        "competition",
        "year",
        "problem_number",
        "section",
        "problem_text",
        "metadata_status",
        "match_score",
        "source",
        "source_url",
    ]

    recommendations = (
        recommendations.drop(
            columns=[
                field
                for field in metadata_fields
                if field in recommendations.columns
            ],
            errors="ignore",
        )
    )

    enriched = recommendations.merge(
        metadata,
        on="problem_id",
        how="left",
    )

    # If the metadata table has no problem text, restore the
    # statement that came from mathnet_difficulty.csv.
    if recommendation_problem_text is not None:
        if "problem_text" not in enriched.columns:
            enriched[
                "problem_text"
            ] = recommendation_problem_text
        else:
            enriched[
                "problem_text"
            ] = enriched[
                "problem_text"
            ].where(
                enriched["problem_text"].notna()
                & enriched["problem_text"].astype(str).str.strip().ne(""),
                recommendation_problem_text,
            )

    enriched[
        "title"
    ] = enriched.apply(
        build_fallback_title,
        axis=1,
    )

    return enriched


# ============================================================
# JSON-SAFE VALUE
# ============================================================

def make_json_safe(value):
    """
    Convert anything that is not valid JSON
    into a valid JSON value.

    NaN / +Infinity / -Infinity в†’ null.
    """

    if value is None:
        return None

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

        return value

    if isinstance(
        value,
        (int, str, bool),
    ):
        return value

    if isinstance(
        value,
        dict,
    ):
        return {
            str(key):
                make_json_safe(val)
            for key, val in value.items()
        }

    if isinstance(
        value,
        list,
    ):
        return [
            make_json_safe(item)
            for item in value
        ]

    # pandas / numpy scalar fallback
    try:
        if pd.isna(value):
            return None
    except (
        TypeError,
        ValueError,
    ):
        pass

    try:
        return value.item()
    except AttributeError:
        return str(value)


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(
    recommendations,
):
    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    recommendations.to_csv(
        OUTPUT_CSV,
        index=False,
    )


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    recommendations,
):
    """
    Create strictly valid JSON.

    JSON does NOT support NaN or Infinity,
    so all non-finite numbers become null.
    """

    frontend_columns = [
        "problem_id",

        # User-facing metadata
        "title",
        "competition",
        "year",
        "problem_number",
        "section",
        "problem_text",

        # Recommendation values
        "target_domain",
        "difficulty_score",
        "student_skill",
        "recommendation_skill",
        "weakness_priority",
        "weakness_classification",
        "weakness_confidence",
        "difficulty_gap",
        "difficulty_fit",
        "adaptive_score",
        "training_zone",
        "skill_unknown",
        "problem_type",

        # Metadata quality
        "metadata_status",
        "match_score",
        "source",
        "source_url",
    ]

    available = [
        column
        for column in frontend_columns
        if column in recommendations.columns
    ]

    data = (
        recommendations[
            available
        ]
        .head(
            TOP_RECOMMENDATIONS
        )
        .copy()
    )

    # Convert to object so missing values can
    # safely become Python None.
    data = data.astype(
        object
    )

    records = data.to_dict(
        orient="records"
    )

    safe_records = [
        make_json_safe(
            record
        )
        for record in records
    ]

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            safe_records,
            file,
            indent=4,
            ensure_ascii=False,
            allow_nan=False,
        )


# ============================================================
# VALIDATE OUTPUT JSON
# ============================================================

def validate_json_output():
    """
    Immediately re-open the generated JSON.
    If this fails, the Python pipeline stops instead
    of giving the frontend a broken file.
    """

    with open(
        OUTPUT_JSON,
        "r",
        encoding="utf-8",
    ) as file:

        parsed = json.load(
            file
        )

    if not isinstance(
        parsed,
        list,
    ):
        raise ValueError(
            "Recommendation JSON must be a list."
        )

    print(
        f"\nJSON validation passed: "
        f"{len(parsed)} records."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "ADAPTIVE RECOMMENDATIONS"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load profile
    # --------------------------------------------------------

    profile = load_json(
        PROFILE_PATH
    )

    # --------------------------------------------------------
    # Load weaknesses
    # --------------------------------------------------------

    weaknesses = load_json(
        WEAKNESS_PATH
    )

    # --------------------------------------------------------
    # Load difficulty data
    # --------------------------------------------------------

    if not PROBLEMS_PATH.exists():
        raise FileNotFoundError(
            f"Problem file not found: "
            f"{PROBLEMS_PATH}"
        )

    problems = pd.read_csv(
        PROBLEMS_PATH
    )

    problems = normalize_problem_text_column(
        problems
    )

    print(
        f"\nLoaded problems: "
        f"{len(problems)}"
    )

    problem_text_count = int(
        problems["problem_text"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )

    print(
        f"Problem statements available: "
        f"{problem_text_count}/{len(problems)}"
    )

    # --------------------------------------------------------
    # Build recommendations
    # --------------------------------------------------------

    recommendations = (
        build_recommendations(
            profile=profile,
            weaknesses=weaknesses,
            problems=problems,
        )
    )

    if recommendations.empty:
        print(
            "\nNo recommendations generated."
        )
        return

    # --------------------------------------------------------
    # Metadata enrichment
    # --------------------------------------------------------

    metadata = load_metadata()

    print(
        f"Loaded metadata rows: "
        f"{len(metadata)}"
    )

    recommendations = (
        enrich_recommendations(
            recommendations,
            metadata,
        )
    )

    # --------------------------------------------------------
    # Final ranking
    # --------------------------------------------------------

    recommendations = (
        recommendations
        .sort_values(
            "adaptive_score",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )

    # --------------------------------------------------------
    # Save CSV
    # --------------------------------------------------------

    save_csv(
        recommendations
    )

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    save_json(
        recommendations
    )

    # --------------------------------------------------------
    # Validate JSON immediately
    # --------------------------------------------------------

    validate_json_output()

    # --------------------------------------------------------
    # Console report
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "TOP ADAPTIVE RECOMMENDATIONS"
    )
    print("=" * 70)

    display_columns = [
        "problem_id",
        "title",
        "target_domain",
        "difficulty_score",
        "student_skill",
        "difficulty_fit",
        "adaptive_score",
    ]

    available_display = [
        column
        for column in display_columns
        if column in recommendations.columns
    ]

    print(
        recommendations[
            available_display
        ]
        .head(15)
        .to_string(
            index=False
        )
    )

    print()
    print(
        f"Saved CSV: "
        f"{OUTPUT_CSV}"
    )

    print(
        f"Saved JSON: "
        f"{OUTPUT_JSON}"
    )

    print()
    print("=" * 70)
    print(
        "ADAPTIVE RECOMMENDATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()