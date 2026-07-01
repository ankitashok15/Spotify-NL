#!/usr/bin/env python3
"""Run Phase 1 FastAPI server."""

import sys
from pathlib import Path

import uvicorn

_PHASE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PHASE_ROOT))

from phase01.shared.config import settings  # noqa: E402

if __name__ == "__main__":
    uvicorn.run(
        "phase01.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
