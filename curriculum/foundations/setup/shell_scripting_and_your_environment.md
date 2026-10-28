### Introduction

In Command Line Basics you learned to move around and manage files. This lesson goes one level deeper, into the environment that every program on your computer runs inside. Why does typing `python3` find a program, but typing `uv` right after installing it sometimes says "command not found"? Where do API keys live so your code can read them without writing them into a file? How do you stop a program that has frozen? And how do you save a sequence of commands so you never have to type it again?

These questions come up constantly in AI engineering. You'll set API keys as environment variables, fix broken `PATH`s after installing tools, kill servers that won't shut down, and write small scripts that set up a project or run your tests and checks in one go. None of it is hard, but it's confusing until someone explains it once.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What environment variables are and how to set and read them.
- How `PATH` decides which program runs, and how to inspect it with `which`.
- File permissions and how to change them with `chmod`.
- Processes: listing them with `ps` and stopping them with `kill`.
- Finding files with `find` and feeding results to other commands with `xargs`.
- Writing and running your first bash script.

### Environment variables

Every program that runs on your computer gets a small set of named text values handed to it when it starts. These are **environment variables**. They're how the outside world configures a program without changing its code. Try a few:

```bash
echo $HOME    # your home folder
echo $USER    # your username
echo $SHELL   # which shell you're using (zsh on macOS, bash on Ubuntu)
env           # list all of them
```

The `$` in front of a name means "replace this with the variable's value." You create one with `export`. Note there are no spaces around the `=`:

```bash
export GREETING="hello from the environment"
echo $GREETING
```

`export` matters. It marks the variable to be passed down to every program you start from this shell. Later in the curriculum, your Python code will read `ANTHROPIC_API_KEY` from the environment exactly like this, which is why keys belong in the environment and never in your source code.

A variable you set with `export` only lasts until you close the terminal window. To make one permanent, add the `export` line to your shell's startup file: `~/.zshrc` on macOS (zsh) or `~/.bashrc` on Ubuntu and WSL (bash). The shell runs that file every time a new terminal opens. After editing it, either open a new terminal or run `source ~/.zshrc` (or `source ~/.bashrc`) to apply it to the current one.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Keep secrets out of startup files you share

Putting an API key in `~/.zshrc` works, but it makes the key visible to every program you run, and some people publish their "dotfiles" on GitHub by accident. In API Keys and Secrets you'll learn the safer habit: a per-project `.env` file that Git ignores.

</div>

### How PATH finds programs

When you type `ls` or `git`, how does the shell know where that program lives? It looks in the folders listed in an environment variable called `PATH`, in order, and runs the first match:

```bash
echo $PATH
# /Users/sam/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
```

The folders are separated by colons. To see which file a command actually runs, use `which`:

```bash
which git       # /usr/bin/git
which python3   # /opt/homebrew/bin/python3 (or similar)
which uv        # prints nothing if uv isn't on your PATH
```

This explains the most common setup error you'll meet: **"command not found" right after an install**. Usually the installer put the program in a folder such as `~/.local/bin` but your `PATH` doesn't include that folder yet, or your current terminal started before the installer changed your startup file. The fixes, in order: open a new terminal; check the installer's last few lines of output for instructions; and if needed add the folder yourself in your startup file:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

That line puts the new folder in front of the existing list, so programs there win over others with the same name. When two copies of a program exist (very common with Python), `which` tells you which one you're really running.

### Permissions and chmod

Every file has an owner and a set of **permissions**: who may read it, write (change) it, and execute (run) it. `ls -l` shows them:

```text
-rw-r--r--  1 sam  staff  120 Oct 28 10:02 notes.txt
-rwxr-xr-x  1 sam  staff  310 Oct 28 10:05 setup.sh
```

Ignore the first character (`-` for a file, `d` for a folder). The next nine come in three groups of three: the owner, the owner's group, and everyone else. Each group is `r` (read), `w` (write) and `x` (execute), or `-` when that permission is missing. So `notes.txt` can be read and written by `sam` and only read by everyone else, while `setup.sh` can also be executed by anyone.

You change permissions with `chmod` ("change mode"). The one you'll use most adds execute permission so you can run a script:

```bash
chmod +x setup.sh     # add execute for everyone
chmod u+x setup.sh    # add execute for the owner (u = user) only
chmod 600 secrets.txt # owner may read and write; nobody else gets anything
```

The number form is shorthand: each digit is the sum of read (4), write (2) and execute (1), for owner, group and others. `600` is a common choice for files with secrets, such as an SSH key. You've already seen the error that this fixes: "Permission denied" when you try to run a file that isn't executable.

You'll also meet `sudo`, which runs one command as the administrator. Use it to install system packages (`sudo apt install ...`) and almost nothing else. If a command in your own project folder needs `sudo`, something is wrong; stop and find out why.

### Processes

A running program is a **process**. Each one has a number, its **process ID** or PID. To see what's running:

```bash
ps aux | grep python   # every process, filtered to lines mentioning python
```

The second column of `ps aux` is the PID. If a program in your terminal is stuck, press <kbd>Ctrl</kbd> + <kbd>C</kbd> first; that politely asks it to stop. If a program is running somewhere else, such as a web server you started in a terminal you've since closed, use `kill`:

```bash
kill 48213      # ask process 48213 to shut down cleanly
kill -9 48213   # force it to stop immediately (last resort)
```

A common version of this problem: you start a web server, and the next time you try you get "address already in use". An old server is still holding the port. `lsof -i :8000` shows which process is using port 8000, and then you `kill` its PID.

`top` (or the friendlier `htop`, if installed) shows processes live, sorted by how much CPU they use. Press `q` to quit. It's the terminal equivalent of Activity Monitor or Task Manager.

### Finding files and xargs

`find` searches a folder tree for files that match conditions:

```bash
find . -name "*.md"                   # every Markdown file under the current folder
find . -name "*.log" -mtime -1        # .log files modified in the last day
find . -type d -name ".venv"          # folders (-type d) named .venv
```

Pipes, which you learned in Command Line Basics, send one command's *output text* into the next command's *input*. But many commands, like `rm` or `wc`, want file names as *arguments*, not as input text. `xargs` bridges the gap: it reads lines from its input and adds them as arguments to a command.

```bash
find . -name "*.md" | xargs wc -l     # count lines in every Markdown file
find . -name "*.pyc" | xargs rm       # delete compiled Python files
```

File names with spaces break this, because `xargs` splits on spaces. The safe version uses `-print0` and `-0`, which separate names with an invisible "null" character instead: `find . -name "*.md" -print0 | xargs -0 wc -l`. Always run the `find` part alone first, and look at the list, before piping it into anything destructive like `rm`.

### Your first bash script

A **shell script** is a text file of commands that run one after another, exactly as if you'd typed them. Create `project-info.sh`:

```bash
#!/usr/bin/env bash
# project-info.sh: print a quick summary of a project folder.
set -euo pipefail   # stop on errors, unset variables and failed pipes

folder="${1:-.}"    # first argument, or "." if none was given

if [ ! -d "$folder" ]; then
  echo "Error: $folder is not a folder" >&2
  exit 1
fi

echo "Project: $(basename "$(cd "$folder" && pwd)")"
echo "Files:   $(find "$folder" -type f -not -path '*/.git/*' | wc -l | tr -d ' ')"
echo "Markdown files:"
find "$folder" -name "*.md" -not -path '*/.git/*' | sort

for tool in git uv python3; do
  if command -v "$tool" > /dev/null; then
    echo "  found $tool at $(which "$tool")"
  else
    echo "  missing $tool"
  fi
done
```

Make it executable and run it:

```bash
chmod +x project-info.sh
./project-info.sh                  # summarize the current folder
./project-info.sh ~/projects       # summarize another folder
```

Line by line:

- `#!/usr/bin/env bash` is the **shebang**. It tells the operating system which program should run this file. Using `env` finds `bash` on your `PATH`, so it works on macOS and Linux alike.
- `set -euo pipefail` makes the script stop at the first failing command instead of carrying on and doing damage. Start every script with it.
- `$1` is the first argument. `${1:-.}` means "use `$1`, or `.` if it's empty."
- `$( ... )` runs a command and substitutes its output into the line.
- `>&2` sends the error message to **standard error**, a separate output stream for errors, so it doesn't mix with normal output in a pipe. `exit 1` ends the script with a non-zero **exit code**, the number every program returns to say whether it succeeded (0) or failed (anything else). Check the last one with `echo $?`.
- Always wrap variables in double quotes (`"$folder"`) so names with spaces stay in one piece.

You need `./` in front because the current folder isn't on your `PATH`, a deliberate safety choice so a file in a random folder can't pretend to be `ls`.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Scripts versus Python

Bash is great for gluing commands together: a dozen lines that set things up or run tools in order. Once a script needs real logic, such as parsing data, lots of conditions or error recovery, write it in Python instead. You'll learn how in the Python section.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [The Missing Semester: Shell Tools and Scripting](https://missing.csail.mit.edu/2020/shell-tools/), an MIT course on the tools nobody teaches. It covers variables, quoting, exit codes and `find` with more examples than this lesson.
   - Read up to and including "Finding files". Skip the parts about specific tools such as `fd`, `rg` and `fzf` for now.
1. Read the first pages of [Writing Shell Scripts at LinuxCommand.org](https://linuxcommand.org/lc3_writing_shell_scripts.php): "Writing your first script and getting it to work" through "Here Scripts". It is slow and friendly, and it explains permissions and `PATH` from a script writer's point of view.
1. Practice environment variables and `PATH`:
   - Run `echo $PATH | tr ':' '\n'` to print one folder per line. For each of `git`, `uv` and `python3`, run `which` and note which folder it lives in.
   - Add `export MIMIR_NAME="your name"` to your startup file, open a new terminal, and check that `echo $MIMIR_NAME` prints it.
1. Practice processes: run `sleep 600 &` (the `&` runs it in the background), find its PID with `ps aux | grep sleep`, then stop it with `kill` and check that it's gone.
1. Write `project-info.sh` from this lesson in your `mimir-learning-journal` folder, then extend it:
   - Also print the total size of the folder (look up `du -sh`).
   - Print a warning to standard error if the folder has no `README.md`.
   - Run it on two folders, then deliberately pass a path that doesn't exist and check with `echo $?` that the exit code is 1.
   - Paste the script and its output into a journal entry.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What does export do, and how do you make an environment variable permanent?](#environment-variables)
- [Why might you get "command not found" right after installing a tool, and how do you fix it?](#how-path-finds-programs)
- [What does rwxr-xr-x mean, and what does chmod +x do?](#permissions-and-chmod)
- [How do you find and stop a process that's still holding a port?](#processes)
- [Why do you need xargs to pass find results to rm?](#finding-files-and-xargs)
- [What do the shebang line and set -euo pipefail do in a script?](#your-first-bash-script)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [explainshell.com](https://explainshell.com/) takes any shell command you paste and explains each part, which is handy for commands copied from install instructions.
- [ShellCheck](https://www.shellcheck.net/) finds bugs in shell scripts, such as missing quotes. Paste your script in, or install it and run it from the terminal.
- [The Missing Semester: Course overview and the shell](https://missing.csail.mit.edu/2020/course-shell/) is the first lecture of the same course, with more on permissions and connecting programs.
