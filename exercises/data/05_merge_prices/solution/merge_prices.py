import pandas as pd


def add_costs(calls: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """Left-join prices onto calls by model and add a cost_usd column (NaN if unknown)."""
    merged = calls.merge(prices, on="model", how="left", validate="many_to_one")
    merged["cost_usd"] = (
        merged["input_tokens"] * merged["input_per_m"]
        + merged["output_tokens"] * merged["output_per_m"]
    ) / 1_000_000
    return merged


def cost_by_model(df: pd.DataFrame) -> dict[str, float]:
    """Return {model: total cost_usd}, skipping missing costs."""
    totals = df.groupby("model")["cost_usd"].sum()
    return {model: float(total) for model, total in totals.items()}
