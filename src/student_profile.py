"""
OLYMPIAD INTELLIGENCE
Student Performance Profile

Day 9 final version.
Creates a student profile and saves it as JSON
for the visual student card system.
"""

import json
from pathlib import Path


PROFILE_FEATURES = [
    "algebra",
    "geometry",
    "number_theory",
    "discrete_mathematics",
    "proof",
    "reasoning",
    "calculation",
    "case_analysis",
]


def calculate_rating(values):
    """Calculate the average of valid rating values."""

    valid_values = [
        value for value in values
        if value is not None
    ]

    if not valid_values:
        return 0

    return round(sum(valid_values) / len(valid_values))


def get_tier(rating):
    """Convert overall rating into a student tier."""

    if rating >= 90:
        return "Elite"
    elif rating >= 80:
        return "Advanced"
    elif rating >= 70:
        return "Intermediate"
    elif rating >= 60:
        return "Developing"
    else:
        return "Beginner"


def create_student_profile(
    student_id=None,
    student_name=None,
    problems_attempted=0,
    problems_solved=0,
    ratings=None,
):
    """Create a complete student performance profile."""

    if ratings is None:
        ratings = {}

    profile = {
        "student_id": student_id,
        "student_name": student_name,
        "problems_attempted": problems_attempted,
        "problems_solved": problems_solved,
    }

    for feature in PROFILE_FEATURES:
        profile[feature] = ratings.get(feature, 0)

    feature_values = [
        profile[feature]
        for feature in PROFILE_FEATURES
        if profile[feature] is not None
    ]

    profile["overall_rating"] = calculate_rating(feature_values)
    profile["tier"] = get_tier(profile["overall_rating"])

    return profile


def get_strongest_areas(profile, count=3):
    """Return the strongest student areas."""

    areas = [
        (feature, profile.get(feature, 0))
        for feature in PROFILE_FEATURES
    ]

    areas.sort(key=lambda x: x[1], reverse=True)

    return areas[:count]


def get_areas_to_improve(profile, count=3):
    """Return the areas with the lowest ratings."""

    areas = [
        (feature, profile.get(feature, 0))
        for feature in PROFILE_FEATURES
    ]

    areas.sort(key=lambda x: x[1])

    return areas[:count]


def format_feature_name(feature):
    """Convert internal feature names into readable names."""

    return feature.replace("_", " ").title()


def save_profile(
    profile,
    output_path="data/processed/student_profile.json"
):
    """Save student profile as JSON."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False
        )

    return path


def print_profile(profile):
    """Display the complete student profile."""

    print()
    print("=" * 70)
    print("OLYMPIAD INTELLIGENCE - STUDENT PERFORMANCE PROFILE")
    print("=" * 70)

    print()

    print("## STUDENT")
    print()

    print(f"Student ID:          {profile['student_id']}")
    print(f"Student Name:        {profile['student_name']}")
    print(f"Problems Attempted:  {profile['problems_attempted']}")
    print(f"Problems Solved:     {profile['problems_solved']}")

    print()

    print("## OVERALL RATING")
    print()

    overall = profile["overall_rating"]

    print(f"Rating: {overall}")
    print(f"Tier:   {profile['tier']}")

    print()

    print("## OLYMPIAD SKILLS")
    print()

    for feature in PROFILE_FEATURES:

        name = format_feature_name(feature)
        value = profile[feature]

        print(f"{name:<25}: {value}")

    print()

    print("## STRONGEST AREAS")
    print()

    strongest = get_strongest_areas(profile)

    for feature, value in strongest:

        print(
            f"{format_feature_name(feature)}: {value}"
        )

    print()

    print("## AREAS TO IMPROVE")
    print()

    weakest = get_areas_to_improve(profile)

    for feature, value in weakest:

        print(
            f"{format_feature_name(feature)}: {value}"
        )

    print()

    print("=" * 70)


def run_test():

    ratings = {
        "algebra": 91,
        "geometry": 84,
        "number_theory": 88,
        "discrete_mathematics": 79,
        "proof": 92,
        "reasoning": 89,
        "calculation": 76,
        "case_analysis": 81,
    }

    profile = create_student_profile(
        student_id="TEST-001",
        student_name="Test Student",
        problems_attempted=10,
        problems_solved=8,
        ratings=ratings,
    )

    print_profile(profile)

    output_path = save_profile(profile)

    print()
    print(f"Profile saved to: {output_path}")


if __name__ == "__main__":
    run_test()