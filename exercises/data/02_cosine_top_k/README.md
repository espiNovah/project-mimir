# 02 · Cosine similarity and top-k

**Lesson:** [NumPy and pandas Basics](https://espinovah.github.io/project-mimir/#/lessons/foundations/numpy-and-pandas-basics)
Also used in: [Vectors and Similarity](https://espinovah.github.io/project-mimir/#/lessons/core/vectors-and-similarity)

## Task

Retrieval in a RAG system comes down to three array operations. Write them with NumPy:

- `cosine(a, b)` returns the cosine similarity of two 1D vectors: their dot product divided by the product of their lengths (norms). Return a plain `float`.
- `normalize(m)` scales every **row** of a 2D array to length 1. (It should also work on a single 1D vector.)
- `top_k(query, docs, k=3)` returns the `k` rows of `docs` most similar to `query` by cosine similarity, as a list of `(row_index, score)` tuples, best first.

```python
a = np.array([1.0, 2.0, 2.0])
b = np.array([2.0, 0.0, 1.0])
cosine(a, b)        # 0.596...   (4 / (3 * 2.236))

docs = np.array([[1.0, 0.0], [0.0, 2.0], [3.0, 3.0]])
top_k(np.array([1.0, 1.0]), docs, k=2)
# [(2, 1.0), (0, 0.707...)]
```

## Hints

- `a @ b` is the dot product; `np.linalg.norm(a)` is the length.
- `np.linalg.norm(m, axis=-1, keepdims=True)` gives one norm per row, shaped so that `m / norms` divides each row by its own norm (broadcasting).
- After normalizing, cosine similarity is just a dot product, so `normalize(docs) @ normalize(query)` scores every document at once.
- `np.argsort(-scores)` gives indices from highest score to lowest.
- Convert to plain Python with `int(i)` and `float(score)`.

## Run the tests

```bash
cd exercises
uv run pytest data/02_cosine_top_k
```

Stuck? Make the tests pass first, then compare with `solution/cosine_top_k.py`.
