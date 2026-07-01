"""Bootstrap paths and secrets for Streamlit Cloud and local .env."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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

_backend = str(ROOT / "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)

_ALIASES = {
    "GEMINI_API_KEY": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "DATABASE_URL": ("DATABASE_URL", "POSTGRES_URL"),
    "QDRANT_URL": ("QDRANT_URL",),
}


def _flatten_secrets(obj: object, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            upper = str(key).upper()
            full = f"{prefix}{upper}" if prefix else upper
            if isinstance(value, dict):
                out.update(_flatten_secrets(value, f"{full}_"))
                if full == "GEMINI" and "API_KEY" in value:
                    out["GEMINI_API_KEY"] = str(value["API_KEY"])
            else:
                out[full] = str(value)
    return out


def apply_secrets() -> None:
    """Load local .env then Streamlit Cloud secrets into os.environ."""
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env", override=False)
    except ImportError:
        pass

    try:
        import streamlit as st

        flat = _flatten_secrets(dict(st.secrets))
        for key, value in flat.items():
            if value:
                os.environ[key] = value
        for target, sources in _ALIASES.items():
            if os.environ.get(target):
                continue
            for src in sources:
                if os.environ.get(src):
                    os.environ[target] = os.environ[src]
                    break
    except Exception:
        pass


def init_runtime() -> None:
    """Call once at the top of every Streamlit page before phase imports."""
    apply_secrets()


def gemini_key_configured() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())
