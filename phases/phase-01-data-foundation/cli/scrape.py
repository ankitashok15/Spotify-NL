#!/usr/bin/env python3
"""Phase 1 CLI — scrape Google Play reviews for Spotify."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add phase-01 package to path
_PHASE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PHASE_ROOT))

from phase01.database.models import init_db  # noqa: E402
from phase01.database.session import get_db_session  # noqa: E402
from phase01.scrape.scraper import GooglePlayReviewScraper  # noqa: E402
from phase01.shared.config import settings  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phase01.cli")


def cmd_init_db(_: argparse.Namespace) -> None:
    init_db(settings.database_url)
    logger.info("Database tables created at %s", settings.database_url)


def cmd_scrape(args: argparse.Namespace) -> None:
    init_db(settings.database_url)
    app_id = args.app_id or settings.spotify_app_id
    months_back = args.months_back or settings.scrape_months_back

    with get_db_session() as session:
        scraper = GooglePlayReviewScraper(session)

        if args.validate:
            report = scraper.validate_corpus(app_id, months_back=months_back)
            print(json.dumps(report.to_dict(), indent=2, default=str))
            return

        if args.resume:
            run_id = scraper.resume(app_id, months_back=months_back)
            logger.info("Resume complete. run_id=%s", run_id)
            return

        if args.since:
            since = datetime.fromisoformat(args.since)
            run_id = scraper.scrape_incremental(
                since, app_id=app_id, limit=args.limit, months_back=months_back
            )
            logger.info("Incremental scrape complete. run_id=%s", run_id)
            return

        if args.mode in ("full", "window"):
            logger.info("Scraping reviews from the last %s months", months_back)
            run_id = scraper.scrape_all(
                app_id=app_id, limit=args.limit, months_back=months_back
            )
            logger.info("Window scrape complete. run_id=%s", run_id)
            return

        raise SystemExit("Specify --mode window, --resume, --validate, or --since")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Spotify NL Phase 1 — Google Play scraper")
    sub = parser.add_subparsers(dest="command")

    init_parser = sub.add_parser("init-db", help="Create database tables")
    init_parser.set_defaults(func=cmd_init_db)

    scrape_parser = sub.add_parser("scrape", help="Scrape reviews (default: last 6 months)")
    scrape_parser.add_argument("--app-id", default=None, help="Play Store app id")
    scrape_parser.add_argument(
        "--mode",
        choices=["window", "full", "incremental"],
        default="window",
        help="window/full = last N months; incremental = since date",
    )
    scrape_parser.add_argument("--months-back", type=int, default=None, help="Rolling window in months (default: 6)")
    scrape_parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    scrape_parser.add_argument("--validate", action="store_true", help="Validate window + dedup")
    scrape_parser.add_argument("--since", help="Incremental: ISO date YYYY-MM-DD")
    scrape_parser.add_argument("--limit", type=int, default=None, help="Max reviews (dev subset)")
    scrape_parser.set_defaults(func=cmd_scrape)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        raise SystemExit(1)
    args.func(args)


if __name__ == "__main__":
    main()
