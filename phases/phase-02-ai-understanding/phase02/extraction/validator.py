from __future__ import annotations

import logging
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from phase02.extraction.schema import BatchExtractionResponse, ReviewExtraction
from phase02.shared.config import settings
from phase02.shared.llm_provider import LLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


def validate_extraction_batch(
    payload,
    expected_ids: list[str],
) -> list[ReviewExtraction]:
    batch = BatchExtractionResponse.from_llm_payload(payload)
    by_id = {item.review_id: item for item in batch.extractions}
    missing = set(expected_ids) - set(by_id)
    if missing:
        raise ValueError(f"Missing review_id in extraction batch: {sorted(missing)}")
    return [by_id[rid] for rid in expected_ids]


def extract_with_retry(
    llm: LLMProvider,
    prompt: str,
    *,
    system: str,
    expected_ids: list[str],
    max_retries: int | None = None,
) -> list[ReviewExtraction]:
    retries = max_retries if max_retries is not None else settings.extract_max_retries
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            payload = llm.generate_json(prompt, system=system)
            return validate_extraction_batch(payload, expected_ids)
        except (ValidationError, ValueError, KeyError) as exc:
            last_error = exc
            logger.warning("Extraction validation failed (attempt %s/%s): %s", attempt, retries, exc)
            prompt = (
                f"{prompt}\n\n"
                f"RETRY {attempt}: Previous output was invalid ({exc}). "
                f"Return valid JSON with extractions for ALL review_ids: {sorted(expected_ids)}"
            )
    raise RuntimeError(f"Extraction failed after {retries} retries") from last_error
