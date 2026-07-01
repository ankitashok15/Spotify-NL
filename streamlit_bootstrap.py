"""Bootstrap paths and secrets for Streamlit Cloud and local .env."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

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

_CANONICAL_ALIASES: dict[str, tuple[str, ...]] = {
    "GEMINI_API_KEY": ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_APIKEY"),
    "DATABASE_URL": (
        "DATABASE_URL",
        "POSTGRES_URL",
        "NEON_DATABASE_URL",
        "DB_URL",
        "POSTGRESQL_URL",
    ),
    "QDRANT_URL": ("QDRANT_URL",),
    "QDRANT_API_KEY": ("QDRANT_API_KEY",),
    "QDRANT_COLLECTION": ("QDRANT_COLLECTION",),
    "GEMINI_MODEL": ("GEMINI_MODEL",),
    "GEMINI_MODEL_RAG": ("GEMINI_MODEL_RAG",),
    "GEMINI_EMBEDDING_MODEL": ("GEMINI_EMBEDDING_MODEL",),
    "SPOTIFY_APP_ID": ("SPOTIFY_APP_ID",),
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
                db_url = _postgres_url_from_section(value)
                if db_url:
                    out.setdefault("DATABASE_URL", db_url)
            else:
                out[full] = str(value)
    return out


def _postgres_url_from_section(section: dict) -> str:
    for key in ("url", "URL", "database_url", "DATABASE_URL"):
        raw = section.get(key)
        if raw and str(raw).strip():
            return str(raw).strip()

    host = section.get("host") or section.get("HOST")
    if not host:
        return ""

    user = str(section.get("username") or section.get("user") or section.get("USERNAME") or "")
    password = str(section.get("password") or section.get("PASSWORD") or "")
    port = section.get("port") or section.get("PORT") or 5432
    database = str(
        section.get("database")
        or section.get("dbname")
        or section.get("DATABASE")
        or section.get("DBNAME")
        or "postgres"
    )
    auth = ""
    if user:
        auth = quote_plus(user)
        if password:
            auth += f":{quote_plus(password)}"
        auth += "@"
    return f"postgresql://{auth}{host}:{port}/{database}"


def _streamlit_secrets_dict() -> dict:
    try:
        import streamlit as st

        return dict(st.secrets)
    except Exception:
        return {}


def _collect_secret_values() -> dict[str, str]:
    """Merge top-level secrets, nested sections, and flattened keys."""
    raw = _streamlit_secrets_dict()
    collected: dict[str, str] = {}

    # Top-level keys (Streamlit Secrets panel uses these directly)
    for key, value in raw.items():
        if isinstance(value, (str, int, float, bool)):
            collected[str(key).upper()] = str(value)

    collected.update(_flatten_secrets(raw))

    # Suffix / alias match: e.g. CONNECTIONS_POSTGRESQL_DATABASE_URL -> DATABASE_URL
    for canonical, aliases in _CANONICAL_ALIASES.items():
        if collected.get(canonical, "").strip():
            continue
        for alias in aliases:
            if collected.get(alias, "").strip():
                collected[canonical] = collected[alias].strip()
                break
        if collected.get(canonical, "").strip():
            continue
        for key, value in collected.items():
            if not value.strip():
                continue
            if key == canonical or key.endswith(f"_{canonical}") or key in aliases:
                collected[canonical] = value.strip()
                break

    return collected


def apply_secrets() -> None:
    """Load local .env then Streamlit Cloud secrets into os.environ."""
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env", override=False)
    except ImportError:
        pass

    for key, value in _collect_secret_values().items():
        if value and value.strip():
            os.environ[key] = value.strip()

    for target, sources in _CANONICAL_ALIASES.items():
        if os.environ.get(target, "").strip():
            continue
        for src in sources:
            val = os.environ.get(src, "").strip()
            if val:
                os.environ[target] = val
                break


def init_runtime() -> None:
    """Call once at the top of every Streamlit page before phase imports."""
    apply_secrets()
    reload_phase_settings()


def reload_phase_settings() -> None:
    """Recreate phase Settings singletons from the current environment."""
    import importlib

    for module_name in (
        "phase01.shared.config",
        "phase02.shared.config",
        "phase03.shared.config",
        "phase04.shared.config",
        "phase05.shared.config",
        "phase06.shared.config",
    ):
        try:
            if module_name in sys.modules:
                mod = sys.modules[module_name]
            else:
                mod = importlib.import_module(module_name)
            mod.settings = mod.Settings()
        except Exception:
            continue


def _config_value(key: str) -> str:
    apply_secrets()
    return os.environ.get(key, "").strip()


def gemini_key_configured() -> bool:
    return bool(_config_value("GEMINI_API_KEY"))


def _is_local_url(value: str) -> bool:
    v = (value or "").strip().lower()
    if not v:
        return True
    return any(h in v for h in ("localhost", "127.0.0.1", "::1"))


def deploy_config_issues() -> list[str]:
    """Return human-readable config problems for Streamlit Cloud."""
    issues: list[str] = []
    if _is_local_url(_config_value("DATABASE_URL")):
        issues.append(
            "DATABASE_URL is missing or points to localhost. "
            "Set a **cloud PostgreSQL** URL in Streamlit Cloud → Settings → Secrets."
        )
    if _is_local_url(_config_value("QDRANT_URL")):
        issues.append(
            "QDRANT_URL is missing or points to localhost. "
            "Set your **Qdrant Cloud** URL (and QDRANT_API_KEY) in Streamlit secrets."
        )
    if not _config_value("QDRANT_API_KEY") and not _is_local_url(_config_value("QDRANT_URL")):
        issues.append(
            "QDRANT_API_KEY is missing. Add it in Streamlit Cloud → Settings → Secrets."
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

    raw = _streamlit_secrets_dict()
    if raw:
        top_keys = [str(k) for k in raw.keys()]
        st.caption(f"Secrets sections/keys detected: `{', '.join(top_keys)}`")
    else:
        st.warning(
            "No Streamlit secrets detected. Open **Settings → Secrets**, paste the TOML block, "
            "click **Save**, then **Reboot app**."
        )

    st.code(
        """GEMINI_API_KEY = "your-key"
DATABASE_URL = "postgresql://user:pass@host.neon.tech/neondb?sslmode=require"
QDRANT_URL = "https://xxxx.cloud.qdrant.io"
QDRANT_API_KEY = "your-qdrant-key"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_MODEL_RAG = "gemini-2.5-flash"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
QDRANT_COLLECTION = "spotify_reviews"
SPOTIFY_APP_ID = "com.spotify.music\"""",
        language="toml",
    )

    st.markdown(
        """
        **Checklist**
        1. Use **TOML** format above (quotes required, `KEY = "value"` — not `.env` `KEY=value`)
        2. Keys must be at the **top level** (no `[section]` headers unless using nested postgres config)
        3. Click **Save** → **⋮ Reboot app**
        4. `.env` on your PC is **not** uploaded to Streamlit — secrets must be pasted here
        """
    )
