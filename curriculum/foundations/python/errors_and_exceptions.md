### Introduction

Things go wrong. Users type `twelve` when you asked for a number. Files go missing. Networks drop. And when you work with AI models, things go wrong in new ways: an API call times out, you hit a rate limit, or the model replies with text that was supposed to be JSON but isn't quite.

Python reports problems by raising **exceptions**. In this lesson you'll learn to read the error report Python prints, to *handle* exceptions you expect so your program recovers gracefully, and, just as important, to let unexpected ones crash loudly so you notice them. Reliable AI systems are mostly careful error handling around an unreliable core.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Reading a traceback from the bottom up.
- Common built-in exceptions and what they mean.
- Handling errors with `try`, `except`, `else` and `finally`.
- Catching specific exceptions instead of everything.
- Raising your own exceptions and defining custom ones.
- When to recover, when to retry and when to fail loudly.

### Reading a traceback

Save this as `broken.py` and run it with `uv run broken.py`:

```python
def average(numbers):
    return sum(numbers) / len(numbers)


def report(scores):
    print(f"Average: {average(scores)}")


report([])
```

Python prints a **traceback**, a report of what was running when the error happened. (The exact `~` and `^` markers that point at the failing expression vary a little between Python versions.)

```text
Traceback (most recent call last):
  File "/home/ada/python-practice/broken.py", line 9, in <module>
    report([])
    ~~~~~~^^^^
  File "/home/ada/python-practice/broken.py", line 6, in report
    print(f"Average: {average(scores)}")
                      ~~~~~~~^^^^^^^^
  File "/home/ada/python-practice/broken.py", line 2, in average
    return sum(numbers) / len(numbers)
           ~~~~~~~~~~~~~^~~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

Read it **from the bottom up**. The last line names the exception type (`ZeroDivisionError`) and gives a message. The lines above it show the chain of calls that led there, with the most recent call last: line 9 called `report`, which called `average`, which divided by zero on line 2. The bug is often not on the bottom line itself but in whatever passed it bad data, here an empty list.

When you ask for help, or paste an error into an AI assistant, always include the full traceback, not just the last line.

### Common exceptions

You'll meet these constantly:

- `NameError`: you used a name that doesn't exist, usually a typo.
- `TypeError`: you used a value of the wrong type, such as `"3" + 4`.
- `ValueError`: the type is right but the value isn't, such as `int("twelve")`.
- `KeyError`: a dict doesn't have that key.
- `IndexError`: a list doesn't have that position.
- `AttributeError`: an object doesn't have that method or attribute, such as `None.strip()`.
- `FileNotFoundError`: the path doesn't point to a file.
- `json.JSONDecodeError`: the text isn't valid JSON.

### Handling exceptions

Wrap code that might fail in a `try` block, and say what to do in an `except` block:

```python
def ask_int(prompt):
    while True:
        text = input(prompt)
        try:
            return int(text)
        except ValueError:
            print(f"{text!r} isn't a whole number. Try again.")


age = ask_int("How old are you? ")
```

If `int(text)` raises `ValueError`, Python jumps straight to the `except` block, prints the message, and the loop asks again. If it succeeds, `return` hands back the number. (`{text!r}` shows the value with quotes around it, which makes empty input visible.)

The full form has two optional extra blocks. `else` runs only if nothing went wrong, and `finally` runs no matter what, which is useful for cleanup:

```python
import json


def load_config(path):
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"No config at {path}; using defaults.")
        return {}
    except json.JSONDecodeError as e:
        print(f"{path} is not valid JSON: {e}")
        return {}
    else:
        print(f"Loaded {len(config)} settings.")
        return config
    finally:
        print("Done reading config.")
```

`except json.JSONDecodeError as e` stores the exception in `e` so you can show its message, which for JSON errors includes the line and column of the problem.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Don't catch everything

It's tempting to write `except:` or `except Exception:` and print "something went wrong". Don't. A blanket `except` hides typos and real bugs along with the problem you meant to handle, and you'll lose hours wondering why your program silently does nothing. Catch the *specific* exceptions you expect, keep the `try` block as short as possible, and let everything else crash with a full traceback.

</div>

### Raising exceptions

Your own functions should raise exceptions when they're given something they can't work with. That is much better than returning a strange value and letting the problem surface somewhere else:

```python
def average(numbers):
    if not numbers:
        raise ValueError("average() needs at least one number")
    return sum(numbers) / len(numbers)
```

Now the error message says exactly what went wrong and where. This is what "fail loudly" means: stop as early as possible with a clear message, instead of carrying on with bad data.

For errors specific to your program, you can define your own exception type by **subclassing** (building on) `Exception`. You'll learn what that means in the Classes and Objects lesson; for now, the pattern is enough:

```python
class QuizFileError(Exception):
    """Raised when a quiz file is missing required fields."""


def check_question(q):
    if "question" not in q or "answer" not in q:
        raise QuizFileError(f"Question is missing a field: {q}")
```

Code that calls `check_question` can then catch `QuizFileError` specifically, without accidentally catching anything else.

### Recover, retry or fail?

When you write an `except`, you're making a decision. There are three reasonable ones:

1. **Recover**: the problem is expected and you know a sensible fallback, such as asking the user again or using default settings.
1. **Retry**: the problem is probably temporary, such as a network timeout or a rate-limit error from an API. Wait a moment and try again, a limited number of times. You'll do exactly this when you call model APIs, and the official SDKs already retry some errors for you.
1. **Fail loudly**: the problem means something is genuinely wrong, such as a missing API key or a bug. Let the exception propagate, or raise a clearer one, so the program stops with a useful message.

A good rule: handle errors at the place where you know what to do about them. A low-level function that reads a file usually can't decide whether a missing file is fine; the `main()` function that called it often can.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 3: Exceptions](https://cs50.harvard.edu/python/weeks/3/). It builds up `try`, `except`, `else` and `pass` around a `get_int()` function very like `ask_int()` above.
1. Read [chapter 8, "Errors and Exceptions", of the official Python tutorial](https://docs.python.org/3/tutorial/errors.html), sections 8.1 to 8.7.
   - Skip 8.8 onward (predefined clean-up actions, exception groups and notes) for now.
1. Read [chapter 5, "Debugging", of Automate the Boring Stuff](https://automatetheboringstuff.com/3e/chapter5.html). It covers raising exceptions, assertions, logging and using a debugger.
   - The book demonstrates the debugger in the Mu editor. Follow along in VS Code instead, using [VS Code's Python debugging guide](https://code.visualstudio.com/docs/python/debugging) for the buttons. Learning to set a **breakpoint** (a line where the program pauses so you can inspect variables) is worth the effort now. It will save you hours later.
1. Practice:
   - Do Fuel Gauge, Felipe's Taqueria and Outdated from [CS50P Problem Set 3](https://cs50.harvard.edu/python/psets/3/).
   - Harden your Project: CLI Quiz Game. If `questions.json` is missing or isn't valid JSON, print a clear message and exit instead of showing a traceback. If a question is missing its `"answer"` field, raise a custom exception that names the bad question. Commit the change to your `mimir-quiz-game` repo.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The built-in exceptions reference](https://docs.python.org/3/library/exceptions.html) lists every exception and the hierarchy they form, so you can see why catching `OSError` also catches `FileNotFoundError`.
