### Introduction

So far your programs run every line, top to bottom, exactly once. Real programs need to make decisions ("if the user typed quit, stop") and repeat work ("ask every question in the quiz"). Those two ideas, **conditionals** and **loops**, are called *control flow*, because they control which lines run and how many times.

Control flow is also the skeleton of every AI agent you will build. Stripped to its core, an agent is a loop: send the conversation to the model, check whether it wants to use a tool, run the tool if so, and repeat until the model says it is done. You will write that loop yourself in the Agentic Systems path. Today you learn the pieces it is made of.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Making decisions with `if`, `elif` and `else`.
- Comparison operators and combining conditions with `and`, `or` and `not`.
- Truthy and falsy values.
- Repeating work with `while` loops.
- Looping over sequences with `for` and `range()`.
- Controlling loops with `break` and `continue`.

### Making decisions

An `if` statement runs a block of code only when its condition is `True`. The block is the indented lines underneath the colon. Python uses indentation (four spaces, by convention) to know which lines belong to the block, so indentation is not decoration; it is part of the syntax.

```python
tokens_used = 1200
limit = 1000

if tokens_used > limit:
    print("Over budget!")
    print("Consider a shorter prompt.")
print("This line always runs.")
```

Add `elif` ("else if") for more cases and `else` for "none of the above". Python checks each condition from the top and runs only the first block whose condition is true:

```python
score = 72

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"
print(grade)  # C
```

The comparison operators are `==` (equal), `!=` (not equal), `<`, `<=`, `>` and `>=`. Combine conditions with `and` (both must be true), `or` (at least one must be true) and `not` (flip true and false):

```python
answer = input("Continue? (y/n) ").strip().lower()

if answer == "y" or answer == "yes":
    print("Continuing.")
elif not answer:
    print("You didn't type anything.")
else:
    print("Stopping.")
```

### Truthy and falsy

That `not answer` line works because Python can treat any value as true or false. The **falsy** values are `False`, `None`, `0`, `0.0`, the empty string `""` and empty collections such as `[]` and `{}`. Everything else is **truthy**. So `if answer:` means "if the user typed something". You will see this style everywhere, for example `if not api_key:` to check that a setting was provided.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Indentation errors

Mixing tabs and spaces, or indenting one line by three spaces and the next by four, gives you `IndentationError`. VS Code inserts four spaces when you press Tab in a Python file, so let it do the work. If a block "isn't running", check that it is indented under the right `if`.

</div>

### While loops

A `while` loop repeats its block as long as its condition stays true. It is the right tool when you do not know in advance how many times you will loop, such as "keep asking until the user gets it right":

```python
secret = 7
guess = None

while guess != secret:
    guess = int(input("Guess a number from 1 to 10: "))
    if guess < secret:
        print("Too low.")
    elif guess > secret:
        print("Too high.")

print("You got it!")
```

Something inside the loop must eventually make the condition false. If nothing does, you have an **infinite loop**. Press `Ctrl+C` in the terminal to stop a program that is stuck.

Sometimes it is clearer to loop "forever" and leave from the middle with `break`:

```python
while True:
    message = input("You: ")
    if message == "quit":
        break
    print(f"Echo: {message}")
```

Look closely at that shape. Replace the `print` line with "send the message to a model and print the reply", and you have the core of the terminal chatbot you will build in the Your First LLM App section.

### For loops

A `for` loop runs its block once for each item in a sequence. A string is a sequence of characters, so you can already loop over one:

```python
for letter in "agent":
    print(letter.upper())
```

To repeat something a fixed number of times, use `range()`. `range(5)` produces `0, 1, 2, 3, 4`: it starts at 0 and stops *before* the number you give it. `range(1, 6)` produces `1` to `5`, and `range(0, 10, 2)` counts by twos.

```python
total = 0
for n in range(1, 6):
    total = total + n
print(total)  # 15
```

That pattern, starting a running total before the loop and updating it inside, is called an **accumulator**. You will use it to add up token costs, count correct quiz answers and total expenses.

Inside any loop, `continue` skips the rest of the current pass and jumps to the next one, while `break` leaves the loop entirely:

```python
for n in range(1, 11):
    if n % 2 == 0:
        continue          # skip even numbers
    if n > 7:
        break             # stop completely after 7
    print(n)              # prints 1, 3, 5, 7
```

### Choosing between while and for

Use `for` when you are walking through a known collection or a known number of steps. Use `while` when you loop until something happens. In practice, `for` is far more common. In the next lessons you will loop over lists of questions, dictionaries of settings and lines of a file, all with `for`.

Python also has a `match` statement for comparing one value against many patterns. You do not need it yet; a chain of `if` and `elif` handles everything in this section.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 1: Conditionals](https://cs50.harvard.edu/python/weeks/1/) for `if`, `elif`, `else`, `and`, `or` and a first look at `match`.
1. Watch [CS50P Lecture 2: Loops](https://cs50.harvard.edu/python/weeks/2/) for `while`, `for`, `range()` and `break`.
   - The second half of this lecture also uses lists and dictionaries. Follow along, but don't worry if they feel new; the Lists, Dicts, Sets and Tuples lesson covers them in depth.
1. Read chapters 2 and 3 of Automate the Boring Stuff: [chapter 2, "if-else and Flow Control"](https://automatetheboringstuff.com/3e/chapter2.html) and [chapter 3, "Loops"](https://automatetheboringstuff.com/3e/chapter3.html).
   - Type in and run the short programs in both chapters, and step through at least one of them with [Python Tutor](https://pythontutor.com/) to watch the loop variable change.
1. Read sections 4.1 to 4.4 of [the official tutorial's "More Control Flow Tools"](https://docs.python.org/3/tutorial/controlflow.html), covering `if`, `for`, `range()`, `break` and `continue`. Section 4.5, on `else` clauses on loops, is optional; the rest of the page is for later lessons.
1. Practice:
   - From [CS50P Problem Set 1](https://cs50.harvard.edu/python/psets/1/), do Deep Thought, Home Federal Savings Bank, File Extensions and Math Interpreter.
   - From [CS50P Problem Set 2](https://cs50.harvard.edu/python/psets/2/), do camelCase, Coke Machine and Just setting up my twttr.
   - On Exercism, complete "Meltdown Mitigation" (conditionals) and "Making the Grade" (loops) from the [Python track](https://exercism.org/tracks/python).

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How does Python decide which branch of an if/elif/else chain runs?](#making-decisions)
- [How do and, or and not combine conditions?](#making-decisions)
- [Which values count as falsy in Python, and how does that let you shorten a condition?](#truthy-and-falsy)
- [How can a while loop run forever, and how do break and continue change a loop's flow?](#while-loops)
- [How do you loop over a list or a range of numbers with for?](#for-loops)
- [When should you choose a while loop over a for loop?](#choosing-between-while-and-for)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The truth value testing section of the Python docs](https://docs.python.org/3/library/stdtypes.html#truth-value-testing) is the official list of falsy values.
- [The tutorial's section on match statements](https://docs.python.org/3/tutorial/controlflow.html#match-statements) shows Python's pattern matching when you are curious.
