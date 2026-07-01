from __future__ import annotations

import logging

from phase06.database.session import get_db_session
from phase06.orchestration.celery_app import celery_app
from phase06.orchestration.pipeline import IncrementalIngestionPipeline

logger = logging.getLogger(__name__)


@celery_app.task(name="phase06.orchestration.tasks.pipeline.run_incremental_pipeline")
def run_incremental_pipeline(
    extract_limit: int = 500,
    embed_limit: int = 500,
    assign_limit: int = 500,
) -> dict:
    with get_db_session() as session:
        report = IncrementalIngestionPipeline(session).run(
            extract_limit=extract_limit,
            embed_limit=embed_limit,
            assign_limit=assign_limit,
        )
        logger.info("Incremental pipeline: %s", report.to_dict())
        return report.to_dict()


@celery_app.task(name="phase06.orchestration.tasks.pipeline.run_weekly_insights")
def run_weekly_insights() -> dict:
    with get_db_session() as session:
        result = IncrementalIngestionPipeline(session).run_weekly()
        logger.info("Weekly cluster+insights completed")
        return result
