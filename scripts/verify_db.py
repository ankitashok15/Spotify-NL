#!/usr/bin/env python3
"""Verify PostgreSQL is reachable using DATABASE_URL from .env."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "phases" / "phase-01-data-foundation"))

from dotenv import dotenv_values  # noqa: E402

try:
    import psycopg2
except ImportError:
    print("Install dependencies: pip install -r requirements.txt")
    raise SystemExit(1)


def main() -> int:
    url = (dotenv_values(_REPO / ".env").get("DATABASE_URL") or "").strip()
    if not url:
        print("FAIL: DATABASE_URL is missing in .env")
        return 1

    try:
        conn = psycopg2.connect(url, connect_timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
    except Exception as exc:
        print("FAIL: Cannot connect to PostgreSQL")
        print(f"  URL host: {url.split('@')[1].split('/')[0] if '@' in url else 'invalid'}")
        print(f"  Error: {exc}")
        print()
        print("Next steps:")
        print("  1. Install PostgreSQL (see phases/phase-01-data-foundation/POSTGRES_SETUP.md)")
        print("  2. Run scripts/setup_postgres.sql as user postgres")
        print("  3. Re-run: python scripts/verify_db.py")
        return 1

    print("OK: PostgreSQL connection successful")
    print(f"  {version.split(',')[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
