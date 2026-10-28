import pandas as pd


def summary_by_model(df: pd.DataFrame) -> pd.DataFrame:
    """One row per model: model, calls, timed, mean_latency_ms, pass_rate."""
    raise NotImplementedError("Write this function")


def pass_rate_by_version(df: pd.DataFrame) -> dict[str, float]:
    """Return {prompt_version: fraction of calls that passed}."""
    raise NotImplementedError("Write this function")
