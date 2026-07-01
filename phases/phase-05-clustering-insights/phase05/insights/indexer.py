from __future__ import annotations

import logging

from phase05.database.models import Insight

logger = logging.getLogger(__name__)


class InsightIndexer:
    """
    Optional: embed insight summaries into Qdrant for RAG retrieval.
    Deferred until insight corpus is large; logs intent for Phase 6 integration.
    """

    def index_insight(self, insight: Insight) -> None:
        logger.debug("Insight indexer stub for insight %s (%s)", insight.id, insight.insight_type)

    def index_batch(self, insights: list[Insight]) -> int:
        for insight in insights:
            self.index_insight(insight)
        return len(insights)
