# 03 · FizzBuzz

**Lesson:** [Conditionals and Loops](https://espinovah.github.io/project-mimir/#/lessons/foundations/conditionals-and-loops)

## Task

Write `fizzbuzz(n)`. It returns a list of strings for the numbers 1 to `n`:

- multiples of 3 become `"Fizz"`;
- multiples of 5 become `"Buzz"`;
- multiples of both become `"FizzBuzz"`;
- every other number becomes its digits as a string.

```python
fizzbuzz(5)   # ["1", "2", "Fizz", "4", "Buzz"]
```

## Hints

- `range(1, n + 1)` counts from 1 up to and including `n`.
- `i % 3 == 0` is true when `i` divides evenly by 3.
- The order of your `if`/`elif` checks matters. Which case must you check first?

## Run the tests

```bash
cd exercises
uv run pytest python-basics/03_fizzbuzz
```

Stuck? Make the tests pass first, then compare with `solution/fizzbuzz.py`.
