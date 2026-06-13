import os
from typing import Any, Callable, Dict, List, Optional, ContextManager

from ..observability import Tracer, TokenCounter, CostTracker, Span
from ..security import PIIScanner, SecretScanner, InjectionScanner
from ..reliability import retry
from ..utils.logger import Logger

__all__ = ["Inspector"]


class Inspector:
    """The central entry point for vigilai observability, security, and reliability."""

    def __init__(
        self,
        model: str = "gpt-4o",
        provider: str = "openai",
        spend_limit_usd: float = 10.0,
        redact_logs: bool = True,
        log_dir: str = "~/.vigilai/logs",
    ) -> None:
        """Initialize the Inspector.

        Args:
            model: The LLM model name.
            provider: The LLM provider.
            spend_limit_usd: Hard budget cap in USD.
            redact_logs: Whether to auto-mask PII in logs.
            log_dir: Local directory for log storage.
        """
        self.model = model
        self.provider = provider
        self.spend_limit_usd = spend_limit_usd
        self.logger = Logger(log_dir=log_dir, redact=redact_logs)

        self.tracer = Tracer()
        self.token_counter = TokenCounter(model=model)
        self.cost_tracker = CostTracker(model=model)

        self.pii_scanner = PIIScanner()
        self.secret_scanner = SecretScanner()
        self.injection_scanner = InjectionScanner()

    def trace(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> ContextManager[Span]:
        """Wrap an LLM call in a tracing span.

        Args:
            name: Name of the trace.
            metadata: Additional metadata.

        Returns:
            A context manager yielding a Span.
        """
        self.logger.info(f"Starting trace: {name}", metadata=metadata)
        return self.tracer.trace(name, metadata)

    def scan(self, text: str, checks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Scan text for security issues.

        Args:
            text: Text to scan.
            checks: List of checks to perform ('pii', 'secrets', 'prompt_injection').
                    Defaults to all if not specified.

        Returns:
            A dictionary of scan results.
        """
        if checks is None:
            checks = ["pii", "secrets", "prompt_injection"]

        results: Dict[str, Any] = {}
        if "pii" in checks:
            results["pii"] = self.pii_scanner.scan(text)
        if "secrets" in checks:
            results["secrets"] = self.secret_scanner.scan(text)
        if "prompt_injection" in checks:
            results["prompt_injection"] = self.injection_scanner.scan(text)

        return results

    def reliable(
        self, retries: int = 3, timeout_sec: int = 30
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator for automatic retries with exponential backoff.

        Args:
            retries: Max number of retries.
            timeout_sec: Base timeout in seconds.

        Returns:
            A decorator.
        """
        return retry(retries=retries, timeout_sec=timeout_sec)

    def stats(self) -> Dict[str, Any]:
        """Get summary statistics (latency, token, cost).

        Returns:
            Dictionary with current stats.
        """
        total_latency = sum(span.duration for span in self.tracer.spans)
        cost_stats = self.cost_tracker.get_stats()

        summary = {
            "spans_recorded": len(self.tracer.spans),
            "total_latency_sec": total_latency,
            "total_tokens": cost_stats.total_tokens,
            "total_cost_usd": cost_stats.total_cost_usd,
            "budget_remaining_usd": max(
                0.0, self.spend_limit_usd - cost_stats.total_cost_usd
            ),
        }
        self.logger.info("Stats generated", summary=summary)
        return summary

    def report(self) -> str:
        """Generate a local HTML report.

        Returns:
            The file path to the generated report.
        """
        stats = self.stats()
        html_content = f"""
        <html>
            <head><title>VigilAi Report</title></head>
            <body>
                <h1>VigilAi Statistics</h1>
                <ul>
                    <li>Spans Recorded: {stats['spans_recorded']}</li>
                    <li>Total Latency (sec): {stats['total_latency_sec']:.2f}</li>
                    <li>Total Tokens: {stats['total_tokens']}</li>
                    <li>Total Cost (USD): ${stats['total_cost_usd']:.4f}</li>
                </ul>
            </body>
        </html>
        """
        report_path = os.path.join(self.logger.log_dir, "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"Report generated at {report_path}")
        return str(report_path)
