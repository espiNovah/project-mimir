# 01 · Duplicate prompts

**Lesson:** [Complexity and Core Data Structures](https://espinovah.github.io/project-mimir/#/lessons/foundations/complexity-and-core-data-structures)

## Task

Before you pay to run a dataset of prompts through a model, you check it for duplicates. The starter file has two functions that give the right answers but compare every pair of items, which is O(n²):

- `has_duplicates(items)` returns `True` if any item appears more than once.
- `first_duplicate(items)` returns the first item whose **second** occurrence comes earliest in the list, or `None`.

```python
first_duplicate(["a", "b", "c", "b", "a"])   # 'b'  (its repeat, at index 3, comes before a's, at index 4)
```

Rewrite both to run in O(n) by remembering what you've seen.

## How the speed is tested

The tests don't use a stopwatch, so they can't be flaky. They pass in items that **count how many times they're compared with `==`**. The pairwise version on 2,000 items makes about two million comparisons; a version built on a set makes almost none, because a set finds an item by its hash instead of comparing it with everything. The tests allow at most `2 * n` comparisons.

## Hints

- `item in some_set` is O(1) on average; `item in some_list` is O(n).
- Walk the list once. For each item, check whether you've seen it before, then add it.
- The first time that check is true, you've found the first duplicate.

## Run the tests

```bash
cd exercises
uv run pytest complexity/01_has_duplicates
```

Before you change any code, write a comment at the top of the file with the Big-O of the starter and of the version you plan to write. Stuck? Make the tests pass first, then compare with `solution/has_duplicates.py`.
