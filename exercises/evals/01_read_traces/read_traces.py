import json
from collections import Counter
from pathlib import Path


def load_traces(path: str | Path) -> list[dict]:
    """Return one dict per non-blank line of a JSONL trace file, in order."""
    raise NotImplementedError("Write this function")


def error_rate_by_version(traces: list[dict]) -> dict[str, float]:
    """Return {prompt_version: share of traces whose "error" is not None}."""
    raise NotImplementedError("Write this function")


def count_categories(notes: list[dict]) -> list[tuple[str, int]]:
    """Return (category, count) pairs, most common first, ties in alphabetical order."""
    raise NotImplementedError("Write this function")
