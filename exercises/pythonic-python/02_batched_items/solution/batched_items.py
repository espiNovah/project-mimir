from collections.abc import Iterable, Iterator


def batched_items(items: Iterable, size: int) -> Iterator[list]:
    """Yield lists of up to `size` items at a time. The last batch may be smaller.

    This must be a generator: it should not read more of `items` than it needs.
    Raise ValueError if size is less than 1.
    """
    if size < 1:
        raise ValueError("size must be at least 1")
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch
