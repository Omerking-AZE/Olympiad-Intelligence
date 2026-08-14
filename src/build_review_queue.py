import json
from pathlib import Path


VERIFICATION_PATH = Path(
    "data/feedback/external_verification.json"
)

OUTPUT_PATH = Path(
    "data/feedback/review_queue.json"
)


REVIEW_STATUSES = {
    "REVIEW",
    "EXTERNAL_REVIEW",
    "CONFLICTING_EVIDENCE",
    "SUGGESTION_UNSUPPORTED",
    "EXTERNAL_CONFIRMED",
    "AUTO_VERIFY_CANDIDATE",
}


def load_json(path):
    if not path.exists():
        return []

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return []


def priority_for(item):
    verification = item.get(
        "verification",
        {},
    )

    status = verification.get(
        "status",
        "",
    )

    report_count = int(
        item.get(
            "report_count",
            0,
        )
    )

    if status == "AUTO_VERIFY_CANDIDATE":
        return "CRITICAL"

    if status == "CONFLICTING_EVIDENCE":
        return "HIGH"

    if status == "EXTERNAL_CONFIRMED":
        return "HIGH"

    if report_count >= 3:
        return "MEDIUM"

    return "LOW"


def build_reason(item):
    verification = item.get(
        "verification",
        {},
    )

    status = verification.get(
        "status",
        "UNKNOWN",
    )

    reason = verification.get(
        "reason",
        "",
    )

    best = item.get(
        "best_text_candidate"
    )

    suggested = item.get(
        "suggested_candidate"
    )

    return {
        "status": status,
        "reason": reason,
        "suggested_candidate_exists":
            suggested is not None,
        "best_text_candidate":
            best.get("title")
            if best
            else None,
        "best_text_score":
            best.get(
                "combined_similarity"
            )
            if best
            else None,
    }


def main():
    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "REVIEW QUEUE"
    )
    print("=" * 70)

    verification_results = load_json(
        VERIFICATION_PATH
    )

    print(
        f"\nVerification records: "
        f"{len(verification_results)}"
    )

    queue = []

    for item in verification_results:
        verification = item.get(
            "verification",
            {},
        )

        status = verification.get(
            "status",
            "",
        )

        if status not in REVIEW_STATUSES:
            continue

        queue_item = {
            "problem_id":
                item.get(
                    "problem_id"
                ),

            "issue_type":
                item.get(
                    "issue_type"
                ),

            "suggested_value":
                item.get(
                    "suggested_value"
                ),

            "report_count":
                item.get(
                    "report_count",
                    0,
                ),

            "priority":
                priority_for(
                    item
                ),

            "analysis":
                build_reason(
                    item
                ),

            "action":
                (
                    "MANUAL_REVIEW"
                    if status
                    != "AUTO_VERIFY_CANDIDATE"
                    else
                    "VERIFY_BEFORE_APPLY"
                ),
        }

        queue.append(
            queue_item
        )

    priority_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    queue.sort(
        key=lambda item: (
            priority_order.get(
                item["priority"],
                99,
            ),
            -int(
                item.get(
                    "report_count",
                    0,
                )
            ),
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            queue,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nReview queue items: "
        f"{len(queue)}"
    )

    print("\nQueue:")

    if not queue:
        print("  Empty")

    else:
        for item in queue:
            analysis = item[
                "analysis"
            ]

            print(
                f"  "
                f"{item['priority']} | "
                f"{item['problem_id']} | "
                f"{item['suggested_value']} | "
                f"{item['report_count']} report(s)"
            )

            print(
                f"    Status: "
                f"{analysis['status']}"
            )

            print(
                f"    Best candidate: "
                f"{analysis['best_text_candidate']}"
            )

            print(
                f"    Best score: "
                f"{analysis['best_text_score']}"
            )

            print(
                f"    Action: "
                f"{item['action']}"
            )

    print(
        f"\nSaved: {OUTPUT_PATH}"
    )

    print(
        "\nNo metadata was changed."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()