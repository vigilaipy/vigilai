from __future__ import annotations

from typing import List

from .tracer import Span


class OTelExporter:
    """Exports vigilai spans to OpenTelemetry format."""

    def __init__(self, endpoint: str = "http://localhost:4317") -> None:
        """Initialize the OpenTelemetry exporter.

        Args:
            endpoint: OTLP gRPC endpoint. Defaults to local
                      collector on port 4317.
        """
        self.endpoint = endpoint

    def export(self, spans: List[Span]) -> str:
        """Convert vigilai Span objects to OTEL spans and export.

        Args:
            spans: List of spans to export.

        Returns:
            "exported" on success, or an error message on failure.
        """
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.trace import Status, StatusCode
        except ImportError:
            return "OpenTelemetry export requires: pip install vigilaipy[otel]"

        try:
            resource = Resource.create({"service.name": "vigilai"})
            provider = TracerProvider(resource=resource)
            exporter = OTLPSpanExporter(endpoint=self.endpoint, insecure=True)
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)

            tracer = provider.get_tracer("vigilai.tracer")

            for span in spans:
                start_time_ns = int(span.start_time * 1e9)
                end_time_ns = int(span.end_time * 1e9)

                otel_span = tracer.start_span(
                    name=span.name,
                    start_time=start_time_ns,
                )

                otel_span.set_attribute("vigilai.duration_sec", span.duration)
                if span.metadata:
                    for k, v in span.metadata.items():
                        if isinstance(v, (str, bool, int, float)):
                            otel_span.set_attribute(k, v)
                        else:
                            otel_span.set_attribute(k, str(v))

                if span.status == "error":
                    otel_span.set_status(Status(StatusCode.ERROR))
                else:
                    otel_span.set_status(Status(StatusCode.OK))

                otel_span.end(end_time=end_time_ns)

            provider.force_flush()
            return "exported"

        except Exception as e:
            return str(e)
