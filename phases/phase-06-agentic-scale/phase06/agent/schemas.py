from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ToolCallRecord:
    step: int
    tool: str
    args: dict
    result_summary: str
    took_ms: float
    result: Any = None


@dataclass
class AgentResult:
    answer: str
    citations: list[dict]
    confidence: float
    steps: int
    tool_trace: list[ToolCallRecord] = field(default_factory=list)
    took_ms: float = 0.0

    def to_dict(self, *, include_trace: bool = False) -> dict:
        payload = {
            "answer": self.answer,
            "citations": self.citations,
            "confidence": self.confidence,
            "steps": self.steps,
            "took_ms": self.took_ms,
        }
        if include_trace:
            payload["tool_trace"] = [
                {
                    "step": t.step,
                    "tool": t.tool,
                    "args": t.args,
                    "result_summary": t.result_summary,
                    "took_ms": t.took_ms,
                }
                for t in self.tool_trace
            ]
        return payload


@dataclass
class AgentPlanAction:
    tool: str | None = None
    args: dict = field(default_factory=dict)
    finish: bool = False
    reason: str = ""
