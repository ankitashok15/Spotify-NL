from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from qdrant_client.http import models as qmodels
from sqlalchemy.orm import Session

from phase03.database.repositories import EmbeddingReviewRepository
from phase03.embedding.embedder import ReviewEmbedder
from phase03.embedding.indexer import QdrantIndexer
from phase03.embedding.templates import ReviewEmbedInput
from phase03.shared.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmbedIndexReport:
    embedded: int = 0
    indexed: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "embedded": self.embedded,
            "indexed": self.indexed,
            "failed": self.failed,
            "errors": self.errors,
        }


class EmbedIndexPipeline:
    def __init__(
        self,
        session: Session,
        embedder: ReviewEmbedder | None = None,
        indexer: QdrantIndexer | None = None,
    ):
        self.session = session
        self.repo = EmbeddingReviewRepository(session)
        self.embedder = embedder or ReviewEmbedder()
        self.indexer = indexer or QdrantIndexer()

    def init_vector_store(self) -> None:
        self.indexer.ensure_collection()

    def run(
        self,
        *,
        batch_size: int | None = None,
        limit: int | None = None,
        review_ids: list[uuid.UUID] | None = None,
    ) -> EmbedIndexReport:
        batch_size = batch_size or settings.embed_batch_size
        report = EmbedIndexReport()
        remaining = limit

        self.init_vector_store()

        while True:
            fetch_limit = batch_size
            if remaining is not None:
                if remaining <= 0:
                    break
                fetch_limit = min(batch_size, remaining)

            rows = self.repo.fetch_pending(
                limit=fetch_limit,
                review_ids=review_ids if report.embedded == 0 and report.failed == 0 and review_ids else None,
            )
            if not rows:
                break

            inputs: list[ReviewEmbedInput] = []
            metadata: list[dict] = []
            for row in rows:
                embed_input, meta = row.to_embed_input()
                if not embed_input.text_en.strip():
                    report.failed += 1
                    report.errors.append(f"{row.review_id}: empty text")
                    continue
                inputs.append(embed_input)
                metadata.append(meta)

            try:
                embedded = self.embedder.embed_inputs(inputs, metadata)
                self.repo.mark_embedded([item.review_id for item in embedded])
                count = self.indexer.upsert_embeddings(embedded)
                self.repo.mark_indexed([item.review_id for item in embedded])
                self.session.commit()
                report.embedded += len(embedded)
                report.indexed += count
            except Exception as exc:
                self.session.rollback()
                report.failed += len(inputs)
                report.errors.append(f"batch failed — {exc}")
                logger.exception("Embed/index batch failed")

            if review_ids:
                break
            if remaining is not None:
                remaining -= len(rows)
                if remaining <= 0:
                    break
            if len(rows) < fetch_limit:
                break

        return report

    def status(self) -> dict:
        return {
            "pending_embed": self.repo.count_pending(),
            "indexed_db_state": self.repo.count_by_state("INDEXED"),
            "embedded_db_state": self.repo.count_by_state("EMBEDDED"),
            "qdrant_points": self.indexer.count_indexed(),
            "collection": settings.qdrant_collection,
        }
