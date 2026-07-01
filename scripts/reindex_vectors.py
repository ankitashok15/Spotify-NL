#!/usr/bin/env python3
"""Blue-green style reindex across year-partitioned Qdrant collections."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for name in (
    "phase-01-data-foundation",
    "phase-02-ai-understanding",
    "phase-03-semantic-search",
    "phase-06-agentic-scale",
):
    sys.path.insert(0, str(_REPO / "phases" / name))

from phase03.database.session import get_db_session  # noqa: E402
from phase03.embedding.indexer import QdrantIndexer  # noqa: E402
from phase03.pipeline import EmbedIndexPipeline  # noqa: E402
from phase06.embedding.partition import all_partition_collections  # noqa: E402
from phase06.shared.config import settings  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reindex_vectors")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reindex embeddings (optionally per-year collections)")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--collection-suffix", default="_v2", help="Suffix for blue-green target collections")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    targets = [f"{name}{args.collection_suffix}" for name in all_partition_collections()]
    logger.info("Target collections: %s", targets)

    if args.dry_run:
        return

    with get_db_session() as session:
        for target in targets:
            indexer = QdrantIndexer(collection_name=target)
            indexer.ensure_collection()
            report = EmbedIndexPipeline(session, indexer=indexer).run(limit=args.limit)
            logger.info("Indexed %s vectors into %s", report.indexed, target)


if __name__ == "__main__":
    main()
