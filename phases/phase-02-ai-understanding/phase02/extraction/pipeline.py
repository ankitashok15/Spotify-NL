from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from phase02.database.repositories import (
    ExtractionCacheRepository,
    ReviewExtractionRepository,
    StructuredReviewRepository,
)
from phase02.extraction.extractor import (
    PreparedReview,
    extract_batch,
    extraction_to_row,
    prepare_review_text,
)
from phase02.extraction.schema import ReviewExtraction
from phase02.shared.config import settings
from phase02.shared.llm_gemini import GeminiProvider
from phase02.shared.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class ExtractionRunReport:
    processed: int = 0
    cached: int = 0
    failed: int = 0
    discovery_related: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "processed": self.processed,
            "cached": self.cached,
            "failed": self.failed,
            "discovery_related": self.discovery_related,
            "errors": self.errors,
        }


class ExtractionPipeline:
    def __init__(self, session: Session, llm: LLMProvider | None = None):
        self.session = session
        self.llm = llm or GeminiProvider()
        self.reviews = ReviewExtractionRepository(session)
        self.structured = StructuredReviewRepository(session)
        self.cache = ExtractionCacheRepository(session)
        self.model_name = getattr(self.llm, "_model_name", settings.gemini_model)

    def run(
        self,
        *,
        batch_size: int | None = None,
        limit: int | None = None,
        review_ids: list[uuid.UUID] | None = None,
        skip_spam: bool | None = None,
    ) -> ExtractionRunReport:
        batch_size = batch_size or settings.extract_batch_size
        skip_spam = settings.extract_skip_spam if skip_spam is None else skip_spam
        report = ExtractionRunReport()
        remaining = limit

        while True:
            fetch_limit = batch_size
            if remaining is not None:
                if remaining <= 0:
                    break
                fetch_limit = min(batch_size, remaining)

            pending = self.reviews.fetch_pending(
                limit=fetch_limit,
                skip_spam=skip_spam,
                review_ids=review_ids if report.processed == 0 and review_ids else None,
            )
            if not pending:
                break

            prepared_batch: list[PreparedReview] = []
            cached_results: list[tuple[PreparedReview, ReviewExtraction, dict]] = []

            for review in pending:
                try:
                    prepared = prepare_review_text(review, self.llm)
                    self.reviews.mark_translated(review.id)

                    cached_payload = self.cache.get(prepared.content_hash)
                    if cached_payload:
                        extraction = ReviewExtraction.model_validate(cached_payload)
                        extraction = extraction.model_copy(update={"review_id": prepared.review_id})
                        from phase02.extraction.enrichment import (
                            apply_feature_normalization,
                            enrich_with_play_metadata,
                        )

                        extraction = apply_feature_normalization(extraction)
                        extraction, metadata = enrich_with_play_metadata(extraction, review)
                        cached_results.append((prepared, extraction, metadata))
                        report.cached += 1
                    else:
                        prepared_batch.append(prepared)
                except Exception as exc:
                    report.failed += 1
                    report.errors.append(f"{review.id}: prepare failed — {exc}")
                    logger.exception("Prepare failed for %s", review.id)

            try:
                extracted = extract_batch(prepared_batch, self.llm) if prepared_batch else []
            except Exception as exc:
                report.failed += len(prepared_batch)
                report.errors.append(f"batch extract failed — {exc}")
                logger.exception("Batch extraction failed")
                extracted = []

            for prepared, extraction, metadata in cached_results:
                try:
                    row = extraction_to_row(
                        prepared, extraction, metadata, model_name=self.model_name
                    )
                    self.structured.upsert(row)
                    self.reviews.mark_extracted(prepared.review.id)
                    report.processed += 1
                    if extraction.is_discovery_related:
                        report.discovery_related += 1
                except Exception as exc:
                    report.failed += 1
                    report.errors.append(f"{prepared.review_id}: persist failed — {exc}")
                    logger.exception("Persist failed for %s", prepared.review_id)

            for prepared, extraction, metadata in extracted:
                try:
                    self.cache.put(
                        prepared.content_hash,
                        extraction.model_dump(),
                        self.model_name,
                    )
                    row = extraction_to_row(
                        prepared, extraction, metadata, model_name=self.model_name
                    )
                    self.structured.upsert(row)
                    self.reviews.mark_extracted(prepared.review.id)
                    report.processed += 1
                    if extraction.is_discovery_related:
                        report.discovery_related += 1
                except Exception as exc:
                    report.failed += 1
                    report.errors.append(f"{prepared.review_id}: persist failed — {exc}")
                    logger.exception("Persist failed for %s", prepared.review_id)

            self.session.commit()

            if review_ids:
                break
            if remaining is not None:
                remaining -= len(pending)
                if remaining <= 0:
                    break
            if len(pending) < fetch_limit:
                break

        return report

    def status(self) -> dict:
        return {
            "pending": self.reviews.count_pending(skip_spam=settings.extract_skip_spam),
            "structured_total": self.structured.count_all(),
            "discovery_related": self.structured.count_discovery_related(),
        }
