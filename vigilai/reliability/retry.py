import time
import functools
from typing import Any, Callable, TypeVar, cast

__all__ = ["retry"]

T = TypeVar("T", bound=Callable[..., Any])

def retry(retries: int = 3, timeout_sec: int = 30) -> Callable[[T], T]:
    """Decorator to retry a function with exponential backoff.
    
    Args:
        retries: Number of retry attempts.
        timeout_sec: Base timeout in seconds before the first retry.
        
    Returns:
        The decorated function.
    """
    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_err = None
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    if attempt < retries:
                        time.sleep(timeout_sec * (2 ** attempt))
            raise RuntimeError(f"Failed after {retries} retries") from last_err
        return cast(T, wrapper)
    return decorator
