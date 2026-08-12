"""
OLYMPIAD INTELLIGENCE
Dynamic Student Profile Update

Day 10 - Step 3

Reads the student's problem-solving history and
rebuilds the student profile automatically.

Flow:

student_history.json
        ↓
skill performance
        ↓
student rating engine
        ↓
student_profile.json
"""

import json
from pathlib import Path

from student_rating import (
    StudentRatingInput,
    calculate_student_ovr,
    get_rating_tier,
)


HISTORY_PATH = Path(
    "data/processed/student_history.json"
)

PROFILE_PATH = Path(
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


def load_history():

    if not HISTORY_PATH.exists():

        raise FileNotFoundError(
            "student_history.json not found.\n"
            "Run:\n"
            "python src/student_history.py"
        )

    with open(
        HISTORY_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def average(values):

    if not values:
        return 0

    return round(
        sum(values) / len(values)
    )


def calculate_profile_from_history(
    history
):
    """
    Build skill ratings directly from
    historical problem attempts.
    """

    if not history:
        raise ValueError(
            "Student history is empty."
        )

    # --------------------------------------------------------
    # Domain performance
    # --------------------------------------------------------

    domain_scores = {
        "algebra": [],
        "geometry": [],
        "number_theory": [],
        "discrete_mathematics": [],
    }

    # --------------------------------------------------------
    # Reasoning-style features
    # --------------------------------------------------------

    proof_scores = []
    reasoning_scores = []
    calculation_scores = []
    case_scores = []

    solved_count = 0

    # --------------------------------------------------------
    # Hard-problem performance
    # --------------------------------------------------------

    hard_attempts = []
    hard_solved = 0

    for attempt in history:

        solved = bool(
            attempt.get(
                "solved",
                False
            )
        )

        if solved:
            solved_count += 1

        # -------------------------------
        # Domain
        # -------------------------------

        domain = DOMAIN_MAP.get(
            attempt.get(
                "domain"
            )
        )

        if domain is not None:

            domain_scores[
                domain
            ].append(
                float(
                    attempt.get(
                        "score",
                        0
                    )
                )
            )

        # -------------------------------
        # Solution characteristics
        # -------------------------------

        for source_key, target_list in [

            (
                "proof_score",
                proof_scores
            ),

            (
                "reasoning_score",
                reasoning_scores
            ),

            (
                "calculation_score",
                calculation_scores
            ),

            (
                "case_analysis_score",
                case_scores
            ),
        ]:

            value = attempt.get(
                source_key
            )

            if value is not None:
                target_list.append(
                    float(value)
                )

        # -------------------------------
        # Hard problems
        # -------------------------------

        difficulty = float(
            attempt.get(
                "difficulty",
                0
            )
        )

        if difficulty >= 70:

            hard_attempts.append(
                attempt
            )

            if solved:
                hard_solved += 1

    # --------------------------------------------------------
    # Profile
    # --------------------------------------------------------

    profile = {

        "student_id": "TEST-001",

        "student_name": "Test Student",

        "problems_attempted": len(
            history
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

    # --------------------------------------------------------
    # Skill confidence
    # --------------------------------------------------------

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

    profile[
        "skill_confidence"
    ] = {}

    for skill in SKILLS:

        count = skill_counts[skill]

        profile[
            "skill_confidence"
        ][skill] = min(
            count / 20,
            1.0
        )

    # --------------------------------------------------------
    # Measured skill average
    # --------------------------------------------------------

    measured_values = [
        profile[skill]
        for skill in SKILLS
        if profile[skill] > 0
    ]

    profile[
        "measured_skill_average"
    ] = average(
        measured_values
    )

    # --------------------------------------------------------
    # Hard-problem success
    # --------------------------------------------------------

    if hard_attempts:

        profile[
            "hard_problem_success"
        ] = round(
            hard_solved
            /
            len(hard_attempts)
            * 100,
            2
        )

    else:

        profile[
            "hard_problem_success"
        ] = 0

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    profile[
        "olympiad_experience"
    ] = min(
        len(history) / 2,
        100
    )

    # --------------------------------------------------------
    # Preserve achievement information
    # --------------------------------------------------------

    old_profile = {}

    if PROFILE_PATH.exists():

        with open(
            PROFILE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            old_profile = json.load(file)

    profile[
        "achievement_level"
    ] = old_profile.get(
        "achievement_level",
        0
    )

    profile[
        "achievement"
    ] = old_profile.get(
        "achievement",
        "NONE"
    )

    profile[
        "special_event_winner"
    ] = old_profile.get(
        "special_event_winner",
        False
    )

    # --------------------------------------------------------
    # Rating engine
    # --------------------------------------------------------

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

    rating = calculate_student_ovr(
        rating_input
    )

    profile[
        "overall_rating"
    ] = rating[
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
            rating[
                "effective_skill"
            ],

        "experience_score":
            rating[
                "experience_score"
            ],

        "consistency_score":
            rating[
                "consistency_score"
            ],

        "hard_problem_success":
            rating[
                "hard_problem_success"
            ],

        "data_confidence":
            rating[
                "data_confidence"
            ],
    }

    return profile


def save_profile(profile):

    PROFILE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        PROFILE_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False
        )


def print_profile(profile):

    print("=" * 70)

    print(
        "OLYMPIAD INTELLIGENCE - "
        "DYNAMIC PROFILE UPDATE"
    )

    print("=" * 70)

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

        confidence = (
            profile[
                "skill_confidence"
            ][skill]
        )

        print(
            f"{skill:<24}: "
            f"{profile[skill]:>3} "
            f"({confidence:.0%})"
        )

    print()

    print("PERFORMANCE")
    print("-" * 50)

    print(
        f"Measured Skill Average: "
        f"{profile['measured_skill_average']}"
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

    print()

    print("PLAYER RATING")
    print("-" * 50)

    print(
        f"OVR:  "
        f"{profile['overall_rating']}"
    )

    print(
        f"TIER: "
        f"{profile['tier']}"
    )

    print()

    print(
        f"Achievement: "
        f"{profile['achievement']}"
    )

    print()

    print(
        f"Saved: {PROFILE_PATH}"
    )

    print()

    print("=" * 70)

    print(
        "DYNAMIC PROFILE UPDATE COMPLETE"
    )

    print("=" * 70)


def main():

    history = load_history()

    profile = calculate_profile_from_history(
        history
    )

    save_profile(
        profile
    )

    print_profile(
        profile
    )


if __name__ == "__main__":
    main()