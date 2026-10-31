### Introduction

This is the capstone of the Python Fundamentals section. You'll build a command-line expense tracker: a program that lets you record what you spend, list your expenses, and summarize them by category, saving everything to a CSV file so it's still there tomorrow.

Unlike the Project: CLI Quiz Game, this time you're expected to build it the way a professional would from the start. That means a dataclass for your data, type hints that pass mypy, clear error messages for bad input, a pytest suite that proves the important parts work, and code that passes ruff. It also means **continuous integration** (CI): a GitHub Actions workflow, like the one you wrote in Linting, Formatting and CI, that runs ruff and your tests on every push, so the green badge in your README proves the checks pass on a clean machine, not just on yours. These are exactly the habits that the rest of the curriculum relies on. When you build an LLM-powered API or an agent later, the code around the model will look a lot like this: typed data, validated input, saved results and tests.

### Before you start

1. Create a new uv project and a GitHub repository named `mimir-expense-tracker`:

   ```bash
   uv init mimir-expense-tracker
   cd mimir-expense-tracker
   uv add --dev pytest mypy ruff
   ```

   Then add the `[tool.ruff]` and `[tool.ruff.lint]` settings from the Linting, Formatting and CI lesson to `pyproject.toml`, and copy that lesson's `.github/workflows/ci.yml` into the repo. Push it now, before you write any features. The first run will fail, because pytest exits with code `5` when there are no tests yet. That's expected; it turns green once your first test exists, and then every push after that is checked.

1. You'll store expenses in a **CSV** (comma-separated values) file, a plain-text table that any spreadsheet app can open. The first row holds column names:

   ```text
   date,description,category,amount
   2026-10-01,Groceries,food,54.20
   2026-10-02,Bus pass,transport,30.00
   2026-10-02,"Coffee, large",food,4.75
   ```

   Notice the quotes around `Coffee, large`: a value containing a comma has to be quoted. Don't write CSV by joining strings yourself; Python's `csv` module handles quoting for you. `csv.DictWriter` writes dicts as rows and `csv.DictReader` reads each row back as a dict of **strings**:

   ```python
   import csv
   from pathlib import Path

   FIELDS = ["date", "description", "category", "amount"]
   path = Path("expenses.csv")

   with open(path, "w", newline="", encoding="utf-8") as f:
       writer = csv.DictWriter(f, fieldnames=FIELDS)
       writer.writeheader()
       writer.writerow({"date": "2026-10-01", "description": "Groceries",
                        "category": "food", "amount": 54.2})

   with open(path, newline="", encoding="utf-8") as f:
       for row in csv.DictReader(f):
           print(row["description"], float(row["amount"]))
   ```

   Always pass `newline=""` when opening CSV files; the `csv` docs explain why. Because every value comes back as a string, you'll need to convert `amount` to a number when you load it.

1. Decide how the user will interact with the program. Either works:
   - **Subcommands** with `argparse`, such as `uv run expenses.py add 12.50 food "Lunch"`, `uv run expenses.py list` and `uv run expenses.py summary`. The Command-Line Apps lesson covers subcommands with `add_subparsers` and the `main(argv=None)` shape that returns an exit code, and [the argparse docs](https://docs.python.org/3/library/argparse.html) fill in the details.
   - **An interactive menu** that loops, asking "add, list, summary or quit?", like the loops you wrote in Conditionals and Loops.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Separate the logic from the input and output

Put the parts that compute things (parsing an amount, building an `Expense`, summarizing a list of expenses, reading and writing a CSV at a given path) in functions that take arguments and return values. Keep `input()`, `print()` and argument parsing in a thin layer on top, such as `main()`. This one decision is what makes the program easy to test, as you saw in the Testing with pytest lesson. It also means the CSV path can be a parameter, so tests pass a file inside `tmp_path` and never touch your real `expenses.csv`.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Represent each expense with a dataclass, for example `Expense`, with at least these fields: date, description, category and amount. Use a `datetime.date` for the date (today's date by default when adding) and a number for the amount.
   - Hint: as in the Command-Line Apps lesson, after `from datetime import date`, `date.today()` gives today's date, `date.fromisoformat("2026-10-01")` turns a string into a date, and `some_date.isoformat()` turns it back into a string for the CSV. A dataclass field can default to today with `field(default_factory=date.today)`.
1. **Add**: let the user add an expense with an amount, a category and a description. Store categories in lowercase so `Food` and `food` count as the same category.
1. **List**: show all expenses as a readable, aligned table, with amounts formatted to two decimal places (an f-string such as `f"{amount:>8.2f}"` right-aligns a number in eight characters). Show a friendly message instead of an empty table when there are no expenses yet.
1. **Summarize**: show the total spent per category, sorted from largest to smallest, and a grand total.
1. **Save to CSV**: save every expense to `expenses.csv` using the `csv` module, and load the file on startup so data survives between runs. If the file doesn't exist yet, start with an empty list rather than crashing.
1. **Handle bad input**: a non-numeric amount like `twelve`, a zero or negative amount, and an empty description must each produce a clear error message, not a traceback, and must not save anything. Do this by having your parsing or validation functions raise `ValueError` (or your own exception class) with a helpful message, and catching it where you talk to the user. A corrupted row in the CSV should also give a clear error that says which line is bad.
1. **Type hints**: annotate every function's parameters and return value. `uv run mypy .` must report no errors.
1. **Tests**: write at least five meaningful pytest tests, and make sure `uv run pytest` passes. Your tests must include:
   - at least one test that invalid input raises the expected exception, using `pytest.raises`;
   - at least one test of the per-category summary, with a known list of expenses and known totals;
   - at least one round-trip test that saves expenses to a CSV inside `tmp_path`, loads them back, and checks they're equal to the originals;
   - at least one test of the command layer that checks an error message and exit code with `capsys` (if you used `main(argv=None)` with argparse), or that passes your input-reading function in as a dependency, or replaces it with `monkeypatch`, if you built a menu. The Testing with pytest lesson shows all three.
1. **Lint and format**: `uv run ruff check .` and `uv run ruff format --check .` must both pass, with the rule set from Linting, Formatting and CI. Fix what ruff reports rather than turning rules off; if one line really needs an exception, use a `# noqa` comment naming the exact rule.
1. **CI**: a GitHub Actions workflow in `.github/workflows/ci.yml` runs `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest` on every push and pull request. Commit `uv.lock` so `--locked` works. You may add a `uv run mypy .` step too, and it's a good idea; ruff and pytest are the required minimum.
1. **Run with uv**: the whole program must run with `uv run` from a fresh clone, with no manual setup beyond what the README says.
1. Push your project to GitHub with a README that explains what it does, how to run it (with an example of each command), how to run the tests, ruff and the type checker, and what you learned.

#### Evidence

- `uv run pytest` passes with at least five meaningful tests, and the README includes its output.
- The GitHub Actions workflow runs ruff and pytest on every push, and the latest run on `main` passes. Show its status badge at the top of the README, as in [GitHub's guide to adding a status badge](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge). (Linting, Formatting and CI)
- The README includes a short, real terminal transcript of adding, listing and summarizing expenses, and of at least one bad input, such as `add twelve food "Lunch"`, producing a clear error instead of a traceback.

#### Extra credit

- Add filters: list or summarize only one category, or only one month (for example `summary --month 2026-10`).
- Add a `delete` command that removes an expense by its number in the list, with tests.
- Add monthly budgets per category, stored in a small JSON file, and warn when a category goes over budget.
- Store amounts as integer cents, or use Python's `decimal` module, so totals are always exact. Write a test that shows the floating-point problem your change avoids.
- Run `uv run mypy --strict .` cleanly.
- Add a pre-commit hook that runs ruff before every commit, as in Linting, Formatting and CI, so formatting problems never reach CI.

</div>

### Submitting your work

A strong submission convinces a reviewer in two minutes that the program works and is built well. The README opens with a green CI badge and shows real commands and real output, not just a description. The test output shows at least five passing tests, and the tests themselves check behavior that matters (bad input rejected, totals correct, data survives a save and load), not trivia such as "the dataclass has a field called amount".

Look over your code once more before you submit. Can a reader understand each function from its name, type hints and docstring alone? Is all the `input()` and `print()` in one place? Would a bad CSV row crash the program or explain itself? Keep this repo: you'll reuse its structure, and maybe its code, when you start calling APIs in The Web for AI Builders section.
