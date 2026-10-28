### Introduction

The **command line** (also called the terminal or the shell) is a text interface to your computer. Instead of clicking icons, you type commands. It looks old-fashioned, but almost every tool you'll use as an AI engineer lives here: Python, Git, package managers, servers, cloud tools and coding agents. Many of the agents you'll build later in this curriculum work by running shell commands themselves, so understanding the shell is understanding what your agents are doing.

This lesson gets you set up with a terminal and comfortable with the dozen commands you'll use every day.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What the terminal, the shell and the prompt are.
- How to get a good terminal on macOS, Windows (with WSL) and Linux.
- How files and folders are organized as paths.
- How to navigate and manage files from the terminal.
- How to combine commands with pipes and redirection.
- How to get help on a command.

### Getting a terminal

**On macOS**, open the Terminal app (press <kbd>Cmd</kbd> + <kbd>Space</kbd> and type "Terminal"). The default shell is called `zsh`.

**On Linux**, open your distribution's terminal app (often <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd>). The default shell is usually `bash`.

**On Windows**, we recommend you install **WSL**, the Windows Subsystem for Linux. WSL runs a real Linux system inside Windows. Most AI tooling, documentation and servers assume a Unix-like system (Linux or macOS), and using WSL means every command in this curriculum works for you exactly as written. Follow [Microsoft's WSL install guide](https://learn.microsoft.com/en-us/windows/wsl/install): open PowerShell as Administrator, run `wsl --install`, restart, and create a Linux username and password when Ubuntu starts for the first time. From then on, open "Ubuntu" from the Start menu whenever this curriculum says "open a terminal."

<div class="lesson-note lesson-note--warning" markdown="1">

#### Windows: keep your work inside Linux

Once you have WSL, keep your project folders inside the Linux file system (your Linux home folder, `~`), not in `C:\Users\...`. Tools run much faster there, and you avoid confusing permission problems. VS Code can open those folders directly, as you'll see in the next lesson.

</div>

### Paths and navigation

When you open a terminal, you see a **prompt**, a short bit of text that ends in `$` or `%` and waits for you to type. You are always "in" a folder, called the **working directory**. Folders (also called **directories**) are nested inside each other, and a **path** describes where something is:

- `/Users/sam/projects/notes.txt` is an **absolute path**. It starts at the top of the file system, `/` (called the root).
- `projects/notes.txt` is a **relative path**. It starts from your working directory.
- `~` is a shortcut for your home folder. `.` means "the current folder" and `..` means "the folder above this one."

Try these, one at a time. Lines starting with `#` are comments for you; you don't type them.

```bash
pwd              # print working directory: where am I?
ls               # list what's in this folder
ls -la           # list everything, including hidden files, with details
cd ~             # change directory to your home folder
mkdir practice   # make a new directory called practice
cd practice      # move into it
cd ..            # move back up one level
```

Most commands take **options** (also called flags), like the `-la` in `ls -la`, and **arguments**, like the `practice` in `mkdir practice`.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Let the terminal type for you

Press <kbd>Tab</kbd> to autocomplete file and folder names. Press the up arrow to bring back previous commands. Press <kbd>Ctrl</kbd> + <kbd>C</kbd> to stop a command that's running or stuck. These three keys will save you hours.

</div>

### Working with files

```bash
cd ~/practice
touch notes.txt               # create an empty file
echo "first line" > notes.txt # write text into a file (replaces its contents)
echo "second line" >> notes.txt # add text to the end of a file
cat notes.txt                 # print a file's contents
cp notes.txt backup.txt       # copy a file
mv backup.txt old.txt         # move or rename a file
rm old.txt                    # delete a file
```

Be careful with `rm`. The terminal has no trash can, so deleted files are gone. `rm -r folder` deletes a folder and everything inside it, so double-check the path before you press <kbd>Enter</kbd>.

### Pipes and redirection

The real power of the shell is combining small commands. The `>` and `>>` you used above are **redirection**: they send a command's output into a file instead of the screen. A **pipe**, written `|`, sends one command's output into another command as input.

```bash
ls -la ~ | wc -l          # count how many lines ls prints (wc = word count)
cat notes.txt | grep second   # show only lines containing "second"
history | grep mkdir      # find every mkdir command you've run
```

`grep` searches text for a pattern and `wc -l` counts lines. Chaining tools like this is how you'll inspect logs, search code and check data later on, and it's exactly what coding agents do when they explore a project.

### Getting help

You don't have to memorize options. Most commands describe themselves:

```bash
man ls        # open the manual for ls (press q to quit)
grep --help   # a shorter summary for many commands
```

Manual pages are dense at first. Skim for the option you need, and when they don't help, search the web or ask an AI to explain a command. Just make sure you understand any command before you run it, especially if it deletes or moves things.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Set up your terminal.
   - Windows: follow [Microsoft's WSL install guide](https://learn.microsoft.com/en-us/windows/wsl/install), then read [Set up a WSL development environment](https://learn.microsoft.com/en-us/windows/wsl/setup/environment) up to and including the section on updating and upgrading packages.
   - macOS and Linux: open your terminal and run `echo $SHELL` to see which shell you're using.
1. Watch or read the first lecture of [MIT's Missing Semester of Your CS Education](https://missing.csail.mit.edu/), "Course Overview + Introduction to the Shell". This free MIT course teaches the practical tools that computer science classes usually skip.
   - Do the exercises at the end of the lecture. Skip any that use commands you don't have yet.
   - Bookmark the course. You'll come back to its later lectures, including the one on agentic coding.
1. Work through [The Unix Shell from Software Carpentry](https://swcarpentry.github.io/shell-novice/), a hands-on beginner lesson that comes with a sample data set.
   - Do episodes 1 through 4 (introducing the shell, navigating files and directories, working with files and directories, and pipes and filters). Type every command yourself.
1. Practice without instructions.
   - In your home folder, create a folder called `shell-practice` with two subfolders, `drafts` and `final`. Create three text files in `drafts`, each with a line of text, using `echo` and `>`. Move one file to `final`, copy another into `final`, and use `ls | wc -l` to count how many files are in each folder. Then delete the whole `shell-practice` folder in one command.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why should Windows users keep their work inside the Linux file system in WSL?](#getting-a-terminal)
- [What is the difference between an absolute path and a relative path?](#paths-and-navigation)
- [How do you create, copy, move and delete files from the terminal, and why should you be careful with deleting?](#working-with-files)
- [What does a pipe do, and how is it different from redirecting output to a file?](#pipes-and-redirection)
- [How can you find out what a command does and which options it accepts?](#getting-help)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Odin Project's Command Line Basics](https://www.theodinproject.com/lessons/foundations-command-line-basics) covers the same ground from a different angle, with tips on opening files in VS Code from the terminal.
- [Learning the Shell at LinuxCommand.org](https://linuxcommand.org/lc3_learning_the_shell.php) is a free, gentle tutorial that goes further, from wildcards to permissions.
