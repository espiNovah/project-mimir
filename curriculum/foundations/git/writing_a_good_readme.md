### Introduction

A **README** is the file GitHub shows on a repository's front page. For most visitors, including recruiters and hiring managers skimming your profile, it's the only file they'll read. A great project with an empty README looks like an unfinished one. A clear README tells people what the project does, proves it works, and shows how you think.

Every project in this curriculum needs a README, so in this lesson you'll learn what goes in one and how to write it in Markdown.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a README is for and who reads it.
- The sections a good project README contains.
- The Markdown you need to format one.
- How to show evidence that your project works.
- How to write about what you learned without overselling.

### Who reads your README

Write for three readers:

- **A stranger deciding whether your project is interesting.** They'll give it about 30 seconds. The first two lines must say what it is.
- **Someone who wants to run it**, including you in six months. They need exact steps that work on a fresh computer.
- **A hiring manager.** They want to see that you can build something that works, explain your decisions and judge your own results honestly.

### What goes in a project README

Not every project needs every section, but most of yours will use this shape:

```markdown
# mimir-hello-uv

A command-line tool that lists the files in a folder as a formatted table.

## Demo

    $ uv run main.py ~/projects/mimir-hello-uv
    (paste real output here)

## Getting started

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

    git clone git@github.com:your-username/mimir-hello-uv.git
    cd mimir-hello-uv
    uv run main.py

## How it works

Two or three sentences on the approach and the main libraries.

## What I learned

The hardest part, how you solved it, and what you'd do differently.
```

A few points about each section:

- **Title and one-line description.** Say what it does in plain words. "A command-line tool that lists files as a table" beats "A blazingly fast file explorer."
- **Demo.** Real output, a screenshot or a short GIF. This is your evidence. Later in the curriculum it will include test results and measured numbers, such as an accuracy score or the cost per request.
- **Getting started.** Exact, copyable commands. Test them yourself by cloning the repo into a new folder and following your own instructions.
- **How it works.** Brief. Link to the code for details.
- **What I learned.** Honest and specific. "Handling missing folders taught me how exceptions work" is worth more than "I learned a lot."

<div class="lesson-note lesson-note--tip" markdown="1">

#### Be honest about limits

A short "Limitations" or "Known issues" line, such as "Doesn't handle folders with thousands of files quickly", makes you look more credible, not less. In AI engineering especially, being clear about where a system fails is a core professional skill.

</div>

### Markdown in five minutes

READMEs are written in **Markdown**, which you first met in the Learning Plan project. The syntax you'll use most:

```markdown
# Big heading
## Smaller heading

Plain paragraph text. **Bold**, *italic*, and `inline code`.

- A bullet point
- Another one

1. A numbered step
1. Another step (GitHub numbers them for you)

[Link text](https://example.com)
![Screenshot description](images/screenshot.png)
```

For blocks of code or terminal output, put a line of three backticks above and below the block, and add the language name after the first set, like `python` or `bash`, to get syntax highlighting. In the example above the code blocks are indented by four spaces instead, which also works.

VS Code previews Markdown: open a `.md` file and press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd> (<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd> on macOS).

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Make a README](https://www.makeareadme.com/), a short guide to what a README should contain and why.
   - Read the whole page, including the suggested sections.
1. Read GitHub's [About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) to learn where GitHub looks for READMEs and how it displays them.
1. Work through [Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) on GitHub Docs.
   - Focus on headings, text styling, code blocks, links, images and lists.
1. Rewrite your `mimir-hello-uv` README using the structure in this lesson.
   - Do it on a branch and merge it through a pull request, as you learned in the previous lesson.
   - Test your "Getting started" steps: clone the repo into a temporary folder and follow them exactly. Fix anything that doesn't work.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Who reads your project README, and what does each reader want from it?](#who-reads-your-readme)
- [What sections does a good project README contain?](#what-goes-in-a-project-readme)
- [How can a README show evidence that a project actually works?](#what-goes-in-a-project-readme)
- [Why is being honest about a project's limits a strength rather than a weakness?](#what-goes-in-a-project-readme)
- [How do you write headings, links, images and code blocks in Markdown?](#markdown-in-five-minutes)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Awesome README](https://github.com/matiassingers/awesome-readme) is a curated list of well-written READMEs to borrow ideas from.
