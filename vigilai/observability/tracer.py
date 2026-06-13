import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from contextlib import contextmanager

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
            span.metadata["error"] = str(e)
            raise
        finally:
            span.end_time = time.time()
            span.duration = span.end_time - span.start_time
