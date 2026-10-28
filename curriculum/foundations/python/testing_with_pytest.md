### Introduction

How do you know your code works? So far, you've run it, typed a few inputs and eyeballed the output. That's fine once. But every time you change something, you'd have to repeat every check by hand, and you won't. Bugs creep back in silently.

An **automated test** is a small piece of code that runs your code with known inputs and checks the result. Once written, a test runs in milliseconds, forever. A good set of tests lets you change code fearlessly: if all the tests still pass, you didn't break what they cover.

In AI engineering, this idea grows into one of the most important skills you'll learn: **evals** (evaluations). An eval is a test for a system whose output isn't exactly predictable, like a model's answer. You'll build eval harnesses in the Evals section, and they're built on the same habits you start here: define inputs, define what "correct" means, run everything automatically, look at the score.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What automated tests are and why they're worth writing.
- The `assert` statement.
- Installing pytest and writing your first test file.
- Reading pytest's output when a test fails.
- Testing that code raises the right exception.
- Running one test against many cases with `parametrize`.
- Testing code that uses files with `tmp_path`.

### Assert

Python's `assert` statement checks that something is true. If it is, nothing happens. If it isn't, Python raises `AssertionError`:

```python
assert 2 + 2 == 4        # passes silently
assert "ai" in "agents"  # AssertionError
```

A test is, at its simplest, a function that calls your code and asserts something about the result.

### Your first tests

Suppose your quiz has a module, `grading.py`, with the logic for checking answers. Note that these are pure functions: they take inputs and return outputs without printing or asking for input. That's what makes them easy to test.

```python
# grading.py
def normalize(answer: str) -> str:
    """Lowercase an answer and strip surrounding whitespace."""
    return answer.strip().lower()


def is_correct(given: str, expected: str) -> bool:
    return normalize(given) == normalize(expected)


def percentage(correct: int, total: int) -> float:
    if total <= 0:
        raise ValueError("total must be positive")
    return round(correct / total * 100, 1)
```

Install **pytest**, the most popular Python testing tool, as a development dependency:

```bash
uv add --dev pytest
```

Then create `test_grading.py` next to `grading.py`:

```python
# test_grading.py
import pytest

from grading import is_correct, normalize, percentage


def test_normalize_strips_and_lowercases():
    assert normalize("  Dict ") == "dict"


def test_is_correct_ignores_case():
    assert is_correct("PARIS", "Paris")


def test_is_correct_rejects_wrong_answer():
    assert not is_correct("London", "Paris")


def test_percentage():
    assert percentage(7, 10) == 70.0


def test_percentage_rejects_zero_total():
    with pytest.raises(ValueError):
        percentage(1, 0)
```

Run them:

```bash
uv run pytest
```

pytest finds every file named `test_*.py`, runs every function in it whose name starts with `test_`, and prints a dot for each one that passes:

```text
collected 5 items

test_grading.py .....                                                    [100%]

============================== 5 passed in 0.03s ===============================
```

The last test shows how to test errors. `with pytest.raises(ValueError):` passes only if the code inside raises `ValueError`. Testing that bad input fails loudly is just as important as testing that good input works.

### When a test fails

Now introduce a bug: change `percentage` to return `round(correct / total, 1)`, forgetting the `* 100`. Run pytest again:

```text
test_grading.py ...F.                                                    [100%]

=================================== FAILURES ===================================
_______________________________ test_percentage ________________________________

    def test_percentage():
>       assert percentage(7, 10) == 70.0
E       assert 0.7 == 70.0
E        +  where 0.7 = percentage(7, 10)

test_grading.py:19: AssertionError
=========================== short test summary info ============================
FAILED test_grading.py::test_percentage - assert 0.7 == 70.0
========================= 1 failed, 4 passed in 0.03s ==========================
```

The `F` marks the failure, and pytest shows exactly which assertion failed, what the actual value was (`0.7`) and where it came from. You didn't need to write any error messages yourself; pytest inspects the plain `assert` for you.

Good test names help here. `test_percentage_rejects_zero_total` tells you what broke before you even read the code.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Make sure a test can fail

A test that never fails is worse than no test, because it gives you false confidence. When you write a new test, break the code on purpose (or flip the expected value) and check that the test goes red. Then fix it and watch it go green.

</div>

### Many cases, one test

Answer checking has lots of cases worth trying. Instead of copying a test five times, use `parametrize`, which runs the same test once for each set of values:

```python
import pytest

from grading import is_correct


@pytest.mark.parametrize(
    "given, expected, result",
    [
        ("dict", "dict", True),
        (" Dict ", "dict", True),
        ("DICT", "dict", True),
        ("list", "dict", False),
        ("", "dict", False),
    ],
)
def test_is_correct(given, expected, result):
    assert is_correct(given, expected) == result
```

pytest reports each case as its own test, so you see exactly which one failed. Notice the shape: a table of inputs and expected outputs, run through the same check. Keep that picture in mind. An eval dataset for a language model is that same table, just with prompts as inputs and a fuzzier definition of "correct".

### Testing code that uses files

Tests shouldn't touch your real data files. pytest provides **fixtures**, ready-made helpers you request by naming them as a test's parameter. The `tmp_path` fixture gives each test a fresh, empty temporary folder as a `Path`:

```python
import json


def save_scores(path, scores):
    path.write_text(json.dumps(scores), encoding="utf-8")


def test_save_scores_writes_json(tmp_path):
    path = tmp_path / "scores.json"
    save_scores(path, {"ada": 7})
    assert json.loads(path.read_text(encoding="utf-8")) == {"ada": 7}
```

The temporary folder is cleaned up for you. This is why it pays to write functions that take a path as a parameter instead of hard-coding `"scores.json"` inside them: the test can pass in a temporary path, and the real program passes in the real one.

### Organizing tests

For small projects, test files can sit next to the code. As a project grows, move them into a `tests/` folder. If you do, pytest won't automatically find your modules in the project root, so add this to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

What should you test? Start with your pure functions: parsing, validation, calculations, formatting. Test the normal case, the edge cases (empty input, zero, one item) and the error cases. Code that's hard to test is often a sign that a function is doing too much, such as mixing calculation with `input()` and `print()`. Splitting it up makes it both testable and better.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 5: Unit Tests](https://cs50.harvard.edu/python/weeks/5/). It starts with `assert`, shows why hand-written checks get unwieldy, and then moves to pytest, including testing for exceptions and organizing tests in a folder.
1. Work through [pytest's "Get Started" page](https://docs.pytest.org/en/stable/getting-started.html). Use `uv add --dev pytest` instead of the `pip install` it shows, and `uv run pytest` to run it.
   - You can skip the section on grouping tests in a class. The section on `pytest.approx` is worth reading, since it solves the floating-point comparison problem from the Variables and Types lesson.
1. Read these short pytest how-to guides: [writing assertions](https://docs.pytest.org/en/stable/how-to/assert.html) (the first two sections, on `assert` and `pytest.raises`), [parametrizing tests](https://docs.pytest.org/en/stable/how-to/parametrize.html) (the first section only) and [temporary directories](https://docs.pytest.org/en/stable/how-to/tmp_path.html) (the `tmp_path` section only).
1. Practice:
   - Do all four problems in [CS50P Problem Set 5](https://cs50.harvard.edu/python/psets/5/): Testing my twttr, Back to the Bank, Re-requesting a Vanity Plate and Refueling. Each asks you to restructure an earlier program so it can be tested, which is exactly the skill to build.
   - Add tests to your `mimir-quiz-game` repo: at least one for answer checking (parametrized), one for scoring, and one for loading questions from a temporary JSON file with `tmp_path`, including a test that a broken file raises your custom exception. Make sure `uv run pytest` passes and commit.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The pytest fixtures guide](https://docs.pytest.org/en/stable/how-to/fixtures.html) explains how to write your own fixtures for setup code shared by many tests.
- Every exercise on the [Exercism Python track](https://exercism.org/tracks/python) comes with a pytest test file. Reading those files is a good way to see how experienced developers structure tests.
