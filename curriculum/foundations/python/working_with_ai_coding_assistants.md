### Introduction

You'll spend much of your career working next to an AI coding assistant. Most professional developers already do, and teams hiring AI engineers expect you to use these tools well. "Well" doesn't mean typing a wish and accepting whatever comes back. It means directing an assistant the way a good lead directs a fast, tireless junior developer who sometimes makes things up with total confidence: give clear instructions, check every piece of work, and stay responsible for what ships.

There's a second reason this lesson sits here, after testing, linting and CI and before you touch a language model API. Later in the curriculum you'll *build* agents. A coding agent is the agent you'll use most, so using one carefully now teaches you how agents behave, how they fail and why they need guardrails, all from the user's side.

This lesson is also about protecting your learning. An assistant can write code faster than you can, and that's exactly why it can stop you from learning to write it at all. You'll learn when to use one and when to keep it switched off.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The kinds of AI coding assistants, from autocomplete to agents that open pull requests.
- When an assistant speeds up your learning and when it gets in the way.
- How to give an agent context with a spec and an `AGENTS.md` or `CLAUDE.md` file.
- Working in small steps on a branch, so every change is easy to check and easy to undo.
- Using tests as the check, and spotting an agent that "fixes" tests instead of code.
- Reviewing a diff line by line, and why you never commit code you don't understand.
- Keeping secrets and your machine safe from a tool that can read files and run commands.

### Kinds of coding assistants

AI coding tools come in roughly three shapes, and most products now offer more than one.

- **Autocomplete** suggests the next few lines as you type, in gray text you accept with Tab. It's fast and low-risk, because every suggestion is small and lands right where you're looking.
- **Chat** answers questions in a side panel or browser tab: "What does this error mean?", "Explain this function." You copy code across yourself, if you use any at all.
- **Coding agents** take a task, then work on it in a loop: read files, edit them, run commands such as `uv run pytest`, read the output and try again until they think they're done. Some run in your editor or terminal on your own machine. Others run in the cloud and hand you a finished pull request.

Popular agents include [Claude Code](https://code.claude.com/docs/en/overview), [OpenAI Codex](https://github.com/openai/codex), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [GitHub Copilot in VS Code](https://code.visualstudio.com/docs/agents/overview), Cursor, and [Aider](https://aider.chat/), which is open source and can use a model running locally. They differ in price, interface and which models they use, but the skills in this lesson apply to all of them. Several have a free tier; check current pricing before you pick one, because it changes often.

That loop of "think, use a tool, look at the result, repeat" is the definition of an agent you'll meet again in the Agentic Systems path. Notice how much power it has: it can delete files, install packages and run any command your user account can. Everything else in this lesson follows from that.

### When assistants help and when they hurt

Learning to code means building a model of how programs work in your own head. That model only forms when you struggle a little: when you write a loop, get it wrong, read the error and fix it. If an assistant does the struggling for you, the program works but your head stays empty. You'll notice the gap later, in a debugging session the agent can't solve or in a job interview with no assistant in the room.

So use a simple rule. **When the goal is to learn a skill, do the work yourself. When the goal is to get something built and you already have the skill, an assistant can help.** In practice:

- **Turn it off** for exercises, for the first time you meet a concept, and while you're still slow at something. Disable autocomplete too; it quietly finishes the very lines you're meant to practice.
- **Use it as a tutor**: ask it to explain an error, a library function or a piece of code you're reading. Then check the explanation against the official docs, as you learned in Reading Code and Docs.
- **Use it as a helper** for work you could do yourself but would do slowly: boilerplate, a first draft of tests for edge cases you then check, renaming across files, or a quick script you'll throw away.

A good test is the **explain-back check**: after the assistant writes something, close the chat and explain every line out loud. If you can't, you weren't ready to delegate that task yet.

### Giving the agent context

An agent starts every session knowing nothing about your project except what it can read. Vague requests get vague results. Compare these two prompts:

- "Add a month filter."
- "Add a `--month YYYY-MM` option to the `list` and `summary` commands in `expenses.py`. Put the filtering logic in a pure function with type hints, and raise `ValueError` with a clear message for a badly formatted month. Add pytest tests for a normal month, a month with no expenses and a bad format. Don't change the CSV format. Done means `uv run pytest`, `uv run ruff check .` and `uv run mypy .` all pass."

The second is a **spec** (short for specification): the goal, the constraints and what "done" means. Writing it forces you to think through the feature first, which is half the work of building it anyway.

For things that are true of every task, most agents read a project instructions file at the start of a session. [AGENTS.md](https://agents.md/) is an open format that many tools read. Claude Code reads `CLAUDE.md` instead, and some tools have their own file name, so check your tool's docs. A small one is enough:

```markdown
# AGENTS.md

## Project
A command-line expense tracker. Data lives in expenses.csv.
Logic is in pure functions; all input() and print() calls are in main().

## Commands
- Install: uv sync
- Test: uv run pytest
- Lint and format: uv run ruff check . && uv run ruff format .
- Types: uv run mypy .

## Rules
- Every new function has type hints and at least one test.
- Never edit or delete an existing test to make it pass. Ask me instead.
- Don't add new dependencies without asking.
- Never read or print the contents of .env files.
```

Keep it short and specific. Every line costs the agent attention, so a list of commands and rules beats a page of philosophy.

### Small steps on a branch

Agents are most reliable on small, well-defined tasks, and *you* are most reliable at reviewing small diffs. So break the work down, and set up a safety net first:

```bash
git status                       # must be clean before the agent starts
git switch -c add-month-filter   # the agent works on a branch, never on main
# ...ask the agent for ONE step, for example "first just the filter function and its tests"
uv run pytest                    # check it yourself; don't trust "all tests pass!"
git diff                         # read every changed line
git add -p                       # stage the parts you understand and want, hunk by hunk
git commit -m "Add filter_by_month with tests"
```

`git add -p` (for "patch") shows each changed chunk and asks whether to stage it, which makes you look at every piece. If a step goes badly, you don't argue with the agent for twenty minutes. Throw the change away with `git restore .`, as you learned in Undoing Mistakes in Git (`git restore` doesn't remove brand-new files, so delete any that `git status` lists as untracked), and try again with a clearer instruction.

Many agents also have a **plan mode** or can be asked to "propose a plan before changing any files." Use it for anything bigger than one function. Reading a plan takes one minute, and it catches misunderstandings before they turn into fifty lines of code.

### Tests as the check

An agent will often finish with "I've implemented the feature and all tests pass!" Treat that as a claim, not a fact. Run the tests yourself, and then ask the harder question: **do the tests check the right thing?** Here's a realistic first attempt from an agent asked for the month filter:

```python
# filters.py
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Expense:
    date: date
    description: str
    category: str
    amount: float


def filter_by_month_v1(expenses: list[Expense], month: str) -> list[Expense]:
    """The agent's version: compare the start of the ISO date string."""
    return [e for e in expenses if e.date.isoformat().startswith(month)]


def filter_by_month(expenses: list[Expense], month: str) -> list[Expense]:
    """The reviewed version: parse the month, then compare year and month."""
    try:
        start = datetime.strptime(month, "%Y-%m").date()
    except ValueError:
        raise ValueError(f"month must look like 2026-10, got {month!r}") from None
    return [
        e for e in expenses
        if (e.date.year, e.date.month) == (start.year, start.month)
    ]
```

The agent's version looks fine, and its own test, `filter_by_month_v1(expenses, "2026-01")`, passes. But a user who types `2026-1` gets January *and* October, November and December, because `"2026-10-02"` starts with `"2026-1"`. And `2026` silently returns the whole year. Tests written by the same agent that wrote the code tend to share its blind spots. Your job is to add the cases it didn't think of:

```python
# test_filters.py
from datetime import date

import pytest

from filters import Expense, filter_by_month

JAN = Expense(date(2026, 1, 5), "Train", "transport", 12.0)
OCT = Expense(date(2026, 10, 2), "Bus pass", "transport", 30.0)


def test_short_month_does_not_match_october():
    assert filter_by_month([JAN, OCT], "2026-1") == [JAN]


@pytest.mark.parametrize("bad", ["2026", "October", "2026-13", ""])
def test_bad_month_raises(bad):
    with pytest.raises(ValueError):
        filter_by_month([JAN, OCT], bad)
```

Run the first test against `filter_by_month_v1` and it fails; run it against the reviewed version and it passes. That's the habit from Testing with pytest, "make sure a test can fail," applied to someone else's code.

Watch for the opposite trick too. When a test fails, an agent under pressure to finish sometimes edits the *test*, loosens an assertion, adds a `skip`, or wraps the code in a broad `try`/`except` that hides the error. That's why the `AGENTS.md` above forbids it, and why a changed test file is the first thing to look for in a diff. Your CI workflow from Linting, Formatting and CI is the final backstop: it runs the same checks on every push, whoever wrote the code.

### Reviewing the diff

Read the diff the way a careful reviewer reads a teammate's pull request. Start with `git diff --stat` to see which files changed, then go file by file. A checklist helps:

- **Scope.** Did it change only what you asked? Agents love "while I was here" improvements, and every unrequested change is something else to check.
- **Tests.** Were any tests edited, deleted or skipped? Do the new ones test behavior that matters, including bad input?
- **Made-up APIs.** Does every function and argument it calls really exist? Models sometimes **hallucinate**, confidently inventing a plausible-looking method. Check anything unfamiliar in the docs.
- **Errors.** Are exceptions handled where you talk to the user, or swallowed silently with `except Exception: pass`?
- **Dependencies.** Was anything added to `pyproject.toml`? Is it a real, well-known package? Is it needed at all?
- **Leftovers.** Debug `print` calls, commented-out code, files you don't recognize.

### Own every line you commit

The rule is simple: **never commit code you don't understand.** Once it's in your repo with your name on the commit, it's your code. Saying "the AI wrote it" doesn't help when it breaks, and in an interview, an employer will ask you about it.

When you hit a line you don't understand, you have three honest options: learn it (ask the agent to explain, then confirm in the docs), rewrite it in a way you do understand, or delete it. Asking "why did you do it this way, and what are the alternatives?" is often the most useful prompt you can send. Treat the answer as a lead to check, not as truth.

### Secrets and safety

A coding agent runs with your permissions. Anything you can read, it can read, and anything it reads may be sent to the provider's servers as part of the conversation. So:

- **Keep secrets out of reach.** Real API keys and passwords belong in a `.env` file that's listed in `.gitignore`, never in code. (The API Keys and Secrets lesson goes deeper.) Never paste a key into a chat. Many tools let you block files such as `.env` from being read; set that up.
- **Check before every commit** that no secret is staged. `git status` and the diff will show it. If a key ever reaches GitHub, deleting the file isn't enough: it's still in the history, so revoke the key and make a new one.
- **Approve commands.** Keep the tool in a mode where it asks before running shell commands or editing files outside the project, at least until you know it well. Read each command before you approve it, and say no to anything that deletes, installs or touches the network for no clear reason.
- **Work inside the project folder**, never in your home directory, so a mistake can't reach unrelated files.
- **Be wary of what it reads.** Text the agent reads in a file, web page or issue can contain instructions aimed at the agent itself. This is called **prompt injection**, and you'll study it properly in the Agentic path. For now, don't point an agent at code or pages you don't trust.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Claude Code best practices](https://code.claude.com/docs/en/best-practices). It's written for one tool, but most of its advice applies to any agent.
   - Read the sections from "Tell Claude what it can't see" through "Review against your spec", plus "Limit access with permission rules and the sandbox". Skip the parts on hooks, skills, subagents and scheduled runs; they're for later.
1. Read Simon Willison's [Here's how I use LLMs to help me write code](https://simonwillison.net/2025/Mar/11/using-llms-for-code/), an experienced developer's honest account of where these tools help and where they don't. Pay special attention to the parts on context and on testing what the model writes.
1. Skim [the AGENTS.md site](https://agents.md/) to see what instruction files look like in real projects, then read your chosen tool's docs on permissions and on its instruction file.
1. Practice: set up an assistant and give it context.
   - Pick one coding agent and install it. Configure it to ask before running commands, and to stay out of `.env` files if it supports that.
   - Add an `AGENTS.md` (or your tool's file) to your `mimir-expense-tracker` repo, modeled on the one above, with your real commands.
   - Ask the agent, read-only, to explain how your program loads and saves expenses. Check each claim against your own code and write down anything it got wrong.
1. Practice: compare your work with an agent's. Do one exercise from the [Pythonic Python exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/pythonic-python) that you haven't solved yet, **by yourself first**, until `uv run pytest` passes. Commit it. Then, on a new branch, reset the starter file and ask the agent to solve it with the tests as its check. Review its diff using the checklist, and write three differences between its solution and yours, including which one you'd rather maintain and why.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What makes a coding agent different from autocomplete or chat?](#kinds-of-coding-assistants)
- [When should you keep an assistant switched off, and what is the explain-back check?](#when-assistants-help-and-when-they-hurt)
- [What three things should a good spec for an agent include?](#giving-the-agent-context)
- [Why should an agent work on a branch in small steps, and how do you throw away a bad step?](#small-steps-on-a-branch)
- [Why can an agent's own tests pass while the feature is still wrong?](#tests-as-the-check)
- [Name four things to check when reviewing an agent's diff.](#reviewing-the-diff)
- [What should you do if an API key is accidentally pushed to GitHub?](#secrets-and-safety)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [GitHub's best practices for using Copilot](https://docs.github.com/en/copilot/get-started/best-practices) covers choosing between autocomplete, chat and agents, with advice that applies beyond Copilot.
- [Aider's documentation](https://aider.chat/docs/) shows how to run a coding agent against a local or low-cost model, if paid tools aren't an option for you.
