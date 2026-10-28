### Introduction

You'll spend more of your programming life finding out why code doesn't work than writing new code. That's true for beginners and for senior engineers, and it's even more true when you build with language models, where a bug might be in your code, in your prompt, in the data, or in what the model decided to do. The difference between a frustrating afternoon and a ten-minute fix is usually not intelligence. It's method.

This lesson gives you that method. First, tools to see inside a running program: the VS Code debugger and Python's built-in `pdb`. Then techniques for narrowing a bug down: minimal reproductions, bisecting and explaining the problem out loud. Finally, **logging**, which records what your program did so that when something goes wrong at 3 a.m., or in the middle of a 200-step agent run, you can read what happened instead of guessing.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- A repeatable process for debugging.
- Using the VS Code debugger: breakpoints, stepping and inspecting variables.
- Pausing a program from code with `breakpoint()` and `pdb`.
- Shrinking a bug to a minimal reproduction, and bisecting to find where it starts.
- Rubber duck debugging.
- The `logging` module: levels, formats, and writing logs to a file.

### A debugging process

When code misbehaves, resist the urge to start changing things at random. Work through these steps instead:

1. **Read the error.** If there's a traceback, read it from the bottom up, as you learned in Errors and Exceptions: the last line says *what* went wrong, and the lines above it say *where*, ending with the line that actually failed. Find the lowest frame that's in your own code rather than in a library; that's usually where to look.
1. **Reproduce it reliably.** Find the exact input or steps that trigger the bug every time. A bug you can trigger on demand is half solved.
1. **Form a guess, then check it.** "I think `total` is zero here." Don't change code to test the guess yet; *look* at what the program is doing, with a debugger or a print.
1. **Fix one thing, then rerun.** If the fix works, add a test that would have caught the bug, so it can't come back quietly.

The middle step is where most time goes. There are two ways to look inside a program: add `print()` calls, or use a debugger. Printing is fine for a quick check. But each question costs you an edit and a rerun, and you have to remember to delete the prints afterward. A debugger lets you ask as many questions as you like in one run.

### The VS Code debugger

Save this buggy script as `stats.py`. It's meant to print the average reply length per model:

```python
def average_lengths(replies):
    totals = {}
    counts = {}
    for reply in replies:
        model = reply["model"]
        totals[model] = totals.get(model, 0) + len(reply["text"])
        counts[model] = counts.get(model, 0) + 1
    return {model: totals[model] / counts[model] for model in totals}


replies = [
    {"model": "cheap", "text": "Paris."},
    {"model": "capable", "text": "The capital of France is Paris."},
    {"model": "cheap", "text": ""},
    {"model": "Capable", "text": "Paris, of course."},
]
print(average_lengths(replies))
```

It runs without an error, but the output has three models instead of two. Let's watch it happen.

1. Open the file in VS Code and click in the margin to the left of the line `model = reply["model"]`. A red dot appears. That's a **breakpoint**: the program will pause just before running that line.
1. Press <kbd>F5</kbd> (or open the **Run and Debug** view and choose **Python Debugger: Debug Python File**). The program starts and stops at your breakpoint, with the line highlighted.
1. Look at the **Variables** panel on the left. It shows every variable in scope, including `reply`, `totals` and `counts`, with their current values. Expand dicts and lists by clicking them.
1. Use the toolbar at the top: **Continue** (<kbd>F5</kbd>) runs to the next breakpoint, **Step Over** (<kbd>F10</kbd>) runs the current line and stops at the next, and **Step Into** (<kbd>F11</kbd>) goes inside a function call on the current line.
1. Press Continue a few times and watch `totals` grow. On the fourth pass, `reply["model"]` is `"Capable"` with a capital C, and a new key appears. Found it.

Two more tools save time. In the **Debug Console** at the bottom you can type any Python expression, such as `reply["model"].lower()`, and see its value while the program is paused. And you can right-click a breakpoint to make it **conditional**, such as `reply["model"] not in ("cheap", "capable")`, so it pauses only on the interesting loop pass instead of all thousand.

The fix here is to normalize the name with `.lower()`. But the more useful question is *why* the data was inconsistent, because the same mistake is probably lurking somewhere else.

### Pausing from code with breakpoint

Sometimes you're not in VS Code: you're in a terminal, or on a remote server. Python has a debugger built in, called **pdb**. Put a call to `breakpoint()` on the line where you want to stop:

```python
for reply in replies:
    breakpoint()
    model = reply["model"]
```

Run the script normally with `uv run stats.py`, and when it reaches that line you get a `(Pdb)` prompt. The commands you need are:

| Command | Does |
| --- | --- |
| `p expression` | print a value, such as `p reply` or `p len(totals)` |
| `n` | run the next line (step over) |
| `s` | step into a function call |
| `c` | continue until the next breakpoint |
| `l` | list the code around the current line |
| `w` | show where you are (the call stack) |
| `q` | quit |

`pdb` is less pretty than VS Code but works everywhere. Remember to delete the `breakpoint()` line when you're done. A forgotten one will freeze your program in production waiting for someone to type a command. The linter you'll set up in Linting, Formatting and CI can catch leftovers for you.

### Minimal reproductions and bisecting

Real bugs hide in big programs. The most powerful debugging technique is to make the program smaller until the bug has nowhere to hide. A **minimal reproduction** (or "repro") is the shortest code and smallest input that still shows the bug. Make one by repeatedly deleting things: a function that's not involved, half the input data, the API call (replace it with a hard-coded reply). After each cut, check the bug is still there. If it disappears, the part you just removed was involved, so put it back and cut something else.

Very often, you'll find the bug while making the repro. If you don't, you now have something small enough to ask about clearly. Asking for Help described why people answer questions with a minimal example and ignore questions with 300 lines of code.

**Bisecting** is the same idea applied to a search. If a 1,000-line input file crashes your program, try the first 500 lines. If those crash, try the first 250; if not, try the second 500. Halving each time, you find the one bad line in about ten tries. The same works across history: if your code worked last week and doesn't today, check out a commit from the middle of the week and test it. Git even automates this with `git bisect`, which walks you through the halving and tells you which commit introduced the bug.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Explain it to a rubber duck

**Rubber duck debugging** means explaining your code, line by line, out loud, to someone who knows nothing: a colleague, a pet, or a literal rubber duck. It works because explaining forces you to say what each line *actually* does rather than what you assume it does, and the gap between the two is where the bug is. Explaining a problem to an AI assistant often works the same way, sometimes before you hit Enter.

</div>

### Logging instead of printing

Debuggers help while you're watching. **Logging** helps when you aren't: it records what the program did as it ran, so you can read it afterward. You could use `print()`, but Python's built-in `logging` module is much better. Every message has a **level** that says how serious it is, and you choose at startup which levels to show and where to send them, without touching the rest of the code.

| Level | Use it for |
| --- | --- |
| `DEBUG` | detailed information for diagnosing problems: full prompts, raw responses |
| `INFO` | normal events worth recording: "loaded 40 questions", "request took 1.8s" |
| `WARNING` | something unexpected that the program handled: a retry, a missing optional setting |
| `ERROR` | something failed: a request gave up after all retries |
| `CRITICAL` | the program can't continue |

Here's a small program that logs to both the terminal and a file:

```python
import logging
import random
import time

logger = logging.getLogger("quiz")   # one named logger per program or module


def setup_logging(verbose=False):
    console = logging.StreamHandler()                    # to the terminal (stderr)
    console.setLevel(logging.DEBUG if verbose else logging.INFO)

    file = logging.FileHandler("app.log", encoding="utf-8")
    file.setLevel(logging.DEBUG)                         # the file keeps everything

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[console, file],
    )


def fake_model_call(question):
    if random.random() < 0.3:
        raise TimeoutError("model took too long")
    time.sleep(0.1)
    return "Paris"


def ask(question):
    for attempt in range(1, 4):
        logger.debug("attempt %d for question %r", attempt, question)
        try:
            answer = fake_model_call(question)
        except TimeoutError:
            logger.warning("timeout on attempt %d, retrying", attempt)
            continue
        logger.info("answered %r in %d attempt(s)", question, attempt)
        return answer
    logger.error("gave up on %r after 3 attempts", question)
    return None


setup_logging(verbose=False)
for q in ["Capital of France?", "Capital of Peru?", "Capital of Japan?"]:
    ask(q)
```

Run it a few times. The terminal shows `INFO` and above, while `app.log` also contains every `DEBUG` line, with a timestamp. Set `verbose=True` to see debug messages in the terminal too. That's the big advantage over `print()`: you leave the detailed logging in your code permanently, and turn it up only when you need it.

A few details to notice:

- A **handler** decides where messages go. `StreamHandler` writes to the terminal and `FileHandler` to a file. Each can have its own level.
- The **format** string adds the time, level and logger name to every line, so a log file can be searched and sorted.
- Messages use `%s`-style placeholders with the values passed separately, as in `logger.info("took %d ms", ms)`. The logging module only builds the string if the message will actually be shown, which matters for debug messages in hot loops.
- Inside an `except` block, `logger.exception("request failed")` logs at `ERROR` level and includes the full traceback.
- Call `basicConfig` once, at the start of your program. Library code should only create loggers with `logging.getLogger(__name__)` and never configure handlers, so the application stays in charge.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Never log secrets

Log files get copied, shared and uploaded. Never log API keys, passwords or full authorization headers, and think twice before logging users' personal data. If you need to log a request, log the model, token counts and timings, not the key.

</div>

Later in the curriculum, this habit grows into **tracing**: recording every model call, its inputs, outputs, tokens and timing, so you can debug and evaluate LLM systems. It starts with knowing what your program did, here.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Python debugging in VS Code](https://code.visualstudio.com/docs/python/debugging), the official guide. Read from the start through "Set configuration options" to learn how to start a session; skim the long list of configuration options.
   - Then read the "Breakpoints" and "Data inspection" sections of the general [Debug code with Visual Studio Code](https://code.visualstudio.com/docs/debugtest/debugging) page, which cover conditional breakpoints, logpoints and watch expressions.
1. Read the [Basic Logging Tutorial](https://docs.python.org/3/howto/logging.html) in the Python docs, through "Logging variable data" and "Changing the format of displayed messages". Skim the "Advanced Logging Tutorial" for the idea of loggers, handlers and formatters.
1. Read [How to create a Minimal, Reproducible Example](https://stackoverflow.com/help/minimal-reproducible-example) from Stack Overflow. It's written for people asking questions, but the same steps are how you'd shrink a bug for yourself.
1. Do the [debugging exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/debugging). Each exercise has a bug and failing tests. Use the VS Code debugger or `breakpoint()` to find each bug before you fix it, and write down in a sentence what the bug was. Run the tests with `uv run pytest exercises/debugging/<exercise>`.
1. Add logging to your `mimir-quiz-game` project:
   - Configure logging once in `main()`, with an `INFO` handler for the terminal and a `DEBUG` handler that writes to `quiz.log`. Add `quiz.log` to `.gitignore`.
   - Log at least one message at each of `DEBUG`, `INFO` and `WARNING`, such as the questions file loaded, each answer and its result, and a skipped malformed question.
   - Replace any debugging `print()` calls with log calls. Keep the prints that are the game's real output.
   - Commit, and paste a few lines of `quiz.log` into your README.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the four steps of a debugging process?](#a-debugging-process)
- [What's the difference between Step Over and Step Into, and what's a conditional breakpoint for?](#the-vs-code-debugger)
- [What does breakpoint() do, and which pdb command prints a value?](#pausing-from-code-with-breakpoint)
- [How do you make a minimal reproduction, and how does bisecting find a bad line quickly?](#minimal-reproductions-and-bisecting)
- [What are the five logging levels, and why is logging better than print for diagnostics?](#logging-instead-of-printing)
- [What does a logging handler do, and why should you never log an API key?](#logging-instead-of-printing)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The pdb docs](https://docs.python.org/3/library/pdb.html) list every debugger command, including `until` and `return` for leaving loops and functions quickly.
- [The logging module reference](https://docs.python.org/3/library/logging.html) lists every format attribute you can put in a log line, such as `%(funcName)s` and `%(lineno)d`.
- [A debugging manifesto](https://jvns.ca/blog/2022/12/08/a-debugging-manifesto/) by Julia Evans is a short list of attitudes that make debugging easier, such as "trust nobody and nothing".
- [Rubber Duck Debugging](https://rubberduckdebugging.com/) explains the technique in one page.
