from pydantic import BaseModel, Field

__all__ = ["CostTracker", "CostStats"]

class CostStats(BaseModel):
    """Data model representing cost statistics."""
    total_tokens: int = 0
    total_cost_usd: float = 0.0

class CostTracker:
    """Tracks costs based on token usage and model pricing."""

    # Simple placeholder pricing (cost per 1k tokens)
    PRICING = {
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    }

    def __init__(self, model: str = "gpt-4o") -> None:
        """Initialize the cost tracker.
        
        Args:
            model: The model name.
        """
        self.model = model
        self.stats = CostStats()

    def add_usage(self, prompt_tokens: int, completion_tokens: int = 0) -> float:
        """Add usage to the cost tracker.
        
        Args:
            prompt_tokens: The number of prompt tokens used.
            completion_tokens: The number of completion tokens used.
            
        Returns:
            The calculated cost for this usage in USD.
        """
        rates = self.PRICING.get(self.model, {"prompt": 0.0, "completion": 0.0})
        cost = (prompt_tokens / 1000.0) * rates["prompt"] + (completion_tokens / 1000.0) * rates["completion"]
        
        self.stats.total_tokens += (prompt_tokens + completion_tokens)
        self.stats.total_cost_usd += cost
        return cost
        
    def get_stats(self) -> CostStats:
        """Get the current cost statistics.
        
        Returns:
            The CostStats model.
        """
        return self.stats
