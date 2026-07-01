#!/usr/bin/env python3
"""Phase 5 CLI — clustering, insights, and trends."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PHASE05_ROOT = Path(__file__).resolve().parents[1]
for name in (
    "phase-01-data-foundation",
    "phase-02-ai-understanding",
    "phase-03-semantic-search",
    "phase-04-rag-qa",
    "phase-05-clustering-insights",
):
    sys.path.insert(0, str(_PHASE05_ROOT.parent / name))

from phase05.database.models import init_phase5_tables  # noqa: E402
from phase05.database.session import get_db_session  # noqa: E402
from phase05.pipeline import ClusteringPipeline, IncrementalPipeline, InsightsPipeline  # noqa: E402
from phase05.shared.config import settings  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phase05.cli")


def cmd_init_db(_: argparse.Namespace) -> None:
    init_phase5_tables(settings.database_url)
    logger.info("Phase 5 tables created (clusters, cluster_memberships, insights)")


def cmd_cluster(args: argparse.Namespace) -> None:
    init_phase5_tables(settings.database_url)
    with get_db_session() as session:
        pipeline = ClusteringPipeline(session)
        report = pipeline.run_full(vector_limit=args.limit)
        print(json.dumps(report.to_dict(), indent=2))


def cmd_assign(args: argparse.Namespace) -> None:
    init_phase5_tables(settings.database_url)
    with get_db_session() as session:
        result = IncrementalPipeline(session).run(limit=args.limit)
        print(json.dumps(result, indent=2))


def cmd_insights(_: argparse.Namespace) -> None:
    init_phase5_tables(settings.database_url)
    with get_db_session() as session:
        result = InsightsPipeline(session).run()
        print(json.dumps(result, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Spotify NL Phase 5 — clustering & insights")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-db", help="Create Phase 5 tables")
    init_parser.set_defaults(func=cmd_init_db)

    cluster_parser = sub.add_parser("cluster", help="Run full clustering on Qdrant vectors")
    cluster_parser.add_argument("--limit", type=int, default=None, help="Max vectors to cluster")
    cluster_parser.set_defaults(func=cmd_cluster)

    assign_parser = sub.add_parser("assign", help="Incrementally assign new reviews to clusters")
    assign_parser.add_argument("--limit", type=int, default=200)
    assign_parser.set_defaults(func=cmd_assign)

    insights_parser = sub.add_parser("insights", help="Generate and persist insight records")
    insights_parser.set_defaults(func=cmd_insights)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
