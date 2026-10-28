### Introduction

So far you've made every commit directly on `main`. That's fine when you work alone on something small, but it's not how teams work. On a real team, `main` is the version everyone trusts, and new work happens on **branches**: separate lines of development where you can experiment without breaking anything. When the work is ready, you open a **pull request** on GitHub to propose merging it into `main`, and teammates review it first.

This is also how AI coding agents fit into a team. An agent works on a branch and opens a pull request, and a human reviews the diff before anything is merged. Knowing this workflow well is what lets you use agents safely.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a branch is and why teams use them.
- How to create, switch between and delete branches.
- How to merge a branch, and what a merge conflict is.
- How to push a branch and open a pull request on GitHub.
- How to merge a pull request and bring the result back to your computer.
- The GitHub flow, the simple workflow most teams use.

### What a branch is

A branch is a movable label pointing at a commit. When you make a new commit on a branch, the label moves forward to it. `main` is just a branch like any other. It's special only by convention.

When you create a new branch, it starts at the commit you're on. From then on, commits you make on the new branch don't affect `main`, and vice versa. Branches are cheap in Git, so make one for every new feature or fix, however small.

```bash
cd ~/projects/git-practice
git branch                     # list branches; * marks the one you're on
git switch -c add-notes        # create a branch called add-notes and switch to it
echo "Branches are movable labels." > notes.md
git add notes.md
git commit -m "Add notes on branches"
git log --oneline --graph --all
```

The last command draws your history as a graph. You'll see `add-notes` one commit ahead of `main`. Now switch back:

```bash
git switch main
ls                             # notes.md is gone: it only exists on add-notes
git switch add-notes
ls                             # and it's back
```

Git swaps the files in your folder to match whichever branch you're on. Commit (or otherwise save) your changes before switching branches, or Git may refuse to switch.

### Merging, and merge conflicts

To bring a branch's work into `main` locally, switch to `main` and merge:

```bash
git switch main
git merge add-notes
git branch -d add-notes        # delete the branch now that its work is merged
```

Usually Git combines the changes automatically. A **merge conflict** happens when both branches changed the same lines of the same file, and Git can't know which version you want. Git stops and marks the file like this:

```text
<<<<<<< HEAD
The version on the branch you're merging into.
=======
The version on the branch you're merging in.
>>>>>>> other-branch
```

To resolve it, edit the file to contain what you actually want, delete the three marker lines, then `git add` the file and `git commit`. VS Code highlights conflicts and offers buttons to accept one side or both, which makes this much less scary. Conflicts are a normal part of teamwork, not a sign that you did something wrong.

### Pull requests

On GitHub, instead of merging locally, you usually push your branch and open a pull request (often shortened to **PR**). A PR is a page that shows the diff between your branch and `main`, lets people comment on specific lines, runs any automated checks, and has a button to merge when everyone is happy.

```bash
git switch -c improve-readme
echo "Learning branches and pull requests." >> README.md
git commit -am "Explain what this repo is for"
git push -u origin improve-readme
```

(`git commit -am` stages every modified tracked file and commits in one step. It doesn't include brand new files, so you still need `git add` for those.)

After the push, GitHub prints a link, and the repo page shows a "Compare & pull request" button. Open the PR, write a title and a description of *what* changed and *why*, and create it. Read through the "Files changed" tab as if you were the reviewer. Then merge it with the button on GitHub.

Your local `main` doesn't know about the merge yet. Bring it up to date:

```bash
git switch main
git pull                       # download and merge new commits from origin
git branch -d improve-readme
```

<div class="lesson-note" markdown="1">

#### The GitHub flow

Most teams follow a loop called the GitHub flow: create a branch from an up-to-date `main`, commit your work, push and open a pull request, get it reviewed, merge, then pull `main` and start the next branch. Your projects in this curriculum are solo, but use this loop anyway. It's the habit employers expect, and your PR history shows you have it.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapter 3 of [Pro Git](https://git-scm.com/book/en/v2), on branching.
   - Read [Branches in a Nutshell](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell) and [Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging) carefully, including the part on basic merge conflicts. Skim the rest of the chapter; rebasing can wait.
1. Play [Learn Git Branching](https://learngitbranching.js.org/), an interactive visual game that shows exactly what each command does to your history.
   - Complete the "Introduction Sequence" levels on the Main tab. Then do the first levels of the "Remote" tab, which cover pushing and pulling.
1. Read GitHub's docs on [about pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) and [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow).
1. Try a course from [GitHub Skills](https://skills.github.com/), GitHub's free, hands-on courses that run inside a real repository.
   - Do [Introduction to GitHub](https://github.com/skills/introduction-to-github). If you have time, also do [Resolve merge conflicts](https://github.com/skills/resolve-merge-conflicts).
1. Practice a conflict on purpose.
   - In `git-practice`, create a branch and change the first line of `README.md`, then commit. Switch to `main`, change the same line differently, and commit. Merge the branch into `main`, resolve the conflict in VS Code, and commit the result. Run `git log --oneline --graph` to see the two lines of history joining.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Source control in VS Code](https://code.visualstudio.com/docs/sourcecontrol/overview) shows how to stage, commit, switch branches and resolve conflicts from the editor.
- [Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) on GitHub Docs walks through every option on the PR form.
