### Introduction

Most of your programs so far have asked for what they need with `input()`, or had their settings typed straight into the code. That's fine for a game you play once, but it's not how real tools work. Real tools, like `git`, `uv` and `curl`, take their instructions on the command line: `git commit -m "Fix bug"`, `uv add --dev pytest`, `curl -s https://example.com`. You can run them from a script, repeat them from your shell history, and chain them together, and none of that works when a program stops to ask questions.

In this lesson you'll build command-line apps the professional way. You'll use `argparse`, the standard library module that turns command-line text into Python values and writes a `--help` page for you. You'll learn to work with dates and times using `datetime`, which nearly every real tool needs, whether it's logging when something happened or filtering "everything from last week". And you'll learn to report success or failure through **exit codes**, so other programs and scripts can tell whether yours worked.

This matters for AI work more than it might seem. Evaluation scripts, data-cleaning jobs and agent runners are almost always command-line programs: `uv run evals.py --model cheap --limit 50`. Coding agents also drive your tools through the terminal, and they rely on clear `--help` text and honest exit codes to know whether a command succeeded.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What arguments, options and flags are, and how they reach your program through `sys.argv`.
- Building a command-line interface with `argparse`: positional arguments, options, types, defaults, choices and flags.
- Grouping commands with subcommands.
- Working with `date`, `datetime` and `timedelta`, and converting them to and from text.
- Why time zones matter, and how to get an "aware" datetime.
- Exit codes, standard error and `sys.exit`.
- Structuring a CLI so its logic is easy to test.

### Arguments, options and flags

When you run a command, the shell splits what you typed into words and hands them to the program. Take this command:

```text
uv run countdown.py 2026-12-25 --weeks
```

Everything after the script name is an **argument**. People usually distinguish three kinds:

- A **positional argument** is identified by its position, such as `2026-12-25` here. It's usually required.
- An **option** starts with `-` or `--` and takes a value, such as `--limit 50` or `--model cheap`. It's usually optional and has a default.
- A **flag** is an option with no value. It's either there or not, such as `--weeks` or `--verbose`.

Python gives you the raw words in `sys.argv`, a list of strings whose first item is the script's name:

```python
import sys

print(sys.argv)
```

Running `uv run show_args.py 2026-12-25 --weeks` prints `['show_args.py', '2026-12-25', '--weeks']`. You could write your program around that list, but you'd quickly end up handling every detail yourself. What if the user puts `--weeks` first? What if they forget the date, or type `--wekes`? What should `--help` print? Every one of those cases is an `if` statement you'd have to write and get right. `argparse` handles all of them for you.

### Your first argparse parser

Here's a complete tool that counts the days until a date. Save it as `countdown.py` and run it:

```python
import argparse
from datetime import date


def build_parser():
    parser = argparse.ArgumentParser(
        prog="countdown",
        description="Count the days until a date.",
    )
    parser.add_argument(
        "target",                        # positional: no dashes, required
        type=date.fromisoformat,         # turn "2026-12-25" into a date object
        help="the date to count down to, as YYYY-MM-DD",
    )
    parser.add_argument(
        "--since",                       # option: takes a value, optional
        type=date.fromisoformat,
        default=date.today(),
        help="count from this date instead of today",
    )
    parser.add_argument(
        "--weeks",
        action="store_true",             # flag: True if present, False if not
        help="show the result in weeks and days",
    )
    return parser


def main():
    args = build_parser().parse_args()   # reads sys.argv for you
    days = (args.target - args.since).days
    if args.weeks:
        print(f"{days // 7} weeks and {days % 7} days")
    else:
        print(f"{days} days")


if __name__ == "__main__":
    main()
```

`parse_args()` reads `sys.argv`, checks it against the arguments you described, and returns an object with one attribute per argument: `args.target`, `args.since` and `args.weeks`. Option names lose their leading dashes, and a dash inside a name becomes an underscore, so `--dry-run` becomes `args.dry_run`.

Look at what you got for free. Run `uv run countdown.py --help`:

```text
usage: countdown [-h] [--since SINCE] [--weeks] target

Count the days until a date.

positional arguments:
  target         the date to count down to, as YYYY-MM-DD

options:
  -h, --help     show this help message and exit
  --since SINCE  count from this date instead of today
  --weeks        show the result in weeks and days
```

Now try some mistakes. Leaving out the date prints `error: the following arguments are required: target`. Typing `2026-13-01` prints `error: argument target: invalid fromisoformat value: '2026-13-01'`, because `type=` can be any function that takes a string. If it raises `ValueError`, argparse turns that into a friendly usage error instead of a traceback. The common types are `type=int`, `type=float` and `type=Path` (from `pathlib`), and you can pass your own function too.

A few more `add_argument` settings you'll use constantly:

- `choices=["cheap", "capable"]` rejects any other value and lists the valid ones in the error.
- `default=10` sets the value when the option is missing. Without a default, a missing option is `None`.
- `nargs="+"` accepts one or more values and gives you a list, as in `weather Lagos Oslo Lima`. `nargs="*"` accepts zero or more.
- `required=True` makes an option mandatory, though if something is always required it's usually clearer as a positional argument.
- Short names: `parser.add_argument("-v", "--verbose", action="store_true")` accepts both `-v` and `--verbose`.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Write the help text first

Before writing any logic, write the `add_argument` calls with good `help=` strings and run `--help`. Reading your own help page is the fastest way to spot a confusing interface, such as an option nobody would guess the name of, or a positional argument that should really be optional.

</div>

### Subcommands

Bigger tools group their features into **subcommands**: `git commit`, `git push` and `git log` are one program with three subcommands, each with its own arguments. `argparse` supports this with `add_subparsers`. This is the shape you'll want for the Project: Expense Tracker:

```python
import argparse


def build_parser():
    parser = argparse.ArgumentParser(prog="expenses")
    subcommands = parser.add_subparsers(dest="command", required=True)

    add = subcommands.add_parser("add", help="record an expense")
    add.add_argument("amount", type=float)
    add.add_argument("category")
    add.add_argument("description")

    listing = subcommands.add_parser("list", help="show all expenses")
    listing.add_argument("--category", help="only show this category")

    return parser


args = build_parser().parse_args()
if args.command == "add":
    print(f"Adding {args.amount:.2f} to {args.category}: {args.description}")
elif args.command == "list":
    print(f"Listing expenses (category filter: {args.category})")
```

`dest="command"` stores which subcommand was chosen in `args.command`, and `required=True` makes running the program with no subcommand an error. Each subparser gets its own `--help`, so `uv run expenses.py add --help` explains only the `add` arguments.

### Dates and times

The `datetime` module has three types you'll use all the time:

- `date` is a calendar day: year, month and day.
- `datetime` is a date plus a time of day, down to microseconds.
- `timedelta` is a length of time, such as 3 days or 90 minutes. Subtracting one date or datetime from another gives you a `timedelta`, and adding a `timedelta` moves a date forward or back.

```python
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

today = date.today()
print(today.isoformat())                       # '2026-10-28'
print(today + timedelta(days=30))              # 30 days from now
print(date(2026, 12, 25) - today)              # e.g. '58 days, 0:00:00'
print((date(2026, 12, 25) - today).days)       # just the number: 58

deadline = date.fromisoformat("2026-11-15")    # text -> date
print(deadline.strftime("%A %d %B %Y"))        # 'Sunday 15 November 2026'
print(deadline > today)                        # dates compare like numbers

now = datetime.now(timezone.utc)               # an "aware" datetime in UTC
print(now.isoformat(timespec="seconds"))       # '2026-10-28T14:03:12+00:00'
print(now.astimezone(ZoneInfo("Africa/Lagos")))  # same moment, Lagos clock

last_week = now - timedelta(weeks=1)
logged_at = datetime.fromisoformat("2026-10-25T09:30:00+00:00")  # text -> datetime
print(logged_at > last_week)                   # True: within the last 7 days
```

Two kinds of conversion matter most. **ISO 8601** is the international standard format, `2026-10-28` for dates and `2026-10-28T14:03:12+00:00` for datetimes. Use `isoformat()` and `fromisoformat()` whenever you store dates in files, CSV, JSON or a database: the format is unambiguous, and ISO strings even sort correctly as plain text. For showing dates to people, use `strftime()` (string *format* time) with format codes such as `%Y` for the four-digit year, `%m` for the month number, `%d` for the day and `%A` for the weekday name. Its opposite, `datetime.strptime(text, format)` (string *parse* time), reads dates in other formats, like `datetime.strptime("28/10/2026", "%d/%m/%Y")`.

### Time zones

A `datetime` without time zone information is called **naive**. `datetime.now()` returns one: it's your computer's local time, with nothing in it saying which time zone that is. A `datetime` that carries its time zone is **aware**. Naive datetimes cause real bugs. A server in Virginia and a laptop in Lagos will record different "now" values for the same moment, and Python refuses to compare a naive datetime with an aware one, raising `TypeError: can't compare offset-naive and offset-aware datetimes`.

The rule that avoids nearly all of this: **store and compute in UTC, convert to local time only for display.** UTC (Coordinated Universal Time) is the world's reference clock, which never shifts for daylight saving time. Get the current time with `datetime.now(timezone.utc)`, and when you need a person's local time, convert with `astimezone(ZoneInfo("Europe/Oslo"))`. `ZoneInfo` uses the standard time zone names from the IANA database, such as `America/New_York` and `Asia/Kolkata`.

<div class="lesson-note lesson-note--warning" markdown="1">

#### ZoneInfo on Windows

`zoneinfo` reads time zone data from your operating system. Windows doesn't ship that data in the form Python expects, so if `ZoneInfo("Africa/Lagos")` raises `ZoneInfoNotFoundError`, run `uv add tzdata` to install it as a package.

</div>

Plain `date` objects have no time zone, and that's fine: "the expense happened on October 28" is a calendar fact, not a moment in time. Reach for aware datetimes when you're recording *when something happened*, such as a log line, an API call or a model response.

### Exit codes and standard error

In Shell Scripting and Your Environment you met **exit codes**: every program ends by returning a number, `0` for success and anything else for failure, which you can check with `echo $?`. Shell scripts, `&&` chains and, as you'll see in the Linting, Formatting and CI lesson, automated test servers all rely on it. `uv run pytest && git push` only pushes if the tests passed, because pytest exits with a non-zero code when any test fails.

Python sets the exit code for you in two cases. A program that finishes normally exits with `0`, and one that crashes with an uncaught exception exits with `1`. argparse adds a third: a usage error exits with `2`, the traditional code for "you called this wrong". To choose the code yourself, use `sys.exit(code)`. You'll also want to send error messages to **standard error** (stderr), the separate output stream for errors, with `print(..., file=sys.stderr)`. That way, if someone redirects your output to a file with `>`, the errors still appear on their screen instead of being hidden in the file.

Here's the countdown tool rewritten with both, plus a structure that makes it easy to test:

```python
import argparse
import sys
from datetime import date


def days_between(start, end):
    """Pure logic: no printing, no argparse, easy to test."""
    return (end - start).days


def main(argv=None):
    parser = argparse.ArgumentParser(prog="countdown")
    parser.add_argument("target", type=date.fromisoformat)
    parser.add_argument("--since", type=date.fromisoformat, default=date.today())
    args = parser.parse_args(argv)       # None means "use sys.argv"

    days = days_between(args.since, args.target)
    if days < 0:
        print(f"error: {args.target} is in the past", file=sys.stderr)
        return 1                         # failure
    print(f"{days} days until {args.target}")
    return 0                             # success


if __name__ == "__main__":
    sys.exit(main())
```

Check the codes from your shell:

```bash
uv run countdown.py 2027-01-01; echo $?                 # prints the days, then 0
uv run countdown.py 2020-01-01; echo $?                 # error on stderr, then 1
uv run countdown.py not-a-date; echo $?                 # usage error, then 2
uv run countdown.py 2027-01-01 > out.txt 2> errors.txt  # stdout and stderr apart
```

Three habits are packed into that example:

1. **`main(argv=None)` passes its argument to `parse_args`.** When `argv` is `None`, argparse reads `sys.argv` as usual. But a test can call `main(["2027-01-01", "--since", "2026-12-31"])` directly, without starting a new process or touching the real command line. You'll write exactly those tests in the Testing with pytest lesson.
1. **`main` returns an exit code, and only the last line calls `sys.exit`.** Calling `sys.exit` deep inside your logic makes the code hard to reuse, because exiting kills whatever program called it. Return codes upward and exit once, at the edge.
1. **The logic lives in its own function.** `days_between` knows nothing about argparse or printing, so it's trivial to check. Keep `main` as a thin layer that parses, calls your functions, prints and picks the exit code.

Catch expected failures, such as a missing file or a network error, in `main`. Print a one-line message to stderr and return `1`. Let truly unexpected bugs raise, so you still get a traceback to debug.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the official [argparse tutorial](https://docs.python.org/3/howto/argparse.html). It builds a CLI one argument at a time, so you see each feature in isolation, and it covers the short and long option names and `action="count"` for `-vvv`-style verbosity that this lesson skipped.
   - You can skip the "Conflicting options" and "How to translate the argparse output" sections.
1. Skim the [argparse reference](https://docs.python.org/3/library/argparse.html) so you know what's there. Read the sections on `add_argument`'s `type`, `choices` and `nargs` parameters, and the section on sub-commands. You'll come back to this page whenever you build a CLI.
1. Read the "Aware and naive objects" section and skim the `date` and `timedelta` sections of [the datetime docs](https://docs.python.org/3/library/datetime.html). Then look at the table of format codes near the end (search the page for "Format codes"), which you'll look up for years.
1. Read [the sys.exit documentation](https://docs.python.org/3/library/sys.html#sys.exit). It's only a paragraph, and it explains what happens when you pass a string or `None` instead of a number.
1. Practice with the [cli-apps exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/cli-apps). Each exercise has a starter file and failing tests; run them with `uv run pytest cli-apps/<exercise>` from the `exercises/` folder and make them pass.
1. Build `mimir-habits`, a small habit log, as a new uv project:
   - `uv run habits.py done reading` appends the habit name and the current UTC time (as an ISO string) to a JSON file.
   - `uv run habits.py streak reading` prints how many consecutive days, ending today, the habit was done.
   - `uv run habits.py log --since 2026-10-01` lists entries on or after a date.
   - Use subcommands, `type=date.fromisoformat` for the date, and a `-v`/`--verbose` flag that turns on `DEBUG` logging from the Debugging and Logging lesson.
   - Return exit code `1` with a message on stderr when asked for a habit that has never been logged, and check it with `echo $?`. Push it to GitHub; you'll add tests and CI to it in the next few lessons.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between a positional argument, an option and a flag?](#arguments-options-and-flags)
- [What does argparse do when a type function such as date.fromisoformat raises ValueError?](#your-first-argparse-parser)
- [How do you give a tool separate commands like add and list, each with its own arguments?](#subcommands)
- [Which date format should you use when storing dates in a file, and why?](#dates-and-times)
- [What is a naive datetime, and why should you store times in UTC?](#time-zones)
- [What exit code does a Python program return after an uncaught exception, and after an argparse usage error?](#exit-codes-and-standard-error)
- [Why should main accept an argv parameter and return an exit code instead of calling sys.exit itself?](#exit-codes-and-standard-error)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Command Line Interface Guidelines](https://clig.dev/) is an open guide to designing CLIs people enjoy using: help text, error messages, output for humans versus scripts, and much more.
- [Typer](https://typer.tiangolo.com/) is a popular third-party library that builds CLIs from your functions' type hints. Try it after the Type Hints lesson; it's from the author of FastAPI, which you'll use in the Core path.
