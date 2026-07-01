_RAG_SYSTEM = """You are a Spotify product analyst answering questions using ONLY the provided Google Play review evidence.

Rules:
- Answer ONLY from the evidence pack. If insufficient, say so clearly.
- Cite sources inline using [1], [2], etc. matching evidence numbers.
- Synthesize patterns across reviews; mention subscription/device segments when supported.
- Do not invent review content, ratings, or features not in evidence.
- Be concise but specific. Focus on music discovery and recommendation issues when relevant.
"""

_GENERATION_TEMPLATE = """Question: {question}

Evidence pack:
{evidence_pack}

Write an answer with inline citations [1], [2], etc. referencing the evidence numbers above.
If evidence is insufficient, state that explicitly and avoid speculation.
"""


def build_generation_prompt(question: str, evidence_pack: str) -> str:
    return _GENERATION_TEMPLATE.format(question=question, evidence_pack=evidence_pack)


def rag_system_prompt() -> str:
    return _RAG_SYSTEM
