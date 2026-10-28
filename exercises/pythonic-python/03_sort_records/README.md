# 03 · Sort records

**Lesson:** [Pythonic Python](https://espinovah.github.io/project-mimir/#/lessons/foundations/pythonic-python)

## Task

Write two functions that sort lists of dictionaries with `sorted(..., key=...)`:

- `rank_results(results)` sorts search results by `"score"`, highest first. When two scores tie, sort those by `"name"` from A to Z. Return a new list and leave the input alone.
- `cheapest(models, n)` returns the **names** of the `n` models with the lowest `"price"`.

```python
rank_results([{"name": "b", "score": 0.7}, {"name": "a", "score": 0.7}])
# [{"name": "a", "score": 0.7}, {"name": "b", "score": 0.7}]
```

## Hints

- `key=lambda r: r["score"]` tells `sorted` what to compare.
- A key can return a tuple. Tuples compare item by item, which handles tie-breaks.
- To sort one part high-to-low and another low-to-high, negate the number.

## Run the tests

```bash
cd exercises
uv run pytest pythonic-python/03_sort_records
```

Stuck? Make the tests pass first, then compare with `solution/`.
