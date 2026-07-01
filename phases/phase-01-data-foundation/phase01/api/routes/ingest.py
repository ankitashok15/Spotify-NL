import csv
import io
import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from phase01.cleaning.pipeline import clean_review_row
from phase01.database.repositories import ReviewRepository
from phase01.database.session import get_db
from phase01.scrape.normalizer import normalize_play_review
from phase01.scrape.window import filter_reviews_in_window, review_in_window
from phase01.shared.config import settings

router = APIRouter(prefix="/api/v1", tags=["ingest"])


def _parse_upload(content: bytes, filename: str) -> list[dict]:
    text = content.decode("utf-8")
    if filename.endswith(".json"):
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "reviews" in data:
            return data["reviews"]
        raise HTTPException(status_code=400, detail="JSON must be a list or {reviews: [...]}")

    if filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)

    raise HTTPException(status_code=400, detail="Only .json and .csv files are supported")


@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Dev-only manual upload of review exports."""
    raw_items = _parse_upload(await file.read(), file.filename or "upload.json")
    repo = ReviewRepository(db)
    app_id = settings.spotify_app_id

    rows = []
    for raw in raw_items:
        mapped = {
            "reviewId": raw.get("reviewId") or raw.get("external_review_id") or raw.get("id"),
            "userName": raw.get("userName") or raw.get("user_name"),
            "content": raw.get("content") or raw.get("text") or raw.get("text_original"),
            "score": raw.get("score") or raw.get("rating"),
            "thumbsUpCount": raw.get("thumbsUpCount") or raw.get("thumbs_up", 0),
            "at": raw.get("at") or raw.get("review_created_at"),
            "replyContent": raw.get("replyContent") or raw.get("developer_reply"),
        }
        if not mapped["reviewId"]:
            continue
        row = normalize_play_review(mapped, app_id)
        if row.get("review_created_at") and row["review_created_at"] < settings.scrape_cutoff_date():
            continue
        row = clean_review_row(row, repo)
        row.pop("_content_hash", None)
        rows.append(row)

    new, updated = repo.upsert_reviews_batch(rows)
    return {"ingested": len(rows), "new": new, "updated": updated}
