from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Optional

__all__ = ["Tracer", "Span"]


@dataclass
class Span:
    """Represents a tracing span for an LLM call."""

    name: str
    start_time: float
    end_time: float = 0.0
    duration: float = 0.0
    status: str = "running"
    metadata: Optional[Dict[str, Any]] = None


class Tracer:
    """Manages execution spans for observability."""

    def __init__(self) -> None:
        """Initialize the tracer."""
        self.spans: list[Span] = []

    @contextmanager
    def trace(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """Trace a block of code execution.

        Args:
            name: The name of the trace span.
            metadata: Additional metadata for the span.

        Yields:
            The created span.
        """
        span = Span(name=name, start_time=time.time(), metadata=metadata or {})
        self.spans.append(span)
        try:
            yield span
            span.status = "success"
        except Exception as e:
            span.status = "error"
            if span.metadata is None:
                span.metadata = {}
            span.metadata["error"] = str(e)
            raise
        finally:
            span.end_time = time.time()
            span.duration = span.end_time - span.start_time

    def latency_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles and statistics."""
        completed_spans = [
            s.duration for s in self.spans if s.status in ("success", "error")
        ]
        if not completed_spans:
            return {
                "p50": 0.0,
                "p75": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0.0,
            }

        completed_spans.sort()
        count = len(completed_spans)

        def _percentile(p: float) -> float:
            k = (count - 1) * p
            f = int(k)
            c = f + 1
            if c >= count:
                return completed_spans[-1]
            return completed_spans[f] + (k - f) * (
                completed_spans[c] - completed_spans[f]
            )

        return {
            "p50": _percentile(0.50),
            "p75": _percentile(0.75),
            "p95": _percentile(0.95),
            "p99": _percentile(0.99),
            "mean": sum(completed_spans) / count,
            "min": completed_spans[0],
            "max": completed_spans[-1],
            "count": float(count),
        }
