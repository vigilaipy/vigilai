from __future__ import annotations

from typing import Any, List

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
        self.history: List[str] = []
        self.loop_detected = False

    def tick(self, state: Any = None) -> None:
        """Register an iteration.

        Args:
            state: Optional state object to track repetition.

        Raises:
            RuntimeError: If the maximum number of iterations is exceeded,
                          or if a repeated state is detected.
        """
        self.current_iteration += 1

        if state is not None:
            state_str = str(state)
            if state_str in self.history:
                self.loop_detected = True
                raise RuntimeError("Infinite loop detected! Repeated state found.")
            self.history.append(state_str)

        if self.current_iteration > self.max_iterations:
            self.loop_detected = True
            raise RuntimeError(
                f"Infinite loop detected! Max iterations "
                f"({self.max_iterations}) exceeded."
            )

    def reset(self) -> None:
        """Reset the iteration counter and history."""
        self.current_iteration = 0
        self.history.clear()
        self.loop_detected = False

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the loop guard's state.

        Returns:
            A dictionary containing the total iterations, whether a loop
            was detected, and the number of tracked states.
        """
        return {
            "total_iterations": self.current_iteration,
            "loop_detected": self.loop_detected,
            "tracked_states": len(self.history),
        }
