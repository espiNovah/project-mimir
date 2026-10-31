### Introduction

Up to now, each of your programs has lived in a single file and used only what Python gives you out of the box. Real projects don't work that way. They split code across several files so each file has one job, and they lean heavily on code other people wrote: Python's huge standard library, plus hundreds of thousands of third-party packages.

AI engineering is especially dependent on other people's code. You won't write an HTTP client or a JSON Schema validator from scratch; you'll install the `anthropic` or `openai` SDK, `pydantic`, `httpx` and friends, and wire them together. This lesson shows how imports work, how to organize your own code into modules, and how to manage third-party packages properly with uv.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What modules and imports are.
- The different forms of the `import` statement.
- A tour of useful standard library modules.
- Splitting your own code into modules, and what `__name__ == "__main__"` really does.
- Packages: folders of modules.
- Installing third-party packages with `uv add`, and what `pyproject.toml` and `uv.lock` record.

### Modules and imports

A **module** is simply a `.py` file. When you write `import json`, Python finds the module named `json`, runs it once, and gives you a name, `json`, through which you can reach everything it defines:

```python
import random
import statistics

scores = [72, 88, 95, 61]
print(random.choice(scores))      # one score at random
print(statistics.mean(scores))    # 79
```

There are a few forms of import, and you'll see all of them:

```python
import json                          # use as json.loads(...)
from pathlib import Path             # use as Path(...) directly
from statistics import mean, median  # import several names
import datetime as dt                # give the module a shorter alias
```

`import module` keeps everything behind the module's name, so it's always clear where a function came from. `from module import name` is shorter and fine for things you use a lot. Avoid `from module import *`, which dumps every name into your file and makes it impossible to tell where anything came from.

By convention, imports go at the top of the file: standard library modules first, then third-party packages, then your own modules, each group separated by a blank line.

### The standard library

Python ships with a **standard library** of modules for common jobs, so you don't need to install anything to use them. A few you'll reach for often:

- `json`, `csv` and `pathlib` for data and files (you've met these).
- `random` for random choices and shuffling.
- `datetime` for dates and times.
- `math` and `statistics` for numbers.
- `os` and `sys` for talking to the operating system, such as reading environment variables with `os.environ`, which is how you'll load API keys in the API Keys and Secrets lesson.
- `argparse` for command-line options like `--verbose`.
- `collections` for extra containers, such as `Counter` for counting things.

Before writing a utility yourself, search the standard library docs. There's a good chance it's already there.

### Splitting your own code into modules

Any `.py` file you write can be imported by another file in the same folder. Suppose your quiz has grown. Move the question-loading code into `questions.py`:

```python
# questions.py
import json


def load_questions(path):
    """Load a list of question dicts from a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # Quick manual check when this file is run directly
    print(load_questions("questions.json")[0])
```

Then use it from `main.py`:

```python
# main.py
from questions import load_questions


def main():
    questions = load_questions("questions.json")
    print(f"Loaded {len(questions)} questions.")


if __name__ == "__main__":
    main()
```

Now the mystery line from the Functions lesson makes sense. Every module has a built-in variable called `__name__`. When you run a file directly (`uv run questions.py`), Python sets its `__name__` to `"__main__"`. When another file imports it, `__name__` is set to the module's name, `"questions"`. So the code under `if __name__ == "__main__":` runs when you execute the file, but *not* when you import it. Without that guard, importing `questions` would print a question as a side effect.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Don't name your files after modules

If you create a file called `json.py` or `random.py` in your project, `import json` will find *your* file instead of the standard library, and you'll get baffling errors such as `AttributeError: module 'json' has no attribute 'loads'`. Give your modules distinctive names like `quiz_data.py`.

</div>

### Packages

A **package** is a folder of modules. Once a project has more than a handful of files, you group related modules into packages:

```text
mimir-quiz-game/
  pyproject.toml
  main.py
  quiz/
    __init__.py
    questions.py
    scoring.py
```

The `__init__.py` file (often empty) marks the folder as a regular package. You import from it with dots: `from quiz.questions import load_questions`. Third-party libraries are packages too, just much bigger ones. When you write `from anthropic import Anthropic` later, you're importing a name from the `anthropic` package's `__init__.py`.

### Third-party packages with uv

Packages published by the community live on [PyPI](https://pypi.org/), the Python Package Index. In the Virtual Environments and uv lesson you saw that each project gets its own virtual environment so its packages don't clash with other projects. To install a package into the current project, use `uv add`:

```bash
uv add rich
```

That does three things: it downloads `rich` into the project's `.venv`, records it under `dependencies` in `pyproject.toml`, and writes the exact versions of `rich` and everything it depends on into `uv.lock`. Now any file in the project can use it:

```python
from rich import print

print("[bold green]Correct![/bold green] Your score is [bold]7/10[/bold].")
```

Run it with `uv run main.py`, as usual. Commit both `pyproject.toml` and `uv.lock` to Git, but never the `.venv` folder (the `.gitignore` that `uv init` creates already excludes it). Anyone who clones your repo then runs `uv sync` (or just `uv run`) and gets exactly the same versions you had, which is what makes "it works on my machine" work on theirs too.

Some packages are only needed while developing, such as test runners and type checkers. Add those as **development dependencies** with `uv add --dev pytest`, which you'll do in the Testing with pytest lesson. To remove a package, use `uv remove rich`.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 4: Libraries](https://cs50.harvard.edu/python/weeks/4/). It covers `random`, `statistics`, command-line arguments with `sys.argv`, installing packages, calling a web API and writing your own module.
   - Whenever the lecture says `pip install something`, use `uv add something` inside your practice project instead.
   - The part about calling an API with `requests` is a preview of the Working with APIs lesson in The Web for AI Builders section.
1. Read [chapter 6, "Modules", of the official Python tutorial](https://docs.python.org/3/tutorial/modules.html), sections 6.1 (including 6.1.1, "Executing modules as scripts", and 6.1.2, "The Module Search Path"), 6.2 and the introduction to 6.4, "Packages". Skip 6.1.3 (compiled files), 6.3 (`dir()`) and the subsections of 6.4.
1. Skim [the official tutorial's "Brief Tour of the Standard Library"](https://docs.python.org/3/tutorial/stdlib.html) so you know roughly what's already available.
1. Read [the uv guide to working on projects](https://docs.astral.sh/uv/guides/projects/), focusing on "Managing dependencies", `pyproject.toml` and `uv.lock`.
1. Practice:
   - From [CS50P Problem Set 4](https://cs50.harvard.edu/python/psets/4/), do Emojize, Frank, Ian and Glen's Letters, Adieu, Adieu, Guessing Game and Little Professor. Install the packages they need with `uv add`.
   - Refactor your Project: CLI Quiz Game into at least two modules, for example one for loading and checking questions and one for running the game, keeping `uv run main.py` working. Commit the change.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between import json and from json import loads?](#modules-and-imports)
- [Why search the standard library before writing a utility yourself?](#the-standard-library)
- [What does if __name__ == "__main__" actually do?](#splitting-your-own-code-into-modules)
- [Why can naming your file random.py or json.py break your program?](#splitting-your-own-code-into-modules)
- [What is a package, and how do you import from one?](#packages)
- [What does uv add record in pyproject.toml and uv.lock?](#third-party-packages-with-uv)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The `__main__` docs](https://docs.python.org/3/library/__main__.html) explain `__name__ == "__main__"` and `__main__.py` in full.
- [The uv docs on managing dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/) cover development dependencies, version constraints and more.
- [The argparse tutorial](https://docs.python.org/3/howto/argparse.html) is a gentle introduction to giving your scripts proper command-line options, which you can use in the Project: Expense Tracker.
