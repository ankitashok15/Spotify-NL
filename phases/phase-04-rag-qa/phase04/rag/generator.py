from __future__ import annotations

import logging

from phase02.shared.llm_gemini import GeminiProvider
from phase04.rag.prompts import build_generation_prompt, rag_system_prompt
from phase04.rag.schemas import EvidenceDocument
from phase04.shared.config import settings

logger = logging.getLogger(__name__)


class RAGGenerator:
    def __init__(self, llm: GeminiProvider | None = None):
        self.llm = llm or GeminiProvider(model_name=settings.gemini_model_rag)

    def generate(self, question: str, evidence_pack: str, documents: list[EvidenceDocument]) -> str:
        if not documents:
            return (
                "Insufficient evidence: no relevant Google Play reviews were retrieved for this question. "
                "Try broadening filters or indexing more reviews."
            )

        prompt = build_generation_prompt(question, evidence_pack)
        try:
            return self.llm.generate_text(prompt, system=rag_system_prompt())
        except Exception as exc:
            logger.exception("RAG generation failed")
            return f"Unable to generate answer: {exc}"
