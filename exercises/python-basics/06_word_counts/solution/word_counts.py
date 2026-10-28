def word_counts(text: str) -> dict[str, int]:
    """Return a dict mapping each word in text to how many times it appears.

    Words are compared in lower case, and the punctuation marks . , ! ? are ignored.
    """
    cleaned = text.lower()
    for mark in ".,!?":
        cleaned = cleaned.replace(mark, "")

    counts: dict[str, int] = {}
    for word in cleaned.split():
        counts[word] = counts.get(word, 0) + 1
    return counts
