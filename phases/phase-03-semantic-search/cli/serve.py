#!/usr/bin/env python3
"""Phase 3 API server — semantic search."""

from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

_PHASE03_ROOT = Path(__file__).resolve().parents[1]
_PHASE01_ROOT = _PHASE03_ROOT.parent / "phase-01-data-foundation"
_PHASE02_ROOT = _PHASE03_ROOT.parent / "phase-02-ai-understanding"
for path in (_PHASE01_ROOT, _PHASE02_ROOT, _PHASE03_ROOT):
    sys.path.insert(0, str(path))

from phase03.shared.config import settings  # noqa: E402


def main() -> None:
    uvicorn.run(
        "phase03.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
