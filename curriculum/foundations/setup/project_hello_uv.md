### Introduction

Time to put the whole setup together. You'll build a tiny command-line tool that lists the files in a folder as a nicely formatted table, using a third-party package for the formatting. You'll create, run and inspect it entirely from the terminal, then open it in VS Code with the right interpreter.

The program is small on purpose. The point is the workflow: creating a project with `uv`, adding a dependency, running code in the project's environment, and combining your program with other shell tools. You'll repeat this workflow at the start of every project from here on.

### Before you start

- Make sure you've finished the three lessons in this section: you should have a terminal (WSL on Windows), VS Code with the Python extension, and `uv` installed. Run `uv --version` and `code --version` to check.
- Your project will be called `mimir-hello-uv`. Create it in your projects folder, not inside `mimir-learning-journal`. You'll put it on GitHub in the next section; for now it lives on your computer.
- You'll use [Rich](https://rich.readthedocs.io/en/stable/tables.html), a popular library for good-looking terminal output. Read the linked page about tables before you start.
- You'll need a few things from Python you haven't formally learned yet. That's fine; look them up as you go. The most useful is [pathlib](https://docs.python.org/3/library/pathlib.html), Python's built-in module for working with files and folders. You only need `Path`, `Path.iterdir()`, `.is_file()`, `.name`, `.suffix` and `.stat().st_size`. To read an argument from the command line, look up `sys.argv`.

Here's a starting point to make the first step less intimidating. It just proves the dependency works:

```python
from rich.console import Console

console = Console()
console.print("[bold green]Hello, uv![/bold green]")
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Create the project from the terminal with `uv init mimir-hello-uv`, move into it, and add Rich as a dependency with `uv add rich`.
   - Open `pyproject.toml` and confirm `rich` is listed under dependencies. Open `uv.lock` and find which version of Rich was installed.
1. Replace the contents of `main.py` with a program that prints a Rich table of the files in a directory, with at least three columns: file name, file extension (suffix) and size in bytes.
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
