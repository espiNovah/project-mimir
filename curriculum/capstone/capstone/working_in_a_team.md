### Introduction

Every project so far has been yours alone: you picked the work, wrote the code, reviewed it and merged it. Jobs don't work like that. On a team, five people and a couple of coding agents change the same repo in the same week, half of them are asleep when you have a question, and someone in product needs to know whether the feature ships Friday. The code matters, but most of what makes a team fast or slow is everything around the code: how work is written down, split up, handed off and talked about.

This lesson teaches that layer with plain Git and GitHub, which you already know from Foundations. You'll then run your capstone repo as if it were a team project. Employers can't watch you work on a team before they hire you, but they can read a repo's issues, pull requests and decision records, and those show it.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Tracking work with issues, labels, milestones and a small project board.
- Breaking a feature into small issues that one person can finish in a day or two.
- The team pull request flow: rebasing or merging, resolving conflicts, protected branches and required checks.
- Writing for async teams: status updates, decision records and good questions.
- Which meetings are worth having: standups, planning and retros.
- Working with product managers and designers.
- How AI coding tools change team workflows.

### Tracking work with issues

An **issue** is a GitHub page for one piece of work: a bug, a feature, a question or a chore. It has a title, a description, comments, and people assigned to it. The rule most teams follow is simple: **if it isn't in an issue, it isn't happening.** Ideas in chat get lost, and work nobody wrote down can't be planned, split or handed to someone else.

A good issue answers four questions: what's wrong or wanted, why it matters, what "done" looks like, and anything the person picking it up needs to know. Here's one for a capstone that drafts replies to supplier emails:

```markdown
Title: Drafted replies ignore the supplier's requested delivery date

When a supplier email asks for a specific delivery date, the draft
proposes our default date instead. Seen in 4 of the 30 emails in
evals/cases.jsonl (ids 7, 12, 19, 22).

Why it matters: our user has to rewrite these drafts by hand, which is
most of the time the tool is meant to save.

Done when:
- [ ] A requested date in the email appears in the draft.
- [ ] The 4 cases above pass, and the full eval score doesn't drop.

Notes: dates are extracted in extract.py; the prompt is prompts/draft_v3.md.
```

The checkbox list under "Done when" is **acceptance criteria**: the conditions a reviewer checks to decide the work is finished. Writing them first prevents the most common team argument, "I thought you meant something else."

Three GitHub features keep a pile of issues organized:

- **Labels** are colored tags. Keep a small set that answers useful questions: the type (`bug`, `feature`, `chore`), the area (`evals`, `frontend`) and the state (`blocked`, `needs-decision`). `good first issue` is a convention open-source projects use to flag easy starting points. Fifty labels nobody applies consistently are worse than six that everyone uses.
- **Milestones** group issues toward a goal or date, such as "MVP in front of first user." GitHub shows how many of the milestone's issues are closed, which is an honest progress bar.
- A **project board** (GitHub Projects) shows issues as cards in columns such as Todo, In progress, In review and Done. It answers "what is everyone working on?" at a glance. Start with those four columns. You can add custom fields like priority or size later, but a board only helps if it's kept up to date, so keep it small.

Link work to issues as you go. If a pull request description contains `Closes #42`, GitHub links the two and closes issue 42 automatically when the PR merges. Anyone reading the issue later can follow it to the code that fixed it.

### Breaking work into small issues

"Build the email assistant" is not an issue; it's a project. Nobody can review it, estimate it or pick up half of it. Teams split work until each issue is something one person can finish and get merged in a day or two.

A useful way to split is by **vertical slices**: thin pieces that each work end to end, rather than layers. Slicing by layer gives you "build the database," "build the API" and "build the UI," and nothing works until all three are done. Slicing vertically gives you:

1. Fetch one email from a test inbox and print a draft reply in the terminal.
1. Save drafts to Postgres so the user can see past ones.
1. Add a page that lists drafts with approve and reject buttons.
1. Send an approved draft (behind the approval step).
1. Add the 30-case eval set and run it in CI.

After item 1, something real exists that you can show your user. Every later item makes it better, and you can stop at any point and still have a working system.

Some signs an issue is too big: the acceptance criteria run past five or six items, it touches every part of the codebase, or you can't guess how long it will take. Split it, and use a parent issue with a checklist of the smaller ones to keep track. If you can't split it because you don't know enough yet, make the first issue a **spike**: a time-boxed investigation ("spend half a day finding out whether the email provider's API supports threads") whose output is a written answer, not production code.

Small issues lead to small pull requests, which get reviewed faster and more carefully. The [Code Review](#/lessons/production/code-review) lesson covers why small diffs matter to reviewers and how to write a PR that's easy to review. This lesson is about the flow around it.

### The team pull request flow

You know the GitHub flow from [Branches and Pull Requests](#/lessons/foundations/branches-and-pull-requests): branch from an up-to-date `main`, commit, push, open a PR, get it reviewed, merge. On a team there's one new problem. While your PR is open, other PRs merge, so `main` moves on without you. Before you merge, your branch has to catch up.

There are two ways to bring new commits from `main` into your branch. **Merging** (`git merge origin/main`) adds a merge commit that joins the two histories. It's safe and never rewrites anything, but a long-lived branch collects lots of "Merge main into my-branch" commits. **Rebasing** replays your commits one by one on top of the new `main`, as if you had started your branch today. The history stays in a straight line, but your commits get new IDs, which means rewriting history.

```bash
git switch fix-delivery-date
git fetch origin                 # download new commits without changing your branches
git rebase origin/main           # replay your commits on top of the latest main

# If a commit conflicts, Git stops and marks the files, as with a merge.
# Edit the files to what you want, then:
git add extract.py
git rebase --continue            # carry on with the next commit
# Or give up and put everything back exactly as it was:
git rebase --abort

git push --force-with-lease      # your commits have new IDs, so a normal push is refused
```

`--force-with-lease` overwrites the branch on GitHub, but refuses if someone else pushed to it since you last fetched, so you can't silently delete a teammate's commits. Never use a plain `--force` on a shared branch.

This connects to the warning in [Undoing Mistakes in Git](#/lessons/foundations/undoing-mistakes-in-git) about rewriting pushed history. The team rule is: **rebase your own branches freely, but never rebase a branch other people are building on, and never rebase `main`.** If two people share a branch, merge instead.

GitHub also asks how to merge the PR itself. A **merge commit** keeps every commit from the branch. **Squash and merge** combines the whole PR into one commit on `main`, which is what many teams choose: messy "fix typo" commits disappear, and each commit on `main` matches one reviewed PR that can be reverted in one step. **Rebase and merge** keeps each commit but without a merge commit. Teams pick one and set it in the repo settings, so nobody has to think about it.

Conflicts are more common on teams, and they're cheaper when they're small. Keep branches short-lived, update from `main` daily, and tell people in the issue when you're about to touch a file everyone uses, like a shared prompt or the database models. When a conflict involves code you didn't write, don't guess. Ask its author which version is right.

#### Protected branches and required checks

On a team, nobody pushes straight to `main`, not even the senior engineers. GitHub enforces this with **branch protection rules** (or the newer **rulesets**, which do the same job with more options). In the repo's Settings, under Branches or Rules, you can require that every change to `main`:

- comes through a pull request;
- has at least one approving review from someone other than the author;
- passes named **status checks**, such as the ruff-and-pytest workflow from [Linting, Formatting and CI](#/lessons/foundations/linting-formatting-and-ci) or your eval job;
- is up to date with `main` before merging, so the checks ran against the code that will actually land.

Once this is on, a red CI run or a missing review greys out the merge button. Nobody has to remember the rules, and nobody can skip them in a hurry. At the time of writing, these rules are free on public repos but need a paid plan on private repos, so keep your capstone public if you want them.

### Writing for async teams

Most modern teams are partly remote and spread across time zones. **Async** (asynchronous) communication means writing things down so people can read and respond in their own time, instead of needing everyone in the same meeting. It only works if the writing is good. Three kinds of writing come up constantly.

**Status updates.** A short, regular note on where your work stands, posted where the team looks (a channel, a pinned issue, the project board). A format that works well:

```markdown
**Done:** Delivery-date fix merged (#42). Eval score 0.81 → 0.86.
**Next:** Approval page (#45), then sending (#46).
**Blocked:** Need the supplier test inbox password from Dana.
**Risk:** The email API rate limit may be too low for 30 evals per CI run.
```

Lead with the outcome, link to the evidence, and make blockers impossible to miss. Bad news early is a favor. "This will slip a week" on Monday lets people plan; on Friday it's a surprise.

**Decision records.** Teams make lots of decisions, and six months later nobody remembers why. An **architecture decision record** (ADR) is a short file, usually in `docs/decisions/`, written when a choice is made:

```markdown
# 0003. Use a fixed workflow instead of an agent for drafting

Status: accepted (2026-11-04)

Context: Every supplier email needs the same three steps: extract
dates and items, look up the order, draft a reply. Our eval set has
no case where a different order of steps would help.

Decision: Use a fixed three-step workflow with one model call per step.

Consequences: Cheaper and easier to test. If we later need to handle
free-form requests, revisit this and supersede it with a new record.
```

It's short on purpose: context, decision, consequences. Records are never edited after the fact. If the decision changes, write a new record that says which one it replaces. Decision records pair well with the spec you'll write in [Writing a Spec](#/lessons/capstone/writing-a-spec): the spec describes the plan, and the records explain how and why it changed.

**Asking good questions.** You learned in Foundations to ask for help with a minimal example. At work, add context the reader doesn't have, and ask in a way that can be answered in one reply. Compare "hey, got a sec?" (which forces a round trip just to learn the question) with "In #45, should rejected drafts be deleted or kept for evals? I'd lean to keep them with a `rejected` flag, since they're useful failure cases. I'll go with that tomorrow unless you object." The second states the question, gives your best guess and sets a default, so work doesn't stop if the person is busy. Ask in a public channel or on the issue rather than in a private message, so the answer helps the next person too.

### Meetings that matter

Async writing doesn't replace every meeting. A few are worth their time, and each has a clear job.

- **Standup.** A daily check-in of about 15 minutes: what you did, what's next, what's blocking you. Its real purpose is surfacing blockers. If it turns into everyone reading status aloud, move that part to written updates and keep the meeting for problems.
- **Planning.** At the start of a cycle (often one or two weeks), the team picks which issues to do, checks each is small and clear enough, and agrees who takes what. A good outcome is a short list the team believes it can finish, not a wish list.
- **Retrospective.** At the end of a cycle, the team asks what went well, what didn't and what to change. The output is one or two concrete actions with an owner, such as "turn on the required eval check" or "split issues bigger than two days." Retros are **blameless**: they look at how the process allowed a problem, not at whose fault it was. This is the same idea as the incident reviews in [Alerting and Incidents](#/lessons/production/alerting-and-incidents).

Every meeting should have an agenda before it starts and written notes after it, linked from the relevant issues, so people who missed it aren't left out.

### Working with product and design

On most product teams, you won't decide alone what to build. A **product manager** (PM) owns *what* and *why*: which user problems matter most and how success is measured. A **designer** owns how it looks and feels to use. Engineers own *how* it's built and what it costs. Good teams argue across those lines constantly, and that's healthy.

A few habits make you easy to work with. Bring tradeoffs, not just yes or no: "We can ship the approval page this week without editing, or next week with it." Raise technical constraints early, especially AI-specific ones a PM might not expect, like latency, cost per task, or the fact that a model will be wrong some of the time. Show your evals and traces when discussing quality, because "it seems better" can't be planned around and "accepted without edits rose from 62% to 78%" can. And when a design can't be built as drawn, go back to the designer with options rather than quietly building something different.

For your capstone, your real user plays the PM role. Treat their feedback the same way: write it into issues, and say plainly what you will and won't do.

### How AI coding tools change the workflow

Coding agents are now teammates of a sort. They write code, open pull requests, and some can be assigned an issue directly and come back with a PR. That changes a few things.

**A human owns every change.** If you asked an agent to write code and you open the PR, you're the author, and you're responsible for every line as if you'd typed it. You review it yourself first, as you learned in [Working With AI Coding Assistants](#/lessons/foundations/working-with-ai-coding-assistants). Then a second person reviews it like any other PR. AI review bots can be a useful first pass that catches typos and obvious bugs, but on a team they don't count as the approving review. When an agent opens a PR on its own, the person who assigned the work is the author for review purposes.

**Disclose AI use.** Say in the PR description which parts an agent wrote and how you checked them: "Agent-generated; I rewrote the retry logic and added tests for the timeout case." Reviewers then know where to look hardest. Some companies and open-source projects require disclosure, and some don't accept AI-generated contributions at all, so read the `CONTRIBUTING.md` before you open a PR on someone else's project.

**Issues become prompts.** An issue with a clear problem, acceptance criteria and pointers to the right files is exactly what an agent needs, too. Teams that write good issues get much more out of agents.

**Agent instructions become shared config.** A project instructions file holds the build and test commands and the rules every agent session should follow. `AGENTS.md` is an open format many tools read. Some tools use their own file name: `CLAUDE.md` is Claude Code's file, and GitHub Copilot reads `.github/copilot-instructions.md`. These files are tool-specific, so check what your team's tools read; some teams keep the rules in `AGENTS.md` and point the other files at it. On a team, commit the file and change it through pull requests like code, because one careless line affects every agent run for everyone. Keep personal preferences out of it; most tools have a separate, uncommitted file for those.

**Review becomes the bottleneck.** Agents make code cheap to produce, but reviewing it still takes human attention. Teams that adopt agents well keep PRs small, limit how many agent PRs are open at once, and rely on required checks so the obvious problems are caught before a person looks. Protected branches apply to agents too: never give an agent a token that can bypass them.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Your repo is your team history

Hiring managers do look at repos. A capstone with linked issues, small reviewed PRs, green checks and a few decision records shows you can work on a team, which is hard to show any other way.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read GitHub's docs on [About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) and [About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects). They show the features from Tracking Work With Issues in the real interface.
   - Also skim [Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue) for the full list of keywords like `Closes`.
1. Read [Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing) in Pro Git, which you skipped in Foundations. Its diagrams show exactly what rebasing does to history, and its "Perils of Rebasing" section explains the team rule in this lesson.
   - Then read GitHub's [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) and [About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github).
1. Read Michael Nygard's [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), the short post that started decision records, and skim GitLab's guide to [asynchronous communication](https://handbook.gitlab.com/handbook/company/culture/all-remote/asynchronous/) from a company with no offices at all.
1. Practice: run your capstone repo as a team project. Use the problem you picked in Finding a Real Problem. Do this alone, or better, with a study partner who does the same in their repo, so you each have a real reviewer.
   - Create the `mimir-capstone-<short-name>` repo if you haven't yet. Add six or fewer labels, a milestone called "First version in front of a user" and a project board with Todo, In progress, In review and Done.
   - Write 8–12 small issues as vertical slices, each with acceptance criteria. Add a parent issue that lists them.
   - Protect `main`: require a pull request and require your CI check to pass. With a partner, add each other as collaborators and require one approval; alone, require zero approvals, since GitHub won't let you approve your own PR.
   - Do at least three issues through the full flow: a branch, a PR that says `Closes #N` (and discloses any AI help), review, squash-merge. With a partner, review each other's PRs using the [Code Review](#/lessons/production/code-review) lesson, and make one of you create a conflict on purpose so the other resolves it with a rebase.
   - Commit `AGENTS.md` (or your tool's file) and at least one decision record in `docs/decisions/`.
   - At the end of the week, post a written status update on a pinned issue, then hold a 20-minute retro, alone or together, and turn its one or two actions into issues.
1. Keep working this way for the rest of the capstone. After the next lesson, Writing a Spec, turn your spec's milestones into GitHub milestones and its work into issues.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What four things should a good issue answer, and what are acceptance criteria for?](#tracking-work-with-issues)
- [Why do teams slice work vertically rather than by layer?](#breaking-work-into-small-issues)
- [When is it safe to rebase a branch, and why do you push with force-with-lease afterwards?](#the-team-pull-request-flow)
- [What goes in a decision record, and what do you do when the decision changes?](#writing-for-async-teams)
- [What is a retrospective for, and what does "blameless" mean?](#meetings-that-matter)
- [If an agent wrote most of a pull request, who is responsible for it and who reviews it?](#how-ai-coding-tools-change-the-workflow)
- [Why should a shared agent instructions file go through pull requests?](#how-ai-coding-tools-change-the-workflow)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) explains GitHub's newer alternative to branch protection rules.
- [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) shows how teams automatically request reviews from the people responsible for each part of a repo.
- [Configuring issue templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository) lets you build the "good issue" shape into your repo, so every new issue starts with the right headings.
- [The ADR GitHub organization](https://adr.github.io/) collects decision-record templates and tools.
- [no hello](https://nohello.net/) is a one-page explanation of why you should put your question in your first message.
- [AGENTS.md](https://agents.md/) describes the open project-instructions format and lists the tools that read it.
