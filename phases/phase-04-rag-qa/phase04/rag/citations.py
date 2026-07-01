from __future__ import annotations

import re
from dataclasses import dataclass, field

from phase04.rag.schemas import EvidenceDocument

_CITATION = re.compile(r"\[(\d+)\]")


@dataclass
class CitationValidation:
    valid: bool
    cited_ids: list[int] = field(default_factory=list)
    invalid_ids: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def extract_citation_ids(answer: str) -> list[int]:
    return sorted({int(m) for m in _CITATION.findall(answer)})


def validate_citations(answer: str, documents: list[EvidenceDocument]) -> CitationValidation:
    valid_ids = {doc.citation_id for doc in documents}
    cited = extract_citation_ids(answer)
    invalid = [cid for cid in cited if cid not in valid_ids]
    warnings: list[str] = []

    if not cited and documents:
        warnings.append("Answer contains no [n] citations despite available evidence.")

    unsupported = []
    for cid in invalid:
        unsupported.append(f"Citation [{cid}] does not map to retrieved evidence.")

    return CitationValidation(
        valid=len(invalid) == 0 and (bool(cited) or not documents),
        cited_ids=cited,
        invalid_ids=invalid,
        warnings=warnings + unsupported,
    )


def build_citation_payload(documents: list[EvidenceDocument], cited_ids: list[int]) -> list[dict]:
    by_id = {doc.citation_id: doc for doc in documents}
    payload: list[dict] = []
    for cid in cited_ids:
        doc = by_id.get(cid)
        if not doc:
            continue
        payload.append(
            {
                "id": cid,
                "document_id": doc.review_id,
                "external_review_id": doc.external_review_id,
                "rating": doc.rating,
                "thumbs_up": doc.thumbs_up,
                "device_type": doc.device_type,
                "subscription_type": doc.subscription_type,
                "primary_issue": doc.primary_issue,
                "excerpt": doc.excerpt,
                "review_created_at": (
                    doc.review_created_at.isoformat() if doc.review_created_at else None
                ),
            }
        )
    return payload
