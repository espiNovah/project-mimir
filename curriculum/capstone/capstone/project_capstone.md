### Introduction

This is it: the project that ties the whole curriculum together. You will build a deployed agentic system that solves the real problem you found for a real user, prove that it works with evals and usage data, and write it up so other people can understand what you did and why it matters.

Everything you have learned shows up here: prompting and structured outputs, tools and workflow patterns, retrieval and memory if your problem needs them, evals, safety, deployment, tracing and cost control. What's new is the user. Real people will try your system, it will surprise you, and you will have to change it in response. That loop of building, watching and improving is the actual job.

This project becomes portfolio item number one in the Getting Hired path that follows, so treat the write-up and demo with the same care as the code.

### Before you start

- Complete the Finding a Real Problem and Writing a Spec lessons. You need a chosen problem, a `SPEC.md` with measurable success criteria, and at least three people who have agreed to try what you build.
- Create a GitHub repo named `mimir-capstone-<short-name>` (for example `mimir-capstone-invoice-chaser`) and commit your spec as the first file.
- Reuse your production setup from Ship It: Dockerfile, deploy config, tracing, CI evals, prompt files and runbook template. Don't rebuild these from scratch.
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
   - If the design changes during the build, update the spec and note what changed and why.
1. Build the agentic system.
   - It solves the problem in your spec using the simplest design that works. Explain in the README why you chose a workflow, an agent or a mix.
   - Any action that is risky or hard to undo (sending, deleting, paying, changing someone else's data) requires explicit human approval before it runs.
1. Build an eval suite and show before-and-after results.
   - Cover every success criterion in your spec, using real examples from your user plus failure cases found in traces.
   - Include prompt injection or misuse cases relevant to your app.
   - Report the score of your first working version and of your final version, and explain what changed between them.
   - Evals run on every pull request in CI.
1. Deploy it, trace it and track its cost.
   - The system runs at a public URL (protected by a login or access code as appropriate) or in the place your user works, such as a chat app or email.
   - Every request is traced with tokens and latency, and you report cost per task and p50 and p95 latency against the budget in your spec.
   - Include a short security review and runbook, as in Ship It.
1. Get at least three real users to try it.
   - Keep usage logs (from traces or your own records) showing each user's real sessions.
   - Collect written feedback from each user and summarize it in a `FEEDBACK.md`: what worked, what didn't, and quotes where they help.
   - Make at least one change in response to feedback, and show its effect (an eval result, a metric or a follow-up quote).
1. Measure against your success criteria.
   - Include a table in the README with each criterion, its target, the baseline and the result you measured. Mark which ones you met and which you didn't.
1. Write it up and show it.
   - Publish a case-study post (on your blog, GitHub Pages or a free writing platform) covering the problem, the user, your design decisions, the results with numbers, what went wrong and what you would do next.
   - Record a demo video of about 3 minutes that shows the problem, the system solving a real task, and the results. Free tools like [OBS Studio](https://obsproject.com/) work well.
   - Link both from the top of your README.

#### Extra credit

- Keep your users using it for a second week and report whether usage held up.
- Compare one or more key steps on two different model providers and report cost and quality for each.
- Open-source a reusable piece of your system (a tool, an MCP server or an eval) as its own package with documentation.

</div>

### Submitting your work

A strong capstone tells a clear story that someone outside AI can follow: a real person had a real problem, you built something, you measured it and real people used it. The README should open with one sentence on the problem, the demo video, the live link and the success criteria table. Behind that, a technical reviewer should find the spec, the eval suite and its results, traces, cost numbers, CI runs, security review, runbook and user feedback.

Be honest about what didn't work. A capstone that met three of its four criteria, and explains clearly why the fourth fell short and what you would try next, is more convincing than one that claims everything went perfectly. You'll polish the case study and demo further in the Getting Hired path, where this project becomes the centerpiece of your portfolio.
