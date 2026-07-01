import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PHASE06 = Path(__file__).resolve().parents[2] / "phases" / "phase-06-agentic-scale"
for name in (
    "phase-01-data-foundation",
    "phase-02-ai-understanding",
    "phase-03-semantic-search",
    "phase-04-rag-qa",
    "phase-05-clustering-insights",
    "phase-06-agentic-scale",
):
    sys.path.insert(0, str(_PHASE06.parent / name))

from phase06.agent.orchestrator import AgentOrchestrator, ToolRegistry  # noqa: E402
from phase06.embedding.partition import collection_name_for_date  # noqa: E402
from phase06.rag.cache import QueryCache  # noqa: E402


def test_collection_name_partitioned():
    from datetime import datetime

    name = collection_name_for_date(datetime(2026, 4, 1))
    assert name.endswith("_2026")


def test_query_cache_roundtrip():
    cache = QueryCache(prefix="test", ttl=60)
    payload = {"question": "top free user issues"}
    cache.set("agent", payload, {"answer": "ok"})
    assert cache.get("agent", payload)["answer"] == "ok"


def test_heuristic_planner_starts_with_structured_query():
    session = MagicMock()
    orchestrator = AgentOrchestrator(session, llm=None)
    action = orchestrator._heuristic_plan(
        "What discovery issues do free phone users report most?",
        used=set(),
        observations=[],
    )
    assert action.tool == "structured_query"
    assert action.args["filters"]["subscription_type"] == "free"
    assert action.args["filters"]["device_type"] == "phone"


def test_tool_registry_has_six_tools():
    session = MagicMock()
    registry = ToolRegistry(session)
    assert len(registry.tools) == 6
    assert "semantic_search" in registry.tools
    assert "summarize_evidence" in registry.tools
