# 04 · Drop empty replies

**Lesson:** [Debugging and Logging](https://espinovah.github.io/project-mimir/#/lessons/foundations/debugging-and-logging)

## The bug report

`drop_empty_replies(replies)` should return a new list with every empty or whitespace-only reply removed, keeping the order of the rest. It must not change the list it was given, because the caller still needs the raw replies for logging.

```python
raw = ["Paris", "", "", "  ", "Lima"]
drop_empty_replies(raw)   # expected: ['Paris', 'Lima']
raw                       # expected: unchanged
```

It works on some inputs but not others, and the raw replies end up changed. Step through the loop with two empty replies in a row and watch the list.

## How to work on it

1. Run the tests and read the failures. Which input breaks, and what came out instead?
1. Set a breakpoint (or add `breakpoint()`) and watch the variables until you see where the program stops doing what you expect.
1. Write one sentence at the top of the file saying what the bug was, then fix it.

## Run the tests

```bash
cd exercises
uv run pytest debugging/04_drop_empty_replies
```

Stuck? Make the tests pass first, then compare with `solution/drop_empty_replies.py`.
