### Introduction

You have been calling functions since your first line of Python: `print()`, `input()`, `len()` and `int()` are all functions somebody else wrote. In this lesson you write your own.

A **function** is a named, reusable block of code. You give it some inputs, it does one job, and it hands back a result. Functions let you break a big problem into small pieces you can understand, reuse and test one at a time.

Functions matter even more in AI engineering than in ordinary programming. When you give a model "tools" later in this curriculum, each tool is a Python function: it has a name, a description of what it does and a list of parameters with types. The model decides *when* to call it, and your code runs it. Writing small, clear functions with good names and docstrings is practice for writing good tools.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Defining functions with `def` and calling them.
- Parameters, arguments, defaults and keyword arguments.
- The difference between `return` and `print()`.
- Scope: where a variable can be seen.
- Docstrings and naming functions well.
- Structuring a script with a `main()` function.

### Defining and calling a function

Use `def`, a name, parentheses with any **parameters** (the input names), and a colon. The indented block below is the function's body:

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Ada")
print(message)  # Hello, Ada!
```

Defining a function does not run it. The body runs only when you **call** the function by writing its name followed by parentheses. The value you pass in, `"Ada"`, is called an **argument**. Inside the function, the parameter `name` refers to that argument.

### Return versus print

This is the single most common beginner confusion, so slow down here. `print()` shows something on the screen. `return` hands a value back to whoever called the function, so they can store it, combine it or pass it on.

```python
def add_print(a, b):
    print(a + b)

def add_return(a, b):
    return a + b

x = add_print(2, 3)   # shows 5 on screen
print(x)              # None: add_print didn't return anything

y = add_return(2, 3)  # shows nothing
print(y * 10)         # 50: we can use the result
```

A function without a `return` statement returns `None`. As a rule, functions that *compute* something should `return` it and leave printing to the code that calls them. That makes them reusable (you can print the result, save it to a file or send it to a model) and testable (a test can check the returned value, as you will see in the Testing with pytest lesson).

`return` also ends the function immediately. Any lines after it in the same block never run.

### Parameters with defaults and keyword arguments

Parameters can have **default values**, which are used when the caller leaves that argument out:

```python
def build_prompt(question, tone="friendly", max_sentences=3):
    return (
        f"Answer in a {tone} tone, in at most {max_sentences} sentences.\n"
        f"Question: {question}"
    )

print(build_prompt("What is a token?"))
print(build_prompt("What is a token?", tone="formal"))
print(build_prompt("What is a token?", max_sentences=1, tone="playful"))
```

The last two calls use **keyword arguments**: you name the parameter when you pass the value. Keyword arguments make calls readable and let you skip or reorder optional parameters. You will see them all over AI SDKs. A typical model call looks like `client.messages.create(model=..., max_tokens=..., messages=...)`, which is just a function call with keyword arguments. That example is Anthropic's SDK; OpenAI's looks like `client.chat.completions.create(model=..., messages=...)`, the same idea with different names.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Never use a list or dict as a default

Write `def add_item(item, items=None):` and then `if items is None: items = []` inside the body, instead of `def add_item(item, items=[]):`. Python creates a default value once, when the function is defined, so a default list is shared between every call and quietly grows. The Lists, Dicts, Sets and Tuples lesson explains why.

</div>

### Scope

Variables created inside a function are **local**: they exist only while the function runs, and code outside cannot see them.

```python
def double(n):
    result = n * 2
    return result

print(double(4))   # 8
print(result)      # NameError: name 'result' is not defined
```

A function *can* read variables defined at the top level of the file (global variables), but relying on that makes code hard to follow. Pass in what a function needs as arguments and return what it produces. A function whose output depends only on its inputs, and which changes nothing outside itself, is called a **pure function**. Pure functions are the easiest code in the world to test and reason about, so aim for them whenever you can.

### Docstrings and good names

A **docstring** is a string placed as the first line of a function's body. It explains what the function does, and tools such as VS Code show it when you hover over a call:

```python
def estimate_cost(input_tokens, output_tokens, price_in, price_out):
    """Return the cost in dollars of one model call.

    Prices are in dollars per million tokens.
    """
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000
```

Name functions with a verb that says what they do: `estimate_cost`, `load_questions`, `is_valid_email`. A function should do one thing. If you need the word "and" to describe it, consider splitting it into two.

Later in the curriculum this habit pays off directly: when you describe a tool to a model, the function's name and docstring become the tool's name and description, and a vague description leads the model to misuse the tool.

### Structuring a script with main

As your programs grow, put the top-level logic in a function called `main()` and call it at the bottom of the file:

```python
def ask_number(prompt):
    return int(input(prompt))


def main():
    a = ask_number("First number: ")
    b = ask_number("Second number: ")
    print(f"The sum is {a + b}.")


if __name__ == "__main__":
    main()
```

The `if __name__ == "__main__":` line means "only call `main()` when this file is run directly". It will make sense in the Modules and Packages lesson, when you import functions from one file into another. For now, treat it as the standard way to end a script.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Rewatch the second half of [CS50P Lecture 0](https://cs50.harvard.edu/python/weeks/0/), where David Malan defines his own functions, `main()`, default parameters and return values. It will make much more sense now.
1. Read [chapter 4, "Functions", of Automate the Boring Stuff](https://automatetheboringstuff.com/3e/chapter4.html). Pay special attention to the sections on return values, `None`, the call stack and local and global scope.
1. Read sections 4.8 and 4.9 of [the official tutorial's "More Control Flow Tools"](https://docs.python.org/3/tutorial/controlflow.html), "Defining Functions" and "More on Defining Functions".
   - Read 4.9.1 (default argument values) and 4.9.2 (keyword arguments) carefully, including the warning about mutable defaults.
   - Skim the rest of 4.9 (special parameters, arbitrary argument lists, lambdas). You'll see `*args` and `**kwargs` in other people's code; it's enough to recognize them.
1. Practice:
   - Do Tip Calculator from [CS50P Problem Set 0](https://cs50.harvard.edu/python/psets/0/) and Meal Time from [CS50P Problem Set 1](https://cs50.harvard.edu/python/psets/1/). Both ask you to fill in specific functions.
   - Do Vanity Plates from [CS50P Problem Set 2](https://cs50.harvard.edu/python/psets/2/), which rewards splitting the rules into small helper functions.
   - Go back to one program you wrote in the previous two lessons and restructure it: move the logic into functions that `return` values, and add a `main()`.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between a function returning a value and printing it?](#return-versus-print)
- [How do default values and keyword arguments make a function easier to call?](#parameters-with-defaults-and-keyword-arguments)
- [Why should you never use a list or dict as a default parameter value?](#parameters-with-defaults-and-keyword-arguments)
- [Can code outside a function see a variable created inside it? Why or why not?](#scope)
- [What should a docstring tell the reader, and what makes a good function name?](#docstrings-and-good-names)
- [Why structure a script around a main() function?](#structuring-a-script-with-main)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The built-in functions reference](https://docs.python.org/3/library/functions.html) lists every function Python gives you for free, such as `len()`, `round()`, `sum()`, `min()` and `max()`. Skim it so you don't rewrite one by accident.
- [PEP 8, the Python style guide](https://peps.python.org/pep-0008/), sets the naming and layout conventions most Python code follows.
