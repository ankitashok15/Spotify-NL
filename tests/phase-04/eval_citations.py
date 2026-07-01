"""Citation accuracy helpers for Phase 4 eval runs."""

from __future__ import annotations

import json
import re
from pathlib import Path

from phase04.rag.citations import extract_citation_ids, validate_citations
from phase04.rag.schemas import EvidenceDocument

_CITATION = re.compile(r"\[(\d+)\]")


def score_citation_validity(answer: str, evidence: list[dict]) -> dict:
    docs = [
        EvidenceDocument(
            citation_id=item["citation_id"],
            review_id=item["review_id"],
            external_review_id=item.get("external_review_id"),
            rating=item.get("rating"),
            thumbs_up=item.get("thumbs_up", 0),
            device_type=item.get("device_type"),
            subscription_type=item.get("subscription_type"),
            primary_issue=item.get("primary_issue"),
            text_en=item.get("text_en", ""),
        )
        for item in evidence
    ]
    validation = validate_citations(answer, docs)
    return {
        "valid": validation.valid,
        "cited_ids": validation.cited_ids,
        "invalid_ids": validation.invalid_ids,
        "warnings": validation.warnings,
        "citation_count": len(extract_citation_ids(answer)),
    }


if __name__ == "__main__":
    sample = Path(__file__).parent / "eval_rag.json"
    print(json.dumps({"eval_file": str(sample), "status": "import score_citation_validity for eval loops"}, indent=2))
