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
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "spotify_reviews"
    cluster_algorithm: str = "kmeans"  # kmeans | hdbscan
    cluster_min_size: int = 3
    cluster_k: int = 12
    emerging_growth_threshold: float = 0.20
    api_host: str = "0.0.0.0"
    api_port: int = 8003


settings = Settings()
