# Evals

Practice for the evals lessons, all offline: no API key, no model calls, fixed data and fixed random seeds, so every run gives the same result.

- [Why Evals Matter](https://espinovah.github.io/project-mimir/#/lessons/core/why-evals-matter): reading traces and counting failure categories (exercise 01).
- [Code Checks and LLM-as-Judge](https://espinovah.github.io/project-mimir/#/lessons/core/code-checks-and-llm-as-judge): code graders (02, 03) and measuring a judge with confusion-matrix rates and bootstrap intervals (05, 06).
- [Eval Statistics](https://espinovah.github.io/project-mimir/#/lessons/core/eval-statistics): pass rates and their uncertainty (04, 05, 06).

## How to run

From the repo root:

```bash
cd exercises
uv run pytest evals/01_read_traces   # one exercise
uv run pytest evals                  # the whole set
```

## Exercises

| # | Exercise | Practices |
| --- | --- | --- |
| 01 | [Read traces](01_read_traces/) | JSONL traces, error rate per prompt version, counting failure categories |
| 02 | [Code checks](02_code_checks/) | citation, word-limit and allowed-label graders |
| 03 | [Exact-match grader](03_exact_match/) | normalization, multiple acceptable answers, accuracy |
| 04 | [Pass rate and its standard error](04_pass_rate_se/) | SE of a proportion, 95% intervals, "is this gain real?" |
| 05 | [Confusion matrix, precision, recall and F1](05_confusion_matrix/) | tp/fp/fn/tn, precision, recall (TPR), F1, TNR |
| 06 | [Bootstrap confidence interval](06_bootstrap_ci/) | resampling with a fixed seed, percentile intervals |
