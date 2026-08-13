"""
OLYMPIAD INTELLIGENCE
Adaptive Recommendation Engine

Exports recommendations as:
- CSV for analysis
- JSON for the web dashboard
"""

import json
from pathlib import Path

import pandas as pd


PROFILE_PATH = Path(
    "data/processed/student_profile.json"
)

WEAKNESS_PATH = Path(
    "data/processed/student_weaknesses.json"
)

PROBLEMS_PATH = Path(
    "data/processed/mathnet_difficulty.csv"
)

OUTPUT_CSV = Path(
    "data/processed/adaptive_recommendations.csv"
)

OUTPUT_JSON = Path(
    "data/processed/adaptive_recommendations.json"
)


DOMAIN_MAP = {
    "Algebra": "algebra",
    "Geometry": "geometry",
    "Number Theory": "number_theory",
    "Discrete Mathematics": "discrete_mathematics",
}


NEUTRAL_SKILL = 55


def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def calculate_difficulty_fit(
    difficulty,
    skill
):

    target = skill + 6

    distance = abs(
        difficulty - target
    )

    return max(
        0,
        50 - distance * 2
    )


def calculate_adaptive_score(
    difficulty,
    skill,
    weakness_priority
):

    difficulty_score = (
        calculate_difficulty_fit(
            difficulty,
            skill
        )
    )

    score = (
        weakness_priority * 0.60
        +
        difficulty_score * 0.40
    )

    return round(
        score,
        2
    )


def recommend_domain(
    problems,
    domain_name,
    skill,
    weakness_priority,
    skill_unknown,
    count=5
):

    domain_problems = problems[
        problems["domain"]
        .astype(str)
        .str.contains(
            domain_name,
            case=False,
            na=False
        )
    ].copy()

    if domain_problems.empty:
        return pd.DataFrame()

    recommendation_skill = (
        NEUTRAL_SKILL
        if skill_unknown
        else skill
    )

    domain_problems[
        "student_skill"
    ] = skill

    domain_problems[
        "recommendation_skill"
    ] = recommendation_skill

    domain_problems[
        "weakness_priority"
    ] = weakness_priority

    domain_problems[
        "skill_unknown"
    ] = skill_unknown

    domain_problems[
        "difficulty_gap"
    ] = (
        domain_problems[
            "difficulty_score"
        ]
        -
        recommendation_skill
    )

    domain_problems[
        "difficulty_fit"
    ] = domain_problems[
        "difficulty_score"
    ].apply(
        lambda difficulty:
            calculate_difficulty_fit(
                difficulty,
                recommendation_skill
            )
    )

    domain_problems[
        "adaptive_score"
    ] = domain_problems[
        "difficulty_score"
    ].apply(
        lambda difficulty:
            calculate_adaptive_score(
                difficulty,
                recommendation_skill,
                weakness_priority
            )
    )

    domain_problems[
        "target_domain"
    ] = domain_name

    domain_problems[
        "training_zone"
    ] = (
        (domain_problems["difficulty_gap"] >= 3)
        &
        (domain_problems["difficulty_gap"] <= 10)
    )

    return (
        domain_problems
        .sort_values(
            [
                "training_zone",
                "adaptive_score"
            ],
            ascending=[
                False,
                False
            ]
        )
        .head(count)
    )


def build_recommendations(
    profile,
    weaknesses,
    problems
):

    results = []

    for domain_name, skill_key in DOMAIN_MAP.items():

        rating = profile.get(
            skill_key,
            0
        )

        weakness = weaknesses.get(
            skill_key,
            {}
        )

        priority = weakness.get(
            "priority",
            0
        )

        classification = weakness.get(
            "classification",
            "NONE"
        )

        confidence = weakness.get(
            "confidence",
            0
        )

        skill_unknown = (
            classification == "NOT_ENOUGH_DATA"
            or rating == 0
        )

        if skill_unknown:
            recommendation_priority = 20
        else:
            recommendation_priority = priority

        selected = recommend_domain(
            problems=problems,
            domain_name=domain_name,
            skill=rating,
            weakness_priority=recommendation_priority,
            skill_unknown=skill_unknown,
            count=5
        )

        if selected.empty:
            continue

        selected[
            "weakness_classification"
        ] = classification

        selected[
            "weakness_confidence"
        ] = confidence

        results.append(
            selected
        )

    if not results:
        return pd.DataFrame()

    result = pd.concat(
        results,
        ignore_index=True
    )

    return (
        result
        .sort_values(
            "adaptive_score",
            ascending=False
        )
        .reset_index(drop=True)
    )


def save_json(
    recommendations
):

    frontend_columns = [
        "problem_id",
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
    ]

    available = [
        column
        for column in frontend_columns
        if column in recommendations.columns
    ]

    data = recommendations[
        available
    ].head(15).to_dict(
        orient="records"
    )

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "ADAPTIVE RECOMMENDATIONS"
    )
    print("=" * 70)

    profile = load_json(
        PROFILE_PATH
    )

    weaknesses = load_json(
        WEAKNESS_PATH
    )

    problems = pd.read_csv(
        PROBLEMS_PATH
    )

    recommendations = build_recommendations(
        profile,
        weaknesses,
        problems
    )

    if recommendations.empty:

        print(
            "\nNo recommendations generated."
        )

        return

    recommendations.to_csv(
        OUTPUT_CSV,
        index=False
    )

    save_json(
        recommendations
    )

    print()
    print(
        "TOP ADAPTIVE RECOMMENDATIONS"
    )

    print("-" * 100)

    print(
        recommendations
        .head(15)
        .to_string(
            index=False
        )
    )

    print()
    print(
        f"Saved CSV:  {OUTPUT_CSV}"
    )

    print(
        f"Saved JSON: {OUTPUT_JSON}"
    )

    print()
    print("=" * 70)
    print(
        "ADAPTIVE RECOMMENDATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()