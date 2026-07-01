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
    gemini_embedding_model: str = "gemini-embedding-001"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "spotify_reviews"
    embed_batch_size: int = 50
    embed_max_retries: int = 3
    embed_rate_limit_seconds: float = 1.0
    api_host: str = "0.0.0.0"
    api_port: int = 8001


settings = Settings()
