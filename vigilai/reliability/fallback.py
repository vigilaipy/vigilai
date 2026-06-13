from __future__ import annotations

from typing import Any, Callable, List

__all__ = ["FallbackChain"]


class FallbackChain:
    """Provides a fallback mechanism for a sequence of functions."""

    def __init__(self, functions: List[Callable[..., Any]]) -> None:
        """Initialize the fallback chain.

        Args:
            functions: A list of functions to try in order.
        """
        self.functions = functions

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the chain of functions.

        Args:
            *args: Positional arguments to pass to the functions.
            **kwargs: Keyword arguments to pass to the functions.

        Returns:
            The result of the first successful function.

        Raises:
            RuntimeError: If all functions in the chain fail.
        """
        errors = []
        for func in self.functions:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                errors.append(e)

        raise RuntimeError(f"All fallback functions failed. Errors: {errors}")
