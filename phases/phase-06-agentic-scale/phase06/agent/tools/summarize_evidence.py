from __future__ import annotations

import json
import logging
import os

from sqlalchemy import text
from sqlalchemy.orm import Session

from phase02.shared.llm_gemini import GeminiProvider
from phase06.agent.tools.base import AgentTool
from phase06.shared.config import settings

logger = logging.getLogger(__name__)


class SummarizeEvidenceTool(AgentTool):
    name = "summarize_evidence"
    description = "Synthesize findings from review IDs with citations."

    def __init__(self, session: Session, llm: GeminiProvider | None = None) -> None:
        self.session = session
        self.llm = llm

    def run(self, args: dict) -> dict:
        review_ids = args.get("review_ids") or args.get("document_ids") or []
        context = args.get("context") or args.get("question") or ""
        if not review_ids:
            observations = args.get("observations") or []
            for obs in observations:
                if isinstance(obs, list):
                    for item in obs:
                        if isinstance(item, dict) and item.get("review_id"):
                            review_ids.append(item["review_id"])
                elif isinstance(obs, dict):
                    for key in ("member_review_ids", "representative_review_ids"):
                        review_ids.extend(obs.get(key) or [])
            review_ids = list(dict.fromkeys(review_ids))[:15]

        evidence = self._load_reviews(review_ids[:20])
        if not evidence:
            return {
                "summary": "No review evidence available to summarize.",
                "citations": [],
                "confidence": 0.0,
            }

        if self.llm is None or not (
            os.environ.get("GEMINI_API_KEY") or settings.gemini_api_key
        ):
            return self._fallback_summary(evidence, context)

        try:
            payload = self.llm.generate_json(
                json.dumps({"context": context, "reviews": evidence}, ensure_ascii=False),
                system=(
                    "Synthesize product research findings from Spotify Play Store reviews. "
                    "Return JSON: summary (markdown), citations [{review_id, quote, rating}], confidence (0-1)."
                ),
            )
            return {
                "summary": payload.get("summary", ""),
                "citations": payload.get("citations", []),
                "confidence": float(payload.get("confidence", 0.7)),
            }
        except Exception as exc:
            logger.warning("summarize_evidence LLM failed: %s", exc)
            return self._fallback_summary(evidence, context)

    def _load_reviews(self, review_ids: list) -> list[dict]:
        if not review_ids:
            return []
        rows = self.session.execute(
            text(
                """
                SELECT
                    r.id::text AS review_id,
                    r.rating,
                    r.device_type,
                    COALESCE(sr.subscription_type, 'unknown') AS subscription_type,
                    sr.primary_issue,
                    COALESCE(sr.text_en, r.text_cleaned, r.text_original, '') AS text_en
                FROM reviews r
                LEFT JOIN structured_reviews sr ON sr.review_id = r.id
                WHERE r.id::text = ANY(:ids)
                """
            ),
            {"ids": [str(rid) for rid in review_ids]},
        ).mappings().all()
        return [dict(row) for row in rows]

    def _fallback_summary(self, evidence: list[dict], context: str) -> dict:
        citations = []
        for row in evidence[:5]:
            text_en = (row.get("text_en") or "")[:200]
            citations.append(
                {
                    "review_id": row["review_id"],
                    "quote": text_en,
                    "rating": row.get("rating"),
                }
            )
        summary = (
            f"Based on {len(evidence)} reviews"
            + (f" regarding: {context}" if context else "")
            + f". Top themes include {evidence[0].get('primary_issue', 'discovery issues')}."
        )
        return {"summary": summary, "citations": citations, "confidence": 0.55}
