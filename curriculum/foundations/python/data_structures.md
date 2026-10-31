### Introduction

A single variable holds a single value. Real programs juggle many values at once: every question in a quiz, every message in a conversation, every setting in a configuration. Python's built-in **collections** hold groups of values, and four of them cover almost everything you will ever need: lists, dictionaries, sets and tuples.

These four are not just beginner topics. When you call a chat model's API, the conversation you send is a *list* of *dictionaries*. The response comes back as nested dictionaries and lists. Configuration files, tool definitions, evaluation datasets: all of them are lists and dicts underneath. Get fluent here and the rest of the curriculum gets much easier.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Lists: ordered, changeable sequences.
- Dictionaries: looking values up by key.
- Sets: unique values and fast membership checks.
- Tuples: fixed groups of values and unpacking.
- Looping over collections and nesting them.
- List and dict comprehensions.
- Mutability, and why two names can share one list.

### Lists

A **list** is an ordered collection, written with square brackets. It can grow, shrink and change:

```python
questions = ["What is 2 + 2?", "What color is the sky?"]
questions.append("What is the capital of France?")  # add to the end
print(len(questions))   # 3
print(questions[0])     # first item
print(questions[-1])    # last item
print(questions[1:])    # a slice: every item from index 1 on

questions[1] = "What color is grass?"  # replace an item
removed = questions.pop()              # remove and return the last item
print("capital" in removed)            # True
```

Loop over a list with `for`. If you also need the position, use `enumerate()`, which gives you an index and the item together:

```python
for number, question in enumerate(questions, start=1):
    print(f"{number}. {question}")
```

Other everyday tools: `sorted(items)` returns a new sorted list, `items.sort()` sorts in place, `sum(numbers)`, `min()` and `max()` do what they say, and `", ".join(words)` glues a list of strings together. Going the other way, `"a,b,c".split(",")` turns a string into a list.

### Dictionaries

A **dictionary** (dict) stores **key-value pairs**, written with curly braces. Instead of asking for item number 2, you ask for the value under a key:

```python
settings = {
    "model": "claude-haiku-5-5",
    "max_tokens": 1024,
    "temperature": 0.7,
}

print(settings["model"])               # look up by key
settings["temperature"] = 0.2          # change a value
settings["stream"] = False             # add a new key
print(settings.get("top_p"))           # None: .get() doesn't crash on a missing key
print(settings.get("top_p", 1.0))      # 1.0: or you can give a fallback
print("model" in settings)             # True: checks keys
```

Asking for a missing key with square brackets, `settings["top_p"]`, raises a `KeyError`. Use `.get()` when a key might legitimately be missing.

Loop over keys and values together with `.items()`:

```python
for key, value in settings.items():
    print(f"{key} = {value}")
```

A classic pattern is counting with a dict:

```python
words = "the cat and the hat and the bat".split()
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
print(counts)  # {'the': 3, 'cat': 1, 'and': 2, 'hat': 1, 'bat': 1}
```

Dict keys must be unique and unchangeable (strings and numbers are typical). Values can be anything, including other lists and dicts.

### Nesting: the shape of real data

Here is what a conversation with a chat model looks like as Python data. Every major provider uses some version of this shape:

```python
messages = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "Paris."},
    {"role": "user", "content": "And of Japan?"},
]

for message in messages:
    print(f"{message['role']}: {message['content']}")

messages.append({"role": "assistant", "content": "Tokyo."})
print(messages[0]["content"])  # index into the list, then key into the dict
```

Reading nested data is a skill: work from the outside in. `messages[0]` is a dict; `messages[0]["content"]` is the string inside it. When you are lost, `print()` the intermediate value and check its `type()`.

### Sets and tuples

A **set** is an unordered collection of *unique* values. Adding a duplicate does nothing. Sets are ideal for removing duplicates and for asking "have I seen this before?", which is very fast even with millions of items:

```python
tags = ["python", "ai", "python", "agents", "ai"]
unique_tags = set(tags)
print(unique_tags)            # {'python', 'ai', 'agents'} (order not guaranteed)
print("ai" in unique_tags)    # True

allowed = {"search", "calculator"}
requested = {"search", "delete_files"}
print(requested - allowed)    # {'delete_files'}: in requested but not allowed
```

Note that `{}` makes an empty *dict*. An empty set is `set()`.

A **tuple** is like a list that cannot be changed, written with parentheses. Use one for a small, fixed group of related values, such as a pair of coordinates or a function returning two things:

```python
def min_max(numbers):
    return min(numbers), max(numbers)   # returns a tuple

low, high = min_max([4, 9, 1, 7])      # unpacking
print(low, high)  # 1 9
```

**Unpacking** assigns each item of a tuple (or list) to its own name. You already used it in `for key, value in settings.items()`.

### Comprehensions

A **comprehension** builds a new list or dict from an existing one in a single line. These two blocks do the same thing:

```python
prices = [3.5, 12.0, 0.99, 25.0]

cheap = []
for p in prices:
    if p < 10:
        cheap.append(p)

cheap = [p for p in prices if p < 10]
```

Read it as "`p`, for each `p` in `prices`, if `p < 10`". Dict comprehensions use braces: `{word: len(word) for word in ["agent", "tool"]}` gives `{'agent': 5, 'tool': 4}`. Use comprehensions when they read clearly, and fall back to a normal loop when they don't.

### Mutability and shared references

Lists, dicts and sets are **mutable**: they can change in place. Strings, numbers and tuples are **immutable**. This has a surprising consequence:

```python
a = [1, 2, 3]
b = a          # b is another name for the SAME list
b.append(4)
print(a)       # [1, 2, 3, 4]

c = a.copy()   # a new, separate list
c.append(5)
print(a)       # [1, 2, 3, 4]: unchanged
```

Assignment never copies; it just adds another name for the same object. When you pass a list into a function, the function can change the caller's list. That is sometimes what you want, and occasionally a confusing bug, so keep it in mind.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Choosing a collection

Need order and duplicates? Use a list. Need to look things up by name? Use a dict. Need uniqueness or fast "is it in there?" checks? Use a set. Have a small fixed group of values that belong together? Use a tuple.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [chapter 6, "Lists"](https://automatetheboringstuff.com/3e/chapter6.html) and [chapter 7, "Dictionaries and Structuring Data"](https://automatetheboringstuff.com/3e/chapter7.html) of Automate the Boring Stuff. Chapter 6 also covers tuples and the reference behavior from the last section, with helpful diagrams.
1. Read [chapter 5, "Data Structures", of the official Python tutorial](https://docs.python.org/3/tutorial/datastructures.html), sections 5.1 to 5.6. Section 5.1.3 covers list comprehensions and 5.6 shows looping techniques such as `enumerate()`, `zip()` and `.items()`.
   - You can skip 5.1.1 (lists as stacks), 5.1.2 (queues) and 5.1.4 (nested comprehensions) on a first read.
1. Rewatch the second half of [CS50P Lecture 2: Loops](https://cs50.harvard.edu/python/weeks/2/), where lists and dicts are combined with loops, including a list of dicts.
1. Practice:
   - From [CS50P Problem Set 2](https://cs50.harvard.edu/python/psets/2/), do camelCase, Coke Machine and Just setting up my twttr (more loop practice, now that you've rewatched Lecture 2), and Nutrition Facts (a dict lookup).
   - On the [Exercism Python track](https://exercism.org/tracks/python), complete "Card Games" (lists), "Inventory Management" (dicts), "Cater Waiter" (sets) and "Tisbury Treasure Hunt" (tuples).
   - In the [Python basics exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/python-basics), make the tests pass for exercises 06 and 07 (Word counts and Common tags). Each exercise has a starter file and failing tests; run them with `uv run pytest python-basics/<exercise>` from the `exercises/` folder (the set's README shows the setup).
1. Build a tiny conversation log. In your practice project, write a script with a `messages` list like the one above. In a loop, read lines from the user with `input()`, append each as a `{"role": "user", "content": ...}` dict, append a fake assistant reply (for example, the user's text reversed), and stop when the user types `quit`. At the end, print how many messages were sent by each role using a counting dict.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [When would you reach for a dictionary instead of a list?](#dictionaries)
- [What is the difference between d[key] and d.get(key) when the key is missing?](#dictionaries)
- [How do you dig a value out of a list of dictionaries?](#nesting-the-shape-of-real-data)
- [What are sets good at, and what is tuple unpacking?](#sets-and-tuples)
- [How can a comprehension replace a loop that builds a list?](#comprehensions)
- [Why can changing one list also change what another variable shows?](#mutability-and-shared-references)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Python docs on built-in types](https://docs.python.org/3/library/stdtypes.html) list every method on lists, dicts, sets and tuples. Search the page for the one you need.
- [Python Tutor](https://pythontutor.com/) draws arrows from names to objects, which makes shared references obvious.
