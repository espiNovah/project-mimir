import re


def has_citation(answer: str) -> bool:
    """PASS if the answer cites a source like [1], or is a refusal containing "i don't know"."""
    raise NotImplementedError("Write this function")


def citations_were_retrieved(answer: str, num_sources: int) -> bool:
    """PASS if every citation [n] satisfies 1 <= n <= num_sources."""
    raise NotImplementedError("Write this function")


def under_word_limit(answer: str, limit: int = 150) -> bool:
    """PASS if the answer has at most `limit` whitespace-separated words."""
    raise NotImplementedError("Write this function")


def is_allowed_label(output: str, allowed: set[str]) -> bool:
    """PASS if output, stripped of surrounding whitespace, is exactly one allowed label."""
    raise NotImplementedError("Write this function")


def run_checks(answer: str, num_sources: int) -> dict[str, bool]:
    """Run the three answer checks and return {check_name: passed}."""
    raise NotImplementedError("Write this function")
