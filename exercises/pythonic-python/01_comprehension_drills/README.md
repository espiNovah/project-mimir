# 01 · Comprehension drills

**Lesson:** [comprehension_drills.py](https://espinovah.github.io/project-mimir/#/lessons/foundations pythonic-python/Pythonic Python)

## Task

Write each function as a **single** comprehension:

- `even_squares(numbers)`: a list of the squares of the even numbers.
- `word_lengths(words)`: a dict from each word to its length.
- `initials(names)`: a set of the upper-case first letters, skipping empty names.

```python
even_squares([1, 2, 3, 4])          # [4, 16]
word_lengths(["agent", "tool"])     # {"agent": 5, "tool": 4}
initials(["ada", "Alan", ""])       # {"A"}
```

## Hints

- The shape is `[expression for item in items if condition]`.
- Dict comprehensions use `{key: value for ...}`. Set comprehensions use `{value for ...}`.
- An empty string is falsy, so `if name` skips it.

## Run the tests

```bash
cd exercises
uv run pytest pythonic-python/01_comprehension_drills
```

Stuck? Make the tests pass first, then compare with `solution/`.
