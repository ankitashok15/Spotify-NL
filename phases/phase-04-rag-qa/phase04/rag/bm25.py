from __future__ import annotations

import logging
import re
from collections import Counter

from sqlalchemy import text
from sqlalchemy.orm import Session

from phase04.rag.schemas import EvidenceDocument, RouterFilters

logger = logging.getLogger(__name__)

_TOKEN = re.compile(r"[a-z0-9_]+", re.I)


class BM25Retriever:
    """PostgreSQL full-text search over review text (sparse retrieval)."""

    def __init__(self, session: Session):
        self.session = session

    def search(self, query: str, *, limit: int = 50, filters: RouterFilters | None = None) -> list[EvidenceDocument]:
        filters = filters or RouterFilters()
        sql = """
            SELECT
                r.id::text AS review_id,
                r.external_review_id,
                r.rating,
                r.thumbs_up,
                r.device_type,
                COALESCE(sr.subscription_type, 'unknown') AS subscription_type,
                sr.primary_issue,
                sr.emotions,
                sr.pain_points,
                r.review_created_at,
                COALESCE(sr.text_en, r.text_cleaned, r.text_original, '') AS text_en,
                ts_rank(
                    to_tsvector('english', COALESCE(sr.text_en, r.text_cleaned, r.text_original, '')),
                    plainto_tsquery('english', :query)
                ) AS sparse_score
            FROM reviews r
            LEFT JOIN structured_reviews sr ON sr.review_id = r.id
            WHERE r.is_spam = FALSE
              AND to_tsvector('english', COALESCE(sr.text_en, r.text_cleaned, r.text_original, ''))
                  @@ plainto_tsquery('english', :query)
              AND (:rating_min IS NULL OR r.rating >= :rating_min)
              AND (:rating_max IS NULL OR r.rating <= :rating_max)
              AND (:subscription_type IS NULL OR sr.subscription_type = :subscription_type)
              AND (:device_type IS NULL OR r.device_type = :device_type)
              AND (:is_discovery_related IS NULL OR sr.is_discovery_related = :is_discovery_related)
              AND (:primary_issue IS NULL OR sr.primary_issue = :primary_issue)
              AND (:date_from IS NULL OR r.review_created_at >= :date_from)
              AND (:date_to IS NULL OR r.review_created_at <= :date_to)
            ORDER BY sparse_score DESC
            LIMIT :limit
        """
        rows = self.session.execute(
            text(sql),
            {
                "query": query,
                "rating_min": filters.rating_min,
                "rating_max": filters.rating_max,
                "subscription_type": filters.subscription_type,
                "device_type": filters.device_type,
                "is_discovery_related": filters.is_discovery_related,
                "primary_issue": filters.primary_issue,
                "date_from": filters.date_from,
                "date_to": filters.date_to,
                "limit": limit,
            },
        ).mappings().all()

        docs: list[EvidenceDocument] = []
        for row in rows:
            docs.append(
                EvidenceDocument(
                    citation_id=0,
                    review_id=row["review_id"],
                    external_review_id=row["external_review_id"],
                    rating=row["rating"],
                    thumbs_up=row["thumbs_up"] or 0,
                    device_type=row["device_type"],
                    subscription_type=row["subscription_type"],
                    primary_issue=row["primary_issue"],
                    emotions=list(row["emotions"] or []),
                    pain_points=list(row["pain_points"] or []),
                    review_created_at=row["review_created_at"],
                    text_en=row["text_en"] or "",
                    sparse_score=float(row["sparse_score"] or 0.0),
                )
            )
        return docs


class SQLStructuredRetriever:
    """Metadata pre-filter retrieval when BM25/vector miss structured-only matches."""

    def __init__(self, session: Session):
        self.session = session

    def search(
        self,
        query: str,
        *,
        limit: int = 30,
        filters: RouterFilters | None = None,
    ) -> list[EvidenceDocument]:
        filters = filters or RouterFilters()
        feature = filters.mentioned_feature
        tokens = _TOKEN.findall(query.lower())
        if not feature and not filters.primary_issue and not filters.is_discovery_related:
            return []

        sql = """
            SELECT
                r.id::text AS review_id,
                r.external_review_id,
                r.rating,
                r.thumbs_up,
                r.device_type,
                COALESCE(sr.subscription_type, 'unknown') AS subscription_type,
                sr.primary_issue,
                sr.emotions,
                sr.pain_points,
                r.review_created_at,
                COALESCE(sr.text_en, r.text_cleaned, r.text_original, '') AS text_en
            FROM reviews r
            INNER JOIN structured_reviews sr ON sr.review_id = r.id
            WHERE r.is_spam = FALSE
              AND (:rating_min IS NULL OR r.rating >= :rating_min)
              AND (:rating_max IS NULL OR r.rating <= :rating_max)
              AND (:subscription_type IS NULL OR sr.subscription_type = :subscription_type)
              AND (:device_type IS NULL OR r.device_type = :device_type)
              AND (:is_discovery_related IS NULL OR sr.is_discovery_related = :is_discovery_related)
              AND (:primary_issue IS NULL OR sr.primary_issue = :primary_issue)
              AND (
                    :mentioned_feature IS NULL
                    OR sr.mentioned_features::text ILIKE '%' || :mentioned_feature || '%'
                    OR sr.feature_requests::text ILIKE '%' || :mentioned_feature || '%'
              )
            ORDER BY r.review_created_at DESC NULLS LAST
            LIMIT :limit
        """
        rows = self.session.execute(
            text(sql),
            {
                "rating_min": filters.rating_min,
                "rating_max": filters.rating_max,
                "subscription_type": filters.subscription_type,
                "device_type": filters.device_type,
                "is_discovery_related": filters.is_discovery_related,
                "primary_issue": filters.primary_issue or filters.mentioned_feature,
                "mentioned_feature": feature,
                "limit": limit,
            },
        ).mappings().all()

        docs: list[EvidenceDocument] = []
        for row in rows:
            text_en = row["text_en"] or ""
            overlap = sum(1 for t in tokens if t in text_en.lower())
            docs.append(
                EvidenceDocument(
                    citation_id=0,
                    review_id=row["review_id"],
                    external_review_id=row["external_review_id"],
                    rating=row["rating"],
                    thumbs_up=row["thumbs_up"] or 0,
                    device_type=row["device_type"],
                    subscription_type=row["subscription_type"],
                    primary_issue=row["primary_issue"],
                    emotions=list(row["emotions"] or []),
                    pain_points=list(row["pain_points"] or []),
                    review_created_at=row["review_created_at"],
                    text_en=text_en,
                    sparse_score=float(overlap),
                )
            )
        return docs
