import re


def parse_line(line: str) -> dict | None:
    """Parse one request log line into a dict, or return None if it doesn't fit.

    Keys: date, time, level, model (strings) and latency_ms, status (ints).
    """
    raise NotImplementedError("Write this function")


def slow_requests(lines: list[str], threshold_ms: int = 2000) -> list[tuple[str, str, int]]:
    """Return (time, model, latency_ms) for every valid line slower than threshold_ms."""
    raise NotImplementedError("Write this function")
