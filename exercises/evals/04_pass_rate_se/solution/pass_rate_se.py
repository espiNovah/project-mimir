import math


def pass_rate(results: list[bool]) -> float:
    """Share of True values. Empty list raises ValueError."""
    if not results:
        raise ValueError("no results")
    return sum(results) / len(results)


def standard_error(results: list[bool]) -> float:
    """sqrt(p * (1 - p) / n). Empty list raises ValueError."""
    p = pass_rate(results)
    return math.sqrt(p * (1 - p) / len(results))


def confidence_interval(results: list[bool], z: float = 1.96) -> tuple[float, float]:
    """(p - z*SE, p + z*SE), clipped to [0, 1]. Empty list raises ValueError."""
    p = pass_rate(results)
    margin = z * standard_error(results)
    return max(0.0, p - margin), min(1.0, p + margin)


def is_real_improvement(old: list[bool], new: list[bool], z: float = 1.96) -> bool:
    """True if new's pass rate is higher and its interval lies entirely above old's."""
    _, old_high = confidence_interval(old, z)
    new_low, _ = confidence_interval(new, z)
    return pass_rate(new) > pass_rate(old) and new_low > old_high
