"""
OLYMPIAD INTELLIGENCE
Student Intelligence Pipeline

Runs the complete student-analysis pipeline:

1. Update student profile
2. Detect weaknesses
3. Generate adaptive recommendations
4. Aggregate user edit requests
5. Verify reported metadata externally
6. Build review queue
7. Generate final student intelligence summary

Important:

- Review decisions are NOT automatically applied here.
- Human review remains a separate step.
- Metadata is never modified by this pipeline.
"""

import json
import subprocess
import sys
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

ROOT = Path(
    __file__
).resolve().parent.parent

PROFILE_PATH = (
    ROOT
    / "data/processed/student_profile.json"
)

WEAKNESS_PATH = (
    ROOT
    / "data/processed/student_weaknesses.json"
)

RECOMMENDATION_CSV_PATH = (
    ROOT
    / "data/processed/adaptive_recommendations.csv"
)

RECOMMENDATION_JSON_PATH = (
    ROOT
    / "data/processed/adaptive_recommendations.json"
)

HISTORY_PATH = (
    ROOT
    / "data/processed/student_history.json"
)

REPORTS_PATH = (
    ROOT
    / "data/feedback/edit_requests.json"
)

REPORT_SUMMARY_PATH = (
    ROOT
    / "data/feedback/edit_request_summary.json"
)

EXTERNAL_VERIFICATION_PATH = (
    ROOT
    / "data/feedback/external_verification.json"
)

REVIEW_QUEUE_PATH = (
    ROOT
    / "data/feedback/review_queue.json"
)

INTELLIGENCE_PATH = (
    ROOT
    / "data/processed/student_intelligence.json"
)


# ============================================================
# PIPELINE SCRIPTS
# ============================================================

PIPELINE_STEPS = [
    (
        "update_student_profile.py",
        "Build/update student profile",
    ),
    (
        "detect_weaknesses.py",
        "Detect student weaknesses",
    ),
    (
        "adaptive_recommendations.py",
        "Generate adaptive recommendations",
    ),
    (
        "aggregate_edit_requests.py",
        "Aggregate user reports",
    ),
    (
        "verify_edit_requests.py",
        "Verify edit requests",
    ),
    (
        "external_metadata_verifier.py",
        "Verify against external catalog",
    ),
    (
        "build_review_queue.py",
        "Build manual review queue",
    ),
]


# ============================================================
# RUN SCRIPT
# ============================================================

def run_script(
    script_name,
    description,
):
    """
    Run another project script safely.

    Uses the current Python interpreter and the project
    root as cwd.
    """

    script_path = (
        ROOT
        / "src"
        / script_name
    )

    if not script_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found: "
            f"{script_path}"
        )

    print()
    print("=" * 70)
    print(
        f"PIPELINE STEP: {description}"
    )
    print(
        f"SCRIPT: {script_name}"
    )
    print("=" * 70)

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
        ],
        cwd=ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{script_name} failed "
            f"with exit code "
            f"{result.returncode}"
        )

    print()
    print(
        f"COMPLETED: {script_name}"
    )


# ============================================================
# JSON LOADER
# ============================================================

def load_json(
    path,
    default=None,
):
    """
    Load JSON safely.
    """

    if default is None:
        default = {}

    if not path.exists():
        return default

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(
                file
            )

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return default


# ============================================================
# FINAL SUMMARY
# ============================================================

def create_summary():
    """
    Create compact student intelligence summary.
    """

    profile = load_json(
        PROFILE_PATH,
        {},
    )

    weaknesses = load_json(
        WEAKNESS_PATH,
        {},
    )

    history = load_json(
        HISTORY_PATH,
        [],
    )

    recommendations = load_json(
        RECOMMENDATION_JSON_PATH,
        [],
    )

    reports = load_json(
        REPORTS_PATH,
        [],
    )

    report_summary = load_json(
        REPORT_SUMMARY_PATH,
        [],
    )

    external_verification = load_json(
        EXTERNAL_VERIFICATION_PATH,
        [],
    )

    review_queue = load_json(
        REVIEW_QUEUE_PATH,
        [],
    )

    # --------------------------------------------------------
    # Weakness buckets
    # --------------------------------------------------------

    high_priority = []

    medium_priority = []

    unknown_skills = []

    for skill, data in weaknesses.items():

        classification = data.get(
            "classification"
        )

        if classification == "HIGH":
            high_priority.append(
                skill
            )

        elif classification == "MEDIUM":
            medium_priority.append(
                skill
            )

        elif (
            classification
            == "NOT_ENOUGH_DATA"
        ):
            unknown_skills.append(
                skill
            )

    # --------------------------------------------------------
    # Recommendation count
    # --------------------------------------------------------

    if isinstance(
        recommendations,
        list,
    ):
        recommendation_count = len(
            recommendations
        )

    else:
        recommendation_count = 0

    # --------------------------------------------------------
    # Report statistics
    # --------------------------------------------------------

    if isinstance(
        reports,
        list,
    ):
        report_count = len(
            reports
        )

    else:
        report_count = 0

    if isinstance(
        report_summary,
        list,
    ):
        grouped_report_count = len(
            report_summary
        )

    else:
        grouped_report_count = 0

    # --------------------------------------------------------
    # Verification statistics
    # --------------------------------------------------------

    verified_high = 0

    verified_medium = 0

    verified_low = 0

    for item in external_verification:

        verification = item.get(
            "verification",
            {},
        )

        confidence = verification.get(
            "confidence"
        )

        if confidence == "HIGH":
            verified_high += 1

        elif confidence == "MEDIUM":
            verified_medium += 1

        elif confidence == "LOW":
            verified_low += 1

    # --------------------------------------------------------
    # Review queue statistics
    # --------------------------------------------------------

    review_count = (
        len(review_queue)
        if isinstance(
            review_queue,
            list,
        )
        else 0
    )

    # --------------------------------------------------------
    # Student skill ratings
    # --------------------------------------------------------

    skill_names = [
        "algebra",
        "geometry",
        "number_theory",
        "discrete_mathematics",
        "proof",
        "reasoning",
        "calculation",
        "case_analysis",
    ]

    skill_ratings = {}

    for skill in skill_names:
        skill_ratings[skill] = profile.get(
            skill,
            0,
        )

    # --------------------------------------------------------
    # Strongest skills
    # --------------------------------------------------------

    ranked = sorted(
        skill_ratings.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    strongest_skills = [
        skill
        for skill, rating in ranked
        if isinstance(
            rating,
            (int, float),
        )
        and rating > 0
    ][:3]

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

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
            len(history)
            if isinstance(
                history,
                list,
            )
            else 0,
        ),

        "problems_solved": profile.get(
            "problems_solved",
            0,
        ),

        "achievement": profile.get(
            "achievement",
            "NONE",
        ),

        "strongest_skills":
            strongest_skills,

        "high_priority_weaknesses":
            high_priority,

        "medium_priority_weaknesses":
            medium_priority,

        "unknown_skills":
            unknown_skills,

        "skill_ratings":
            skill_ratings,

        "recommendations": {
            "count":
                recommendation_count,

            "csv_path":
                str(
                    RECOMMENDATION_CSV_PATH
                    .relative_to(ROOT)
                ),

            "json_path":
                str(
                    RECOMMENDATION_JSON_PATH
                    .relative_to(ROOT)
                ),
        },

        "feedback": {
            "reports":
                report_count,

            "grouped_suggestions":
                grouped_report_count,

            "external_verification":
                len(
                    external_verification
                )
                if isinstance(
                    external_verification,
                    list,
                )
                else 0,

            "high_confidence":
                verified_high,

            "medium_confidence":
                verified_medium,

            "low_confidence":
                verified_low,

            "review_queue":
                review_count,
        },

        "pipeline_status": {
            "metadata_changed":
                False,

            "human_review_required":
                review_count > 0,

            "ready_for_review":
                review_count,
        },
    }

    return summary


# ============================================================
# SAVE SUMMARY
# ============================================================

def save_summary(
    summary,
):
    """
    Save final intelligence summary.
    """

    INTELLIGENCE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        INTELLIGENCE_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return INTELLIGENCE_PATH


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
    summary,
):
    print()
    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "FINAL STUDENT SUMMARY"
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

    print(
        "STRONGEST SKILLS"
    )

    print(
        "-" * 50
    )

    if summary[
        "strongest_skills"
    ]:

        for skill in summary[
            "strongest_skills"
        ]:

            rating = summary[
                "skill_ratings"
            ].get(
                skill,
                0,
            )

            print(
                f"- {skill}: "
                f"{rating}"
            )

    else:
        print(
            "- None"
        )

    print()

    print(
        "HIGH PRIORITY WEAKNESSES"
    )

    print(
        "-" * 50
    )

    if summary[
        "high_priority_weaknesses"
    ]:

        for skill in summary[
            "high_priority_weaknesses"
        ]:

            print(
                f"- {skill}"
            )

    else:
        print(
            "- None"
        )

    print()

    print(
        "MEDIUM PRIORITY WEAKNESSES"
    )

    print(
        "-" * 50
    )

    if summary[
        "medium_priority_weaknesses"
    ]:

        for skill in summary[
            "medium_priority_weaknesses"
        ]:

            print(
                f"- {skill}"
            )

    else:
        print(
            "- None"
        )

    print()

    print(
        "UNKNOWN SKILLS"
    )

    print(
        "-" * 50
    )

    if summary[
        "unknown_skills"
    ]:

        for skill in summary[
            "unknown_skills"
        ]:

            print(
                f"- {skill}"
            )

    else:
        print(
            "- None"
        )

    print()

    print(
        "FEEDBACK PIPELINE"
    )

    print(
        "-" * 50
    )

    feedback = summary[
        "feedback"
    ]

    print(
        f"Reports: "
        f"{feedback['reports']}"
    )

    print(
        f"Grouped suggestions: "
        f"{feedback['grouped_suggestions']}"
    )

    print(
        f"External verification: "
        f"{feedback['external_verification']}"
    )

    print(
        f"High confidence: "
        f"{feedback['high_confidence']}"
    )

    print(
        f"Medium confidence: "
        f"{feedback['medium_confidence']}"
    )

    print(
        f"Low confidence: "
        f"{feedback['low_confidence']}"
    )

    print(
        f"Review queue: "
        f"{feedback['review_queue']}"
    )

    print()

    print(
        "PIPELINE SAFETY"
    )

    print(
        "-" * 50
    )

    pipeline_status = summary[
        "pipeline_status"
    ]

    print(
        f"Metadata changed: "
        f"{pipeline_status['metadata_changed']}"
    )

    print(
        f"Human review required: "
        f"{pipeline_status['human_review_required']}"
    )

    print()

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "OLYMPIAD INTELLIGENCE - "
        "FULL STUDENT PIPELINE"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Run all automatic stages
    # --------------------------------------------------------

    for script_name, description in (
        PIPELINE_STEPS
    ):

        run_script(
            script_name,
            description,
        )

    # --------------------------------------------------------
    # Build final summary
    # --------------------------------------------------------

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