### Introduction

In this project you'll publish your learning journal as your first public repository, built from scratch with the Git workflow you learned in this section. It starts with the plan you wrote in the "Learning Plan" project and becomes the place where you log your progress for the rest of the curriculum.

It practices everything in the section: creating a repo, staging and committing from the terminal, writing a `.gitignore`, pushing over SSH, and making a change through a branch and a pull request. It's also the first thing on your GitHub profile that says "I'm learning this seriously, and here's my plan."

### Before you start

- You need your `mimir-learning-journal` folder containing `learning-plan.md` from the "Learning Plan" project.
- You need Git configured with your name and email, a GitHub account, and a working SSH key. Run `ssh -T git@github.com` to check. It should greet you by your username.
- Your repo must be named `mimir-learning-journal` and be **public**.
- Everything in this repo will be public. Before you start, reread your learning plan and remove anything you don't want strangers to read, such as personal details about your job or family.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Turn your local `mimir-learning-journal` folder into a Git repository with `git init`, and make your first commit containing `learning-plan.md`. Use the terminal for every Git command in this project, not VS Code's buttons or the GitHub website.
1. Add a `.gitignore` file that ignores at least operating-system clutter (`.DS_Store` and `Thumbs.db`), editor settings folders (`.vscode/`), and `.env` files. Commit it on its own, with a message that explains what it does.
   - Prove it works: create a file called `.env` containing `TEST=1`, run `git status`, and confirm `.env` does not appear. Then delete the file.
1. Write a `README.md` for the journal using what you learned in "Writing a Good README". It should include:
   - A one-line description of what the repo is.
   - A link to Project Mímir and the role you're aiming for.
   - A link to `learning-plan.md`, written as a relative link like `[my learning plan](learning-plan.md)`.
   - A "Progress" section listing the sections you've finished so far, each with a link to its project repo if it has one (for example, `mimir-hello-uv`).
1. Create an empty public repo called `mimir-learning-journal` on GitHub, connect it as `origin` using the SSH address, and push `main`. By now you should have at least three commits, all made from the terminal.
1. Make one change through a pull request.
   - Create a branch, add your first weekly check-in entry to the log in `learning-plan.md` (or update your schedule based on what your first weeks taught you), commit, and push the branch.
   - Open a pull request on GitHub with a title and a description that explains what changed and why. Review the "Files changed" tab, then merge it.
   - Pull the merged `main` back to your computer and delete the branch locally.
1. Check your work with `git log --oneline --graph`. You should see at least four commits, including the merge, and local `main` should match GitHub's.

#### Evidence

The repo is most of the evidence, because GitHub records it for you. Make sure a reviewer can check each of these from the repo page alone:

- The repo link works for someone who isn't logged in, which proves it's public.
- The README links to `learning-plan.md` (and the link works on GitHub), and its "Progress" section links to `mimir-hello-uv` if you've pushed it.
- The commit history shows at least three commits made before the pull request, each with a clear message, including one that adds only `.gitignore`.
- The "Pull requests" tab shows one merged pull request with a description that explains what changed and why. Add its link to the README's "Progress" section.
- The README, or a short `NOTES.md` linked from it, includes two pasted terminal outputs: `git status` with the test `.env` file present but not listed, and `git log --oneline --graph` after the merge, showing the merge commit.
- The calendar screenshot from the "Learning Plan" project is committed next to `learning-plan.md`, if you took one.

#### Extra credit

- Create a GitHub profile README: a special repo named exactly the same as your username, whose README appears on your profile page. Introduce yourself in two or three sentences and link to `mimir-learning-journal`.
- Commit a weekly check-in to the journal every week for the rest of Foundations, so your GitHub contribution graph shows steady progress.
- Find a typo or broken link in Project Mímir's curriculum and fix it by forking the repo and opening a pull request, following the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Submitting your work

Your submission is the public repo itself. A strong `mimir-learning-journal`:

- Has a README that explains in two lines what the repo is, and links to your plan and your project repos.
- Shows a history of at least three small commits with clear messages, not one giant "add everything" commit.
- Has a `.gitignore` that you tested.
- Has one closed, merged pull request with a real description. Anyone can open the "Pull requests" tab, click "Closed", and see it.
- Contains a learning plan you'd be comfortable showing a future employer.
