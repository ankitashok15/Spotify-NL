from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root: phases/phase-01-data-foundation/phase01/shared -> 4 levels up
_REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://spotify:spotify@localhost:5432/spotify_nl"
    spotify_app_id: str = "com.spotify.music"
    scrape_delay_seconds: float = 2.0
    scrape_batch_size: int = 200
    scrape_lang: str = "en"
    scrape_country: str = "us"
    scrape_months_back: int = 6
    raw_data_dir: Path = _REPO_ROOT / "data" / "raw" / "play_store"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    @property
    def play_store_url(self) -> str:
        return f"https://play.google.com/store/apps/details?id={self.spotify_app_id}"

    def scrape_cutoff_date(self):
        from phase01.scrape.window import scrape_cutoff_date

        return scrape_cutoff_date(self.scrape_months_back)


settings = Settings()
