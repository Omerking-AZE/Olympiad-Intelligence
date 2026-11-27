"""Conservative text-based language detection for MathNet problem statements."""
from __future__ import annotations

import re

LANGUAGE_NAMES = {
    "ar": "Arabic", "bg": "Bulgarian", "zh-cn": "Chinese", "zh-tw": "Chinese (Traditional)",
    "zh": "Chinese", "hr": "Croatian", "cs": "Czech", "nl": "Dutch", "en": "English",
    "fi": "Finnish", "fr": "French", "de": "German", "el": "Greek", "hu": "Hungarian",
    "it": "Italian", "ja": "Japanese", "ko": "Korean", "lt": "Lithuanian",
    "lv": "Latvian", "mn": "Mongolian", "pl": "Polish", "pt": "Portuguese",
    "ro": "Romanian", "ru": "Russian", "sr": "Serbian", "sk": "Slovak",
    "sl": "Slovenian", "es": "Spanish", "sv": "Swedish", "tr": "Turkish",
    "uk": "Ukrainian", "vi": "Vietnamese", "fa": "Persian", "hi": "Hindi",
    "id": "Indonesian",
}

def detect_language(text: str | None, minimum_probability: float = 0.70) -> str | None:
    """Return a human-readable language label, or None when evidence is weak.

    Math-heavy text can confuse language detectors, so short statements and
    low-confidence guesses are deliberately left unresolved.
    """
    if not text:
        return None
    plain = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", str(text))
    plain = re.sub(r"\\[a-zA-Z]+|\\[{}]", " ", plain)
    plain = re.sub(r"\$+.*?\$+", " ", plain, flags=re.DOTALL)
    plain = re.sub(r"[^\w\sÀ-ÿ]", " ", plain, flags=re.UNICODE)
    words = re.findall(r"\b[\wÀ-ÿ]+\b", plain, flags=re.UNICODE)
    if len(words) < 8 or len(" ".join(words)) < 40:
        return None
    try:
        from langdetect import detect_langs
        guesses = detect_langs(" ".join(words))
    except Exception:
        return None
    if not guesses or guesses[0].prob < minimum_probability:
        return None
    code = guesses[0].lang.lower()
    return LANGUAGE_NAMES.get(code) or LANGUAGE_NAMES.get(code.split("-")[0])


def is_compound_language(value: str | None) -> bool:
    value = str(value or "").strip()
    return bool(re.search(r"[;,/]", value))
