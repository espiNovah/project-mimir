# 04 · Summarize calls per model

**Lesson:** [NumPy and pandas Basics](https://espinovah.github.io/project-mimir/#/lessons/foundations/numpy-and-pandas-basics)

## Task

Most questions about a log are "per something": pass rate per prompt version, average latency per model. Using the same `calls.csv` as exercise 03, write:

- `summary_by_model(df)` returns a DataFrame with **one row per model**, sorted by model name, and these columns, in this order:

  | Column | Meaning |
  | --- | --- |
  | `model` | the model name (an ordinary column, not the index) |
  | `calls` | number of rows for the model, missing values or not |
  | `timed` | number of rows with a latency |
  | `mean_latency_ms` | mean latency, skipping missing values |
  | `pass_rate` | the fraction of calls that passed |

- `pass_rate_by_version(df)` returns a dict such as `{"v1": 0.6, "v2": 0.571...}`.

```python
summary_by_model(df)
#      model  calls  timed  mean_latency_ms  pass_rate
# 0  capable      5      4           2632.5   0.600000
# 1    cheap      7      6           1475.0   0.571429
```

Reporting `calls` next to `timed` is the habit from the lesson: it shows how many rows each average is really based on.

## Hints

- Named aggregation: `.agg(calls=("trace_id", "size"), timed=("latency_ms", "count"), ...)`.
- `"size"` counts every row; `"count"` counts only the non-missing ones.
- The mean of a `True`/`False` column is the fraction that are `True`.
- `groupby` sorts by the group key, and `.reset_index()` turns the group labels back into a column.

## Run the tests

```bash
cd exercises
uv run pytest data/04_group_summary
```

Stuck? Make the tests pass first, then compare with `solution/group_summary.py`.
