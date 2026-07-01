#!/usr/bin/env python3
"""Create all database tables (Phases 1–6) using DATABASE_URL from .env."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_PHASES = (
    "phase-01-data-foundation",
    "phase-02-ai-understanding",
    "phase-03-semantic-search",
    "phase-04-rag-qa",
    "phase-05-clustering-insights",
    "phase-06-agentic-scale",
)
for folder in _PHASES:
    sys.path.insert(0, str(_REPO / "phases" / folder))

from dotenv import dotenv_values, load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env", override=True)

from phase06.database.models import init_phase6_tables  # noqa: E402


def _resolve_database_url() -> str:
    file_env = dotenv_values(_REPO / ".env")
    url = (file_env.get("DATABASE_URL") or "").strip()
    if url:
        return url
    from phase06.shared.config import settings

    return settings.database_url


def main() -> int:
    url = _resolve_database_url()
    host = url.split("@")[-1] if "@" in url else url
    if "localhost" in url and "neon" not in url.lower():
        print(f"Initializing local database: {host}")
    else:
        print(f"Initializing cloud database: {host.split('/')[0]}")
    init_phase6_tables(url)
    print("OK: All tables created (reviews, structured_reviews, clusters, insights, …)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
