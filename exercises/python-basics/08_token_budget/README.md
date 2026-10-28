# 08 · Token budget

**Lesson:** [Functions](https://espinovah.github.io/project-mimir/#/lessons/foundations/functions)

## Task

Language models read text as **tokens**. A rough rule of thumb is that one token is about 4 characters of English. Write two functions:

- `estimate_tokens(text, chars_per_token=4)` returns `len(text) / chars_per_token`, **rounded up** to a whole number.
- `fits_budget(texts, budget, chars_per_token=4)` returns `True` if the estimates for all the texts add up to `budget` or less.

```python
estimate_tokens("abcde")                     # 2  (5 / 4 = 1.25, rounded up)
estimate_tokens("abcdefgh", chars_per_token=3)  # 3
fits_budget(["abcd", "abcde"], budget=2)    # False (1 + 2 = 3)
```

## Hints

- `math.ceil` rounds up, or you can do it with integer division: `-(-a // b)`.
- `fits_budget` should call `estimate_tokens` rather than repeat its logic. Remember to pass `chars_per_token` along.
- The `= 4` in the signature is a default value. Callers can leave it out.

## Run the tests

```bash
cd exercises
uv run pytest python-basics/08_token_budget
```

Stuck? Make the tests pass first, then compare with `solution/token_budget.py`.
