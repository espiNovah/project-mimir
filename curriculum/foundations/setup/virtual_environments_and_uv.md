### Introduction

Real Python projects use other people's code. An AI project might use an SDK to call a model, a web framework, a database library and a testing tool. These outside pieces of code are called **packages**, and the packages your project needs are its **dependencies**.

Dependencies cause a classic problem: one project needs version 1 of a package, another needs version 2, and installing both into the same Python breaks one of them. The solution every working engineer uses is to give each project its own isolated environment. In this lesson you'll learn how that works, first with Python's built-in tool and then with `uv`, the fast, modern tool you'll use for every project in this curriculum.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What packages, dependencies and PyPI are.
- What a virtual environment is and why every project needs one.
- How to create one by hand with `venv` and `pip`.
- How to install `uv` and create a project with it.
- What `pyproject.toml` and `uv.lock` are for.
- How to add, remove and run things with `uv`.

### Packages and virtual environments

Python packages are published on **PyPI**, the Python Package Index, a free public registry at pypi.org. A tool called a **package manager** downloads packages from PyPI and installs them for you.

A **virtual environment** is a folder that contains its own copy of the Python interpreter setup plus its own installed packages. When an environment is **activated**, the `python` command uses that folder's packages instead of the system's. Each project gets its own environment, so projects can't break each other, and you can delete an environment and rebuild it any time.

Python has a built-in way to do this. It's worth seeing once, because you'll meet it in tutorials and older projects:

```bash
mkdir ~/projects/venv-demo && cd ~/projects/venv-demo
python3 -m venv .venv          # create an environment in a folder called .venv
source .venv/bin/activate      # activate it; your prompt now starts with (.venv)
pip install humanize           # pip is the classic package installer
python -c "import humanize; print(humanize.naturalsize(1234567))"
deactivate                     # leave the environment
```

The last Python line should print `1.2 MB`. This works, but you have to remember to activate the environment, keep a separate list of what you installed, and pick a Python version yourself.

### Why uv

[uv](https://docs.astral.sh/uv/) is a package and project manager for Python that handles all of this in one tool. It creates the environment for you, records your dependencies, installs the right Python version if you don't have it, and is very fast. It has quickly become the standard choice for new Python projects, including in the AI ecosystem.

Install it on macOS, Linux or WSL with the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then close and reopen your terminal and check that it works:

```bash
uv --version
```

<div class="lesson-note lesson-note--tip" markdown="1">

#### Reading install commands

`curl ... | sh` downloads a script and runs it immediately. Only do this with scripts from sources you trust, like the official uv docs. Get in the habit of checking where an install command comes from before you paste it. This matters even more later, when AI agents suggest commands to run.

</div>

### A uv project

Create a project and look at what you get:

```bash
cd ~/projects
uv init uv-demo
cd uv-demo
ls -a
```

You'll see:

- `pyproject.toml`: the project's settings file. It records the project's name, the Python version it needs, and its dependencies. It's the standard format, so other tools read it too.
- `.python-version`: which Python version this project uses.
- `main.py`: a starter program.
- `README.md`: a place to describe the project.
- `.gitignore` and a `.git` folder: `uv init` also sets the project up for Git, which you'll learn about in the next section.

Now add a dependency and run some code:

```bash
uv add humanize
```

This does three things: it adds `humanize` to the dependencies list in `pyproject.toml`, creates a `.venv` folder with an environment if one doesn't exist, and writes a `uv.lock` file. Edit `main.py`:

```python
import humanize


def main() -> None:
    sizes = [512, 48_000, 1_234_567, 9_800_000_000]
    for size in sizes:
        print(f"{size:>14,} bytes is {humanize.naturalsize(size)}")


if __name__ == "__main__":
    main()
```

Run it with:

```bash
uv run main.py
```

`uv run` runs a command inside the project's environment, after making sure the environment matches `pyproject.toml` and `uv.lock`. You never need to activate anything. (You can still activate `.venv` the classic way if a tool needs it.)

### The lockfile and reproducibility

`pyproject.toml` says what you asked for, like "humanize, any recent version." `uv.lock` records exactly what was installed: the precise version of every package, including the packages your packages depend on. When someone else downloads your project and runs `uv sync` (or just `uv run`), they get the identical set of packages. That's called a **reproducible** environment, and it's why "works on my machine" problems are much rarer with a lockfile.

Commit `pyproject.toml` and `uv.lock` to Git. Don't commit `.venv`. It's large, specific to your computer and can always be rebuilt. The `.gitignore` that `uv init` creates already excludes it.

A few more commands you'll use constantly:

```bash
uv add --dev pytest      # a dependency only needed while developing, like a test tool
uv remove humanize       # remove a dependency
uv sync                  # make .venv match the lockfile exactly
uv python install 3.13   # download a specific Python version
uv python list           # see which Pythons uv can find
```

<div class="lesson-note" markdown="1">

#### Pointing VS Code at the environment

When you open a uv project with `code .`, run **Python: Select Interpreter** and choose the one inside the project's `.venv` folder. VS Code usually suggests it. Now its error checking sees the same packages `uv run` does.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Virtual Environments and Packages tutorial](https://docs.python.org/3/tutorial/venv.html) in the official Python docs. It explains the problem uv solves, in Python's own words.
   - Read all three sections. You don't need to memorize the `pip` commands.
1. Read the [uv getting started guide](https://docs.astral.sh/uv/) and then the [Working on projects guide](https://docs.astral.sh/uv/guides/projects/).
   - Use the [installation page](https://docs.astral.sh/uv/getting-started/installation/) if the install command above didn't work for you.
   - In the projects guide, read "Creating a new project", "Project structure" (which covers `pyproject.toml`, `.venv` and `uv.lock`), "Managing dependencies" and "Running commands". Skip "Building distributions" for now.
1. Watch or read the [Packaging and Shipping Code lecture from MIT's Missing Semester](https://missing.csail.mit.edu/2026/shipping-code/) for the bigger picture of dependencies, environments and how code gets from your laptop to other machines.
   - It's fine if parts go beyond what you need right now. Focus on the parts about dependencies and environments.
1. Practice.
   - Build the `uv-demo` project from this lesson yourself. Then delete its `.venv` folder with `rm -rf .venv` and run `uv run main.py` again. Notice that uv rebuilds the environment from the lockfile. Open `uv.lock` and find the exact version of `humanize` that was installed.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is a virtual environment, and why does every project need its own?](#packages-and-virtual-environments)
- [What does uv do for you that venv and pip don't?](#why-uv)
- [What happens when you run uv add, and why don't you need to activate the environment before uv run?](#a-uv-project)
- [What is the difference between what pyproject.toml records and what uv.lock records?](#the-lockfile-and-reproducibility)
- [Why should you commit uv.lock to Git but not the .venv folder?](#the-lockfile-and-reproducibility)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Running scripts with uv](https://docs.astral.sh/uv/guides/scripts/) shows how to run single-file scripts with their own dependencies, handy for quick experiments.
- [Installing Python with uv](https://docs.astral.sh/uv/guides/install-python/) explains how uv finds and downloads Python versions.
