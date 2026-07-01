"""Bootstrap paths and secrets for Streamlit Cloud."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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

sys.path.insert(0, str(ROOT / "backend"))


def apply_secrets() -> None:
    """Map Streamlit Cloud secrets into os.environ for phase settings."""
    try:
        import streamlit as st

        secrets = dict(st.secrets)
    except Exception:
        return

    for key, value in secrets.items():
        if isinstance(value, str):
            os.environ.setdefault(key, value)
