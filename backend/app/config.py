from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_host: str = "0.0.0.0"
    api_port: int = 8080
    cors_origins: str = (
        "http://localhost:5173,http://localhost:3000,"
        "https://spotify-nl.vercel.app,https://spotify-nl-frontend.vercel.app"
    )
    database_url: str = "postgresql://spotify:spotify@localhost:5433/spotify_nl"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "spotify_reviews"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
