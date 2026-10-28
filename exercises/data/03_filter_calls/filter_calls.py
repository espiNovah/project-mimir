from pathlib import Path

import pandas as pd


def load_calls(path: str | Path) -> pd.DataFrame:
    """Read the call log CSV into a DataFrame."""
    raise NotImplementedError("Write this function")


def missing_counts(df: pd.DataFrame) -> dict[str, int]:
    """Return {column: number of missing values} for columns with at least one gap."""
    raise NotImplementedError("Write this function")


def slow_failures(df: pd.DataFrame, threshold_ms: float = 2000) -> pd.DataFrame:
    """Return the rows slower than threshold_ms that did not pass."""
    raise NotImplementedError("Write this function")


def for_models(df: pd.DataFrame, models: list[str]) -> pd.DataFrame:
    """Return the rows whose model is in models."""
    raise NotImplementedError("Write this function")
