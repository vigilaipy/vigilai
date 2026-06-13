from __future__ import annotations

from pydantic import BaseModel

__all__ = ["CostTracker", "CostStats"]


class CostStats(BaseModel):
    """Data model representing cost statistics."""

    total_tokens: int = 0
    total_cost_usd: float = 0.0


class CostTracker:
    """Tracks costs based on token usage and model pricing."""

    # NOTE: Update with current model names and pricing before v1.0 release
    PRICING_TABLE = {
        "gpt-4o": {"prompt": 5.0, "completion": 15.0},
        "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
        "claude-sonnet-4-6": {"prompt": 3.0, "completion": 15.0},
        "claude-opus-4-6": {"prompt": 15.0, "completion": 75.0},
        "claude-haiku-4-5": {"prompt": 0.25, "completion": 1.25},
        "llama-3.1-70b": {"prompt": 0.60, "completion": 0.90},
        "mixtral-8x7b": {"prompt": 0.25, "completion": 0.25},
        "deepseek-chat": {"prompt": 0.14, "completion": 0.28},
    }

    def __init__(self, model: str = "gpt-4o") -> None:
        """Initialize the cost tracker.

        Args:
            model: The model name.
        """
        self.model = model
        self.stats = CostStats()

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate the cost of a call.

        Args:
            input_tokens: Number of prompt tokens.
            output_tokens: Number of completion tokens.
            model: The model name.

        Returns:
            The estimated cost in USD.
        """
        rates = self.PRICING_TABLE.get(model, {"prompt": 0.0, "completion": 0.0})
        cost = (input_tokens / 1000000.0) * rates["prompt"] + (
            output_tokens / 1000000.0
        ) * rates["completion"]
        return cost

    def add_usage(self, prompt_tokens: int, completion_tokens: int = 0) -> float:
        """Add usage to the cost tracker.

        Args:
            prompt_tokens: The number of prompt tokens used.
            completion_tokens: The number of completion tokens used.

        Returns:
            The calculated cost for this usage in USD.
        """
        cost = self.estimate_cost(prompt_tokens, completion_tokens, self.model)

        self.stats.total_tokens += prompt_tokens + completion_tokens
        self.stats.total_cost_usd += cost
        return cost

    def get_stats(self) -> CostStats:
        """Get the current cost statistics.

        Returns:
            The CostStats model.
        """
        return self.stats
