from __future__ import annotations

import re

from phase04.rag.schemas import EvidenceDocument

_TOKEN = re.compile(r"[a-z0-9']+")


class LexicalReranker:
    """
    Lightweight reranker combining RRF, dense, sparse, and token overlap.
    Cross-encoder can replace this when COHERE_API_KEY or local model is added.
    """

    def rerank(
        self,
        query: str,
        documents: list[EvidenceDocument],
        *,
        top_n: int = 15,
    ) -> list[EvidenceDocument]:
        if not documents:
            return []

        query_tokens = set(_TOKEN.findall(query.lower()))
        scored: list[tuple[float, EvidenceDocument]] = []

        for doc in documents:
            text_tokens = set(_TOKEN.findall(doc.text_en.lower()))
            overlap = len(query_tokens & text_tokens) / max(len(query_tokens), 1)
            doc.rerank_score = (
                doc.rrf_score * 10.0
                + doc.dense_score * 2.0
                + doc.sparse_score * 1.5
                + overlap
            )
            scored.append((doc.rerank_score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [doc for _, doc in scored[:top_n]]
        for idx, doc in enumerate(top, start=1):
            doc.citation_id = idx
        return top
