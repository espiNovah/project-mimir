import re

CITATION = re.compile(r"\[(\d+)\]")  # matches [1], [12], ...
REFUSAL = "i don't know"


def has_citation(answer: str) -> bool:
    """PASS if the answer cites a source like [1], or is a refusal containing "i don't know"."""
    if REFUSAL in answer.lower():
        return True
    return bool(CITATION.search(answer))


def citations_were_retrieved(answer: str, num_sources: int) -> bool:
    """PASS if every citation [n] satisfies 1 <= n <= num_sources."""
    cited = {int(n) for n in CITATION.findall(answer)}
    return all(1 <= n <= num_sources for n in cited)


def under_word_limit(answer: str, limit: int = 150) -> bool:
    """PASS if the answer has at most `limit` whitespace-separated words."""
    return len(answer.split()) <= limit


def is_allowed_label(output: str, allowed: set[str]) -> bool:
    """PASS if output, stripped of surrounding whitespace, is exactly one allowed label."""
    return output.strip() in allowed


def run_checks(answer: str, num_sources: int) -> dict[str, bool]:
    """Run the three answer checks and return {check_name: passed}."""
    return {
        "has_citation": has_citation(answer),
        "citations_were_retrieved": citations_were_retrieved(answer, num_sources),
        "under_word_limit": under_word_limit(answer),
    }
