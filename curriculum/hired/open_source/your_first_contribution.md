### Introduction

A merged pull request in a library other engineers use is strong evidence. It shows you can read an unfamiliar codebase, follow a project's conventions, take review feedback, and ship something a maintainer was willing to accept. In AI, where many of the tools you've used are open source, it also puts you in contact with the people building them.

You already know the mechanics. [Branches and Pull Requests](#/lessons/foundations/branches-and-pull-requests) taught the GitHub flow, [Code Review](#/lessons/production/code-review) taught you to write a pull request (PR) a reviewer can act on and to take feedback well, and [Working in a Team](#/lessons/capstone/working-in-a-team) taught rebasing, required checks and disclosing AI use. This lesson is about what changes when the repo isn't yours: you're a guest, the maintainers owe you nothing, and their time is the scarcest thing in the project. It ends with you ready to pick the issue for [Project: First Merged PR](#/lessons/hired/project-first-merged-pr).

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why open source contributions help you get hired.
- Choosing a project, and checking that it's healthy enough to review your work.
- Reading a project's CONTRIBUTING guide, code of conduct and AI policy.
- Finding a good first issue, and talking to maintainers before you write code.
- Forking, setting up the dev environment and running the project's own checks.
- Writing a small, focused PR, responding to review, and what to do when a PR stalls.

### Why open source matters for hiring

Most of your portfolio is work you graded yourself. You wrote the spec, the tests and the README, and you decided when it was done. A merged PR is different in three ways a hiring manager cares about.

It's **reviewed by experts who had no reason to be kind.** Maintainers merge what they're willing to maintain for years. If yours got in, it met a bar someone else set.

It's **public and checkable.** Anyone can open the PR, read the discussion, see how you answered a reviewer who asked you to change your approach, and see that CI passed. That's a sample of exactly the job: working in a codebase you didn't write, to someone else's standards.

It's **in the tools employers use.** A fix in an agent framework, an eval library or an MCP SDK says you understand those tools from the inside. It also gives you something concrete to talk about in interviews and a reason to talk to people at the companies that build them.

Keep expectations honest. One small, merged docs fix won't get you hired by itself, and a long list of trivial typo PRs looks like gaming, not contributing. What counts is one or two real contributions you can explain in depth.

### Choosing a project

Start with a library you've **actually used** in this curriculum. You already know what it's for, you've read some of its docs, and you may have hit its rough edges. Good kinds of project for an AI engineer:

- **Agent and LLM libraries**, such as [Pydantic AI](https://github.com/pydantic/pydantic-ai), [LangChain](https://github.com/langchain-ai/langchain) or [LlamaIndex](https://github.com/run-llama/llama_index).
- **Eval tools**, such as [promptfoo](https://github.com/promptfoo/promptfoo), [Inspect](https://github.com/UKGovernmentBEIS/inspect_ai), [Ragas](https://github.com/explodinggradients/ragas) or [DeepEval](https://github.com/confident-ai/deepeval).
- **Observability tools**, such as [Langfuse](https://github.com/langfuse/langfuse).
- **MCP SDKs and servers**, such as the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) or the [reference servers](https://github.com/modelcontextprotocol/servers).
- **Docs** for any of these. Documentation is a real contribution, often the most welcome one, and it lets you learn a project's process before you touch its code.

Big, famous projects aren't automatically best. They get flooded with PRs, so first-time contributions can wait weeks. A mid-sized project with active maintainers often reviews faster and teaches you more.

### Checking that a project is healthy

Before you invest a week, check that someone will actually review your work. Look for:

- **Recent merges from outside contributors.** If only maintainers' PRs get merged, yours probably won't either.
- **A reasonable time to merge.** Days or a couple of weeks is fine. Months is a warning.
- **A high close-without-merge rate.** Many closed-but-unmerged PRs can mean the project auto-closes PRs that skip its process. That's not a reason to avoid it, but it is a reason to read the rules carefully.
- **Labeled starter issues nobody has claimed.**

You can check all of this by hand on GitHub, but it's quicker with a script. This one uses only the standard library and the public GitHub REST API, so `uv run repo_health.py owner/repo` works with no install. Without a token you get 60 requests an hour; set `GITHUB_TOKEN` for more.

```python
"""Check whether an open source repo is a good place for a first PR.

Usage: uv run repo_health.py owner/repo
"""

import json
import os
import statistics
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
# author_association values that mean "not a maintainer"
OUTSIDERS = {"CONTRIBUTOR", "FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER", "NONE"}


def get(path: str):
    """GET a GitHub API path and return parsed JSON, or None on 404."""
    req = urllib.request.Request(API + path)
    req.add_header("Accept", "application/vnd.github+json")
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise


def parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def main(repo: str) -> None:
    now = datetime.now(timezone.utc)

    # 1. Do the community files exist?
    profile = get(f"/repos/{repo}/community/profile") or {"files": {}}
    for name in ("contributing", "code_of_conduct", "pull_request_template"):
        print(f"{name:22} {'yes' if profile['files'].get(name) else 'MISSING'}")
    ai_policy = any(get(f"/repos/{repo}/contents/{f}") for f in ("AI_POLICY.md", ".github/AI_POLICY.md"))
    print(f"{'AI_POLICY.md':22} {'yes' if ai_policy else 'not found (check CONTRIBUTING)'}")

    # 2. Are outside contributors' PRs getting merged, and how fast?
    pulls = get(f"/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=100")
    merged = [p for p in pulls if p["merged_at"]]
    outside = [p for p in merged if p["author_association"] in OUTSIDERS]
    days = [(parse(p["merged_at"]) - parse(p["created_at"])).days for p in outside]
    print(f"\nrecently closed PRs:   {len(pulls)} ({len(merged)} merged)")
    print(f"merged from outsiders: {len(outside)}")
    if days:
        newest = max(parse(p["merged_at"]) for p in outside)
        print(f"median days to merge:  {statistics.median(days)}")
        print(f"last outside merge:    {(now - newest).days} days ago")

    # 3. Are there labeled starter issues nobody has claimed?
    for label in ("good first issue", "help wanted"):
        q = label.replace(" ", "%20")
        issues = get(f"/repos/{repo}/issues?state=open&labels={q}&per_page=100") or []
        # the issues endpoint also returns PRs, so drop those
        free = [i for i in issues if "pull_request" not in i and not i["assignees"]]
        print(f"open '{label}': {len(free)} unassigned")


if __name__ == "__main__":
    main(sys.argv[1])
```

Treat the output as a rough signal, not a verdict. `author_association` can label a maintainer whose organization membership is private as a `CONTRIBUTOR`, so open a few of the "outside" PRs and look. When this lesson was written, running it on the MCP Python SDK showed only 16 of its last 100 closed PRs were merged. The reason was in its CONTRIBUTING guide, which is the next stop.

### Reading the house rules

Read the project's `CONTRIBUTING.md` (sometimes `docs/contributing.md` or a page on the docs site) before you do anything else, every time. It tells you how to set up the project, which commands to run before you push, how to format commits, which branch to target, and whether you need to open an issue first. Ignoring it is the fastest way to get a PR closed.

The MCP Python SDK is a good example of why. As of late 2026, its guide says a PR from outside the maintainer team is closed automatically by a bot unless it links an issue that a maintainer assigned to you or that's labeled `help wanted`. It also says comments that only ask to be assigned don't help, and that typo fixes should be reported as issues instead. Someone who skipped the guide would lose their work. Someone who read it knows exactly what to do.

Look for these too:

- **The code of conduct.** Most projects use the [Contributor Covenant](https://www.contributor-covenant.org/). It sets expectations for how people treat each other, and it applies to you in every issue comment. In short: be kind, assume good faith, and don't argue with people about their decisions on their own project.
- **Legal sign-off.** Some projects ask you to sign a **Contributor License Agreement (CLA)**, usually by clicking through a bot's link on your first PR. Others use the [Developer Certificate of Origin (DCO)](https://developercertificate.org/), a statement that you have the right to submit the code, which you sign by committing with `git commit -s`. That adds a `Signed-off-by:` line, and a DCO check fails without it.
- **The PR template**, in `.github/pull_request_template.md`. Fill in every section. Maintainers notice when you delete it.
- **Project instructions files** such as `AGENTS.md`. They're written for coding agents, but they're often the clearest summary of the build and test commands.

### AI-assisted contributions

Coding agents can turn any open issue into a plausible-looking PR in minutes, and maintainers are drowning in them. Reviewing a PR still takes as long as it always did, so a careless AI-generated PR moves work from the contributor to a volunteer. Many projects have responded with written policies, and they differ a lot. A few real examples, as of late 2026:

- **[LLVM](https://llvm.org/docs/AIToolPolicy.html)** allows any tool, but requires a human in the loop who has read and reviewed everything and can answer questions about it. It specifically **forbids** using AI tools to fix issues labeled `good first issue`, because those exist so newcomers can learn the codebase.
- **[Ghostty](https://github.com/ghostty-org/ghostty/blob/main/AI_POLICY.md)** requires you to disclose every use of AI, name the tool, and fully understand the code. It publicly blocks people who submit obvious AI slop.
- **The MCP Python SDK** welcomes AI tools, but asks for one line of disclosure, answers in your own words when a maintainer asks a question, and no autonomous agents filing PRs.
- **[QEMU](https://www.qemu.org/docs/master/devel/code-provenance.html)** declines contributions that include AI-generated code at all, for legal reasons, though it allows AI for research and debugging.

So the rule is simple: **find the project's AI policy, read it, and follow it.** It may be in `CONTRIBUTING.md`, an `AI_POLICY.md`, or the docs. If the project has none, follow the habits you learned in [Working With AI Coding Assistants](#/lessons/foundations/working-with-ai-coding-assistants) and Code Review: disclose what an assistant wrote, review every line yourself before asking anyone else to, and be able to explain every change without the assistant open.

Never send unreviewed AI output to a project. That includes PRs, and it also includes issue comments and replies to reviewers. When a maintainer asks "why did you do it this way?" and gets a pasted chat answer, they stop trusting you, and on some projects you'll be blocked. Using an assistant to *understand* an unfamiliar codebase, to explain a stack trace or to find where a function is called is usually fine and genuinely useful. The test is whether you could defend the PR alone.

### Finding an issue

Look for issues labeled `good first issue` or `help wanted`, in tools you've used. You can browse a project's Issues tab with a label filter, use [Good First Issue](https://goodfirstissue.dev/), or search across GitHub with the GitHub CLI:

```bash
# Unassigned starter issues in one project
gh issue list --repo pydantic/pydantic-ai --label "good first issue" --search "no:assignee"

# Starter issues across GitHub, in Python, that mention agents
gh search issues "agent" --label "good first issue" --language python --state open --no-assignee --limit 20
```

Labels aren't the only source. Good first contributions also include:

- **Docs gaps** you hit yourself: an example that no longer runs, a missing parameter, an unclear error.
- **Missing tests** for code that has none. Ask first whether they're wanted.
- **Better error messages.** A confusing exception you hit while building a project is a perfect first issue.
- **Reproducing bugs.** Many issues are labeled `needs repro`. Writing a minimal script that reproduces the bug, on the current version, and posting it is valuable work even if someone else writes the fix. [Reading Code and Docs](#/lessons/foundations/reading-code-and-docs) showed how to follow a traceback into library code, which is exactly the skill.

Before you choose, read the whole issue thread. Skip issues where someone already said they're working on it, where a maintainer hasn't agreed the change is wanted, or where the discussion is a design argument. A good first issue is one where the "what" is settled and only the "how" is left.

### Talking before you code

Comment on the issue before you start. This avoids duplicate work, and it lets a maintainer tell you "we'd rather fix it differently" before you spend a weekend on it. Make the comment useful, not just a request to be assigned. Here's the shape of a good one (the details are invented):

```markdown
I can reproduce this on the latest release with the script below: `run_sync` raises
`TypeError` instead of a clear message when `deps` is missing.

[minimal script and full traceback]

I'd like to fix it by checking `deps` in `Agent._prepare` and raising a
`UserError` that names the missing argument, plus a test in
`tests/test_agent.py`. Does that approach sound right?
```

That comment shows you reproduced the problem, read the code, and have a small plan. Then wait for the go-ahead if the guide asks for one. If nobody replies in a week, start anyway on projects that don't require assignment, and say so in the PR.

Ask one question at a time, and do your homework first. "How do I run the tests?" when the answer is in CONTRIBUTING costs goodwill. "The CONTRIBUTING guide says `uv run pytest`, but three tests fail on a fresh clone of `main`. Is that expected?" earns it.

### Fork, set up and run the checks

You can't push branches to someone else's repo, so you **fork** it: GitHub makes a copy under your account. You push to your fork and open a PR from it into the original, which is called **upstream**. The GitHub CLI does the fork, clone and remote setup in one step:

```bash
gh repo fork pydantic/pydantic-ai --clone   # fork, clone, and set remotes
cd pydantic-ai
git remote -v          # origin = your fork, upstream = the original

# Set up exactly as CONTRIBUTING says. Many Python projects use uv:
uv sync                # or `make install`, `uv sync --all-extras`, ...

# Run the project's checks on an untouched main FIRST.
uv run pytest          # or `make test`
uv run ruff check .    # or `make lint`, `pre-commit run --all-files`

# Start your work on a branch named for the issue.
git switch -c fix-missing-deps-error

# Later, when upstream main has moved on:
git fetch upstream
git rebase upstream/main
git push --force-with-lease   # only on your own PR branch
```

Copy the setup and check commands from the project's guide, not from this example. Projects use `make`, `nox`, `tox`, `just` or `pre-commit`, and some need extras or services such as Postgres.

Running the checks **before you change anything** matters. If tests fail on a clean `main`, you've learned something about your environment (a missing extra, the wrong Python version) or the project, and you won't waste an hour thinking your change broke them. Some tests need API keys. Look for markers or flags that skip them; never put your own key in a test or a commit.

Rebasing onto `upstream/main` works exactly as you learned in Working in a Team. During review, follow the project's preference: many maintainers want new commits rather than force-pushes, so they can see what changed since they last looked.

### A small, focused pull request

Everything from Code Review applies, more strongly. A maintainer reviewing a stranger's PR has less context and less patience than a teammate.

- **One change per PR.** Fix the issue and nothing else. Don't reformat files you didn't need to touch, rename things, or "tidy up" nearby code. Scope creep is one of the most common reasons first PRs are closed.
- **Match the project's style**, not yours. Copy how nearby code names things, structures tests and writes docstrings.
- **Include a test** for any behavior change, written so it fails without your fix. For docs changes, build the docs locally and check the page renders.
- **Run the full check suite** before you push. Your PR's CI should be green on the first run. For a first-time contributor, a maintainer often has to click "Approve and run" before CI runs at all, so a red first run costs a whole round trip.
- **Write the description for a reader with no context**: link the issue with a closing keyword (`Fixes #1234`), say what changed and why, how you tested it, and what an assistant wrote, if anything.
- Leave **"Allow edits from maintainers"** ticked. Sometimes a maintainer will push a small fix to your branch rather than ask for it.

### Responding to review

Reply to every comment, push changes promptly, and assume good intent. Code Review covered how to receive feedback; in someone else's project, remember one extra thing: **it's their project.** If a maintainer prefers a different approach, you can make your case once, with evidence, but then do it their way. They'll maintain the code long after you've moved on.

Don't be discouraged by many rounds or by a maintainer rewriting part of your change. That's normal, and it's often how first contributions land. If you don't understand a request, ask: "Do you mean move the check into `_prepare`, or keep it here and change the message?" is a better reply than guessing. And answer questions yourself. If an assistant helped you understand the code, fine, but the reply should be in your words.

### When a pull request stalls

Maintainers are busy, often volunteers, and PRs go quiet. That's usually not a judgment on your work.

- **Wait a week or two**, then post one short, friendly follow-up on the PR: "Friendly ping: this is ready for another look whenever someone has time. CI is green and I've addressed the earlier comments." Don't ping again for another couple of weeks, and don't tag people individually unless the guide says to.
- **Keep it mergeable.** If `main` has moved and there's a conflict, rebase and fix it, so the PR is ready the moment someone looks.
- **Check the project's other channels.** Some projects triage PRs in a Discord, a forum or a community call, and the guide will say so.
- **Know when to let go.** If a month or two passes with no response, or a maintainer says the change no longer fits, close it politely or leave it, and move on. You can still write about the work. A well-made PR that didn't merge, with a clear trail of the conversation, is honest evidence too. Then pick a healthier project.

If your PR is closed, ask what would have made it acceptable, thank them, and use the answer next time.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Complete the [First Contributions tutorial](https://github.com/firstcontributions/first-contributions), a safe practice repo where you make a real PR from a fork, start to finish. It's here so the fork-and-PR mechanics are boring before you try them on a real project.
1. Read [How to Contribute to Open Source from Open Source Guides](https://opensource.guide/how-to-contribute/), maintained by GitHub, for a second view of the etiquette in this lesson.
   - Read "Orienting yourself to a new project," "Finding a project to contribute to" and "How to submit a contribution."
1. Read [GitHub Docs: Finding ways to contribute to open source on GitHub](https://docs.github.com/en/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github) to learn how to search for labeled issues across GitHub.
1. Read [LLVM's AI Tool Use Policy](https://llvm.org/docs/AIToolPolicy.html) and [Ghostty's AI Usage Policy](https://github.com/ghostty-org/ghostty/blob/main/AI_POLICY.md). They're short and explain the maintainer's side of AI-assisted contributions better than any summary.
1. Practice: shortlist a project for Project: First Merged PR.
   - Pick three open source AI or agent libraries you've used in this curriculum. Run `repo_health.py` from [Checking that a project is healthy](#checking-that-a-project-is-healthy) on each, and open a few of the PRs it counts as "outside" to check them.
   - For each, read the CONTRIBUTING guide, code of conduct and AI policy (or note that there isn't one), and write down the setup command, the test and lint commands, and whether PRs need an assigned issue.
   - Fork and clone the healthiest one, set it up, and run its tests and linters on an untouched `main`. Note anything that failed and why.
   - List two open issues you could plausibly tackle, and draft (don't post yet) the comment you'd leave on your favorite, in the shape shown in [Talking before you code](#talking-before-you-code).

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What makes a merged PR stronger evidence than a project you built alone?](#why-open-source-matters-for-hiring)
- [What signs suggest a project will actually review a first-time contributor's PR?](#checking-that-a-project-is-healthy)
- [What is a DCO sign-off, and how do you add one to a commit?](#reading-the-house-rules)
- [Why do some projects forbid using AI tools on good first issues, and what should you do if a project has no AI policy?](#ai-assisted-contributions)
- [What should a comment on an issue include before you start coding?](#talking-before-you-code)
- [Why should you run a project's tests before you change anything?](#fork-set-up-and-run-the-checks)
- [What should you do if your PR gets no response for two weeks?](#when-a-pull-request-stalls)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Good First Issue](https://goodfirstissue.dev/) collects beginner-friendly issues from popular open source projects.
- [Up For Grabs](https://up-for-grabs.net/) is another index of projects with issues set aside for new contributors.
- [GitHub Docs: Creating a pull request from a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) is the step-by-step reference for the PR workflow.
- [GitHub Docs: Syncing a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork) shows how to keep your fork's `main` up to date, from the web or the command line.
- [GitHub Docs: Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue) lists the closing keywords that connect a PR to its issue.
- [The CPython developer guide's page on generative AI](https://devguide.python.org/getting-started/generative-ai/) is another large project's view of acceptable and unacceptable AI use.
- [Figuring out how to contribute to open source](https://jvns.ca/blog/2017/08/06/contributing-to-open-source/), by Julia Evans, is a short, encouraging account of finding small, useful ways to contribute.
