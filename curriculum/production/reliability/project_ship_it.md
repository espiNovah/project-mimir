### Introduction

This is the capstone of the Production and LLMOps path. You will take a real agent and run it the way a professional team would: containerized and live on a public URL, traced on every request, with a dashboard of cost and latency, evals that run on every pull request, prompts versioned in the repo, a security review and an incident runbook.

Every piece of this project is something you practiced in an earlier project in this path. The challenge here is putting them all together on one system and keeping them working. When you're done, you will have something most job candidates can't show: an AI system that is not just built, but operated.

### Before you start

- Create a new GitHub repo named `mimir-ship-it`, or continue in your existing project repo on a new branch.
- Choose what to ship:
  - **Recommended:** your Workflow Automation Agent from the Agentic Systems path.
  - **Fallback:** your Chat With Your Docs app with the UI from the Docs Chatbot UI project. This option requires an existing eval set, either from RAG Eval Harness or from Trace Detective.
- Reuse what you built earlier: the Dockerfile and deploy setup from Hello, Production; the tracing and eval set from Trace Detective; and the caching, routing and fallbacks from Cut the Bill.
- Set a spend limit with your model provider and make sure the public demo requires a login, an access code or a per-user rate limit. A public agent with no limits is an open invitation to drain your account.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Deploy it.
   - The app is Dockerized, starts locally with one command, and runs on a free host at a public demo URL.
   - All keys come from environment variables or the host's secret store.
   - A `/health` endpoint exists and is used by the host.
1. Trace every request.
   - Every request in production creates a trace with spans for each model call and tool call, including tokens and latency.
   - Each trace records the prompt version and the model used.
1. Build a cost and latency dashboard.
   - Use your tracing tool's dashboard or build a simple page. It must show cost per request, total cost per day, and p50 and p95 latency over time.
   - Include a screenshot in your README taken after at least a few days of real or test traffic.
1. Run evals on every pull request.
   - A GitHub Actions workflow runs your tests and an eval subset on each pull request, with the API key stored as a repo secret.
   - The job fails if the eval score drops below a threshold you set and justify.
   - Show a pull request in which CI caught a deliberately bad prompt change.
1. Version your prompts.
   - Every prompt lives in a file in the repo (for example `prompts/`), loaded by name, and changes go through pull requests.
1. Complete a security review.
   - Add `SECURITY.md` with a table covering every item in the OWASP Top 10 for LLM Applications: applies or not, mitigation, and how you tested it.
   - Include prompt injection tests in your eval set, and require human approval for any risky action your agent can take.
1. Write an incident runbook.
   - Add a one-page `RUNBOOK.md` covering what to do when: the model provider is down or rate-limiting, costs spike, a user reports a harmful or wrong output, or a secret leaks.
   - For each, list how you'd notice (which alert or dashboard), the first steps to take, and how to roll back to the last good version.
   - The [Managing Incidents chapter of Google's SRE book](https://sre.google/sre-book/managing-incidents/) is a good free model for how real teams structure this.
1. Push to GitHub with a README that leads with the demo URL and an architecture diagram, then links to the dashboard screenshot, CI runs, `SECURITY.md` and `RUNBOOK.md`, and ends with what you learned.

#### Extra credit

- Add an alert (email or chat message) when daily cost or error rate crosses a threshold, and trigger it once on purpose to prove it works.
- Run a "game day": simulate a provider outage by forcing errors, follow your runbook, and write up what happened.
- Run the full eval set nightly with a batch API and post the score to your dashboard.

</div>

### Submitting your work

A strong submission lets a reviewer verify every claim in a few clicks: open the demo, see a trace, see the dashboard, open a CI run that failed and the one that passed after the fix, and read a security review and runbook that are specific to this app rather than generic. Keep the README scannable, with headings for each requirement. If something isn't perfect, such as cold starts or a known weak spot in the security review, say so and say what you would do next. That honesty is exactly what a production engineer is hired for.
