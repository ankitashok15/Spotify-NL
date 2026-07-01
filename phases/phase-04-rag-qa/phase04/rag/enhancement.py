from __future__ import annotations

import logging

from phase02.shared.llm_gemini import GeminiProvider
from phase04.shared.config import settings

logger = logging.getLogger(__name__)


class QueryEnhancer:
    """Rewrite queries and optional HyDE hypothetical document expansion."""

    def __init__(self, llm: GeminiProvider | None = None):
        self.llm = llm

    def enhance(self, question: str, search_query: str) -> str:
        if self.llm is None:
            return search_query

        try:
            rewritten = self.llm.generate_text(
                f"Rewrite this Spotify review search query for semantic retrieval. "
                f"Return only the rewritten query.\n\nOriginal question: {question}\n"
                f"Current query: {search_query}",
                system="You optimize search queries for music app review retrieval.",
            )
            query = rewritten.strip() or search_query
        except Exception as exc:
            logger.warning("Query rewrite failed: %s", exc)
            query = search_query

        if settings.rag_use_hyde:
            try:
                hypo = self.llm.generate_text(
                    f"Write a short hypothetical Google Play review that would answer: {question}",
                    system="Write one realistic negative Spotify review paragraph.",
                )
                if hypo.strip():
                    query = f"{query}\n{hypo.strip()[:500]}"
            except Exception as exc:
                logger.warning("HyDE failed: %s", exc)

        return query
