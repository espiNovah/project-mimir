def estimate_tokens(text: str, chars_per_token: int = 4) -> int:
    """Estimate how many tokens text uses: its length divided by chars_per_token, rounded UP.

    An empty string uses 0 tokens.
    """
    raise NotImplementedError("Write this function")


def fits_budget(texts: list[str], budget: int, chars_per_token: int = 4) -> bool:
    """Return True if the estimated tokens of all texts added together is at most budget."""
    raise NotImplementedError("Write this function")
