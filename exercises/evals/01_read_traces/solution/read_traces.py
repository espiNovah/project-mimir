import json
from collections import Counter
from pathlib import Path


def load_traces(path: str | Path) -> list[dict]:
    """Return one dict per non-blank line of a JSONL trace file, in order."""
    traces = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                traces.append(json.loads(line))
    return traces


def error_rate_by_version(traces: list[dict]) -> dict[str, float]:
    """Return {prompt_version: share of traces whose "error" is not None}."""
    calls: dict[str, int] = {}
    errors: dict[str, int] = {}
    for t in traces:
        version = t["prompt_version"]
        calls[version] = calls.get(version, 0) + 1
        errors[version] = errors.get(version, 0) + (t["error"] is not None)
    return {version: errors[version] / calls[version] for version in calls}


def count_categories(notes: list[dict]) -> list[tuple[str, int]]:
    """Return (category, count) pairs, most common first, ties in alphabetical order."""
    counts = Counter(note["category"] for note in notes)
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
