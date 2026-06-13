from __future__ import annotations

import re
from typing import List

from pydantic import BaseModel

__all__ = ["SecretScanner", "SecretResult"]


class SecretResult(BaseModel):
    """Result of a secret scan."""

    has_secrets: bool
    secret_types_found: List[str]


class SecretScanner:
    """Scans text for leaked secrets like API keys."""

    # Simple regexes for demonstration
    SECRET_PATTERNS = {
        "OPENAI_API_KEY": r"sk-[a-zA-Z0-9]{48}",
        "AWS_ACCESS_KEY_ID": r"(?i)AKIA[0-9A-Z]{16}",
        "GENERIC_BEARER_TOKEN": r"(?i)bearer\s+[a-zA-Z0-9\-\._~+/]+=*",
    }

    def scan(self, text: str) -> SecretResult:
        """Scan the text for secrets.

        Args:
            text: The text to scan.

        Returns:
            A SecretResult indicating if secrets were found.
        """
        found = []
        for name, pattern in self.SECRET_PATTERNS.items():
            if re.search(pattern, text):
                found.append(name)

        return SecretResult(has_secrets=len(found) > 0, secret_types_found=found)
