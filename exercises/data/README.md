# Data

Exercises for the [NumPy and pandas Basics](https://espinovah.github.io/project-mimir/#/lessons/foundations/numpy-and-pandas-basics) lesson: vectorized arrays and boolean masks, missing values, filtering, `groupby` with named aggregation, and `merge`. The data is the kind your own AI systems will produce: a log of model calls with latencies, tokens and eval results. Everything is bundled or built inline, so no network is needed.

Exercise 02 also drills the array operations from [Vectors and Similarity](https://espinovah.github.io/project-mimir/#/lessons/core/vectors-and-similarity): dot products, norms, normalizing rows and top-k retrieval.

## How to run

From the repo root:

```bash
cd exercises
uv run pytest data/01_latency_arrays   # one exercise
uv run pytest data                     # the whole set
```

NumPy and pandas are installed from `exercises/pyproject.toml` on the first run.

## Exercises

| # | Exercise | Practices |
| --- | --- | --- |
| 01 | [Latency arrays](01_latency_arrays/) | vectorization, boolean masks, `nan`, `np.nanmean` |
| 02 | [Cosine similarity and top-k](02_cosine_top_k/) | `@`, `np.linalg.norm`, broadcasting, `argsort` |
| 03 | [Load and filter a call log](03_filter_calls/) | `read_csv`, `isna`, masks with `&` and `~`, `isin` |
| 04 | [Summarize calls per model](04_group_summary/) | `groupby`, named aggregation, `size` vs `count` |
| 05 | [Join a price list](05_merge_prices/) | `merge`, `how="left"`, `validate`, missing values in math |
