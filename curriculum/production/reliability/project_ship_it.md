### Introduction

This is the capstone of the Production and LLMOps path. You will take a real agent and run it the way a professional team would: released to staging and production, traced on every request, with a dashboard of cost and latency, evals that run on every pull request, prompts versioned in the repo, alerts that reach your phone with a runbook for each, a security review, and changes that go through reviewed pull requests.

Every piece of this project is something you practiced in an earlier project or lesson in this path. The challenge here is putting them all together on one system and keeping them working. When you're done, you will have something most job candidates can't show: an AI system that is not just built, but operated.

### Before you start

- Create a new GitHub repo named `mimir-ship-it`, or continue in your existing project repo on a new branch.
- Choose what to ship:
  - **Recommended:** your Workflow Automation Agent from the Agentic Systems path.
  - **Fallback:** your Chat With Your Docs app with the UI from the Docs Chatbot UI project. This option requires an existing eval set, either from RAG Eval Harness or from Trace Detective.
- Reuse what you built earlier: the image, `release.sh`, secrets and two environments from Hello, Production; the tracing and eval set from Trace Detective; the caching, routing and fallbacks from Cut the Bill; and the eval workflow and gate from Prompt Versioning and CI Evals.
- Set a spend limit with your model provider and keep your cloud budget alerts from Hello, Production. The public demo must require a login and enforce a per-user daily budget, as in Security Review for AI Apps. A public agent with no limits is an open invitation to drain your account.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Deploy it.
   - Release it to staging and production with your `release.sh` from Hello, Production, so production has a public demo URL and every release passes a smoke test first.
   - All keys come from the platform's secret store, one key per environment.
   - `/health` reports the commit that's serving, as in Hello, Production.
1. Trace every request.
   - Every request in production creates a trace with spans for each model call and tool call, including tokens and latency, as in Logging and Tracing.
   - Each trace records the prompt name, version and hash, the model used and the app version.
   - Traces must outlive the container: send them to a tracing backend, a Postgres table or your platform's log service, not a file inside a Cloud Run instance.
1. Build a cost and latency dashboard.
   - Use your tracing tool's dashboard or build a simple page. It must show cost per request, total cost per day, and p50 and p95 latency over time.
   - Include a screenshot in your README taken after at least a few days of real or test traffic.
1. Run evals on every pull request.
   - A GitHub Actions workflow runs your tests on every push, and on each pull request scores a smoke set of at least 20 cases on both the branch and its base branch, as in Prompt Versioning and CI Evals. The API key is stored as a repository secret.
   - The job fails if the score drops more than your `--max-drop` against the base branch or falls below your `--floor`. Justify both numbers: set `--max-drop` from the noise you measured by running the smoke set twice on the same commit.
   - Mark the eval check as required in your branch protection settings.
   - Show a pull request in which CI caught a deliberately bad prompt change.
1. Version your prompts.
   - Every prompt lives in a file in `prompts/`, loaded by name with a version and a hash, and changes go through pull requests.
1. Complete a security review.
   - Add `SECURITY.md` as in Security Review for AI Apps: a short system description, then a table with one row for every item in the OWASP Top 10 for LLM Applications (and the agentic IDs that apply), with whether it applies, the mitigation, and the test or setting that proves it. End with residual risks and how to report a vulnerability.
   - Add gitleaks to your pre-commit hooks and scan the full history. Add `uv lock --check` and pip-audit to CI, and Dependabot for `uv` and `github-actions`.
   - Add security tests like `test_security.py`: every non-public route requires a login, logs and spans hold no canary or token, and the per-user daily budget returns `429` without affecting other users.
   - Include prompt-injection tests in your eval set, and require human approval for any risky action your agent can take, as in Approvals and Permissions. (For the RAG fallback, plant the injection in a retrieved document; there are no actions to approve.)
1. Set up alerts and write a runbook.
   - Write two or three SLOs and their alerts, as in Alerting and Incidents: at least one for errors or latency and one for cost. Run `slo_check.py` (or your platform's alerting) on a schedule against production logs or traces, sending to your phone or chat.
   - Add a one-page `RUNBOOK.md` with an entry for each alert, plus entries for: the model provider is down or rate-limiting, costs spike, a user reports a harmful or wrong output, and a secret leaks. Use the lesson's format: what it means, how to check how bad it is, likely causes, how to mitigate (including the exact rollback command from your `RELEASE.md`), and who to escalate to.
   - Fire one alert on purpose and follow its runbook entry.
   - The [Managing Incidents chapter of Google's SRE book](https://sre.google/sre-book/managing-incidents/) is a good free model for how real teams structure this.
1. Work through reviewed pull requests.
   - Add `.github/pull_request_template.md` from Code Review. After your initial setup, every change reaches `main` through a pull request that uses it, including any AI-use disclosure.
   - Get at least one pull request reviewed by someone else, such as a friend who codes or someone from a developer community, using Conventional Comments labels, and address every comment before merging. If you have no reviewer, review your own coding agent's pull request as in the Code Review lesson, and say so in your README.
1. Push to GitHub with a README that leads with the demo URL and an architecture diagram, then links to the dashboard screenshot, CI runs, `SECURITY.md`, `RUNBOOK.md` and your reviewed pull requests, and ends with what you learned.

#### Evidence

Your README must show:

- A passing GitHub Actions badge, and a workflow that runs `ruff check`, `ruff format --check` and `pytest` on every push, plus `uv lock --check` and pip-audit. Pytest covers your security tests (route auth, no content or tokens in logs and spans, the per-user budget), the eval gate script on two hand-made result files, and the approval gate, with fake clients and no real model calls. (Linting, Formatting and CI; Security Review for AI Apps)
- Traces: an export of at least 20 production traces with personal data removed, each naming its prompt version and hash, model and app version, and a screenshot of one full trace tree with model-call and tool spans. (Logging and Tracing)
- An eval score with a confidence interval: the full eval set's score on the version now in production, with a 95% bootstrap confidence interval, its `n` and the prompt version (Eval Statistics). From the pull request gate, also show the paired change against the base branch with its interval.
- Prompt injection: your injection cases run in the eval set, and for each one, what the agent *did*, shown by environment state or your audit log, not by its reply. Show one run where an injected action reached the approval gate and was refused, if any did. (Prompt Injection and the Lethal Trifecta)
- The CI gate blocking a bad prompt change: a link to the pull request, its failed eval run with the step summary showing the score drop and the `broke:` cases, the fix commit and the passing run after it, and a screenshot of the branch protection rule that makes the check required. (Prompt Versioning and CI Evals)
- An alert fired on purpose: how you triggered it (for example, a flag that forces model errors in staging, or a lowered cost threshold), a screenshot of the notification with its timestamp, the `RUNBOOK.md` entry you followed, and a short timeline of what you checked and did. (Alerting and Incidents)
- The security review results: `SECURITY.md` with every Evidence cell linking a test, CI step or screenshot; the output of `gitleaks git` over the full history; the latest pip-audit output and how you resolved or justified any finding; your provider spend limit (a screenshot); and the residual risks you accept. (Security Review for AI Apps)
- A reviewed pull request: a link to it, showing the filled-in template, the review comments with their labels, your replies and fix commits, and the approval (GitHub won't let you approve your own pull request, so for a self-review, link your summary comment instead). If an AI reviewer also commented, say which of its comments were useful and which were wrong. (Code Review)
- The dashboard screenshot, and the cost per request and p95 latency from it, with the date range.
- **A public post.** A link to your post about this project, as Learning in Public asks for each path you complete: your Production post.

#### Extra credit

- Run a "game day": simulate a provider outage by forcing errors, follow your runbook, and write a blameless postmortem of what happened, as in Alerting and Incidents.
- Run the full eval set nightly with a batch API and post the score to your dashboard.
- Add an AI reviewer to your pull requests for two weeks, and report how many of its comments led to a change and how many were false alarms.

</div>

### Submitting your work

A strong submission lets a reviewer verify every claim in a few clicks: open the demo, see a trace, see the dashboard, open a CI run that failed and the one that passed after the fix, see the alert that fired and the runbook entry it points to, read a reviewed pull request, and read a security review and runbook that are specific to this app rather than generic. Keep the README scannable, with headings for each requirement. If something isn't perfect, such as cold starts or a known weak spot in the security review, say so and say what you would do next. That honesty is exactly what a production engineer is hired for.
