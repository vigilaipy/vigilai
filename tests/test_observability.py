from __future__ import annotations

import time

from vigilai.observability import CostTracker, TokenCounter, Tracer


def test_tracer() -> None:
    tracer = Tracer()
    with tracer.trace("test_span", metadata={"key": "value"}):
        time.sleep(0.01)

    assert len(tracer.spans) == 1
    assert tracer.spans[0].name == "test_span"
    assert tracer.spans[0].duration >= 0.01
    assert tracer.spans[0].status == "success"
    assert tracer.spans[0].metadata == {"key": "value"}


def test_token_counter() -> None:
    counter = TokenCounter("gpt-4o")
    # "Hello, world!" is exactly 4 tokens in cl100k_base
    count = counter.count("Hello, world!")
    assert count > 0

    count_claude = counter.count_tokens("Hello, world!", "claude-sonnet-4-6")
    assert count_claude == 3  # 13 chars // 4 = 3


def test_cost_tracker() -> None:
    tracker = CostTracker("gpt-4o")
    # For gpt-4o, prompt=$0.005/1k, completion=$0.015/1k
    # 1000 prompt tokens = 0.005, 1000 completion = 0.015
    cost = tracker.add_usage(prompt_tokens=1000, completion_tokens=1000)
    assert cost == 0.02

    stats = tracker.get_stats()
    assert stats.total_tokens == 2000
    assert stats.total_cost_usd == 0.02


def test_latency_percentiles() -> None:
    from vigilai.observability import Span

    tracer = Tracer()
    for i in range(1, 11):
        span = Span(name=f"span_{i}", start_time=0.0)
        span.duration = float(i)
        span.status = "success"
        tracer.spans.append(span)

    percentiles = tracer.latency_percentiles()
    assert percentiles["p50"] == 5.5
    assert 9.0 <= percentiles["p95"] <= 10.0
    assert percentiles["p99"] >= 9.0
    assert percentiles["mean"] == 5.5
    assert percentiles["min"] == 1.0
    assert percentiles["max"] == 10.0
    assert percentiles["count"] == 10.0

    empty_tracer = Tracer()
    empty_percentiles = empty_tracer.latency_percentiles()
    assert empty_percentiles["p50"] == 0.0
    assert empty_percentiles["count"] == 0.0


def test_inspector_stats_latency() -> None:
    from vigilai import Inspector

    inspector = Inspector()
    with inspector.trace("test"):
        pass
    stats = inspector.stats()
    assert "latency_p50_sec" in stats
    assert "latency_p99_sec" in stats
    assert stats["latency_p50_sec"] >= 0.0


def test_inspector_export_otel_no_package() -> None:
    from vigilai import Inspector

    inspector = Inspector()
    with inspector.trace("test"):
        pass
    res = inspector.export(format="otel")
    assert isinstance(res, str)
    if "requires" in res:
        assert res == "OpenTelemetry export requires: pip install vigilaipy[otel]"


def test_inspector_export_json_csv(tmp_path) -> None:
    import json
    import os

    from vigilai import Inspector

    inspector = Inspector(log_dir=str(tmp_path))
    with inspector.trace("test"):
        pass

    json_path = inspector.export(format="json")
    assert os.path.exists(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "spans" in data

    csv_path = inspector.export(format="csv")
    assert os.path.exists(csv_path)
    with open(csv_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "test" in content
