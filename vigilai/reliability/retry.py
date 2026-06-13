from __future__ import annotations

import asyncio
import functools
import threading
import time
from typing import Any, Callable, TypeVar, cast

__all__ = ["retry", "aretry", "TimeoutException"]

T = TypeVar("T", bound=Callable[..., Any])


class TimeoutException(Exception):
    """Raised when a function execution times out."""

    pass


def retry(retries: int = 3, timeout_sec: int = 30) -> Callable[[T], T]:
    """Decorator to retry a function with exponential backoff and a timeout.

    Args:
        retries: Number of retry attempts.
        timeout_sec: Maximum execution time allowed for a single attempt
                     in seconds. (0 for no timeout)

    Returns:
        The decorated function.
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_err: Exception | None = None
            for attempt in range(retries + 1):
                result_container: dict[str, Any] = {}

                def worker() -> None:
                    try:
                        result_container["result"] = func(*args, **kwargs)
                    except Exception as e:
                        result_container["exception"] = e

                t = threading.Thread(target=worker)
                t.daemon = True
                t.start()

                if timeout_sec > 0:
                    t.join(timeout_sec)
                else:
                    t.join()

                if t.is_alive():
                    last_err = TimeoutException(
                        f"Function timed out after {timeout_sec} seconds"
                    )
                elif "exception" in result_container:
                    last_err = result_container["exception"]
                else:
                    return result_container["result"]

                if attempt < retries:
                    # Exponential backoff starting at 1 second: 1, 2, 4...
                    time.sleep(2**attempt)

            raise RuntimeError(f"Failed after {retries} retries") from last_err

        return cast(T, wrapper)

    return decorator


def aretry(retries: int = 3, timeout_sec: int = 30) -> Callable[[T], T]:
    """Decorator to asynchronously retry a function with exponential backoff
    and a timeout.

    Args:
        retries: Number of retry attempts.
        timeout_sec: Maximum execution time allowed for a single attempt
                     in seconds. (0 for no timeout)

    Returns:
        The decorated async function.
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_err: Exception | None = None
            for attempt in range(retries + 1):
                try:
                    if timeout_sec > 0:
                        return await asyncio.wait_for(
                            func(*args, **kwargs), timeout=timeout_sec
                        )
                    else:
                        return await func(*args, **kwargs)
                except asyncio.TimeoutError:
                    last_err = TimeoutException(
                        f"Function timed out after {timeout_sec} seconds"
                    )
                except Exception as e:
                    last_err = e

                if attempt < retries:
                    # Exponential backoff starting at 1 second: 1, 2, 4...
                    await asyncio.sleep(2**attempt)

            raise RuntimeError(f"Failed after {retries} retries") from last_err

        return cast(T, wrapper)

    return decorator
