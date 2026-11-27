"""Import the complete MathNet v0 train split into the local SQLite database.

Run from the repository root:
    python src/import_mathnet_full.py
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from language_detection import detect_language, is_compound_language\nfrom language_detection import detect_language, is_compound_language
from platform_store import IMAGE_DIR, connect, init_db

DATASET_ID = "ShadenA/MathNet"
BATCH_SIZE = 200


def clean(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def joined_solutions(value):
    if not value:
        return None
    if isinstance(value, str):
        return clean(value)
    return "\n\n---\n\n".join(str(item).strip() for item in value if item)


def safe_stem(value, fallback):
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value or fallback)).strip("_")
    return (stem or str(fallback))[:80]


def save_images(dataset_id, images):
    saved = []
    for index, image in enumerate(images or []):
        if image is None:
            continue
        name = f"{safe_stem(dataset_id, 'problem')}_{index + 1}.png"
        target = IMAGE_DIR / name
        if not target.exists():
            try:
                if hasattr(image, "save"):
                    image.save(target, format="PNG")
                elif isinstance(image, dict) and image.get("bytes"):
                    from PIL import Image
                    from io import BytesIO

                    Image.open(BytesIO(image["bytes"])).convert("RGB").save(target, format="PNG")
                else:
                    continue
            except Exception as error:
                print(f"Skipping image {name}: {error}")
                continue
        saved.append(name)
    return saved


def record_for(row, imported_at):
    dataset_id = str(clean(row.get("id")) or "")
    problem_id = f"MATHNET-{dataset_id}" if dataset_id else ""
    statement = clean(row.get("problem_markdown"))
    language = clean(row.get("language")) or "Unknown"
    # Resolve missing or compound metadata from the actual statement text.
    if language == "Unknown" or is_compound_language(language):
        language = detect_language(statement) or language
    language_is_english = str(language).strip().lower() in {"en", "eng", "english"}
    topics = row.get("topics_flat") or []
    topics = [str(topic).strip() for topic in topics if topic]
    domain = topics[0].split(">")[0].strip() if topics else None
    competition = clean(row.get("competition"))
    solutions = joined_solutions(row.get("solutions_markdown"))
    images = save_images(dataset_id, row.get("images") or [])

    return (
        problem_id,
        dataset_id,
        competition or "Olympiad problem",
        clean(row.get("country")),
        competition,
        language,
        domain,
        clean(row.get("problem_type")),
        statement,
        statement if language_is_english else None,
        solutions,
        solutions if language_is_english else None,
        clean(row.get("final_answer")),
        clean(row.get("source_booklet")),
        clean(row.get("booklet_source")),
        json.dumps(topics, ensure_ascii=False),
        json.dumps(images, ensure_ascii=False),
        50.0,
        "source_english" if language_is_english else "pending",
        imported_at,
    )


def main():
    try:
        from datasets import load_dataset
    except ImportError as error:
        raise SystemExit(
            "Missing dependency. Install it with: pip install -r requirements.txt"
        ) from error

    init_db()
    print(f"Downloading {DATASET_ID} (train split); this includes problem images.")
    dataset = load_dataset(DATASET_ID, split="train")
    print(f"Dataset loaded: {len(dataset):,} problems")

    imported_at = datetime.now(timezone.utc).isoformat()
    statement = """
        INSERT INTO problems (
            problem_id, dataset_id, title, country, competition, language, domain,
            problem_type, problem_text_original, problem_text_en,
            solution_text_original, solution_text_en, final_answer,
            source_booklet, booklet_source, topics_json, images_json,
            difficulty_score, translation_status, imported_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(problem_id) DO UPDATE SET
            title=excluded.title, country=excluded.country,
            competition=excluded.competition, language=excluded.language,
            domain=excluded.domain, problem_type=excluded.problem_type,
            problem_text_original=excluded.problem_text_original,
            problem_text_en=COALESCE(problems.problem_text_en, excluded.problem_text_en),
            solution_text_original=excluded.solution_text_original,
            solution_text_en=COALESCE(problems.solution_text_en, excluded.solution_text_en),
            final_answer=excluded.final_answer,
            source_booklet=excluded.source_booklet,
            booklet_source=excluded.booklet_source,
            topics_json=excluded.topics_json, images_json=excluded.images_json,
            imported_at=excluded.imported_at
    """

    batch = []
    english = 0
    non_english = 0
    with connect() as db:
        for index, row in enumerate(dataset, start=1):
            record = record_for(row, imported_at)
            if not record[0]:
                continue
            batch.append(record)
            if record[19] == "source_english":
                english += 1
            else:
                non_english += 1
            if len(batch) >= BATCH_SIZE:
                db.executemany(statement, batch)
                db.commit()
                batch.clear()
                if index % 2000 == 0:
                    print(f"Imported {index:,}/{len(dataset):,}")
        if batch:
            db.executemany(statement, batch)
            db.commit()
        total = db.execute("SELECT COUNT(*) FROM problems").fetchone()[0]

    print(f"Import complete. Problems in local DB: {total:,}")
    print(f"Already English: {english:,}; translation pending: {non_english:,}")
    print(f"Image cache: {IMAGE_DIR}")
    print("Source attribution: MathNet (ShadenA/MathNet), ICLR 2026; see its dataset card and booklet-level rights.")


if __name__ == "__main__":
    main()
