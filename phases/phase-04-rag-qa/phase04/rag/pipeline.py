from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from phase02.shared.llm_gemini import GeminiProvider
from phase03.search.schemas import SearchFilters
from phase04.rag.bm25 import BM25Retriever, SQLStructuredRetriever
from phase04.rag.citations import build_citation_payload, validate_citations
from phase04.rag.context import build_evidence_pack
from phase04.rag.enhancement import QueryEnhancer
from phase04.rag.filters import merge_filters
from phase04.rag.fusion import reciprocal_rank_fusion
from phase04.rag.generator import RAGGenerator
from phase04.rag.retriever import HybridRetriever
from phase04.rag.reranker import LexicalReranker
from phase04.rag.router import QueryRouter
from phase04.rag.schemas import EvidenceDocument, RouterFilters
from phase04.shared.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    answer: str
    citations: list[dict]
    confidence: float
    reviews_considered: int
    reviews_cited: int
    intent: str
    search_query: str
    took_ms: float
    citation_valid: bool
    warnings: list[str] = field(default_factory=list)
    evidence: list[EvidenceDocument] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "citations": self.citations,
            "confidence": self.confidence,
            "reviews_considered": self.reviews_considered,
            "reviews_cited": self.reviews_cited,
            "intent": self.intent,
            "search_query": self.search_query,
            "took_ms": self.took_ms,
            "citation_valid": self.citation_valid,
            "warnings": self.warnings,
        }


class RAGPipeline:
    def __init__(
        self,
        session: Session,
        llm: GeminiProvider | None = None,
    ):
        self.session = session
        self.llm = llm or GeminiProvider(model_name=settings.gemini_model_rag)
        self.router = QueryRouter(self.llm)
        self.enhancer = QueryEnhancer(self.llm)
        self.dense = HybridRetriever()
        self.bm25 = BM25Retriever(session)
        self.sql_retriever = SQLStructuredRetriever(session)
        self.reranker = LexicalReranker()
        self.generator = RAGGenerator(self.llm)

    def query(
        self,
        question: str,
        *,
        filters: SearchFilters | None = None,
        skip_llm_router: bool = False,
    ) -> RAGResult:
        started = time.perf_counter()
        warnings: list[str] = []

        routed = self.router.route(question) if not skip_llm_router else QueryRouter().route(question)
        merged_search_filters = merge_filters(filters, routed.filters)
        search_query = self.enhancer.enhance(question, routed.search_query)

        dense_hits = self.dense.dense_search(
            search_query,
            filters=merged_search_filters,
            top_k=settings.rag_retrieve_top_k,
        )
        sparse_hits = self.bm25.search(
            search_query,
            limit=settings.rag_retrieve_top_k,
            filters=routed.filters,
        )
        sql_hits = self.sql_retriever.search(
            search_query,
            limit=30,
            filters=routed.filters,
        )

        fused = reciprocal_rank_fusion([dense_hits, sparse_hits, sql_hits])
        reranked = self.reranker.rerank(
            search_query,
            fused,
            top_n=settings.rag_rerank_top_n,
        )

        evidence_pack = build_evidence_pack(reranked)
        answer = self.generator.generate(question, evidence_pack, reranked)
        validation = validate_citations(answer, reranked)
        warnings.extend(validation.warnings)

        cited_payload = build_citation_payload(reranked, validation.cited_ids)
        confidence = self._estimate_confidence(reranked, validation)

        took_ms = round((time.perf_counter() - started) * 1000, 2)
        return RAGResult(
            answer=answer,
            citations=cited_payload,
            confidence=confidence,
            reviews_considered=len(fused),
            reviews_cited=len(cited_payload),
            intent=routed.intent,
            search_query=search_query,
            took_ms=took_ms,
            citation_valid=validation.valid,
            warnings=warnings,
            evidence=reranked,
        )

    def _estimate_confidence(
        self,
        documents: list[EvidenceDocument],
        validation,
    ) -> float:
        if not documents:
            return 0.0
        top_score = documents[0].rerank_score if documents else 0.0
        base = min(0.95, 0.45 + top_score * 0.1)
        if not validation.valid:
            base *= 0.7
        if not validation.cited_ids:
            base *= 0.6
        return round(base, 2)
