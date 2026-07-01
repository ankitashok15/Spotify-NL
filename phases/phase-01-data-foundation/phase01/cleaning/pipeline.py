from phase01.cleaning.normalizer import content_hash, normalize_text
from phase01.cleaning.spam_filter import is_spam
from phase01.database.repositories import ReviewRepository
from phase01.shared.constants import PIPELINE_VERSION, ProcessingState


def clean_review_row(row: dict, review_repo: ReviewRepository) -> dict:
    """Apply cleaning rules; never drop the review."""
    original = row.get("text_original")
    cleaned = normalize_text(original)

    if not cleaned:
        cleaned = None

    c_hash = content_hash(cleaned or original)
    is_near_dup = False
    if c_hash and review_repo.content_hash_exists(c_hash):
        is_near_dup = True

    row["text_cleaned"] = cleaned
    row["is_spam"] = is_spam(cleaned or original, row.get("rating"))
    row["is_near_duplicate"] = is_near_dup
    row["processing_state"] = ProcessingState.CLEANED
    row["pipeline_version"] = PIPELINE_VERSION
    row["_content_hash"] = c_hash
    return row


def register_dedup_hashes(rows: list[dict], review_repo: ReviewRepository, review_ids: list) -> None:
    for row, review_id in zip(rows, review_ids):
        c_hash = row.pop("_content_hash", None)
        if c_hash and not row.get("is_near_duplicate"):
            review_repo.add_dedup_index(c_hash, review_id)
