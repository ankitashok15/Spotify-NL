#!/usr/bin/env python3
"""Phase 6 API server — agent orchestrator."""

from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

_PHASE06_ROOT = Path(__file__).resolve().parents[1]
for name in (
    "phase-01-data-foundation",
    "phase-02-ai-understanding",
    "phase-03-semantic-search",
    "phase-04-rag-qa",
    "phase-05-clustering-insights",
    "phase-06-agentic-scale",
):
    sys.path.insert(0, str(_PHASE06_ROOT.parent / name))

from phase06.shared.config import settings  # noqa: E402


def main() -> None:
    uvicorn.run(
        "phase06.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
