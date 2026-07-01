#!/usr/bin/env python3
"""Phase 6 CLI — agent queries and incremental pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PHASE06_ROOT = Path(__file__).resolve().parents[1]
for name in (
    "phase-01-data-foundation",
    "phase-02-ai-understanding",
    "phase-03-semantic-search",
    "phase-04-rag-qa",
    "phase-05-clustering-insights",
    "phase-06-agentic-scale",
):
    sys.path.insert(0, str(_PHASE06_ROOT.parent / name))

from phase02.shared.llm_gemini import GeminiProvider  # noqa: E402
from phase06.agent.orchestrator import AgentOrchestrator  # noqa: E402
from phase06.database.models import init_phase6_tables  # noqa: E402
from phase06.database.repositories import AgentQueryRepository  # noqa: E402
from phase06.database.session import get_db_session  # noqa: E402
from phase06.orchestration.pipeline import IncrementalIngestionPipeline  # noqa: E402
from phase06.shared.config import settings  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phase06.cli")


def cmd_init_db(_: argparse.Namespace) -> None:
    init_phase6_tables(settings.database_url)
    logger.info("Phase 6 tables created (agent_queries)")


def cmd_query(args: argparse.Namespace) -> None:
    init_phase6_tables(settings.database_url)
    with get_db_session() as session:
        llm = GeminiProvider(model_name=settings.gemini_model_rag) if settings.gemini_api_key else None
        result = AgentOrchestrator(session, llm).run(args.question, debug=args.debug)
        AgentQueryRepository(session).log(args.question, result, include_trace=args.debug)
        print(json.dumps(result.to_dict(include_trace=args.debug), indent=2))


def cmd_pipeline(args: argparse.Namespace) -> None:
    init_phase6_tables(settings.database_url)
    with get_db_session() as session:
        if args.weekly:
            report = IncrementalIngestionPipeline(session).run_weekly()
        else:
            report = IncrementalIngestionPipeline(session).run(
                extract_limit=args.extract_limit,
                embed_limit=args.embed_limit,
                assign_limit=args.assign_limit,
                run_insights=args.insights,
            )
            report = report.to_dict()
        print(json.dumps(report, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Spotify NL Phase 6 — agent & scale")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-db", help="Create Phase 6 tables")
    init_parser.set_defaults(func=cmd_init_db)

    query_parser = sub.add_parser("query", help="Run multi-step agent on a question")
    query_parser.add_argument("question", help="Analytical question")
    query_parser.add_argument("--debug", action="store_true", help="Include tool trace")
    query_parser.set_defaults(func=cmd_query)

    pipe_parser = sub.add_parser("pipeline", help="Run incremental ingest pipeline")
    pipe_parser.add_argument("--extract-limit", type=int, default=200)
    pipe_parser.add_argument("--embed-limit", type=int, default=200)
    pipe_parser.add_argument("--assign-limit", type=int, default=200)
    pipe_parser.add_argument("--insights", action="store_true")
    pipe_parser.add_argument("--weekly", action="store_true", help="Full cluster + insights")
    pipe_parser.set_defaults(func=cmd_pipeline)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
