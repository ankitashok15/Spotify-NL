from __future__ import annotations

import logging

from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0
logger = logging.getLogger(__name__)

ENGLISH_CODES = {"en", "en-us", "en-gb"}


def detect_language(text: str, *, min_confidence: float = 0.8) -> tuple[str, float]:
    """
    Detect language code and confidence.
    Returns ('en', 1.0) for empty or undetectable short text.
    """
    cleaned = (text or "").strip()
    if len(cleaned) < 10:
        return "en", 1.0

    try:
        candidates = detect_langs(cleaned)
        if not candidates:
            return "en", 0.5
        best = candidates[0]
        code = best.lang.lower()
        confidence = float(best.prob)
        if confidence < min_confidence and len(candidates) > 1:
            code = candidates[0].lang.lower()
        return code, confidence
    except LangDetectException:
        logger.debug("Language detection failed; defaulting to en")
        return "en", 0.5


def is_english(lang_code: str) -> bool:
    return lang_code.lower() in ENGLISH_CODES or lang_code.lower().startswith("en")
