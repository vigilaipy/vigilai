from __future__ import annotations

__all__ = ["BudgetExceededError"]


class BudgetExceededError(Exception):
    """Raised when a budget limit is exceeded."""

    pass
