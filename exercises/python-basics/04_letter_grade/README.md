# 04 · Letter grade

**Lesson:** [Conditionals and Loops](https://espinovah.github.io/project-mimir/#/lessons/foundations/conditionals-and-loops)

## Task

Write `letter_grade(score)`. It turns a score from 0 to 100 into a letter:

| Score | Grade |
| --- | --- |
| 90 and up | `"A"` |
| 80 to under 90 | `"B"` |
| 70 to under 80 | `"C"` |
| 60 to under 70 | `"D"` |
| under 60 | `"F"` |

Scores below 0 or above 100 return `"Invalid score"`.

```python
letter_grade(85)    # "B"
letter_grade(101)   # "Invalid score"
```

## Hints

- Check the invalid cases first, then go from the highest grade down.
- Once one branch returns, the rest of the function doesn't run, so you don't need `and` in every condition.
- Test the edges yourself: what does `89.9` give? What about `90`?

## Run the tests

```bash
cd exercises
uv run pytest python-basics/04_letter_grade
```

Stuck? Make the tests pass first, then compare with `solution/letter_grade.py`.
