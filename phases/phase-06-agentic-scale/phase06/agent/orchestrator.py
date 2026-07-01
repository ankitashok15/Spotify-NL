from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any

from sqlalchemy.orm import Session

from phase02.shared.llm_gemini import GeminiProvider
from phase06.agent.schemas import AgentPlanAction, AgentResult, ToolCallRecord
from phase06.agent.tools import (
    CompareSegmentsTool,
    GetClusterTool,
    GetTrendsTool,
    SemanticSearchTool,
    StructuredQueryTool,
    SummarizeEvidenceTool,
)
from phase06.agent.tools.base import AgentTool
from phase06.shared.config import settings
from phase06.shared.observability import observability

logger = logging.getLogger(__name__)

_PLANNER_SYSTEM = """You are a Spotify product research agent planner.
Given a user question and prior tool observations, choose the NEXT tool call.
Return JSON only:
{"tool": "<name>|finish", "args": {...}, "reason": "..."}
Available tools:
- semantic_search: {query, filters?, top_k?}
- structured_query: {group_by: primary_issue|subscription_type|device_type, filters?, limit?}
- get_cluster: {cluster_id?|cluster_key?}
- compare_segments: {segment_a: {subscription_type?, device_type?}, segment_b: {...}, topic?}
- get_trends: {months?, primary_issue?, filters?}
- summarize_evidence: {review_ids?, context?, observations?}
Use "finish" when enough evidence exists for a final answer.
"""


class ToolRegistry:
    def __init__(self, session: Session, llm: GeminiProvider | None = None):
        self.tools: dict[str, AgentTool] = {
            SemanticSearchTool.name: SemanticSearchTool(),
            StructuredQueryTool.name: StructuredQueryTool(session),
            GetClusterTool.name: GetClusterTool(session),
            CompareSegmentsTool.name: CompareSegmentsTool(session),
            GetTrendsTool.name: GetTrendsTool(session),
            SummarizeEvidenceTool.name: SummarizeEvidenceTool(session, llm),
        }

    def execute(self, name: str, args: dict) -> Any:
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        return tool.run(args)

    def summary(self, name: str, result: Any) -> str:
        tool = self.tools.get(name)
        return tool.summary(result) if tool else str(result)[:200]


class AgentOrchestrator:
    """Plan → tool call → observe → iterate → synthesize."""

    def __init__(self, session: Session, llm: GeminiProvider | None = None):
        self.session = session
        self.llm = llm
        self.registry = ToolRegistry(session, llm)

    def run(self, question: str, *, debug: bool = False) -> AgentResult:
        started = time.perf_counter()
        trace: list[ToolCallRecord] = []
        observations: list[Any] = []

        with observability.trace_agent_run(question) as trace_ctx:
            for step in range(1, settings.agent_max_steps + 1):
                action = self._plan(question, observations, trace)
                if action.finish or not action.tool:
                    break

                tool_started = time.perf_counter()
                try:
                    result = self.registry.execute(action.tool, action.args)
                except Exception as exc:
                    result = {"error": str(exc)}
                    logger.warning("Tool %s failed: %s", action.tool, exc)

                took_ms = (time.perf_counter() - tool_started) * 1000
                summary = self.registry.summary(action.tool, result)
                record = ToolCallRecord(
                    step=step,
                    tool=action.tool,
                    args=action.args,
                    result_summary=summary,
                    took_ms=round(took_ms, 2),
                    result=result if debug else None,
                )
                trace.append(record)
                observations.append(result)
                observability.log_tool_call(trace_ctx, action.tool, action.args, summary)

            synthesis = self.registry.execute(
                "summarize_evidence",
                {
                    "context": question,
                    "observations": observations,
                    "review_ids": self._collect_review_ids(observations),
                },
            )

        citations = synthesis.get("citations", []) if isinstance(synthesis, dict) else []
        answer = synthesis.get("summary", "") if isinstance(synthesis, dict) else str(synthesis)
        confidence = float(synthesis.get("confidence", 0.6)) if isinstance(synthesis, dict) else 0.6
        took_ms = (time.perf_counter() - started) * 1000

        return AgentResult(
            answer=answer,
            citations=citations,
            confidence=confidence,
            steps=len(trace),
            tool_trace=trace,
            took_ms=round(took_ms, 2),
        )

    def _plan(
        self,
        question: str,
        observations: list[Any],
        trace: list[ToolCallRecord],
    ) -> AgentPlanAction:
        used = {t.tool for t in trace}
        if self.llm and (os.environ.get("GEMINI_API_KEY") or settings.gemini_api_key):
            try:
                payload = self.llm.generate_json(
                    json.dumps(
                        {
                            "question": question,
                            "observations": observations[-3:],
                            "tools_used": list(used),
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                    system=_PLANNER_SYSTEM,
                )
                tool = payload.get("tool")
                if tool == "finish":
                    return AgentPlanAction(finish=True, reason=payload.get("reason", ""))
                if tool in self.registry.tools:
                    return AgentPlanAction(tool=tool, args=payload.get("args") or {}, reason=payload.get("reason", ""))
            except Exception as exc:
                logger.warning("LLM planner failed, using heuristic: %s", exc)

        return self._heuristic_plan(question, used, observations)

    def _heuristic_plan(
        self,
        question: str,
        used: set[str],
        observations: list[Any],
    ) -> AgentPlanAction:
        q = question.lower()
        filters: dict[str, Any] = {}
        if "free" in q:
            filters["subscription_type"] = "free"
        if "premium" in q and "free" not in q:
            filters["subscription_type"] = "premium"
        if "phone" in q:
            filters["device_type"] = "phone"
        if re.search(r"\b20(25|26)\b", q):
            year = re.search(r"\b(20\d{2})\b", q).group(1)  # type: ignore[union-attr]
            filters["date_from"] = f"{year}-01-01"
            filters["date_to"] = f"{year}-12-31"

        if "compare" in q or ("free" in q and "premium" in q):
            if "compare_segments" not in used:
                return AgentPlanAction(
                    tool="compare_segments",
                    args={
                        "segment_a": {"subscription_type": "free", "device_type": filters.get("device_type")},
                        "segment_b": {"subscription_type": "premium", "device_type": filters.get("device_type")},
                        "topic": "discovery",
                    },
                    reason="Comparative segment question",
                )

        if "trend" in q or "changed" in q or "over time" in q:
            if "get_trends" not in used:
                return AgentPlanAction(tool="get_trends", args={"months": 6, "filters": filters}, reason="Trend analysis")

        if "structured_query" not in used:
            return AgentPlanAction(
                tool="structured_query",
                args={"group_by": "primary_issue", "filters": filters, "limit": 10},
                reason="Rank top structured issues",
            )

        if "semantic_search" not in used:
            top_issue = self._top_issue_from_observations(observations)
            search_q = top_issue or "discovery complaints"
            return AgentPlanAction(
                tool="semantic_search",
                args={"query": search_q, "filters": filters, "top_k": 8},
                reason="Sample reviews for top issues",
            )

        return AgentPlanAction(finish=True, reason="Heuristic plan complete")

    def _top_issue_from_observations(self, observations: list[Any]) -> str | None:
        for obs in observations:
            if isinstance(obs, list) and obs:
                first = obs[0]
                if isinstance(first, dict):
                    return first.get("dimension") or first.get("primary_issue")
            if isinstance(obs, dict):
                for key in ("segment_a_issues", "issue_series"):
                    rows = obs.get(key) or []
                    if rows and isinstance(rows[0], dict):
                        return rows[0].get("primary_issue") or rows[0].get("dimension")
        return None

    def _collect_review_ids(self, observations: list[Any]) -> list[str]:
        ids: list[str] = []
        for obs in observations:
            if isinstance(obs, list):
                for item in obs:
                    if isinstance(item, dict) and item.get("review_id"):
                        ids.append(str(item["review_id"]))
            elif isinstance(obs, dict):
                for key in ("member_review_ids", "representative_review_ids"):
                    ids.extend(str(x) for x in (obs.get(key) or []))
        return list(dict.fromkeys(ids))[:20]
