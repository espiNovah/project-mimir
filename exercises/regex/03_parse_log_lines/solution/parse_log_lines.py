import re

LINE_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>[A-Z]+) "
    r"model=(?P<model>\S+) latency_ms=(?P<latency_ms>\d+) status=(?P<status>\d{3})"
)


def parse_line(line: str) -> dict | None:
    """Parse one request log line into a dict, or return None if it doesn't fit.

    Keys: date, time, level, model (strings) and latency_ms, status (ints).
    """
    m = LINE_RE.fullmatch(line.strip())
    if m is None:
        return None
    row = m.groupdict()
    row["latency_ms"] = int(row["latency_ms"])
    row["status"] = int(row["status"])
    return row


def slow_requests(lines: list[str], threshold_ms: int = 2000) -> list[tuple[str, str, int]]:
    """Return (time, model, latency_ms) for every valid line slower than threshold_ms."""
    slow = []
    for line in lines:
        row = parse_line(line)
        if row is not None and row["latency_ms"] > threshold_ms:
            slow.append((row["time"], row["model"], row["latency_ms"]))
    return slow
