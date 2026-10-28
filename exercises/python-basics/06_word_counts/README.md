# 06 · Word counts

**Lesson:** [Lists, Dicts, Sets and Tuples](https://espinovah.github.io/project-mimir/#/lessons/foundations/data-structures)

## Task

Write `word_counts(text)`. It returns a dictionary that maps each word to the number of times it appears.

- Compare words in lower case, so `"The"` and `"the"` are the same word.
- Ignore the punctuation marks `.` `,` `!` `?`.

```python
word_counts("Hi! Hi, you.")   # {"hi": 2, "you": 1}
```

## Hints

- `text.split()` with no argument splits on any run of spaces.
- `str.replace(".", "")` removes every full stop.
- `counts.get(word, 0)` returns 0 for a word you haven't seen yet.

## Run the tests

```bash
cd exercises
uv run pytest python-basics/06_word_counts
```

Stuck? Make the tests pass first, then compare with `solution/word_counts.py`.
