from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from phase01.database.session import get_db_session
from phase01.scrape.scraper import GooglePlayReviewScraper
from phase06.orchestration.celery_app import celery_app
from phase06.shared.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="phase06.orchestration.tasks.scrape.scrape_incremental", bind=True)
def scrape_incremental(self, limit: int | None = None) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=1)
    with get_db_session() as session:
        scraper = GooglePlayReviewScraper(session)
        run_id = scraper.scrape_incremental(
            since=since,
            app_id=settings.spotify_app_id,
            limit=limit,
            months_back=settings.scrape_months_back,
        )
        session.commit()
        logger.info("Incremental scrape completed run_id=%s", run_id)
        return {"run_id": str(run_id), "since": since.isoformat()}
