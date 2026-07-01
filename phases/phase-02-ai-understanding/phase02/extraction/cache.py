from __future__ import annotations

import hashlib
import json
from pathlib import Path

from phase02.shared.config import settings


def content_hash(text: str) -> str:
    normalized = (text or "").strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class ExtractionCacheStore:
    """File-backed cache for extraction payloads (supplements DB cache)."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or settings.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> dict | None:
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def put(self, key: str, payload: dict) -> None:
        self._path(key).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
