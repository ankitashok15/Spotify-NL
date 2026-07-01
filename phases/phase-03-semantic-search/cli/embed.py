#!/usr/bin/env python3
"""Phase 3 CLI — embed reviews and index vectors in Qdrant."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from pathlib import Path

_PHASE03_ROOT = Path(__file__).resolve().parents[1]
_PHASE01_ROOT = _PHASE03_ROOT.parent / "phase-01-data-foundation"
_PHASE02_ROOT = _PHASE03_ROOT.parent / "phase-02-ai-understanding"
for path in (_PHASE01_ROOT, _PHASE02_ROOT, _PHASE03_ROOT):
    sys.path.insert(0, str(path))

from phase03.database.session import get_db_session  # noqa: E402
from phase03.embedding.indexer import QdrantIndexer  # noqa: E402
from phase03.pipeline import EmbedIndexPipeline  # noqa: E402
from phase03.shared.config import settings  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phase03.cli")


def cmd_init_qdrant(_: argparse.Namespace) -> None:
    indexer = QdrantIndexer()
    indexer.ensure_collection()
    logger.info("Qdrant collection ready: %s at %s", settings.qdrant_collection, settings.qdrant_url)


def cmd_embed(args: argparse.Namespace) -> None:
    if not settings.gemini_api_key:
        raise SystemExit("GEMINI_API_KEY is not set in .env")

    review_ids = None
    if args.review_ids:
        review_ids = [uuid.UUID(rid) for rid in args.review_ids.split(",")]

    with get_db_session() as session:
        pipeline = EmbedIndexPipeline(session)
        report = pipeline.run(
            batch_size=args.batch_size,
            limit=args.limit,
            review_ids=review_ids,
        )
        print(json.dumps(report.to_dict(), indent=2))


def cmd_status(_: argparse.Namespace) -> None:
    with get_db_session() as session:
        pipeline = EmbedIndexPipeline(session)
        print(json.dumps(pipeline.status(), indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Spotify NL Phase 3 — embeddings & vector index")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-qdrant", help="Create Qdrant collection and payload indexes")
    init_parser.set_defaults(func=cmd_init_qdrant)

    embed_parser = sub.add_parser("embed", help="Embed reviews and upsert to Qdrant")
    embed_parser.add_argument("--batch-size", type=int, default=settings.embed_batch_size)
    embed_parser.add_argument("--limit", type=int, default=None)
    embed_parser.add_argument("--review-ids", default=None, help="Comma-separated review UUIDs")
    embed_parser.set_defaults(func=cmd_embed)

    status_parser = sub.add_parser("status", help="Show embed/index progress")
    status_parser.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
