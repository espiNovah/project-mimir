# 05 · Join a price list

**Lesson:** [NumPy and pandas Basics](https://espinovah.github.io/project-mimir/#/lessons/foundations/numpy-and-pandas-basics)

## Task

Your call log records tokens but not cost. Prices live in a separate table with one row per model: `model`, `input_per_m` and `output_per_m` (US dollars per million tokens). Write:

- `add_costs(calls, prices)` joins the price list onto the calls and adds a `cost_usd` column: `(input_tokens * input_per_m + output_tokens * output_per_m) / 1_000_000`.
  - Keep **every** call, in the original order, even if its model isn't in the price list. Its cost is then missing (`NaN`).
  - If a call's `output_tokens` is missing, its cost is missing too. Don't fill it with zero: that would make the system look cheaper than it is.
  - If the price list has two rows for the same model, raise an error instead of silently duplicating calls.
- `cost_by_model(df)` takes the result of `add_costs` and returns a dict `{model: total cost}`, skipping missing costs.

```python
calls = pd.DataFrame({"model": ["cheap", "capable"], "input_tokens": [10_000, 1_000],
                      "output_tokens": [1_000, 2_000]})
prices = pd.DataFrame({"model": ["cheap", "capable"], "input_per_m": [1.0, 3.0],
                       "output_per_m": [5.0, 15.0]})
add_costs(calls, prices)["cost_usd"].tolist()   # [0.015, 0.033]
```

## Hints

- `calls.merge(prices, on="model", how="left", validate="many_to_one")`. The `validate` argument raises `pandas.errors.MergeError` when the price list has duplicates.
- A left merge keeps the left table's row order.
- Arithmetic with `NaN` gives `NaN`, which is exactly what you want here.
- `groupby(...)["cost_usd"].sum()` skips missing values.

## Run the tests

```bash
cd exercises
uv run pytest data/05_merge_prices
```

Stuck? Make the tests pass first, then compare with `solution/merge_prices.py`.
