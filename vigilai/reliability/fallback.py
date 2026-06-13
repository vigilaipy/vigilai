from __future__ import annotations

from typing import Any, Callable, List, Optional

from ..utils.logger import Logger

__all__ = ["FallbackChain", "AsyncFallbackChain"]


class FallbackChain:
    """Provides a fallback mechanism for a sequence of functions."""

    def __init__(
        self, functions: List[Callable[..., Any]], logger: Optional[Logger] = None
    ) -> None:
        """Initialize the fallback chain.

        Args:
            functions: A list of functions to try in order.
            logger: Optional logger for recording attempts.
        """
        self.functions = functions
        self.logger = logger

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
        for i, func in enumerate(self.functions):
            try:
                res = func(*args, **kwargs)
                if self.logger:
                    self.logger.info(f"Fallback step {i} ({func.__name__}) succeeded.")
                return res
            except Exception as e:
                if self.logger:
                    self.logger.warning(
                        f"Fallback step {i} ({func.__name__}) failed: {e}"
                    )
                errors.append(e)

        if self.logger:
            self.logger.error("All fallback functions failed.")
        raise RuntimeError(f"All fallback functions failed. Errors: {errors}")


class AsyncFallbackChain:
    """Provides a fallback mechanism for a sequence of async functions."""

    def __init__(
        self, functions: List[Callable[..., Any]], logger: Optional[Logger] = None
    ) -> None:
        """Initialize the fallback chain.

        Args:
            functions: A list of functions to try in order.
            logger: Optional logger for recording attempts.
        """
        self.functions = functions
        self.logger = logger

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the chain of functions asynchronously.

        Args:
            *args: Positional arguments to pass to the functions.
            **kwargs: Keyword arguments to pass to the functions.

        Returns:
            The result of the first successful function.

        Raises:
            RuntimeError: If all functions in the chain fail.
        """
        errors = []
        for i, func in enumerate(self.functions):
            try:
                res = await func(*args, **kwargs)
                if self.logger:
                    self.logger.info(f"Fallback step {i} ({func.__name__}) succeeded.")
                return res
            except Exception as e:
                if self.logger:
                    self.logger.warning(
                        f"Fallback step {i} ({func.__name__}) failed: {e}"
                    )
                errors.append(e)

        if self.logger:
            self.logger.error("All fallback functions failed.")
        raise RuntimeError(f"All fallback functions failed. Errors: {errors}")
