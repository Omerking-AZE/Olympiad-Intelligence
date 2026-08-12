"""
OLYMPIAD INTELLIGENCE
Adaptive Problem Recommendation Engine

Rules:

- Weak measured skills are prioritized.
- Unknown skills display as 0 on the card.
- Unknown skills use neutral 55 for recommendations.
- Problems slightly above the student's level are preferred.
- Recommendation never changes OVR.
"""

import json
from pathlib import Path

import pandas as pd


PROFILE_PATH = Path(
    "data/processed/student_profile.json"
)

PROBLEMS_PATH = Path(
    "data/processed/mathnet_difficulty.csv"
)

OUTPUT_PATH = Path(
    "data/processed/recommended_problems.csv"
)


DOMAIN_MAP = {
    "Algebra": "algebra",
    "Geometry": "geometry",
    "Number Theory": "number_theory",
    "Discrete Mathematics": "discrete_mathematics",
}


NEUTRAL_RATING = 55


def load_profile():

    if not PROFILE_PATH.exists():

        raise FileNotFoundError(
            "student_profile.json not found.\n"
            "Run:\n"
            "python src/build_student_profile.py"
        )

    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def load_problems():

    if not PROBLEMS_PATH.exists():

        raise FileNotFoundError(
            "mathnet_difficulty.csv not found."
        )

    return pd.read_csv(
        PROBLEMS_PATH
    )


def get_recommendation_skill(
    profile,
    skill_key
):

    displayed_skill = profile.get(
        skill_key,
        0
    )

    if displayed_skill > 0:

        return (
            displayed_skill,
            False
        )

    return (
        NEUTRAL_RATING,
        True
    )


def difficulty_fit(
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


def weakness_priority(
    skill
):

    return 100 - skill


def recommendation_score(
    difficulty,
    skill
):

    weakness = weakness_priority(
        skill
    )

    difficulty_score = difficulty_fit(
        difficulty,
        skill
    )

    return round(
        weakness * 0.55
        +
        difficulty_score * 0.45,
        2
    )


def recommend_for_domain(
    problems,
    domain_name,
    recommendation_skill,
    displayed_skill,
    unknown,
    count=3
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

    domain_problems[
        "student_skill"
    ] = displayed_skill

    domain_problems[
        "recommendation_skill"
    ] = recommendation_skill

    domain_problems[
        "skill_unknown"
    ] = unknown

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
        "recommendation_score"
    ] = domain_problems[
        "difficulty_score"
    ].apply(
        lambda difficulty:
            recommendation_score(
                difficulty,
                recommendation_skill
            )
    )

    domain_problems[
        "target_domain"
    ] = domain_name

    # Preferred training zone:
    # 3 to 10 points above current level.
    domain_problems[
        "training_zone"
    ] = (
        (domain_problems[
            "difficulty_gap"
        ] >= 3)
        &
        (domain_problems[
            "difficulty_gap"
        ] <= 10)
    )

    domain_problems = (
        domain_problems
        .sort_values(
            [
                "training_zone",
                "recommendation_score"
            ],
            ascending=[
                False,
                False
            ]
        )
        .head(count)
    )

    return domain_problems


def recommend_problems(
    profile,
    problems
):

    results = []

    domains = sorted(
        DOMAIN_MAP.items(),
        key=lambda item:
            profile.get(
                item[1],
                0
            )
    )

    for domain_name, skill_key in domains:

        displayed_skill = profile.get(
            skill_key,
            0
        )

        recommendation_skill, unknown = (
            get_recommendation_skill(
                profile,
                skill_key
            )
        )

        selected = recommend_for_domain(
            problems=problems,
            domain_name=domain_name,
            recommendation_skill=(
                recommendation_skill
            ),
            displayed_skill=displayed_skill,
            unknown=unknown,
            count=3
        )

        if not selected.empty:

            results.append(
                selected
            )

    if not results:

        return pd.DataFrame()

    return pd.concat(
        results,
        ignore_index=True
    )


def main():

    print("=" * 70)

    print(
        "OLYMPIAD INTELLIGENCE - "
        "ADAPTIVE RECOMMENDATIONS"
    )

    print("=" * 70)

    profile = load_profile()

    problems = load_problems()

    print()

    print(
        f"Student: "
        f"{profile['student_name']}"
    )

    print(
        f"OVR: "
        f"{profile['overall_rating']}"
    )

    print()

    print("SKILL PROFILE")
    print("-" * 60)

    for domain_name, skill_key in DOMAIN_MAP.items():

        print(
            f"{domain_name:<24}: "
            f"{profile.get(skill_key, 0)}"
        )

    recommendations = recommend_problems(
        profile,
        problems
    )

    if recommendations.empty:

        print(
            "\nNo recommendations available."
        )

        return

    columns = [
        "problem_id",
        "target_domain",
        "difficulty_score",
        "student_skill",
        "recommendation_skill",
        "difficulty_gap",
        "recommendation_score",
        "training_zone",
        "skill_unknown",
        "problem_type",
    ]

    columns = [
        column
        for column in columns
        if column in recommendations.columns
    ]

    recommendations = recommendations[
        columns
    ]

    recommendations.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()

    print(
        "TOP RECOMMENDATIONS"
    )

    print("-" * 100)

    print(
        recommendations
        .head(12)
        .to_string(
            index=False
        )
    )

    print()

    print(
        f"Saved: {OUTPUT_PATH}"
    )

    print()

    print("=" * 70)

    print(
        "RECOMMENDATION COMPLETE"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()