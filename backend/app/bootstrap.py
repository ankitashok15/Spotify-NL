"""Add all phase packages to sys.path before imports."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASES = ROOT / "phases"

for folder in (
    "phase-01-data-foundation",
    "phase-02-ai-understanding",
    "phase-03-semantic-search",
    "phase-04-rag-qa",
    "phase-05-clustering-insights",
    "phase-06-agentic-scale",
):
    path = str(PHASES / folder)
    if path not in sys.path:
        sys.path.insert(0, path)
