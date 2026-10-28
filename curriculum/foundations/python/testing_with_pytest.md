### Introduction

How do you know your code works? So far, you've run it, typed a few inputs and eyeballed the output. That's fine once. But every time you change something, you'd have to repeat every check by hand, and you won't. Bugs creep back in silently.

An **automated test** is a small piece of code that runs your code with known inputs and checks the result. Once written, a test runs in milliseconds, forever. A good set of tests lets you change code fearlessly: if all the tests still pass, you didn't break what they cover.

In AI engineering, this idea grows into one of the most important skills you'll learn: **evals** (evaluations). An eval is a test for a system whose output isn't exactly predictable, like a model's answer. You'll build eval harnesses in the Evals section, and they're built on the same habits you start here: define inputs, define what "correct" means, run everything automatically, look at the score.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What automated tests are, the `assert` statement, and writing your first pytest file.
- Reading pytest's output when a test fails, and testing that code raises the right exception.
- Running one test against many cases with `parametrize`.
- Testing code that uses files with `tmp_path`.
- Testing what a program prints, and its exit code, with `capsys`.
- Fakes and dependency injection: swapping a slow or unreliable part for a stand-in.
- Patching attributes and environment variables with `monkeypatch`.

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

### Testing what a program prints

Pure functions are the easiest code to test, but a real program also has a command layer that parses arguments, prints results and picks an exit code. In the Command-Line Apps lesson you gave your countdown tool a `main(argv=None)` that returns an exit code instead of calling `sys.exit` itself. That shape pays off now. A test can call `main` with a list of strings, check the number it returns, and check what it printed.

To see the printed text, use pytest's built-in `capsys` fixture. While a test that asks for `capsys` runs, pytest **captures** (secretly collects) everything written to standard output and standard error. Calling `capsys.readouterr()` hands you what was collected so far, as an object with two strings: `.out` for stdout and `.err` for stderr.

```python
# test_countdown.py, next to countdown.py from the Command-Line Apps lesson
import pytest

from countdown import main


def test_prints_days_left(capsys):
    assert main(["2027-01-01", "--since", "2026-12-25"]) == 0  # exit code
    captured = capsys.readouterr()       # everything printed so far
    assert captured.out == "7 days until 2027-01-01\n"
    assert captured.err == ""


def test_past_date_is_an_error(capsys):
    assert main(["2020-01-01", "--since", "2026-12-25"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""            # nothing on stdout...
    assert "is in the past" in captured.err  # ...the message went to stderr


def test_bad_date_is_a_usage_error(capsys):
    with pytest.raises(SystemExit) as exc_info:  # argparse calls sys.exit(2)
        main(["not-a-date"])
    assert exc_info.value.code == 2
    assert "invalid fromisoformat value" in capsys.readouterr().err
```

Three things to notice. First, the tests pass `--since` so the answer never depends on today's date; a test that passes today and fails tomorrow is a bad test. Second, `print` adds a newline, so an exact comparison needs the `\n` (or use `.strip()`). Third, argparse handles usage errors by calling `sys.exit(2)` itself. `sys.exit` works by raising the `SystemExit` exception, so you test it with `pytest.raises` like any other exception, and `exc_info.value.code` holds the exit code.

Use exact comparisons for short, stable output and `in` for long messages whose wording might change. Either way, keep most of your tests on the pure functions underneath, and use `capsys` for a handful of tests that prove the command layer is wired up correctly.

### Fakes and dependency injection

Some code depends on things a test can't control: a web service, a language model, the current time, a random number. Calling the real thing in a test makes the test slow, flaky (passing or failing at random), sometimes expensive, and impossible to run without Wi-Fi. You also can't easily make a real service fail on demand, yet failure paths are exactly what you most need to test.

The fix is to replace the real thing with a **fake**: a small stand-in, written for tests, that behaves like the real thing in the ways your code cares about and returns canned answers. The cleanest way to get a fake into your code is **dependency injection**. The name is grand, but the idea is simple: instead of a function creating or finding the thing it depends on (its **dependency**), the caller passes it in as an argument. You already did this with file paths in the previous section. The real program passes the real path, and the test passes a temporary one.

Here's a weather tool. `describe` doesn't create a `WeatherService`; it's handed one:

```python
# weather.py
import argparse
import os
import sys


class WeatherError(Exception):
    """The weather service couldn't give us an answer."""


class WeatherService:
    """Talks to a real weather API over the network."""

    def temperature(self, city: str) -> float:
        # You'll write the real network request in Working with APIs.
        raise WeatherError("network calls aren't written yet")


def describe(city: str, service: WeatherService) -> str:
    """Turn a temperature into a sentence. The service is passed in."""
    try:
        celsius = service.temperature(city)
    except WeatherError:
        return f"Sorry, no weather for {city} right now."
    feel = "cold" if celsius < 10 else "mild" if celsius < 22 else "warm"
    return f"{city}: {celsius:.0f}°C, {feel}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="weather")
    parser.add_argument("city")
    args = parser.parse_args(argv)
    if not os.environ.get("WEATHER_API_KEY"):
        print("error: set WEATHER_API_KEY first", file=sys.stderr)
        return 1
    print(describe(args.city, WeatherService()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

The test file defines a fake. It subclasses `WeatherService`, so it fits the type hint, and overrides `temperature` to look up a dictionary instead of using the network. It also records every call, so a test can check that the code asked the right question:

```python
# test_weather.py
import weather
from weather import WeatherError, WeatherService, describe


class FakeWeather(WeatherService):
    """A stand-in for WeatherService: canned answers, no network."""

    def __init__(self, temperatures: dict[str, float]):
        self.temperatures = temperatures
        self.calls: list[str] = []       # remember what we were asked

    def temperature(self, city: str) -> float:
        self.calls.append(city)
        if city not in self.temperatures:
            raise WeatherError(f"unknown city: {city}")
        return self.temperatures[city]


def test_describe_cold_city():
    fake = FakeWeather({"Oslo": 3.6})
    assert describe("Oslo", fake) == "Oslo: 4°C, cold"
    assert fake.calls == ["Oslo"]        # asked once, for the right city


def test_describe_handles_service_errors():
    message = describe("Atlantis", FakeWeather({}))
    assert message == "Sorry, no weather for Atlantis right now."
```

The second test is the important one. Making a real weather service fail on cue is nearly impossible, but making a fake fail takes one line. The same trick covers time and randomness: a function that takes `today: date` as a parameter, or a random-number generator, is trivial to test, while one that calls `date.today()` inside itself gives a different answer every day.

You'll use this pattern constantly. In the projects ahead you'll pass a fake HTTP client into your fetch functions, and later a fake model client into an LLM app, so your tests run offline, for free, in milliseconds.

### Patching with monkeypatch

Dependency injection needs the code to be written with a parameter you can pass a fake through. Sometimes it isn't: `main` above creates `WeatherService()` itself and reads an environment variable. For those cases pytest has the `monkeypatch` fixture, which temporarily replaces things for the length of one test:

- `monkeypatch.setattr(module, "name", new_value)` replaces an attribute, such as a function or class inside a module.
- `monkeypatch.setenv("NAME", "value")` and `monkeypatch.delenv("NAME", raising=False)` set or remove an environment variable. `raising=False` means "don't complain if it wasn't set".

When the test ends, pass or fail, monkeypatch puts everything back the way it was, so one test's changes can't leak into the next. Add these tests to `test_weather.py`:

```python
def test_main_prints_the_description(monkeypatch, capsys):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")    # a fake key
    monkeypatch.setattr(weather, "WeatherService", lambda: FakeWeather({"Oslo": 3.6}))

    assert weather.main(["Oslo"]) == 0
    assert capsys.readouterr().out == "Oslo: 4°C, cold\n"


def test_main_needs_an_api_key(monkeypatch, capsys):
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)  # make sure it's unset

    assert weather.main(["Oslo"]) == 1
    assert "WEATHER_API_KEY" in capsys.readouterr().err
```

The first test swaps the name `WeatherService` inside the `weather` module for a `lambda` that builds a fake, so when `main` calls `WeatherService()` it gets a `FakeWeather` instead. That's why the test imports the module with `import weather` and patches `weather`: **patch the name where your code looks it up**. Python finds `WeatherService` in the `weather` module each time `main` runs, so that's the name to replace. Patching it somewhere else has no effect on `main`.

Patching is powerful, but it couples your test to the inside of your code: rename a function and the patch silently stops matching. So prefer dependency injection for your own logic, and keep `monkeypatch` for the edges, such as environment variables, the command layer, or code you can't change. If you find yourself patching five things to test one function, that function is doing too much.

### Organizing tests

For small projects, test files can sit next to the code. As a project grows, move them into a `tests/` folder. If you do, pytest won't automatically find your modules in the project root, so add this to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

What should you test? Start with your pure functions: parsing, validation, calculations, formatting. Test the normal case, the edge cases (empty input, zero, one item) and the error cases. Code that's hard to test is often a sign that a function is doing too much, such as mixing calculation with `input()` and `print()`. Splitting it up makes it both testable and better. Then add a few `capsys` tests for the command layer, and use fakes for anything slow or outside your control.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 5: Unit Tests](https://cs50.harvard.edu/python/weeks/5/). It starts with `assert`, shows why hand-written checks get unwieldy, and then moves to pytest, including testing for exceptions and organizing tests in a folder.
1. Work through [pytest's "Get Started" page](https://docs.pytest.org/en/stable/getting-started.html). Use `uv add --dev pytest` instead of the `pip install` it shows, and `uv run pytest` to run it.
   - You can skip the section on grouping tests in a class. The section on `pytest.approx` is worth reading, since it solves the floating-point comparison problem from the Variables and Types lesson.
1. Read these short pytest how-to guides: [writing assertions](https://docs.pytest.org/en/stable/how-to/assert.html) (the first two sections, on `assert` and `pytest.raises`), [parametrizing tests](https://docs.pytest.org/en/stable/how-to/parametrize.html) (the first section only) and [temporary directories](https://docs.pytest.org/en/stable/how-to/tmp_path.html) (the `tmp_path` section only).
1. Read two more how-to guides that back up the last three sections: [capturing output](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html) (the "Accessing captured output from a test function" section) and [monkeypatching](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) (the opening summary, "Monkeypatching functions", "Monkeypatching returned objects: building mock classes" and "Monkeypatching environment variables"; skip the rest). Its examples patch `requests`, a web library you haven't met yet. Read it as "some library that makes network calls".
1. Practice:
   - Do all four problems in [CS50P Problem Set 5](https://cs50.harvard.edu/python/psets/5/): Testing my twttr, Back to the Bank, Re-requesting a Vanity Plate and Refueling. Each asks you to restructure an earlier program so it can be tested, which is exactly the skill to build.
   - Add tests to your `mimir-quiz-game` repo: at least one for answer checking (parametrized), one for scoring, and one for loading questions from a temporary JSON file with `tmp_path`, including a test that a broken file raises your custom exception. Make sure `uv run pytest` passes and commit.
   - Write the `capsys` tests from this lesson for your own countdown tool from Command-Line Apps, including the usage-error test. Then open the test files in the [cli-apps exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/cli-apps), which test every exercise this same way, and read them to see more examples.
   - Copy `weather.py` and its tests from this lesson, run them, then break `describe` on purpose (for example, swap "cold" and "warm") and watch the fake-based tests catch it. Add one more test: a `FakeWeather` whose `temperature` returns exactly `10.0`, checking which word you get at the boundary.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How do you test that a function raises the right exception?](#your-first-tests)
- [Why should you deliberately break your code after writing a new test?](#when-a-test-fails)
- [What does `parametrize` do, and how does it relate to an eval dataset?](#many-cases-one-test)
- [Why is it better to pass a file path into a function than to hard-code it, and how does `tmp_path` help?](#testing-code-that-uses-files)
- [How can a test check what `main` printed to stdout and stderr, and how do you test an argparse usage error?](#testing-what-a-program-prints)
- [What is a fake, and how does dependency injection let a test use one?](#fakes-and-dependency-injection)
- [What can `monkeypatch` replace, why should you patch a name where your code looks it up, and when should you prefer dependency injection instead?](#patching-with-monkeypatch)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The pytest fixtures guide](https://docs.pytest.org/en/stable/how-to/fixtures.html) explains how to write your own fixtures for setup code shared by many tests.
- Every exercise on the [Exercism Python track](https://exercism.org/tracks/python) comes with a pytest test file. Reading those files is a good way to see how experienced developers structure tests.
