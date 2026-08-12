"""
OLYMPIAD INTELLIGENCE
Student Intelligence Pipeline

Runs the complete student-analysis pipeline:

1. Student history
2. Dynamic profile
3. Weakness detection
4. Adaptive recommendations
5. Summary JSON

The visual card can then consume student_profile.json.
"""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

PROFILE_PATH = ROOT / "data/processed/student_profile.json"
WEAKNESS_PATH = ROOT / "data/processed/student_weaknesses.json"
RECOMMENDATION_PATH = (
    ROOT / "data/processed/adaptive_recommendations.csv"
)
HISTORY_PATH = ROOT / "data/processed/student_history.json"


def run_script(script_name):
    """Run another project script safely."""

    script_path = ROOT / "src" / script_name

    print()
    print("=" * 70)
    print(f"RUNNING: {script_name}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{script_name} failed with "
            f"exit code {result.returncode}"
        )


def load_json(path):
    """Load JSON safely."""

    if not path.exists():
        return {}

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def create_summary():
    """Create a compact student intelligence summary."""

    profile = load_json(PROFILE_PATH)
    weaknesses = load_json(WEAKNESS_PATH)
    history = load_json(HISTORY_PATH)

    high_priority = []
    medium_priority = []

    for skill, data in weaknesses.items():

        classification = data.get(
            "classification"
        )

        if classification == "HIGH":
            high_priority.append(skill)

        elif classification == "MEDIUM":
            medium_priority.append(skill)

    summary = {
        "student_id": profile.get(
            "student_id"
        ),

        "student_name": profile.get(
            "student_name"
        ),

        "overall_rating": profile.get(
            "overall_rating",
            0,
        ),

        "tier": profile.get(
            "tier",
            "UNKNOWN",
        ),

        "problems_attempted": profile.get(
            "problems_attempted",
            len(history),
        ),

        "problems_solved": profile.get(
            "problems_solved",
            0,
        ),

        "achievement": profile.get(
            "achievement",
            "NONE",
        ),

        "strongest_skills": [],

        "high_priority_weaknesses": high_priority,

        "medium_priority_weaknesses": medium_priority,

        "unknown_skills": [
            skill
            for skill, data in weaknesses.items()
            if data.get("classification")
            == "NOT_ENOUGH_DATA"
        ],

        "skill_ratings": {
            skill: profile.get(
                skill,
                0,
            )
            for skill in [
                "algebra",
                "geometry",
                "number_theory",
                "discrete_mathematics",
                "proof",
                "reasoning",
                "calculation",
                "case_analysis",
            ]
        },
    }

    # Find strongest skills
    ranked = sorted(
        summary["skill_ratings"].items(),
        key=lambda item: item[1],
        reverse=True,
    )

    summary["strongest_skills"] = [
        skill
        for skill, rating in ranked
        if rating > 0
    ][:3]

    return summary


def save_summary(summary):
    """Save final intelligence summary."""

    output_path = (
        ROOT / "data/processed/student_intelligence.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return output_path


def print_summary(summary):
    """Display final pipeline result."""

    print()
    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "STUDENT INTELLIGENCE SUMMARY"
    )
    print("=" * 70)

    print()

    print(
        f"Student: "
        f"{summary['student_name']}"
    )

    print(
        f"OVR:     "
        f"{summary['overall_rating']}"
    )

    print(
        f"Tier:    "
        f"{summary['tier']}"
    )

    print()

    print(
        f"Problems: "
        f"{summary['problems_solved']}/"
        f"{summary['problems_attempted']}"
    )

    print(
        f"Achievement: "
        f"{summary['achievement']}"
    )

    print()

    print("STRONGEST SKILLS")
    print("-" * 50)

    for skill in summary["strongest_skills"]:
        print(
            f"- {skill}: "
            f"{summary['skill_ratings'][skill]}"
        )

    print()

    print("HIGH PRIORITY WEAKNESSES")
    print("-" * 50)

    if summary["high_priority_weaknesses"]:
        for skill in summary[
            "high_priority_weaknesses"
        ]:
            print(f"- {skill}")
    else:
        print("- None")

    print()

    print("MEDIUM PRIORITY WEAKNESSES")
    print("-" * 50)

    if summary["medium_priority_weaknesses"]:
        for skill in summary[
            "medium_priority_weaknesses"
        ]:
            print(f"- {skill}")
    else:
        print("- None")

    print()

    print("UNKNOWN SKILLS")
    print("-" * 50)

    if summary["unknown_skills"]:
        for skill in summary["unknown_skills"]:
            print(f"- {skill}")
    else:
        print("- None")

    print()

    print("=" * 70)


def main():

    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "FULL STUDENT PIPELINE"
    )
    print("=" * 70)

    # 1. Build/update profile
    run_script(
        "update_student_profile.py"
    )

    # 2. Detect weaknesses
    run_script(
        "detect_weaknesses.py"
    )

    # 3. Generate adaptive recommendations
    run_script(
        "adaptive_recommendations.py"
    )

    # 4. Build final summary
    summary = create_summary()

    output_path = save_summary(
        summary
    )

    print_summary(
        summary
    )

    print()
    print(
        f"Final summary saved to: "
        f"{output_path}"
    )

    print()
    print("=" * 70)
    print(
        "FULL STUDENT PIPELINE COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()