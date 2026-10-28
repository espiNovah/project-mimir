### Introduction

Imagine writing an essay by saving copies called `essay_final.docx`, `essay_final_v2.docx` and `essay_final_REALLY_final.docx`. Now imagine five people editing the same essay at once. **Version control** is software that solves this properly: it records every change to a set of files, who made it and why, and lets many people work on the same files without overwriting each other.

**Git** is the version control system almost every software team uses. **GitHub** is a website that hosts Git projects online. You'll use both every day: to save your work, to undo mistakes, to collaborate, and to show employers what you've built. AI coding agents use Git too. They commit their changes and open pull requests, and reviewing that work means reading Git history. In this lesson you'll learn what Git is, install it, and set it up.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What version control is and what problems it solves.
- How Git thinks about your project: repositories, commits and snapshots.
- The difference between Git and GitHub.
- How to install Git and check your version.
- How to configure Git with your name, email and default branch.
- How to create a GitHub account.

### What Git actually does

Git keeps track of a folder called a **repository** (or **repo**). Inside a repo, Git stores a hidden history in a `.git` folder. You work on your files normally, and whenever you reach a point worth keeping, you make a **commit**: a saved snapshot of the whole project at that moment, with a message describing what changed.

Over time, the commits form a timeline. You can:

- **See history:** what changed, when, by whom, and the message explaining why.
- **Compare versions:** exactly which lines changed between any two commits.
- **Go back:** restore a file, or the whole project, to an earlier commit.
- **Work in parallel:** make an experimental copy of the timeline (a **branch**), and merge it back in if it works.

Git is **distributed**, which means every copy of a repo contains the entire history. Your laptop has a full copy; GitHub has a full copy; a teammate has a full copy. If GitHub went down tomorrow, nobody would lose their history.

### Git versus GitHub

People mix these up, so it's worth being precise:

- **Git** is a program that runs on your computer. It works entirely offline.
- **GitHub** is a website owned by Microsoft that stores copies of Git repos online, and adds collaboration features on top: pull requests, issues, code review and automation. GitLab and Bitbucket are similar services.

You'll use Git in the terminal to make commits, then **push** them to GitHub so they're backed up and visible. GitHub is also where your portfolio lives. Recruiters and hiring managers will look at your GitHub profile, so everything you build in this curriculum ends up there.

### Installing and configuring Git

Check whether Git is already installed:

```bash
git --version
```

- **macOS:** if Git isn't installed, running `git --version` offers to install Apple's command line developer tools, which include Git. Accept and wait for it to finish.
- **Windows (WSL) and Linux:** run `sudo apt update && sudo apt install -y git` in your Ubuntu terminal.

Any version from 2.28 onward works with this curriculum. Next, tell Git who you are. Every commit records a name and email, so set them once:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global --list
```

The third line makes new repos start on a branch called `main`, which matches GitHub. The last line shows your settings so you can check them.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Keeping your email private

Commits on public repos show the author's email address. If you'd rather not publish your personal email, GitHub gives you a private "noreply" address. Find it in your GitHub email settings after you create your account, and use it for `user.email`. The assignment links to instructions.

</div>

### Creating a GitHub account

Sign up for a free account at github.com. Pick your username carefully. It appears in the address of every project you publish (`github.com/your-username/project-name`), and employers will see it. Something close to your real name is a safe choice. Turn on two-factor authentication when GitHub prompts you; it protects the account that holds your portfolio.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapter 1 of [Pro Git](https://git-scm.com/book/en/v2), the free official Git book.
   - Read [About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control) and [What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F) carefully. The second one explains snapshots and the three states of a file, which you'll use in the next lesson.
   - Skim the rest of chapter 1, and use [First-Time Git Setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup) to check your configuration.
1. Watch or read the [Version Control and Git lecture from MIT's Missing Semester](https://missing.csail.mit.edu/2026/version-control/). It explains how Git models history, which makes the commands much less mysterious.
   - Don't worry if the later parts feel advanced. Come back to it after the next two lessons.
1. Create your GitHub account by following [Creating an account on GitHub](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github).
   - Then follow [Setting your commit email address](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address) if you want to keep your email private, and update `user.email` to match.
1. Install and configure Git using the commands in this lesson, and confirm with `git config --global --list` that your name, email and default branch are set.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [About Git on GitHub Docs](https://docs.github.com/en/get-started/using-git/about-git) is a short, friendly overview of Git and how GitHub uses it.
