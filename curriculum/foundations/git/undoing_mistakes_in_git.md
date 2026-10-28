### Introduction

Everyone makes mistakes with Git. You commit to the wrong branch, commit a file you meant to leave out, write a typo in a commit message, or edit a file into a mess and wish you could start over. The good news is that Git almost never truly loses work you've committed. Once you know a handful of commands, nearly every mistake becomes a thirty-second fix instead of a panic.

This matters even more when you work with AI coding assistants later in the curriculum. An assistant can change a dozen files in seconds. If you commit before letting it loose, undoing a bad change is one command. This lesson teaches those commands and then has you practice them on a throwaway repository, so that the first time you use them isn't on real work.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Throwing away uncommitted changes with `git restore`.
- Unstaging files you added by mistake.
- Fixing the last commit with `git commit --amend`.
- Moving a branch back with `git reset`, and the difference between `--soft`, `--mixed` and `--hard`.
- Undoing a commit safely with `git revert`.
- Setting work aside with `git stash`.
- Recovering "lost" commits with `git reflog`.

### Three places to undo from

Recall from Git Basics that a change lives in one of three places: the **working directory** (your files on disk), the **staging area** (what `git add` has queued for the next commit), and the **commit history**. Every undo command works on one or more of those places, so the first question to ask is always "where is the thing I want to undo?"

- An edit you haven't staged lives only in the working directory.
- A file you ran `git add` on is in the staging area.
- A commit is in the history. Whether you've pushed it to GitHub yet changes which tool is safe.

`git status` answers the question for you, and it even prints hints about which command to use. Read it before undoing anything.

### Discarding changes with restore

You edited `notes.md`, made a mess, and want it back the way it was at the last commit:

```bash
git restore notes.md      # throw away unstaged changes to one file
git restore .             # throw away all unstaged changes in this folder and below
```

This is one of the few Git commands that destroys work for good. The edits you discard were never committed, so Git has no copy of them. Run `git diff` first and look at what you're about to lose.

If you staged a file by accident, say a `.env` file or a huge data file, take it out of the staging area without touching the file itself:

```bash
git restore --staged .env   # unstage; the file on disk is unchanged
```

You may see older tutorials use `git checkout -- file` and `git reset HEAD file` for these jobs. They still work, but `git restore` was added to make the intent clearer, and it's what `git status` now suggests.

### Fixing the last commit

You just committed and noticed a typo in the message, or forgot to include a file. If you haven't pushed yet, `--amend` replaces the last commit with a corrected one:

```bash
git add forgotten_file.py
git commit --amend -m "Add quiz scoring and its tests"
```

Without `-m`, Git opens your editor with the old message so you can edit it. `--amend --no-edit` keeps the message and just adds the newly staged changes.

Amending doesn't edit a commit in place. It makes a brand-new commit with a different ID and moves your branch to point at it. That's fine for a commit only you have seen, and a problem for one you've already pushed, which is the theme of the rest of this lesson.

### Moving a branch with reset

A branch is just a label pointing at a commit. `HEAD` means "the commit you're on now," and `HEAD~1` means "one commit before that." `git reset` moves the current branch's label to a different commit. Its three modes differ in what happens to the changes from the commits you move past:

| Command | History | Staging area | Your files |
| --- | --- | --- | --- |
| `git reset --soft HEAD~1` | last commit removed | changes stay staged | unchanged |
| `git reset HEAD~1` (`--mixed`, the default) | last commit removed | changes unstaged | unchanged |
| `git reset --hard HEAD~1` | last commit removed | cleared | **changes deleted** |

When to use each:

- `--soft`: "I want to redo that commit." Everything is still staged, so you can recommit it differently, for example squashing three messy commits into one with `git reset --soft HEAD~3` followed by a single `git commit`.
- `--mixed`: "I want to uncommit and re-stage things more carefully," such as splitting one big commit into two.
- `--hard`: "I want those commits and their changes gone." This also discards any uncommitted edits in your working directory, so run `git status` first and make sure there's nothing there you want.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Don't rewrite history you've pushed

`reset` and `--amend` rewrite history: the commits you move past disappear from the branch. If you've already pushed them, your copy and GitHub's copy now disagree, and pushing again requires `--force`, which can wipe out a teammate's work. For commits that are already pushed, use `git revert` instead.

</div>

### Undoing safely with revert

`git revert` undoes a commit by adding a **new** commit that does the exact opposite. If commit `a1b2c3d` added three lines, the revert commit removes them. History only moves forward, so it's safe on shared branches and on anything you've pushed:

```bash
git log --oneline          # find the ID of the commit to undo
git revert a1b2c3d         # opens your editor with a message like "Revert ..."
git push                   # a normal push, no force needed
```

The bad commit stays in the history along with the revert, which is a feature: anyone reading the log can see what happened and why. Revert is the right tool when something you shipped broke and you want it undone now, while you work out the proper fix.

### Setting work aside with stash

You're halfway through a change when you need a clean working directory, perhaps to pull your teammate's fix or switch to another branch. You aren't ready to commit. `git stash` saves your uncommitted changes onto a stack and resets your files to the last commit:

```bash
git stash push -m "half-done retry logic"   # save and clean up
git status                                  # clean
# ...pull, switch branches, fix something else...
git stash list                              # see what's stashed
git stash pop                               # reapply the newest stash and remove it
```

By default, stash ignores **untracked** files (new files Git has never seen). Add `-u` to include them. Stashes are easy to forget, so treat them as a short-term pocket, not storage. If something will sit for more than a day, commit it on a branch instead.

### Recovering lost commits with reflog

You ran `git reset --hard HEAD~3` and realize one of those three commits mattered. Is it gone? Almost certainly not. Git keeps a private diary, the **reflog**, of every position `HEAD` has been at in your local repo, including commits that no branch points to anymore:

```bash
git reflog
```

```text
9f3e2a1 HEAD@{0}: reset: moving to HEAD~3
c47d8b0 HEAD@{1}: commit: Add retry with backoff
5e1a9f2 HEAD@{2}: commit: Parse retry-after header
...
```

Find the line just before your mistake, then move your branch back to it:

```bash
git reset --hard c47d8b0
```

Your commits are back. The reflog only exists on your machine, and Git eventually cleans out very old entries (after about 90 days by default), but for the "I just did something terrible" moment it's a reliable safety net. The one thing it can't recover is work you never committed. That's the real lesson here: commit early and often, because committed work is very hard to lose.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Make a safety branch first

Before any risky operation, run `git branch backup-before-reset`. It costs nothing, and if the operation goes wrong you can get everything back with `git reset --hard backup-before-reset`. Delete it with `git branch -D backup-before-reset` once you're happy.

</div>

### Choosing the right command

| Situation | Command |
| --- | --- |
| Throw away unstaged edits to a file | `git restore file` |
| Unstage a file but keep the edits | `git restore --staged file` |
| Fix the message or contents of the last, unpushed commit | `git commit --amend` |
| Undo unpushed commits but keep the changes | `git reset --soft` or `git reset` |
| Undo unpushed commits and delete the changes | `git reset --hard` |
| Undo a commit that's already pushed | `git revert` |
| Put unfinished work aside for a moment | `git stash` |
| Get back commits after a bad reset | `git reflog`, then `git reset --hard` |

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Git Basics: Undoing Things](https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things) from the free Pro Git book. It's short and shows the same commands with the exact `git status` output you'll see.
1. Read [Reset Demystified](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified), also from Pro Git, for diagrams of what `--soft`, `--mixed` and `--hard` do to each of the three places.
   - Read up to and including "Reset With a Path". The rest is optional.
1. Skim [How to undo (almost) anything with Git](https://github.blog/open-source/git/how-to-undo-almost-anything-with-git/) from GitHub's blog. It's organized by scenario, so it's a good page to bookmark for real emergencies.
1. Do the hands-on lab. Create a throwaway repo outside your other projects so you can't hurt real work: `mkdir ~/git-undo-lab && cd ~/git-undo-lab && git init`. Make five small commits, each adding a line to `story.txt`. Then:
   - Edit `story.txt`, check `git diff`, and discard the edit with `git restore`.
   - Create `secret.env`, `git add` it, then unstage it with `git restore --staged`.
   - Make a commit with a typo in the message, and fix it with `--amend`. Compare `git log --oneline` before and after: did the ID change?
   - Run `git reset --soft HEAD~2`, check `git status`, and recommit the changes as one commit.
   - Run `git reset --hard HEAD~2`. Use `git reflog` to find the commits you just "lost" and bring them back.
   - Use `git revert` on one commit and look at the log to see the new commit it added.
   - Start an edit, `git stash` it, make a different commit, then `git stash pop`.
   - Write a journal entry in `mimir-learning-journal` listing each command you ran and one sentence on what it did. Delete the lab folder when you're done.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How do you discard edits to a file, and why can't Git get them back afterward?](#discarding-changes-with-restore)
- [How do you add a forgotten file to the commit you just made?](#fixing-the-last-commit)
- [What's the difference between reset --soft, --mixed and --hard?](#moving-a-branch-with-reset)
- [Why should you use revert rather than reset for a commit you've pushed?](#undoing-safely-with-revert)
- [When would you use git stash, and what does it leave out by default?](#setting-work-aside-with-stash)
- [How do you recover commits after a bad reset --hard?](#recovering-lost-commits-with-reflog)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Oh Shit, Git!?!](https://ohshitgit.com/) gives plain-English fixes for the most common Git mistakes. It uses mild profanity.
- [Learn Git Branching](https://learngitbranching.js.org/) is an interactive visual tutorial. Its "Reversing Changes in Git" level animates reset and revert on a commit graph.
- [Stashing and Cleaning](https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning) in Pro Git covers stash in depth, plus `git clean` for deleting untracked files.
