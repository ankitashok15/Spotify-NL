from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from phase05.pipeline import ClusteringPipeline, IncrementalPipeline, InsightsPipeline

logger = logging.getLogger(__name__)


@dataclass
class PipelineReport:
    extracted: int = 0
    embedded: int = 0
    assigned: int = 0
    insights_saved: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "extracted": self.extracted,
            "embedded": self.embedded,
            "assigned": self.assigned,
            "insights_saved": self.insights_saved,
            "errors": self.errors,
        }


class IncrementalIngestionPipeline:
    """New reviews → extract → embed → cluster assign → insights."""

    def __init__(self, session: Session):
        self.session = session

    def run(
        self,
        *,
        extract_limit: int = 200,
        embed_limit: int = 200,
        assign_limit: int = 200,
        run_insights: bool = False,
    ) -> PipelineReport:
        report = PipelineReport()
        try:
            report.extracted = self._run_extract(extract_limit)
            report.embedded = self._run_embed(embed_limit)
            report.assigned = IncrementalPipeline(self.session).run(limit=assign_limit).get("assigned", 0)
            if run_insights:
                result = InsightsPipeline(self.session).run()
                report.insights_saved = result.get("insights_saved", 0)
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            report.errors.append(str(exc))
            logger.exception("Incremental pipeline failed")
        return report

    def run_weekly(self) -> dict:
        cluster_report = ClusteringPipeline(self.session).run_full()
        insights = InsightsPipeline(self.session).run()
        self.session.commit()
        return {
            "clustering": cluster_report.to_dict(),
            "insights": insights,
        }

    def _run_extract(self, limit: int) -> int:
        try:
            from phase02.extraction.pipeline import ExtractionPipeline

            report = ExtractionPipeline(self.session).run(limit=limit)
            return report.processed
        except Exception as exc:
            logger.warning("Extract step skipped: %s", exc)
            return 0

    def _run_embed(self, limit: int) -> int:
        try:
            from phase03.embedding.indexer import QdrantIndexer
            from phase03.pipeline import EmbedIndexPipeline

            report = EmbedIndexPipeline(self.session, indexer=QdrantIndexer()).run(limit=limit)
            return report.indexed
        except Exception as exc:
            logger.warning("Embed step skipped: %s", exc)
            return 0
