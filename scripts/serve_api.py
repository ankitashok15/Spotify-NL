#!/usr/bin/env python3
"""Run the unified Spotify NL API server."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from backend.cli.serve import main

if __name__ == "__main__":
    main()
