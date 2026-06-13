from __future__ import annotations

import csv
import json
import os
from typing import Any, Callable, ContextManager, Dict, List, Optional

from ..observability import CostTracker, Span, TokenCounter, Tracer
from ..reliability import aretry, retry
from ..security import (
    InjectionScanner,
    OutputGuard,
    OutputGuardResult,
    PIIScanner,
    SecretScanner,
)
from ..utils.logger import Logger
from .exceptions import BudgetExceededError

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
        self.output_guard = OutputGuard()

    def check_budget(self) -> float:
        """Check if the budget is exceeded.

        Returns:
            The remaining budget in USD.

        Raises:
            BudgetExceededError: If the total cost exceeds the spend limit.
        """
        stats = self.cost_tracker.get_stats()
        if stats.total_cost_usd >= self.spend_limit_usd:
            raise BudgetExceededError(
                f"Budget exceeded! Current spend: ${stats.total_cost_usd:.4f}, "
                f"Limit: ${self.spend_limit_usd:.4f}"
            )
        return max(0.0, self.spend_limit_usd - stats.total_cost_usd)

    def guard_output(
        self, text: str, policy: Optional[Dict] = None
    ) -> OutputGuardResult:
        """Guard the output text against safety policies.

        Args:
            text: Text to check.
            policy: Policy dictionary for OutputGuard.

        Returns:
            OutputGuardResult indicating safety status.
        """
        return self.output_guard.check(text, policy=policy)

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

    def areliable(
        self, retries: int = 3, timeout_sec: int = 30
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator for async automatic retries with exponential backoff.

        Args:
            retries: Max number of retries.
            timeout_sec: Base timeout in seconds.

        Returns:
            An async decorator.
        """
        return aretry(retries=retries, timeout_sec=timeout_sec)

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

        svg_bars = ""
        total_latency = max(stats["total_latency_sec"], 0.001)
        total_cost = stats["total_cost_usd"]
        max_bar_width = 300

        for i, span in enumerate(self.tracer.spans):
            span_cost = total_cost * (span.duration / total_latency)
            width = max(5, int((span.duration / total_latency) * max_bar_width))
            y_pos = i * 30 + 10

            display_name = span.name
            if len(display_name) > 22:
                display_name = display_name[:19] + "..."

            svg_bars += (
                f'<text x="170" y="{y_pos + 12}" fill="#E6EDF3" font-size="12" '
                f'text-anchor="end">{display_name}</text>\n'
                f'<rect x="180" y="{y_pos}" width="{width}" '
                f'height="15" fill="#4FA8E8"></rect>\n'
                f'<text x="{185 + width}" y="{y_pos + 12}" fill="#E6EDF3" '
                f'font-size="12">${span_cost:.4f}</text>\n'
            )

        span_rows = ""
        for span in self.tracer.spans:
            span_rows += (
                f"<tr><td>{span.name}</td><td>{span.duration:.2f}s</td>"
                f"<td>{span.status}</td></tr>\n"
            )

        svg_height = max(50, len(self.tracer.spans) * 30 + 20)

        html_content = f"""
        <html>
            <head>
                <title>vigilai — Observability Report</title>
                <style>
                    body {{
                        background-color: #0D1117;
                        color: #E6EDF3;
                        font-family: sans-serif;
                        padding: 20px;
                    }}
                    h1, h2 {{ color: #E6EDF3; }}
                    .card {{
                        background-color: #161B22;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                        border: 1px solid #30363D;
                    }}
                    .summary-grid {{
                        display: grid;
                        grid-template-columns: repeat(4, 1fr);
                        gap: 15px;
                    }}
                    .stat {{ font-size: 24px; color: #4FA8E8; font-weight: bold; }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 10px;
                    }}
                    th, td {{
                        padding: 10px;
                        text-align: left;
                        border-bottom: 1px solid #30363D;
                    }}
                    th {{ background-color: #21262D; }}
                </style>
            </head>
            <body>
                <h1>vigilai — Observability Report</h1>

                <div class="card">
                    <h2>Summary</h2>
                    <div class="summary-grid">
                        <div>
                            <div>Total Cost</div>
                            <div class="stat">${stats['total_cost_usd']:.4f}</div>
                        </div>
                        <div>
                            <div>Total Tokens</div>
                            <div class="stat">{stats['total_tokens']}</div>
                        </div>
                        <div>
                            <div>Spans Recorded</div>
                            <div class="stat">{stats['spans_recorded']}</div>
                        </div>
                        <div>
                            <div>Budget Remaining</div>
                            <div class="stat">${stats['budget_remaining_usd']:.4f}</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Cost per Span (Estimated)</h2>
                    <svg width="100%" height="{svg_height}">
                        {svg_bars}
                    </svg>
                </div>

                <div class="card">
                    <h2>Span Details</h2>
                    <table>
                        <tr><th>Name</th><th>Duration</th><th>Status</th></tr>
                        {span_rows}
                    </table>
                </div>
            </body>
        </html>
        """
        report_path = os.path.join(self.logger.log_dir, "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"Report generated at {report_path}")
        return str(report_path)

    def export(self, format: str, path: Optional[str] = None) -> str:
        """Export spans to a file.

        Args:
            format: 'json' or 'csv'
            path: Optional file path.

        Returns:
            The path of the exported file.
        """
        if path is None:
            path = os.path.join(self.logger.log_dir, f"export.{format}")

        if format == "json":
            data = {
                "stats": self.stats(),
                "spans": [
                    {
                        "name": s.name,
                        "start_time": s.start_time,
                        "end_time": s.end_time,
                        "duration": s.duration,
                        "status": s.status,
                        "metadata": s.metadata,
                    }
                    for s in self.tracer.spans
                ],
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        elif format == "csv":
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "start_time", "duration", "status"])
                for s in self.tracer.spans:
                    writer.writerow([s.name, s.start_time, s.duration, s.status])
        else:
            raise ValueError("Unsupported format. Use 'json' or 'csv'.")

        return str(path)
