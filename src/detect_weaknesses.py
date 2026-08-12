"""
OLYMPIAD INTELLIGENCE
Student Weakness Detection

Distinguishes between:

1. Genuine weakness
2. Insufficient data
3. Strong skill

IMPORTANT:
Low confidence does not erase a possible weakness.
Instead, confidence is reported separately.
"""

import json
from pathlib import Path

import pandas as pd


PROFILE_PATH = Path(
    "data/processed/student_profile.json"
)

HISTORY_PATH = Path(
    "data/processed/student_history.json"
)

OUTPUT_PATH = Path(
    "data/processed/student_weaknesses.json"
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


DOMAIN_TO_SKILL = {
    "Algebra": "algebra",
    "Geometry": "geometry",
    "Number Theory": "number_theory",
    "Discrete Mathematics": "discrete_mathematics",
}


def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def calculate_recent_score(
    history,
    skill
):

    relevant = []

    for attempt in reversed(history):

        domain = DOMAIN_TO_SKILL.get(
            attempt.get("domain")
        )

        if domain == skill:

            relevant.append(
                float(
                    attempt.get(
                        "score",
                        0
                    )
                )
            )

        if len(relevant) >= 5:
            break

    if not relevant:
        return None

    return round(
        sum(relevant) / len(relevant),
        2
    )


def calculate_failure_rate(
    history,
    skill
):

    relevant = []

    for attempt in history:

        domain = DOMAIN_TO_SKILL.get(
            attempt.get("domain")
        )

        if domain == skill:

            relevant.append(
                bool(
                    attempt.get(
                        "solved",
                        False
                    )
                )
            )

    if not relevant:
        return None

    failures = sum(
        not solved
        for solved in relevant
    )

    return round(
        failures
        / len(relevant)
        * 100,
        2
    )


def calculate_priority(
    rating,
    confidence,
    recent_score,
    failure_rate
):
    """
    Calculate weakness priority from 0-100.

    IMPORTANT:
    Confidence affects the interpretation, but does not
    completely suppress a genuine low rating.

    This prevents:
        rating 42 + low confidence
    from incorrectly becoming:
        "no weakness".

    Unknown skills (rating 0) are handled separately.
    """

    if rating <= 0:
        return 0

    # --------------------------------------------------------
    # 1. Current rating weakness
    # --------------------------------------------------------

    rating_component = max(
        0,
        80 - rating
    )

    # --------------------------------------------------------
    # 2. Recent performance
    # --------------------------------------------------------

    recent_component = 0

    if recent_score is not None:

        recent_component = max(
            0,
            80 - recent_score
        )

    # --------------------------------------------------------
    # 3. Failure rate
    # --------------------------------------------------------

    failure_component = 0

    if failure_rate is not None:

        failure_component = (
            failure_rate * 0.5
        )

    # --------------------------------------------------------
    # Base weakness
    # --------------------------------------------------------

    base_priority = (
        rating_component * 0.45
        +
        recent_component * 0.25
        +
        failure_component * 0.30
    )

    # --------------------------------------------------------
    # Confidence modifier
    #
    # Never remove the weakness completely.
    #
    # 0% confidence is already handled as unknown.
    # Low confidence keeps at least 50% of the signal.
    # --------------------------------------------------------

    if confidence >= 0.75:
        confidence_factor = 1.0

    elif confidence >= 0.25:
        confidence_factor = 0.85

    else:
        confidence_factor = 0.65

    priority = (
        base_priority
        * confidence_factor
    )

    return round(
        min(
            max(
                priority,
                0
            ),
            100
        ),
        2
    )


def classify_priority(
    priority
):

    if priority >= 50:
        return "HIGH"

    if priority >= 20:
        return "MEDIUM"

    if priority > 0:
        return "LOW"

    return "NONE"


def detect_weaknesses(
    profile,
    history
):

    results = {}

    confidence_map = profile.get(
        "skill_confidence",
        {}
    )

    for skill in SKILLS:

        rating = profile.get(
            skill,
            0
        )

        confidence = confidence_map.get(
            skill,
            0
        )

        recent_score = (
            calculate_recent_score(
                history,
                skill
            )
        )

        failure_rate = (
            calculate_failure_rate(
                history,
                skill
            )
        )

        # ----------------------------------------------------
        # No data
        # ----------------------------------------------------

        if rating <= 0:

            results[skill] = {

                "rating": 0,

                "confidence": confidence,

                "recent_score": None,

                "failure_rate": None,

                "priority": 0,

                "classification":
                    "NOT_ENOUGH_DATA",

            }

            continue

        # ----------------------------------------------------
        # Real skill
        # ----------------------------------------------------

        priority = calculate_priority(
            rating=rating,
            confidence=confidence,
            recent_score=recent_score,
            failure_rate=failure_rate,
        )

        results[skill] = {

            "rating": rating,

            "confidence": round(
                confidence,
                3
            ),

            "recent_score": (
                recent_score
            ),

            "failure_rate": (
                failure_rate
            ),

            "priority": priority,

            "classification":
                classify_priority(
                    priority
                ),
        }

    return results


def main():

    print("=" * 70)

    print(
        "OLYMPIAD INTELLIGENCE - "
        "WEAKNESS DETECTION"
    )

    print("=" * 70)

    profile = load_json(
        PROFILE_PATH
    )

    history = load_json(
        HISTORY_PATH
    )

    results = detect_weaknesses(
        profile,
        history
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
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    rows = []

    for skill, data in results.items():

        rows.append({

            "skill": skill,

            "rating":
                data["rating"],

            "confidence":
                data["confidence"],

            "recent_score":
                data["recent_score"],

            "failure_rate":
                data["failure_rate"],

            "priority":
                data["priority"],

            "classification":
                data["classification"],
        })

    df = pd.DataFrame(
        rows
    )

    print()
    print(
        "SKILL ANALYSIS"
    )

    print("-" * 90)

    print(
        df.to_string(
            index=False
        )
    )

    print()
    print(
        f"Saved: {OUTPUT_PATH}"
    )

    print()
    print("=" * 70)

    print(
        "WEAKNESS DETECTION COMPLETE"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()