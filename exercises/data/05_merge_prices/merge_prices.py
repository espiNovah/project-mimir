import pandas as pd


def add_costs(calls: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """Left-join prices onto calls by model and add a cost_usd column (NaN if unknown)."""
    raise NotImplementedError("Write this function")


def cost_by_model(df: pd.DataFrame) -> dict[str, float]:
    """Return {model: total cost_usd}, skipping missing costs."""
    raise NotImplementedError("Write this function")
