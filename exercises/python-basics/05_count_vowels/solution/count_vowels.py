def count_vowels(text: str) -> int:
    """Return how many vowels (a, e, i, o, u, upper or lower case) are in text."""
    count = 0
    for char in text.lower():
        if char in "aeiou":
            count += 1
    return count
