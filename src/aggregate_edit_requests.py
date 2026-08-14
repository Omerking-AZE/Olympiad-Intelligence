import json
from collections import Counter
from pathlib import Path


REPORTS_PATH = Path(
    "data/feedback/edit_requests.json"
)

OUTPUT_PATH = Path(
    "data/feedback/edit_request_summary.json"
)

# Safety thresholds.
# A single report must NEVER change metadata.
REVIEW_THRESHOLD = 3
AUTO_VERIFY_THRESHOLD = 5


def normalize(value):
    return (
        str(value)
        .strip()
        .lower()
    )


def load_reports():
    if not REPORTS_PATH.exists():
        return []

    try:
        with open(
            REPORTS_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(
            data,
            list,
        ):
            return []

        return data

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return []


def build_summary(reports):
    grouped = Counter()

    for report in reports:
        problem_id = normalize(
            report.get(
                "problem_id",
                "",
            )
        )

        issue_type = normalize(
            report.get(
                "issue_type",
                "",
            )
        )

        suggested_value = normalize(
            report.get(
                "suggested_value",
                "",
            )
        )

        if not problem_id:
            continue

        if not issue_type:
            continue

        if not suggested_value:
            continue

        key = (
            problem_id,
            issue_type,
            suggested_value,
        )

        grouped[key] += 1

    results = []

    for key, count in grouped.items():
        problem_id, issue_type, suggestion = key

        if count >= AUTO_VERIFY_THRESHOLD:
            status = "AUTO_VERIFY"

        elif count >= REVIEW_THRESHOLD:
            status = "REVIEW"

        else:
            status = "PENDING"

        results.append(
            {
                "problem_id": problem_id,
                "issue_type": issue_type,
                "suggested_value": suggestion,
                "report_count": count,
                "status": status,
            }
        )

    results.sort(
        key=lambda item: (
            -item["report_count"],
            item["problem_id"],
        )
    )

    return results


def main():
    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "EDIT REQUEST AGGREGATOR"
    )
    print("=" * 70)

    reports = load_reports()

    print(
        f"\nReports loaded: {len(reports)}"
    )

    summary = build_summary(
        reports
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
            summary,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Suggestions grouped: "
        f"{len(summary)}"
    )

    print("\nCurrent suggestions:")

    if not summary:
        print("  None")

    else:
        for item in summary:
            print(
                f"  {item['problem_id']} | "
                f"{item['issue_type']} | "
                f"{item['suggested_value']} | "
                f"{item['report_count']} report(s) | "
                f"{item['status']}"
            )

    print(
        f"\nSaved: {OUTPUT_PATH}"
    )

    print("\nRules:")
    print(
        f"  1 report  -> PENDING"
    )
    print(
        f"  {REVIEW_THRESHOLD}+ reports -> REVIEW"
    )
    print(
        f"  {AUTO_VERIFY_THRESHOLD}+ reports -> AUTO_VERIFY"
    )

    print(
        "\nNo metadata was changed."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()