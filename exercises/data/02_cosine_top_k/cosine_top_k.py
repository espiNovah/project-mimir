import numpy as np


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Return the cosine similarity of two 1D vectors."""
    raise NotImplementedError("Write this function")


def normalize(m: np.ndarray) -> np.ndarray:
    """Scale each row (or a single 1D vector) to length 1."""
    raise NotImplementedError("Write this function")


def top_k(query: np.ndarray, docs: np.ndarray, k: int = 3) -> list[tuple[int, float]]:
    """Return the k (row_index, cosine score) pairs most similar to query, best first."""
    raise NotImplementedError("Write this function")
