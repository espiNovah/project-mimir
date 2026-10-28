# 06 · Bootstrap confidence interval

**Lesson:** [Eval Statistics](https://espinovah.github.io/project-mimir/#/lessons/core/eval-statistics)
Also used in: [Code Checks and LLM-as-Judge](https://espinovah.github.io/project-mimir/#/lessons/core/code-checks-and-llm-as-judge)

## Task

The standard-error formula from exercise 04 works for a simple pass rate. For anything more complicated, such as a judge's TPR, F1 or a median latency, there's a method that works for almost any statistic: the **bootstrap**. Pretend your sample is the whole population, draw many new samples from it *with replacement*, compute the statistic on each, and see how much it varies.

Write `bootstrap_ci(items, stat, n_resamples=2000, seed=0, confidence=0.95)` that returns `(low, high)`:

1. Make a random generator with `rng = random.Random(seed)`, so the same seed always gives the same interval. Never use the global `random` functions here.
1. Repeat `n_resamples` times: build a resample of the **same length** as `items` by picking items at random with replacement, and compute `stat(resample)`. If `stat` raises `ZeroDivisionError` (say, a resample with no failures in it when you're computing TPR), skip that resample.
1. Sort the results. With `alpha = 1 - confidence` and `m` kept results, return the values at index `int(alpha / 2 * m)` and `int((1 - alpha / 2) * m)`, capping the second index at `m - 1`.

If every resample was skipped, or `items` is empty, raise `ValueError`.

```python
results = [True] * 70 + [False] * 30
bootstrap_ci(results, lambda xs: sum(xs) / len(xs))
# roughly (0.61, 0.79): close to exercise 04's 0.70 ± 0.09
```

This is the same procedure as `bootstrap_ci` in the Code Checks and LLM-as-Judge lesson, made general by passing the statistic in as a function.

## Hints

- `[rng.choice(items) for _ in items]` is one resample.
- `stat` is just a function. You call it like any other: `stat(sample)`.
- `try` / `except ZeroDivisionError: continue` skips a resample.
- Why a fixed seed? So your eval report is reproducible: rerun it tomorrow and get the same interval.

## Run the tests

```bash
cd exercises
uv run pytest evals/06_bootstrap_ci
```

No API key is needed: everything runs offline on fixed data. Stuck? Make the tests pass first, then compare with `solution/bootstrap_ci.py`.
