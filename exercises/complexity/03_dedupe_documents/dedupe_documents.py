def normalize(text: str) -> str:
    """Lowercase and collapse all whitespace to single spaces."""
    return " ".join(text.lower().split())


def dedupe(docs: list[str]) -> list[str]:
    """Return docs without later duplicates (compared after normalize), in original order."""
    seen = []
    unique = []
    for doc in docs:
        key = normalize(doc)
        if key not in seen:
            seen.append(key)
            unique.append(doc)
    return unique
