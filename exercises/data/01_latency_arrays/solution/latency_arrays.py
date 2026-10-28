import numpy as np


def summarize_latencies(latencies_ms: np.ndarray, slow_ms: float = 2000) -> dict:
    """Return count, missing, mean_ms, p95_ms and slow for an array that may contain nan."""
    missing = np.isnan(latencies_ms)
    return {
        "count": int((~missing).sum()),
        "missing": int(missing.sum()),
        "mean_ms": float(np.nanmean(latencies_ms)),
        "p95_ms": float(np.nanpercentile(latencies_ms, 95)),
        "slow": int((latencies_ms > slow_ms).sum()),  # nan > x is False
    }


def batch_cost(
    input_tokens: np.ndarray, output_tokens: np.ndarray, input_price: float, output_price: float
) -> np.ndarray:
    """Return the cost of each call in US dollars. Prices are per million tokens."""
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000
