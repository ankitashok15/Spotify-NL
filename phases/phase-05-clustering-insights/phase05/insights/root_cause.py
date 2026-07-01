from __future__ import annotations

import json
import logging

from phase02.shared.llm_gemini import GeminiProvider
from phase05.shared.config import settings

logger = logging.getLogger(__name__)


class RootCauseSynthesizer:
    def __init__(self, llm: GeminiProvider | None = None):
        self.llm = llm

    def synthesize(self, cluster_label: str, evidence_texts: list[str], *, evidence_ids: list[str]) -> dict:
        if not evidence_texts:
            return {
                "summary": "Insufficient evidence for root cause synthesis.",
                "confidence": 0.0,
                "evidence_document_ids": [],
            }

        if self.llm is None or not settings.gemini_api_key:
            return {
                "summary": (
                    f"Users repeatedly report issues related to '{cluster_label}'. "
                    f"Representative complaints mention: {evidence_texts[0][:200]}"
                ),
                "confidence": 0.6,
                "evidence_document_ids": evidence_ids[:5],
            }

        try:
            payload = self.llm.generate_json(
                json.dumps(
                    {
                        "cluster_label": cluster_label,
                        "evidence_reviews": evidence_texts[:10],
                        "evidence_ids": evidence_ids[:10],
                    },
                    ensure_ascii=False,
                ),
                system="Synthesize root cause patterns from Spotify review evidence. Return JSON with summary, confidence, evidence_document_ids.",
            )
            return {
                "summary": payload.get("summary", ""),
                "confidence": float(payload.get("confidence", 0.7)),
                "evidence_document_ids": payload.get("evidence_document_ids", evidence_ids[:5]),
            }
        except Exception as exc:
            logger.warning("Root cause synthesis failed: %s", exc)
            return {
                "summary": f"Pattern detected around {cluster_label} based on {len(evidence_texts)} reviews.",
                "confidence": 0.5,
                "evidence_document_ids": evidence_ids[:5],
            }
