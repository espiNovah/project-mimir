# 05 · Confusion matrix, precision, recall and F1

**Lesson:** [Eval Statistics](https://espinovah.github.io/project-mimir/#/lessons/core/eval-statistics)
Also used in: [Code Checks and LLM-as-Judge](https://espinovah.github.io/project-mimir/#/lessons/core/code-checks-and-llm-as-judge)

## Task

You labeled 20 outputs PASS or FAIL yourself, and an LLM judge labeled the same 20. How good is the judge? Plain agreement hides the important part, so you count the four kinds of outcome, treating **FAIL as the positive class** (it's what the judge is trying to detect):

| | judge says FAIL | judge says PASS |
| --- | --- | --- |
| **you said FAIL** | true positive (`tp`) | false negative (`fn`) |
| **you said PASS** | false positive (`fp`) | true negative (`tn`) |

Write:

- `confusion_matrix(pairs, positive="FAIL")`: `pairs` is a list of `(human, judge)` labels. Return `{"tp": ..., "fp": ..., "fn": ..., "tn": ...}`.
- `precision(cm)` = `tp / (tp + fp)`: when the judge says FAIL, how often is it right?
- `recall(cm)` = `tp / (tp + fn)`: of the real failures, how many did it catch? This is the lesson's **TPR**.
- `f1(cm)` = `2 * precision * recall / (precision + recall)`: one number that's high only when both are.
- `tnr(cm)` = `tn / (tn + fp)`: of the real passes, how many did it let through?

If a denominator is zero, return `0.0` instead of crashing.

```python
pairs = [("FAIL", "FAIL")] * 6 + [("FAIL", "PASS")] * 2 + [("PASS", "FAIL")] * 3 + [("PASS", "PASS")] * 9
cm = confusion_matrix(pairs)   # {'tp': 6, 'fp': 3, 'fn': 2, 'tn': 9}
precision(cm)                  # 0.667
recall(cm)                     # 0.75
f1(cm)                         # 0.706
tnr(cm)                        # 0.75
```

## Hints

- Loop over the pairs once and decide which of the four boxes each one goes in.
- A judge that always says PASS has a TNR of 1.0 and a recall of 0.0. Try it: the tests do.
- Any label that isn't `positive` counts as negative.

## Run the tests

```bash
cd exercises
uv run pytest evals/05_confusion_matrix
```

No API key is needed: everything runs offline on fixed data. Stuck? Make the tests pass first, then compare with `solution/confusion_matrix.py`.
