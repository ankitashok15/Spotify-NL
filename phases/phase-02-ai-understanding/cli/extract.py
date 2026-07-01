#!/usr/bin/env python3
"""Phase 2 CLI — language detection, translation, Gemini structured extraction."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from pathlib import Path

_PHASE02_ROOT = Path(__file__).resolve().parents[1]
_PHASE01_ROOT = _PHASE02_ROOT.parent / "phase-01-data-foundation"
sys.path.insert(0, str(_PHASE01_ROOT))
sys.path.insert(0, str(_PHASE02_ROOT))

from phase02.database.models import init_phase2_tables  # noqa: E402
from phase02.database.session import get_db_session  # noqa: E402
from phase02.extraction.pipeline import ExtractionPipeline  # noqa: E402
from phase02.shared.config import settings  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phase02.cli")


def cmd_init_db(_: argparse.Namespace) -> None:
    init_phase2_tables(settings.database_url)
    logger.info("Phase 2 tables created (structured_reviews, extraction_cache)")


def cmd_extract(args: argparse.Namespace) -> None:
    if not settings.gemini_api_key:
        raise SystemExit("GEMINI_API_KEY is not set in .env")

    init_phase2_tables(settings.database_url)
    review_ids = None
    if args.review_ids:
        review_ids = [uuid.UUID(rid) for rid in args.review_ids.split(",")]

    with get_db_session() as session:
        pipeline = ExtractionPipeline(session)
        report = pipeline.run(
            batch_size=args.batch_size,
            limit=args.limit,
            review_ids=review_ids,
            skip_spam=not args.include_spam,
        )
        print(json.dumps(report.to_dict(), indent=2))


def cmd_status(_: argparse.Namespace) -> None:
    init_phase2_tables(settings.database_url)
    with get_db_session() as session:
        pipeline = ExtractionPipeline(session)
        print(json.dumps(pipeline.status(), indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Spotify NL Phase 2 — AI extraction")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-db", help="Create Phase 2 database tables")
    init_parser.set_defaults(func=cmd_init_db)

    extract_parser = sub.add_parser("extract", help="Run Gemini extraction pipeline")
    extract_parser.add_argument("--batch-size", type=int, default=settings.extract_batch_size)
    extract_parser.add_argument("--limit", type=int, default=None, help="Max reviews to process")
    extract_parser.add_argument(
        "--review-ids",
        default=None,
        help="Comma-separated review UUIDs (optional)",
    )
    extract_parser.add_argument(
        "--include-spam",
        action="store_true",
        help="Include reviews flagged as spam",
    )
    extract_parser.set_defaults(func=cmd_extract)

    status_parser = sub.add_parser("status", help="Show extraction progress")
    status_parser.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
