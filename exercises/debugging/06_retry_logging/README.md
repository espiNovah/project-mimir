# 06 · Retry logging

**Lesson:** [Debugging and Logging](https://espinovah.github.io/project-mimir/#/lessons/foundations/debugging-and-logging)

## The bug report

`call_with_retries(func, attempts=3)` calls `func()` until it succeeds, retrying when it raises `TimeoutError`, up to `attempts` tries. It logs what happens with the `"retry"` logger. The function works, but the logs are useless when something goes wrong at 3 a.m. The team agreed on this logging contract:

| Event | Level | Message |
| --- | --- | --- |
| a try times out | `WARNING` | `timeout on attempt N of M` |
| a try succeeds | `INFO` | `succeeded on attempt N` |
| every try timed out | `ERROR` | `gave up after M attempts` |

Attempts are counted from 1, as a person would count them. The function returns `func`'s result, or `None` if it gave up. Other exceptions are not retried: they go straight to the caller.

Run the program at `DEBUG` level to see every message it logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
```

The tests use pytest's built-in [`caplog` fixture](https://docs.pytest.org/en/stable/how-to/logging.html), which records every log message so a test can check its level and text.

## How to work on it

1. Run the tests and read the failures. Which input breaks, and what came out instead?
1. Set a breakpoint (or add `breakpoint()`) and watch the variables until you see where the program stops doing what you expect.
1. Write one sentence at the top of the file saying what the bug was, then fix it.

## Run the tests

```bash
cd exercises
uv run pytest debugging/06_retry_logging
```

Stuck? Make the tests pass first, then compare with `solution/retry_logging.py`.
