#!/usr/bin/env python3
"""Phase 4 CLI — ask RAG questions from the terminal."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PHASE04_ROOT = Path(__file__).resolve().parents[1]
for name in ("phase-01-data-foundation", "phase-02-ai-understanding", "phase-03-semantic-search", "phase-04-rag-qa"):
    sys.path.insert(0, str(_PHASE04_ROOT.parent / name))

from phase04.database.models import init_phase4_tables  # noqa: E402
from phase04.database.repositories import QueryLogRepository  # noqa: E402
from phase04.database.session import get_db_session  # noqa: E402
from phase04.rag.pipeline import RAGPipeline  # noqa: E402
from phase04.shared.config import settings  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phase04.cli")


def cmd_init_db(_: argparse.Namespace) -> None:
    init_phase4_tables(settings.database_url)
    logger.info("Phase 4 tables created (queries audit log)")


def cmd_ask(args: argparse.Namespace) -> None:
    if not settings.gemini_api_key:
        raise SystemExit("GEMINI_API_KEY is not set in .env")

    init_phase4_tables(settings.database_url)
    with get_db_session() as session:
        pipeline = RAGPipeline(session)
        result = pipeline.query(args.question, skip_llm_router=args.skip_router)
        if not args.no_log:
            QueryLogRepository(session).log(args.question, result)
        print(json.dumps(result.to_dict(), indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Spotify NL Phase 4 — RAG Q&A")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-db", help="Create queries audit table")
    init_parser.set_defaults(func=cmd_init_db)

    ask_parser = sub.add_parser("ask", help="Ask a grounded question")
    ask_parser.add_argument("question", help="Natural language question")
    ask_parser.add_argument("--skip-router", action="store_true", help="Use heuristic router only")
    ask_parser.add_argument("--no-log", action="store_true", help="Skip query audit log")
    ask_parser.set_defaults(func=cmd_ask)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
