### Introduction

Python is **dynamically typed**: a variable can hold any type of value, and Python only discovers a type mistake when the offending line actually runs. That flexibility is pleasant for small scripts and painful in bigger ones, where a function quietly receives a string instead of a number and crashes three files away.

**Type hints** (also called type annotations) let you write down what type each variable, parameter and return value is supposed to be. Python itself ignores them when running your code, but tools don't: your editor uses them for autocomplete and warnings, and a **type checker** such as mypy reads them to find bugs before you run anything.

For AI engineering, type hints are more than a safety net. They're how you *describe your data* to other code. Pydantic turns annotated classes into validators and JSON Schemas. SDKs and frameworks read a function's annotated parameters to generate the tool definition a model sees. Writing clear types now is practice for describing tools and structured outputs to models later.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Annotating variables, parameters and return values.
- Types for collections, such as `list[str]` and `dict[str, int]`.
- Optional values with `X | None`, and union types.
- Type aliases, `Literal` and `TypedDict`.
- Running the mypy type checker with uv.
- How code can read type hints, and why that matters for tools and schemas.

### Basic annotations

Put a colon and a type after a parameter or variable name, and `->` plus a type before the colon of a function definition to say what it returns:

```python
def estimate_cost(input_tokens: int, output_tokens: int, price_per_million: float) -> float:
    """Return the cost in dollars of one model call."""
    return (input_tokens + output_tokens) * price_per_million / 1_000_000


model: str = "claude-haiku-5-5"
retries: int = 3
verbose: bool = False
```

You rarely need to annotate simple variables like `retries`, since tools can infer the type from the value. Focus on function signatures. A fully annotated signature tells a reader everything they need to call the function without reading its body. A function that returns nothing is annotated `-> None`.

The built-in types you already know (`int`, `float`, `str`, `bool`) are all valid annotations, and so is any class you define, such as `Expense` or `Path`.

### Collections

For collections, put the type of the contents in square brackets:

```python
def average(scores: list[float]) -> float:
    return sum(scores) / len(scores)


def count_words(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts


unique_tags: set[str] = {"ai", "python"}
point: tuple[int, int] = (3, 4)
messages: list[dict[str, str]] = [{"role": "user", "content": "Hi"}]
```

Read `dict[str, int]` as "a dict whose keys are strings and whose values are ints". Older code and tutorials use `List`, `Dict` and `Optional` imported from the `typing` module. Since Python 3.9 and 3.10 you can use the lowercase built-in names and the `|` operator instead, and that's what this curriculum does.

### Optional values and unions

Many functions sometimes return a value and sometimes return `None`. Say so explicitly with `| None`:

```python
def find_user(users: dict[str, int], name: str) -> int | None:
    return users.get(name)
```

The `|` means "or", so `int | None` reads "an int, or None". The same syntax works for any **union** (a value that may be one of several types), such as `int | float`. Annotating the `None` case is valuable because forgetting about it is one of the most common bugs in any language, and the type checker will now remind you.

### Checking your code with mypy

Here's a file with two bugs. Python won't notice the second one until it runs that line:

```python
def estimate_cost(input_tokens: int, output_tokens: int, price_per_million: float) -> float:
    return (input_tokens + output_tokens) * price_per_million / 1_000_000


def find_user(users: dict[str, int], name: str) -> int | None:
    return users.get(name)


total = estimate_cost("1200", 300, 1.0)
age = find_user({"ada": 36}, "ada")
print(age + 1)
```

Add mypy to your project as a development dependency and run it:

```bash
uv add --dev mypy
uv run mypy costs.py
```

```text
costs.py:9: error: Argument 1 to "estimate_cost" has incompatible type "str"; expected "int"  [arg-type]
costs.py:11: error: Unsupported operand types for + ("None" and "int")  [operator]
costs.py:11: note: Left operand is of type "int | None"
Found 2 errors in 1 file (checked 1 source file)
```

Both bugs found, without running the program. The fix for the second is to handle the `None` case, for example `if age is not None: print(age + 1)`. After that check, mypy knows `age` must be an `int`. This is called **narrowing**.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Type hints are not enforced at runtime

`estimate_cost("1200", 300, 1.0)` still runs (and crashes) if you don't run a type checker. Hints are promises that tools check ahead of time, not guards. When data comes from outside your program, such as user input, a file or a model's reply, you still need to validate it at runtime. That's the job Pydantic will do for you in the Structured Outputs section.

</div>

VS Code's Python extension also understands type hints and underlines mistakes as you type. Running mypy on the command line is still worth it, because it checks the whole project at once and you can run it automatically before every commit.

### Aliases, Literal and TypedDict

A few more tools let you describe data precisely:

```python
from typing import Literal, TypedDict

Role = Literal["user", "assistant"]   # only these exact strings are allowed


class Message(TypedDict):
    role: Role
    content: str


Conversation = list[Message]          # a type alias: a name for a type


def last_user_message(conversation: Conversation) -> str | None:
    for message in reversed(conversation):
        if message["role"] == "user":
            return message["content"]
    return None
```

- A **type alias** like `Conversation` is just a readable name for a longer type.
- `Literal["user", "assistant"]` says the value must be one of those exact strings. mypy flags `{"role": "admin", ...}`.
- `TypedDict` describes a dict with fixed keys, each with its own type. It's ideal for JSON-shaped data that you want to keep as plain dicts. When you want an actual object instead, use a dataclass, whose fields are annotated the same way.

### Code can read your type hints

Type hints are stored on the function, and any code can read them:

```python
import typing

print(typing.get_type_hints(estimate_cost))
# {'input_tokens': <class 'int'>, 'output_tokens': <class 'int'>,
#  'price_per_million': <class 'float'>, 'return': <class 'float'>}
```

This is the trick behind a lot of AI tooling. A framework can take your function, read its name, docstring and annotated parameters, and generate a description of the function, in a format called JSON Schema, that a model uses to decide how to call it as a tool. Pydantic does the same for classes. So a function with good names, a clear docstring and precise type hints is already most of the way to being a good tool. You'll see this for real in the Structured Outputs and Tool Use sections.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Real Python's "Python Type Checking (Guide)"](https://realpython.com/python-type-checking/), a long, thorough and free walkthrough.
   - Read the sections on type systems, hello types, annotations and type checking with mypy, and the parts on sequences, mappings and type aliases.
   - Skim or skip the advanced material on generics, protocols, covariance and stub files. Some examples use the older `List` and `Optional` spellings; mentally translate them to `list` and `X | None`.
1. Read [mypy's "Getting started" guide](https://mypy.readthedocs.io/en/stable/getting_started.html) and keep [the mypy type hints cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) open while you practice. The cheat sheet answers almost every "how do I annotate this?" question.
1. Skim the introduction and the sections on type aliases, `Literal`, and `TypedDict` in [the typing module docs](https://docs.python.org/3/library/typing.html). It's a reference, not a tutorial, so use the page's table of contents to jump to the parts you need.
1. Practice:
   - Add type hints to every function in your `mimir-quiz-game` repo, including `-> None` on functions that return nothing.
   - Add mypy as a dev dependency and run `uv run mypy .` until it reports no errors. Note each bug or confusing spot it found, and commit the change.
   - Then try `uv run mypy --strict .`, which also complains about anything left unannotated, and see how far you can get.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Python typing documentation site](https://typing.python.org/en/latest/) collects guides and best practices from the people who maintain Python's type system.
- [The type narrowing guide](https://typing.python.org/en/latest/guides/type_narrowing.html) explains how checks like `if x is not None` change what a type checker knows.
- [The Pydantic docs](https://docs.pydantic.dev/latest/) are worth a glance now to see where annotated classes lead; you'll study Pydantic properly later.
