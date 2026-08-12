"""
OLYMPIAD INTELLIGENCE
Automatic Student Profile Builder

Builds:
- Mathematical skill ratings
- Skill confidence
- Difficulty performance
- Experience
- Achievement information
- Final 50-99 OVR
"""

import json
from pathlib import Path

from student_performance import PROBLEMS

from student_rating import (
    StudentRatingInput,
    calculate_student_ovr,
    get_rating_tier,
)


OUTPUT_PATH = Path(
    "data/processed/student_profile.json"
)


DOMAIN_MAP = {
    "Algebra": "algebra",
    "Geometry": "geometry",
    "Number Theory": "number_theory",
    "Discrete Mathematics": "discrete_mathematics",
}


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


def average(values):

    valid = [
        value
        for value in values
        if value is not None
    ]

    if not valid:
        return 0

    return round(
        sum(valid) / len(valid)
    )


def calculate_skill_confidence(
    count
):

    if count <= 0:
        return 0.0

    return min(
        count / 20,
        1.0
    )


def get_tier_from_achievement(
    achievement_level
):

    names = {
        0: "NONE",
        1: "PARTICIPATION",
        2: "NATIONAL BRONZE",
        3: "NATIONAL SILVER",
        4: "NATIONAL GOLD",
        5: "INTERNATIONAL BRONZE",
        6: "INTERNATIONAL SILVER",
        7: "INTERNATIONAL GOLD",
    }

    return names.get(
        achievement_level,
        "NONE"
    )


def build_profile(
    problems,
    student_id="TEST-001",
    student_name="Test Student",
    achievement_level=0,
    special_event_winner=False
):

    domain_scores = {
        "algebra": [],
        "geometry": [],
        "number_theory": [],
        "discrete_mathematics": [],
    }

    proof_scores = []
    reasoning_scores = []
    calculation_scores = []
    case_scores = []

    solved_count = 0

    for problem in problems:

        if problem["solved"]:
            solved_count += 1

        domain_key = DOMAIN_MAP.get(
            problem["domain"]
        )

        if domain_key is not None:

            domain_scores[
                domain_key
            ].append(
                problem["score"]
            )

        proof_scores.append(
            problem["proof"]
        )

        reasoning_scores.append(
            problem["reasoning"]
        )

        calculation_scores.append(
            problem["calculation"]
        )

        case_scores.append(
            problem["case"]
        )

    profile = {

        "student_id": student_id,

        "student_name": student_name,

        "problems_attempted": len(
            problems
        ),

        "problems_solved": solved_count,

        "algebra": average(
            domain_scores["algebra"]
        ),

        "geometry": average(
            domain_scores["geometry"]
        ),

        "number_theory": average(
            domain_scores["number_theory"]
        ),

        "discrete_mathematics": average(
            domain_scores[
                "discrete_mathematics"
            ]
        ),

        "proof": average(
            proof_scores
        ),

        "reasoning": average(
            reasoning_scores
        ),

        "calculation": average(
            calculation_scores
        ),

        "case_analysis": average(
            case_scores
        ),
    }

    # ========================================================
    # CONFIDENCE
    # ========================================================

    skill_confidence = {}

    skill_counts = {

        "algebra": len(
            domain_scores["algebra"]
        ),

        "geometry": len(
            domain_scores["geometry"]
        ),

        "number_theory": len(
            domain_scores["number_theory"]
        ),

        "discrete_mathematics": len(
            domain_scores[
                "discrete_mathematics"
            ]
        ),

        "proof": len(
            proof_scores
        ),

        "reasoning": len(
            reasoning_scores
        ),

        "calculation": len(
            calculation_scores
        ),

        "case_analysis": len(
            case_scores
        ),
    }

    for skill in SKILLS:

        skill_confidence[skill] = (
            calculate_skill_confidence(
                skill_counts[skill]
            )
        )

    profile[
        "skill_confidence"
    ] = skill_confidence

    # ========================================================
    # MEASURED SKILL AVERAGE
    # ========================================================

    measured_skills = [
        profile[skill]
        for skill in SKILLS
        if profile[skill] > 0
    ]

    profile[
        "measured_skill_average"
    ] = average(
        measured_skills
    )

    # ========================================================
    # HARD PROBLEM PERFORMANCE
    # ========================================================

    hard_problems = [

        problem
        for problem in problems
        if problem["difficulty"] >= 70

    ]

    if hard_problems:

        hard_solved = sum(
            problem["solved"]
            for problem in hard_problems
        )

        hard_problem_success = (
            hard_solved
            /
            len(hard_problems)
            *
            100
        )

    else:

        hard_problem_success = 0

    profile[
        "hard_problem_success"
    ] = round(
        hard_problem_success,
        2
    )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    profile[
        "olympiad_experience"
    ] = min(
        len(problems) / 2,
        100
    )

    # ========================================================
    # ACHIEVEMENT
    # ========================================================

    profile[
        "achievement_level"
    ] = achievement_level

    profile[
        "achievement"
    ] = get_tier_from_achievement(
        achievement_level
    )

    profile[
        "special_event_winner"
    ] = special_event_winner

    # ========================================================
    # RATING ENGINE
    # ========================================================

    rating_input = StudentRatingInput(

        skill_average=profile[
            "measured_skill_average"
        ],

        problems_attempted=profile[
            "problems_attempted"
        ],

        problems_solved=profile[
            "problems_solved"
        ],

        hard_problem_success=profile[
            "hard_problem_success"
        ],

        olympiad_experience=profile[
            "olympiad_experience"
        ],

        achievement_level=profile[
            "achievement_level"
        ],

        special_event_winner=profile[
            "special_event_winner"
        ],
    )

    rating_result = calculate_student_ovr(
        rating_input
    )

    profile[
        "overall_rating"
    ] = rating_result[
        "overall_rating"
    ]

    profile[
        "tier"
    ] = get_rating_tier(
        profile[
            "overall_rating"
        ]
    )

    profile[
        "rating_components"
    ] = {

        "effective_skill":
            rating_result[
                "effective_skill"
            ],

        "experience_score":
            rating_result[
                "experience_score"
            ],

        "consistency_score":
            rating_result[
                "consistency_score"
            ],

        "hard_problem_success":
            rating_result[
                "hard_problem_success"
            ],

        "data_confidence":
            rating_result[
                "data_confidence"
            ],
    }

    return profile


def save_profile(
    profile
):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    print("=" * 70)

    print(
        "OLYMPIAD INTELLIGENCE - "
        "STUDENT RATING PROFILE"
    )

    print("=" * 70)

    profile = build_profile(
        PROBLEMS
    )

    print()

    print(
        f"Student: "
        f"{profile['student_name']}"
    )

    print(
        f"Problems: "
        f"{profile['problems_solved']}/"
        f"{profile['problems_attempted']}"
    )

    print()

    print("SKILLS")
    print("-" * 50)

    for skill in SKILLS:

        print(
            f"{skill:<24}: "
            f"{profile[skill]}"
        )

    print()

    print("CONFIDENCE")
    print("-" * 50)

    for skill in SKILLS:

        confidence = (
            profile[
                "skill_confidence"
            ][skill]
        )

        print(
            f"{skill:<24}: "
            f"{confidence:.0%}"
        )

    print()

    print("RATING")
    print("-" * 50)

    print(
        f"Measured Skill Average: "
        f"{profile['measured_skill_average']}"
    )

    print(
        f"Effective Skill: "
        f"{profile['rating_components']['effective_skill']}"
    )

    print(
        f"Hard Problem Success: "
        f"{profile['hard_problem_success']}%"
    )

    print(
        f"Experience Score: "
        f"{profile['rating_components']['experience_score']}"
    )

    print(
        f"Consistency Score: "
        f"{profile['rating_components']['consistency_score']}"
    )

    print(
        f"Achievement: "
        f"{profile['achievement']}"
    )

    print()

    print(
        f"OVR: "
        f"{profile['overall_rating']}"
    )

    print(
        f"TIER: "
        f"{profile['tier']}"
    )

    save_profile(
        profile
    )

    print()

    print(
        f"Saved: {OUTPUT_PATH}"
    )

    print()

    print("=" * 70)

    print(
        "STUDENT RATING PROFILE COMPLETE"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()