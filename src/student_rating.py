"""
OLYMPIAD INTELLIGENCE
Student Rating Engine

OVR is a 0-99 student ability rating.

Design principles:

50-59  -> Beginner
60-69  -> Developing
75-85  -> Experienced student
80-82  -> typical National Bronze range
82-86  -> typical National Silver range
86-90  -> typical National Gold / International Bronze range
90-93  -> typical International Silver range
94-97  -> typical International Gold range
98-99  -> extremely rare exceptional level

IMPORTANT:
Achievement does not automatically increase OVR.

A medal is evidence of achievement, but OVR primarily
represents demonstrated mathematical ability.

98-99 requires exceptional performance AND a large,
reliable history, with elite achievement or equivalent
mathematical evidence.
"""

from dataclasses import dataclass


MIN_OVR = 50
MAX_OVR = 99

NEUTRAL_SKILL = 55


@dataclass
class StudentRatingInput:

    skill_average: float

    problems_attempted: int

    problems_solved: int

    hard_problem_success: float = 0.0

    olympiad_experience: float = 0.0

    achievement_level: int = 0

    special_event_winner: bool = False


# ============================================================
# EXPERIENCE
# ============================================================

def calculate_experience_score(
    problems_attempted: int,
    olympiad_experience: float
):
    """
    Convert experience into a 0-100 score.

    The number of attempted problems is the main source
    of experience. External olympiad experience is a
    secondary signal.
    """

    problem_experience = min(
        problems_attempted / 100 * 100,
        100
    )

    experience_score = (
        problem_experience * 0.70
        +
        olympiad_experience * 0.30
    )

    return round(
        min(
            max(
                experience_score,
                0
            ),
            100
        ),
        2
    )


# ============================================================
# CONSISTENCY
# ============================================================

def calculate_consistency_score(
    problems_attempted: int,
    problems_solved: int
):
    """
    Calculate solve consistency.

    With little data, the result is pulled toward neutral.
    """

    if problems_attempted <= 0:
        return 50.0

    success_rate = (
        problems_solved
        / problems_attempted
        * 100
    )

    confidence = min(
        problems_attempted / 20,
        1.0
    )

    score = (
        success_rate * confidence
        +
        50 * (1 - confidence)
    )

    return round(
        min(
            max(score, 0),
            100
        ),
        2
    )


# ============================================================
# HARD PROBLEM PERFORMANCE
# ============================================================

def calculate_hard_performance(
    hard_problem_success: float
):
    """
    Normalize hard-problem performance.
    """

    return round(
        min(
            max(
                hard_problem_success,
                0
            ),
            100
        ),
        2
    )


# ============================================================
# DATA CONFIDENCE
# ============================================================

def calculate_data_confidence(
    problems_attempted: int
):
    """
    Confidence in the student's current rating.

    0 problems  -> 0%
    20+ problems -> 100%
    """

    return min(
        problems_attempted / 20,
        1.0
    )


# ============================================================
# EFFECTIVE SKILL
# ============================================================

def calculate_effective_skill(
    skill_average: float,
    problems_attempted: int
):
    """
    Pull very small samples toward a neutral starting point.

    This prevents a beginner who solved only one unusually
    easy/effective problem from immediately receiving a
    very high OVR.
    """

    confidence = calculate_data_confidence(
        problems_attempted
    )

    effective_skill = (
        NEUTRAL_SKILL * (1 - confidence)
        +
        skill_average * confidence
    )

    return round(
        min(
            max(
                effective_skill,
                0
            ),
            100
        ),
        2
    )


# ============================================================
# BASE OVR
# ============================================================

def calculate_base_ovr(
    effective_skill: float,
    hard_problem_success: float,
    consistency_score: float,
    experience_score: float
):
    """
    Calculate the base OVR.

    Skill is the strongest signal.

    Hard problems, consistency and experience help
    distinguish experienced olympiad students from
    beginners with limited history.
    """

    skill_component = max(
        effective_skill - 50,
        0
    ) * 0.65

    hard_component = max(
        hard_problem_success - 50,
        0
    ) * 0.15

    consistency_component = max(
        consistency_score - 50,
        0
    ) * 0.10

    experience_component = max(
        experience_score - 50,
        0
    ) * 0.10

    raw_ovr = (
        MIN_OVR
        +
        skill_component
        +
        hard_component
        +
        consistency_component
        +
        experience_component
    )

    return round(
        min(
            max(
                raw_ovr,
                MIN_OVR
            ),
            MAX_OVR
        )
    )


# ============================================================
# EXCEPTIONAL 98-99
# ============================================================

def check_exceptional_level(
    base_ovr: int,
    effective_skill: float,
    hard_problem_success: float,
    consistency_score: float,
    experience_score: float,
    problems_attempted: int,
    achievement_level: int,
    special_event_winner: bool
):
    """
    98-99 is deliberately extremely rare.

    Requirements:
    - excellent effective skill
    - very high hard-problem performance
    - very high consistency
    - large problem history
    - international-level achievement OR special event
    """

    exceptional_history = (
        problems_attempted >= 300
    )

    exceptional_skill = (
        effective_skill >= 96
    )

    exceptional_hard = (
        hard_problem_success >= 96
    )

    exceptional_consistency = (
        consistency_score >= 90
    )

    elite_achievement = (
        achievement_level >= 7
    )

    elite_event = (
        special_event_winner
    )

    if (
        exceptional_history
        and exceptional_skill
        and exceptional_hard
        and exceptional_consistency
        and (
            elite_achievement
            or elite_event
        )
    ):

        return min(
            max(
                base_ovr,
                98
            ),
            99
        )

    return min(
        base_ovr,
        97
    )


# ============================================================
# FINAL OVR
# ============================================================

def calculate_student_ovr(
    rating_input: StudentRatingInput
):
    """
    Calculate the final OVR.
    """

    experience_score = (
        calculate_experience_score(
            rating_input.problems_attempted,
            rating_input.olympiad_experience
        )
    )

    consistency_score = (
        calculate_consistency_score(
            rating_input.problems_attempted,
            rating_input.problems_solved
        )
    )

    hard_problem_success = (
        calculate_hard_performance(
            rating_input.hard_problem_success
        )
    )

    effective_skill = (
        calculate_effective_skill(
            rating_input.skill_average,
            rating_input.problems_attempted
        )
    )

    base_ovr = calculate_base_ovr(
        effective_skill=effective_skill,
        hard_problem_success=hard_problem_success,
        consistency_score=consistency_score,
        experience_score=experience_score
    )

    final_ovr = check_exceptional_level(
        base_ovr=base_ovr,
        effective_skill=effective_skill,
        hard_problem_success=hard_problem_success,
        consistency_score=consistency_score,
        experience_score=experience_score,
        problems_attempted=rating_input.problems_attempted,
        achievement_level=rating_input.achievement_level,
        special_event_winner=rating_input.special_event_winner
    )

    return {
        "overall_rating": final_ovr,
        "effective_skill": effective_skill,
        "experience_score": experience_score,
        "consistency_score": consistency_score,
        "hard_problem_success": hard_problem_success,
        "data_confidence": calculate_data_confidence(
            rating_input.problems_attempted
        ),
    }


# ============================================================
# TIERS
# ============================================================

def get_rating_tier(
    ovr: int
):
    """
    Student-facing OVR tiers.
    """

    if ovr >= 98:
        return "LEGENDARY"

    if ovr >= 94:
        return "INTERNATIONAL GOLD LEVEL"

    if ovr >= 90:
        return "INTERNATIONAL SILVER LEVEL"

    if ovr >= 86:
        return "NATIONAL GOLD / INTERNATIONAL BRONZE LEVEL"

    if ovr >= 80:
        return "NATIONAL MEDAL LEVEL"

    if ovr >= 75:
        return "EXPERIENCED"

    if ovr >= 70:
        return "STRONG DEVELOPING"

    if ovr >= 60:
        return "DEVELOPING"

    return "BEGINNER"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_cases = [

        (
            "New Beginner",
            StudentRatingInput(
                skill_average=55,
                problems_attempted=5,
                problems_solved=3,
                hard_problem_success=0,
                olympiad_experience=0,
                achievement_level=0,
            )
        ),

        (
            "Experienced Student",
            StudentRatingInput(
                skill_average=80,
                problems_attempted=120,
                problems_solved=88,
                hard_problem_success=65,
                olympiad_experience=70,
                achievement_level=0,
            )
        ),

        (
            "National Bronze Level",
            StudentRatingInput(
                skill_average=82,
                problems_attempted=160,
                problems_solved=120,
                hard_problem_success=68,
                olympiad_experience=80,
                achievement_level=2,
            )
        ),

        (
            "National Gold / International Bronze Level",
            StudentRatingInput(
                skill_average=88,
                problems_attempted=220,
                problems_solved=175,
                hard_problem_success=84,
                olympiad_experience=90,
                achievement_level=4,
            )
        ),

        (
            "International Silver Level",
            StudentRatingInput(
                skill_average=92,
                problems_attempted=280,
                problems_solved=230,
                hard_problem_success=91,
                olympiad_experience=100,
                achievement_level=6,
            )
        ),

        (
            "International Gold Level",
            StudentRatingInput(
                skill_average=95,
                problems_attempted=400,
                problems_solved=350,
                hard_problem_success=96,
                olympiad_experience=100,
                achievement_level=7,
            )
        ),

        (
            "Legendary",
            StudentRatingInput(
                skill_average=98,
                problems_attempted=500,
                problems_solved=470,
                hard_problem_success=98,
                olympiad_experience=100,
                achievement_level=7,
                special_event_winner=True,
            )
        ),
    ]

    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - RATING ENGINE"
    )
    print("=" * 70)

    for name, rating_input in test_cases:

        result = calculate_student_ovr(
            rating_input
        )

        print()
        print(name)
        print("-" * 50)
        print(
            f"OVR: "
            f"{result['overall_rating']}"
        )
        print(
            f"Tier: "
            f"{get_rating_tier(result['overall_rating'])}"
        )
        print(
            f"Effective Skill: "
            f"{result['effective_skill']}"
        )
        print(
            f"Experience: "
            f"{result['experience_score']}"
        )
        print(
            f"Consistency: "
            f"{result['consistency_score']}"
        )
        print(
            f"Hard Problems: "
            f"{result['hard_problem_success']}%"
        )