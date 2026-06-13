import time
from vigilai.observability import Tracer, TokenCounter, CostTracker


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


def test_cost_tracker() -> None:
    tracker = CostTracker("gpt-4o")
    # For gpt-4o, prompt=$0.005/1k, completion=$0.015/1k
    # 1000 prompt tokens = 0.005, 1000 completion = 0.015
    cost = tracker.add_usage(prompt_tokens=1000, completion_tokens=1000)
    assert cost == 0.02

    stats = tracker.get_stats()
    assert stats.total_tokens == 2000
    assert stats.total_cost_usd == 0.02
