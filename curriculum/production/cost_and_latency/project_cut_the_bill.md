### Introduction

In this project you will take an app you already built and make it at least 40% cheaper or 40% faster, with no drop in quality. You will measure a baseline, apply prompt caching and model routing, add retries and a fallback model, and finish with a before-and-after table backed by real numbers.

This is a very common real-world task. Teams rarely ask "can you build it?" twice; they ask "can you make it cost less?" all the time. Doing it with measurements and an eval score, instead of hunches, is what makes the result believable.

### Before you start

- Create a new GitHub repo named `mimir-cut-the-bill`, and copy in the app you want to optimize. Your Workflow Automation Agent, Chat With Your Docs or the agent you traced in Trace Detective are all good choices. Pick one that makes several model calls per task and has a long system prompt or tool list, since those have the most to gain.
- You need an existing eval set for this app: the one from RAG Eval Harness, Trace Detective or the Workflow Automation Agent. If you don't have one, build at least 20 cases before you start. Without it you can't prove "no eval drop."
- Prepare 50 realistic requests to use as your benchmark. Reuse the same 50 for every measurement so the comparison is fair.
- Note your provider's current prices per million input, output and cached tokens from its pricing page, and record the date you checked.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Write the measurement script first

Before changing anything, write one script that runs the 50 requests, records tokens, cost and latency for each, and prints a summary. You will run it many times. If it is painful to run, you will stop measuring.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Measure the baseline.
   - Run the 50 requests and record, for each: input tokens, output tokens, cached tokens, cost (from token counts and published prices) and total latency.
   - Report total and average cost per task, and p50 and p95 latency.
   - Run your eval set and record the score.
   - Save the raw results to a file in the repo (for example `results/baseline.csv`).
1. Add prompt caching.
   - Restructure prompts so stable content (system prompt, tool definitions, reference documents) comes first and changing content comes last.
   - Show from the API's `usage` fields that cache reads are happening on repeated requests.
1. Route simple steps to a smaller model.
   - Identify at least one step (for example classification, extraction or tool selection) that a smaller, cheaper model can handle.
   - Show that step's eval results on both models before you switch it.
1. Add retries and a fallback model.
   - Retry temporary errors (`429`, overloaded, `5xx`) with exponential backoff and jitter, respecting `retry-after` when present, with a capped number of attempts.
   - After the last retry, fall back to a second model and log that it happened.
   - Write an automated test that simulates a `429` (with a fake or mocked client) and asserts that your code backs off, retries and finally uses the fallback model.
1. Measure the result.
   - Re-run the same 50 requests and the eval set with all changes in place.
   - Include a before-and-after table in your README with: average cost per task, p50 latency, p95 latency and eval score.
   - The optimized version must be at least 40% cheaper or 40% faster (on p50 or p95), with an eval score no lower than the baseline. If you fall short, keep going, or explain clearly what you tried and why it didn't get there.
1. Push to GitHub with a README covering how to reproduce your measurements, the results table, which change contributed how much and what you learned.

#### Extra credit

- Break the savings down change by change (caching alone, routing alone, both) in a second table.
- Run your eval set through a batch API and report how much cheaper it was than running it live.
- Add streaming and report time to first token before and after.

</div>

### Submitting your work

A strong submission makes the reviewer trust your numbers. Show the same 50 requests measured before and after, the date you checked prices, the raw results files and an eval score next to every cost figure. Explain trade-offs honestly: if routing saved money but added latency on some requests, say so. A clear table and two paragraphs of reasoning will impress more than any claim of "10x cheaper."
