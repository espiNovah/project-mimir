### Introduction

In this project you'll add a real feature to your Expense Tracker, but you won't write the first draft. A coding agent will. Your job is the part that employers actually pay for: writing a clear spec, keeping the agent on a short leash, reviewing its pull request line by line, and refusing to merge until the code is correct, tested and something you fully understand.

You'll also keep a **mistake log**: every place the agent was wrong, did something you didn't ask for, or claimed something it hadn't checked. That log is the heart of the project. It trains you to read AI-written code with suspicion, and it gives you a concrete, honest story to tell in interviews when someone asks, "How do you use AI tools?"

Nothing here needs a model API key. You'll use the coding agent you set up in Working With AI Coding Assistants, and the tests, ruff and CI you added to the Expense Tracker.

### Before you start

- Your `mimir-expense-tracker` repo must be in good shape on `main`: `uv run pytest`, `uv run ruff check .` and `uv run mypy .` all pass, and the GitHub Actions workflow from Linting, Formatting and CI runs ruff and pytest on every push and is green. If any of that is missing, fix it yourself first. You need a trustworthy baseline to compare the agent's work against.
- Pick one coding agent, such as Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot's agent mode or Aider. A cloud agent that opens the pull request for you is fine, and so is a local agent whose branch you push yourself. Say which tool and which model you used in your write-up.
- Keep the agent in a mode where it asks before running commands, and make sure it can't read any `.env` file. Your Expense Tracker shouldn't contain secrets, but check: `git status` should be clean and `.gitignore` should list `.env`.
- Pick **one** feature that you haven't built yet. It should touch both logic and the command-line interface, and be big enough to need several tests. For example:
  - filters: `list` and `summary` for one category and/or one month (`--month 2026-10`);
  - a `delete` or `edit` command that works on an expense's number in the list;
  - monthly budgets per category stored in a small JSON file, with a warning when a category goes over;
  - storing amounts as integer cents (or `decimal.Decimal`) so totals are exact, without breaking existing CSV files;
  - an `export` command that writes the summary to a Markdown or JSON file.

<div class="lesson-note lesson-note--warning" markdown="1">

#### You are the reviewer, not a spectator

It's tempting to let the agent run, see green checks and click merge. Don't. Green CI only means the checks you have passed. This project is graded on what you caught. If your mistake log is empty, the most likely explanation is that you didn't look closely enough.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### The spec

1. Before you open the agent, write a GitHub issue for the feature ([creating an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue) shows how). It must say what the feature does, how a user runs it (example commands and their expected output), what should happen with bad input, what must not change (for example, the CSV format, or existing commands), and a "done when" list that includes `uv run pytest`, `uv run ruff check .` and `uv run mypy .` passing.
1. Write at least three acceptance tests yourself, before the agent starts, and commit them on the feature branch. They should fail now and pass once the feature works. At least one must cover an edge case or bad input. These are your check on the agent, so the agent must not edit them.
1. Add or update an `AGENTS.md` (or your tool's instruction file) with your project's commands and rules, including "never edit or delete existing tests without asking" and "don't add dependencies without asking."

#### The agent's work

1. Have the agent implement the feature on a branch, in at least two separate steps (for example, "logic and its tests" and then "the command-line interface"). Ask for a plan before the first step and keep it in your notes.
1. Give it the issue as its spec. Don't write any of the feature code yourself during this phase. If the agent gets stuck, write a better instruction instead of the code.
1. Save the conversation, or an excerpt of every prompt you sent and a summary of what the agent did, in `docs/agent-session.md`. Remove anything private before committing.
1. Open a pull request from the branch to `main`, written by you or by the agent. Its description must link the issue.

#### The review

1. Review the pull request on GitHub in the "Files changed" tab, line by line, using the checklist from Working With AI Coding Assistants: scope, tests, made-up APIs, error handling, dependencies and leftovers. Leave at least five line comments explaining what's wrong or what you checked.
1. Run everything yourself from a fresh state: `uv sync`, `uv run pytest`, `uv run ruff check .`, `uv run mypy .`, and the new command by hand with good and bad input. Don't rely on the agent's report.
1. Write at least two more tests of your own for cases the agent didn't think of. For each one, show that it would fail against a broken version of the code (temporarily break the code or check out the agent's earlier commit), then passes.
1. Get the fixes made, either by sending your review comments to the agent or by fixing the code yourself, until every comment is resolved. You must be able to explain every line in the final diff. Anything you can't explain gets rewritten or removed.
1. Merge the pull request only when CI is green and your review is complete.

#### The mistake log

1. Keep `docs/agent-mistakes.md` as a table with one row per problem. Include at least five rows. Each row records:
   - **where** (file and line, or a link to the PR comment);
   - **what was wrong**, specifically;
   - **category**: a bug, a weak or missing test, an edited test, scope creep (a change you didn't ask for), a made-up API, ignored instructions, an unverified claim ("all tests pass" when they didn't), or a style or convention problem;
   - **how you found it** (reading the diff, a test, CI, running it by hand);
   - **how it was fixed**.
1. Below the table, write a short reflection: which category came up most, which mistake would have reached users if you hadn't reviewed, and one change to your spec or `AGENTS.md` that would have prevented a mistake. Make that change and commit it.

#### Evidence

- The GitHub Actions workflow runs ruff and pytest on the pull request and on `main`, and both runs are green. Show the passing badge in your README.
- Your acceptance tests are in a commit that comes before the agent's feature code, so a reviewer can see they were written first. Link to that commit.
- `uv run pytest` output from the merged `main`, pasted in the README or the PR, including your extra tests.
- A link to the merged pull request with your line comments visible.
- A short terminal transcript of the new feature working, including one bad input being rejected with a clear message.
- `docs/agent-session.md` and `docs/agent-mistakes.md`, committed.

#### Extra credit

- Do the same feature twice, with two different agents (or the same agent with a stronger and a weaker model), and compare their mistake logs in a table.
- Run the agent as a cloud agent that opens the PR itself, and compare the experience with working locally.
- Plant a bug on purpose in a branch of your own and ask the agent to review the diff. Did it find it? Add the result to your mistake log.
- Add a pre-commit hook that runs ruff, so the agent's edits are formatted before they can even be committed.

</div>

### Submitting your work

A strong submission shows a reviewer, in a few minutes, that you were in charge. The README links the issue, the pull request, the CI run and the two `docs/` files, and explains the new feature with a real example. The PR shows real review: specific line comments, not "LGTM" (short for "looks good to me"). The mistake log is specific enough that someone else could find each problem from your description.

Be honest in the log. "The agent wrote a correct `delete` function, but its test only checked the length of the list, not which expense was removed" is far more valuable than a vague "some tests were weak." Hiring managers know these tools make mistakes. What they want to see is that you catch them.
