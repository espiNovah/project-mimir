from bisect import bisect_left, bisect_right


def count_in_range(scores: list[float], lo: float, hi: float) -> int:
    """Return how many scores s (sorted ascending) satisfy lo <= s <= hi."""
    return sum(1 for s in scores if lo <= s <= hi)


def percentile_rank(scores: list[float], value: float) -> float:
    """Return the fraction of scores (sorted ascending) strictly below value."""
    if not scores:
        return 0.0
    below = 0
    for s in scores:
        if s < value:
            below += 1
    return below / len(scores)
