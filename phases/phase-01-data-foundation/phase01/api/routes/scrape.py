import csv
import io
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from phase01.api.schemas import (
    ReviewListResponse,
    ReviewResponse,
    ScrapeRequest,
    ScrapeResponse,
    ScrapeStatusResponse,
    ValidationResponse,
)
from phase01.cleaning.pipeline import clean_review_row
from phase01.database.models import init_db
from phase01.database.repositories import ReviewRepository, ScrapeRunRepository
from phase01.database.session import get_db
from phase01.scrape.normalizer import normalize_play_review
from phase01.scrape.scraper import GooglePlayReviewScraper
from phase01.shared.config import settings

router = APIRouter(prefix="/api/v1", tags=["scrape"])


def _run_scrape_task(
    mode: str, app_id: str, limit: int | None, since: datetime | None, months_back: int | None
) -> None:
    from phase01.database.session import get_db_session

    init_db(settings.database_url)
    with get_db_session() as session:
        scraper = GooglePlayReviewScraper(session)
        if mode == "incremental":
            if not since:
                raise ValueError("since is required for incremental mode")
            scraper.scrape_incremental(since, app_id=app_id, limit=limit, months_back=months_back)
        else:
            scraper.scrape_all(app_id=app_id, limit=limit, months_back=months_back)


@router.post("/scrape", response_model=ScrapeResponse)
def trigger_scrape(
    body: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    app_id = body.app_id or settings.spotify_app_id
    run_repo = ScrapeRunRepository(db)

    if run_repo.get_active(app_id):
        raise HTTPException(status_code=409, detail="A scrape run is already active for this app")

    background_tasks.add_task(
        _run_scrape_task, body.mode, app_id, body.limit, body.since, body.months_back
    )

    return ScrapeResponse(
        run_id=uuid.uuid4(),
        message=(
            f"Scrape queued ({body.mode}) — last {body.months_back or settings.scrape_months_back} months. "
            "Check GET /api/v1/scrape/status"
        ),
    )


@router.get("/scrape/status", response_model=ScrapeStatusResponse)
def scrape_status(
    app_id: str | None = None,
    db: Session = Depends(get_db),
):
    app_id = app_id or settings.spotify_app_id
    run_repo = ScrapeRunRepository(db)
    run = run_repo.get_latest(app_id)

    if not run:
        return ScrapeStatusResponse(
            run_id=None,
            status=None,
            app_id=app_id,
            reviews_target=None,
            reviews_scraped=0,
            reviews_new=0,
            reviews_updated=0,
            gap_report=None,
            started_at=None,
            ended_at=None,
        )

    return ScrapeStatusResponse(
        run_id=run.id,
        status=run.status,
        app_id=run.app_id,
        reviews_target=run.reviews_target,
        reviews_scraped=run.reviews_scraped,
        reviews_new=run.reviews_new,
        reviews_updated=run.reviews_updated,
        gap_report=run.gap_report,
        started_at=run.started_at,
        ended_at=run.ended_at,
    )


@router.get("/scrape/validate", response_model=ValidationResponse)
def validate_corpus(
    app_id: str | None = None,
    db: Session = Depends(get_db),
):
    scraper = GooglePlayReviewScraper(db)
    report = scraper.validate_corpus(app_id, months_back=settings.scrape_months_back)
    return ValidationResponse(report=report.to_dict())
