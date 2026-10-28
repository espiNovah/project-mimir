# Pythonic Python

Exercises for the [Pythonic Python](https://espinovah.github.io/project-mimir/#/lessons/foundations/pythonic-python) lesson: comprehensions, generators, `lambda` and `sorted(key=...)`, `*args` and `**kwargs`, and context managers. The examples come from the kind of code you'll write later in LLM apps, like batching API calls and chunking documents.

## How to run

From the repo root:

```bash
cd exercises
uv run pytest pythonic-python/01_comprehension_drills   # one exercise
uv run pytest pythonic-python                           # the whole set
```

## Exercises

| # | Exercise | Practices |
| --- | --- | --- |
| 01 | [Comprehension drills](01_comprehension_drills/) | list, dict and set comprehensions |
| 02 | [Batched items](02_batched_items/) | generators, `yield`, lazy evaluation |
| 03 | [Sort records](03_sort_records/) | `sorted(key=...)`, `lambda`, tuple keys |
| 04 | [Prompt builder](04_prompt_builder/) | `*args`, `**kwargs`, unpacking |
| 05 | [Timed block](05_timed_block/) | `@contextmanager`, `try`/`finally` |
| 06 | [Sliding windows](06_sliding_windows/) | generators with `range` steps and slicing |
