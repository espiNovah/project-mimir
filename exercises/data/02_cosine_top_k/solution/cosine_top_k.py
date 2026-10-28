import numpy as np


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Return the cosine similarity of two 1D vectors."""
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def normalize(m: np.ndarray) -> np.ndarray:
    """Scale each row (or a single 1D vector) to length 1."""
    return m / np.linalg.norm(m, axis=-1, keepdims=True)


def top_k(query: np.ndarray, docs: np.ndarray, k: int = 3) -> list[tuple[int, float]]:
    """Return the k (row_index, cosine score) pairs most similar to query, best first."""
    scores = normalize(docs) @ normalize(query)  # one cosine score per document
    best = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in best]
