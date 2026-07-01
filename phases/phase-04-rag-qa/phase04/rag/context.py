from __future__ import annotations

from phase04.rag.schemas import EvidenceDocument


def _format_date(doc: EvidenceDocument) -> str:
    if doc.review_created_at:
        return doc.review_created_at.date().isoformat()
    return "unknown"


def build_evidence_pack(documents: list[EvidenceDocument]) -> str:
    if not documents:
        return "(No evidence retrieved)"

    lines: list[str] = []
    for doc in documents:
        rating = doc.rating if doc.rating is not None else "?"
        sub = doc.subscription_type or "unknown"
        device = doc.device_type or "unknown"
        issues = doc.primary_issue or "none"
        emotions = ", ".join(doc.emotions) if doc.emotions else "none"
        pain = ", ".join(doc.pain_points[:3]) if doc.pain_points else "none"
        lines.append(
            f"[{doc.citation_id}] Google Play | ★{rating}/5 | {doc.thumbs_up} helpful | "
            f"{device} | {sub} user | {_format_date(doc)}\n"
            f'    "{doc.text_en.strip()[:600]}"\n'
            f"    Issues: {issues}\n"
            f"    Emotion: {emotions}\n"
            f"    Pain points: {pain}"
        )
    return "\n\n".join(lines)
