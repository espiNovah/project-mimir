### Introduction

You now have tests and a type checker. Both only help when someone runs them, and people forget. You'll push a quick fix at midnight without running `pytest`. A teammate will commit code formatted their own way, and the next pull request will be full of noise about spaces and quotes instead of real changes. A coding agent will hand you 200 lines with an unused import and a subtle bug that a tool could have caught in a millisecond.

The fix is to hand these checks to machines and make them automatic. In this lesson you'll set up three layers:

1. **Ruff**, a fast tool that finds likely bugs and formats your code the same way every time.
1. **pre-commit**, which runs ruff for you each time you make a commit.
1. **Continuous integration (CI)** with **GitHub Actions**, which runs ruff and pytest on GitHub's computers every time you push, and puts a green check or a red cross next to every commit.

From the Project: Expense Tracker on, every project in this curriculum needs a CI workflow that runs ruff and pytest. Employers look for it too. A green CI badge on a repo tells a reviewer that the tests aren't just there, they actually pass, on a machine that isn't yours.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What linters and formatters are, and how they differ.
- Running `ruff check` and `ruff format`, and fixing what they find.
- Configuring ruff's rules in `pyproject.toml`.
- Running checks automatically before each commit with pre-commit.
- What continuous integration is, and the parts of a GitHub Actions workflow.
- Writing a workflow that runs ruff and pytest on every push.
- Reading a failing CI run and adding a status badge to your README.

### Linters and formatters

A **linter** reads your code without running it and reports patterns that are probably mistakes: an import you never use, a variable you misspelled, a comparison that doesn't do what it looks like. The name comes from an old Unix tool that picked "lint", little bits of fluff, out of C programs. A **formatter** doesn't look for mistakes at all. It rewrites the layout of your code, such as spacing, line breaks, quotes and blank lines, into one consistent style.

The two solve different problems. The linter catches bugs. The formatter ends arguments: once a project uses a formatter, nobody spends time on style in code review, and every diff shows only real changes.

For years Python developers used separate tools for these jobs: Flake8 and Pylint for linting, isort for sorting imports, Black for formatting. **Ruff** does all of it in a single tool, and it's so fast it can check a large project before you've lifted your finger off the Enter key. It's now the most common choice for new Python projects, and it's the one this curriculum uses.

### Running ruff

Add ruff to your project as a development dependency, just like pytest:

```bash
uv add --dev ruff
```

Here's a short file with four problems a reader might miss. Save it as `scores.py`:

```python
import os
import json


def add_score(score, scores=[]):
    scores.append(score)
    return scores


def load_scores(path):
    with open(path) as f:
        data = json.load(f)
    if data == None:
        return []
    return data
```

Run the linter with `uv run ruff check`. With the rules you'll turn on in the next section, the short version of its report (add `--output-format concise` to see it this way) looks like this:

```text
scores.py:1:1: I001 [*] Import block is un-sorted or un-formatted
scores.py:1:8: F401 [*] `os` imported but unused
scores.py:5:29: B006 Do not use mutable data structures for argument defaults
scores.py:13:16: E711 Comparison to `None` should be `cond is None`
Found 4 errors.
[*] 2 fixable with `--fix` (2 unsafe fixes available with `--fix --unsafe-fixes`).
```

Each line gives the file, line and column, a **rule code** and a message. The codes are worth learning to read. The letter prefix says which family a rule comes from (`F` for Pyflakes, `E` for pycodestyle, `B` for flake8-bugbear, `I` for isort), and you can look up any code on [ruff's rules page](https://docs.astral.sh/ruff/rules/) to see a longer explanation with examples. `B006` is a real bug: Python creates the default list once, when the function is defined, so every call to `add_score` without a list shares the same one. Call `add_score(1)` twice and the second call returns `[1, 1]`.

Rules marked `[*]` can be fixed automatically, so `uv run ruff check --fix` sorts the imports and removes `os` for you. Ruff calls some fixes **unsafe** because they could change what the program does, so it won't apply them unless you ask. Fix those by hand, after you understand the problem.

Then run the formatter:

```bash
uv run ruff format            # rewrite files in place
uv run ruff format --check    # only report which files would change
```

`ruff format` follows the same style as Black: four-space indentation, double quotes, lines up to 88 characters and two blank lines between top-level functions. You don't choose the style; that's the point.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Format on save in VS Code

Install the official Ruff extension in VS Code, then turn on "Format On Save" in your settings and set Ruff as the default formatter for Python. Your file is formatted every time you save, and lint problems appear as squiggly underlines while you type, so most of them never reach a commit.

</div>

### Configuring ruff

Out of the box, ruff only enables a cautious set of rules: the `F` rules and a few of the `E` rules. That avoids flooding you with warnings, but it misses useful checks. Turn on more in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle: style errors such as comparing to None with ==
    "F",    # Pyflakes: unused imports, undefined names
    "I",    # isort: sorted, grouped imports
    "B",    # flake8-bugbear: likely bugs, such as mutable default arguments
    "UP",   # pyupgrade: use modern syntax for your Python version
    "SIM",  # flake8-simplify: code that can be written more simply
]
```

This is a good starting set for any project in this curriculum. Ruff reads your project's `requires-python` setting from the same file, so `UP` suggests only syntax your Python version supports.

Sometimes a rule is wrong for one specific line. Silence it there with a comment naming the exact rule, such as `import readline  # noqa: F401`, which keeps an import you need only for its side effect. Never write a bare `# noqa`, which silences every rule on the line, and don't turn rules off project-wide just to make the warnings go away. Each warning is either a real problem or a rule you've consciously decided doesn't apply.

### Checking before every commit

**Git hooks** are scripts Git runs at certain moments, such as just before it records a commit. **pre-commit** is a tool that manages those hooks for you. You list the checks in a file, and pre-commit installs them, keeps them at the versions you chose and runs them only on the files you're committing.

Create `.pre-commit-config.yaml` in your project root:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.3            # the ruff version to use
    hooks:
      - id: ruff-check      # the linter
        args: [--fix]
      - id: ruff-format     # the formatter
```

Then install pre-commit and connect it to Git:

```bash
uv add --dev pre-commit
uv run pre-commit install           # adds the hook to .git/hooks
uv run pre-commit run --all-files   # check everything once, right now
```

From now on, `git commit` runs both hooks first. If ruff changes a file or finds a problem it can't fix, the commit stops. Look at the changes, fix anything left over, `git add` the files again and commit again. Commit `.pre-commit-config.yaml` itself so everyone who clones the repo uses the same checks; each person runs `pre-commit install` once.

Keep the `rev` in step with the ruff version in your `uv.lock` so both give the same results. `uv run pre-commit autoupdate` moves every hook to its newest version.

Hooks run on your machine, so they're a convenience, not a guarantee. Anyone can skip them with `git commit --no-verify`, and a new contributor may never have installed them. The guarantee comes from CI.

### Continuous integration

**Continuous integration** means every change is automatically built and tested, on a clean machine, as soon as it's pushed. "Clean" is the key word. Your laptop has packages you installed months ago and files you forgot to commit. A CI machine starts from nothing, so if your tests pass there, they pass for anyone who clones your repo.

**GitHub Actions** is GitHub's built-in CI service, and it's free for public repositories. You describe what to do in a **workflow**, a YAML file in the `.github/workflows/` folder of your repo. A few terms:

- A **trigger** (the `on:` key) says when the workflow runs, such as on every push or every pull request.
- A **job** is a group of steps that runs on one fresh virtual machine, called a **runner**. `runs-on: ubuntu-latest` asks for a Linux runner.
- A **step** is either a shell command (`run:`) or an **action** (`uses:`), a reusable piece of setup someone else published. `actions/checkout` copies your repo onto the runner, and `astral-sh/setup-uv` installs uv.

If any step exits with a non-zero exit code, the step fails, the job stops and the run is marked as failed. This is exactly why exit codes mattered in the Command-Line Apps lesson: `ruff check` and `pytest` exit with `1` when they find problems, and that's how GitHub knows.

### A workflow for ruff and pytest

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: astral-sh/setup-uv@v10.3.3

      - name: Install dependencies
        run: uv sync --locked        # fail if uv.lock is out of date

      - name: Lint
        run: uv run ruff check .

      - name: Check formatting
        run: uv run ruff format --check .

      - name: Run tests
        run: uv run pytest
```

Commit it and push. Open the **Actions** tab of your repo on GitHub and you'll see the run start within a few seconds. Click into it to watch each step's output live.

A few details to notice:

- `uv sync` installs your project's dependencies, including the `dev` group with ruff and pytest. It also installs the Python version your project asks for, so you don't need a separate step for it. `--locked` makes it fail if `uv.lock` doesn't match `pyproject.toml`, which catches the "I added a package but forgot to commit the lock file" mistake.
- In CI, use `ruff format --check`, not `ruff format`. CI should report problems, not quietly rewrite files that then get thrown away.
- `@v7` and `@v10.3.3` pin the version of each action, so a new release can't change your build without you knowing.
- If your repo has no tests yet, pytest exits with code `5` ("no tests collected"), which fails the run. That's on purpose: a CI run with no tests proves nothing.

When a run fails, GitHub shows a red cross next to the commit and emails you. Click into the failed step and read the output exactly as you'd read it in your terminal. Then reproduce it locally by running the same command, such as `uv run pytest`, fix it, and push again. Never "fix" a red build by deleting the failing test.

### Showing the result

Add a **status badge** to the top of your README so visitors can see at a glance whether the main branch passes:

```markdown
[![CI](BADGE-URL)](WORKFLOW-URL)
```

Replace `BADGE-URL` with `https://github.com/<username>/<repo>/actions/workflows/ci.yml/badge.svg` and `WORKFLOW-URL` with the same address minus `/badge.svg`, filling in your username and repo name. The badge is an image of the latest run's result, and clicking it opens the list of runs. It updates itself after every run. You can also copy a ready-made badge from GitHub: open a workflow in the Actions tab, click the `...` menu and choose "Create status badge".

On a team, you'd go one step further with **branch protection**: in the repo's settings, you can require the CI check to pass before a pull request can be merged into `main`. Then a broken change can't land at all. It's worth turning on even for solo projects, because it stops you from merging your own pull request in a hurry when the tests are red.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Do [ruff's tutorial](https://docs.astral.sh/ruff/tutorial/). It walks through linting, formatting, configuration and editor setup on a tiny project. Use `uv add --dev ruff` in your own project rather than creating a new one.
   - Then skim [the linter page](https://docs.astral.sh/ruff/linter/), especially the sections on rule selection, fixes (including fix safety) and error suppression.
1. Read the introduction and the "Quick start" section of [the pre-commit docs](https://pre-commit.com/). Use `uv add --dev pre-commit` instead of `pip install pre-commit`, and `uv run pre-commit` to run it.
1. Read [Understanding GitHub Actions](https://docs.github.com/en/actions/get-started/understand-github-actions), GitHub's own explanation of workflows, events, jobs, steps, runners and actions, with a diagram of how they fit together.
1. Read the "Installation", "Syncing and running" and "Caching" sections of [the uv guide to GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/). It shows more ways to set up Python and dependencies than this lesson did. Use `actions/checkout@v7` and `astral-sh/setup-uv@v10.3.3` as in this lesson, even where the guide's examples show older versions.
1. Practice on your `mimir-habits` repo from the Command-Line Apps lesson:
   - Add at least three pytest tests, including one that calls `main([...])` with a test argument list and checks the exit code it returns.
   - Add ruff with the rule set from this lesson and fix everything it reports, by hand where a fix is unsafe.
   - Add the pre-commit config and install it. Make a commit with an unused import and watch the hook stop it.
   - Add the CI workflow and the badge. Then push a commit with a deliberately failing test, look at the red run, fix it and push again so the badge is green.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between a linter and a formatter?](#linters-and-formatters)
- [What does a rule code such as B006 tell you, and what is an unsafe fix?](#running-ruff)
- [How do you turn on more ruff rules, and how should you silence a rule for a single line?](#configuring-ruff)
- [Why isn't pre-commit enough on its own to keep a repo's main branch passing?](#checking-before-every-commit)
- [What are a trigger, a job, a runner and a step in GitHub Actions?](#continuous-integration)
- [Why should CI run ruff format with the check option, and what does uv sync with the locked option catch?](#a-workflow-for-ruff-and-pytest)
- [What does branch protection add on top of a status badge?](#showing-the-result)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [GitHub's Actions quickstart](https://docs.github.com/en/actions/get-started/quickstart) builds a first workflow step by step in the browser, if you'd like a second walkthrough.
- [Adding a workflow status badge](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge) shows how to make a badge for a specific branch or event.
- [The setup-uv README](https://github.com/astral-sh/setup-uv) lists every option the action accepts, including pinning a uv version and testing several Python versions with a matrix.
