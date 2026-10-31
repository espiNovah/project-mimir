### Introduction

This is it: the project that ties the whole curriculum together. You will build a deployed agentic system that solves the real problem you found for a real user, prove that it works with evals and usage data, and write it up so other people can understand what you did and why it matters.

Everything you have learned shows up here: prompting and structured outputs, tools and workflow patterns, retrieval and memory if your problem needs them, evals, safety, deployment, tracing and cost control. The Core Open Brief gave you a problem to design for, and Ship It had you operate a system you'd already built. What's new here is the user. Real people will try your system, it will surprise you, and you will have to change it in response. That loop of building, watching and improving is the actual job.

This project becomes portfolio item number one in the Getting Hired path that follows, so treat the write-up and demo with the same care as the code.

### Before you start

- Complete the Finding a Real Problem, Working in a Team and Writing a Spec lessons. You need a chosen problem, a `SPEC.md` with measurable success criteria and a threat model, and at least three people who have agreed to try what you build.
- Create a GitHub repo named `mimir-capstone-<short-name>` (for example `mimir-capstone-invoice-chaser`) and commit your spec as one of the first files.
- Set the repo up as in Working in a Team: a handful of labels, a milestone for each milestone in your spec, a project board, a protected `main` that requires the CI check to pass, and an `AGENTS.md` (or your coding tool's instructions file).
- Reuse your production setup from Ship It: Dockerfile, deploy config, tracing, CI evals, prompt files and runbook template. Don't rebuild these from scratch.
- Use any model provider you like: Claude, OpenAI, Gemini, an open model you run yourself as in Running Open Models, or a mix. The lessons used one provider so the code stayed consistent, but the capstone is your design. Say in the README which models you chose and why, and if you host an open model, count the hosting in your cost per task.
- Collect real examples from your user (with their permission) to seed your eval set. Remove or mask personal information before committing anything.
- Set a spend limit with your model provider and budget your time. About 100 hours goes quickly; aim to have a rough working version in front of a user by the halfway point.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Ship to your user early

The most common capstone mistake is polishing for weeks before anyone else sees it. Put a rough version in front of your first user as soon as it does one useful thing. Their first ten minutes of use will teach you more than your next ten hours of guessing.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Write and maintain the spec.
   - `SPEC.md` describes the problem, user, design, non-goals and measurable success criteria, including at least one quality metric, one cost or latency budget and one user outcome, with a measured baseline.
   - It includes success criteria written as evals (quality, cost or latency, user outcome and safety, each with a grader, `n` and threshold), non-goals, a threat model listing every risky action, and cost and latency budgets with their arithmetic.
   - If the design changes during the build, update the spec and add a decision record in `docs/decisions/` saying what changed and why. Keep at least one decision record.
1. Build the agentic system.
   - It solves the problem in your spec using the simplest design that works. Explain in the README why you chose a workflow, an agent or a mix.
   - Any action that is risky or hard to undo (sending, deleting, paying, changing someone else's data) requires explicit human approval before it runs.
   - Every change goes through a pull request that links an issue (`Closes #N`) and says whether an AI tool helped write it.
1. Build an eval suite and show before-and-after results.
   - Cover every success criterion in your spec, using real examples from your user plus failure cases found in traces.
   - Include prompt injection or misuse cases relevant to your app, based on the threat model in your spec.
   - Report the score of your first working version and of your final version, and explain what changed between them.
   - Evals run on every pull request in CI.
1. Deploy it, trace it and track its cost.
   - The system runs at a public URL (protected by a login or access code as appropriate), deployed as in One Real Cloud or on another host you justify in the README, with a staging environment and a rollback you have tried, as in Environments and Releases. If your user works in a chat app or email, the system can meet them there, but it still needs a deployed service behind it.
   - Every request is traced with tokens and latency, and you report cost per task and p50 and p95 latency against the budget in your spec.
   - Set up at least one alert, on error rate or daily cost, as in Alerting and Incidents.
   - Include a `SECURITY.md` (your spec's threat model plus the OWASP table from Ship It) and a `RUNBOOK.md` specific to this system.
1. Get at least three real users to use it for at least two weeks, for at least 30 real tasks in total.
   - Keep usage logs (from traces or your own records) showing each user's real sessions.
   - Collect written feedback from each user and summarize it in a `FEEDBACK.md`: what worked, what didn't, and quotes where they help.
   - Make at least one change in response to feedback, and show its effect (an eval result, a metric or a follow-up quote).
   - While users are trying it, post a short weekly status update (for example on a pinned issue), as in Working in a Team.
1. Measure against your success criteria.
   - Include a table in the README with each criterion, its target, the baseline and the result you measured. Mark which ones you met and which you didn't.
   - Report at least one online metric from real use (such as drafts accepted without edits, or time saved) next to your offline eval scores.
1. Write it up and show it.
   - Publish a case-study post (on your blog, GitHub Pages or a free writing platform) covering the problem, the user, your design decisions, the results with numbers, what went wrong and what you would do next.
   - Record a demo video of about 3 minutes that shows the problem, the system solving a real task, and the results. Free tools like [OBS Studio](https://obsproject.com/) work well.
   - Link both from the top of your README, along with your project board and decision records.

#### Evidence

Your README must show each of these, with links a reviewer can follow:

- **CI.** A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and runs an eval subset on every pull request that fails when a score drops below its threshold. Show the status badge, and link one run that failed on a deliberately bad change and the passing run after the fix. (Linting, Formatting and CI; Prompt Versioning and CI Evals)
- **Traces.** Every production request produces a trace with spans for each model call and tool call, recording the model, prompt version, tokens and latency. Include a screenshot of one full trace and commit a sample of at least 20 traces with personal data removed. (Logging and Tracing)
- **Eval scores with confidence intervals.** Your first working version's score and your final score, each with a 95% confidence interval and `n`, plus the paired difference between them with its interval. (Eval Statistics)
- **Prompt injection.** At least one prompt-injection test that plants instructions in the untrusted input your system actually reads (an email, a document, a web page, a tool result), runs in CI, and shows what the system did: ignored it, refused, or was stopped by an approval step. If the agent has a risky action, also show a test that the action can't run without approval. (Prompt Injection, Approvals and Permissions)
- **Real users.** At least three real users, with usage logs showing how many real tasks each one ran, a `FEEDBACK.md` summarizing their written feedback with quotes, and the change you made in response with its measured effect.
- **Success criteria, met or missed.** The table from requirement 6, with every criterion from `SPEC.md`: target, baseline, measured value (with a confidence interval and `n` for rates) and met or missed. Misses stay in the table with a sentence on why and what you'd try next.
- **A deployed URL.** The live link, plus smoke-test output against it: `GET /health` and one real request.
- **A runbook.** `RUNBOOK.md` covers this system's likely incidents (provider down, cost spike, harmful or wrong output, leaked secret) with how you'd notice, first steps and how to roll back, and links the alert you set up.
- **Cost per task.** Average cost per task and p50 and p95 latency, computed from trace token counts and your provider's published prices (with the date you checked them), next to the budgets in your spec.

#### Extra credit

- Keep your users using it for a third and fourth week and report whether usage held up.
- Do it as a team of two or three: each pull request is approved by a teammate before it merges, and the team holds a retro whose actions become issues.
- Compare one or more key steps on two different model providers and report cost and quality for each.
- Open-source a reusable piece of your system (a tool, an MCP server or an eval) as its own package with documentation.

</div>

### Submitting your work

A strong capstone tells a clear story that someone outside AI can follow: a real person had a real problem, you built something, you measured it and real people used it. The README should open with one sentence on the problem, the demo video, the live link and the success criteria table. Behind that, a technical reviewer should find the spec, the eval suite and its results, traces, cost numbers, CI runs, security review, runbook, user feedback, and a project board and decision records that show how the work was run.

Be honest about what didn't work. A capstone that met three of its four criteria, and explains clearly why the fourth fell short and what you would try next, is more convincing than one that claims everything went perfectly. You'll polish the case study and demo further in the Getting Hired path, where this project becomes the centerpiece of your portfolio.
