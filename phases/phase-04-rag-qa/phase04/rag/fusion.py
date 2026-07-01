from __future__ import annotations

from phase04.rag.schemas import EvidenceDocument


def reciprocal_rank_fusion(
    ranked_lists: list[list[EvidenceDocument]],
    *,
    k: int = 60,
) -> list[EvidenceDocument]:
    """Merge multiple ranked lists with RRF scores."""
    scores: dict[str, float] = {}
    merged: dict[str, EvidenceDocument] = {}

    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked, start=1):
            scores[doc.review_id] = scores.get(doc.review_id, 0.0) + 1.0 / (k + rank)
            if doc.review_id not in merged:
                merged[doc.review_id] = doc
            else:
                existing = merged[doc.review_id]
                existing.dense_score = max(existing.dense_score, doc.dense_score)
                existing.sparse_score = max(existing.sparse_score, doc.sparse_score)

    result = list(merged.values())
    for doc in result:
        doc.rrf_score = scores.get(doc.review_id, 0.0)
    result.sort(key=lambda d: d.rrf_score, reverse=True)
    return result
