### Introduction

Welcome to Python. This is the longest section in Foundations, and it is the one everything else rests on. Every AI app, agent and evaluation script you build later in this curriculum is a Python program. The model does the "thinking", but your Python code builds the prompt, sends the request, reads the reply and decides what to do next.

You start with the smallest building blocks: values, the types those values have, and variables, the names you give them. A prompt is a string. A token count is an integer. A temperature setting is a float. A flag that says whether the model is finished is a boolean. Once you can create, combine and convert these, you can already write small useful programs.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Running Python interactively and as a script with `uv`.
- What variables are and how to name them.
- Integers, floats and arithmetic.
- Strings, f-strings and common string methods.
- Booleans and `None`.
- Checking and converting types, and reading user input.

### Two ways to run Python

Make a practice project for this whole section, the same way you did in the Virtual Environments and uv lesson:

```bash
uv init python-practice
cd python-practice
```

The first way to run Python is the **REPL** (Read-Eval-Print Loop), an interactive prompt that runs each line as soon as you press Enter. Start it with `uv run python`. You will see `>>>`. Type `2 + 3` and press Enter, and Python prints `5`. Leave with `exit()`. The REPL is perfect for quick experiments.

The second way is a **script**: a `.py` file that runs from top to bottom. Create `hello.py` in VS Code:

```python
print("Hello from a script")
```

Run it with `uv run hello.py`. Use scripts for anything you want to keep. In the REPL, Python shows the value of each expression automatically; in a script, nothing appears unless you `print()` it.

### Variables are names for values

A **variable** is a name that points to a value. You create one with `=`, which means "assign", not "equals":

```python
model_name = "claude-haiku-5-5"
max_tokens = 1024
max_tokens = max_tokens * 2   # take the old value, double it, store it back
print(model_name, max_tokens)  # claude-haiku-5-5 2048
```

Python reads the right side first, works out its value, then attaches the name on the left to that value. That is why `max_tokens = max_tokens * 2` is fine.

Naming rules: names can contain letters, digits and underscores, cannot start with a digit, and are case sensitive (`Score` and `score` are different). By convention, Python uses `snake_case`: lowercase words joined by underscores. Pick names that say what the value means. `user_question` is far better than `x` when you reread your code next week.

### Numbers

Python has two everyday number types. An **int** (integer) is a whole number such as `42` or `-7`. A **float** (floating-point number) has a decimal point, such as `0.7` or `3.0`.

```python
print(7 + 2)    # 9
print(7 - 2)    # 5
print(7 * 2)    # 14
print(7 / 2)    # 3.5   (/ always gives a float)
print(7 // 2)   # 3     (floor division: drop the remainder)
print(7 % 2)    # 1     (modulo: just the remainder)
print(2 ** 10)  # 1024  (exponent)
```

Floats are stored in binary, so some decimals cannot be represented exactly:

```python
print(0.1 + 0.2)            # 0.30000000000000004
print(round(0.1 + 0.2, 2))  # 0.3
```

This is not a Python bug; almost every language does it. When you display a float, round it. When you need exact money values later, you can count in cents with ints.

### Strings

A **string** (`str`) is text wrapped in quotes. Single and double quotes both work; triple quotes (`"""`) let a string span several lines, which you will use constantly for prompts.

The most useful string feature is the **f-string**. Put `f` before the opening quote, and anything inside `{}` is evaluated and inserted:

```python
name = "Ada"
topic = "recursion"
prompt = f"""You are a patient tutor.
Explain {topic} to {name} in three sentences."""
print(prompt)
```

That is exactly how you will build prompts from data later. A few more things worth knowing:

```python
text = "  Hello, World  "
print(text.strip())          # "Hello, World"  (remove surrounding whitespace)
print(text.lower())          # "  hello, world  "
print(text.replace("World", "Python"))
print("World" in text)       # True
print(len("Hello"))          # 5 characters

word = "Python"
print(word[0])     # "P"  (indexes start at 0)
print(word[-1])    # "n"  (negative indexes count from the end)
print(word[0:3])   # "Pyt" (a slice: start up to, but not including, the end)
```

Strings are **immutable**: methods such as `.lower()` return a new string and leave the original unchanged. If you want to keep the result, assign it: `text = text.strip()`.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Read your error messages

When something breaks, Python prints an error. Read the last line first. `NameError: name 'promt' is not defined` tells you exactly what went wrong: a typo. You will learn to read full error reports in the Errors and Exceptions lesson, but the habit of reading the last line starts today.

</div>

### Booleans and None

A **boolean** (`bool`) is either `True` or `False`. You usually get one by comparing things:

```python
tokens_used = 900
limit = 1000
print(tokens_used < limit)    # True
print(tokens_used == limit)   # False  (== compares, = assigns)
print(tokens_used != limit)   # True
```

`None` is Python's way of saying "no value here yet". A function that has nothing to return gives back `None`, and you will often start a variable as `None` until something fills it in, such as `reply = None` before a model has answered.

### Checking and converting types

Every value has a type, and `type()` tells you what it is:

```python
print(type(42))       # <class 'int'>
print(type("42"))     # <class 'str'>
print(type(4.2))      # <class 'float'>
print(type(None))     # <class 'NoneType'>
```

`42` and `"42"` look alike but behave differently: `"42" + "1"` is `"421"`, while `42 + 1` is `43`. Mixing them, as in `"42" + 1`, raises a `TypeError`. Convert explicitly with `int()`, `float()`, `str()` and `bool()`.

This matters most with `input()`, which pauses the program, waits for the user to type something and press Enter, and **always** returns a string:

```python
age_text = input("How old are you? ")
age = int(age_text)
print(f"Next year you will be {age + 1}.")
```

If the user types `twelve`, `int()` raises a `ValueError`. For now that is fine; in the Errors and Exceptions lesson you will learn to handle it gracefully. The same idea shows up all over AI work: a model's reply always arrives as text, and your code has to turn it into the numbers, booleans or structures you actually need.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 0: Functions, Variables](https://cs50.harvard.edu/python/weeks/0/) from Harvard's free Introduction to Programming with Python. David Malan explains strings, ints, floats and `input()` slowly and clearly.
   - Watch the whole lecture. It also introduces writing your own functions; treat that part as a preview of the Functions lesson.
   - The course uses its own online editor. You can follow along in VS Code instead and run files with `uv run`.
1. Read [chapter 1, "Python Basics", of Automate the Boring Stuff with Python](https://automatetheboringstuff.com/3e/chapter1.html), which is free online. It covers expressions, data types, variables and your first full program.
   - Type every example yourself rather than copying it. Typing is how the syntax sticks.
1. Read sections 3.1.1 to 3.1.3 of [the official Python tutorial's informal introduction](https://docs.python.org/3/tutorial/introduction.html) (numbers, text and lists). This is the source the rest of the community refers to, so get comfortable with its style.
   - You can skim the part on lists; you will cover them properly in the Lists, Dicts, Sets and Tuples lesson.
1. Do [CS50P Problem Set 0](https://cs50.harvard.edu/python/psets/0/): Indoor Voice, Playback Speed, Making Faces and Einstein.
   - Skip Tip Calculator for now; you will do it in the Functions lesson.
   - Submitting through CS50's tools is optional. Writing and running the programs in your `python-practice` project is what counts.
1. Join the [Exercism Python track](https://exercism.org/tracks/python) (free) and complete the "Guido's Gorgeous Lasagna", "Ghost Gobble Arcade Game" and "Little Sister's Vocabulary" exercises. Exercism runs tests on your solution, and you can request free feedback from a human mentor.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between running Python interactively and running a script with uv?](#two-ways-to-run-python)
- [What does it mean that a variable is a name for a value?](#variables-are-names-for-values)
- [What do // and % do, and why doesn't 0.1 + 0.2 print exactly 0.3?](#numbers)
- [Why are f-strings usually the clearest way to build text from values?](#strings)
- [What is None, and how is it different from False or 0?](#booleans-and-none)
- [Why does input() always give you a string, and how do you turn it into a number?](#checking-and-converting-types)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Python Tutor](https://pythontutor.com/) visualizes your code step by step, showing which value each variable points to. It is excellent when assignment feels confusing.
- [The Python tutorial's page on floating-point arithmetic](https://docs.python.org/3/tutorial/floatingpoint.html) explains why `0.1 + 0.2` is not exactly `0.3`.
- [The string methods reference](https://docs.python.org/3/library/stdtypes.html#string-methods) lists every method you can call on a string.
