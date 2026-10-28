# Complexity

Exercises for the [Complexity and Core Data Structures](https://espinovah.github.io/project-mimir/#/lessons/foundations/complexity-and-core-data-structures) lesson. Every starter file already gives the right answers, just slowly. Your job is to find the repeated work and swap in the data structure that removes it: a set, a dict, a deque or binary search.

Before you change any code, write a comment at the top of the file stating the Big-O of the starter and of your version.

## How speed is tested

Timing tests are easy to get wrong: a busy laptop or a slow CI machine can make good code look slow. So most of these tests count **operations** instead of seconds. They pass in values that count how often they're compared, or lists that count how many elements they hand out, and check the count is in the right range for your Big-O. Two exercises (03 and 04) use a stopwatch, with limits about ten times looser than a correct solution needs.

## How to run

From the repo root:

```bash
cd exercises
uv run pytest complexity/01_has_duplicates   # one exercise
uv run pytest complexity                     # the whole set
```

The starters are slow on purpose, so a failing run takes a few seconds.

## Exercises

| # | Exercise | From | To | How it's tested |
| --- | --- | --- | --- | --- |
| 01 | [Duplicate prompts](01_has_duplicates/) | nested loops, O(n²) | set, O(n) | counts `==` comparisons |
| 02 | [Two sum: fit the budget](02_two_sum/) | every pair, O(n²) | dict, O(n) | counts list reads |
| 03 | [Deduplicate documents](03_dedupe_documents/) | `in` on a list, O(n²) | set, O(n) | timed, 0.5 s limit |
| 04 | [Crawl a docs site with a queue](04_crawl_queue/) | `list.pop(0)`, O(n²) | `deque`, O(n) | timed, 0.5 s limit |
| 05 | [Score ranges with binary search](05_score_ranges/) | scan, O(n) | `bisect`, O(log n) | counts list reads |
