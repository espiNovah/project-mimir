### Introduction

**Code review** is the habit of having someone other than the author read a change before it's merged. On almost every software team, nothing reaches `main` without it. You've practiced the solo version since Foundations: reading an assistant's diff in Working With AI Coding Assistants, and reading a coding agent's work "as if a stranger wrote it" in How Coding Agents Work. This lesson makes it a professional skill, from both sides of the pull request.

As the **reviewer**, you need to know what to look for, in what order, and how to say it so the author wants to fix it instead of defending it. As the **author**, you need to make your pull requests small, explained and easy to check, because a reviewer's attention is the scarcest thing on a team. That's even more true now that coding agents can produce a 900-line diff in ten minutes. Writing code got cheap. Checking it didn't.

Working in a Team, in the Capstone, covers the process around review: issues, protected branches, merging and who approves what. This lesson is about the review itself.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What code review is for, and what to look for, in order.
- Reading a pull request efficiently, with the GitHub CLI and a triage script.
- What's different about reviewing AI-generated changes.
- Why small pull requests get better reviews, and how to split big ones.
- Writing a pull request description a reviewer can act on.
- Giving and receiving feedback kindly.
- Review tooling, including AI reviewers and where they fit.

### What review is for

Review does three jobs. It **catches problems** before users do: bugs, missing tests, security holes, a change that quietly doubles the token bill. It **spreads knowledge**, because after a review two people understand the change instead of one. And it **keeps the code readable**, since code that a reviewer can't follow today is code nobody can safely change in six months.

Google's engineering practices guide puts the standard well: approve a change once it definitely improves the overall health of the code, even if it isn't perfect. There's no perfect code, only better code. A reviewer who blocks every change until it matches their personal taste slows the whole team down. A reviewer who approves everything to be friendly lets the codebase rot.

Notice what review is **not** for: arguing about formatting, import order or quote style. Ruff and pre-commit (from Linting, Formatting and CI) settle those automatically, before a human ever looks. The same goes for "do the tests pass?": CI answers that. Human attention is expensive, so spend it on what machines can't judge.

### What to look for

Look at a change from the top down. There's no point polishing variable names in a function that shouldn't exist.

1. **Is this the right change?** Read the description and the linked issue first. Does the change solve the stated problem? Is the problem worth solving this way, or is there a simpler approach? Catch a wrong direction now, before the line-by-line review.
1. **Design.** Does the code belong where it was put? Does it reuse what the project already has, or add a second way to do the same thing? Is it more complex than the problem needs?
1. **Correctness.** Walk through the logic with real inputs, especially awkward ones: empty lists, `None`, a timeout, a model reply cut off at `max_tokens`, two requests at once.
1. **Tests.** Is the new behavior tested? Would the test fail if the code were wrong? Were any existing tests changed, loosened or deleted, and if so, why?
1. **Security and data.** New routes need auth. New logging mustn't include content or tokens. New tools need the least privilege. The checklist from Security Review for AI Apps is your guide.
1. **Readability.** Can you understand it without the author explaining it? Names, comments that say *why*, and small functions all count.

AI apps add a few items that ordinary code review checklists miss:

- **A prompt change is a behavior change.** It needs an eval result in the description, from the CI gate you built in Prompt Versioning and CI Evals. "Small wording tweak" has broken plenty of production systems.
- **Model and parameter changes.** A new model, a higher `max_tokens`, more agent steps or a removed budget changes cost and latency. Ask for the before-and-after numbers.
- **New tools or permissions.** A tool that can send, delete or pay needs the approval gate from Approvals and Permissions, and a check that it doesn't complete a lethal trifecta.
- **Tracing.** New model calls and tools should produce spans with the prompt version, as in Logging and Tracing. A change that's invisible in production is hard to debug later.

### Reading a pull request

A good order for reading a pull request: description first, then the tests, then the code. The tests tell you what the author thinks the code does, which makes the code much faster to read.

For anything bigger than a few lines, check the branch out and run it. The **GitHub CLI**, `gh`, makes this one command. Install it from [cli.github.com](https://cli.github.com/), run `gh auth login` once, and then:

```bash
gh pr checkout 42          # fetch PR #42 into a local branch and switch to it
uv sync --locked           # install exactly what the PR's lockfile says
uv run pytest              # don't take CI's word for it on a risky change
gh pr diff 42 --name-only  # which files changed?
gh pr review 42 --comment -b "Left a few questions inline."
```

Before reading line by line, it helps to know where to look hardest. This script, `pr_triage.py`, flags the parts of a branch that deserve extra attention. It uses only the standard library and Git:

```python
# pr_triage.py: point a reviewer at the risky parts of a branch before they read it.
# Usage: uv run pr_triage.py [base]   (base defaults to origin/main)
import subprocess
import sys
from fnmatch import fnmatch

BIG_PR_LINES = 400  # past this, reviews get much less careful
WATCH = {  # glob pattern -> the question a reviewer should ask
    "*test*.py": "tests changed: was any test weakened, skipped or deleted?",
    "pyproject.toml": "dependencies changed: is each new package real and needed?",
    "uv.lock": "lockfile changed: does it match a pyproject.toml change?",
    "prompts/*": "prompt changed: is the eval result linked in the description?",
    ".github/workflows/*": "CI changed: check triggers, permissions and secrets",
    "*/versions/*.py": "migration: is it safe on live data, and reversible?",
}


def git(*args: str) -> list[str]:
    out = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return out.stdout.splitlines()


def main(base: str = "origin/main") -> int:
    changed, notes = 0, []
    # Three dots: compare with the point where this branch split off from base.
    # --numstat prints "added<TAB>deleted<TAB>path", with "-" for binary files.
    for line in git("diff", "--numstat", f"{base}...HEAD"):
        added, deleted, path = line.split("\t")
        if added != "-":
            changed += int(added) + int(deleted)
        notes += [
            f"{path}: {q}" for pattern, q in WATCH.items() if fnmatch(path, pattern)
        ]
    for line in git("diff", "--name-status", "--diff-filter=D", f"{base}...HEAD"):
        notes.append(f"{line.split()[-1]}: file DELETED")

    if changed > BIG_PR_LINES:
        notes.append(f"{changed} lines changed: can this be split into smaller PRs?")
    print(f"{changed} lines changed against {base}")
    print("\n".join(f"- {n}" for n in notes) or "- nothing flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
```

Run it on a checked-out branch with `uv run pr_triage.py`, or `uv run pr_triage.py main` if you compare against your local `main`. On a branch that edits a prompt, deletes a test file, adds a dependency and dumps in a 500-line file, it prints:

```text
504 lines changed against main
- prompts/triage.toml: prompt changed: is the eval result linked in the description?
- pyproject.toml: dependencies changed: is each new package real and needed?
- tests/test_app.py: tests changed: was any test weakened, skipped or deleted?
- tests/test_app.py: file DELETED
- 504 lines changed: can this be split into smaller PRs?
```

The script doesn't judge anything. It just makes sure the four or five riskiest questions get asked every time, including when you're tired. Adapt `WATCH` to your repo; the Alembic migration pattern, for example, assumes the `versions/` folder from Migrations with Alembic. Some teams run a script like this in CI and post its output as a pull request comment.

### Reviewing AI-generated changes

A diff written by a coding agent fails in different ways from one written by a junior developer, and you need to read it differently.

A junior's code usually *looks* uncertain: odd names, missing pieces, questions in the description. Agent code looks finished. It's formatted, commented and comes with tests that pass. That polish is exactly what makes it risky, because it lowers your guard. The common problems are:

- **Tests bent to fit the code.** The agent made a failing test pass by loosening the assertion, adding a `skip`, or catching the exception. Read test changes before code changes, every time.
- **Plausible but wrong.** It handles the case in the test and quietly mishandles others, like the `"2026-1"` month filter in Working With AI Coding Assistants.
- **Invented or unnecessary dependencies.** A package that doesn't exist, or a real one for a job the standard library already does. Look up every new package before approving; Security Review for AI Apps explains how attackers register commonly hallucinated names.
- **Reinventing what's there.** Agents often write a new helper instead of finding the existing one, so the codebase grows two ways of doing the same thing.
- **Too much.** Defensive checks for impossible cases, configuration nobody asked for, comments that narrate each line. Every extra line is something to maintain. "Can this be half as long?" is a fair review question.
- **Scope creep.** Unrequested "improvements" in files unrelated to the task. Ask for them in a separate pull request.

The response to all of these is the same: **ask for proof, not confidence.** As Simon Willison puts it, your job is to deliver code you have proven to work. A pull request should show that the author ran it, with test output, a screenshot, a trace or an eval result. That's true whether the author is a person, an agent, or a person who used an agent. And if you're the one who opened it, you're the author: you review the agent's work yourself before asking anyone else to.

Review the size of the diff too. A 900-line agent pull request isn't a 900-line review; it's a request to split the work. You can ask the agent to do the splitting.

### Small pull requests

Small pull requests get better reviews. A reviewer can hold a 100-line change in their head, check every branch and spot the missing case. A 1,000-line change gets skimmed and approved with "LGTM" ("looks good to me"), because nobody has two hours. Small pull requests also merge sooner, conflict less with other people's work, and are easy to revert when something goes wrong.

There's no magic number, but a common rule of thumb is to aim for under about 200 changed lines and treat anything over 400 as a warning, which is why the triage script flags it. Some ways to split a change:

- **Refactor first, then change behavior.** A pull request that renames and moves code with no behavior change is easy to check. The behavior change that follows is then small.
- **One concern per pull request.** The prompt change, the new tool and the dependency upgrade are three pull requests.
- **Layers.** The database migration and model first, then the API route, then the UI.
- **Hide unfinished work behind a flag.** Feature Flags and A/B Tests showed how to merge code that isn't switched on yet, so you can merge in small steps without shipping half a feature.

Generated files, lockfiles and test fixtures make a diff look bigger than it is. Say so in the description so the reviewer knows what to skip.

### Writing a good description

The description is your chance to do the reviewer's thinking for them. A good one answers: what changed, why, how you know it works, and what to look at closely. Put a template in `.github/pull_request_template.md` and GitHub fills it into every new pull request:

```markdown
## What and why
Route billing tickets to the cheap model. Closes #31.
Billing tickets are 40% of traffic and the capable model was overkill for them.

## How I tested it
- `uv run pytest`: 48 passed, including 3 new routing tests.
- Eval smoke set: 92% (95% CI 85% to 97%) vs 93% on main; no cases broke.
- Cost per billing ticket in traces: $0.004 -> $0.0009.

## Where to look
- `router.py`: the new rule. `prompts/` is unchanged.
- `uv.lock` only changed because I bumped `anthropic`.

## AI use
Claude Code wrote the first draft of `router.py`; I rewrote the fallback and wrote the tests.

## Risk and rollback
Behind the `cheap_billing_route` flag, off by default. Turning it off reverts the behavior.
```

Two more author habits make a big difference. **Review your own pull request first**: open the "Files changed" tab and read it as a stranger would. You'll catch the leftover `print`, the debug file and the unclear name before anyone else spends time on them. And add your own inline comments where a choice needs explaining, though if the explanation matters long-term, it belongs in a code comment instead.

### Giving feedback kindly

Review comments are written to a person who just put work in front of you. Text loses tone, so a comment that sounds neutral in your head can read as harsh. A few habits keep reviews useful and friendly:

- **Talk about the code, not the person.** "This loop runs a query per item" instead of "you wrote an N+1 query."
- **Explain why.** "Let's use a parameterized query here, because the model's text goes into it" teaches something. "Fix this" doesn't.
- **Ask real questions when you're unsure.** "What happens if the model returns an empty list?" might uncover a bug, or might teach you something.
- **Label how much each comment matters.** The [Conventional Comments](https://conventionalcomments.org/) format puts a label first, such as `issue:`, `suggestion:`, `question:`, `nitpick:` or `praise:`, and optionally `(blocking)` or `(non-blocking)`. The author then knows that `nitpick:` can be ignored and `issue (blocking):` can't.
- **Say what's good.** A specific `praise:` ("nice test for the timeout case") costs nothing and tells the author what to keep doing.
- **Offer the fix when it's small.** On GitHub, a suggestion block turns your comment into a one-click change:

````markdown
suggestion: the timeout should come from settings, like the others.

```suggestion
    timeout=settings.model_timeout_s,
```
````

- **Finish with a clear verdict.** Approve, comment or request changes. "Approved with two nitpicks, merge when ready" saves a round trip. If a thread goes back and forth more than twice, talk instead of typing.

### Receiving feedback

Being reviewed is a skill too. The comments are about the code, and every bug found in review is one that didn't reach a user.

Reply to every comment, even if just "Done." When you change something, push a new commit rather than rewriting history mid-review, so the reviewer can see exactly what changed since they last looked. If you disagree, say why, with evidence: a test, a doc link, a measurement. Then accept that the reviewer may still be right. And if a reviewer misunderstood your code, treat that as information: the next reader will misunderstand it too. Usually the right fix is clearer code or a comment, not a longer reply.

When you review a coding agent's work and it needs changes, the same idea applies in reverse: write the feedback as a clear instruction with the reason, exactly as you would for a person.

### Review tooling

Most review happens on GitHub. The "Files changed" tab has a **Viewed** checkbox per file that collapses it and tracks your progress, comment threads on any line or range, and suggestion blocks. Starting a **review** instead of single comments lets you batch your comments and send them with one verdict. The `gh` commands above do the same from the terminal.

Automation should run before a human looks: ruff, pytest, the eval gate, and the security tests from Security Review for AI Apps, all as required checks. Then the human review starts from "the machines are happy" and focuses on judgment.

**AI reviewers** are now common. Claude Code can review pull requests through its GitHub Action or its automatic [Code Review](https://code.claude.com/docs/en/code-review) feature (both Claude features), GitHub Copilot has code review built into GitHub, and OpenAI's [Codex](https://developers.openai.com/codex/integrations/github) can review pull requests too. They're good at a fast first pass: typos, obvious bugs, missing error handling, inconsistencies with the rest of the file. They're weaker at the questions at the top of the list in What to look for: whether this is the right change, and whether the design fits where the project is going. They also produce confident false alarms. Treat an AI review as one more check that runs before yours, read its comments critically, and don't let it count as the approving review. A human still owns the decision to merge.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Google's [code review developer guide](https://google.github.io/eng-practices/review/): [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), [How to write code review comments](https://google.github.io/eng-practices/review/reviewer/comments.html), [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) and [Writing good CL descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html). It's the most widely cited free guide to review; "CL" is Google's word for a pull request.
1. Read Michael Lynch's [How to Make Your Code Reviewer Fall in Love with You](https://mtlynch.io/code-review-love/) for the author's side, and [How to Do Code Reviews Like a Human](https://mtlynch.io/human-code-reviews-1/) for the reviewer's.
1. Read Simon Willison's [Your job is to deliver code you have proven to work](https://simonwillison.net/2025/Dec/18/code-proven-to-work/), on what "proof" in a pull request means when an agent wrote the code.
1. Read GitHub's [Reviewing proposed changes in a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request) and [Creating a pull request template](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository).
   - Then skim the docs for one AI reviewer, such as [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions) or [GitHub Copilot code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review), so you know how they're set up and what they're allowed to do.
1. Practice: review an AI-generated change, then make your own pull requests easy to review.
   - In one of your project repos, ask a coding agent to add a small feature on a branch and open a pull request. Run `pr_triage.py` on it, check it out with `gh pr checkout`, and review it on GitHub using Conventional Comments labels. Leave at least five comments, at least one `praise:` and at least one suggestion block, and finish with a verdict.
   - Fix what you found, replying to each comment, then merge.
   - Add `.github/pull_request_template.md` to the repo. Use it for your next three pull requests, and keep each one under 200 changed lines, not counting lockfiles.
   - If you have a study partner, swap: review one of their pull requests, and have them review one of yours.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What three jobs does code review do, and what should it leave to tools?](#what-review-is-for)
- [In what order should you review a change, and what extra items do AI apps add?](#what-to-look-for)
- [Why can a polished AI-generated diff be riskier than a rough human one, and what should you ask for?](#reviewing-ai-generated-changes)
- [Name three ways to split a large pull request.](#small-pull-requests)
- [What four questions should a pull request description answer?](#writing-a-good-description)
- [How do Conventional Comments labels make feedback easier to act on?](#giving-feedback-kindly)
- [Where do AI reviewers help, and why shouldn't they count as the approving review?](#review-tooling)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Google's guide for authors, [The CL author's guide to getting through code review](https://google.github.io/eng-practices/review/developer/), including [How to handle reviewer comments](https://google.github.io/eng-practices/review/developer/handling-comments.html).
- GitHub's blog post [How to write the perfect pull request](https://github.blog/developer-skills/github/how-to-write-the-perfect-pull-request/) is a short, practical checklist from the team that built pull requests.
- Chris Beams's [How to Write a Git Commit Message](https://cbea.ms/git-commit/) covers the commit messages reviewers read alongside your diff.
- The [GitHub CLI manual](https://cli.github.com/manual/gh_pr_review) documents `gh pr review`, `gh pr checkout` and the other pull request commands.
