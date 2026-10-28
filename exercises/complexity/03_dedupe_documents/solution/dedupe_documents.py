# Starter: O(n^2), because `key not in seen` scans a list.
# This version: O(n) time and O(n) space, with a set of normalized keys.


def normalize(text: str) -> str:
    """Lowercase and collapse all whitespace to single spaces."""
    return " ".join(text.lower().split())


def dedupe(docs: list[str]) -> list[str]:
    """Return docs without later duplicates (compared after normalize), in original order."""
    seen: set[str] = set()
    unique = []
    for doc in docs:
        key = normalize(doc)
        if key not in seen:
            seen.add(key)
            unique.append(doc)
    return unique
