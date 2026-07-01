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


def _is_local_url(value: str) -> bool:
    v = (value or "").strip().lower()
    if not v:
        return True
    return any(h in v for h in ("localhost", "127.0.0.1", "::1"))


def deploy_config_issues() -> list[str]:
    """Return human-readable config problems for Streamlit Cloud."""
    issues: list[str] = []
    if _is_local_url(os.environ.get("DATABASE_URL", "")):
        issues.append(
            "DATABASE_URL is missing or points to localhost. "
            "Set a **cloud PostgreSQL** URL in Streamlit Cloud → Settings → Secrets."
        )
    if _is_local_url(os.environ.get("QDRANT_URL", "")):
        issues.append(
            "QDRANT_URL is missing or points to localhost. "
            "Set your **Qdrant Cloud** URL (and QDRANT_API_KEY) in Streamlit secrets."
        )
    if not gemini_key_configured():
        issues.append(
            "GEMINI_API_KEY is missing. Add it in Streamlit Cloud → Settings → Secrets."
        )
    return issues


def render_deploy_config_help() -> None:
    """Show setup instructions when cloud secrets are not configured."""
    import streamlit as st

    for msg in deploy_config_issues():
        st.error(msg)
    st.markdown(
        """
        **Why this happens:** Streamlit Cloud runs on remote servers. It cannot connect to
        `localhost` on your PC. You need hosted PostgreSQL and Qdrant.

        1. Create a free DB at [Neon](https://neon.tech) or [Supabase](https://supabase.com)
        2. Use your [Qdrant Cloud](https://cloud.qdrant.io) cluster URL + API key
        3. Paste all values in **Streamlit Cloud → Settings → Secrets** (see `.streamlit/secrets.toml.example`)
        4. Click **Save** → **Reboot app**
        5. From your PC, point `.env` at the same cloud URLs and run scrape / extract / index scripts to load data
        """
    )
