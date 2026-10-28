# Python basics

Small, focused functions that practice the first four Python lessons: values and types, `if` and loops, functions, and the four built-in collections. Each exercise is a file with an empty function and a test file that checks it. Your job is to make the tests pass.

Do these alongside the lessons in [Python Fundamentals](https://espinovah.github.io/project-mimir/#/paths/foundations). Each exercise's README says which lesson it belongs to.

## How to run

You need [uv](https://docs.astral.sh/uv/). From the repo root:

```bash
cd exercises
uv run pytest python-basics/01_temperature_converter   # one exercise
uv run pytest python-basics                            # the whole set
```

The first run installs pytest and the other exercise dependencies from `exercises/pyproject.toml`.

## Exercises

| # | Exercise | Lesson | Practices |
| --- | --- | --- | --- |
| 01 | [Temperature converter](01_temperature_converter/) | Variables and Types | arithmetic, `round`, `return` |
| 02 | [Receipt line](02_receipt_line/) | Variables and Types | f-strings, number formatting |
| 03 | [FizzBuzz](03_fizzbuzz/) | Conditionals and Loops | `for`, `range`, `%`, `if`/`elif` order |
| 04 | [Letter grade](04_letter_grade/) | Conditionals and Loops | chained conditions, boundaries |
| 05 | [Count vowels](05_count_vowels/) | Conditionals and Loops | looping over a string, `in` |
| 06 | [Word counts](06_word_counts/) | Lists, Dicts, Sets and Tuples | building a dict, `dict.get` |
| 07 | [Common tags](07_common_tags/) | Lists, Dicts, Sets and Tuples | sets, intersection and union |
| 08 | [Token budget](08_token_budget/) | Functions | default arguments, calling your own functions |
