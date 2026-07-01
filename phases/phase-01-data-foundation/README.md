# Phase 1 — Data Foundation

Scrape **last 6 months** of Spotify Google Play reviews (`com.spotify.music`), clean, and store in PostgreSQL.

## Review window

| Setting | Default | Description |
|---------|---------|-------------|
| `SCRAPE_MONTHS_BACK` | `6` | Rolling window in months |
| Cutoff | `now - 180 days` | Reviews older than this are **skipped** |

## Quick start

```bash
pip install -r requirements.txt
cd phases/phase-01-data-foundation
docker compose up -d
python cli/scrape.py init-db
python cli/scrape.py scrape --limit 50          # dev test
python cli/scrape.py scrape --mode window       # full 6-month window
python cli/scrape.py scrape --validate
```

## Package layout

| Path | Purpose |
|------|---------|
| `phase01/scrape/window.py` | 6-month cutoff + filtering |
| `phase01/scrape/scraper.py` | Window-aware orchestrator |
| `phase01/cleaning/` | Normalization pipeline |
| `phase01/database/` | SQLAlchemy models, repositories |
| `phase01/api/` | FastAPI REST endpoints |
| `cli/scrape.py` | CLI entry point |

## Docs

- [REQUIREMENTS.md](./REQUIREMENTS.md)
- [RUNBOOK.md](./RUNBOOK.md)
- [../../docs/ragarchitecture.md](../../docs/ragarchitecture.md)
