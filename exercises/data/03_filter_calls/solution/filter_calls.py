from pathlib import Path

import pandas as pd


def load_calls(path: str | Path) -> pd.DataFrame:
    """Read the call log CSV into a DataFrame."""
    return pd.read_csv(path)


def missing_counts(df: pd.DataFrame) -> dict[str, int]:
    """Return {column: number of missing values} for columns with at least one gap."""
    counts = df.isna().sum()
    return {col: int(n) for col, n in counts[counts > 0].items()}


def slow_failures(df: pd.DataFrame, threshold_ms: float = 2000) -> pd.DataFrame:
    """Return the rows slower than threshold_ms that did not pass."""
    return df[(df["latency_ms"] > threshold_ms) & ~df["passed"]]


def for_models(df: pd.DataFrame, models: list[str]) -> pd.DataFrame:
    """Return the rows whose model is in models."""
    return df[df["model"].isin(models)]
