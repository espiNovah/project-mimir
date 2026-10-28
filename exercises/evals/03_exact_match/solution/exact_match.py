def normalize(text: str) -> str:
    """Lowercase, trim, collapse whitespace and drop trailing . ! ? , ; :"""
    return " ".join(text.lower().split()).rstrip(".!?,;:").rstrip()


def exact_match(output: str, expected: str | list[str]) -> bool:
    """True if output matches expected (or any item of an expected list) after normalizing."""
    options = expected if isinstance(expected, list) else [expected]
    out = normalize(output)
    return any(out == normalize(option) for option in options)


def grade(outputs: list[str], expecteds: list) -> list[bool]:
    """Exact-match each output against its expected answer. Different lengths raise ValueError."""
    return [exact_match(o, e) for o, e in zip(outputs, expecteds, strict=True)]


def accuracy(outputs: list[str], expecteds: list) -> float:
    """Share of outputs that exactly match, or 0.0 for no cases."""
    grades = grade(outputs, expecteds)
    return sum(grades) / len(grades) if grades else 0.0
