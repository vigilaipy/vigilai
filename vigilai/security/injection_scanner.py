import re
from pydantic import BaseModel

__all__ = ["InjectionScanner", "InjectionResult"]

class InjectionResult(BaseModel):
    """Result of a prompt injection scan."""
    is_injection: bool
    confidence: float

class InjectionScanner:
    """Scans text for prompt injection attempts."""

    # Simple heuristic patterns for demonstration
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+all\s+previous\s+instructions",
        r"(?i)system\s+prompt",
        r"(?i)you\s+are\s+now",
        r"(?i)forget\s+everything",
    ]

    def scan(self, text: str) -> InjectionResult:
        """Scan the text for prompt injection.
        
        Args:
            text: The text to scan.
            
        Returns:
            An InjectionResult indicating if injection was detected.
        """
        matches = sum(1 for p in self.INJECTION_PATTERNS if re.search(p, text))
        
        if matches == 0:
            return InjectionResult(is_injection=False, confidence=0.0)
            
        confidence = min(1.0, matches * 0.4)
        return InjectionResult(is_injection=True, confidence=confidence)
