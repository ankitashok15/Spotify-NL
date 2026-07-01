from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://spotify:spotify@localhost:5432/spotify_nl"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    extract_batch_size: int = 25
    extract_max_retries: int = 3
    extract_skip_spam: bool = True
    translation_confidence_threshold: float = 0.8
    cache_dir: Path = _REPO_ROOT / "data" / "cache" / "extraction"


settings = Settings()
