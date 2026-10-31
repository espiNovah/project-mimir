### Introduction

In this project you will take an app you already built and make it at least 40% cheaper or 40% faster, with no drop in quality. You will measure a baseline under load, apply prompt caching and model choice, add a fallback route for bad days, and finish with a before-and-after table backed by real numbers and a paired eval comparison.

This is a very common real-world task. Teams rarely ask "can you build it?" twice; they ask "can you make it cost less?" all the time. Doing it with measurements and an eval score, instead of hunches, is what makes the result believable.

### Before you start

- Create a new GitHub repo named `mimir-cut-the-bill`, and copy in the app you want to optimize. Your Workflow Automation Agent, Chat With Your Docs or the agent you traced in Trace Detective are all good choices. Pick one that makes several model calls per task and has a long system prompt, tool list or shared documents, since those have the most to gain.
- You need an existing eval set for this app: the one from RAG Eval Harness, Trace Detective or the Workflow Automation Agent. It should have at least 50 cases. With 20, a paired comparison's interval is usually too wide to show that quality held (Eval Statistics, "How many examples you need"), so add cases before you start if you need to. Make sure it contains at least one prompt-injection case (see Evidence).
- Prepare 50 realistic requests to use as your benchmark. Reuse the same 50 for every measurement so the comparison is fair. They can overlap with your eval cases, but they should look like real traffic.
- Note your provider's current prices per million input, output, cache-write and cache-read tokens from its pricing page, and record the date you checked. On the Claude API, cache writes and cache reads are billed at different prices, so you need both.
- Create a separate API key, in its own workspace if your provider supports it, with a low spending limit for the load tests, as in Load Testing's "Testing against the real API."

<div class="lesson-note lesson-note--tip" markdown="1">

#### Write the measurement script first

Before changing anything, write one script that runs the 50 requests, records tokens, cost and latency for each, and prints a summary, plus one command that runs your load test and one that runs your eval. You will run them many times. If they are painful to run, you will stop measuring.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Measure the baseline.
   - Make sure every model call writes a trace with the route or step, model, fresh input tokens, cache-write tokens, cache-read tokens, output tokens, cost, latency and retry attempt, as in Logging and Tracing and Agent Cost and Latency.
   - Run a short load test against a staging deployment that calls the real API, using Locust or k6 from Load Testing with a fixed arrival rate (for example 1 request per second for 5 minutes), cycling through your 50 benchmark requests. Estimate the cost before you start and write it in your README. You need at least 200 completed requests for a meaningful p95.
   - From the traces, report average and p95 cost per request, and from the load tool, p50 and p95 latency (and time to first token, if the app streams) and the error rate.
   - Run your eval set and record the score with a 95% bootstrap confidence interval.
   - Save the raw results in the repo (for example `results/baseline_load.csv`, `results/baseline_eval.jsonl`).
1. Find where the money goes.
   - Group the baseline traces by step and rank the steps by total cost and by latency, as in Caching and Model Choice. Name the one or two steps you will optimize and write your target before changing anything.
1. Add prompt caching.
   - Restructure prompts into layers so shared content (instructions, tool definitions, reference documents) comes first and per-user and per-request content comes last. Add a test that two different users produce byte-identical prefixes.
   - Show from the `usage` fields that cache reads are happening on repeated requests, and report the cache hit rate.
   - If you also add a response cache, don't let it inflate your results: the load test replays the same 50 requests, so nearly every request would be a hit. Either turn the response cache off for the load test, or report its hit rate on a realistic sample of traffic separately.
1. Choose the model for each step you're optimizing.
   - Build a cost/quality table for that step, as in Caching and Model Choice, with at least three configurations (models and effort levels). Include the paired difference from the current configuration with its confidence interval.
   - Switch only to a configuration that passes a non-inferiority rule you state in advance, for example "the lower end of the paired difference is above -3 points." If you add a router or cascade, report its escalation rate.
1. Add a fallback route.
   - Keep your retries from Timeouts, Retries and Rate Limits, with a small retry budget per route. When they run out on a transient error (`429`, overloaded, `5xx`, timeout), fall back to a second model and log `route` and `fallback` on the trace, as in Batching, Rate Limits and Fallbacks. A `400` must not trigger the fallback.
   - Give the fallback model its own row in your cost/quality table, so you know it's acceptable before it ever serves a user.
   - Write automated tests with a fake client that simulate a `429` and assert that your code retries, then uses the fallback model, and that a `400` is raised without falling back.
1. Measure the result.
   - Re-run the same load test and the eval set with all changes in place.
   - The optimized version must be at least 40% cheaper (average cost per request) or 40% faster (p95 latency), and pass your non-inferiority rule on the full eval set. If you fall short, keep going, or explain clearly what you tried and why it didn't get there.
1. Push to GitHub with a README covering how to reproduce your measurements, the results tables, which change contributed how much and what you learned.

#### Evidence

Your README must show:

- A passing GitHub Actions badge, and a workflow that runs `ruff check`, `ruff format --check` and `pytest` on every push. Pytest covers the identical-prefix test, the `429` fallback test and the `400` no-fallback test, and your cost calculation, all with fake clients and no real API calls. (Linting, Formatting and CI)
- Traces: commit the traces (or the JSONL export) from both load tests, before and after, with any private data removed. A script in the repo computes every cost figure in your README from those traces and the dated prices, so a reviewer can rerun it and get the same numbers.
- The before-and-after cost and latency table from the two load tests: requests sent and completed, arrival rate and duration, average and p95 cost per request, p50 and p95 latency (and time to first token if you stream), error rate, cache hit rate and fallback rate. State the percentage change for cost and for p95 latency.
- Quality held: the eval score before and after, each with a 95% bootstrap confidence interval, plus the paired difference (after minus before) with its 95% bootstrap interval over the same cases, your non-inferiority margin, and how many cases flipped in each direction. Read every case that went from pass to fail and write one line on each. (Eval Statistics)
- Proof the cache works: `usage` numbers from two consecutive requests showing cache reads on the second, and the cache hit rate before and after.
- The cost/quality table for each step you changed, including the fallback model's row, with the date and prompt version.
- Prompt injection: at least one injection case in your eval set, run on every route you now use (the primary, any cheaper routed model and the fallback). For an agent, use a tool result or document that tells it to take an action the user didn't ask for, and show the action didn't happen, using your traces or audit log. For a non-agent app such as a RAG chatbot, use a retrieved document that tells the model to ignore its instructions. Cheaper models can be easier to hijack, so a cost cut that weakens your defenses doesn't count. (Prompt Injection and the Lethal Trifecta)

#### Extra credit

- Break the savings down change by change (caching alone, model choice alone, both) in a second table.
- Run your eval set through a batch API and report how much cheaper it was than running it live, using `usage` from the batch results.
- Add streaming and report time to first token before and after.
- Add a circuit breaker and a client-side token-bucket limiter, and show from a load test that your app stays under its provider limits and skips a failing route instead of waiting on it.
- Add a fallback route on a second provider or a local open model, with its own eval row.

</div>

### Submitting your work

A strong submission makes the reviewer trust your numbers. Show the same 50 requests measured before and after under the same load, the date you checked prices, the raw results files and a paired eval comparison next to every cost figure. Explain trade-offs honestly: if routing saved money but added latency on some requests, or the fallback model is noticeably weaker, say so. A clear table and two paragraphs of reasoning will impress more than any claim of "10x cheaper."
