from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any

from phase06.shared.config import settings

logger = logging.getLogger(__name__)


class QueryCache:
    """Redis-backed cache with in-memory fallback for RAG/agent responses."""

    def __init__(self, prefix: str = "spotify_nl", ttl: int | None = None) -> None:
        self.prefix = prefix
        self.ttl = ttl or settings.agent_cache_ttl_seconds
        self._memory: dict[str, tuple[float, Any]] = {}
        self._redis = None
        if settings.redis_url:
            try:
                import redis

                self._redis = redis.from_url(settings.redis_url, decode_responses=True)
                self._redis.ping()
            except Exception as exc:
                logger.info("Redis unavailable, using in-memory cache: %s", exc)
                self._redis = None

    def _key(self, namespace: str, payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"{self.prefix}:{namespace}:{digest}"

    def get(self, namespace: str, payload: dict) -> Any | None:
        key = self._key(namespace, payload)
        if self._redis:
            try:
                raw = self._redis.get(key)
                return json.loads(raw) if raw else None
            except Exception as exc:
                logger.debug("Redis get failed: %s", exc)

        entry = self._memory.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            self._memory.pop(key, None)
            return None
        return value

    def set(self, namespace: str, payload: dict, value: Any) -> None:
        key = self._key(namespace, payload)
        if self._redis:
            try:
                self._redis.setex(key, self.ttl, json.dumps(value, default=str))
                return
            except Exception as exc:
                logger.debug("Redis set failed: %s", exc)

        self._memory[key] = (time.time() + self.ttl, value)
