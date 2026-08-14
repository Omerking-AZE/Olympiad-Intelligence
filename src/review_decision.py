import json
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

QUEUE_PATH = Path(
    "data/feedback/review_queue.json"
)

VERIFICATION_PATH = Path(
    "data/feedback/external_verification.json"
)

DECISIONS_PATH = Path(
    "data/feedback/review_decisions.json"
)


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(path, default):
    if not path.exists():
        return default

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return default


def save_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_suffix(
        ".tmp"
    )

    with open(
        temporary_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_path.replace(
        path
    )


# ============================================================
# FIND RECORD
# ============================================================

def find_verification(
    verification,
    problem_id,
):
    target = str(
        problem_id
    ).strip().lower()

    for item in verification:
        current = str(
            item.get(
                "problem_id",
                "",
            )
        ).strip().lower()

        if current == target:
            return item

    return None


# ============================================================
# DISPLAY
# ============================================================

def print_review_context(item):
    verification = item.get(
        "verification",
        {},
    )

    print()
    print("=" * 70)
    print("REVIEW CONTEXT")
    print("=" * 70)

    print(
        f"\nProblem ID: "
        f"{item.get('problem_id')}"
    )

    print(
        f"Suggested value: "
        f"{item.get('suggested_value')}"
    )

    print(
        f"Report count: "
        f"{item.get('report_count', 0)}"
    )

    print(
        f"Verification status: "
        f"{verification.get('status')}"
    )

    print(
        f"Confidence: "
        f"{verification.get('confidence')}"
    )

    print(
        f"Reason: "
        f"{verification.get('reason')}"
    )

    suggested = item.get(
        "suggested_candidate"
    )

    best = item.get(
        "best_text_candidate"
    )

    print()
    print("Suggested external candidate:")

    if suggested:
        print(
            f"  Title: "
            f"{suggested.get('title')}"
        )

        print(
            f"  External ID: "
            f"{suggested.get('problem_id_external')}"
        )

        print(
            f"  Year: "
            f"{suggested.get('year')}"
        )

        print(
            f"  Problem number: "
            f"{suggested.get('problem_number')}"
        )

        print(
            f"  Competition: "
            f"{suggested.get('competition')}"
        )

        print(
            f"  URL: "
            f"{suggested.get('source_url')}"
        )

    else:
        print("  None")

    print()
    print("Best text candidate:")

    if best:
        print(
            f"  Title: "
            f"{best.get('title')}"
        )

        print(
            f"  External ID: "
            f"{best.get('problem_id_external')}"
        )

        print(
            f"  Combined similarity: "
            f"{best.get('combined_similarity')}"
        )

        print(
            f"  Word similarity: "
            f"{best.get('word_similarity')}"
        )

        print(
            f"  Character similarity: "
            f"{best.get('char_similarity')}"
        )

        print(
            f"  Sequence similarity: "
            f"{best.get('sequence_similarity')}"
        )

        print(
            f"  URL: "
            f"{best.get('source_url')}"
        )

    else:
        print("  None")

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "REVIEW DECISION"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    queue = load_json(
        QUEUE_PATH,
        [],
    )

    verification = load_json(
        VERIFICATION_PATH,
        [],
    )

    decisions = load_json(
        DECISIONS_PATH,
        [],
    )

    if not isinstance(
        queue,
        list,
    ):
        queue = []

    if not isinstance(
        verification,
        list,
    ):
        verification = []

    if not isinstance(
        decisions,
        list,
    ):
        decisions = []

    # --------------------------------------------------------
    # Empty queue
    # --------------------------------------------------------

    if not queue:
        print(
            "\nReview queue is empty."
        )
        return

    print(
        f"\nQueue items: "
        f"{len(queue)}"
    )

    # --------------------------------------------------------
    # Show queue
    # --------------------------------------------------------

    print(
        "\nAvailable review items:"
    )

    for index, item in enumerate(
        queue,
        start=1,
    ):
        analysis = item.get(
            "analysis",
            {},
        )

        print()
        print(
            f"[{index}] "
            f"{item.get('problem_id')} | "
            f"{item.get('suggested_value')} | "
            f"{item.get('priority')}"
        )

        print(
            f"    Status: "
            f"{analysis.get('status')}"
        )

        print(
            f"    Best candidate: "
            f"{analysis.get('best_text_candidate')}"
        )

        print(
            f"    Best score: "
            f"{analysis.get('best_text_score')}"
        )

        print(
            f"    Action: "
            f"{item.get('action')}"
        )

    # --------------------------------------------------------
    # Select item
    # --------------------------------------------------------

    selection = input(
        "\nEnter item number to review "
        "(or Q to quit): "
    ).strip()

    if selection.lower() == "q":
        print(
            "\nNo decision made."
        )
        return

    try:
        selected_index = (
            int(selection) - 1
        )

    except ValueError:
        print(
            "\nInvalid item number."
        )
        return

    if (
        selected_index < 0
        or selected_index >= len(queue)
    ):
        print(
            "\nInvalid item number."
        )
        return

    selected_item = queue[
        selected_index
    ]

    problem_id = str(
        selected_item.get(
            "problem_id",
            "",
        )
    ).strip().lower()

    # --------------------------------------------------------
    # Find verification record
    # --------------------------------------------------------

    verification_item = (
        find_verification(
            verification,
            problem_id,
        )
    )

    if verification_item is None:
        print(
            "\nVerification record not found."
        )
        return

    # --------------------------------------------------------
    # Show context
    # --------------------------------------------------------

    print_review_context(
        verification_item
    )

    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    print()
    print(
        "Decision options:"
    )

    print(
        "  A = APPROVE"
    )

    print(
        "  R = REJECT"
    )

    print(
        "  S = SKIP"
    )

    decision_input = input(
        "\nDecision: "
    ).strip().upper()

    if decision_input == "S":
        print(
            "\nSkipped."
        )
        print(
            "No decision was saved."
        )
        return

    if decision_input == "A":
        decision = "APPROVED"

    elif decision_input == "R":
        decision = "REJECTED"

    else:
        print(
            "\nInvalid decision."
        )
        return

    # --------------------------------------------------------
    # Reviewer note
    # --------------------------------------------------------

    note = input(
        "Reviewer note (optional): "
    ).strip()

    # --------------------------------------------------------
    # Decision ID
    # --------------------------------------------------------

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .strftime(
            "%Y%m%d%H%M%S%f"
        )
    )

    decision_id = (
        "review_" + timestamp
    )

    # --------------------------------------------------------
    # Create decision
    # --------------------------------------------------------

    decision_record = {
        "decision_id": decision_id,

        "problem_id": problem_id,

        "issue_type": (
            verification_item.get(
                "issue_type"
            )
        ),

        "suggested_value": (
            verification_item.get(
                "suggested_value"
            )
        ),

        "report_count": (
            verification_item.get(
                "report_count",
                0,
            )
        ),

        "verification_status": (
            verification_item
            .get(
                "verification",
                {},
            )
            .get(
                "status"
            )
        ),

        "verification_confidence": (
            verification_item
            .get(
                "verification",
                {},
            )
            .get(
                "confidence"
            )
        ),

        "decision": decision,

        "reviewer_note": note,

        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "metadata_applied": False,
    }

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    decisions.append(
        decision_record
    )

    save_json(
        DECISIONS_PATH,
        decisions,
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("DECISION SAVED")
    print("=" * 70)

    print(
        f"\nDecision: {decision}"
    )

    print(
        f"Problem: {problem_id}"
    )

    print(
        f"Suggestion: "
        f"{verification_item.get('suggested_value')}"
    )

    print(
        f"Saved to: "
        f"{DECISIONS_PATH}"
    )

    print(
        "\nMetadata was NOT modified."
    )

    print(
        "This decision will be used by "
        "the metadata application step."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()