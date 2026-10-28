# 02 · Batched items

**Lesson:** [Pythonic Python](https://espinovah.github.io/project-mimir/#/lessons/foundations/pythonic-python)

## Task

When you send thousands of texts to an embedding API, you send them in batches. Write a **generator** `batched_items(items, size)` that yields lists of up to `size` items. The last batch can be smaller.

```python
list(batched_items("abcde", 2))   # [["a", "b"], ["c", "d"], ["e"]]
```

It must work on an endless input, such as `itertools.count()`, by only reading what it needs. If `size` is less than 1, raise `ValueError`.

## Hints

- A function that contains `yield` is a generator function.
- Keep a list for the current batch. When it's full, yield it and start a new one.
- Don't forget the leftover items after the loop ends.
- A generator's code doesn't run until someone asks for the first value, so `list(...)` around the call is what triggers the `ValueError`.

## Run the tests

```bash
cd exercises
uv run pytest pythonic-python/02_batched_items
```

Stuck? Make the tests pass first, then compare with `solution/`.
