import sys
from datetime import datetime
from pathlib import Path

import pytest

_PHASE04 = Path(__file__).resolve().parents[2] / "phases" / "phase-04-rag-qa"
_PHASE02 = Path(__file__).resolve().parents[2] / "phases" / "phase-02-ai-understanding"
sys.path.insert(0, str(_PHASE02))
sys.path.insert(0, str(_PHASE04))

from phase04.rag.citations import build_citation_payload, extract_citation_ids, validate_citations  # noqa: E402
from phase04.rag.context import build_evidence_pack  # noqa: E402
from phase04.rag.fusion import reciprocal_rank_fusion  # noqa: E402
from phase04.rag.router import QueryRouter  # noqa: E402
from phase04.rag.schemas import EvidenceDocument  # noqa: E402


def _doc(review_id: str, dense=0.0, sparse=0.0) -> EvidenceDocument:
    return EvidenceDocument(
        citation_id=0,
        review_id=review_id,
        external_review_id=review_id,
        rating=2,
        thumbs_up=5,
        device_type="phone",
        subscription_type="free",
        primary_issue="repetitive_recommendations",
        review_created_at=datetime(2026, 3, 1),
        text_en="Discover Weekly keeps repeating the same songs.",
        dense_score=dense,
        sparse_score=sparse,
    )


def test_reciprocal_rank_fusion_merges_lists():
    a = [_doc("a", dense=0.9), _doc("b", dense=0.5)]
    b = [_doc("b", sparse=0.8), _doc("c", sparse=0.7)]
    merged = reciprocal_rank_fusion([a, b])
    ids = [d.review_id for d in merged]
    assert ids[0] == "b"
    assert set(ids) == {"a", "b", "c"}


def test_validate_citations_valid():
    docs = [_doc("a"), _doc("b")]
    docs[0].citation_id = 1
    docs[1].citation_id = 2
    answer = "Users report repetition [1] and fatigue [2]."
    result = validate_citations(answer, docs)
    assert result.valid is True
    assert result.cited_ids == [1, 2]


def test_validate_citations_invalid_id():
    docs = [_doc("a")]
    docs[0].citation_id = 1
    result = validate_citations("Problem described [2].", docs)
    assert result.valid is False
    assert 2 in result.invalid_ids


def test_build_citation_payload():
    docs = [_doc("uuid-1")]
    docs[0].citation_id = 1
    payload = build_citation_payload(docs, [1])
    assert payload[0]["id"] == 1
    assert payload[0]["document_id"] == "uuid-1"


def test_router_heuristic_premium_filter():
    routed = QueryRouter(llm=None).route("What do Premium users complain about?")
    assert routed.filters.subscription_type == "premium"
    assert routed.intent == "why_complaint"


def test_build_evidence_pack_contains_citation_numbers():
    docs = [_doc("a"), _doc("b")]
    docs[0].citation_id = 1
    docs[1].citation_id = 2
    pack = build_evidence_pack(docs)
    assert "[1]" in pack
    assert "[2]" in pack
    assert "Discover Weekly" in pack


def test_extract_citation_ids_deduplicates():
    assert extract_citation_ids("See [1] and again [1] plus [2]") == [1, 2]
