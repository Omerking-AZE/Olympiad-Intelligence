"""
OLYMPIAD INTELLIGENCE
Student Performance Data

Day 10
Stores individual problem performance data.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProblemPerformance:
    problem_id: str
    domain: str
    difficulty: float
    solved: bool
    score: float
    proof: Optional[float] = None
    reasoning: Optional[float] = None
    calculation: Optional[float] = None
    case_analysis: Optional[float] = None


PROBLEMS = [
    {
        "id": "MATHNET-001",
        "domain": "Algebra",
        "difficulty": 65.0,
        "solved": True,
        "score": 92.0,
        "proof": 90.0,
        "reasoning": 88.0,
        "calculation": 85.0,
        "case": 80.0,
    },
    {
        "id": "MATHNET-002",
        "domain": "Geometry",
        "difficulty": 72.0,
        "solved": True,
        "score": 86.0,
        "proof": 94.0,
        "reasoning": 91.0,
        "calculation": 78.0,
        "case": 88.0,
    },
    {
        "id": "MATHNET-003",
        "domain": "Number Theory",
        "difficulty": 80.0,
        "solved": False,
        "score": 42.0,
        "proof": 65.0,
        "reasoning": 70.0,
        "calculation": 55.0,
        "case": 60.0,
    },
    {
        "id": "MATHNET-004",
        "domain": "Algebra",
        "difficulty": 55.0,
        "solved": True,
        "score": 95.0,
        "proof": 93.0,
        "reasoning": 90.0,
        "calculation": 91.0,
        "case": 85.0,
    },
]


def create_performances():
    """Convert raw problem dictionaries to dataclass objects."""

    return [
        ProblemPerformance(
            problem_id=problem["id"],
            domain=problem["domain"],
            difficulty=problem["difficulty"],
            solved=problem["solved"],
            score=problem["score"],
            proof=problem["proof"],
            reasoning=problem["reasoning"],
            calculation=problem["calculation"],
            case_analysis=problem["case"],
        )
        for problem in PROBLEMS
    ]


def print_performances(performances):
    """Display problem performance data."""

    print("=" * 70)
    print("OLYMPIAD INTELLIGENCE - STUDENT PERFORMANCE")
    print("=" * 70)

    print()

    for index, performance in enumerate(
        performances,
        start=1
    ):
        print(f"Problem {index}")
        print(f"  ID:          {performance.problem_id}")
        print(f"  Domain:      {performance.domain}")
        print(f"  Difficulty:  {performance.difficulty}")
        print(f"  Solved:      {performance.solved}")
        print(f"  Score:       {performance.score}")
        print(f"  Proof:       {performance.proof}")
        print(f"  Reasoning:   {performance.reasoning}")
        print(f"  Calculation: {performance.calculation}")
        print(f"  Case:        {performance.case_analysis}")
        print()


if __name__ == "__main__":
    performances = create_performances()
    print_performances(performances)