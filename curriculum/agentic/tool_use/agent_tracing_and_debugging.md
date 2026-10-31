### Introduction

A chatbot answer is one model call, so when it's wrong you read the prompt and the reply and usually see why. An agent run is twenty calls: model, tool, model, tool, model. When the final answer is wrong, the mistake might have happened at step 3, and everything after it was the agent faithfully building on a bad observation. Reading only the last message tells you almost nothing. This lesson turns the `print` statements you've been adding to your loops into proper **traces**: a structured record of every step that you can read, search, check automatically and even replay. It's the single most useful debugging habit in agent engineering, and the Agent Loop From Scratch project requires it.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How a trace of a whole run is built from spans, and what trace IDs and parent IDs are for.
- What to record for each model call and each tool call.
- How to add a small JSONL tracer to an agent loop.
- How to read a trace to find the step where a run went wrong.
- The common failure patterns and what each one looks like in a trace.
- How to replay a recorded run to test a fix.
- Where OpenTelemetry, its GenAI conventions and tools like Langfuse and Phoenix fit in.

### From one call to a whole run

In Why Evals Matter you wrote `traced_call`, which appends one JSON line per model call to `traces/calls.jsonl`. Each line had a `trace_id`, the input, the output, token counts, the stop reason, latency and any error. That was enough for a single-call app, because one request was one model call.

An agent run breaks that one-to-one match. One user request now causes many model calls and many tool calls, and you need to see them together, in order, as one story. The vocabulary for this comes from distributed systems, where one web request might pass through ten services:

- A **span** is one timed unit of work: a single model call, a single tool call, or the whole run. It has a name, a start time, a duration and whatever facts you attach to it.
- A **trace** is all the spans belonging to one run. Every span in the run carries the same **trace ID**, so you can pull one run out of thousands.
- Each span also has its own **span ID** and a **parent ID**, the span ID of the span it belongs to. The whole run is the **root span**, with no parent. Each model call and tool call is a **child span** whose parent is the run.

Parent IDs turn a flat list of lines into a tree:

```text
invoke_agent  (root: goal, final answer, end reason, total tokens)
├── chat claude-haiku-5-5     step 1  -> asks for read_file
├── read_file                 step 1  -> ERROR: file not found
├── chat claude-haiku-5-5     step 2  -> asks for read_file
├── read_file                 step 2  -> ok
└── chat claude-haiku-5-5     step 3  -> final answer
```

For now the tree is shallow. It gets deeper later: when an agent hands work to a subagent, or a tool itself calls a model, those spans become children of the span that started them, and the tree shows exactly who called whom.

### What to record in each span

Keep the fields from `traced_call` and add the ones an agent needs. A good rule: record enough to answer "what did the model see, what did it do, and what came back?" for every step, without having to rerun anything.

**On every span:** `trace_id`, `span_id`, `parent_id`, `kind` (run, model or tool), `name`, `timestamp`, `latency_s` and `error`. The error field is `None` when things went fine and the exception text when your code crashed. Failed spans are traces too, and often the most interesting ones.

**On the run span:** the goal, the `model`, the `prompt_version` and system prompt, the final answer, the total tokens, the number of steps and the **end reason**. The end reason is why the loop stopped: `end_turn` (the model finished), `step_limit` (your safety stop fired) or something unusual like `max_tokens` or `refusal`. Those names are Claude's `stop_reason` values; other APIs use their own (OpenAI's `finish_reason` says `stop`, `length` or `tool_calls`), so map them onto your end reasons as shown in [On other providers](#on-other-providers). You'll filter on it constantly. "Show me every run that hit the step limit" is a great way to find stuck agents.

**On model spans:** the step number, the full response content (text, tool requests and thinking blocks), the `stop_reason`, and the input and output tokens. Notice what's missing: the full message list sent to the model. It's long and grows every step, so storing it each time would make traces huge. You don't need it, because it can be rebuilt from the earlier spans, and later in this lesson you'll do exactly that.

**On tool spans:** the step, the tool name, the `tool_use_id` that links it to the model's request, the arguments, the result text and whether it was an error (`is_error`). Note that a tool that *reported* an error and a tool that *crashed* are different things: the first sets `is_error`, the second fills `error`.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Traces hold whatever the agent touched

An agent trace contains every file it read and every tool result it saw, which can include private data or secrets. Keep `traces/` out of Git unless the data is synthetic (the project asks you to commit traces, so use made-up files for those runs), and never log API keys or passwords in tool arguments.

</div>

### A tracer for the agent loop

Here is a tracer in about 40 lines. It's a class with one method, `span`, used as a **context manager**, which you met in Pythonic Python: the code inside the `with` block is the work being timed, and the `finally` clause writes the line whether the work succeeded or raised. Save it as `tracer.py`:

```python
# tracer.py: one JSONL line per span, one file per agent run
import json
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class Tracer:
    def __init__(self, folder: str = "traces"):
        self.trace_id = str(uuid.uuid4())               # one trace = one whole run
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = Path(folder) / f"run-{stamp}-{self.trace_id[:8]}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def span(self, kind: str, name: str, parent_id: str | None = None, **fields):
        """Time one unit of work. The caller fills in the yielded dict."""
        record = {
            "trace_id": self.trace_id,
            "span_id": uuid.uuid4().hex[:16],
            "parent_id": parent_id,                     # None for the root span
            "kind": kind,                               # "run", "model" or "tool"
            "name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **fields,
            "error": None,
        }
        start = time.perf_counter()
        try:
            yield record
        except Exception as exc:
            record["error"] = repr(exc)                 # crashed spans are traces too
            raise
        finally:
            record["latency_s"] = round(time.perf_counter() - start, 3)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, default=str) + "\n")
```

The `span` method hands your code a dictionary, `record`. Anything you add to it inside the `with` block (an output, a token count) ends up in the line. Each run gets its own file named with the time and the start of the trace ID, as the Agent Loop From Scratch project asks.

Now wire it into the `read_file` agent from Tool Errors and Parallel Calls, simplified to run tools one at a time. Set up a project with `uv add anthropic python-dotenv`, create a `sandbox` folder with `notes.md` and `todo.txt` in it, and save this as `agent.py`:

```python
# agent.py  (uv add anthropic python-dotenv)
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from tracer import Tracer

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
PROMPT_VERSION = "files-v1"
SYSTEM = "Answer questions about the files in the sandbox. Read files with read_file."
SANDBOX = Path("sandbox")
MAX_STEPS = 10
client = anthropic.Anthropic()

TOOLS = [{
    "name": "read_file",
    "description": "Read a text file from the sandbox folder. Pass a bare file name such as 'notes.txt'.",
    "input_schema": {"type": "object", "properties": {"name": {"type": "string"}},
                     "required": ["name"], "additionalProperties": False},
    "strict": True,
}]


def read_file(name: str) -> str:
    path = SANDBOX / name
    if path.parent != SANDBOX or not path.is_file():
        available = ", ".join(sorted(p.name for p in SANDBOX.iterdir()))
        raise ValueError(f"No file named '{name}'. Available files: {available}.")
    return path.read_text()


def run_tool(tracer: Tracer, parent_id: str, step: int, call) -> dict:
    result = {"type": "tool_result", "tool_use_id": call.id}
    with tracer.span("tool", call.name, parent_id, step=step,
                     tool_use_id=call.id, input=call.input) as span:
        try:
            result["content"] = read_file(**call.input)
        except Exception as exc:                        # report it, don't crash
            result |= {"content": str(exc), "is_error": True}
        span["output"] = result["content"]
        span["is_error"] = result.get("is_error", False)
    return result


def run_agent(goal: str) -> str:
    tracer = Tracer()
    with tracer.span("run", "invoke_agent", None, model=MODEL, input=goal,
                     prompt_version=PROMPT_VERSION, system=SYSTEM) as run:
        run["input_tokens"] = run["output_tokens"] = 0
        messages = [{"role": "user", "content": goal}]
        for step in range(1, MAX_STEPS + 1):
            with tracer.span("model", f"chat {MODEL}", run["span_id"], step=step) as span:
                response = client.messages.create(
                    model=MODEL, max_tokens=16000, system=SYSTEM,
                    tools=TOOLS, messages=messages)
                span["output"] = [b.model_dump(mode="json", exclude_none=True) for b in response.content]
                span["stop_reason"] = response.stop_reason
                span["input_tokens"] = response.usage.input_tokens
                span["output_tokens"] = response.usage.output_tokens
            run["input_tokens"] += response.usage.input_tokens
            run["output_tokens"] += response.usage.output_tokens
            messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason != "tool_use":
                run["end_reason"] = response.stop_reason
                break
            calls = [b for b in response.content if b.type == "tool_use"]
            results = [run_tool(tracer, run["span_id"], step, c) for c in calls]
            messages.append({"role": "user", "content": results})
        else:
            run["end_reason"] = "step_limit"
        run["steps"] = step
        run["output"] = "".join(b.text for b in response.content if b.type == "text")
    print("trace saved to", tracer.path)
    return run["output"]


if __name__ == "__main__":
    print(run_agent("Summarize notes.txt in one sentence."))
```

Run it with `uv run agent.py`. The loop is the one you already know. What changed:

- **The whole run is a span.** Everything happens inside `with tracer.span("run", ...)`, so the root span's line is written last, once the final answer, end reason and totals are known.
- **Every model call is a child span.** Its parent is `run["span_id"]`. The response content is saved with `model_dump(mode="json", exclude_none=True)`, which turns the SDK's block objects into plain dictionaries, in exactly the shape the API accepts back.
- **Every tool call is a child span** with the `tool_use_id`, so you can match each result to the request that caused it.
- **The `for ... else` clause** runs only when the loop used up all its steps without a `break`, which is how the end reason becomes `step_limit`.

The goal deliberately names `notes.txt`, a file that doesn't exist, so you get a run with an error in it to look at.

### Reading a trace

A raw JSONL file is hard to read, so write a small viewer. This script prints one run as a timeline and runs a few automatic checks you'll meet in the next section. Save it as `debug.py`:

```python
# debug.py: print one run as a timeline and flag common failure patterns
import json
import sys
from collections import Counter


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        spans = [json.loads(line) for line in f]
    return sorted(spans, key=lambda s: s["timestamp"])    # parents are written last


def timeline(spans: list[dict]) -> None:
    for s in spans:
        if s["kind"] == "model":
            asked = [b["name"] for b in s.get("output") or [] if b["type"] == "tool_use"]
            print(f"step {s['step']:>2}  model {s['latency_s']:5.2f}s  in={s.get('input_tokens')} "
                  f"out={s.get('output_tokens')}  stop={s.get('stop_reason')}  -> {asked}")
        elif s["kind"] == "tool":
            status = "ERROR" if s.get("is_error") else "ok"
            print(f"         tool  {s['name']}({json.dumps(s['input'])}) {status}: "
                  f"{str(s.get('output')).strip()[:70]}")
    run = next(s for s in spans if s["kind"] == "run")
    print(f"run ended: {run.get('end_reason')} after {run.get('steps')} steps, "
          f"{run.get('input_tokens')} in / {run.get('output_tokens')} out tokens")


def check(spans: list[dict]) -> list[str]:
    problems = []
    tools = [s for s in spans if s["kind"] == "tool"]
    calls = Counter((s["name"], json.dumps(s["input"], sort_keys=True)) for s in tools)
    for (name, args), n in calls.items():
        if n >= 3:
            problems.append(f"LOOP: {name}{args} was called {n} times")
    for before, after in zip(tools, tools[1:]):
        if before.get("is_error") and (before["name"], before["input"]) == (after["name"], after["input"]):
            problems.append(f"IGNORED ERROR: step {after['step']} repeated the call that failed")
    run = next(s for s in spans if s["kind"] == "run")
    if run.get("end_reason") != "end_turn":
        problems.append(f"UNFINISHED: run ended with {run.get('end_reason')}")
    problems += [f"CRASH in {s['name']}: {s['error']}" for s in spans if s.get("error")]
    return problems


def rebuild_messages(spans: list[dict], before_step: int) -> list[dict]:
    """The message list exactly as the model saw it at the start of `before_step`."""
    run = next(s for s in spans if s["kind"] == "run")
    messages = [{"role": "user", "content": run["input"]}]
    for step in range(1, before_step):
        model = next(s for s in spans if s["kind"] == "model" and s["step"] == step)
        messages.append({"role": "assistant", "content": model["output"]})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": s["tool_use_id"], "content": s["output"],
             **({"is_error": True} if s["is_error"] else {})}
            for s in spans if s["kind"] == "tool" and s["step"] == step]})
    return messages


if __name__ == "__main__":
    spans = load(sys.argv[1])
    timeline(spans)
    for problem in check(spans) or ["no known failure patterns found"]:
        print("!", problem)
```

Run it on the file your agent printed, for example `uv run debug.py traces/run-20261028-142206-2732e5a7.jsonl`. A run where the agent got stuck for a step looks something like this:

```text
step  1  model  1.21s  in=412 out=38  stop=tool_use  -> ['read_file']
         tool  read_file({"name": "notes.txt"}) ERROR: No file named 'notes.txt'. Available files: notes.md, todo.txt.
step  2  model  0.98s  in=501 out=30  stop=tool_use  -> ['read_file']
         tool  read_file({"name": "notes.txt"}) ERROR: No file named 'notes.txt'. Available files: notes.md, todo.txt.
step  3  model  1.05s  in=590 out=31  stop=tool_use  -> ['read_file']
         tool  read_file({"name": "notes.md"}) ok: Buy milk. Call the plumber about the leak on Friday.
step  4  model  1.40s  in=660 out=25  stop=end_turn  -> []
run ended: end_turn after 4 steps, 2163 in / 124 out tokens
! IGNORED ERROR: step 2 repeated the call that failed
```

Read a trace the way a detective reads a timeline: from the top, asking at each step "given what the model could see, was this a sensible move?" The goal is to find the **first** step that went wrong, because everything after it is usually a consequence. Here, step 1 is fine (the user did say `notes.txt`), and the error message is good: it lists the real files. Step 2 is the first bad step. The model ignored that list and tried the same name again. That points the fix at the model's instructions, not at the tool.

Also read the numbers. Input tokens climb every step because the whole history is resent; a step whose input jumps by thousands means a tool returned something huge. A model span with high latency is often one that thought hard or wrote a long answer. These patterns are invisible from the final answer, and obvious in a timeline.

### Common failure patterns

Agent runs fail in a handful of recognizable ways, and each leaves a distinct fingerprint in the trace. Learn to spot them:

- **Loops.** The same tool with the same arguments, three or more times. Often the tool's output gave the model nothing new to work with. `check` flags these.
- **Ignored tool errors.** A tool span with `is_error: true` followed by the identical call. Either the error message didn't say what to do instead, or the model didn't read it. Compare the error text with the next request to tell which.
- **Wrong tool.** The model called `search_web` when the answer was in a local file, or `delete_file` when it meant `read_file`. In the trace, the tool name doesn't fit the step's purpose. Usually two tool descriptions overlap or one is vague. Designing Tools for Agents covers the fix, and the next lesson but one, Scaling to Many Tools, shows how to measure it.
- **Bad arguments.** The right tool with wrong inputs: a date in the wrong format, a path with a folder in it, a made-up ID. Look at the arguments next to the tool's schema and description, and ask whether the description told the model the format.
- **Finishing too early.** The run ends with `end_turn` and a confident answer, but there's no tool span that could have produced the facts in it. "The tests pass" with no `run_tests` span is a classic.
- **Truncation and other odd stops.** A model span with `stop_reason: max_tokens` or `refusal`. Your loop should stop on these, and the end reason on the run span tells you it did.
- **Runaway cost.** The run hits `step_limit`, or one step's input tokens jump because a tool returned an entire web page. This is a design problem in the tool's output, not a model problem.

Automatic checks like `check` are cheap smoke detectors. Run them over every trace in a folder and they'll point you at the runs worth reading. They don't replace reading: most real failures, like "searched with a bad query" or "summarized the wrong paragraph", only make sense to a human looking at the step. This is the same error analysis you practiced in Error Analysis and Labeling, applied to runs. The next lesson, Agent Eval Fundamentals, turns these runs into transcripts you grade.

### Replaying a run

Once you've found the bad step, you want to test a fix. Rerunning the whole task is slow, costs money, and the model might not even make the same mistake again, since its output varies from run to run. A **replay** is better: rebuild the exact message list the model saw just before the bad step, then send it again with your change, and see what the model does now.

That's what `rebuild_messages` in `debug.py` does. Starting from the goal, it adds each recorded model response and each recorded tool result, step by step, until it reaches the step you asked for. Because the tool results come from the trace, the tools aren't run again. Nothing gets written, no web page has changed since, and the replay costs one model call. Save this as `replay.py`:

```python
# replay.py: rerun one step of a recorded run with a changed prompt
import sys

from agent import MODEL, TOOLS, client
from debug import load, rebuild_messages

path, step = sys.argv[1], int(sys.argv[2])
NEW_SYSTEM = ("Answer questions about the files in the sandbox. Read files with read_file. "
              "If a file is missing, pick the closest match from the list of available files.")

messages = rebuild_messages(load(path), before_step=step)
for m in messages:                                     # see the note below about thinking blocks
    if m["role"] == "assistant":
        m["content"] = [b for b in m["content"] if b["type"] not in ("thinking", "redacted_thinking")]

for trial in range(5):                                 # one replay proves little; run several
    response = client.messages.create(model=MODEL, max_tokens=16000, system=NEW_SYSTEM,
                                      tools=TOOLS, messages=messages)
    asked = [(b.name, b.input) for b in response.content if b.type == "tool_use"]
    print(f"trial {trial + 1}: stop={response.stop_reason} tool calls={asked}")
```

Run `uv run replay.py traces/run-....jsonl 2` to replay step 2 with the new system prompt. If all five trials now ask for `notes.md`, the fix works on this case. Two details matter:

- **Run several trials.** One good replay could be luck. Five trials of the same step give you a rough rate, and from Eval Statistics you know a handful of trials is enough to spot a fix that doesn't work, not to prove one that does. A fix that matters goes into your eval set as a new case.
- **Thinking blocks are removed.** Thinking blocks are the model's hidden reasoning, returned with each response. Newer Claude models can reject a request that sends an old thinking block back after anything earlier in the conversation changed, and changing the system prompt counts. Dropping them from the replayed history avoids that error. This rule is specific to Claude; other providers have their own rules for replaying reasoning, so check before you replay.

You can also replay with a changed tool description, a different model, or a fixed tool output you write by hand ("what if the error message had been clearer?"). The idea is always the same: freeze everything except the one thing you're testing.

### OpenTelemetry and the GenAI conventions

Your JSONL tracer works, but every team that writes its own uses different field names, so no tool can read everyone's traces. **OpenTelemetry** (often shortened to **OTel**) is the open, vendor-neutral standard that solves this. It defines how programs create spans, how spans carry trace and parent IDs, and how they're sent to a backend. Almost every observability product accepts it.

On top of that, OpenTelemetry's **GenAI semantic conventions** agree on names for AI-specific spans and attributes. Here is how your fields map onto them:

| Your JSONL field | GenAI convention |
| --- | --- |
| run span, `name="invoke_agent"` | span named `invoke_agent` (plus the agent's name, if it has one) |
| model span, `name="chat <model>"` | span named `chat {model}`, with `gen_ai.operation.name` = `chat` |
| `model` | `gen_ai.request.model` |
| `input_tokens`, `output_tokens` | `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |
| `stop_reason` | `gen_ai.response.finish_reasons` |
| tool span | span named `execute_tool {tool name}`, with `gen_ai.tool.name` |
| `tool_use_id`, `input`, `output` | `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result` |
| `error` | `error.type` and the span's error status |

The names in this lesson were chosen to line up, so moving to OTel later is a translation, not a redesign. Two cautions. The GenAI conventions are still marked "Development", which means names can change; check the current spec before you depend on one. And you don't always have to write these spans yourself. Instrumentation libraries such as OpenInference can create them for common SDKs, and some provider SDKs emit them directly. The Anthropic Python SDK, for example, has built-in OpenTelemetry tracing in beta. That is a Claude SDK feature; for the OpenAI SDK, or a local model reached through it, an instrumentation library such as OpenInference creates the same kind of spans. Whichever you use, wrap your agent loop in your own `invoke_agent` span so the model and tool spans have a parent.

### Trace viewers: Langfuse and Phoenix

Once traces are in OpenTelemetry format, you can view them in a **trace UI**: a web page that shows each run as a collapsible tree, with timings, token counts and the full content of each span. Two popular ones are free:

- **Langfuse** is open source (MIT license for its core). You can self-host it with Docker Compose, which you learned in the Core path, or use its free cloud tier.
- **Arize Phoenix** runs on your own machine after one install (`uv add arize-phoenix`). Its source is public under the Elastic License 2.0, which lets you use and self-host it for free but isn't an OSI-approved open-source license.

Both let you add scores and notes to traces and turn traces into eval datasets. For the agents in this section, JSONL files and `debug.py` are enough, and they keep you close to the data. You'll set up a real trace backend, sampling, privacy masking and dashboards in Logging and Tracing in the Production path, and use them in the Trace Detective project.

### On other providers

Spans, trace and parent IDs, the tracer, the failure patterns, the checks in `debug.py` and the idea of replay don't care which model you call, and the OpenTelemetry GenAI conventions were designed for every provider: the same `gen_ai.*` attribute names, with `gen_ai.provider.name` saying whose model it was. What changes is where you find each fact in the raw response before you copy it into a span. In OpenAI's Chat Completions API the reply is in `choices[0].message`, tool requests are in `message.tool_calls` with arguments as a JSON *string*, the stop signal is `choices[0].finish_reason` (`tool_calls`, `stop`, `length`, `content_filter`), and tokens are `usage.prompt_tokens` and `usage.completion_tokens`; a normal finish is `stop`, not `end_turn`, so `check` in `debug.py` needs that name. Token fields also differ in what they include: Claude's `usage.input_tokens` leaves out cached tokens, while OpenAI's `prompt_tokens` counts them, so note which you stored before comparing runs. Replay needs care too, because `rebuild_messages` builds Claude-shaped content blocks; for another provider, store the message exactly as that API returned it and rebuild from that. Here is the model span from `agent.py` rewritten for a local open model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) (set `MIMIR_MODEL` to a local model such as `qwen3:4b`, and convert `TOOLS` to OpenAI's format, where the schema goes under `function.parameters` as OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) shows):

```python
from openai import OpenAI  # uv add openai

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # or OpenAI() with OPENAI_API_KEY

with tracer.span("model", f"chat {MODEL}", run["span_id"], step=step) as span:
    response = client.chat.completions.create(model=MODEL, tools=TOOLS,
                                              messages=[{"role": "system", "content": SYSTEM}, *messages])
    choice = response.choices[0]
    span["output"] = choice.message.model_dump(mode="json", exclude_none=True)
    span["stop_reason"] = choice.finish_reason        # "tool_calls" here means "run the tools"
    span["input_tokens"] = response.usage.prompt_tokens
    span["output_tokens"] = response.usage.completion_tokens
```

OpenTelemetry keeps a separate page of [GenAI conventions for OpenAI](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/openai.md) that shows how these fields map to attributes, and OpenAI's Agents SDK has its own [tracing](https://openai.github.io/openai-agents-python/tracing/) built in. For open models, [OpenInference](https://github.com/Arize-ai/openinference) instruments the OpenAI client, so pointing it at Ollama gives you spans for a local model that Phoenix or Langfuse can display.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Traces](https://opentelemetry.io/docs/concepts/signals/traces/) page of the OpenTelemetry docs. It's the standard description of spans, span context, parent IDs and attributes, with a worked JSON example that looks a lot like your trace file.
   - Find the fields in its example span that match `trace_id`, `span_id` and `parent_id` in your tracer.
1. Skim the [GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) conventions on GitHub to see how `invoke_agent` spans are named and what attributes they carry. Don't memorize them; notice the "Development" status labels.
1. Read the "Production reliability and engineering challenges" section of Anthropic's [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system). It's a short, real account of why a team needed full tracing to debug agents that "weren't finding obvious information."
1. Practice: build `tracer.py`, `agent.py` and `debug.py` from this lesson and run the agent on three goals, including the one with the missing file. Read each trace with `debug.py` and write one sentence per run naming the first step that went wrong, if any.
1. Practice: break the agent and catch it in the trace.
   - Change `read_file`'s error message to just `"Error"`. Run the same goal several times and use `debug.py` to show the loop or ignored-error pattern. Restore the good message and compare the step counts.
   - Add a check to `check` that flags a run whose final answer is non-empty but which made no successful tool call ("finishing too early").
   - Use `replay.py` on a step that went wrong and report how many of the five trials the fix changed.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are a trace, a span and a parent ID, and how do they fit together for one agent run?](#from-one-call-to-a-whole-run)
- [What should you record on a model span and on a tool span, and why don't you need to store the full message list every step?](#what-to-record-in-each-span)
- [Why does the tracer write a span's line in a finally clause?](#a-tracer-for-the-agent-loop)
- [When reading a trace, why look for the first step that went wrong?](#reading-a-trace)
- [What does an ignored tool error look like in a trace, and how is it different from a loop?](#common-failure-patterns)
- [How does replaying a run work, and why should you run the replayed step several times?](#replaying-a-run)
- [What do OpenTelemetry's GenAI semantic conventions standardize?](#opentelemetry-and-the-genai-conventions)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [AI Agent Observability: Evolving Standards and Best Practices](https://opentelemetry.io/blog/2025/ai-agent-observability/) on the OpenTelemetry blog explains why the GenAI conventions exist and how agent frameworks are adopting them.
- The [Langfuse observability data model](https://langfuse.com/docs/observability/data-model) shows how one trace UI organizes traces, nested observations and sessions, a useful comparison with your JSONL format.
- [Get started with Phoenix](https://arize.com/docs/phoenix/get-started) walks through running Phoenix locally and sending it your first traces, if you want to see your runs as a tree now.
- [OpenTelemetry in the Claude docs](https://platform.claude.com/docs/en/manage-claude/opentelemetry) describes the spans the Anthropic SDKs and API can emit for you, so you can compare them with the ones you wrote by hand.
