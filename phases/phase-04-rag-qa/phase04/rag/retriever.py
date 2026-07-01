from __future__ import annotations

import logging
from datetime import datetime

from phase03.search.schemas import SearchFilters
from phase03.search.semantic_search import SemanticSearchService
from phase04.rag.schemas import EvidenceDocument, RouterFilters

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Dense vector search via Phase 3 semantic search."""

    def __init__(self, semantic_search: SemanticSearchService | None = None):
        self.semantic = semantic_search or SemanticSearchService()

    def dense_search(
        self,
        query: str,
        *,
        filters: SearchFilters | None = None,
        top_k: int = 50,
    ) -> list[EvidenceDocument]:
        try:
            response = self.semantic.search(query, filters=filters, top_k=top_k)
        except Exception as exc:
            logger.warning("Dense retrieval failed: %s", exc)
            return []

        docs: list[EvidenceDocument] = []
        for hit in response.results:
            docs.append(
                EvidenceDocument(
                    citation_id=0,
                    review_id=hit.review_id,
                    external_review_id=hit.external_review_id,
                    rating=hit.rating,
                    thumbs_up=hit.thumbs_up or 0,
                    device_type=hit.device_type,
                    subscription_type=hit.subscription_type,
                    primary_issue=hit.primary_issue,
                    review_created_at=hit.review_created_at,
                    text_en=hit.text_en or "",
                    dense_score=float(hit.score),
                )
            )
        return docs
