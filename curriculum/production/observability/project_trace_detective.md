### Introduction

In this project you will play detective on your own agent. You will add tracing so every model call and tool call is recorded, run it on a batch of real queries, read the traces to find where it goes wrong, and turn those failures into an eval set. Then you will fix one failure and prove the fix with a before-and-after run.

This is the habit that separates people who build demos from people who run AI products: they look at real behavior, they count failures, and they never fix the same bug twice. The eval set you build here also becomes the backbone of Ship It, later in this path.

### Before you start

- Create a new GitHub repo named `mimir-trace-detective`. Copy in the agent you want to investigate. Good choices are your Workflow Automation Agent, your Research Agent, One vs Many, or your Chat With Your Docs app. Pick the one with the most steps, since there will be more to find.
- Pick a tracing backend: [Langfuse](https://langfuse.com/docs) (free cloud tier or self-hosted with Docker) or [Arize Phoenix](https://arize.com/docs/phoenix/tracing/llm-traces) (runs locally). Both are free.
- Gather at least 30 realistic queries. Real is better than invented: ask two or three friends to write questions they would actually ask your agent, pull questions from forums in your agent's domain, or reuse queries from earlier eval sets. Include some hard and some odd ones.
- Set a spend limit with your model provider. Thirty-plus agent runs, run twice, is cheap with a small model but not free.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Instrument the agent.
   - Every request produces one trace, with a child span for each model call and each tool call (and retrieval step, if you have one).
   - Model call spans record model name, input tokens, output tokens and latency. Tool spans record tool name, arguments, result or error, and latency.
   - Include a screenshot of one full trace tree in your README.
1. Run at least 30 real queries through the traced agent and keep all the traces.
   - Report total tokens, total cost (computed from token counts and your provider's published prices) and p50 and p95 latency across the run.
1. Review every trace and label it.
   - Mark each one pass or fail, with a one-line note explaining the judgment.
   - Find and label at least 5 failures. If you find fewer, your queries are too easy; add harder ones.
   - Save the labels in your repo (for example `labels.csv` with trace ID, pass/fail and note) or as scores in your tracing tool, and export them.
1. Do error analysis.
   - Group the failure notes into categories and include a table of categories with counts in your README.
1. Turn the failures into an eval set.
   - Each failure becomes a test case with its input and a check: a code assertion where possible, an LLM judge only where necessary.
   - Store it as a dataset in your tracing tool or a JSONL file in the repo, plus a script that runs the agent on every case and prints a score.
   - Add a handful of passing cases too, so a fix that breaks things that used to work will show up.
1. Fix one failure category and prove it.
   - Run the eval set before the fix and record the score. Make one change (a prompt edit, a better tool description, a guard in code). Run it again.
   - Show both scores and link to a before trace and an after trace for the same input.
1. Push to GitHub with a README covering how to run the agent and the evals, your run statistics, the failure table, the before-and-after result and what you learned.

#### Extra credit

- Add a dashboard view or saved filter in your tracing tool that shows cost and latency per request over time.
- Build a tiny trace viewer (for example in Streamlit or Gradio) that shows each trace with pass/fail buttons, so labeling is faster.
- Fix a second failure category, and show the first fix still holds.

</div>

### Submitting your work

A strong submission reads like a detective's case file. The reviewer should see the evidence (trace screenshots, the labeled table), your reasoning (failure categories and why you chose which one to fix) and the result (a score that went up, with traces to back it). Small, honest numbers beat big vague claims: "4 of 7 wrong-tool failures fixed, no regressions on the 10 passing cases" is exactly the kind of sentence hiring managers look for.
