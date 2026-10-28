# 05 · Count vowels

**Lesson:** [Conditionals and Loops](https://espinovah.github.io/project-mimir/#/lessons/foundations/conditionals-and-loops)

## Task

Write `count_vowels(text)`. It returns how many vowels (`a e i o u`) are in `text`. Upper case counts too.

```python
count_vowels("hello")   # 2
count_vowels("AEIOU")   # 5
count_vowels("rhythm")  # 0
```

## Hints

- A `for` loop over a string gives you one character at a time.
- `"e" in "aeiou"` is `True`. That's a short way to check for a vowel.
- `text.lower()` saves you from checking upper case separately.

## Run the tests

```bash
cd exercises
uv run pytest python-basics/05_count_vowels
```

Stuck? Make the tests pass first, then compare with `solution/count_vowels.py`.
