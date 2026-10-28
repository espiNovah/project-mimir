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
    if not items:
        raise ValueError("no items")
    rng = random.Random(seed)
    values = []
    for _ in range(n_resamples):
        sample = [rng.choice(items) for _ in items]
        try:
            values.append(stat(sample))
        except ZeroDivisionError:  # e.g. a resample with no failures when computing TPR
            continue
    if not values:
        raise ValueError("every resample was skipped")
    values.sort()
    m = len(values)
    alpha = 1 - confidence
    low = values[int(alpha / 2 * m)]
    high = values[min(int((1 - alpha / 2) * m), m - 1)]
    return low, high
