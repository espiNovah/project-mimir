# 03 · Exact-match grader

**Lesson:** [Code Checks and LLM-as-Judge](https://espinovah.github.io/project-mimir/#/lessons/core/code-checks-and-llm-as-judge)

## Task

For tasks with one right answer, such as a label, a number or a short fact, the simplest grader is **exact match** after light normalization. Without normalization, `"Paris."` would fail against `"paris"`, and you'd be measuring punctuation instead of correctness.

Write:

- `normalize(text)`: lowercase; strip leading and trailing whitespace; collapse runs of whitespace into one space; and remove trailing punctuation (`.`, `!`, `?`, `,`, `;`, `:`).
- `exact_match(output, expected)`: `True` if the two are equal after normalizing. If `expected` is a **list**, any one of the acceptable answers counts.
- `grade(outputs, expecteds)`: returns a list of `True`/`False`, one per pair. If the lists have different lengths, raise `ValueError`, because a silent `zip` would grade the wrong pairs.
- `accuracy(outputs, expecteds)`: the share of `True` grades, or `0.0` for no cases.

```python
normalize("  The  Answer is Paris!! ")     # 'the answer is paris'
exact_match("Paris.", "paris")             # True
exact_match("NYC", ["New York", "NYC"])    # True
accuracy(["4", "five"], ["4", "5"])        # 0.5
```

## Hints

- `" ".join(text.split())` collapses whitespace; `.rstrip(".!?,;:")` removes any mix of trailing punctuation.
- `isinstance(expected, list)` tells you which case you're in.
- `zip(..., strict=True)` raises `ValueError` on a length mismatch.
- Exact match is strict on purpose: `"Paris, France"` does not match `"Paris"`. When that's too strict, you need a different grader, not a looser normalizer.

## Run the tests

```bash
cd exercises
uv run pytest evals/03_exact_match
```

No API key is needed: everything runs offline on fixed data. Stuck? Make the tests pass first, then compare with `solution/exact_match.py`.
