# Starter: O(n) per question, scanning every score.
# This version: O(log n) per question, with binary search on the sorted list.
from bisect import bisect_left, bisect_right


def count_in_range(scores: list[float], lo: float, hi: float) -> int:
    """Return how many scores s (sorted ascending) satisfy lo <= s <= hi."""
    if lo > hi:
        return 0
    return bisect_right(scores, hi) - bisect_left(scores, lo)


def percentile_rank(scores: list[float], value: float) -> float:
    """Return the fraction of scores (sorted ascending) strictly below value."""
    if not scores:
        return 0.0
    return bisect_left(scores, value) / len(scores)
