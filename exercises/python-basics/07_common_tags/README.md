# 07 · Common tags

**Lesson:** [Lists, Dicts, Sets and Tuples](https://espinovah.github.io/project-mimir/#/lessons/foundations/data-structures)

## Task

Two blog posts have lists of tags. Write two functions:

- `common_tags(tags_a, tags_b)` returns the tags in **both** lists.
- `all_tags(tags_a, tags_b)` returns the tags in **either** list.

Both lower-case every tag, drop repeats, and return a list sorted A to Z.

```python
common_tags(["Python", "ai", "web"], ["AI", "python"])  # ["ai", "python"]
all_tags(["web", "AI"], ["ai", "data"])                 # ["ai", "data", "web"]
```

## Hints

- A set holds each value once, so it removes repeats for free.
- Sets have operators for "in both" (`&`) and "in either" (`|`).
- `sorted(some_set)` gives back a sorted list.

## Run the tests

```bash
cd exercises
uv run pytest python-basics/07_common_tags
```

Stuck? Make the tests pass first, then compare with `solution/common_tags.py`.
