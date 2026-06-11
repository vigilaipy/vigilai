__all__ = ["LoopGuard"]

class LoopGuard:
    """Prevents an agent from entering an infinite loop."""

    def __init__(self, max_iterations: int = 10) -> None:
        """Initialize the loop guard.
        
        Args:
            max_iterations: The maximum number of allowed iterations.
        """
        self.max_iterations = max_iterations
        self.current_iteration = 0

    def tick(self) -> None:
        """Register an iteration.
        
        Raises:
            RuntimeError: If the maximum number of iterations is exceeded.
        """
        self.current_iteration += 1
        if self.current_iteration > self.max_iterations:
            raise RuntimeError(f"Infinite loop detected! Max iterations ({self.max_iterations}) exceeded.")

    def reset(self) -> None:
        """Reset the iteration counter."""
        self.current_iteration = 0
