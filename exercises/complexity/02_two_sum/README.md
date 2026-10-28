# 02 · Two sum: fit the budget

**Lesson:** [Complexity and Core Data Structures](https://espinovah.github.io/project-mimir/#/lessons/foundations/complexity-and-core-data-structures)

## Task

You have a list of document lengths in tokens and want two documents that **exactly** fill a context budget. This is the classic interview question "two sum". Write `two_sum(nums, target)`, which returns a tuple `(i, j)` of indices with `i < j` and `nums[i] + nums[j] == target`, or `None` if there's no such pair.

If several pairs work, return the one with the **smallest `j`**, and for that `j` the smallest `i`. That's the pair you find first if you walk the list once from the left.

```python
two_sum([300, 700, 450, 550], 1000)   # (0, 1)
two_sum([450, 300, 550, 700], 1000)   # (0, 2)
two_sum([500, 500], 1000)             # (0, 1)
two_sum([100, 200], 1000)             # None
```

The starter checks every pair: correct, but O(n²). Make it O(n), as the lesson's interview walkthrough describes.

## How the speed is tested

The tests pass in a list that **counts every element it hands out**, whether by indexing (`nums[i]`), by looping over it, or by an `in` check. On 2,000 numbers the starter reads about four million elements. The tests allow `3 * n`.

## Hints

- For each number `x` at index `j`, the partner you need is `target - x`. Have you seen it already?
- A dict from value to the index where you first saw it answers that in O(1).
- Check for the partner *before* you store the current number, so `[500]` with target 1000 doesn't pair 500 with itself.
- `for j, x in enumerate(nums)` reads each element once.

## Run the tests

```bash
cd exercises
uv run pytest complexity/02_two_sum
```

Before you change any code, write a comment at the top of the file with the Big-O of the starter and of the version you plan to write. Stuck? Make the tests pass first, then compare with `solution/two_sum.py`.
