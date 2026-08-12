"""
OLYMPIAD INTELLIGENCE
Student Problem-Solving History

Day 10 - Step 2

Stores every student problem attempt as a historical record.

This history will later be used for:
- dynamic skill updates
- OVR progression
- weakness detection
- personalized recommendations
- progress charts
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


HISTORY_PATH = Path(
    "data/processed/student_history.json"
)


@dataclass
class ProblemAttempt:
    """
    One attempt at one olympiad problem.
    """

    problem_id: str
    domain: str
    difficulty: float

    solved: bool
    score: float

    time_minutes: Optional[float] = None
    attempts: int = 1

    proof_score: Optional[float] = None
    reasoning_score: Optional[float] = None
    calculation_score: Optional[float] = None
    case_analysis_score: Optional[float] = None


def create_test_history():
    """
    Create a small test history.

    This is temporary test data.
    Later it will be replaced by actual
    student interactions.
    """

    return [
        ProblemAttempt(
            problem_id="MATHNET-001",
            domain="Algebra",
            difficulty=65.0,
            solved=True,
            score=92.0,
            time_minutes=28,
            attempts=1,
            proof_score=90.0,
            reasoning_score=88.0,
            calculation_score=85.0,
            case_analysis_score=80.0,
        ),

        ProblemAttempt(
            problem_id="MATHNET-002",
            domain="Geometry",
            difficulty=72.0,
            solved=True,
            score=86.0,
            time_minutes=41,
            attempts=1,
            proof_score=94.0,
            reasoning_score=91.0,
            calculation_score=78.0,
            case_analysis_score=88.0,
        ),

        ProblemAttempt(
            problem_id="MATHNET-003",
            domain="Number Theory",
            difficulty=80.0,
            solved=False,
            score=42.0,
            time_minutes=55,
            attempts=2,
            proof_score=65.0,
            reasoning_score=70.0,
            calculation_score=55.0,
            case_analysis_score=60.0,
        ),

        ProblemAttempt(
            problem_id="MATHNET-004",
            domain="Algebra",
            difficulty=55.0,
            solved=True,
            score=95.0,
            time_minutes=22,
            attempts=1,
            proof_score=93.0,
            reasoning_score=90.0,
            calculation_score=91.0,
            case_analysis_score=85.0,
        ),

        ProblemAttempt(
            problem_id="MATHNET-005",
            domain="Geometry",
            difficulty=88.0,
            solved=False,
            score=58.0,
            time_minutes=63,
            attempts=2,
            proof_score=72.0,
            reasoning_score=67.0,
            calculation_score=60.0,
            case_analysis_score=75.0,
        ),
    ]


def save_history(history):
    """
    Save the complete student history as JSON.
    """

    HISTORY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = [
        asdict(attempt)
        for attempt in history
    ]

    with open(
        HISTORY_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_history():
    """
    Load existing student history.

    Returns an empty list when no history exists.
    """

    if not HISTORY_PATH.exists():
        return []

    with open(
        HISTORY_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return [
        ProblemAttempt(**item)
        for item in data
    ]


def summarize_history(history):
    """
    Calculate basic history statistics.
    """

    if not history:
        return {
            "problems_attempted": 0,
            "problems_solved": 0,
            "success_rate": 0,
            "average_score": 0,
            "average_difficulty": 0,
            "average_time_minutes": 0,
        }

    solved = sum(
        attempt.solved
        for attempt in history
    )

    total_score = sum(
        attempt.score
        for attempt in history
    )

    total_difficulty = sum(
        attempt.difficulty
        for attempt in history
    )

    timed_attempts = [
        attempt.time_minutes
        for attempt in history
        if attempt.time_minutes is not None
    ]

    return {
        "problems_attempted": len(history),

        "problems_solved": solved,

        "success_rate": round(
            solved / len(history) * 100,
            2
        ),

        "average_score": round(
            total_score / len(history),
            2
        ),

        "average_difficulty": round(
            total_difficulty / len(history),
            2
        ),

        "average_time_minutes": round(
            sum(timed_attempts)
            / len(timed_attempts),
            2
        ) if timed_attempts else 0,
    }


def print_history(history):
    """
    Print the student's problem history.
    """

    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "STUDENT HISTORY"
    )
    print("=" * 70)

    print()

    for index, attempt in enumerate(
        history,
        start=1
    ):

        status = (
            "SOLVED"
            if attempt.solved
            else "NOT SOLVED"
        )

        print(
            f"{index}. "
            f"{attempt.problem_id}"
        )

        print(
            f"   Domain:      "
            f"{attempt.domain}"
        )

        print(
            f"   Difficulty:  "
            f"{attempt.difficulty}"
        )

        print(
            f"   Result:      "
            f"{status}"
        )

        print(
            f"   Score:       "
            f"{attempt.score}"
        )

        print(
            f"   Time:        "
            f"{attempt.time_minutes} min"
        )

        print(
            f"   Attempts:    "
            f"{attempt.attempts}"
        )

        print()


def print_summary(
    summary
):
    """
    Print aggregate history statistics.
    """

    print(
        "HISTORY SUMMARY"
    )

    print("-" * 50)

    print(
        f"Problems Attempted: "
        f"{summary['problems_attempted']}"
    )

    print(
        f"Problems Solved:    "
        f"{summary['problems_solved']}"
    )

    print(
        f"Success Rate:       "
        f"{summary['success_rate']}%"
    )

    print(
        f"Average Score:      "
        f"{summary['average_score']}"
    )

    print(
        f"Average Difficulty:  "
        f"{summary['average_difficulty']}"
    )

    print(
        f"Average Time:       "
        f"{summary['average_time_minutes']} min"
    )


def main():

    history = create_test_history()

    save_history(
        history
    )

    loaded_history = load_history()

    summary = summarize_history(
        loaded_history
    )

    print_history(
        loaded_history
    )

    print_summary(
        summary
    )

    print()

    print(
        f"Saved: {HISTORY_PATH}"
    )

    print()

    print("=" * 70)
    print(
        "STUDENT HISTORY COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()