from enum import StrEnum


class ProcessingState(StrEnum):
    RAW = "RAW"
    CLEANED = "CLEANED"
    TRANSLATED = "TRANSLATED"
    EXTRACTED = "EXTRACTED"
    EMBEDDED = "EMBEDDED"
    CLUSTERED = "CLUSTERED"
    INDEXED = "INDEXED"


class ScrapeRunStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeRunType(StrEnum):
    WINDOW_BACKFILL = "window_backfill"
    FULL_BACKFILL = "full_backfill"  # legacy alias
    INCREMENTAL = "incremental"


class CheckpointStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


SORT_PASS_CONFIG = [
    ("newest", "NEWEST"),
    ("rating", "RATING"),
    ("most_relevant", "MOST_RELEVANT"),
]

DEFAULT_SCRAPE_MONTHS_BACK = 6
PIPELINE_VERSION = "1.0"
