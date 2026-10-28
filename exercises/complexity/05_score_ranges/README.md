# 05 · Score ranges with binary search

**Lesson:** [Complexity and Core Data Structures](https://espinovah.github.io/project-mimir/#/lessons/foundations/complexity-and-core-data-structures)

## Task

You've scored 100,000 model outputs and sorted the scores. Now a dashboard asks many questions of the same sorted list:

- `count_in_range(scores, lo, hi)` returns how many scores `s` satisfy `lo <= s <= hi`.
- `percentile_rank(scores, value)` returns the fraction of scores **strictly below** `value`, between 0 and 1 (and `0.0` for an empty list).

```python
scores = [0.1, 0.2, 0.2, 0.5, 0.9]
count_in_range(scores, 0.2, 0.5)   # 3
percentile_rank(scores, 0.5)       # 0.6
```

The starter loops over every score for every question: O(n). Because the list is sorted, each question can be answered in O(log n).

## How the speed is tested

The tests pass in a sorted list of 100,000 scores that **counts every element it hands out**. A loop reads all 100,000; binary search reads about 17 per search. The tests allow 100 reads per call.

## Hints

- `bisect_left(scores, x)` is the number of scores **less than** `x`.
- `bisect_right(scores, x)` is the number of scores **less than or equal to** `x`.
- So the count in a range is the difference of two of them.

## Run the tests

```bash
cd exercises
uv run pytest complexity/05_score_ranges
```

Before you change any code, write a comment at the top of the file with the Big-O of the starter and of the version you plan to write. Stuck? Make the tests pass first, then compare with `solution/score_ranges.py`.
