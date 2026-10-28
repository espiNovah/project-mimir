import pandas as pd


def summary_by_model(df: pd.DataFrame) -> pd.DataFrame:
    """One row per model: model, calls, timed, mean_latency_ms, pass_rate."""
    return (
        df.groupby("model")
        .agg(
            calls=("trace_id", "size"),
            timed=("latency_ms", "count"),
            mean_latency_ms=("latency_ms", "mean"),
            pass_rate=("passed", "mean"),
        )
        .reset_index()
    )


def pass_rate_by_version(df: pd.DataFrame) -> dict[str, float]:
    """Return {prompt_version: fraction of calls that passed}."""
    rates = df.groupby("prompt_version")["passed"].mean()
    return {version: float(rate) for version, rate in rates.items()}
