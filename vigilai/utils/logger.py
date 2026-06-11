import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console

__all__ = ["Logger"]

console = Console()


class Logger:
    """Local structured logger that writes to JSONL files and rich console."""

    def __init__(self, log_dir: str = "~/.vigilai/logs", redact: bool = False) -> None:
        """Initialize the logger.

        Args:
            log_dir: Directory where the logs will be stored.
            redact: Whether to automatically mask PII in logs (placeholder behavior).
        """
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"vigilai_{time.strftime('%Y%m%d')}.jsonl"
        self.redact = redact

    def _write(self, level: str, message: str, **kwargs: Any) -> None:
        """Internal method to write structured logs."""
        log_entry: Dict[str, Any] = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs,
        }

        # Simple placeholder for redaction
        if self.redact and "text" in log_entry:
            log_entry["text"] = "[REDACTED]"

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except IOError as e:
            console.print(f"[red]Failed to write log: {e}[/red]")

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self._write("INFO", message, **kwargs)
        if kwargs.get("print_console", False):
            console.print(f"[blue]INFO:[/blue] {message}")

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self._write("ERROR", message, **kwargs)
        console.print(f"[red]ERROR:[/red] {message}")

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self._write("WARNING", message, **kwargs)
        console.print(f"[yellow]WARNING:[/yellow] {message}")
