# 02 · Receipt line

**Lesson:** [Functions](https://espinovah.github.io/project-mimir/#/lessons/foundations/functions)

## Task

Write `receipt_line(item, quantity, unit_price)`. It returns one line of a shop receipt as a string:

```python
receipt_line("apple", 3, 0.5)    # "3 x apple @ $0.50 = $1.50"
receipt_line("coffee", 2, 3)     # "2 x coffee @ $3.00 = $6.00"
```

Prices always show exactly two decimal places.

## Hints

- An f-string can format a number: `f"{price:.2f}"` gives `"0.50"` for `0.5`.
- Work out the total first and store it in a variable, then build the string.
- A literal `$` inside an f-string is just a normal character.

## Run the tests

```bash
cd exercises
uv run pytest python-basics/02_receipt_line
```

Stuck? Make the tests pass first, then compare with `solution/receipt_line.py`.
