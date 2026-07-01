#!/usr/bin/env python3
"""Run the unified Spotify NL API server."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

import uvicorn

from backend.app.config import settings


def main() -> None:
    port = int(os.environ.get("PORT", settings.api_port))
    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
