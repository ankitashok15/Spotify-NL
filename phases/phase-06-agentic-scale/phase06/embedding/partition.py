from __future__ import annotations

from datetime import datetime

from phase03.shared.config import settings as phase3_settings
from phase06.shared.config import settings


def collection_name_for_date(review_date: datetime | None, *, base: str | None = None) -> str:
    """Return year-partitioned Qdrant collection name when enabled."""
    base_name = base or phase3_settings.qdrant_collection
    if not settings.embedding_partition_by_year:
        return base_name
    year = (review_date or datetime.utcnow()).year
    return f"{base_name}_{year}"


def all_partition_collections(*, base: str | None = None) -> list[str]:
    base_name = base or phase3_settings.qdrant_collection
    if not settings.embedding_partition_by_year:
        return [base_name]
    current_year = datetime.utcnow().year
    return [f"{base_name}_{year}" for year in range(current_year - 5, current_year + 1)]
