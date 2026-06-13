from __future__ import annotations

import tiktoken

__all__ = ["TokenCounter"]


class TokenCounter:
    """Utility to count tokens using tiktoken or approximation."""

    PROVIDER_MAP = {
        "gpt-": "openai",
        "o1-": "openai",
        "claude-": "anthropic",
        "llama": "generic",
        "mixtral": "generic",
        "deepseek": "generic",
    }

    def __init__(self, model: str = "gpt-4o") -> None:
        """Initialize the token counter.

        Args:
            model: The default model name to use for token encoding.
        """
        self.model = model
        self._tiktoken_cache: dict[str, tiktoken.Encoding] = {}

    def _get_provider(self, model: str) -> str:
        model_lower = model.lower()
        for prefix, provider in self.PROVIDER_MAP.items():
            if model_lower.startswith(prefix):
                return provider
        return "generic"

    def _get_encoding(self, model: str) -> tiktoken.Encoding:
        if model not in self._tiktoken_cache:
            try:
                self._tiktoken_cache[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                self._tiktoken_cache[model] = tiktoken.get_encoding("cl100k_base")
        return self._tiktoken_cache[model]

    def count_tokens(self, text: str, model: str) -> int:
        """Count the number of tokens in the given text for a specific model.

        Args:
            text: The text to count tokens for.
            model: The model name to use.

        Returns:
            The estimated or exact number of tokens.
        """
        provider = self._get_provider(model)
        if provider == "openai":
            encoding = self._get_encoding(model)
            return len(encoding.encode(text))

        # Approximate for other providers (1 token ~= 4 chars)
        return max(1, len(text) // 4)

    def count(self, text: str) -> int:
        """Count the number of tokens in the given text using the default model.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens.
        """
        return self.count_tokens(text, self.model)
