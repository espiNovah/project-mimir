### Introduction

So far, you've mostly read code you wrote yourself. At work, you'll spend far more time reading code than writing it: a teammate's pull request, a codebase you've just joined, a library that's behaving strangely, or a diff an AI coding assistant just produced. In AI engineering, libraries change faster than tutorials can keep up, so the docs and the source code are the truth.

Reading code is a skill, not a talent, and it has techniques you can learn. This lesson shows you how to approach an unfamiliar codebase without drowning, how to move around code quickly in VS Code, how to read tracebacks that pass through other people's code, how to read function signatures and type hints, and how to get answers from official documentation instead of guessing. It's also the foundation for the next lesson: you can't safely use an AI coding assistant if you can't read and check what it wrote.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- A strategy for finding your way around an unfamiliar codebase.
- Navigating code with VS Code: go to definition, find references and search.
- Finding and reading the source of the libraries you use.
- Reading tracebacks that pass through library code, including chained exceptions.
- Reading function signatures, type hints and the output of `help()`.
- How documentation is organized, and how to find answers in it.

### Reading a codebase with a question

The biggest beginner mistake is trying to read a codebase from top to bottom, file by file, like a book. Real projects have thousands of lines, and most of them are irrelevant to whatever you need right now. Experienced developers read code the way you'd use a map: with a destination in mind.

So start with a **question**. "How does this project load its settings?" "What happens when I call this function with `None`?" "Where does the expense total get calculated?" A question tells you what to look for and, just as important, what to skip.

Then orient yourself in roughly this order:

1. **The README.** It tells you what the project does, how to install and run it, and often how the code is laid out. You've written READMEs yourself, so you know what to look for.
1. **The project file.** For Python, that's `pyproject.toml`. It lists the dependencies (what the project builds on), the supported Python versions, and often **entry points**, the commands the package installs and the functions they run.
1. **The folder structure.** Look at the top-level folders and file names without opening them. A `src/` or package folder holds the code, `tests/` holds the tests, and `docs/` holds documentation. File names like `cli.py`, `config.py` or `models.py` are strong hints.
1. **The entry point.** Find where execution starts, such as a `main()` function or an `if __name__ == "__main__":` block, and follow the calls that are relevant to your question. Skim past everything else.
1. **The tests.** Tests are some of the best documentation a project has. Each one shows a real call with real inputs and the expected output. If you want to know how a function behaves on an edge case, search the tests for its name first.

As you go, note the files and functions you've traced and what each does, so tomorrow you don't start over. If you can, **run the code** too. Add a `breakpoint()` or a log line, or run one test with `uv run pytest -k some_name`, and watch what actually happens. Running code beats guessing about it.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Not understanding everything is normal

You'll hit code you don't understand: unfamiliar syntax, a design pattern you haven't seen, a clever trick. Note it and move on unless it blocks your question. Professional developers work in codebases they only partly understand every day. The goal is to understand enough to answer your question, not everything.

</div>

### Navigating code in your editor

Scrolling and opening files one by one is slow. VS Code, with the Python extension you installed in Your Setup, understands your code well enough to jump around it for you. These are the moves that matter most (on Windows and Linux, use Ctrl where this says Cmd):

- **Go to Definition** (F12, or Cmd-click a name): jump to where a function, class or variable is defined, even if it's in another file or inside an installed library.
- **Peek Definition** (Option+F12 on macOS, Alt+F12 elsewhere): show the definition in a small inline window, so you don't lose your place.
- **Go Back** (Ctrl+- on macOS, Alt+Left elsewhere): return to where you were before you jumped. Use it constantly; it turns jumping around into a trail you can retrace.
- **Find All References** (Shift+F12): list every place a function or class is used. This is how you find out who calls something before you change it.
- **Go to File** (Cmd+P): type part of a file name to open it.
- **Go to Symbol** (Cmd+Shift+O): list the functions and classes in the current file and jump to one.
- **Search across files** (Cmd+Shift+F): search the whole project for text, such as an error message. Pasting part of an error message into project search is often the fastest way to find the code that raised it.
- **Hover**: rest the mouse on a name to see its type and its docstring.

The terminal can do some of this too. From the Shell Scripting lesson, `grep -rn "load_config" src/` finds every line mentioning `load_config`, with line numbers. And Git can tell you *why* code looks the way it does: `git log -p path/to/file.py` shows each change to that file with its commit message, and `git blame path/to/file.py` shows which commit last changed each line. A good commit message often explains a strange-looking line better than any comment.

### Reading library source code

Libraries aren't magic. They're Python files, like yours, sitting on your disk. When the docs don't answer a question, read the source.

The easiest route is Go to Definition: Cmd-click `json.loads` in your code and VS Code opens the standard library's `json/__init__.py`. Third-party packages installed with `uv add` live inside your project's virtual environment, in `.venv/lib/python3.12/site-packages/`. You can also ask Python directly. The standard library's `inspect` module can look inside other code:

```python
# peek.py: find out where code lives and what it looks like.
import inspect
import json
import textwrap

# Where is this module on disk?
print(json.__file__)

# What arguments does this function take?
print(inspect.signature(json.dumps))

# What does its docstring say? (Just the first line here.)
print(inspect.getdoc(textwrap.shorten).splitlines()[0])

# Show me the actual source code.
print(inspect.getsource(textwrap.shorten))
```

Run it with `uv run peek.py`. The last line prints the whole `shorten` function: just two lines of code plus a docstring. Library functions are often shorter and more readable than you'd fear.

When you read library code, read it with your question in mind, just like a codebase. Look for the function you called, skip private helpers (names starting with `_`) until you need them, and remember that the tests in the library's GitHub repository show how its authors expect it to be used. Look, but don't edit files in `site-packages`. Your changes would vanish the next time uv reinstalls the package.

### Tracebacks through library code

You learned to read a traceback from the bottom up in the Errors and Exceptions lesson. Real tracebacks are often longer, because the error happens deep inside a library you called. Here's a small program that wraps a library error in its own exception, as you've learned to do:

```python
# load_config.py
import json


class ConfigError(Exception):
    pass


def load_config(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        raise ConfigError("config is not valid JSON") from err


load_config('{"model": fast}')  # fast should be in quotes
```

Running it prints two tracebacks (shortened here, and the exact lines vary by Python version):

```text
Traceback (most recent call last):
  File ".../load_config.py", line 10, in load_config
    return json.loads(text)
  File ".../lib/python3.12/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
  File ".../lib/python3.12/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File ".../lib/python3.12/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 11 (char 10)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File ".../load_config.py", line 15, in <module>
    load_config('{"model": fast}')
  File ".../load_config.py", line 12, in load_config
    raise ConfigError("config is not valid JSON") from err
ConfigError: config is not valid JSON
```

Three habits help:

- **Read chained tracebacks from the top.** "The above exception was the direct cause of the following exception" means the first traceback is the root cause and the second is the wrapper. (You'd see "During handling of the above exception, another exception occurred" instead if a new error happened inside an `except` block without `from`.) Here, the useful detail, "Expecting value: line 1 column 11", is in the first one.
- **Find the last frame in your code.** File paths tell you whose code each frame is. Frames under `lib/python3.12/` or `site-packages/` belong to Python or a library. The last frame in a file you wrote, `load_config.py` line 10, is almost always where to start, because that's where you handed the library something it didn't like.
- **Assume your bug first.** Libraries have bugs, but much less often than the code calling them. Check what you passed in before suspecting the library.

### Reading signatures and type hints

A function's **signature** is its name, its parameters and its return type: a compact summary of how to call it. Learn to read one and you'll often not need the rest of the docs. Ask Python with `help()`:

```text
>>> help(sorted)
sorted(iterable, /, *, key=None, reverse=False)
    Return a new list containing all items from the iterable in ascending order.
```

Two markers in that signature trip people up:

- A **`/`** means every parameter before it is **positional-only**: you pass it by position, never by name. You must write `sorted(items)`, not `sorted(iterable=items)`.
- A **`*`** on its own means every parameter after it is **keyword-only**: you must pass it by name. You write `sorted(items, reverse=True)`, never `sorted(items, None, True)`.

Parameters with `=` have default values and are optional. A trailing `**kwargs` (or `**kw`) means "extra keyword arguments", which are usually passed on to something else, so check the docs to see where they go. `json.dumps` from the example above shows all of these: `(obj, *, skipkeys=False, ..., sort_keys=False, **kw)` means pass `obj` however you like, and everything else by name.

Type hints, which you learned in the Type Hints lesson, add a second layer. A signature like `def fetch(url: str, timeout: float | None = None) -> dict[str, Any]:` tells you that `timeout` is optional, may be `None` and returns a dict with string keys. When the docs are thin, hovering over a function in VS Code to see its types is often enough. And when you pass the wrong type, mypy will usually tell you before you run anything.

### Finding answers in official docs

When you have a question about a tool, go to its official documentation first. Blog posts and forum answers are often written for an older version, and AI assistants can confidently describe functions that don't exist. The official docs are maintained alongside the code.

Good documentation usually comes in four kinds, a split known as **Diátaxis**:

- **Tutorials** walk a beginner through a first project. Read them once, in order.
- **How-to guides** solve one specific task, such as "how to parametrize tests". Use them when you know what you want to do.
- **Reference** lists every function, class and option, precisely and dryly. Use it to look things up, not to learn from scratch. The Python docs' Library Reference is this kind.
- **Explanation** pages discuss background and design: why something works the way it does.

If a reference page feels impenetrable, look for a tutorial or how-to on the same topic.

A few habits make docs work for you:

- **Check the version.** Most docs have a version selector. Make sure it matches the version in your `uv.lock`, or your installed version from `uv pip show package-name`.
- **Search inside the docs**, not just the web. Most doc sites have a search box, and your browser's find-in-page (Cmd+F) works wonders on long reference pages.
- **Read the examples first**, then the parameter list.
- **Check the changelog** (often called "release notes" or "what's new") when code that used to work stops working after an upgrade.
- **Search the project's GitHub issues** for your exact error message. If something looks like a bug, someone has often already reported it, with a workaround.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read VS Code's [Code Navigation guide](https://code.visualstudio.com/docs/editing/editingevolved). It covers every navigation feature from this lesson, with animations. Try each shortcut in your Expense Tracker as you read.
1. Read the [Special parameters section of the official Python tutorial](https://docs.python.org/3/tutorial/controlflow.html#special-parameters), which explains `/` and `*` in signatures with short examples.
1. Read the start page of [Diátaxis](https://diataxis.fr/), then open the [Python documentation home](https://docs.python.org/3/) and the [pytest documentation](https://docs.pytest.org/en/stable/) and identify which parts are tutorials, how-to guides, reference and explanation.
1. Skim the [inspect module docs](https://docs.python.org/3/library/inspect.html), focusing on `signature()`, `getdoc()` and `getsource()`. You don't need the rest yet.
1. Practice by touring a real codebase:
   - Clone [python-dotenv](https://github.com/theskumar/python-dotenv), a small, popular library that loads settings from a `.env` file. You'll use it in the Web section. Open it in VS Code.
   - Following the orientation steps in this lesson, answer these questions in a notes file, citing the file and line for each answer: What does `load_dotenv()` return? By default, does it overwrite an environment variable that's already set, and which parameter changes that? Which test checks that behavior? What happens if the `.env` file doesn't exist?
   - Write a five-sentence "map" of the project: what lives in which file. Then use `git log` on one file and find the commit message for a change that interests you.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why should you start reading a codebase with a question, and where should you look first?](#reading-a-codebase-with-a-question)
- [How do you find every place a function is called in VS Code?](#navigating-code-in-your-editor)
- [Where do installed packages live, and how can you see a function's source code?](#reading-library-source-code)
- [In a chained traceback, which part shows the root cause, and which frame should you check first?](#tracebacks-through-library-code)
- [What do a lone slash and a lone asterisk mean in a function signature?](#reading-signatures-and-type-hints)
- [What are the four kinds of documentation, and when do you use the reference?](#finding-answers-in-official-docs)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [GitHub's code search syntax guide](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax) shows how to search across every public repository, which is a great way to see how other people actually call a function.
- [The Python Library Reference index](https://docs.python.org/3/library/index.html) lists every standard-library module. Skimming the names once helps you notice when something you're about to write already exists.
