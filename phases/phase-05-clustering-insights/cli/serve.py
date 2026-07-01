#!/usr/bin/env python3
"""Phase 5 API server — clusters, insights, trends."""

from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

_PHASE05_ROOT = Path(__file__).resolve().parents[1]
for name in (
    "phase-01-data-foundation",
    "phase-02-ai-understanding",
    "phase-03-semantic-search",
    "phase-04-rag-qa",
    "phase-05-clustering-insights",
):
    sys.path.insert(0, str(_PHASE05_ROOT.parent / name))

from phase05.shared.config import settings  # noqa: E402


def main() -> None:
    uvicorn.run(
        "phase05.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
