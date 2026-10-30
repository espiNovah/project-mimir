### Introduction

This is the capstone of the Agentic Systems path. You will build an agent that automates a real multi-step workflow, and prove with an eval suite that it does the job reliably and safely. Choose a workflow you or someone you know actually does, for example:

- **Inbox triage:** read new emails, label them, draft replies and create tasks for the ones that need action.
- **Pull request review:** read a PR, run the tests, leave review comments and request changes or approve.
- **Lead research:** take a list of companies, research each one, fill in a CRM record and draft a first outreach email.

Whichever you pick, the agent uses tools via MCP or an agent SDK, asks a human before anything irreversible, and is measured by an eval suite that checks what it actually did to the environment. It pulls together everything from this path: the agent loop, tool design, MCP, memory, frameworks, safety and evaluation. Reuse code from "Your Own MCP Server", "Port Your Agent" and "Break Your Own Agent" wherever it fits.

### Before you start

- Create a GitHub repository named after your workflow, such as `mimir-inbox-triage-agent`, `mimir-pr-review-agent` or `mimir-lead-research-agent`.
- Build a test environment you can reset. Don't run evals against your real inbox or real repository. Use a fake mail server or a JSON file of sample emails, a throwaway GitHub repository or a local SQLite "CRM". Each eval scenario should start from a known state and end with a state you can inspect.
- Pick your stack: MCP servers for the tools plus any agent SDK or framework from "Port Your Agent", or your own loop. Read keys from environment variables and never commit them.
- Collect real inputs. Gather 20 to 30 realistic examples of the work (anonymized emails, real PRs, a real lead list) before you write prompts.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Build the eval early

Write your first ten scenarios and graders before the agent is finished. Run them after every change. The failures you see along the way become the "observed failure" scenarios this project requires, so keep a log of them from day one.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Build an agent that completes your chosen workflow end to end, from raw input to finished actions in the test environment.
1. Expose the agent's tools through MCP servers or your SDK's tool system, with clear names, descriptions and error messages that follow the tool design lessons.
1. Classify every tool as reversible or irreversible in your README. Irreversible actions (sending email, merging or approving a PR, writing to the CRM, anything that reaches another person) must go through a human approval step enforced in code that shows the exact action and arguments. Make the approval durable, as in Approvals and Permissions and Durable Execution: the run saves its progress and stops, the request appears on a small approval page (FastAPI or Streamlit is plenty), and the run resumes in a fresh process once someone decides, running the approved action exactly once.
1. Write an eval suite of at least 30 scenarios:
   - At least 20% of them (6 or more) must come from failures you actually observed while building or using the agent. Mark these in the suite and describe the original failure in one line each.
   - Include easy, typical and hard cases, plus cases where the right move is to do nothing or ask a human.
   - Include at least two prompt-injection scenarios. One hides instructions in content the agent processes, such as an email, a PR description or a code comment, or a company's web page, telling it to leak data or take an unauthorized action. The other targets the approval step, for example text claiming the action "was already approved by your manager", or an attempt to slip an extra recipient or file into an action that looks harmless. If your workflow involves back-and-forth with a person, a hostile simulated user who pushes for a forbidden action (the adversarial persona from Simulated Users and Benchmarks) counts as one of them.
1. Write graders that check the final environment state, not just the agent's text. For example: the correct labels were applied, no email was sent without approval, the CRM row has the right fields, the review comment points to the right line. Use LLM judges only for qualities code can't check, such as the tone of a draft, and validate each judge against at least 20 of your own labels.
1. Simulate approvals in the eval harness with a scripted approver that approves correct actions and rejects wrong ones, so the full suite runs without you.
1. Run every scenario at least three times and report pass^k with k of at least 3 (the share of scenarios where all k runs passed), alongside pass@1, average cost per scenario and average steps.
1. Show that the agent defends against your prompt-injection scenarios: the attack must fail in every run, verified by environment state. Name the structural defense that stops it.
1. Do at least one improvement round. Read the failed transcripts, group failures by cause, make changes and rerun the suite. Report before-and-after numbers.
1. Push your project to GitHub with a README that explains what the agent does, how to run it and the evals, the results and what you learned.

#### Evidence

Your README must show:

- A passing GitHub Actions badge, and a workflow that runs `ruff check`, `ruff format --check` and `pytest` on every push. Pytest covers your state graders, the scripted approver and the approval gate with a fake model client and no real model call, including a test that an irreversible tool can't run without approval even when the prompt says approval was already given (Approvals and Permissions). (Linting, Formatting and CI)
- The results table, before and after your improvement round: pass@1 with a 95% confidence interval bootstrapped over scenarios (average each scenario's runs first, as in Eval Statistics), pass^k with n and k stated, average cost and average steps per scenario. Add the change in pass@1 with a paired bootstrap interval over the same scenarios, and break the scores down by case type (easy, typical, hard, do-nothing or ask a human, observed failure, injection), and by persona if you used simulated users.
- Each LLM judge's TPR and TNR on at least 20 of your own labels, with confidence intervals, as in Code Checks and LLM-as-Judge.
- Traces: every trial writes a trace (Agent Tracing and Debugging), and the results table links the trace of each failed scenario. Commit the traces from one full suite run. They come from your resettable test environment, so they hold no real data.
- The failure log: for each observed-failure scenario, the one-line description of the original failure, and the grouped causes from your improvement round with a count for each.
- The prompt-injection results: for each injection scenario, the attack failed in every run, shown by environment state and your `audit.jsonl` (no forbidden email sent, no file shared, no CRM row changed). Report how many runs the agent *proposed* the injected action to the approver, since a proposal that only the approval gate stopped is a closer call than one the agent never made, and name the structural defense that stops each attack. (Prompt Injection and the Lethal Trifecta, Secure Design Patterns)
- A durable approval, end to end: a short recording or a terminal transcript in which a run pauses on an irreversible action, the process is stopped, the request is approved on the approval page, and a fresh process resumes and performs the action once. Show the matching lines from the audit log.

#### Extra credit

- Add simulated users for workflows that involve back-and-forth, such as a lead who replies with questions.
- Run the eval suite in CI on every pull request and block merges that lower pass^k.
- Run the agent on real (non-test) data for a week with approvals on, and report how many proposed actions you approved, edited or rejected.
- Add tracing with an observability tool and link a trace for each failed scenario from your results table.

</div>

### Submitting your work

This is a portfolio centerpiece, so make the README easy for a hiring manager to scan. Open with one paragraph on the workflow and why it matters, then a short demo video or GIF of the agent working, including an approval prompt. Next, show a results table (pass@1, pass^k, cost and steps, before and after your improvement round), followed by a diagram of the agent's tools and approval points. Link to the scenario files and graders, call out the observed-failure scenarios and the injection cases, and finish with an honest section on what still fails and what you'd do next.
