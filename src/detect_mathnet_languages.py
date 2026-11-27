"""Repair missing/compound MathNet language labels in an existing local database.

Run from the repository root:
    python src/detect_mathnet_languages.py
"""
from __future__ import annotations

from language_detection import detect_language
from platform_store import connect, init_db


def main():
    init_db()
    changed = 0
    unresolved = 0
    with connect() as db:
        rows = db.execute(
            """
            SELECT problem_id, language, problem_text_original, solution_text_original
            FROM problems
            WHERE translation_status IN ('pending', 'source_english')
              AND (language IS NULL OR language = '' OR language = 'Unknown'
                   OR language LIKE '%;%' OR language LIKE '%,%' OR language LIKE '%/%')
            ORDER BY problem_id
            """
        ).fetchall()

        for row in rows:
            detected = detect_language(row["problem_text_original"])
            if not detected:
                unresolved += 1
                continue

            if detected == "English":
                db.execute(
                    """
                    UPDATE problems
                    SET language=?, problem_text_en=problem_text_original,
                        solution_text_en=solution_text_original,
                        translation_status='source_english'
                    WHERE problem_id=?
                    """,
                    (detected, row["problem_id"]),
                )
            else:
                db.execute(
                    """
                    UPDATE problems
                    SET language=?, problem_text_en=NULL, solution_text_en=NULL,
                        translation_status='pending'
                    WHERE problem_id=?
                    """,
                    (detected, row["problem_id"]),
                )
            changed += 1
            if changed % 500 == 0:
                db.commit()
                print(f"Resolved {changed:,} language labels...")

        db.commit()

    print(f"Language repair complete. Updated: {changed:,}; still uncertain: {unresolved:,}.")
    print("Uncertain records are intentionally left as Unknown; inspect them rather than guessing.")


if __name__ == "__main__":
    main()
