# 06 · Sliding windows

**Lesson:** [Pythonic Python](https://espinovah.github.io/project-mimir/#/lessons/foundations/pythonic-python)

## Task

RAG systems split long documents into overlapping chunks so that an idea cut at a chunk edge still appears whole in the next chunk. Write a **generator** `sliding_windows(words, size, overlap)` that yields lists of `size` words, where each window repeats the last `overlap` words of the one before.

```python
words = "a b c d e f g".split()
list(sliding_windows(words, 4, 2))
# [["a","b","c","d"], ["c","d","e","f"], ["e","f","g"]]
```

Stop as soon as a window reaches the end of the list, so you never yield a window that only repeats overlap words. Raise `ValueError` unless `size >= 1` and `0 <= overlap < size`.

## Hints

- Each window starts `size - overlap` words after the previous one.
- `range(start, stop, step)` and slicing `words[i : i + size]` do most of the work. Slices past the end are just shorter.
- After yielding, check whether that window reached the end, and `break` if it did.

## Run the tests

```bash
cd exercises
uv run pytest pythonic-python/06_sliding_windows
```

Stuck? Make the tests pass first, then compare with `solution/`.
