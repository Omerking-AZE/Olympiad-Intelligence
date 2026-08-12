"""
OLYMPIAD INTELLIGENCE
Student Progression Simulation

Simulates how a student's:
- skill ratings
- OVR
- experience
- consistency

change as more olympiad problems are solved.
"""

import copy
import json
from pathlib import Path

from student_rating import (
    StudentRatingInput,
    calculate_student_ovr,
    get_rating_tier,
)


OUTPUT_PATH = Path(
    "data/processed/student_progression.json"
)


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

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        2
    )


def calculate_profile_at_stage(
    attempts,
    stage_history
):
    """
    Calculate profile metrics for a specific
    point in the student's history.
    """

    if not stage_history:
        return None

    domain_scores = {
        skill: []
        for skill in [
            "algebra",
            "geometry",
            "number_theory",
            "discrete_mathematics",
        ]
    }

    proof = []
    reasoning = []
    calculation = []
    case_analysis = []

    solved = 0
    hard_attempts = 0
    hard_solved = 0

    domain_map = {
        "Algebra": "algebra",
        "Geometry": "geometry",
        "Number Theory": "number_theory",
        "Discrete Mathematics":
            "discrete_mathematics",
    }

    for problem in stage_history:

        domain = domain_map.get(
            problem["domain"]
        )

        if domain:

            domain_scores[
                domain
            ].append(
                problem["score"]
            )

        proof.append(
            problem.get(
                "proof_score",
                0
            )
        )

        reasoning.append(
            problem.get(
                "reasoning_score",
                0
            )
        )

        calculation.append(
            problem.get(
                "calculation_score",
                0
            )
        )

        case_analysis.append(
            problem.get(
                "case_analysis_score",
                0
            )
        )

        if problem["solved"]:
            solved += 1

        if problem["difficulty"] >= 70:

            hard_attempts += 1

            if problem["solved"]:
                hard_solved += 1

    skill_values = []

    skills = {}

    for skill in SKILLS:

        if skill in domain_scores:

            value = average(
                domain_scores[skill]
            )

        elif skill == "proof":

            value = average(proof)

        elif skill == "reasoning":

            value = average(reasoning)

        elif skill == "calculation":

            value = average(calculation)

        elif skill == "case_analysis":

            value = average(case_analysis)

        else:

            value = 0

        skills[skill] = value

        if value > 0:
            skill_values.append(value)

    measured_skill_average = average(
        skill_values
    )

    hard_success = (
        hard_solved
        / hard_attempts
        * 100
        if hard_attempts
        else 0
    )

    experience = min(
        attempts / 2,
        100
    )

    rating_input = StudentRatingInput(
        skill_average=measured_skill_average,
        problems_attempted=attempts,
        problems_solved=solved,
        hard_problem_success=hard_success,
        olympiad_experience=experience,
        achievement_level=0,
        special_event_winner=False,
    )

    rating = calculate_student_ovr(
        rating_input
    )

    return {
        "attempts": attempts,
        "solved": solved,
        "success_rate": round(
            solved / attempts * 100,
            2
        ),
        "measured_skill_average":
            measured_skill_average,
        "hard_problem_success":
            round(
                hard_success,
                2
            ),
        "experience_score":
            rating[
                "experience_score"
            ],
        "overall_rating":
            rating[
                "overall_rating"
            ],
        "tier":
            get_rating_tier(
                rating[
                    "overall_rating"
                ]
            ),
        "skills": skills,
    }


def create_simulation_history():
    """
    Build a realistic synthetic progression.

    The data is only for testing the rating engine.
    """

    return [

        {
            "problem_id": "SIM-001",
            "domain": "Algebra",
            "difficulty": 48,
            "solved": True,
            "score": 68,
            "proof_score": 60,
            "reasoning_score": 65,
            "calculation_score": 72,
            "case_analysis_score": 55,
        },

        {
            "problem_id": "SIM-002",
            "domain": "Geometry",
            "difficulty": 52,
            "solved": True,
            "score": 70,
            "proof_score": 68,
            "reasoning_score": 67,
            "calculation_score": 64,
            "case_analysis_score": 70,
        },

        {
            "problem_id": "SIM-003",
            "domain": "Number Theory",
            "difficulty": 55,
            "solved": False,
            "score": 45,
            "proof_score": 40,
            "reasoning_score": 48,
            "calculation_score": 55,
            "case_analysis_score": 42,
        },

        {
            "problem_id": "SIM-004",
            "domain": "Algebra",
            "difficulty": 58,
            "solved": True,
            "score": 74,
            "proof_score": 70,
            "reasoning_score": 72,
            "calculation_score": 78,
            "case_analysis_score": 62,
        },

        {
            "problem_id": "SIM-005",
            "domain": "Geometry",
            "difficulty": 62,
            "solved": True,
            "score": 76,
            "proof_score": 74,
            "reasoning_score": 75,
            "calculation_score": 68,
            "case_analysis_score": 72,
        },

        {
            "problem_id": "SIM-006",
            "domain": "Number Theory",
            "difficulty": 65,
            "solved": True,
            "score": 68,
            "proof_score": 65,
            "reasoning_score": 70,
            "calculation_score": 66,
            "case_analysis_score": 60,
        },

        {
            "problem_id": "SIM-007",
            "domain": "Discrete Mathematics",
            "difficulty": 60,
            "solved": True,
            "score": 72,
            "proof_score": 69,
            "reasoning_score": 74,
            "calculation_score": 63,
            "case_analysis_score": 67,
        },

        {
            "problem_id": "SIM-008",
            "domain": "Algebra",
            "difficulty": 70,
            "solved": True,
            "score": 80,
            "proof_score": 77,
            "reasoning_score": 79,
            "calculation_score": 82,
            "case_analysis_score": 71,
        },

        {
            "problem_id": "SIM-009",
            "domain": "Geometry",
            "difficulty": 74,
            "solved": True,
            "score": 82,
            "proof_score": 80,
            "reasoning_score": 84,
            "calculation_score": 76,
            "case_analysis_score": 79,
        },

        {
            "problem_id": "SIM-010",
            "domain": "Number Theory",
            "difficulty": 72,
            "solved": False,
            "score": 58,
            "proof_score": 55,
            "reasoning_score": 62,
            "calculation_score": 60,
            "case_analysis_score": 52,
        },

        {
            "problem_id": "SIM-011",
            "domain": "Discrete Mathematics",
            "difficulty": 68,
            "solved": True,
            "score": 78,
            "proof_score": 76,
            "reasoning_score": 81,
            "calculation_score": 70,
            "case_analysis_score": 74,
        },

        {
            "problem_id": "SIM-012",
            "domain": "Algebra",
            "difficulty": 76,
            "solved": True,
            "score": 84,
            "proof_score": 82,
            "reasoning_score": 85,
            "calculation_score": 86,
            "case_analysis_score": 78,
        },
    ]


def main():

    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "STUDENT PROGRESSION SIMULATION"
    )
    print("=" * 70)

    history = create_simulation_history()

    stages = [
        3,
        6,
        9,
        12,
    ]

    progression = []

    print()

    for stage in stages:

        result = calculate_profile_at_stage(
            attempts=stage,
            stage_history=history[:stage]
        )

        progression.append(
            result
        )

        print(
            f"{stage:>3} problems | "
            f"OVR {result['overall_rating']:>2} | "
            f"{result['tier']:<32} | "
            f"Success {result['success_rate']:>5.1f}%"
        )

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
            progression,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()

    print(
        f"Saved: {OUTPUT_PATH}"
    )

    print()

    print("=" * 70)
    print(
        "PROGRESSION SIMULATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()