### Introduction

In the Prompt Lab you measured something for the first time: you labeled test inputs by hand, ran several prompts against them and let a score pick the winner. Evaluations, or *evals*, make that habit systematic. Practitioners consistently say that the teams who succeed with AI products are the ones with good evals, because evals turn "I think it's better" into a number, and let you change prompts, models and retrieval without fear. This lesson covers where evals come from: real data, a record of every model call, careful reading, and a well-built set of test cases. The next two lessons go deeper into labeling and into reading the numbers honestly.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an eval is and why AI systems need them more than ordinary software.
- What traces are, and how to log one for every model call.
- How error analysis turns traces into a list of real failure modes.
- Why generic metrics often mislead.
- How to build a golden dataset.
- How evals fit into the development loop.

### An eval is a test for behavior that varies

In Testing with pytest you wrote tests that check one exact output: `assert percentage(3, 4) == 75.0`. That works because ordinary code is **deterministic**: same input, same output, every time. A language model is different in two ways. Its output can change between runs, as you saw in the Prompt Lab when you ran each variant twice. And most tasks have many acceptable answers. There are hundreds of good one-sentence summaries of a review, so `assert summary == "..."` is useless.

An **eval** handles both problems. Instead of checking one exact answer, it scores outputs against *criteria* ("is the label one of the allowed values?", "does the summary mention the main complaint?") across a whole *dataset* of inputs, and reports a *rate*: 41 out of 50 passed, or 82%. A single failing case doesn't mean the system is broken, and a single passing case doesn't mean it works. The rate across many cases is what you track.

AI systems need this more than ordinary software for a simple reason: you can't read the code to know what it will do. The "logic" lives in billions of model weights plus your prompt. The only way to know how it behaves is to run it on many inputs and look.

### Traces are the raw material

A **trace** is the full record of one interaction with your system: the input, the exact prompt that was sent, the model and settings, the output, and useful facts like token counts and latency. In later sections a trace will also include retrieved documents and tool calls, but the idea is the same.

You can't evaluate what you didn't record. So the first piece of eval infrastructure is boring and essential: a function that logs every model call. The simplest good format is **JSONL** (one JSON object per line), which you met in Files and JSON. It's easy to append to, easy to read back with pandas, and easy to inspect in a text editor.

```python
# tracing.py  (uv add anthropic)
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
TRACE_FILE = Path("traces/calls.jsonl")
client = anthropic.Anthropic()


def traced_call(prompt_version: str, system: str, user_input: str, max_tokens: int = 1000) -> str:
    """Call the model and append one trace line to TRACE_FILE. Returns the text output."""
    record = {
        "trace_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,  # e.g. "few-shot-v2", so you know which prompt ran
        "model": MODEL,
        "system": system,
        "input": user_input,
    }
    start = time.perf_counter()
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_input}],
        )
        record["output"] = "".join(b.text for b in response.content if b.type == "text")
        record["stop_reason"] = response.stop_reason
        record["input_tokens"] = response.usage.input_tokens
        record["output_tokens"] = response.usage.output_tokens
        record["error"] = None
    except anthropic.APIError as exc:
        record["output"] = None
        record["error"] = repr(exc)  # failed calls are traces too
        raise
    finally:
        record["latency_s"] = round(time.perf_counter() - start, 3)
        TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with TRACE_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    return record["output"]
```

A few design choices are worth copying. Every trace has a unique `trace_id`, so you can refer to it in notes. The `prompt_version` field records which prompt produced the output; without it, a trace from last week is impossible to interpret after you've edited the prompt. The `finally` block writes the line even when the call fails, because errors are some of the most interesting traces. And the file is opened in append mode (`"a"`), so runs accumulate instead of overwriting each other.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Traces can contain private data

Once real users touch your app, traces hold whatever they typed. Keep trace files out of Git (add `traces/` to `.gitignore`) unless the data is synthetic, and in production treat them like any other user data.

</div>

### Error analysis

Once you have traces, the most valuable eval activity is also the simplest: **read them**. Slowly, one at a time, 30 to 100 of them. This is the step people most often skip, and the one that teaches you the most. Here is how a session goes, using a support-email classifier like the one from the Prompt Lab.

First, load the traces into pandas (from NumPy and pandas Basics) so you can read them in a notebook:

```python
import pandas as pd

traces = pd.read_json("traces/calls.jsonl", lines=True)
print(len(traces), "traces")
for row in traces.sample(30, random_state=0).itertuples():
    print(f"--- {row.trace_id[:8]} ({row.prompt_version})")
    print("INPUT: ", row.input[:500])
    print("OUTPUT:", row.output)
```

Then, for each trace, write a one-line note in your own words on anything that looks wrong. Don't use categories yet; just describe what you see. This is called **open coding**. A spreadsheet or a `notes.csv` with `trace_id,note` columns is enough:

```text
trace_id,note
3f2a9c1e,email about refund AND login problem; picked billing, ignored login
8b71d04a,answer had an explanation paragraph instead of just the label
c09e55f2,sarcastic "love paying twice!" read as positive feature request
51aa7e30,refund question labeled other
...
```

After 30 or so notes, patterns jump out. Group similar notes into a handful of categories (this is **axial coding**) and count them:

```python
notes = pd.read_csv("notes.csv")
notes["category"] = notes["note"].map(lambda n: "...")  # in practice you assign these by hand
print(notes["category"].value_counts())
```

```text
two topics, picked one        9
extra text around label       6
billing words missed          4
sarcasm misread               3
```

The counts tell you what to work on. Nine of thirty traces failing on two-topic emails is a bigger problem than three sarcasm cases, and it suggests a specific fix: tell the model how to choose when an email mentions two topics. The extra-text failures suggest a different fix, a stricter format instruction or tags. You now know what's wrong, roughly how often, and what to measure next. The next lesson, Error Analysis and Labeling, turns this into a repeatable process with a small labeling tool.

### Generic metrics are a trap

Libraries and dashboards offer ready-made scores such as "helpfulness," "coherence" or "relevance," usually on a 1-to-5 scale. They sound useful, but they rarely match the failures your users actually hit. A summary can score 4.2 on "coherence" while getting the price wrong every time. And when a vague score moves from 3.8 to 3.9, nobody knows what changed.

Prefer **specific, binary checks** tied to the failure categories you found: "Is the output exactly one allowed label?", "When the email mentions two topics, is the label the one the customer asks about first?", "Does the answer mention a price that isn't in the source?" Each check is pass or fail, and each one maps to a fix. Many can be plain code. Others need a human, or later a model acting as a judge, which you'll build in Evals in Practice.

### A golden dataset

A **golden dataset** is your fixed exam: a set of inputs with known good answers or clear pass criteria. Your Prompt Lab `test_set.jsonl` was a small one. A good golden set draws from three sources: real traces (especially failures), cases written to target each error category, and hand-written edge cases. Make sure it mixes:

- **Easy cases**, so you notice if something basic breaks.
- **Hard cases**, from your error categories.
- **Adversarial cases**, inputs that try to trick or confuse the system.
- **Out-of-scope cases**, where the right behavior is "other" or "I don't know."

Keep the set under version control and grow it whenever you find a new failure. Never tune your prompt's few-shot examples on the exact cases you test with, or your score will flatter you.

### Evals drive the development loop

Evals come in **levels**. Fast code checks (valid label? valid JSON? under 100 words?) are cheap enough to run on every change, like unit tests. Model-graded checks cost money and run less often. Human review and A/B tests with real users sit at the top: most trustworthy, slowest and most expensive. Most of your day-to-day iteration happens at the cheap levels.

Together they form a loop: **log traces, read them, find failures, add them to the golden set, change the system, rerun the eval, compare.** Without the eval you can't tell whether fixing the two-topic problem broke the sarcasm cases. With it, every change comes with evidence. One warning before you start comparing numbers, though: on a small dataset, a score difference of a point or two is usually noise. Eval Statistics, two lessons from now, shows you how to tell.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) by Hamel Husain.
   - Read the whole post. It walks through a real case study and introduces the levels of evaluation.
1. Read [LLM Evals: Everything You Need to Know](https://hamel.dev/blog/posts/evals-faq/), the evals FAQ by Hamel Husain and Shreya Shankar.
   - Read the questions about getting started and error analysis. Skim the rest and come back to it during the next two lessons.
1. Read [Task-Specific LLM Evals that Do & Don't Work](https://eugeneyan.com/writing/evals/) by Eugene Yan.
   - Read the introduction and the sections on classification and extraction, summarization and factual consistency. They show which metrics hold up in practice.
1. Read [Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) in the Claude docs for a practical guide to designing test cases and grading methods.
1. Practice: add `tracing.py` to your Prompt Lab project and route every model call through `traced_call`. Write 30 new, varied inputs for your task (not from your test set), run your best prompt on them, and do a full error analysis: read every trace, write a one-line note for each failure, group the notes into categories, count them, and write down your top three failure modes and a fix you would try for each.
1. Practice: work through the trace exercises in the [evals exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals). Make the tests pass with `uv run pytest exercises/evals/<exercise>`.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why can't you test a model's output with a single exact-match assert?](#an-eval-is-a-test-for-behavior-that-varies)
- [What fields should a trace record, and why does the prompt version matter?](#traces-are-the-raw-material)
- [What are open coding and axial coding?](#error-analysis)
- [Why are generic 1-to-5 scores like "helpfulness" often misleading?](#generic-metrics-are-a-trap)
- [What kinds of cases belong in a golden dataset?](#a-golden-dataset)
- [What are the levels of evaluation, and which do you run most often?](#evals-drive-the-development-loop)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) by Hamel Husain expands on error analysis and on building simple tools to view your data.
- [An LLM eval process](https://eugeneyan.com/writing/eval-process/) by Eugene Yan describes how eval-driven development fits into a team's day-to-day work.
