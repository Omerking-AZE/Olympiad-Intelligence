"""Create English display translations for imported MathNet records.

Install the optional model dependencies first:
    pip install -r requirements-translation.txt

Then run:
    python src/translate_mathnet.py

The source text is never overwritten. Machine translations are marked as needing
review because mathematical wording and OCR/LaTeX should be checked before use.
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone

from platform_store import connect, init_db

MODEL_DEFAULT = "facebook/m2m100_418M"
LANGUAGE_CODES = {
    "en": "en", "eng": "en", "english": "en",
    "ar": "ar", "arabic": "ar",
    "bg": "bg", "bulgarian": "bg",
    "zh": "zh", "zh-cn": "zh", "chinese": "zh", "mandarin": "zh",
    "hr": "hr", "croatian": "hr",
    "cs": "cs", "czech": "cs",
    "nl": "nl", "dutch": "nl",
    "fi": "fi", "finnish": "fi",
    "fr": "fr", "french": "fr",
    "de": "de", "german": "de",
    "el": "el", "greek": "el",
    "hu": "hu", "hungarian": "hu",
    "it": "it", "italian": "it",
    "ja": "ja", "japanese": "ja",
    "ko": "ko", "korean": "ko",
    "lt": "lt", "lithuanian": "lt",
    "lv": "lv", "latvian": "lv",
    "mn": "mn", "mongolian": "mn",
    "pl": "pl", "polish": "pl",
    "pt": "pt", "portuguese": "pt",
    "ro": "ro", "romanian": "ro",
    "ru": "ru", "russian": "ru",
    "sr": "sr", "serbian": "sr",
    "sk": "sk", "slovak": "sk",
    "sl": "sl", "slovenian": "sl",
    "es": "es", "spanish": "es",
    "sv": "sv", "swedish": "sv",
    "tr": "tr", "turkish": "tr",
    "uk": "uk", "ukrainian": "uk",
    "vi": "vi", "vietnamese": "vi",
    "fa": "fa", "persian": "fa",
    "hi": "hi", "hindi": "hi",
    "id": "id", "indonesian": "id",
}

PROTECTED = re.compile(
    r"(\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$(?!\$).*?(?<!\\)\$|!\[[^\]]*\]\(attached_image_\d+\.png\))",
    re.DOTALL,
)


def language_code(value):
    normalized = str(value or "").strip().lower().replace("_", "-")
    if normalized in LANGUAGE_CODES:
        return LANGUAGE_CODES[normalized]
    first = normalized.split("-")[0]
    if first in LANGUAGE_CODES:
        return LANGUAGE_CODES[first]
    for label, code in LANGUAGE_CODES.items():
        if label in normalized:
            return code
    return None


def chunks(value, max_chars=700):
    for paragraph in value.splitlines(keepends=True):
        while len(paragraph) > max_chars:
            split_at = paragraph.rfind(" ", 0, max_chars)
            if split_at < max_chars // 2:
                split_at = max_chars
            yield paragraph[:split_at]
            paragraph = paragraph[split_at:]
        if paragraph:
            yield paragraph


def translate_markdown(value, source_code, tokenizer, model, device):
    if not value or source_code == "en":
        return value
    pieces = PROTECTED.split(value)
    output = []
    work = []
    locations = []

    for piece in pieces:
        if not piece:
            continue
        if PROTECTED.fullmatch(piece):
            output.append(piece)
            continue
        output_index = len(output)
        output.append("")
        for chunk in chunks(piece):
            if chunk.strip():
                locations.append((output_index, len(work)))
                work.append(chunk)
            else:
                output[output_index] += chunk

    if work:
        tokenizer.src_lang = source_code
        translated = []
        for start in range(0, len(work), 8):
            batch = work[start:start + 8]
            encoded = tokenizer(
                batch, return_tensors="pt", padding=True,
                truncation=True, max_length=512
            ).to(device)
            generated = model.generate(
                **encoded,
                forced_bos_token_id=tokenizer.get_lang_id("en"),
                max_new_tokens=512,
            )
            translated.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))

        # Restore translated chunks in their original positions.
        for (output_index, work_index), result in zip(locations, translated):
            output[output_index] += result

    return "".join(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_DEFAULT)
    parser.add_argument("--limit", type=int, default=0, help="Translate at most this many records (0 = all).")
    args = parser.parse_args()

    try:
        import torch
        from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
    except ImportError as error:
        raise SystemExit(
            "Missing optional dependencies. Install with: pip install -r requirements-translation.txt"
        ) from error

    init_db()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {args.model} on {device}; first run downloads the model weights.")
    tokenizer = M2M100Tokenizer.from_pretrained(args.model)
    model = M2M100ForConditionalGeneration.from_pretrained(args.model).to(device)
    model.eval()

    with connect() as db:
        query = """
            SELECT problem_id, language, problem_text_original, solution_text_original
            FROM problems
            WHERE translation_status = 'pending'
            ORDER BY problem_id
        """
        rows = db.execute(query).fetchall()
        if args.limit > 0:
            rows = rows[:args.limit]

        complete = 0
        unsupported = {}
        for index, row in enumerate(rows, start=1):
            source_code = language_code(row["language"])
            if not source_code or source_code not in tokenizer.lang_code_to_id:
                unsupported[row["language"]] = unsupported.get(row["language"], 0) + 1
                continue

            problem_en = translate_markdown(
                row["problem_text_original"], source_code, tokenizer, model, device
            )
            solution_en = translate_markdown(
                row["solution_text_original"], source_code, tokenizer, model, device
            )
            db.execute(
                """
                UPDATE problems
                SET problem_text_en=?, solution_text_en=?,
                    translation_status='machine_translated_review_needed'
                WHERE problem_id=?
                """,
                (problem_en, solution_en, row["problem_id"]),
            )
            complete += 1
            if index % 100 == 0:
                db.commit()
                print(f"Processed {index:,}/{len(rows):,}; translated {complete:,}")

        db.commit()

    print(f"Translation run complete: {complete:,} translated.")
    if unsupported:
        print("Languages needing a configured model mapping:")
        for language, count in sorted(unsupported.items()):
            print(f"  {language}: {count:,}")
    print("Review translated math text before treating it as authoritative.")


if __name__ == "__main__":
    main()
