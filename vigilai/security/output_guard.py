from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel

from .pii_scanner import PIIScanner
from .secret_scanner import SecretScanner

__all__ = ["OutputGuard", "OutputGuardResult"]


class OutputGuardResult(BaseModel):
    """Result of an output guard scan."""

    is_safe: bool
    violations: List[str]


class OutputGuard:
    """Scans LLM outputs for safety policy violations."""

    def __init__(self) -> None:
        self.pii_scanner = PIIScanner()
        self.secret_scanner = SecretScanner()

    def check(self, text: str, policy: Optional[Dict] = None) -> OutputGuardResult:
        """Check the text against the safety policy.

        Args:
            text: The text to check.
            policy: Optional policy dictionary. Can contain 'deny_phrases'.

        Returns:
            An OutputGuardResult.
        """
        violations = []

        secret_result = self.secret_scanner.scan(text)
        if secret_result.has_secrets:
            violations.extend(
                [f"SECRET_LEAK_{t}" for t in secret_result.secret_types_found]
            )

        pii_result = self.pii_scanner.scan(text)
        if pii_result.has_pii:
            violations.extend([f"PII_LEAK_{t}" for t in pii_result.entities_found])

        if policy and "deny_phrases" in policy:
            text_lower = text.lower()
            for phrase in policy["deny_phrases"]:
                if phrase.lower() in text_lower:
                    violations.append("DENY_PHRASE_MATCH")

        return OutputGuardResult(is_safe=len(violations) == 0, violations=violations)
