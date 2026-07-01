from __future__ import annotations

import logging

from celery import Celery

from phase06.shared.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "spotify_nl",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "phase06.orchestration.tasks.scrape",
        "phase06.orchestration.tasks.pipeline",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

try:
    from phase06.orchestration.schedules import beat_schedule

    celery_app.conf.beat_schedule = beat_schedule
except Exception as exc:
    logger.debug("Beat schedule not loaded: %s", exc)
