### Introduction

In this project you will play detective on your own agent. You will add tracing so every model call and tool call is recorded, run it on a batch of real queries, read the traces to find where it goes wrong, and turn those failures into an eval set. Then you will fix one failure and prove the fix with a before-and-after run.

This is the habit that separates people who build demos from people who run AI products: they look at real behavior, they count failures, and they never fix the same bug twice. It's the loop from From Traces to Evals, run for real on your own agent. The eval set you build here also becomes the backbone of Ship It, later in this path.

### Before you start

- Create a new GitHub repo named `mimir-trace-detective`. Copy in the agent you want to investigate. Good choices are your Workflow Automation Agent, your Research Agent, One vs Many, or your Chat With Your Docs app. Pick the one with the most steps, since there will be more to find.
- Use `obs.py` from Logging and Tracing for OpenTelemetry tracing and JSON logs. Pick a tracing backend: [Langfuse](https://langfuse.com/docs) (free cloud tier or self-hosted with Docker) or [Arize Phoenix](https://arize.com/docs/phoenix/tracing/llm-traces) (runs locally, no Docker needed). Both are free, and Jaeger works too. Whichever you pick, keep the `SPANS_FILE` exporter on as well, because `sample.py` and your scripts read that file.
- Gather at least 30 realistic queries. Real is better than invented: ask two or three friends to write questions they would actually ask your agent, pull questions from forums in your agent's domain, or reuse queries from earlier eval sets. Keep these separate from any hard or odd queries you add on purpose to find failures, because only the realistic ones can tell you how often your agent fails (see Labeling Production Traces).
- Set a spend limit with your model provider. Thirty-plus agent runs, run several times, is cheap with the [cheap model](#/models) but not free.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Traces are user data

If your queries come from real people, their words end up in your traces. Redact before export as in [Privacy and cost](#/lessons/production/logging-and-tracing), keep the full traces in your tracing backend rather than in Git, and scrub every input before it becomes a committed eval case. Check your README screenshots for names and emails too.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Instrument the agent.
   - Every request produces one trace, with a child span for each model call and each tool call (and retrieval step, if you have one), following [Instrumenting an agent](#/lessons/production/logging-and-tracing).
   - Model call spans record model name, input tokens, output tokens, finish reason and latency, using the GenAI attribute names. Tool spans record tool name, arguments, result or error, and latency, and a failed tool sets the span's status to ERROR even when the agent recovers.
   - Include a screenshot of one full trace tree in your README.
1. Run at least 30 realistic queries through the traced agent and keep all the traces. Add any hard or odd queries on top of those, tagged so you can tell them apart.
   - Report total tokens, total cost (computed from token counts and your provider's published prices) and p50 and p95 latency across the run.
1. Review every trace and label it.
   - Mark each one pass or fail, with a one-line note naming the first step that went wrong, as in Error Analysis and Labeling.
   - Find and label at least 5 failures. If you find fewer, your queries are too easy; add harder ones (tagged as added on purpose).
   - Save the labels in your repo (for example `labels.csv` with trace ID, which set the query came from, pass/fail and note) or as scores in your tracing tool, and export them.
   - If you have more traces than you can read, build the queue with `sample.py` from From Traces to Evals, with a random slice and a flagged slice.
1. Do error analysis.
   - Group the failure notes into categories and include a table of categories with counts in your README.
   - Estimate the overall failure rate from the realistic queries only (or the random slice), never from the hard queries or the flagged slice, which were chosen because they probably fail.
1. Turn the failures into an eval set.
   - Each failure becomes a regression case in `evals/cases/prod_regressions.jsonl` with its input, its checks, its failure category, the source trace ID, the prompt version that failed and the date, as in [From a failed trace to a test case](#/lessons/production/traces-to-evals). Use a code check where possible and an LLM judge only where necessary. A check tests the failure, not one exact wording.
   - Decide per case whether it runs end to end or with frozen context (the retrieved chunks or tool results saved from the trace), and say which in the case.
   - Add a handful of passing cases too, so a fix that breaks things that used to work will show up.
   - Run the cases with `evals/run_regressions.py` (or your adaptation of it for your agent): at least 3 trials per case, majority wins, writing `results.json` in the `{"prompt": ..., "cases": {...}}` shape. Ship It reuses that file later, so keep the shape.
1. Fix one failure category and prove it.
   - Run the eval set before the fix and record the score. Confirm that every new regression case fails before the fix; a case that already passes doesn't capture the failure, so rewrite it. Make one change (a prompt edit, a better tool description, a guard in code). Run it again.
   - Show both scores and link to a before trace and an after trace for the same input.
1. Push to GitHub with a README covering how to run the agent and the evals, your run statistics, the failure table, the before-and-after result and what you learned.

#### Evidence

Your README must show:

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. (Linting, Formatting and CI) The `pytest` tests never call the model: test your checks (`contains`, `not_contains`, `regex` and any others) on fixed strings, and test the cost and latency statistics on a tiny hand-made spans file. Add the regression set as its own CI step, with your API key stored as a repository secret, as in [Wiring it into CI](#/lessons/production/traces-to-evals).
- Traces: the screenshot of one full trace tree, with the run span, model-call spans and tool spans visible, and an export of all the traces from your run (the `SPANS_FILE` JSONL is fine) with personal data removed. Name the trace IDs of your before and after traces, so a reviewer can find them.
- The labeled sample and the failure rate with an interval: the labels file, the failure category table with counts, and the failure rate over the realistic queries with a 95% confidence interval and its `n`, as in Eval Statistics (for example, "8 of 34 failed: 24%, 95% CI 12% to 40%"). Say which queries you left out of that rate and why.
- Regression cases that fail before the fix and pass after: the `run_regressions.py` output from before the fix, with each new case named as failing, and the output from after, with them passing and every passing case still passing. Show the eval set's overall pass rate before and after, each with a 95% confidence interval and its `n`. With a small set, the intervals will overlap; that's why the per-case before and after matters more than the headline number, so say so.
- A prompt-injection case, as in Prompt Injection and the Lethal Trifecta. Carry over the injection test from the project you copied the agent from, or write one: plant an instruction in something the agent reads (a document, a tool result, a fake web page) and check what the agent *did*, not what it said. Add it to the regression set, and show its trace, with the span where the planted text entered and the tool call that was (or wasn't) blocked.

#### Extra credit

- Add a dashboard view or saved filter in your tracing tool that shows cost and latency per request over time.
- Build a tiny trace viewer (for example in Streamlit or Gradio) that shows each trace with pass/fail buttons, so labeling is faster.
- Fix a second failure category, and show the first fix still holds.
- Run your code checks automatically on a sample of new traces as an online eval, and write an alert rule for the category you fixed, with a runbook entry, as in Alerting and Incidents.
- Ship the fix behind a feature flag to half of your test users, as in Feature Flags and A/B Tests, and compare the two arms.

</div>

### Submitting your work

A strong submission reads like a detective's case file. The reviewer should see the evidence (trace screenshots, the labeled table), your reasoning (failure categories and why you chose which one to fix) and the result (a score that went up, with traces to back it). Small, honest numbers beat big vague claims: "4 of 7 wrong-tool failures fixed, no regressions on the 10 passing cases" is exactly the kind of sentence hiring managers look for.
