from collections.abc import Iterator


def sliding_windows(words: list[str], size: int, overlap: int) -> Iterator[list[str]]:
    """Yield windows of `size` words, where each window shares `overlap` words with the last.

    Stop after the window that reaches the end of the list. Raise ValueError unless
    size >= 1 and 0 <= overlap < size.
    """
    raise NotImplementedError("Write this generator")
