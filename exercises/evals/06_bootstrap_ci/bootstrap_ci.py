import random
from collections.abc import Callable, Sequence


def bootstrap_ci(
    items: Sequence,
    stat: Callable[[list], float],
    n_resamples: int = 2000,
    seed: int = 0,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Percentile bootstrap interval for stat(items), using random.Random(seed).

    Resamples that make stat raise ZeroDivisionError are skipped. Raises ValueError
    if items is empty or every resample was skipped.
    """
    raise NotImplementedError("Write this function")
