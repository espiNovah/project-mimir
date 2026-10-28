### Introduction

So far you've written Python in `.py` files and run them from the terminal. That is the right way to build programs. But a lot of AI engineering isn't building programs. It's poking at data: loading a log of model calls to see which ones were slow, checking what a dataset actually contains, trying three versions of a calculation and comparing the results. For that kind of work, you want to run a few lines, look at the output, and decide what to try next.

A **notebook** is built for exactly this. It's a document made of cells. Some cells hold code you can run one at a time, and the output (text, tables, charts) appears right below the cell and is saved with the document. Notebooks are how most data exploration, many tutorials and nearly every free GPU service work, so you'll meet them constantly.

Notebooks also have a reputation for turning into a mess. This lesson shows you how to run them locally with `uv`, how to use free cloud hardware in Google Colab and Kaggle, and the habits that keep a notebook trustworthy.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a notebook is: cells, a kernel and saved outputs.
- Running JupyterLab with `uv`, or notebooks inside VS Code.
- Using Google Colab and Kaggle for free GPUs.
- Cloning a GitHub repository into Colab and installing it.
- Why notebooks go wrong, and the "restart and run all" habit.
- Keeping notebooks out of trouble in Git.
- Moving reusable code into `.py` modules.

### How a notebook works

A notebook file ends in `.ipynb` (for "IPython notebook", Jupyter's old name). Inside, it's a JSON file holding a list of cells. There are two main kinds:

- **Code cells** hold Python. You run one with Shift+Enter, and its output appears underneath.
- **Markdown cells** hold formatted text: headings, explanations, links. They turn a pile of code into a document someone can read.

The code doesn't run inside the notebook file itself. It runs in a **kernel**, a separate Python process that stays alive while the notebook is open. Every cell you run sends its code to that same process, so variables survive from one cell to the next. If cell 1 says `calls = load_log()`, then cell 5 can use `calls` without loading it again. That's what makes notebooks fast for exploring: you load a big file once and then ask it questions for an hour.

It's also the source of most notebook bugs, as you'll see below. The kernel remembers everything you've run, in the order you ran it, not the order the cells appear on the page. The little number next to each cell, like `[7]`, tells you the order in which cells were run.

### Running Jupyter locally with uv

**Jupyter** is the open-source project behind notebooks, and **JupyterLab** is its browser-based editor. Because you already manage projects with `uv`, there are two clean ways to run it.

For a quick look, run JupyterLab without adding it to your project at all:

```bash
cd my-project
uv run --with jupyter jupyter lab
```

`--with jupyter` tells `uv` to install Jupyter into a temporary environment layered on top of your project, so your notebook can still import your project's packages (like pandas) without Jupyter becoming one of your project's dependencies. A browser tab opens; pick "Python 3" under Notebook to start one.

If you'll use notebooks in a project regularly, add JupyterLab as a development dependency instead, just like you did with pytest:

```bash
uv add --dev jupyterlab
uv run jupyter lab
```

Now anyone who clones the project and runs `uv sync` gets the same setup.

**VS Code notebooks** are the other option, and many people prefer them because you stay in your editor. Create a file ending in `.ipynb`, open it, and click "Select Kernel" in the top right. Choose the Python environment in your project's `.venv` folder. VS Code needs the `ipykernel` package in that environment to talk to it, so run `uv add --dev ipykernel` first. VS Code may offer to install it for you, but doing it with `uv` keeps it recorded in `pyproject.toml`.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Notebook shortcuts worth learning now

Shift+Enter runs a cell and moves to the next one. In command mode (press Esc first), `A` and `B` insert a cell above or below, `M` turns a cell into Markdown and `Y` turns it back into code. Ending a cell with a bare variable name, like `calls`, displays it nicely without `print`.

</div>

### Free GPUs in Colab and Kaggle

Your laptop is fine for everything in Foundations. Later, though, you'll want a **GPU** (graphics processing unit), the kind of chip that makes training and running neural networks fast. You don't need to buy one to learn. Two services give you free notebooks that run on Google's or Kaggle's machines, with a GPU attached:

- **[Google Colab](https://colab.research.google.com/)** needs only a Google account. Open a new notebook, then go to Runtime → Change runtime type and pick a GPU. The free tier has usage limits that change over time and aren't guaranteed, and a session shuts down after a period of inactivity or a maximum lifetime, losing everything not saved elsewhere.
- **Kaggle Notebooks** are similar and come with a fixed weekly GPU quota. You need a free Kaggle account, and you must verify a phone number before GPUs are enabled. Kaggle is also handy because thousands of public datasets can be attached to a notebook in one click.

Both are Jupyter underneath, so everything in this lesson applies. Two differences matter. First, the machine is temporary. Anything you write to its disk is gone when the session ends, so save results to Google Drive, download them, or push them to GitHub. Second, the machine already has many packages installed, and you install more with pip, not `uv add`. A line beginning with `%` is a notebook "magic" command, and a line beginning with `!` runs a shell command:

```python
%pip install -q pandas matplotlib
!nvidia-smi   # shows the GPU you were given, if any
```

### Cloning a repo into Colab

The most useful Colab pattern is running your own GitHub project on a free GPU. Write and test your code locally as a normal package, push it, and then in a Colab notebook:

```python
# Cell 1: get the code onto the Colab machine
!git clone https://github.com/your-username/mimir-data-explorer.git
%cd mimir-data-explorer

# Cell 2: install it, plus its dependencies from pyproject.toml.
# -e means "editable": if you git pull new code, you don't need to reinstall.
%pip install -q -e .

# Cell 3: use it like any installed package
from explorer.clean import load_calls

calls = load_calls("data/calls.csv")
calls.head()
```

Use `%cd`, not `!cd`. Each `!` line runs in its own throwaway shell, so `!cd` changes directory and then immediately forgets it. `%cd` changes the notebook's own working directory.

For a private repository, don't paste a password or token into a cell, because cells and their outputs are saved and easy to share by accident. Make the repo public, or use Colab's Secrets panel (the key icon in the left sidebar), which you'll understand better after the API Keys and Secrets lesson.

You can also open any notebook that's on GitHub directly in Colab by changing the start of its URL from `github.com/` to `colab.research.google.com/github/`.

### Restart and run all

Here's the classic notebook bug. You write a cell that defines `rate = 0.002`. Later you change the cell to `price = 0.002` and run it, and a cell further down still uses `rate`. Everything works, because the kernel still remembers `rate` from earlier. You save, commit and share. The next person who opens the notebook and runs it top to bottom gets a `NameError`.

The kernel's memory and the page have drifted apart. This is called **hidden state**, and it makes notebooks unreliable in ways a `.py` file never is. Cells run out of order cause the same problem: cell 8 might quietly depend on something you ran in cell 12.

The cure is one habit: **before you trust or share a notebook, restart the kernel and run every cell from the top.** In JupyterLab that's Kernel → Restart Kernel and Run All Cells; in VS Code it's Restart, then Run All. If the notebook runs cleanly from a fresh kernel, the page tells the truth. If it doesn't, fix it now, while you still remember what you did. The execution numbers are a quick check: in a trustworthy notebook they go 1, 2, 3, ... down the page.

A few related habits help:

- Put all imports and settings (file paths, random seeds) in the first cell.
- Don't edit a cell and leave the old output under it. Rerun it or clear it.
- Keep notebooks short. One question per notebook beats one notebook for everything.

### Notebooks and Git

Because an `.ipynb` file is JSON with outputs saved inside it, it causes problems in version control. A chart is stored as a long base64-encoded image, a big table is stored as HTML, and an error leaves a full traceback in the file. Rerunning a notebook changes execution counts and outputs even when the code didn't change, so diffs become unreadable and the repository grows fast.

Some rules:

- **Never commit large outputs.** A cell that printed 50,000 rows or rendered 20 high-resolution charts can make a file many megabytes. Clear outputs (Edit → Clear Outputs of All Cells) before committing exploratory notebooks.
- **Keep data out of Git.** Add your raw data folder to `.gitignore` and explain in the README where to download it.
- **Do keep outputs in a notebook that is the report.** If the point of the notebook is to show results, a clean, freshly restarted run with a few charts is fine to commit, since GitHub renders it nicely.
- If clearing outputs by hand gets tedious, the tool [nbstripout](https://github.com/kynan/nbstripout) can strip them automatically every time you commit.

### Move reusable code into modules

Notebooks are good for exploring and for presenting. They're bad for code you need to reuse, test or import. You can't easily import one notebook from another, pytest doesn't run tests inside them, and ruff and code review work far better on plain `.py` files.

So follow this pattern: when a piece of notebook code starts to matter, move it into a module. Say you wrote a few lines that load your log, fix the types and fill missing costs. Turn them into a function in `src/explorer/clean.py`, write a pytest test for it, and have the notebook import it:

```python
# First cell of the notebook
%load_ext autoreload
%autoreload 2

from explorer.clean import load_calls
```

The `autoreload` lines tell Jupyter to reload your module automatically when you edit the `.py` file, so you don't have to restart the kernel after each change. The result is a notebook that stays short and readable (load, ask, plot, explain) while the logic lives in tested code. You'll use exactly this structure in the Data Explorer project.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [uv's guide to using uv with Jupyter](https://docs.astral.sh/uv/guides/integration/jupyter/). It covers both `uv run --with jupyter` and adding Jupyter to a project, plus how VS Code finds your kernel.
   - Read "Using Jupyter within a project" and "Using Jupyter from VS Code". The sections on non-project environments are optional.
1. Read [the JupyterLab overview](https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html) to learn your way around the interface. If you'd rather work in your editor, read [VS Code's Jupyter notebooks guide](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) instead, up to "Variable Explorer and Data Viewer".
1. Open Colab's [overview of features notebook](https://colab.research.google.com/notebooks/basic_features_overview.ipynb) and run every cell. Then skim the [Colab FAQ](https://research.google.com/colaboratory/faq.html) on resource limits, so you know why sessions disconnect.
1. Read [Ten simple rules for writing and sharing computational analyses in Jupyter Notebooks](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007007). It's short, and it explains the hygiene habits from this lesson from the point of view of people who share notebooks for a living.
1. Practice:
   - Create a new `uv` project, add `pandas` and `jupyterlab --dev`, and make a notebook that loads any small CSV file (even one you type yourself) and displays it. Restart and run all, and check that the execution numbers go 1, 2, 3.
   - Move your loading code into a module with a function, import it with `autoreload` on, and change the function to see it reload.
   - Push the project to GitHub, then clone it into a Colab notebook, install it with `%pip install -e .`, and call your function there.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is a kernel, and why do variables survive between cells?](#how-a-notebook-works)
- [What's the difference between `uv run --with jupyter jupyter lab` and `uv add --dev jupyterlab`?](#running-jupyter-locally-with-uv)
- [What happens to files you write on a Colab machine when the session ends?](#free-gpus-in-colab-and-kaggle)
- [Why does `!cd my-repo` not work in a notebook, and what should you use instead?](#cloning-a-repo-into-colab)
- [What is hidden state, and what habit protects you from it?](#restart-and-run-all)
- [Why shouldn't you commit a notebook full of large outputs?](#notebooks-and-git)
- [When should code move out of a notebook and into a `.py` module?](#move-reusable-code-into-modules)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Kaggle's Notebooks documentation](https://www.kaggle.com/docs/notebooks) explains Kaggle's GPU quotas, attaching datasets and saving versions.
- [nbstripout](https://github.com/kynan/nbstripout) strips notebook outputs automatically as a Git filter, if you'd rather not clear them by hand.
