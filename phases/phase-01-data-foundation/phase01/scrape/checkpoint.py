import base64
import json
import pickle
from typing import Any


def serialize_token(token: Any) -> str | None:
    if token is None:
        return None
    try:
        payload = json.dumps(token)
    except (TypeError, ValueError):
        payload = base64.b64encode(pickle.dumps(token)).decode("ascii")
        return f"pickle:{payload}"
    return f"json:{payload}"


def deserialize_token(raw: str | None) -> Any:
    if not raw:
        return None
    if raw.startswith("json:"):
        return json.loads(raw[5:])
    if raw.startswith("pickle:"):
        return pickle.loads(base64.b64decode(raw[7:]))
    # legacy plain json
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return pickle.loads(base64.b64decode(raw))
