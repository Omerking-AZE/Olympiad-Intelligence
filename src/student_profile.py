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


def create_student_profile():
    return {
        "student_id": None,
        "student_name": None,
        "problems_attempted": 0,
        "problems_solved": 0,
        "overall_rating": 0,
        "algebra": 0,
        "geometry": 0,
        "number_theory": 0,
        "discrete_mathematics": 0,
        "proof": 0,
        "reasoning": 0,
        "calculation": 0,
        "case_analysis": 0,
    }


def calculate_rating(values):
    valid_values = [
        value for value in values
        if value is not None
    ]

    if not valid_values:
        return 0

    return round(sum(valid_values) / len(valid_values))


def rating_tier(rating):
    if rating >= 90:
        return "Elite"
    elif rating >= 80:
        return "Advanced"
    elif rating >= 70:
        return "Strong"
    elif rating >= 60:
        return "Developing"
    else:
        return "Beginner"


def analyze_strengths(profile):
    categories = {
        "Algebra": profile["algebra"],
        "Geometry": profile["geometry"],
        "Number Theory": profile["number_theory"],
        "Discrete Mathematics": profile["discrete_mathematics"],
        "Proof": profile["proof"],
        "Reasoning": profile["reasoning"],
        "Calculation": profile["calculation"],
        "Case Analysis": profile["case_analysis"],
    }

    ranked = sorted(
        categories.items(),
        key=lambda x: x[1],
        reverse=True
    )

    strengths = ranked[:3]
    weaknesses = ranked[-3:]

    return strengths, weaknesses


if __name__ == "__main__":

    profile = create_student_profile()

    profile.update({
        "algebra": 91,
        "geometry": 84,
        "number_theory": 88,
        "discrete_mathematics": 79,
        "proof": 92,
        "reasoning": 89,
        "calculation": 76,
        "case_analysis": 81,
    })

    ratings = [
        profile["algebra"],
        profile["geometry"],
        profile["number_theory"],
        profile["discrete_mathematics"],
        profile["proof"],
        profile["reasoning"],
        profile["calculation"],
        profile["case_analysis"],
    ]

    overall = calculate_rating(ratings)

    profile["overall_rating"] = overall

    strengths, weaknesses = analyze_strengths(profile)

    print("=" * 70)
    print("OLYMPIAD INTELLIGENCE - STUDENT PROFILE")
    print("=" * 70)

    for key, value in profile.items():
        print(f"{key}: {value}")

    print()
    print("Overall Rating:", overall)
    print("Tier:", rating_tier(overall))

    print()
    print("STRONGEST AREAS")

    for name, score in strengths:
        print(f"{name}: {score}")

    print()
    print("AREAS TO IMPROVE")

    for name, score in weaknesses:
        print(f"{name}: {score}")