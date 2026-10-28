### Introduction

Time to put the whole setup together. You'll build a tiny command-line tool that lists the files in a folder as a nicely formatted table, using a third-party package for the formatting. You'll create, run and inspect it entirely from the terminal, then open it in VS Code with the right interpreter.

The program is small on purpose. The point is the workflow: creating a project with `uv`, adding a dependency, running code in the project's environment, and combining your program with other shell tools. You'll repeat this workflow at the start of every project from here on.

### Before you start

- Make sure you've finished the three lessons in this section: you should have a terminal (WSL on Windows), VS Code with the Python extension, and `uv` installed. Run `uv --version` and `code --version` to check.
- Your project will be called `mimir-hello-uv`. Create it in your projects folder, not inside `mimir-learning-journal`. You'll put it on GitHub in the next section; for now it lives on your computer.
- You'll use [Rich](https://rich.readthedocs.io/en/stable/tables.html), a popular library for good-looking terminal output. Read the linked page about tables before you start.
- You haven't learned Python yet, so you won't write this program from scratch. Below is a starter `main.py` that already works: it prints a Rich table of the file names in the current folder. Your job is to extend it, following the `TODO` comments. Each line has a comment saying what it does, and the [pathlib](https://docs.python.org/3/library/pathlib.html) docs (Python's built-in module for files and folders) explain `Path`, `.iterdir()`, `.is_file()`, `.is_dir()`, `.name`, `.suffix` and `.stat().st_size` if you want more detail.

Here's the starter. You'll paste it over the `main.py` that `uv init` creates:

```python
"""List the files in a folder as a table. Starter code for Project: Hello, uv."""

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

# sys.argv is the list of words typed after "uv run"; sys.argv[0] is "main.py".
# TODO: if a folder was passed (len(sys.argv) > 1), use Path(sys.argv[1]) instead.
folder = Path(".")

# TODO: if folder.is_dir() is False, print a clear error with console.print
# and stop the program with sys.exit(1).

table = Table(title="Files")  # TODO: show which folder is listed, e.g. f"Files in {folder}"
table.add_column("Name")
# TODO: add "Extension" and "Size (bytes)" columns.

for path in folder.iterdir():  # TODO: loop over sorted(folder.iterdir()) instead.
    # TODO: skip anything that isn't a file: `if not path.is_file(): continue`
    table.add_row(path.name)  # TODO: also pass path.suffix and str(path.stat().st_size)

console.print(table)
```

Run it once, unchanged, before you edit anything. If you see a table of names, uv, Rich and your environment all work, and every problem after that comes from your own edits.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Create the project from the terminal with `uv init mimir-hello-uv`, move into it, and add Rich as a dependency with `uv add rich`.
   - Open `pyproject.toml` and confirm `rich` is listed under dependencies. Open `uv.lock` and find which version of Rich was installed.
1. Paste the starter from "Before you start" over the generated `main.py` and run it with `uv run main.py`. Then work through the `TODO` comments so the program prints a Rich table of the files in a directory, with at least three columns: file name, file extension (suffix) and size in bytes. Delete each `TODO` comment once it's done.
   - By default it should list the current directory. If you pass a folder path as an argument, it should list that folder instead. For example, `uv run main.py ~/projects` lists your projects folder.
   - Only include files, not folders.
   - Sort the rows by file name.
   - Give the table a title showing which directory it lists.
1. Run it with `uv run main.py` on at least two different folders and check the output against `ls -la` for the same folder. The file names and sizes must match.
1. Combine your program with shell tools using pipes. Run each of these and note the result:
   - `uv run main.py | grep py` to show only rows containing "py".
   - `uv run main.py | wc -l` to count the lines of output. Explain in a sentence why this number is larger than the number of files.
   - `uv run main.py > files.txt` to save the output to a file, then `cat files.txt`.
1. Handle a bad input. If the folder you pass doesn't exist, the program should print a clear error message instead of crashing with a long traceback, and exit.
1. Open the project in VS Code with `code .`, then use **Python: Select Interpreter** to pick the interpreter inside the project's `.venv` folder.
   - Check that the `from rich...` import is not underlined as an error. Take a screenshot of VS Code showing the selected interpreter in the status bar and the import with no error.
1. Fill in `README.md` with what the program does, how to run it (the exact commands, starting from `uv run`), example output pasted as text in a code block, and two or three sentences on what you learned. You'll push it to GitHub in the "Git & GitHub" section.

#### Evidence

You haven't learned to write tests yet, so the evidence is real output that anyone can compare with their own run:

- The README shows the table printed for at least one real folder, pasted as text in a code block, together with the `ls -la` output for the same folder, so a reader can see the names and sizes match.
- The README shows the commands and output of the `grep` and `wc -l` pipelines, with your one-sentence explanation of the line count.
- The README shows a short terminal transcript of running the program on a folder that doesn't exist, with your error message and no traceback.
- The README names the exact Rich version from `uv.lock`.
- Your VS Code screenshot is in the project folder and linked from the README, showing the `.venv` interpreter in the status bar and the Rich import without an error.

#### Extra credit

- Show sizes in a human-friendly format (like `1.2 MB`) as well as in bytes. Write it yourself, or use a package and add it with `uv add`.
- Add a column for the last-modified date.
- Add a final row or caption with the total number of files and their combined size.
- Rerun `uv run main.py` after deleting `.venv` and describe in your README what uv did.

</div>

### Submitting your work

Keep everything in the `mimir-hello-uv` folder: `main.py`, `pyproject.toml`, `uv.lock`, the README and your VS Code screenshot. A strong submission:

- Runs on a fresh machine with nothing more than `uv run main.py`, because the lockfile pins the dependencies.
- Shows real output in the README for at least one real folder, plus the outputs of the `grep` and `wc` pipelines.
- Prints a friendly message, not a traceback, for a folder that doesn't exist.
- Includes the screenshot proving VS Code is using the project's environment.
