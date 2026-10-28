### Introduction

You've been using **objects** all along. A string is an object with methods like `.upper()`. A list is an object with `.append()`. A `Path` is an object with `.exists()`. In this lesson you'll learn to create your own kinds of objects by writing **classes**.

A class bundles data and the functions that work on that data into one named thing. Instead of passing a loose dict like `{"description": "Coffee", "amount": 3.5}` around and hoping every part of your code spells the keys the same way, you can define an `Expense` class and let Python enforce the shape.

This matters directly for AI work. The SDKs you'll use return objects, not raw dicts: you'll write `response.content[0].text` and `response.usage.output_tokens`. And Pydantic, the library you'll use to validate model output in the Structured Outputs section, is built around classes that look almost exactly like the dataclasses at the end of this lesson.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What classes and instances are.
- Creating objects with `__init__` and understanding `self`.
- Attributes and methods.
- Readable objects with `__repr__` and `__str__`.
- Dataclasses: classes for holding data with far less typing.
- Inheritance, briefly, and when to reach for a class at all.

### Classes and instances

A **class** is a blueprint. An **instance** is one object built from that blueprint. `str` is a class; `"hello"` is an instance of it. Here's a class of your own:

```python
class Counter:
    """Counts how many times something happened."""

    def __init__(self, name):
        self.name = name
        self.count = 0

    def increment(self, by=1):
        self.count += by

    def reset(self):
        self.count = 0


api_calls = Counter("api_calls")
api_calls.increment()
api_calls.increment(by=2)
print(api_calls.name, api_calls.count)  # api_calls 3
```

A few new ideas are packed in here:

- `class Counter:` defines the class. Class names use `CapitalizedWords` by convention.
- `__init__` is a special method that Python calls automatically when you create an instance with `Counter("api_calls")`. Its job is to set up the new object's starting data. (The double underscores mark it as a name with special meaning to Python; people say "dunder init".)
- Functions defined inside a class are called **methods**. `increment` and `reset` are methods.
- **Attributes** are variables attached to an object, such as `self.name` and `self.count`. You read them with a dot: `api_calls.count`.

### Understanding self

`self` is the instance a method is working on. When you write `api_calls.increment(by=2)`, Python actually calls `Counter.increment(api_calls, by=2)`, passing the object in as the first argument. That's why every method's first parameter is `self`, and why you use `self.count` inside methods to reach this particular object's data.

It matters because each instance has its own attributes:

```python
input_tokens = Counter("input_tokens")
output_tokens = Counter("output_tokens")
input_tokens.increment(by=500)
print(input_tokens.count, output_tokens.count)  # 500 0
```

`self` is just a convention, but it's a universal one, so always call it `self`.

### Making objects readable

Print a plain object and you get something unhelpful like `<__main__.Counter object at 0x104f2a3d0>`. Two more special methods fix that. `__repr__` returns a developer-facing description, used in the REPL, in lists and in tracebacks. `__str__` returns a friendly version for `print()` and f-strings:

```python
class Counter:
    def __init__(self, name):
        self.name = name
        self.count = 0

    def __repr__(self):
        return f"Counter(name={self.name!r}, count={self.count})"

    def __str__(self):
        return f"{self.name}: {self.count}"


c = Counter("retries")
print(c)        # retries: 0
print([c])      # [Counter(name='retries', count=0)]
```

If you only write one, write `__repr__`. Python falls back to it when there's no `__str__`.

### Dataclasses

Many classes exist mainly to hold data. Writing `__init__` and `__repr__` by hand for them gets tedious fast. The `dataclasses` module writes them for you:

```python
from dataclasses import dataclass, field, asdict


@dataclass
class Expense:
    description: str
    amount: float
    category: str = "other"
    tags: list[str] = field(default_factory=list)

    def is_large(self):
        return self.amount > 100


coffee = Expense("Coffee", 3.5, "food")
laptop = Expense(description="Laptop", amount=1200.0, category="tech")

print(coffee)            # Expense(description='Coffee', amount=3.5, category='food', tags=[])
print(laptop.is_large()) # True
print(coffee == Expense("Coffee", 3.5, "food"))  # True: compares field by field
print(asdict(coffee))    # {'description': 'Coffee', 'amount': 3.5, 'category': 'food', 'tags': []}
```

The `@dataclass` line is a **decorator**: it takes the class you defined and adds generated methods to it. Each line like `amount: float` declares a **field** with a type annotation. (You'll learn annotations properly in the next lesson, Type Hints.) Fields with defaults must come after fields without them. For a mutable default such as a list, use `field(default_factory=list)` so each instance gets its own list, for the same reason you never use `[]` as a default argument.

`asdict()` turns a dataclass into a plain dict, which you can then pass to `json.dumps()`. Going from a dict back to a dataclass is just `Expense(**data)`, where `**` unpacks the dict into keyword arguments.

If you want instances that can't be changed after creation, use `@dataclass(frozen=True)`. Trying to assign to a field then raises an error, which prevents a whole class of accidental bugs.

<div class="lesson-note lesson-note--tip" markdown="1">

#### A preview of Pydantic

In the Structured Outputs section you'll define classes like `class Expense(BaseModel): description: str; amount: float`. That's Pydantic, and it looks like a dataclass on purpose. The difference is that Pydantic *checks* the data at runtime: hand it `amount="lots"` and it raises a clear error. That's exactly what you need when the data came from a language model.

</div>

### Inheritance, briefly

A class can **inherit** from another class, which means it gets all of the parent's attributes and methods and can add or override some. You already did this in the Errors and Exceptions lesson:

```python
class QuizFileError(Exception):
    """Raised when a quiz file is missing required fields."""
```

`QuizFileError` inherits everything from `Exception`, so it can be raised and caught like any other exception. Inheritance is powerful, but beginners tend to overuse it. Most of the time, a few plain classes and functions are clearer than a deep family tree of classes.

### When to use a class

Reach for a class when several pieces of data belong together and travel together (use a dataclass), or when some data and the operations on it are tightly linked and you want to keep them in one place (use a regular class with methods). Keep using plain functions for operations that just take inputs and return outputs, and plain dicts for one-off data such as a JSON payload you're about to send. Python lets you mix all of these freely, and good Python code usually does.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 8: Object-Oriented Programming](https://cs50.harvard.edu/python/weeks/8/). It builds a `Student` class step by step, covering `__init__`, `__str__`, validating data by raising exceptions, properties, class methods and inheritance.
   - Properties (`@property`) and class methods (`@classmethod`) are useful to recognize, but you won't need them for this section's projects.
1. Read [chapter 9, "Classes", of the official Python tutorial](https://docs.python.org/3/tutorial/classes.html), sections 9.3 ("A First Look at Classes"), 9.4 ("Random Remarks") and 9.5 ("Inheritance").
   - Sections 9.1 and 9.2 on scopes and namespaces are heavier going. Read them if you're curious, or come back later.
1. Read [the dataclasses module docs](https://docs.python.org/3/library/dataclasses.html) up to and including the description of `field()`, and look at the "Mutable default values" section near the end.
1. Practice:
   - Do Cookie Jar from [CS50P Problem Set 8](https://cs50.harvard.edu/python/psets/8/). It asks for a class with methods, properties and validation.
   - Complete "Ellen's Alien Game" on the [Exercism Python track](https://exercism.org/tracks/python), which practices class attributes and methods.
   - In your `mimir-quiz-game` repo, replace the question dicts with a `Question` dataclass that has `question` and `answer` fields and a `check(answer)` method that does the forgiving comparison. Convert each dict you load from JSON into a `Question` with `Question(**data)`. Commit the change.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Python data model reference](https://docs.python.org/3/reference/datamodel.html#special-method-names) lists every special "dunder" method, such as `__len__` and `__eq__`, that lets your objects work with built-in syntax.
