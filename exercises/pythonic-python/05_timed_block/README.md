# 05 · Timed block

**Lesson:** [Pythonic Python](https://espinovah.github.io/project-mimir/#/lessons/foundations/pythonic-python)

## Task

Write a context manager `timed_block(label, log)` that measures how long the code in a `with` block takes. When the block ends, append a tuple `(label, seconds)` to `log`.

```python
log = []
with timed_block("call model", log):
    do_slow_thing()
print(log)   # [("call model", 1.23...)]
```

It must still record the time if the block raises an exception, and the exception must still reach the caller.

## Hints

- With `@contextmanager`, the code before `yield` runs on entry and the code after runs on exit.
- `time.perf_counter()` is the right clock for measuring durations.
- `try: yield` / `finally: ...` runs the cleanup either way, without swallowing the error.

## Run the tests

```bash
cd exercises
uv run pytest pythonic-python/05_timed_block
```

Stuck? Make the tests pass first, then compare with `solution/`.
