from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Iterator

from phase06.shared.config import settings

logger = logging.getLogger(__name__)


class Observability:
    """Langfuse + structured logging hooks. No-op when keys are unset."""

    def __init__(self) -> None:
        self._langfuse = None
        if settings.langfuse_public_key and settings.langfuse_secret_key:
            try:
                from langfuse import Langfuse

                self._langfuse = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host,
                )
            except ImportError:
                logger.info("langfuse package not installed; tracing disabled")

    @contextmanager
    def trace_agent_run(self, question: str, *, metadata: dict | None = None) -> Iterator[dict[str, Any]]:
        started = time.perf_counter()
        trace_id = f"agent-{int(started * 1000)}"
        span = None
        if self._langfuse:
            try:
                span = self._langfuse.trace(
                    name="agent_query",
                    input={"question": question},
                    metadata=metadata or {},
                )
            except Exception as exc:
                logger.debug("Langfuse trace start failed: %s", exc)

        ctx = {"trace_id": trace_id, "span": span}
        try:
            yield ctx
        finally:
            took_ms = (time.perf_counter() - started) * 1000
            logger.info("Agent run %s completed in %.1fms", trace_id, took_ms)
            if span:
                try:
                    span.update(output={"took_ms": took_ms})
                except Exception:
                    pass

    def log_tool_call(self, trace_ctx: dict[str, Any], tool: str, args: dict, result_summary: str) -> None:
        logger.info("Agent tool %s args=%s -> %s", tool, args, result_summary[:200])
        span = trace_ctx.get("span")
        if span:
            try:
                span.span(name=f"tool:{tool}", input=args, output={"summary": result_summary[:500]})
            except Exception:
                pass


observability = Observability()
