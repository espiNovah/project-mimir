### Introduction

You can now write programs that work. This lesson is about writing them the way experienced Python developers do, which people call **Pythonic** code. Pythonic code isn't about being clever. It uses the tools the language gives you so that code is shorter, harder to get wrong, and easier to read.

There's a practical reason to learn this now: you'll read a lot of other people's code. Library documentation, SDK examples and AI coding assistants all use these features constantly. When you call a language model with streaming turned on, the SDK hands you a **generator** of text chunks. When you sort search results by score, you'll write `sorted(results, key=lambda r: r["score"])`. When you open a file or a network connection, you'll use `with`. If these look like magic, you'll struggle to read examples; once you know them, they're just shorthand.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- More comprehensions, and when not to use them.
- Iterators, generators and `yield`, and why streaming APIs use them.
- Looping helpers: `enumerate` and `zip`.
- Small anonymous functions with `lambda`, and sorting with `key=`.
- Flexible functions with `*args` and `**kwargs`.
- Context managers and the `with` statement.

### Comprehensions revisited

You met list and dict comprehensions in the data structures lesson. There are two more forms. A **set comprehension** uses braces without a colon, and gives you unique values:

```python
words = ["Agent", "tool", "agent", "Tool", "loop"]
unique = {w.lower() for w in words}   # {'agent', 'tool', 'loop'}
```

A comprehension can also transform each item with a **conditional expression**, Python's one-line if/else: `value_if_true if condition else value_if_false`. Note where it goes. A filter (`if` at the end) drops items; a conditional expression (`if ... else` at the front) keeps every item but changes it:

```python
scores = [0.91, 0.42, 0.77, 0.15]
passed = [s for s in scores if s >= 0.5]                   # [0.91, 0.77]
labels = ["pass" if s >= 0.5 else "fail" for s in scores]  # ['pass', 'fail', 'pass', 'fail']
```

Comprehensions are for building a collection. If you're tempted to nest three loops inside one, or to call a function only for its side effects (like `[print(x) for x in items]`), write a normal `for` loop instead. Readability beats brevity.

### Iterators and generators

When you write `for line in something`, Python asks `something` for an **iterator**: an object that hands out one item at a time, on request, until it runs out. Lists, strings, dicts and files all provide iterators. You can drive one by hand with `next()`:

```python
it = iter(["a", "b"])
next(it)   # 'a'
next(it)   # 'b'
next(it)   # raises StopIteration: nothing left
```

A `for` loop is just a tidy way of calling `next()` until `StopIteration`.

A **generator** is the easiest way to make your own iterator. It looks like a function, but it uses `yield` instead of `return`. Each `yield` hands one value to the caller and *pauses* the function right there. The next time the caller asks for a value, the function resumes from where it paused, with all its variables intact:

```python
import time


def fake_stream(text):
    """Pretend to be a model API that streams its reply word by word."""
    for word in text.split():
        time.sleep(0.2)          # pretend the model is thinking
        yield word + " "


def main():
    reply = []
    for chunk in fake_stream("Generators hand you one piece at a time."):
        print(chunk, end="", flush=True)   # show each chunk as it arrives
        reply.append(chunk)
    print()
    print(f"Full reply was {len(''.join(reply))} characters.")


main()
```

Run it and watch the words appear one by one. Calling `fake_stream(...)` doesn't run any of its code; it returns a generator object. The code runs a little at a time as the `for` loop pulls values out. That's exactly the shape of a streaming LLM response: the model produces text a few tokens at a time, and the SDK yields each chunk the moment it arrives, so your program can print it immediately instead of waiting for the whole answer. You'll see this in the Streaming Responses lesson. The loop above, printing each chunk with `end=""` and `flush=True` while collecting the pieces, is the pattern you'll use there.

Generators have a second benefit: they use almost no memory, because only one item exists at a time. A generator can read a 10 GB log file line by line, or even run forever. The trade-off is that a generator can be consumed only once. Loop over it a second time and you get nothing; if you need the items again, store them in a list with `list(gen)`.

A **generator expression** is a comprehension with round brackets. It produces items lazily instead of building a list. It's handy inside functions like `sum()`:

```python
total_tokens = sum(len(chunk.split()) for chunk in ["one two", "three"])   # 3
```

### Looping with enumerate and zip

Two built-ins remove most of the index juggling from loops. `enumerate` gives you a counter alongside each item, and `zip` walks two or more sequences side by side:

```python
questions = ["Capital of France?", "2 + 2?", "Largest planet?"]
expected = ["Paris", "4", "Jupiter"]
given = ["paris", "4", "Saturn"]

for number, (q, want, got) in enumerate(zip(questions, expected, given), start=1):
    mark = "correct" if got.lower() == want.lower() else f"wrong (expected {want})"
    print(f"{number}. {q} {got}: {mark}")

lookup = dict(zip(questions, expected))   # build a dict from two lists
```

Compare that with `for i in range(len(questions)):` followed by `questions[i]`, `expected[i]` and `given[i]`. The `zip` version can't get an index wrong. Be aware that `zip` stops at the shortest sequence, silently. Pass `strict=True` if the lists should always be the same length and you want an error when they aren't.

### Lambda and sorting with a key

`sorted()` sorts numbers and strings out of the box. To sort anything else, such as a list of dicts, you tell it what to sort *by* with the `key` argument. `key` takes a function, which `sorted` calls on each item to get the value to compare:

```python
results = [
    {"doc": "pricing.md", "score": 0.71},
    {"doc": "faq.md", "score": 0.93},
    {"doc": "intro.md", "score": 0.40},
]


def by_score(result):
    return result["score"]


best_first = sorted(results, key=by_score, reverse=True)
```

Writing a named function for a one-line job is clunky, so Python lets you write a small unnamed function inline with `lambda`. `lambda r: r["score"]` means "a function that takes `r` and returns `r["score"]`":

```python
best_first = sorted(results, key=lambda r: r["score"], reverse=True)
top = max(results, key=lambda r: r["score"])        # min and max take key= too
by_name = sorted(results, key=lambda r: r["doc"].lower())
```

A lambda can only contain a single expression: no statements, no loops. If it's getting long, use a named function instead. Also note that `sorted()` returns a new list, while `list.sort()` sorts the list in place and returns `None`, a classic source of bugs.

### Flexible arguments with args and kwargs

Sometimes a function should accept any number of arguments. A parameter starting with `*` collects extra positional arguments into a tuple, and one starting with `**` collects extra keyword arguments into a dict. By convention they're called `*args` and `**kwargs`:

```python
def log_event(name, *args, **kwargs):
    print(f"event={name} args={args} kwargs={kwargs}")


log_event("request", "retry", 3, model="cheap", timeout=30)
# event=request args=('retry', 3) kwargs={'model': 'cheap', 'timeout': 30}
```

The stars also work in reverse, when *calling* a function. `*` unpacks a list into positional arguments and `**` unpacks a dict into keyword arguments:

```python
settings = {"model": "cheap", "timeout": 30}
log_event("request", **settings)   # same as model="cheap", timeout=30
```

You'll see `**` constantly with APIs: build a dict of request options, then pass it with `client.messages.create(**options)`. You'll write `*args` and `**kwargs` yourself less often than you'll read them, mostly in functions that pass arguments along to another function, such as a wrapper that adds retries around any API call.

### Context managers and with

Some resources must be cleaned up after use. An open file should be closed, a network connection released, a lock unlocked. Forgetting to clean up causes slow leaks and corrupted files, and it's easy to forget, especially when an error happens halfway through. A **context manager** is an object that handles setup and cleanup for you, and the `with` statement uses one:

```python
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("Context managers clean up after themselves.\n")
# here, the file is already closed, even if write() had failed
```

`with` runs the setup (opening the file), gives you the resource under the name after `as`, runs your indented block, and then always runs the cleanup when the block ends, however it ends. You'll use `with` for files in the next lesson, and later for HTTP clients and streaming API responses, where `with client.messages.stream(...) as stream:` makes sure the connection is closed.

You can write your own context manager with a generator and the `contextlib` module. Code before the `yield` is setup, and code after it is cleanup:

```python
import time
from contextlib import contextmanager


@contextmanager
def timer(label):
    start = time.perf_counter()
    yield                                   # the with-block runs here
    elapsed = time.perf_counter() - start
    print(f"{label} took {elapsed:.2f}s")


with timer("fake model call"):
    time.sleep(0.5)
```

The `@contextmanager` line is a **decorator**, a way of wrapping a function to give it extra behavior. You don't need to know how decorators work yet; just recognize the pattern. To make the cleanup run even when the block raises an error, you'd wrap the `yield` in `try`/`finally`, which you'll learn in Errors and Exceptions.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 9: Et Cetera](https://cs50.harvard.edu/python/weeks/9/). It's a tour of exactly these features: unpacking, `*args` and `**kwargs`, `map` and `filter`, comprehensions, `enumerate`, and generators with `yield`.
   - You can skip the parts on type hints, docstrings and `argparse`; later lessons cover them.
1. Read the [Generators section of the official tutorial](https://docs.python.org/3/tutorial/classes.html#generators), plus the "Generator Expressions" section right after it. It's short and shows `yield` with a different example.
1. Read the [Sorting Techniques how-to](https://docs.python.org/3/howto/sorting.html), up to and including "Sort Stability and Complex Sorts". It shows `key=` and `lambda` on lists of tuples and objects.
1. Read [Arbitrary Argument Lists and Unpacking Argument Lists](https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists) in the official tutorial for the precise rules on `*` and `**`.
1. Do the [pythonic-python exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/pythonic-python). Each exercise has a starter file and failing tests; make the tests pass with `uv run pytest pythonic-python/<exercise>` from the `exercises/` folder. You'll learn pytest properly later, so for now just read the output: a dot or "passed" is good, and an `F` means keep going.
1. Rewrite an old program Pythonically. Take a script from your practice project and find at least three loops that could use a comprehension, `enumerate`, `zip` or `sorted(key=...)`. Make the change, check the output is the same, and note in your journal which version you find easier to read and why.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What's the difference between a filter and a conditional expression in a comprehension?](#comprehensions-revisited)
- [What happens when a generator function hits yield, and why do streaming APIs use generators?](#iterators-and-generators)
- [What does zip do when its sequences have different lengths?](#looping-with-enumerate-and-zip)
- [How would you sort a list of dicts by their "score" value, highest first?](#lambda-and-sorting-with-a-key)
- [What do `*args` and `**kwargs` collect, and what does `**` do when you call a function?](#flexible-arguments-with-args-and-kwargs)
- [What does a with statement guarantee about cleanup?](#context-managers-and-with)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html) goes deeper into iterators, generators and generator expressions.
- [The itertools docs](https://docs.python.org/3/library/itertools.html) list ready-made tools for working with iterators, such as `islice` for taking the first few items from a generator and `batched` for splitting items into groups.
- [The contextlib docs](https://docs.python.org/3/library/contextlib.html) show more ways to build and combine context managers.
