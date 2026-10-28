def normalize(text: str) -> str:
    """Lowercase, trim, collapse whitespace and drop trailing . ! ? , ; :"""
    raise NotImplementedError("Write this function")


def exact_match(output: str, expected: str | list[str]) -> bool:
    """True if output matches expected (or any item of an expected list) after normalizing."""
    raise NotImplementedError("Write this function")


def grade(outputs: list[str], expecteds: list) -> list[bool]:
    """Exact-match each output against its expected answer. Different lengths raise ValueError."""
    raise NotImplementedError("Write this function")


def accuracy(outputs: list[str], expecteds: list) -> float:
    """Share of outputs that exactly match, or 0.0 for no cases."""
    raise NotImplementedError("Write this function")
