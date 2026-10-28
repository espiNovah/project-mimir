def even_squares(numbers: list[int]) -> list[int]:
    """Return the squares of the even numbers, in their original order."""
    return [n * n for n in numbers if n % 2 == 0]


def word_lengths(words: list[str]) -> dict[str, int]:
    """Return a dict mapping each word to its length."""
    return {word: len(word) for word in words}


def initials(names: list[str]) -> set[str]:
    """Return the set of upper-case first letters of the non-empty names."""
    return {name[0].upper() for name in names if name}
