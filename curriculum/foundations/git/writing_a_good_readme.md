### Introduction

A **README** is the file GitHub shows on a repository's front page. For most visitors, including recruiters and hiring managers skimming your profile, it's the only file they'll read. A great project with an empty README looks like an unfinished one. A clear README tells people what the project does, proves it works, and shows how you think.

Every project in this curriculum needs a README, so in this lesson you'll learn what goes in one, how to write it in Markdown so it looks good on GitHub, and how to check that its instructions actually work. You'll finish by rewriting the README of a repo you already have.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Who reads a README, and what each reader needs from the first screen.
- The sections a good project README contains.
- The Markdown you need, plus GitHub extras like badges, tables and collapsible sections.
- How to write a quick start and test it from a fresh clone.
- How to show evidence that your project works.
- How to be honest about limitations and about AI help.

### Who reads your README

Before you write anything, picture who will open the page. There are four usual readers, and they want different things:

- **A stranger deciding whether your project is interesting.** They'll give it about 30 seconds. The first two lines must say what it is and what problem it solves.
- **A hiring manager skimming your profile.** They might look at five of your repos in five minutes. They want to see quickly that the thing works, that you made sensible decisions, and that you judge your own results honestly.
- **A teammate, or anyone who wants to run it.** They need exact steps that work on a computer that isn't yours, and they need to know what settings the project expects.
- **Future you.** In six months you'll have forgotten which command starts the program, why you picked one library over another, and what the weird environment variable is for. The README is a note to yourself.

The part that matters most is the **first screen**: what appears on GitHub before anyone scrolls. Every reader sees it, and most see nothing else. Put the essentials there: the project name, one sentence saying what it does, a picture or sample output, and (once you have them) a badge or two showing it's tested. The detailed sections go below, for the readers who decide to stay.

### What goes in a project README

Not every project needs every section, but most of yours will use this shape, roughly in this order:

1. **Title and one-line description.** Say what it does in plain words. "A command-line tool that lists files as a table" beats "A blazingly fast file explorer." Avoid hype words; they make readers suspicious.
1. **Demo.** Real output, a screenshot or a short GIF. This is the quickest way to prove the project exists and runs. Paste actual output from your terminal, never a made-up example.
1. **Quick start** (often called "Getting started" or "Installation"). What to install first, then exact, copyable commands that take someone from nothing to a running program. More on this below, because it's the section most often broken.
1. **Usage.** The commands or options a user will type after setup, with an example of each. For a command-line tool, show the most common two or three invocations and what they print.
1. **Configuration.** Any settings the program reads, especially environment variables, with what each one does and its default.
1. **Tests.** The one command that runs the tests, such as `uv run pytest`, and what a passing run looks like. You'll start writing tests in the Python section; until then, leave this out rather than pretend.
1. **Project structure.** For anything bigger than one or two files, a short map of the important files and folders, so a reader knows where to look.
1. **How it works.** Two or three sentences on the approach and the main libraries. Link to the code for the details.
1. **Limitations and what I learned.** What doesn't work yet, and what you'd do differently. More on this below.
1. **License.** The terms under which other people may use your code. Without a license, nobody else is legally allowed to reuse it, even if the repo is public. For portfolio projects, the MIT license is a common, simple choice: GitHub offers it when you create a repo, and you can add a `LICENSE` file later. A one-line "Licensed under MIT, see [LICENSE](LICENSE)" at the bottom is enough.

A project structure section can be as simple as a short annotated tree:

```text
mimir-hello-uv/
├── main.py          # the whole program: reads a folder, prints a table
├── pyproject.toml   # project settings and dependencies (managed by uv)
├── uv.lock          # exact versions of every dependency
└── README.md        # this file
```

### Configuration without leaking secrets

You met **environment variables** in Shell Scripting and Your Environment: named values handed to a program when it starts. Soon your projects will read API keys and other settings this way. A README has to tell readers which variables to set, without ever showing a real secret.

The rule is simple: **document names, never values.** A table works well:

```markdown
| Variable | Required | What it does |
| --- | --- | --- |
| `WEATHER_API_KEY` | Yes | Your key from the weather service. Never commit it. |
| `DEFAULT_CITY` | No | City to use when none is given. Defaults to `London`. |
```

When you write the README, read every code block and screenshot you paste. Terminal output and screenshots are the usual way keys leak: a printed config, a URL with `?key=...` in it, or a settings screen. Replace anything secret with a placeholder like `your-key-here` before committing. Remember from Git Basics that once a secret is pushed to GitHub, deleting it in a later commit isn't enough, because it's still in the history. You'll have to cancel the key and make a new one. In API Keys and Secrets you'll add the matching habit of a committed `.env.example` file that lists the variable names with fake values.

### Markdown in five minutes

READMEs are written in **Markdown**, which you first met in the Learning Plan project. The syntax you'll use most:

````markdown
# Big heading
## Smaller heading

Plain paragraph text. **Bold**, *italic*, and `inline code`.

- A bullet point
- Another one

1. A numbered step
1. Another step (GitHub numbers them for you)

[Link text](https://example.com)
[My learning plan](learning-plan.md)
![Screenshot of the file table](docs/screenshot.png)

```bash
uv run main.py ~/projects
```
````

A few habits make the result render well on GitHub:

- **One `#` heading, at the top.** Use `##` for the sections below it. GitHub builds a table of contents from your headings (the list icon at the top right of the README), so clear headings help long READMEs.
- **Code blocks with a language.** Put a line of three backticks above and below a block, and add the language after the first set: `bash` for commands, `python` for code, `text` for plain output. The language turns on syntax highlighting.
- **Relative links for files in your repo.** `[my learning plan](learning-plan.md)` points to a file next to the README. It keeps working if you rename your GitHub account or someone forks the repo, unlike a full `https://github.com/...` link.
- **Images committed to the repo.** Save screenshots in a folder such as `docs/` and link them with a relative path. Always write a short description in the square brackets: it's shown if the image fails to load, and screen readers read it aloud.

VS Code previews Markdown: open a `.md` file and press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd> (<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd> on macOS). The preview is close to GitHub's but not identical, so check the real page after you push.

### GitHub extras: badges, tables and collapsible sections

GitHub's Markdown adds a few features you'll see in almost every serious repo.

**Tables** use pipes and a row of dashes, as in the configuration example above. They're good for options, settings and results.

**Badges** are small images, usually at the top of a README, that show a live status. The most useful one for you will be a **CI badge**. CI (continuous integration) means GitHub automatically runs your checks, such as your tests, every time you push. You'll set that up in Linting, Formatting and CI, using a feature called **GitHub Actions**, and GitHub then gives you a badge that turns green when the checks pass and red when they fail:

```markdown
![CI](https://github.com/your-username/mimir-expense-tracker/actions/workflows/ci.yml/badge.svg)
```

A green badge is evidence that someone else's computer ran your tests. Don't add badges that only decorate, like a "made with Python" badge. One honest status badge is worth more than ten decorative ones.

**Collapsible sections** hide long material, such as full terminal output, until the reader clicks. They use two HTML tags that GitHub allows inside Markdown. Leave a blank line after `<summary>` so the Markdown inside renders:

````markdown
<details>
<summary>Full output for a folder with 40 files</summary>

```text
(paste the long output here)
```

</details>
````

Use this to keep the first screen short without throwing information away.

### Writing a quick start that works

The quick start is the section most likely to be wrong, because it works perfectly on the one computer it was never meant for: yours. Your machine already has the right Python, the dependencies installed, a `.venv` folder, maybe a `.env` file, and files you forgot to commit. A stranger's machine has none of that.

A good quick start:

- **Lists prerequisites first**, with links: "Requires [uv](https://docs.astral.sh/uv/) and Git." uv will fetch the right Python version itself.
- **Gives every command in a copyable code block**, one command per line, in order, starting from `git clone`.
- **Ends with what success looks like**: "You should see a table titled Files in ...". Then the reader knows it worked.
- **Uses the HTTPS clone address** in the example. Your SSH address only works for people who have set up SSH keys with GitHub; HTTPS works for everyone.

Then **test it from a fresh clone**. This is the step almost everyone skips, and it catches most broken READMEs:

```bash
cd ~                                  # somewhere outside your project
mkdir readme-test && cd readme-test
git clone https://github.com/your-username/mimir-hello-uv.git
cd mimir-hello-uv
uv run main.py                        # now follow your README, line by line
```

Type each command exactly as the README says, no more. If you have to do anything the README didn't tell you, such as installing something, creating a file or changing folder, the README is wrong. Fix it, commit, push, and test again. A fresh clone also exposes files you forgot to commit, because they simply won't be there. When you're done, delete the test folder with `cd ~ && rm -rf readme-test`.

A fresh clone on your own machine still shares your installed tools, so it can't catch everything. Later, when CI runs your project on a clean computer in the cloud, you'll get a stricter version of the same check for free.

### Showing evidence

Anyone can claim their project works. A strong README **shows** it. That's why every project in this curriculum asks for evidence, and why the evidence gets more demanding as you go.

Right now, evidence means real output: pasted terminal results, a screenshot, a link to a merged pull request. Later projects will ask for more:

- **From the Expense Tracker project on:** passing tests and a CI badge showing they run automatically on every push.
- **From the LLM-Powered API project on:** an **eval score**, which measures how often your AI system gives a good answer, reported with a **confidence interval** (a range that says how sure you can be of the number), plus **traces**, saved records of every call your program made to a model.

You don't need to understand those yet; the lessons before each project teach them. The habit to start now is putting proof near the top of the README, in an `## Evidence` or `## Results` section, so a reviewer doesn't have to clone your project to believe it. A numbers table is a natural fit:

```markdown
## Results

| Check | Result |
| --- | --- |
| Folders tested | 3 (empty, 5 files, 200 files) |
| Sizes match `ls -la` | Yes, all 3 |
| Time for 200 files | under 1 second |
```

### Being honest about limits and AI help

A short **Limitations** or **Known issues** section, with lines like "Doesn't handle folders with thousands of files quickly" or "Only tested on macOS and Ubuntu", makes you look more credible, not less. Experienced readers know every project has limits. If you don't name them, they assume you didn't notice. In AI engineering especially, being clear about where a system fails is a core professional skill, and later you'll measure those failures with evals.

The same goes for the **What I learned** section. Make it honest and specific. "Handling missing folders taught me how to stop a program with an exit code" is worth more than "I learned a lot." Mention one thing you'd do differently.

Be open about **AI assistance**, too. Using AI coding assistants is normal, and you'll learn to use them well later in Foundations. What matters to an employer is that you understand and can defend every line. A sentence such as "I wrote the core logic myself and used an AI assistant to suggest test cases, which I reviewed and edited" is honest and shows judgment. Hiding it is risky: in an interview, you'll be asked to explain your code, and the gap shows.

### A before and after example

Here's a README many beginners push:

```markdown
# project1

My project. Run main.py.
```

A stranger learns nothing: not what it does, how to run it, or whether it works. Here's the same project after this lesson:

````markdown
# mimir-hello-uv

A command-line tool that lists the files in a folder as a table, with each
file's extension and size.

```text
            Files in examples
┏━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Name        ┃ Extension ┃ Size (bytes) ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ notes.txt   │ .txt      │ 512          │
│ photo.png   │ .png      │ 20480        │
└─────────────┴───────────┴──────────────┘
```

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and Git.

```bash
git clone https://github.com/your-username/mimir-hello-uv.git
cd mimir-hello-uv
uv run main.py
```

You should see a table of the files in the current folder.

## Usage

```bash
uv run main.py                  # list the current folder
uv run main.py ~/projects       # list another folder
uv run main.py | grep py        # combine with shell tools
```

## How it works

`main.py` uses Python's `pathlib` to read the folder and the
[Rich](https://rich.readthedocs.io/) library to print the table.

## Evidence

Checked against `ls -la` on three folders; names and sizes matched.
See [the pull request that added sorting](https://github.com/your-username/mimir-hello-uv/pull/1).

## Limitations

- Lists files only, not folders, and doesn't look inside subfolders.
- Slow on folders with tens of thousands of files.

## What I learned

How uv manages dependencies, and how a program reports errors with exit
codes. I'd add tests next. I used an AI assistant to explain Rich's table
options; I wrote and checked the code myself.

## License

MIT, see [LICENSE](LICENSE).
````

Notice that the first screen (title, description and sample output) answers the stranger's question, the quick start serves someone running it, the evidence and limitations serve the hiring manager, and the usage section serves future you. The example output and numbers above are illustrations. Yours must be real.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Make a README](https://www.makeareadme.com/), a short guide to what a README should contain and why.
   - Read the whole page, including the suggested sections.
1. Read GitHub's [About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) to learn where GitHub looks for READMEs, how it displays them, and how relative links and images work.
1. Work through [Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) on GitHub Docs.
   - Focus on headings, text styling, code blocks, links, relative links, images and lists.
   - Then skim [Organizing information with tables](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-tables) and [Organizing information with collapsed sections](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections), which cover the two GitHub extras from this lesson.
1. Rewrite your `mimir-hello-uv` README using the structure in this lesson. This is the hands-on practice, on a repo you already pushed in Git Basics.
   - Do it on a branch and merge it through a pull request, as you learned in Branches and Pull Requests.
   - Include at least: a one-line description, real sample output in a `text` code block, a quick start, a usage section with two or three commands, a limitations section, and a "What I learned" section that mentions any AI help honestly.
   - Add a license. On GitHub, use "Add file", "Create new file", name it `LICENSE`, and pick the MIT template, or create it on your computer by copying the text from [choosealicense.com](https://choosealicense.com/licenses/mit/). Then link it from the README.
   - Test your quick start from a fresh clone, exactly as in "Writing a quick start that works". Fix anything that doesn't work and push the fix.
1. Check the result on GitHub as a stranger would. Open the repo in a private (incognito) browser window and look only at the first screen. Can you tell what the project is and that it works without scrolling? Click every link and check every image loads.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Who reads your project README, and what should the first screen show them?](#who-reads-your-readme)
- [What sections does a good project README contain, and why does it need a license?](#what-goes-in-a-project-readme)
- [How do you document environment variables without leaking a secret?](#configuration-without-leaking-secrets)
- [Why should links to files in your own repo be relative rather than full GitHub addresses?](#markdown-in-five-minutes)
- [Why test your quick start from a fresh clone, and what does that catch?](#writing-a-quick-start-that-works)
- [What does a CI badge prove, and what other evidence will later projects ask your README to show?](#showing-evidence)
- [Why is being honest about limitations and AI assistance a strength rather than a weakness?](#being-honest-about-limits-and-ai-help)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Awesome README](https://github.com/matiassingers/awesome-readme) is a curated list of well-written READMEs to borrow ideas from.
- [Creating and highlighting code blocks](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-and-highlighting-code-blocks) on GitHub Docs lists the language names GitHub highlights and shows how to put backticks inside a code block.
- [Adding a workflow status badge](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge) on GitHub Docs is the page you'll need when you set up CI in Linting, Formatting and CI.
- [Choose a License](https://choosealicense.com/) explains the common open-source licenses in plain language.
