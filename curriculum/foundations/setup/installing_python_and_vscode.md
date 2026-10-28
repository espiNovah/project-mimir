### Introduction

Python is the main language of AI engineering. Model providers publish their official software kits (SDKs) for it first, and most agent frameworks, evaluation tools and data libraries are written in it. Visual Studio Code (VS Code) is a free code editor that most AI engineers use, and its extensions make working with Python, Git, remote machines and AI coding assistants smooth.

In this lesson you'll install both, connect them, and run your first Python program from the terminal and from the editor.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What Python and the Python interpreter are.
- How to install Python on macOS, Windows (WSL) and Linux, and check which version you have.
- How to install VS Code and its Python extension.
- How to open folders in VS Code from the terminal.
- How to run a Python file from the terminal and from VS Code.
- What "selecting an interpreter" means in VS Code.

### Python and the interpreter

When you write Python, you write plain text files ending in `.py`. A program called the **Python interpreter** reads those files and runs them. "Installing Python" means installing that interpreter. Your computer can have several interpreters installed at once (different versions, or copies in different places), which is why you'll often need to check *which* Python is running. This curriculum uses **Python 3.12 or newer**.

On macOS and Linux, the command is usually `python3`, not `python`. On many systems, `python` either doesn't exist or points to something old.

### Installing Python

**macOS:** Download the latest Python 3 installer from [python.org's downloads page](https://www.python.org/downloads/) and run it. When it finishes, open a new terminal window and check:

```bash
python3 --version
```

**Windows (WSL) and Linux (Ubuntu or Debian):** Python 3 usually comes preinstalled. In your Ubuntu terminal, update your package list and make sure the essentials are there:

```bash
sudo apt update
sudo apt install -y python3 python3-venv
python3 --version
```

`sudo` runs a command as an administrator and asks for the password you created when you set up Linux. `apt` is Ubuntu's package manager, a tool that installs software for you.

If the version printed is 3.12 or newer, you're done. If it's older (Ubuntu 22.04, for example, ships 3.10), don't worry. In the next lesson you'll install `uv`, which can download and manage any Python version for each project without touching the system one.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Leave the system Python alone

Linux and macOS use their built-in Python for their own tools. Don't upgrade, remove or install packages into it with `sudo pip install`. That can break your operating system's tools. From the next lesson on, every project gets its own isolated environment instead.

</div>

### Installing VS Code

Download VS Code from [the official download page](https://code.visualstudio.com/download) and install it.

- **Windows:** install VS Code on Windows itself, not inside Ubuntu. Then install the **WSL** extension from the Extensions panel. VS Code will run its window on Windows and do all the work inside Linux.
- **macOS:** drag VS Code into your Applications folder, open it, press <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> to open the Command Palette, and run **Shell Command: Install 'code' command in PATH**. This lets you open folders from the terminal.
- **Linux:** install the `.deb` or `.rpm` package for your distribution.

Next, open the Extensions panel (the icon made of four squares on the left) and install the **Python** extension published by Microsoft. It adds syntax highlighting, error checking, running and debugging. On Windows, install it while connected to WSL so it lands on the Linux side.

### Your first program

Create a folder and open it in VS Code from the terminal:

```bash
mkdir -p ~/projects/hello
cd ~/projects/hello
code .
```

`code .` means "open VS Code in the current folder." On Windows in WSL, the first time you run it, VS Code installs a small server inside Linux; the bottom-left corner of the window then says "WSL: Ubuntu".

In VS Code, create a file called `hello.py` and type:

```python
import sys

name = "world"
print(f"Hello, {name}!")
print("This is Python", sys.version.split()[0])
print("Running from", sys.executable)
```

Save it, then run it from the terminal:

```bash
python3 hello.py
```

You should see a greeting, your Python version and the location of the interpreter that ran the file. You can also run it with the play button in the top-right corner of VS Code. VS Code has a built-in terminal too: open it with <kbd>Ctrl</kbd> + <kbd>&#96;</kbd> (backtick). It's the same shell you've been using, so you can stay in one window.

### Selecting an interpreter

Since a computer can have several Pythons, VS Code needs to know which one to use for running your code and for its error checking. Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> (<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> on macOS) and run **Python: Select Interpreter**. You'll see a list of every interpreter VS Code found. The selected one appears in the status bar at the bottom of the window.

For now, pick the Python 3 you just installed. In the next lesson each project will get its own environment, and you'll select that one instead. If VS Code ever underlines imports in red even though your code runs fine in the terminal, the wrong interpreter is almost always the reason.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Follow [VS Code's Getting Started with Python tutorial](https://code.visualstudio.com/docs/python/python-tutorial), the official walkthrough of writing, running and debugging Python in VS Code.
   - Do every section up to and including "Configure and run the debugger". The tutorial creates a virtual environment early on. Follow along; the next lesson explains what that is and shows the `uv` way of doing it.
   - Skip "Install and use packages" for now.
   - Windows users: also read [Developing in WSL](https://code.visualstudio.com/docs/remote/wsl) to understand how VS Code connects to Linux.
1. Read [Using Python environments in VS Code](https://code.visualstudio.com/docs/python/environments) to understand how VS Code finds and chooses interpreters.
   - Focus on the sections about selecting an interpreter. Skim the rest.
1. Watch or read the [Development Environment and Tools lecture from MIT's Missing Semester](https://missing.csail.mit.edu/2026/development-environment/) for a broader view of editors and why engineers invest in learning theirs.
1. Practice.
   - Change `hello.py` so it asks for your name with `input("What's your name? ")` and greets you by it. Run it from the VS Code terminal. Then set a breakpoint on the `print` line, run it with the debugger, and look at the value of your variable in the Variables panel.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Terminal basics in VS Code](https://code.visualstudio.com/docs/terminal/basics) shows how to split terminals, run several at once and customize them.
- [Visual Studio Code on macOS](https://code.visualstudio.com/docs/setup/mac) has extra detail on the `code` command and updates for Mac users.
