import json
import math
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

REPORTS_PATH = Path(
    "data/feedback/edit_requests.json"
)

SUMMARY_PATH = Path(
    "data/feedback/edit_request_summary.json"
)

METADATA_PATH = Path(
    "data/processed/problem_metadata.csv"
)

OUTPUT_PATH = Path(
    "data/feedback/edit_verification.json"
)


# ============================================================
# THRESHOLDS
# ============================================================

REVIEW_THRESHOLD = 3

AUTO_VERIFY_THRESHOLD = 5


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value):
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (
        TypeError,
        ValueError,
    ):
        pass

    return (
        str(value)
        .strip()
        .lower()
    )


# ============================================================
# JSON SAFE CONVERSION
# ============================================================

def json_safe(value):
    """
    Convert pandas / numpy values into strict JSON-safe values.

    NaN / +Infinity / -Infinity -> None
    """

    if value is None:
        return None

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

        return value

    if hasattr(value, "item"):
        try:
            value = value.item()
        except (
            ValueError,
            TypeError,
        ):
            pass

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

        return value

    if isinstance(value, dict):
        return {
            str(key): json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            json_safe(item)
            for item in value
        ]

    try:
        if pd.isna(value):
            return None
    except (
        TypeError,
        ValueError,
    ):
        pass

    return value


# ============================================================
# LOAD JSON
# ============================================================

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

        if isinstance(
            data,
            list,
        ):
            return data

        return []

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return []


# ============================================================
# LOAD METADATA
# ============================================================

def load_metadata():

    if not METADATA_PATH.exists():
        print(
            "\nWarning: metadata file not found."
        )

        return {}

    df = pd.read_csv(
        METADATA_PATH
    )

    if "problem_id" not in df.columns:
        return {}

    result = {}

    for _, row in df.iterrows():

        problem_id = normalize(
            row.get(
                "problem_id",
                "",
            )
        )

        if not problem_id:
            continue

        result[problem_id] = {
            "title": json_safe(
                row.get("title")
            ),

            "competition": json_safe(
                row.get("competition")
            ),

            "year": json_safe(
                row.get("year")
            ),

            "problem_number": json_safe(
                row.get("problem_number")
            ),

            "section": json_safe(
                row.get("section")
            ),

            "metadata_status": json_safe(
                row.get("metadata_status")
            ),

            "match_score": json_safe(
                row.get("match_score")
            ),

            "source": json_safe(
                row.get("source")
            ),

            "source_url": json_safe(
                row.get("source_url")
            ),
        }

    return result


# ============================================================
# GET CURRENT VALUE
# ============================================================

def get_current_value(
    current,
    issue_type,
):
    if issue_type == "competition":
        return normalize(
            current.get(
                "competition"
            )
        )

    if issue_type == "year":
        return normalize(
            current.get(
                "year"
            )
        )

    if issue_type == "problem_number":
        return normalize(
            current.get(
                "problem_number"
            )
        )

    if issue_type == "wrong_problem":
        return normalize(
            current.get(
                "title"
            )
        )

    return normalize(
        current.get(
            "title"
        )
    )


# ============================================================
# DETERMINE STATUS
# ============================================================

def determine_status(
    report_count,
    same_as_current,
):
    if same_as_current:
        return "REJECT_SAME_VALUE"

    if report_count >= AUTO_VERIFY_THRESHOLD:
        return "AUTO_VERIFY_CANDIDATE"

    if report_count >= REVIEW_THRESHOLD:
        return "REVIEW"

    return "PENDING"


# ============================================================
# DETERMINE CONFIDENCE
# ============================================================

def determine_confidence(
    report_count,
    status,
):
    if status == "REJECT_SAME_VALUE":
        return "INVALID"

    if report_count >= AUTO_VERIFY_THRESHOLD:
        return "HIGH"

    if report_count >= REVIEW_THRESHOLD:
        return "MEDIUM"

    return "LOW"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "OLYMPIAD INTELLIGENCE - "
        "EDIT REQUEST VERIFICATION"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    reports = load_json(
        REPORTS_PATH
    )

    summaries = load_json(
        SUMMARY_PATH
    )

    metadata = load_metadata()

    print(
        f"\nReports: "
        f"{len(reports)}"
    )

    print(
        f"Suggestions: "
        f"{len(summaries)}"
    )

    print(
        f"Metadata records: "
        f"{len(metadata)}"
    )

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    verification_results = []

    for suggestion in summaries:

        problem_id = normalize(
            suggestion.get(
                "problem_id",
                "",
            )
        )

        issue_type = normalize(
            suggestion.get(
                "issue_type",
                "",
            )
        )

        suggested_value = normalize(
            suggestion.get(
                "suggested_value",
                "",
            )
        )

        try:
            report_count = int(
                suggestion.get(
                    "report_count",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            report_count = 0

        current = metadata.get(
            problem_id,
            {},
        )

        current_value = get_current_value(
            current,
            issue_type,
        )

        same_as_current = (
            bool(current_value)
            and
            suggested_value
            == current_value
        )

        status = determine_status(
            report_count,
            same_as_current,
        )

        confidence = determine_confidence(
            report_count,
            status,
        )

        verification_results.append(
            {
                "problem_id": problem_id,

                "issue_type": issue_type,

                "current_value": (
                    current_value
                    or None
                ),

                "suggested_value": (
                    suggested_value
                    or None
                ),

                "report_count": (
                    report_count
                ),

                "same_as_current": (
                    same_as_current
                ),

                "status": status,

                "confidence": confidence,

                "metadata": {
                    "title": current.get(
                        "title"
                    ),

                    "competition": current.get(
                        "competition"
                    ),

                    "year": current.get(
                        "year"
                    ),

                    "problem_number": current.get(
                        "problem_number"
                    ),

                    "section": current.get(
                        "section"
                    ),

                    "metadata_status": current.get(
                        "metadata_status"
                    ),

                    "match_score": current.get(
                        "match_score"
                    ),

                    "source": current.get(
                        "source"
                    ),

                    "source_url": current.get(
                        "source_url"
                    ),
                },
            }
        )

    # --------------------------------------------------------
    # Clean everything before JSON output
    # --------------------------------------------------------

    verification_results = json_safe(
        verification_results
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

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
            verification_results,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    # --------------------------------------------------------
    # Validate output
    # --------------------------------------------------------

    with open(
        OUTPUT_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        validated = json.load(
            file
        )

    print(
        "\nJSON validation passed."
    )

    print(
        f"Verification records: "
        f"{len(validated)}"
    )

    # --------------------------------------------------------
    # Console report
    # --------------------------------------------------------

    print(
        "\nVerification results:"
    )

    if not validated:

        print(
            "  None"
        )

    else:

        for item in validated:

            print(
                f"  "
                f"{item['problem_id']} | "
                f"{item['issue_type']} | "
                f"{item['suggested_value']} | "
                f"{item['report_count']} report(s) | "
                f"{item['status']} | "
                f"{item['confidence']}"
            )

    print(
        f"\nSaved: "
        f"{OUTPUT_PATH}"
    )

    print(
        "\nNo metadata was changed."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()