# 01 · Average reply lengths

**Lesson:** [Debugging and Logging](https://espinovah.github.io/project-mimir/#/lessons/foundations/debugging-and-logging)

## The bug report

`average_lengths(replies)` should return the average reply length, in characters, for each model. The model names in the data are messy: some have capital letters or stray spaces, but `"Capable"`, `" capable"` and `"capable"` are all the same model. The function runs without an error, but reports too many models, and the averages are wrong.

```python
average_lengths([
    {"model": "cheap", "text": "Paris."},
    {"model": "Capable ", "text": "Paris, of course."},
    {"model": "capable", "text": "The capital is Paris."},
])
# expected: {"cheap": 6.0, "capable": 19.0}
```

Keys in the result should be the clean, lowercase names.

## How to work on it

1. Run the tests and read the failures. Which input breaks, and what came out instead?
1. Set a breakpoint (or add `breakpoint()`) and watch the variables until you see where the program stops doing what you expect.
1. Write one sentence at the top of the file saying what the bug was, then fix it.

## Run the tests

```bash
cd exercises
uv run pytest debugging/01_average_lengths
```

Stuck? Make the tests pass first, then compare with `solution/average_lengths.py`.
