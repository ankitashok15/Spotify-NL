import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def write_raw_batch(raw_dir: Path, batch: list[dict], scrape_run_id: uuid.UUID, sort_order: str) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    batch_id = f"{scrape_run_id}_{sort_order}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}"
    path = raw_dir / f"{batch_id}.json"
    path.write_text(json.dumps(batch, default=str, ensure_ascii=False), encoding="utf-8")
    return path
