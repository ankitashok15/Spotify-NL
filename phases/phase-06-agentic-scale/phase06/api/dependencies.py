from __future__ import annotations

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from phase06.shared.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    expected = settings.api_key
    if not expected:
        return
    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
