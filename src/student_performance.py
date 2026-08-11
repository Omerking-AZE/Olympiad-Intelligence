import json
from pathlib import Path


SKILLS = [
    "algebra",
    "geometry",
    "number_theory",
    "discrete_mathematics",
    "proof",
    "reasoning",
    "calculation",
    "case_analysis",
]


def calculate_average(values):
    valid_values = [
        value for value in values
        if value is not None and value > 0
    ]

    if not valid_values:
        return 0

    return round(sum(valid_values) / len(valid_values))


def calculate_overall_rating(profile):
    ratings = [
        profile[skill]
        for skill in SKILLS
        if profile.get(skill, 0) > 0
    ]

    return calculate_average(ratings)


def get_tier(rating):
    if rating >= 90:
        return "Elite"
    elif rating >= 80:
        return "Advanced"
    elif rating >= 70:
        return "Intermediate"
    elif rating >= 60:
        return "Developing"
    return "Beginner"


def get_strongest_areas(profile, count=3):
    values = {
        skill: profile.get(skill, 0)
        for skill in SKILLS
        if profile.get(skill, 0) > 0
    }

    return sorted(
        values.items(),
        key=lambda item: item[1],
        reverse=True
    )[:count]


def get_areas_to_improve(profile, count=3):
    values = {
        skill: profile.get(skill, 0)
        for skill in SKILLS
        if profile.get(skill, 0) > 0
    }

    return sorted(
        values.items(),
        key=lambda item: item[1]
    )[:count]


def create_student_profile(
    student_id="TEST-001",
    student_name="Test Student",
    problems_attempted=10,
    problems_solved=8,
    skill_ratings=None
):
    if skill_ratings is None:
        skill_ratings = {
            "algebra": 91,
            "geometry": 84,
            "number_theory": 88,
            "discrete_mathematics": 79,
            "proof": 92,
            "reasoning": 89,
            "calculation": 76,
            "case_analysis": 81,
        }

    profile = {
        "student_id": student_id,
        "student_name": student_name,
        "problems_attempted": problems_attempted,
        "problems_solved": problems_solved,
    }

    for skill in SKILLS:
        profile[skill] = skill_ratings.get(skill, 0)

    profile["overall_rating"] = calculate_overall_rating(profile)
    profile["tier"] = get_tier(profile["overall_rating"])

    return profile


def save_profile(profile, output_path="data/processed/student_profile.json"):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4)

    print(f"\nProfile saved to: {path}")


def print_profile(profile):

    strongest = get_strongest_areas(profile)
    improvement = get_areas_to_improve(profile)

    print()
    print("=" * 70)
    print("OLYMPIAD INTELLIGENCE - STUDENT PROFILE")
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

    print(f"Rating: {profile['overall_rating']}")
    print(f"Tier:   {profile['tier']}")

    print()
    print("## OLYMPIAD SKILLS")
    print()

    for skill in SKILLS:
        display_name = skill.replace("_", " ").title()
        print(f"{display_name:<24}: {profile[skill]}")

    print()
    print("## STRONGEST AREAS")
    print()

    for skill, value in strongest:
        display_name = skill.replace("_", " ").title()
        print(f"{display_name}: {value}")

    print()
    print("## AREAS TO IMPROVE")
    print()

    for skill, value in improvement:
        display_name = skill.replace("_", " ").title()
        print(f"{display_name}: {value}")

    print()
    print("=" * 70)


if __name__ == "__main__":

    profile = create_student_profile()

    print_profile(profile)

    save_profile(profile)