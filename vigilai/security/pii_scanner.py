from typing import List
from pydantic import BaseModel

__all__ = ["PIIScanner", "PIIResult"]


class PIIResult(BaseModel):
    """Result of a PII scan."""

    has_pii: bool
    entities_found: List[str]


class PIIScanner:
    """Scans text for Personally Identifiable Information (PII)."""

    def __init__(self) -> None:
        """Initialize the PII Scanner. Uses presidio if available."""
        self.analyzer = None
        try:
            import presidio_analyzer  

            self.analyzer = presidio_analyzer.AnalyzerEngine()
        except ImportError:
            pass

    def scan(self, text: str) -> PIIResult:
        """Scan the text for PII.

        Args:
            text: The text to scan.

        Returns:
            A PIIResult indicating if PII was found and what types.
        """
        if self.analyzer is not None:
            results = self.analyzer.analyze(text=text, entities=[], language="en")
            entities = list({res.entity_type for res in results})
            return PIIResult(has_pii=len(entities) > 0, entities_found=entities)

        # Basic fallback using simple heuristics if presidio is not installed
        import re

        entities = []
        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", text):
            entities.append("SSN")
        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text):
            entities.append("EMAIL_ADDRESS")

        return PIIResult(has_pii=len(entities) > 0, entities_found=entities)
