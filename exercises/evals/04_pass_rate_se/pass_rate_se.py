import math


def pass_rate(results: list[bool]) -> float:
    """Share of True values. Empty list raises ValueError."""
    raise NotImplementedError("Write this function")


def standard_error(results: list[bool]) -> float:
    """sqrt(p * (1 - p) / n). Empty list raises ValueError."""
    raise NotImplementedError("Write this function")


def confidence_interval(results: list[bool], z: float = 1.96) -> tuple[float, float]:
    """(p - z*SE, p + z*SE), clipped to [0, 1]. Empty list raises ValueError."""
    raise NotImplementedError("Write this function")


def is_real_improvement(old: list[bool], new: list[bool], z: float = 1.96) -> bool:
    """True if new's pass rate is higher and its interval lies entirely above old's."""
    raise NotImplementedError("Write this function")
