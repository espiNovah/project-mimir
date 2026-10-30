### Introduction

Traces tell you what happened. Evals tell you whether a change made things better. The most valuable habit in LLM engineering connects the two: read real traces, find the failures, and turn each one into a test case so it can never silently come back.

You already know both halves. In Error Analysis and Labeling you read traces, wrote open-coding notes and grouped them into a failure taxonomy. In Code Checks and LLM-as-Judge and Evaluating RAG and Catching Regressions you built graders and ran an eval set in CI. Agent Eval Fundamentals applied the same ideas to agent runs. What changes in production is scale and mess. You no longer have 40 traces from a test set; you have 40,000 from real users, most of them fine, a few of them wrong in ways nobody imagined, and some of them full of personal data. This lesson is about the production loop: choosing which traces to read, labeling them on a schedule, turning failures into regression cases that are safe to commit, and wiring those cases into CI so each fix stays fixed.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Which production signals point at failures, and why you still need a random sample.
- Building a weekly review queue from exported traces.
- Labeling production traces, and estimating the real failure rate.
- Turning a failed trace into a regression case, including frozen context and redaction.
- Matching each failure category to the cheapest reliable check.
- Running the regression set and wiring it into CI.
- Closing the loop from fix to production.

### Where production failures hide

A small share of production failures announce themselves. Most don't. It helps to know which signals you have and what each one misses.

- **Errors.** A span with an ERROR status: the model API timed out, a tool raised, your code crashed. These are easy to find in traces and logs, and they're usually the least interesting failures, because ordinary debugging fixes them.
- **Odd stop reasons.** A `max_tokens` stop means a cut-off answer. A `refusal` means the model declined. An agent that hit its step limit is stuck. All of these sit on your spans as attributes.
- **Outliers.** The most expensive 5% of requests, the slowest ones, the agent runs with three times the usual steps. Outliers often hide loops and tools that returned huge outputs.
- **Explicit feedback.** A thumbs-down button that sends the `x-trace-id` header from Logging and Tracing back to a `/feedback` endpoint, which logs `{"trace_id": ..., "score": -1}`. Feedback is gold when you get it, but only a small share of users ever click, and they're not a fair sample: angry users click more.
- **Implicit feedback.** The user asks the same question again in different words, copies the answer and then edits it heavily, or leaves mid-conversation. These need a little analysis to detect but are far more common than button clicks.

Notice what's missing: the confident, polite, wrong answer that nobody complained about. It has no error, a normal stop reason, an average cost and no feedback. The only way to find it is to read a **random sample** of ordinary traces. That's why every review queue has two parts: a random slice that shows you what normal traffic really looks like, and a flagged slice that uses signals to find likely failures faster.

### Building a review queue

You need two things from your traces: a list of trace IDs to read, and enough content to read each one. With the `JsonlSpanExporter` from Logging and Tracing, your spans are already in a file; most backends can also export spans as JSON or CSV, and Langfuse and Phoenix have Python clients for pulling them. This script works on the JSONL format, so adapting it to an export from another tool means changing only the `summarize` function. Save it as `sample.py`:

```python
# sample.py: build this week's review queue from exported spans.
# usage: uv run sample.py spans.jsonl --feedback feedback.jsonl --random 30
import argparse
import json
import random
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("spans")
parser.add_argument("--feedback", help="JSONL lines like {'trace_id': ..., 'score': -1}")
parser.add_argument("--random", type=int, default=30)
parser.add_argument("--flagged", type=int, default=30)
args = parser.parse_args()

traces = defaultdict(list)                       # trace_id -> its spans
with open(args.spans, encoding="utf-8") as f:
    for line in f:
        span = json.loads(line)
        traces[span["trace_id"]].append(span)

thumbs_down = set()
if args.feedback:
    with open(args.feedback, encoding="utf-8") as f:
        thumbs_down = {r["trace_id"] for r in map(json.loads, f) if r["score"] < 0}


def summarize(trace_id: str, spans: list[dict]) -> dict:
    app = next((s["attributes"] for s in spans if s["name"] == "answer_question"), {})
    return {"trace_id": trace_id, "question": app.get("app.question"), "answer": app.get("app.answer"),
            "prompt_version": app.get("app.prompt.version"), "stop_reason": app.get("app.stop_reason"),
            "cost_usd": app.get("app.cost_usd", 0), "error": any(s["status"] == "ERROR" for s in spans)}


rows = [summarize(t, spans) for t, spans in traces.items()]
costly = sorted(r["cost_usd"] for r in rows)[int(len(rows) * 0.95)] if rows else 0


def flags(r: dict) -> list[str]:
    out = []
    if r["trace_id"] in thumbs_down:
        out.append("thumbs_down")
    if r["error"]:
        out.append("error")
    if r["stop_reason"] in ("max_tokens", "refusal"):
        out.append(f"stop:{r['stop_reason']}")
    if r["cost_usd"] > costly:
        out.append("top_5pct_cost")
    return out


rng = random.Random(0)                           # same input, same sample
random_part = rng.sample(rows, min(args.random, len(rows)))
picked = {r["trace_id"] for r in random_part}
flagged = [r for r in rows if flags(r) and r["trace_id"] not in picked]
flagged_part = rng.sample(flagged, min(args.flagged, len(flagged)))

with open("review_queue.jsonl", "w", encoding="utf-8") as f:
    for r in random_part:
        f.write(json.dumps(r | {"why": ["random"] + flags(r)}) + "\n")
    for r in flagged_part:
        f.write(json.dumps(r | {"why": flags(r)}) + "\n")
print(f"{len(rows)} traces -> {len(random_part)} random + {len(flagged_part)} flagged for review")
```

On a week of traffic it prints something like `4210 traces -> 30 random + 30 flagged for review`. The `why` field matters later: it records whether a trace came from the random slice or was flagged, so you never mix the two up when you count.

A few refinements as your app grows:

- **Stratify.** If your app has several routes, prompt versions or customer types, sample the random slice from each group separately, so a small but important group (the new feature launched on Tuesday, the enterprise customers) isn't drowned out by the busy one.
- **Weight toward change.** Right after a release, oversample traces from the new prompt version. That's where new failures appear.
- **Cap per user.** One power user can produce a third of your traffic. Limit how many of one user's traces enter the queue, so you don't label the same habits over and over.

### Labeling production traces

Label the queue exactly as you learned in Error Analysis and Labeling: read each trace, mark PASS or FAIL, write an open-coding note describing the first thing that went wrong, then group notes into categories with axial coding. The tiny labeling tool from that lesson works unchanged if you point it at `review_queue.jsonl`, and Langfuse and Phoenix both let you attach labels (they call them scores or annotations) to traces in their UI if you prefer.

A few things are different in production:

- **Make it a routine.** A 45-minute review every week, on the calendar, beats a heroic two-day session every quarter. New failure modes show up with new users, new features and model updates, and a weekly habit catches them while they're still small.
- **Read the whole trace for complex requests.** For an agent or a RAG pipeline, the summary row isn't enough. Open the full trace in your backend (the trace ID links straight to it) and find the first span that went wrong, as you practiced in Agent Tracing and Debugging. Your note should name that step: "retrieved the 2023 returns policy chunk instead of 2026," not "wrong answer."
- **Keep the labeling guidelines and the benevolent dictator.** Production traffic tests your definitions harder than any test set. When a new kind of borderline case appears, decide it, add it to the guidelines, and date the change.
- **Count rates from the random slice only.** The flagged slice is chosen *because* it probably failed, so its failure rate says nothing about your app overall. To report "about 12% of answers fail, 95% CI 5% to 26%," use only the random traces and the methods from Eval Statistics. With 30 traces a week the interval is wide; pool several weeks for a steadier number. Use the flagged slice to *find* new categories, and the random slice to *measure* how common each one is.

At the end of a session you should have a labels file and an updated table of failure categories with counts, exactly like the one in Error Analysis and Labeling. The biggest category is what you fix next. Every failed trace is also a candidate test case.

### From a failed trace to a test case

A **regression case** is a test that captures one failure, so that if it ever comes back, CI catches it. Turning a production trace into a good case takes more than copying the input. For each failure, record:

- **The input**, exactly as the user sent it, or as close as privacy allows (see below).
- **The check**: the condition a good output must meet. You decide this while labeling, because you know what was wrong.
- **The category** from your taxonomy, so you can report pass rates per category.
- **Where it came from**: the source trace ID, the prompt version that failed and the date. Six months from now, someone will ask why this case exists.

Suppose `askbot` answers questions for an outdoor clothing shop, and you found two failures last week: it told a customer they had 60 days to return an item when the policy is 30, and it answered "What's 2+2?" with three paragraphs. As cases, in `evals/cases/prod_regressions.jsonl`:

```json
{"id": "prod-1028-refund-window", "input": "Can I still return a jacket I bought 40 days ago?", "checks": [{"type": "regex", "value": "30[- ]day"}, {"type": "not_contains", "value": "60 days"}], "category": "outdated policy", "source": "trace fbf04146", "prompt_version": "ask-v3", "added": "2026-10-28"}
{"id": "prod-1028-no-hedge", "input": "What's 2+2?", "checks": [{"type": "max_words", "value": 20}], "category": "rambling", "source": "trace 4ec516ca", "prompt_version": "ask-v3", "added": "2026-10-28"}
```

**Scrub before you commit.** Your Git repo is not a safe place for user data: it's copied to every laptop and CI runner, and its history keeps whatever you delete. Before a case goes into the repo, remove anything personal. Often you can rewrite the input by hand so it keeps the failure but none of the person: "I'm Dana Okafor, order 88123, can I still return my jacket?" becomes "Can I still return a jacket I bought 40 days ago?" Check that the rewritten case still fails on the old prompt. If it doesn't, the detail you removed mattered, and you need a synthetic stand-in for it, such as a made-up order number in the same format. Keep the original trace in your tracing backend, under its access rules and retention, and link to it only by ID.

Also keep a few **passing cases** next to the failures, taken from the random slice. A fix for one category often breaks something nearby, and passing cases are how you notice.

### Freezing the context

For a single model call, the input is the whole story. For RAG and agents, it isn't. The answer depended on which chunks were retrieved and what the tools returned, and those change: the documents get edited, the web page moves, the database rows update. A case that reruns retrieval live today might pass for reasons that have nothing to do with your fix.

So decide which kind of case you want:

- **End-to-end cases** run the whole pipeline, live retrieval and tools included. They test what the user experiences, but they can start passing or failing because the world changed.
- **Frozen cases** save the context from the trace (the retrieved chunks, the tool results, even the date the user asked) and feed it straight to the generation step. They test one thing, your prompt and model, and they're stable. This is the replay idea from Agent Tracing and Debugging, turned into a permanent test. For a RAG app, it means your answer function needs an optional `context` parameter that skips retrieval when given.

Use frozen cases for generation failures ("had the right chunk and still said 60 days") and end-to-end cases for retrieval or tool failures ("never found the 2026 policy"), where the live step is what you're testing. Time-sensitive cases need a frozen date: "what's on sale this week?" means nothing without one.

### Matching the check to the failure

The rule from Code Checks and LLM-as-Judge applies: use the cheapest check that reliably catches the failure. Production categories tend to map like this:

| Failure category | Check |
| --- | --- |
| Wrong fact or number ("60 days") | Code: must contain the right value, must not contain the wrong one |
| Bad format, too long, broken JSON | Code: regex, word count, schema validation |
| Wrong tool, missing step, too many steps | Code on the trace: tool names, order, step count (Agent Eval Fundamentals) |
| Wrong final state (ticket not closed) | Code on the environment |
| Should have refused, or refused wrongly | Code for clear phrases; a judge for subtle cases |
| Tone, helpfulness, faithfulness to sources | A judge, validated against your labels for TPR and TNR |

Two cautions. A check should test the *failure*, not one exact wording: `not_contains "60 days"` plus `regex "30[- ]day"` survives the model rephrasing its answer, while `== "You have 30 days."` would fail on every rewrite. And a judge you add for a new production category needs its own small validation set, built from the traces you just labeled, before you trust it.

### Running the regression set

The runner loads every case, sends it through your app several times, applies the checks and writes per-case results. Because the app is a FastAPI service, the runner calls it in-process with `TestClient`, which you met in FastAPI Basics, so the eval exercises the same code path, middleware and tracing as production. Save it as `evals/run_regressions.py` (with an empty `evals/__init__.py`):

```python
# evals/run_regressions.py: run every regression case against the app, write per-case results.
# usage: uv run python -m evals.run_regressions --trials 3 --out results.json
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient

from app import PROMPT_VERSION, app

CHECKS = {                                       # name -> function(output, value) -> bool
    "contains": lambda out, v: v.lower() in out.lower(),
    "not_contains": lambda out, v: v.lower() not in out.lower(),
    "regex": lambda out, v: re.search(v, out) is not None,
    "max_words": lambda out, v: len(out.split()) <= v,
}

parser = argparse.ArgumentParser()
parser.add_argument("--cases", default="evals/cases/prod_regressions.jsonl")
parser.add_argument("--trials", type=int, default=3)
parser.add_argument("--out", default="results.json")
parser.add_argument("--fail-under", type=float, default=1.0)  # regressions should all pass
args = parser.parse_args()

cases = [json.loads(line) for line in Path(args.cases).read_text(encoding="utf-8").splitlines() if line]
client = TestClient(app)
results, by_category = {}, Counter()

for case in cases:
    if not case.get("checks"):
        raise SystemExit(f"case {case['id']} has no checks yet; finish it before committing")
    passes = 0
    for trial in range(args.trials):
        r = client.post("/ask", json={"question": case["input"]},
                        headers={"x-request-id": f"eval-{case['id']}-{trial}"})  # findable in traces
        out = r.json().get("answer", "") if r.status_code == 200 else ""
        passes += all(CHECKS[c["type"]](out, c["value"]) for c in case["checks"])
    results[case["id"]] = int(passes * 2 > args.trials)  # majority of trials must pass
    if not results[case["id"]]:
        by_category[case["category"]] += 1
        print(f"FAIL {case['id']} ({case['category']}): {passes}/{args.trials} trials passed")

score = sum(results.values()) / len(results)
print(f"{score:.0%} of {len(results)} regression cases pass; failing by category: {dict(by_category)}")
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
Path(args.out).write_text(json.dumps({"prompt": PROMPT_VERSION, "cases": results}, indent=2))
sys.exit(1 if score < args.fail_under else 0)                 # non-zero fails the CI step
```

Run it with `uv run python -m evals.run_regressions`. Before your fix, the output names the broken cases:

```text
FAIL prod-1028-refund-window (outdated policy): 0/3 trials passed
50% of 2 regression cases pass; failing by category: {'outdated policy': 1}
```

Some design choices to notice:

- **Several trials per case, majority wins.** Model output varies, so one lucky or unlucky run proves little. Three trials with a majority vote keeps a case from flipping on noise. A case that passes one trial in three is still telling you something; read it.
- **Every eval request carries a request ID starting with `eval-`.** With tracing on, each eval run produces real traces you can open when a case fails. Set `APP_ENV=ci` so they're easy to filter out of production views.
- **The default `--fail-under` is 1.0.** Each case was a real failure you fixed, so in principle all of them should pass. If a few flaky cases make that too strict, lower it a little, and fix or rewrite the flaky cases rather than ignoring them.
- **The output file uses the `{"prompt": ..., "cases": {...}}` shape**, one 1 or 0 per case. Keep that shape: it's what the CI gate in Prompt Versioning and CI Evals reads.

You can add a `judge` entry to `CHECKS` that calls the judge you built in Code Checks and LLM-as-Judge, for the categories that need one.

### Wiring it into CI

You already have an eval job in GitHub Actions from Evaluating RAG and Catching Regressions. Add the regression set to it as one more step:

```yaml
      - name: Production regression cases
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          APP_ENV: ci
        run: uv run python -m evals.run_regressions --trials 3 --out results/regressions.json
```

Now a pull request that brings back the 60-day answer fails CI with the case name in the log. Later in this path, Prompt Versioning and CI Evals upgrades this into a full eval gate: it scores both the pull request and the main branch in the same job, compares them case by case with a confidence interval, and runs the full set nightly. Your `results/regressions.json` already has the format that gate reads, so you'll plug these cases straight in rather than rebuilding anything.

Some rules keep a regression set healthy over months:

- **Never delete a case because it's failing.** That's the case doing its job. Fix the app, or, if the expected behavior has deliberately changed (the return policy really did become 60 days), update the case in the same pull request and say why in the commit message.
- **Keep it fast.** Code checks are nearly free, but every case costs model calls times the number of trials. When the set grows past what runs in a few minutes, keep a smoke subset on every pull request and run the rest nightly.
- **Watch for duplicates.** Ten cases for the same failure make that category count ten times. Keep two or three varied ones per category.

### Closing the loop

A fix isn't finished when CI goes green. The full loop is:

1. **Find**: sample and label production traces; the biggest category goes to the top of the list.
1. **Capture**: turn the failures into regression cases, scrubbed and with the right checks. Confirm they fail on the current version.
1. **Fix**: change one thing (the prompt, a tool description, retrieval settings, a guard in code), as in Comparing Fairly from the RAG lesson.
1. **Prove**: run the regression set and your main eval set before and after. The new cases should pass, and nothing else should break.
1. **Ship and watch**: after deploying, check the next week's random slice. Did that category's share in production actually drop? Offline cases test what you thought of; production tells you whether it worked for real users.

Step 5 is where many teams stop short. Some go further with **online evals**: running your code checks, and sometimes a validated judge, automatically on a sample of live traffic, and recording the scores on the traces. That turns a failure category into a number you can chart every day, and it's what Alerting and Incidents builds alerts on.

This loop is exactly what the Trace Detective project asks for: instrument an agent, run 30 or more real queries, label every trace, build the failure table, turn the failures into an eval set with code checks where possible, and prove one fix with before-and-after scores and traces.

### On other providers

Nothing in this loop depends on one provider, and that's a strength. Your review queue reads spans whose model-call attributes follow the GenAI conventions, so it works the same whether the traces came from Claude, OpenAI, Gemini or a local model. Your regression cases test your app's behavior through its own API, not a provider's response format, so they're also the safest way to evaluate a switch: run the whole set against the second provider before you move any traffic. Expect different failures, not just a different score. One model rambles where another refuses, so read the failing cases rather than trusting the percentage. The one provider-specific piece is a judge: if you run a judge on another provider's model, revalidate its TPR and TNR on your labels, because a judge's accuracy doesn't transfer between models. Langfuse and Phoenix datasets work with any provider. OpenAI also offers hosted evals in its platform, described in its [evals guide](https://platform.openai.com/docs/guides/evals), but keeping cases in your own repo means they follow you to any provider, including an open model you run yourself.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Hamel Husain's [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/), the classic write-up of the trace-review-eval loop.
   - Focus on the sections about looking at your data and building unit tests from failures.
1. Read [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) for a practical error analysis workflow.
   - Pay special attention to the parts on error analysis and building simple data viewers.
1. Read the [Langfuse datasets documentation](https://langfuse.com/docs/evaluation/experiments/datasets) to learn how to save traces as dataset items and run experiments against them.
   - Note how a dataset run links each new output back to the original item, so you can compare versions. If you use Phoenix instead, read its [datasets overview](https://arize.com/docs/phoenix/datasets-and-experiments/overview-datasets).
1. Read [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) from Anthropic's engineering blog, for how a team grows an agent eval suite from real failures and keeps it honest as models change.
   - Skim the [LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/) for answers to common questions such as how many traces to review and when to use an LLM judge.
1. Practice: using the traced service or agent from Logging and Tracing, run the loop once.
   - Send at least 60 varied requests, including some you expect to fail, and add thumbs-down feedback for a few. Build a review queue with `sample.py`.
   - Label every trace in the queue with PASS or FAIL and a note, group the notes into categories, and estimate the failure rate from the random slice only, with a confidence interval.
   - Turn at least three failures into scrubbed regression cases, plus two passing cases. Confirm the failures fail, fix the biggest category, and rerun.
   - Add the regression step to your CI workflow and open a pull request that breaks one case on purpose, to see CI catch it.
1. Optional practice: the [evals exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals) drills pass rates, confidence intervals and comparisons, which you need to report the random-slice failure rate honestly.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Which production signals point at failures, and what kind of failure do they all miss?](#where-production-failures-hide)
- [Why does a review queue have both a random slice and a flagged slice?](#building-a-review-queue)
- [Why should you estimate the failure rate from the random slice only?](#labeling-production-traces)
- [What does a regression case need besides the input, and why must you scrub it before committing?](#from-a-failed-trace-to-a-test-case)
- [When should a case freeze the retrieved context, and when should it run end to end?](#freezing-the-context)
- [Why should a check test the failure rather than one exact wording?](#matching-the-check-to-the-failure)
- [Why does the runner use several trials per case, and what should you do when a case starts failing?](#running-the-regression-set)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Using LLM-as-a-Judge for evaluation](https://hamel.dev/blog/posts/llm-judge/) walks through building a judge that agrees with a human expert, which is useful when a failure category can't be checked with code.
- [What We Learned from a Year of Building with LLMs](https://applied-llms.org/) collects lessons from practitioners, including many on evaluation and monitoring.
- [OpenTelemetry in the Claude docs](https://platform.claude.com/docs/en/manage-claude/opentelemetry) lists the content and token attributes on Claude's spans, useful if you pull review content straight from SDK spans instead of your own.
