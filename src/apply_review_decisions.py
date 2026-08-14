import json
from pathlib import Path
import shutil


DECISIONS_PATH = Path(
    "data/feedback/review_decisions.json"
)

METADATA_PATH = Path(
    "data/processed/problem_metadata.csv"
)

BACKUP_PATH = Path(
    "data/processed/problem_metadata.before_review.csv"
)


def load_decisions():
    if not DECISIONS_PATH.exists():
        return []

    try:
        with open(
            DECISIONS_PATH,
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


def main():
    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - "
        "APPLY REVIEW DECISIONS"
    )
    print("=" * 70)

    decisions = load_decisions()

    print(
        f"\nDecisions loaded: "
        f"{len(decisions)}"
    )

    if not decisions:
        print(
            "\nNo review decisions found."
        )
        return

    approved = [
        item
        for item in decisions
        if item.get("decision") == "APPROVED"
        and item.get("metadata_applied") is not True
    ]

    rejected = [
        item
        for item in decisions
        if item.get("decision") == "REJECTED"
    ]

    print(
        f"Approved pending: "
        f"{len(approved)}"
    )

    print(
        f"Rejected: "
        f"{len(rejected)}"
    )

    # --------------------------------------------------------
    # Nothing to apply
    # --------------------------------------------------------

    if not approved:
        print(
            "\nNo approved metadata changes "
            "are waiting to be applied."
        )

        print(
            "\nNothing was changed."
        )

        print("=" * 70)
        return

    # --------------------------------------------------------
    # IMPORTANT SAFETY CHECK
    # --------------------------------------------------------

    print(
        "\nApproved changes:"
    )

    for item in approved:
        print(
            f"  "
            f"{item.get('problem_id')} | "
            f"{item.get('issue_type')} | "
            f"{item.get('suggested_value')}"
        )

    confirmation = input(
        "\nApply these changes? "
        "Type APPLY to continue: "
    ).strip()

    if confirmation != "APPLY":
        print(
            "\nCancelled."
        )

        print(
            "No metadata was changed."
        )

        print("=" * 70)
        return

    # --------------------------------------------------------
    # Import pandas only when needed
    # --------------------------------------------------------

    import pandas as pd

    if not METADATA_PATH.exists():
        print(
            f"\nMetadata file not found:"
        )

        print(
            METADATA_PATH
        )

        return

    # --------------------------------------------------------
    # Backup original metadata
    # --------------------------------------------------------

    shutil.copy2(
        METADATA_PATH,
        BACKUP_PATH,
    )

    print(
        f"\nBackup created:"
    )

    print(
        BACKUP_PATH
    )

    # --------------------------------------------------------
    # Load metadata
    # --------------------------------------------------------

    metadata = pd.read_csv(
        METADATA_PATH
    )

    if "problem_id" not in metadata.columns:
        raise ValueError(
            "problem_metadata.csv does not "
            "contain problem_id."
        )

    # Normalize helper map
    metadata["_problem_id_key"] = (
        metadata["problem_id"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    applied_count = 0

    # --------------------------------------------------------
    # Apply approved changes
    # --------------------------------------------------------

    for decision in approved:

        problem_id = str(
            decision.get(
                "problem_id",
                "",
            )
        ).strip().lower()

        issue_type = str(
            decision.get(
                "issue_type",
                "",
            )
        ).strip().lower()

        suggested_value = str(
            decision.get(
                "suggested_value",
                "",
            )
        ).strip()

        if not problem_id:
            print(
                "\nSkipping decision with "
                "missing problem_id."
            )
            continue

        if not suggested_value:
            print(
                f"\nSkipping {problem_id}: "
                "empty suggestion."
            )
            continue

        matches = (
            metadata[
                "_problem_id_key"
            ]
            == problem_id
        )

        if not matches.any():
            print(
                f"\nProblem not found:"
                f" {problem_id}"
            )
            continue

        index = metadata.index[
            matches
        ][0]

        # ----------------------------------------------------
        # Only supported fields can be changed.
        # ----------------------------------------------------

        if issue_type == "competition":

            metadata.loc[
                index,
                "competition",
            ] = suggested_value

        elif issue_type == "year":

            try:
                metadata.loc[
                    index,
                    "year",
                ] = int(
                    suggested_value
                )

            except ValueError:
                print(
                    f"\nInvalid year for "
                    f"{problem_id}: "
                    f"{suggested_value}"
                )
                continue

        elif issue_type == "problem_number":

            try:
                metadata.loc[
                    index,
                    "problem_number",
                ] = int(
                    suggested_value
                )

            except ValueError:
                print(
                    f"\nInvalid problem number "
                    f"for {problem_id}: "
                    f"{suggested_value}"
                )
                continue

        elif issue_type == "wrong_problem":

            if "title" not in metadata.columns:
                print(
                    f"\nNo title column for "
                    f"{problem_id}."
                )
                continue

            metadata.loc[
                index,
                "title",
            ] = suggested_value

        else:
            print(
                f"\nUnsupported issue type:"
                f" {issue_type}"
            )
            continue

        applied_count += 1

        print(
            f"\nAPPLIED:"
            f" {problem_id} | "
            f"{issue_type} | "
            f"{suggested_value}"
        )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    metadata = metadata.drop(
        columns=[
            "_problem_id_key"
        ]
    )

    metadata.to_csv(
        METADATA_PATH,
        index=False,
    )

    # --------------------------------------------------------
    # Mark only successfully applied decisions
    # --------------------------------------------------------

    for decision in decisions:

        if (
            decision.get(
                "decision"
            )
            == "APPROVED"
            and
            decision.get(
                "metadata_applied"
            )
            is not True
        ):
            problem_id = str(
                decision.get(
                    "problem_id",
                    "",
                )
            ).strip().lower()

            issue_type = str(
                decision.get(
                    "issue_type",
                    "",
                )
            ).strip().lower()

            # Check whether this decision was actually
            # applied by matching its identity.
            was_applied = any(
                str(
                    item.get(
                        "problem_id",
                        "",
                    )
                ).strip().lower()
                == problem_id
                and
                str(
                    item.get(
                        "issue_type",
                        "",
                    )
                ).strip().lower()
                == issue_type
                for item in approved
            )

            if was_applied:
                decision[
                    "metadata_applied"
                ] = True

    # --------------------------------------------------------
    # Save decisions
    # --------------------------------------------------------

    with open(
        DECISIONS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            decisions,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print()
    print("=" * 70)

    print(
        "REVIEW APPLICATION COMPLETE"
    )

    print("=" * 70)

    print(
        f"\nApplied changes: "
        f"{applied_count}"
    )

    print(
        f"Backup:"
        f" {BACKUP_PATH}"
    )

    print(
        f"Metadata:"
        f" {METADATA_PATH}"
    )

    print(
        f"Decisions:"
        f" {DECISIONS_PATH}"
    )

    print(
        "\nRejected decisions were not applied."
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()