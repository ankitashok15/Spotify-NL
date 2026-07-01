from __future__ import annotations

import json
import logging

from phase02.extraction.language import is_english
from phase02.shared.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_TRANSLATION_SYSTEM = (
    "You translate Google Play app reviews to English. "
    "Preserve meaning, tone, and product-specific terms (Spotify features). "
    "Return JSON only."
)


def translate_to_english(
    review_id: str,
    text: str,
    source_lang: str,
    llm: LLMProvider,
) -> str:
    if is_english(source_lang):
        return text

    prompt = json.dumps(
        {
            "task": "translate_review",
            "source_language": source_lang,
            "reviews": [{"review_id": review_id, "text": text}],
            "output_format": {"reviews": [{"review_id": "string", "text_en": "string"}]},
        },
        ensure_ascii=False,
    )
    result = llm.generate_json(prompt, system=_TRANSLATION_SYSTEM)
    if isinstance(result, dict):
        items = result.get("reviews") or result.get("translations") or [result]
        if items:
            item = items[0]
            return item.get("text_en") or item.get("translation") or text
    if isinstance(result, list) and result:
        return result[0].get("text_en", text)
    logger.warning("Translation fallback for review %s", review_id)
    return text
