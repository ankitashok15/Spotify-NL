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
    gemini_model_rag: str = "gemini-2.5-flash"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "spotify_reviews"
    rag_retrieve_top_k: int = 50
    rag_rerank_top_n: int = 15
    rag_use_hyde: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8002


settings = Settings()
