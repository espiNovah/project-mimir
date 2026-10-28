### Introduction

In this lesson you'll learn the handful of Git commands you'll use most of the time: creating a repo, checking its status, staging and committing changes, reading history, telling Git which files to ignore, and pushing to GitHub. Learn these well and you'll be comfortable with most of what Git asks of you day to day.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to create a repository and check its status.
- The three places a change lives: working directory, staging area and commit history.
- How to write useful commit messages.
- How to read history and see what changed.
- How to keep files out of Git with a `.gitignore`.
- How to connect to GitHub with SSH and push your work.

### The basic workflow

Make a practice repo:

```bash
mkdir ~/projects/git-practice
cd ~/projects/git-practice
git init
git status
```

`git init` turns the current folder into a repo by creating the hidden `.git` folder. `git status` tells you what Git sees right now. Run it constantly; it's the most useful command in Git.

A change moves through three places:

1. The **working directory**: your files as they are on disk. When you edit a file, the change is here, and Git says it's "modified" or "untracked" (a new file Git isn't tracking yet).
1. The **staging area**: the set of changes you've chosen to include in the next commit. You add changes here with `git add`.
1. The **history**: commits. `git commit` takes everything in the staging area and saves it as a new snapshot.

```bash
echo "# Git practice" > README.md
git status                 # README.md is untracked
git add README.md          # stage it
git status                 # now it's listed under "Changes to be committed"
git commit -m "Add README"
git log                    # see the commit (press q to quit)
```

Why have a staging area at all? It lets you decide exactly what goes into each commit. If you fixed a bug and also changed some unrelated wording, you can stage and commit them separately, so each commit does one thing.

### Seeing what changed

```bash
echo "Practicing the basic Git workflow." >> README.md
git diff                   # what changed but isn't staged yet
git add README.md
git diff --staged          # what's staged and about to be committed
git commit -m "Describe the purpose of the repo"
git log --oneline          # a compact, one-line-per-commit history
```

In a diff, lines starting with `+` were added and lines starting with `-` were removed. Reading diffs is a core skill. You'll do it to check your own work before every commit, to review teammates' changes, and later to review code written by AI agents.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Writing commit messages

A good commit message finishes the sentence "If applied, this commit will...". Write "Add file listing table" or "Fix crash on missing folder", not "stuff" or "changes". Keep the first line under about 50 characters. Your future self, reading the history at 11pm while chasing a bug, will thank you.

</div>

### Ignoring files

Some files should never be committed: virtual environments (`.venv/`), Python's cache folders (`__pycache__/`), operating system clutter like macOS's `.DS_Store`, and above all **secrets**, such as files holding API keys. A file called `.gitignore` in the root of your repo lists patterns for Git to ignore:

```text
# Python
__pycache__/
.venv/

# Secrets
.env

# OS clutter
.DS_Store
```

Ignored files don't show up in `git status` and can't be added by accident with `git add .` (which stages everything in the current folder). Projects created with `uv init` already come with a `.gitignore` covering the Python parts.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Never commit a secret

Once a password or API key is pushed to a public repo, assume it's stolen. Automated bots scan GitHub for keys within minutes. Deleting the file in a later commit doesn't help, because it's still in the history. If it ever happens, revoke the key immediately at the provider and create a new one. You'll learn proper secret handling in the "API Keys and Secrets" lesson.

</div>

### Pushing to GitHub with SSH

So far everything is on your computer. To push to GitHub, Git needs to prove it's you. The standard way is an **SSH key**: a pair of files, one private (stays on your computer, never share it) and one public (you give it to GitHub). Generate one:

```bash
ssh-keygen -t ed25519 -C "you@example.com"
```

Press <kbd>Enter</kbd> to accept the default location, and choose a passphrase. Then copy your public key (the file ending in `.pub`) and add it to GitHub under Settings > SSH and GPG keys. The assignment links to GitHub's step-by-step guide, including how to test the connection.

Then create an empty repo on GitHub named `git-practice` (don't add a README, since you already have one), copy its **SSH** address, and connect your local repo to it:

```bash
git remote add origin git@github.com:YOUR-USERNAME/git-practice.git
git push -u origin main
```

A **remote** is a copy of the repo somewhere else; `origin` is the conventional name for the main one. `-u` tells Git to remember that your `main` branch goes to `origin`, so afterward plain `git push` is enough. Refresh the GitHub page and your commits are there. To start from a repo that already exists on GitHub instead, use `git clone` with its SSH address, which downloads it with the remote already set up.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Edit locally, not on GitHub

GitHub lets you edit files in the browser. For now, avoid it: if the GitHub copy and your local copy both change separately, your next push gets rejected and fixing that takes skills you'll learn in the next lesson. Make changes locally, commit, then push.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapter 2 of [Pro Git](https://git-scm.com/book/en/v2).
   - Read [Getting a Git Repository](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository) and [Recording Changes to the Repository](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) carefully, and type the commands as you go.
   - Read [Undoing Things](https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things) so you know your safety net exists. Skim the rest of the chapter.
1. Set up SSH by following GitHub's guide to [connecting to GitHub with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).
   - Do these three pages in order: [generating a new SSH key and adding it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent), [adding a new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account), and [testing your SSH connection](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection). Choose the Linux tab if you're on WSL.
1. Read GitHub's page on [ignoring files](https://docs.github.com/en/get-started/git-basics/ignoring-files), then browse [GitHub's collection of .gitignore templates](https://github.com/github/gitignore) and open `Python.gitignore` to see what a full one looks like.
1. Put your `mimir-hello-uv` project from the previous section on GitHub.
   - It's probably already a Git repo, because `uv init` runs `git init` for you when Git is installed. Run `git status`. If it says "not a git repository" (Git wasn't installed yet when you ran `uv init`), run `git init` first. Then run `git branch -M main` so your branch is named `main` either way. Check that `.venv` is not listed (the `.gitignore` handles that), then stage, commit with a clear message, create an empty `mimir-hello-uv` repo on GitHub, add it as `origin` and push.
   - Make one more small improvement to the README, commit and push it, and confirm on GitHub that both commits appear in the history.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the three places a change can live, and how does a change move between them?](#the-basic-workflow)
- [How do you see what changed since your last commit, and what's in your history?](#seeing-what-changed)
- [What makes a commit message useful?](#seeing-what-changed)
- [What belongs in a .gitignore file?](#ignoring-files)
- [Why must you never commit a secret, even if you delete it in a later commit?](#ignoring-files)
- [Why connect to GitHub with SSH, and why should you edit locally rather than on GitHub?](#pushing-to-github-with-ssh)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [How to Write a Git Commit Message](https://cbea.ms/git-commit/) by Chris Beams is the classic explanation of commit message style.
- [The GitHub Git cheat sheet](https://training.github.com/downloads/github-git-cheat-sheet/) puts the common commands on one page.
- [Oh Shit, Git!?!](https://ohshitgit.com/) gives plain-English fixes for common Git mistakes. It uses mild profanity.
