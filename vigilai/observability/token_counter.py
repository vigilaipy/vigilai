import tiktoken

__all__ = ["TokenCounter"]

class TokenCounter:
    """Utility to count tokens using tiktoken."""

    def __init__(self, model: str = "gpt-4o") -> None:
        """Initialize the token counter.
        
        Args:
            model: The model name to use for token encoding.
        """
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        """Count the number of tokens in the given text.
        
        Args:
            text: The text to count tokens for.
            
        Returns:
            The number of tokens.
        """
        return len(self.encoding.encode(text))
