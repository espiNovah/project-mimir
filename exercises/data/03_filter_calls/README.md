# 03 · Load and filter a call log

**Lesson:** [NumPy and pandas Basics](https://espinovah.github.io/project-mimir/#/lessons/foundations/numpy-and-pandas-basics)

## Task

`calls.csv` in this folder is a small log of model calls, one row per call, with the columns `trace_id`, `model`, `prompt_version`, `latency_ms`, `input_tokens`, `output_tokens` and `passed` (whether the output passed its eval). Two calls timed out, so their latency and output tokens are missing. Write:

- `load_calls(path)` reads the CSV into a DataFrame.
- `missing_counts(df)` returns a dict of `{column: number_missing}` for **only** the columns that have at least one missing value.
- `slow_failures(df, threshold_ms=2000)` returns the rows that are slower than the threshold **and** failed their eval.
- `for_models(df, models)` returns the rows whose `model` is in the list `models`.

```python
df = load_calls("calls.csv")
missing_counts(df)                    # {'latency_ms': 2, 'output_tokens': 2}
slow_failures(df)["trace_id"].tolist()  # ['t07', 't10']
```

Keep the rows in their original order, and don't change the DataFrame you're given.

## Hints

- Take a first look in a notebook or the REPL with `df.head()`, `df.info()` and `df.isna().sum()`.
- `df.isna().sum()` is a Series. You can filter a Series with a mask too: `s[s > 0]`. `.to_dict()` turns it into a dict.
- Combine conditions with `&` and `~`, and put each condition in parentheses.
- `df["model"].isin(models)` checks membership in a list.
- The tests find `calls.csv` next to the test file, so you don't need to worry about which folder you run from.

## Run the tests

```bash
cd exercises
uv run pytest data/03_filter_calls
```

Stuck? Make the tests pass first, then compare with `solution/filter_calls.py`.
