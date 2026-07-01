"""
Load test skeleton for search + RAG at scale.

Run manually when infrastructure is provisioned:
  locust -f tests/phase-06/load_test.py --headless -u 50 -r 5 -t 5m
"""

from __future__ import annotations

import pytest

locust = pytest.importorskip("locust", reason="locust not installed")
HttpUser = locust.HttpUser
between = locust.between
task = locust.task


class SpotifyNLUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8004"

    @task(3)
    def agent_query(self) -> None:
        self.client.post(
            "/api/v1/agent/query",
            json={
                "question": "What discovery issues do free users on phones report most?",
                "use_cache": True,
            },
            headers={"X-API-Key": ""},
        )

    @task(2)
    def health(self) -> None:
        self.client.get("/health")
