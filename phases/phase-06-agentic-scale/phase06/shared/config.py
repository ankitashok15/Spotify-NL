from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://spotify:spotify@localhost:5433/spotify_nl"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_model_rag: str = "gemini-2.5-flash"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "spotify_reviews"
    redis_url: str = "redis://localhost:6379/0"
    api_key: str = ""
    api_host: str = "0.0.0.0"
    api_port: int = 8004
    agent_max_steps: int = 6
    agent_cache_ttl_seconds: int = 3600
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    scrape_months_back: int = 6
    spotify_app_id: str = "com.spotify.music"
    embedding_partition_by_year: bool = True


settings = Settings()
