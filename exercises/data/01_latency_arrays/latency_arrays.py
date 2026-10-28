import numpy as np


def summarize_latencies(latencies_ms: np.ndarray, slow_ms: float = 2000) -> dict:
    """Return count, missing, mean_ms, p95_ms and slow for an array that may contain nan."""
    raise NotImplementedError("Write this function")


def batch_cost(
    input_tokens: np.ndarray, output_tokens: np.ndarray, input_price: float, output_price: float
) -> np.ndarray:
    """Return the cost of each call in US dollars. Prices are per million tokens."""
    raise NotImplementedError("Write this function")
