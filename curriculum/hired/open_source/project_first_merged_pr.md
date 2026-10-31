### Introduction

In this project you'll land a real contribution in an open source AI or agent library: find a good first issue, talk to the maintainers, submit a pull request with tests or docs, work through review, and write a short post about the experience. The goal is a merged PR. If the review is still going when you finish, a PR you have iterated on seriously in response to maintainer feedback also counts.

This is evidence no tutorial can give you: that you can work in someone else's codebase, to their standards, with their review.

### Before you start

- Work through [Your First Contribution](#/lessons/hired/your-first-contribution), including its practice task. You'll start this project with a shortlisted project, a working local setup and a draft issue comment.
- Choose a library you've actually used. Good candidates include [LangChain](https://github.com/langchain-ai/langchain), [LlamaIndex](https://github.com/run-llama/llama_index), [Pydantic AI](https://github.com/pydantic/pydantic-ai), [promptfoo](https://github.com/promptfoo/promptfoo), [Langfuse](https://github.com/langfuse/langfuse) or an MCP SDK such as the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). Any actively maintained AI or agent project with recent merged PRs from outside contributors is fine, including eval tools and docs.
- Check that the project is healthy with `repo_health.py` from the lesson: PRs from outside contributors were merged in the last month, and issues get replies.
- Read its CONTRIBUTING guide, code of conduct and AI policy, fork it, and get its tests and linters passing locally on an untouched `main` before you pick an issue. Note whether PRs need an assigned issue; some projects, including the MCP Python SDK at the time of writing, close PRs without one automatically.
- Create a small repo named `mimir-first-merged-pr` to hold your notes, your post draft and links. The contribution itself lives in the upstream project.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Be a good guest

Maintainers are often volunteers. Follow the project's AI policy to the letter, disclose any AI help, and never send AI output you haven't reviewed and can't explain, in a PR or a comment. Don't claim several issues at once, and don't ping people repeatedly. Many projects now close low-effort PRs on sight. One careful, small PR is worth more than five rushed ones.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Find an issue labeled "good first issue," "help wanted" or similar, or a small bug or documentation gap you hit yourself while using the library (open an issue for it first). Record the issue link and why you chose it in your notes.
1. Comment on the issue before you start: say you'd like to work on it and describe your planned approach in two or three sentences. Show that you reproduced the problem or read the relevant code. Wait for a maintainer's go-ahead or assignment if the project's guide asks for one.
1. Make a focused change on a branch in your fork. It must include tests for code changes, or be a documentation change that you've built and checked locally. Run the project's full test and lint commands and confirm they pass.
1. Open a pull request that follows the project's template and conventions. Link the issue with a closing keyword, explain what changed and why, describe how you tested it, and disclose any AI assistance as the project's policy asks.
1. Respond to review. Make requested changes promptly, reply to every comment, and keep a log in your notes of each round of feedback and what you learned from it.
1. Get the PR merged, or, if it's still in review when you finish, show at least one full round of iteration on maintainer feedback. If it stalls, follow up as described in [Your First Contribution](#/lessons/hired/your-first-contribution); if it's closed, ask what would have made it acceptable and record the answer.
1. Write and publish a short post (400 to 800 words) on your Portfolio Site about the contribution: the issue, what you had to learn about the codebase, the review feedback, and what you'd do differently. Link the PR.
1. Push your notes repo to GitHub with a README that links the issue, the PR, the post, and summarizes what you learned. It holds the evidence below.

#### Evidence

This contribution lives in someone else's repo, so the ML-style rungs of the evidence ladder don't apply here: you won't add traces, an eval score with a confidence interval, or a prompt-injection test to a project unless the issue itself calls for one. What replaces them is the project's own bar: its CI, its tests and its maintainers' review. Your notes repo's README must link each of these:

- **The issue.** The issue you worked on, with your comment proposing the approach and any maintainer reply or assignment.
- **The PR.** The pull request itself, with a description that links the issue, explains what and why, says how you tested it and discloses AI use.
- **The review trail.** The review discussion, plus your log of each round: what the reviewer asked for, what you changed (link the commit) and what you learned.
- **The merge commit.** The commit on the project's default branch, or, if the PR is still open, the latest commit after your last round of changes and the date of your most recent follow-up.
- **The project's CI passing.** A link to the green CI run on your final commit. If a check failed along the way, link that run too and say what fixed it.
- **The tests or docs build.** For a code change, the tests you added or changed, and the output of the project's test and lint commands run locally on your branch. For a docs change, a screenshot of the page built locally.
- **A short write-up.** The published post from requirement 7, linked from the README.

#### Extra credit

- Land a second PR in the same project, ideally one a little larger than the first.
- Review someone else's PR in the project constructively, or help answer an issue.
- Contribute an example or integration that connects the library to one of your own projects.

</div>

### Submitting your work

A strong submission links a PR that a reviewer could read without context: small, focused, tested, well described, and with polite, prompt responses to review. The post is honest about what was hard. Add the merged PR to your Portfolio Site's About section, and to your resume when you write it in Resume for AI Roles; it's one of the most credible lines you can have.
