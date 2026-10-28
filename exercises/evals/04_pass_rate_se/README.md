# 04 · Pass rate and its standard error

**Lesson:** [Eval Statistics](https://espinovah.github.io/project-mimir/#/lessons/core/eval-statistics)

## Task

"41 of 50 passed" is a measurement, and measurements are noisy. If you reran the eval on 50 *different* cases, you'd get a slightly different number. The **standard error** (SE) says how much the pass rate would typically move. For a pass rate `p` measured on `n` cases:

```text
SE = sqrt(p * (1 - p) / n)
```

A rough 95% confidence interval is `p - 1.96 * SE` to `p + 1.96 * SE`. Write:

- `pass_rate(results)`: the share of `True` values in a list of booleans.
- `standard_error(results)`: the formula above.
- `confidence_interval(results, z=1.96)`: `(low, high)`, clipped so it stays between 0 and 1.
- `is_real_improvement(old, new, z=1.96)`: `True` only if the new pass rate is higher **and** the intervals don't overlap, that is, the new low end is above the old high end. This is a deliberately cautious rule of thumb; Eval Statistics explains better tests.

All four raise `ValueError` on an empty list.

```python
results = [True] * 41 + [False] * 9
pass_rate(results)            # 0.82
standard_error(results)       # 0.0543...
confidence_interval(results)  # (0.7135..., 0.9265...)
```

With 50 cases, the interval is more than 20 points wide. That's why a one-point gain on a small eval is usually noise.

## Hints

- `sum(results)` counts the `True` values.
- `math.sqrt`, `max(0.0, ...)` and `min(1.0, ...)`.
- When `p` is 0 or 1 the SE is 0, which is a sign the formula breaks down at the edges, not that you're certain. It's fine for these exercises.

## Run the tests

```bash
cd exercises
uv run pytest evals/04_pass_rate_se
```

No API key is needed: everything runs offline on fixed data. Stuck? Make the tests pass first, then compare with `solution/pass_rate_se.py`.
