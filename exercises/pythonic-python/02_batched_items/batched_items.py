from collections.abc import Iterable, Iterator


def batched_items(items: Iterable, size: int) -> Iterator[list]:
    """Yield lists of up to `size` items at a time. The last batch may be smaller.

    This must be a generator: it should not read more of `items` than it needs.
    Raise ValueError if size is less than 1.
    """
    raise NotImplementedError("Write this generator")
