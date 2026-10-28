# 01 · Latency arrays

**Lesson:** [NumPy and pandas Basics](https://espinovah.github.io/project-mimir/#/lessons/foundations/numpy-and-pandas-basics)

## Task

You have the latencies of a batch of model calls as a NumPy array, in milliseconds. Calls that timed out have no latency, recorded as `np.nan`. Write `summarize_latencies(latencies_ms, slow_ms=2000)`, which returns a dict:

| Key | Value |
| --- | --- |
| `count` | how many latencies are present (not `nan`) |
| `missing` | how many are `nan` |
| `mean_ms` | the mean of the present values |
| `p95_ms` | the 95th percentile of the present values |
| `slow` | how many are greater than `slow_ms` |

Then write `batch_cost(input_tokens, output_tokens, input_price, output_price)`. The token counts are arrays, one entry per call, and the prices are US dollars per million tokens. Return an **array** of per-call costs.

```python
lat = np.array([820, 1340, np.nan, 2950])
summarize_latencies(lat)
# {'count': 3, 'missing': 1, 'mean_ms': 1703.33..., 'p95_ms': 2789.0, 'slow': 1}
batch_cost(np.array([1_000_000, 0]), np.array([0, 1_000_000]), 1.0, 5.0)
# array([1., 5.])
```

Use no `for` loops: every step is one vectorized expression.

## Hints

- `np.isnan(a)` is a boolean mask; `mask.sum()` counts the `True` values, and `~mask` flips it.
- `a.mean()` returns `nan` if any value is `nan`. `np.nanmean` and `np.nanpercentile` skip them.
- `nan > 2000` is `False`, so missing values never count as slow.
- Convert NumPy numbers to plain Python ones with `int(...)` and `float(...)` so the dict is easy to print and compare.

## Run the tests

```bash
cd exercises
uv run pytest data/01_latency_arrays
```

Stuck? Make the tests pass first, then compare with `solution/latency_arrays.py`.
