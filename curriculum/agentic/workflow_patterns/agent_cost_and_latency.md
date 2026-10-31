### Introduction

A chatbot answer costs a fraction of a cent and takes a couple of seconds. An agent run that does the same job can cost a hundred times more and take a minute, and nobody notices until the bill arrives or a user gives up waiting. Agents are expensive in a way that single calls are not, because every step resends everything that came before it, and the steps happen one after another.

This lesson teaches you to see where an agent's money and time go, measure both for every run from the traces you already write, and cut them with four levers: prompt caching inside the loop, the right model for each step, parallelism, and hard budgets on steps, tokens and dollars. It ends with a cost and latency report you can produce for any run. The Support Ticket Pipeline project asks for exactly these numbers, and every agent you build after it should report them too.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Where an agent's tokens go: growing context, tool definitions, tool results, output and retries.
- How to measure cost and latency per run from your traces.
- Where an agent's time goes, and why steps add up.
- How prompt caching works inside an agent loop, and what silently breaks it.
- Choosing a model for each step, and judging cost per completed task.
- What parallelism saves and what it costs.
- Step, token and dollar budgets, and a cost and latency report for a run.

### Where an agent's tokens go

Recall from Tokens, Cost and Rate Limits that you pay for **input tokens** (everything you send) and **output tokens** (everything the model writes, including thinking), and that output tokens cost several times more per token. With a single call, the output price usually dominates. With an agent, input usually wins, for one reason: **the model has no memory between calls**. Each step sends the whole conversation again: the system prompt, every tool definition, the goal, and every earlier tool call and result.

Work through a small example. Say the system prompt plus tool definitions are 1,500 tokens, and each step adds about 800 tokens of tool call and tool result to the history. Step 1 sends 1,500 input tokens. Step 2 sends 2,300. Step 10 sends 8,700. Add them up and a ten-step run sends about 51,000 input tokens, while the model writes perhaps 1,500 output tokens in total. Even at five times the price per token, the output is a small slice of the bill. And because each step is bigger than the last, doubling the number of steps roughly *quadruples* the input tokens. In Big-O terms from Complexity and Core Data Structures, the total input of a run grows quadratically with its length.

Five things feed that growth:

1. **The growing history.** Every step pays again for every earlier step.
1. **Tool definitions.** They sit at the front of every request. Twenty tools at 300 tokens each is 6,000 tokens per step, 60,000 per ten-step run, before the agent does anything. This is part of why Scaling to Many Tools mattered.
1. **Bulky tool results.** A tool that returns a whole web page or a 5,000-row query result adds that weight to every later step. One careless tool can cost more than the rest of the run.
1. **Output and thinking.** Long reasoning on every step adds up, especially at high effort.
1. **Retries and loops.** A step that fails structured-output validation and reruns, an agent that calls the same tool three times, or an evaluator-optimizer loop that runs to its cap all multiply the bill. Anthropic reported in [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) that its agents used about four times as many tokens as chat, and its multi-agent system about fifteen times as many.

### Measuring a run from its traces

You can't cut what you haven't measured, and you already record what you need. Each model span from Agent Tracing and Debugging holds `input_tokens` and `output_tokens`, each span has `latency_s`, and the run span knows the model. A report is a short script over that file.

One addition first. With caching (later in this lesson), the API reports two more numbers in `usage`: `cache_creation_input_tokens` (tokens written to the cache) and `cache_read_input_tokens` (tokens read from it). They're billed at different prices from normal input, so your traces need them too. The agent later in this lesson records them as `cache_write` and `cache_read`.

Save this as `cost_report.py` next to `tracer.py` and `agent.py`:

```python
# cost_report.py  (run with: uv run cost_report.py traces/*.jsonl)
import json
import sys

# $ per million tokens: (input, output, cache write (5-minute), cache read).
# Prices at the time of writing; check the pricing page before relying on them.
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50, 0.125, 0.01),
    "claude-sonnet-5-5": (2.00, 10.00, 2.50, 0.20),
    "claude-opus-5-5": (4.00, 20.00, 5.00, 0.20),
}


def span_cost(model: str, s: dict) -> float:
    p_in, p_out, p_write, p_read = PRICES[model]
    return (s.get("input_tokens", 0) * p_in + s.get("output_tokens", 0) * p_out
            + s.get("cache_write", 0) * p_write + s.get("cache_read", 0) * p_read) / 1_000_000


def report(path: str) -> dict:
    spans = [json.loads(line) for line in open(path, encoding="utf-8")]
    run = next(s for s in spans if s["kind"] == "run")
    models = sorted((s for s in spans if s["kind"] == "model"), key=lambda s: s["step"])
    tools = [s for s in spans if s["kind"] == "tool"]
    print(f"\n{path}  goal: {run['input'][:60]!r}")
    print(" step  latency    fresh   c.read  c.write    out      cost")
    for s in models:  # (1) one line per model call: where did the tokens go?
        print(f" {s['step']:>4} {s['latency_s']:>7.2f}s {s.get('input_tokens', 0):>8} "
              f"{s.get('cache_read', 0):>8} {s.get('cache_write', 0):>8} "
              f"{s.get('output_tokens', 0):>6}  ${span_cost(run['model'], s):.5f}")
    total = {k: sum(s.get(k, 0) for s in models)
             for k in ("input_tokens", "cache_read", "cache_write", "output_tokens")}
    prompt = total["input_tokens"] + total["cache_read"] + total["cache_write"]
    cost = sum(span_cost(run["model"], s) for s in models)
    model_time = sum(s["latency_s"] for s in models)
    tool_time = sum(s["latency_s"] for s in tools)
    print(f" end: {run.get('end_reason')} after {len(models)} model calls, {len(tools)} tool calls")
    print(f" cost ${cost:.5f}  wall {run['latency_s']:.1f}s "  # (2) time: model vs tools
          f"(model {model_time:.1f}s, tools {tool_time:.1f}s)")
    print(f" prompt tokens {prompt}, {total['cache_read'] / max(prompt, 1):.0%} read from cache; "
          f"output tokens {total['output_tokens']}")
    return {"cost": cost, "seconds": run["latency_s"], "done": run.get("end_reason") == "end_turn"}


if __name__ == "__main__":
    runs = [report(path) for path in sys.argv[1:]]
    done = [r for r in runs if r["done"]]
    total = sum(r["cost"] for r in runs)  # (3) failed runs cost money too
    print(f"\n{len(runs)} runs, {len(done)} finished, total ${total:.5f}")
    if done:
        print(f"cost per completed task: ${total / len(done):.5f}")
```

Three things to notice:

1. **Per-step lines.** The "fresh" column is input billed at the full price. Watch it climb step by step; a sudden jump points at a bulky tool result.
1. **Model time versus tool time.** This tells you whether to speed up the model side (fewer steps, shorter output, caching) or the tools (a slow API, a missing timeout).
1. **Cost per completed task.** Total spend divided by runs that actually finished. A run that hits the step limit and returns nothing still costs money, so an agent that's cheap per run but fails half the time is expensive per useful result. This is the number to compare when you change anything.

### Where the time goes

Latency in an agent run is mostly a sum: every model call, then every tool call, one after another. A model call's time is roughly the **time to first token** (the wait before output starts, which grows with input size and thinking) plus the output tokens divided by the model's writing speed. Writing is the slow part. A step that writes 1,000 tokens of reasoning takes several times longer than one that writes 100, even with identical input.

So the biggest latency levers are the ones that cut sequential work: fewer steps, shorter outputs, lower effort on easy steps, and running independent work at the same time. Tool time is easy to forget. A search API that takes three seconds, called on eight steps, adds 24 seconds no model change can recover. Put a timeout on every tool, as you learned in Timeouts, Retries and Rate Limits, and look at the tool column in your report before blaming the model.

### Prompt caching in agent loops

You met **prompt caching** in Long Context and Context Engineering: the provider keeps the processed start of a prompt for a few minutes, and a later request that begins with exactly the same bytes reads it from the cache, cheaper and faster. Agent loops are the perfect case for it, because each step's request is the previous request plus a little more on the end. Without caching, step 10 pays full price for 8,700 tokens. With caching, it pays a small fraction for the 7,900 tokens that were already in the cache, and full price only for the new 800.

On the Claude API, the simplest way to turn it on is one top-level argument, `cache_control={"type": "ephemeral"}`. It places the cache point at the end of each request and moves it forward as the conversation grows. The pricing, at the time of writing:

- A **cache write** costs 1.25 times the normal input price (for the default 5-minute lifetime).
- A **cache read** costs at most 0.1 times the normal input price, and less on some current models.
- Each read resets the 5-minute timer, so a loop whose steps come less than five minutes apart keeps its cache warm the whole run.

A healthy cached loop has a recognizable signature in your report. Each step reads almost everything the previous step sent, and writes only what the last step added. If `cache_read` stays at zero, something is breaking the cache. Because caching is a prefix match, any change near the front invalidates everything after it. The common culprits in agents:

- **Something that changes on every call near the top**, such as the current time in the system prompt. Put it in the latest user message instead, or round it to the day.
- **A changing tool list.** Tools come first in the request, so adding, removing or reordering one breaks the whole cache. This is another reason Scaling to Many Tools preferred tool search, which adds definitions later instead of swapping the list.
- **Editing earlier messages**, for example trimming old tool results every step. Each edit is a miss from that point on. If you must trim, trim rarely and in large chunks. Compaction and Context Editing in the Memory section covers this properly.
- **Switching models.** Caches belong to one model. A loop that alternates between two models never reads its own cache.
- **A prefix that's too short.** Each model has a minimum cacheable length, a few hundred tokens or more. A tiny agent's first steps may be below it; the cache starts working once the history grows.
- **Parallel requests.** A cache entry can be read only once the request that writes it has started returning. Ten workers launched at the same instant with the same long prefix all pay full price.

Other providers differ in the details. OpenAI and Google cache long prefixes automatically, with their own discounts and minimums, so you don't mark anything, but the same prefix-match rules apply. Whatever the provider, the `usage` numbers are the only proof it's working.

Here is the agent from Agent Tracing and Debugging with caching on, cache numbers recorded, tool results capped, and a budget. Save it as `lean_agent.py` next to `agent.py`, `tracer.py` and `cost_report.py`:

```python
# lean_agent.py  (run with: uv run lean_agent.py)
import os

import anthropic
from dotenv import load_dotenv

from agent import SYSTEM, TOOLS, read_file  # from Agent Tracing and Debugging
from cost_report import span_cost
from tracer import Tracer

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()
MAX_STEPS, MAX_TOKENS, MAX_DOLLARS = 10, 60_000, 0.02  # (1) three budgets per run
MAX_RESULT_CHARS = 4_000


def run_tool(call) -> tuple[str, bool]:
    try:
        text, failed = read_file(**call.input), False
    except Exception as exc:
        text, failed = str(exc), True
    if len(text) > MAX_RESULT_CHARS:  # (2) a bulky result is paid for on every later step
        text = text[:MAX_RESULT_CHARS] + f"\n[truncated: {len(text)} characters in total]"
    return text, failed


def run_agent(goal: str) -> str:
    tracer = Tracer()
    with tracer.span("run", "invoke_agent", None, model=MODEL, input=goal) as run:
        messages, tokens, dollars, steps = [{"role": "user", "content": goal}], 0, 0.0, 0
        run["end_reason"], run["output"] = "step_limit", ""
        while steps < MAX_STEPS:
            if tokens > MAX_TOKENS or dollars > MAX_DOLLARS:  # checked before each call
                run["end_reason"] = "budget"
                break
            steps += 1
            with tracer.span("model", f"chat {MODEL}", run["span_id"], step=steps) as span:
                response = client.messages.create(
                    model=MODEL, max_tokens=16000, system=SYSTEM, tools=TOOLS,
                    messages=messages, cache_control={"type": "ephemeral"})  # (3)
                u = response.usage
                span.update(stop_reason=response.stop_reason, input_tokens=u.input_tokens,
                            output_tokens=u.output_tokens,
                            cache_write=u.cache_creation_input_tokens or 0,  # (4)
                            cache_read=u.cache_read_input_tokens or 0,
                            output=[b.model_dump(mode="json", exclude_none=True)
                                    for b in response.content])
            tokens += span["input_tokens"] + span["cache_write"] + span["cache_read"] + u.output_tokens
            dollars += span_cost(MODEL, span)
            messages.append({"role": "assistant", "content": response.content})
            run["output"] = "".join(b.text for b in response.content if b.type == "text")
            if response.stop_reason != "tool_use":
                run["end_reason"] = response.stop_reason
                break
            results = []
            for call in (b for b in response.content if b.type == "tool_use"):
                with tracer.span("tool", call.name, run["span_id"], step=steps,
                                 tool_use_id=call.id, input=call.input) as t:
                    text, failed = run_tool(call)
                    t.update(output=text, is_error=failed)
                results.append({"type": "tool_result", "tool_use_id": call.id, "content": text,
                                **({"is_error": True} if failed else {})})
            messages.append({"role": "user", "content": results})
        run.update(steps=steps, tokens=tokens, dollars=round(dollars, 6))
    print("trace saved to", tracer.path)
    return run["output"]


if __name__ == "__main__":
    print(run_agent("Read notes.md and todo.txt, then list every date they mention."))
```

The numbered comments:

1. **Three budgets.** Steps, total tokens and dollars, all checked before each model call. Budgets are covered in their own section below.
1. **Capped tool results.** The cap applies before the result ever enters the history, so it never breaks the cache. The note at the end tells the model the result was cut, so it can ask for less (a tool with a `max_rows` or `section` argument is even better; see Designing Tools for Agents).
1. **Caching on.** One argument. The tools and system prompt never change during the run, and the loop only ever appends to `messages`, so every request is a prefix-plus-a-bit of the next.
1. **Cache numbers in the trace.** These are the fields `cost_report.py` reads. Without them, a cached run would look cheaper in tokens but you couldn't price it.

Run `agent.py` and `lean_agent.py` on the same goal a few times each, then run `cost_report.py` over both sets of traces. In the sample report under "A cost and latency report for a run," step 1 is under the minimum cacheable length, so nothing is cached yet; from step 2 on, each step reads what the last one wrote. Without caching, the same run would cost about $0.00074 instead of $0.00052. On a short run the savings are small, and since writes cost a little extra, a one-step run can even cost slightly more. On a long run, most of the prompt comes from the cache.

### Choosing a model for each step

Not every step needs your most capable model. Chaining and Routing already sent easy tickets to the [cheap model](#/models) and hard ones to the [capable model](#/models). In an agent, the same idea applies per step: classifying an input, summarizing a long tool result or extracting fields are jobs a small model does well, while planning the next move in an unfamiliar task may need a big one. Reasoning **effort** is a second dial on the same model: low effort for routine steps, higher effort for the hard decisions.

Two cautions keep this honest. First, caches belong to one model, so switching models on alternate steps of one loop throws the cache away every time. Switch at boundaries instead: a separate workflow step that runs a whole sub-task on the cheaper model and hands back a short answer. (Subagents, in Multi-Agent Systems later, are another such boundary.) Second, judge every change by **cost per completed task**, not cost per call. A cheaper model that takes twice as many steps, or finishes 70% of tasks instead of 90%, can easily cost more per useful result. Measure on the same set of goals, with the same eval, before and after.

### Parallelism trades money for time

Parallelism comes in two kinds, and they behave differently.

**Parallel tool calls within one step** save both. When the model asks for three files in one response and your code runs all three at once (Tool Errors and Parallel Calls), you get one model turn instead of three. That's less waiting *and* fewer resends of the whole history. Encourage it in the system prompt when tool calls are independent.

**Parallel workers**, as in sectioning, voting or orchestrator-workers, save time but cost more. Each worker sends its own copy of the context, writes its own cache entry, and none of them can read the others' cache while they all start together. Five workers finish in roughly the time of the slowest one, for five times the tokens. That's a good trade when a user is waiting and a poor one for an overnight job, where a batch API at a discount (Production path) is the better tool.

### Budgets for steps, tokens and dollars

`max_tokens` caps a single response. Nothing caps a *run* unless you write it. A **budget** is a limit on a whole run, checked before each step, that stops the agent when it's spent. You want three:

- **A step budget** catches loops. You already have this as `MAX_STEPS`.
- **A token budget** catches runs that are short but heavy, like a few steps that each read a giant file.
- **A dollar budget** is the one your manager understands, and it stays correct when you change models.

Set them from data, not guesses. Run the agent on your eval goals, look at the cost of the runs that succeeded, and set the budget comfortably above the most expensive of them, perhaps two or three times it. A budget that cuts off good runs is too tight. One that has never fired might be too loose, or might simply mean your agent is healthy; your traces tell you which.

When a budget fires, stop cleanly. Record `end_reason: "budget"` on the run span, return whatever partial answer exists, and say so to the caller or route the task to a human. Some providers also let you tell the model its budget so it can pace itself and wrap up gracefully. On Claude this is a beta feature called task budgets; check the docs for which models support it. Treat it as a complement to your own hard limit, not a replacement.

### A cost and latency report for a run

Put it together, and every run you care about gets a short report like this one from `cost_report.py`:

```text
traces/run-20261029-101502-9c41e2aa.jsonl  goal: 'Read notes.md and todo.txt, then list every date they mentio'
 step  latency    fresh   c.read  c.write    out      cost
    1    1.32s      420        0        0     64  $0.00007
    2    1.05s        8        0     1210     41  $0.00017
    3    1.21s        8     1210      640     52  $0.00012
    4    1.88s        8     1850      290    188  $0.00015
 end: end_turn after 4 model calls, 3 tool calls
 cost $0.00052  wall 6.1s (model 5.5s, tools 0.6s)
 prompt tokens 5644, 54% read from cache; output tokens 345
```

When you report on an agent, in a README, a project or a design review, include: cost per run and per completed task; tokens split into fresh input, cache reads, cache writes and output; the cache hit rate; wall time split into model and tools; the number of steps; how runs ended (finished, step limit, budget); and the most expensive step. When you change something, show the same report before and after on the same goals, alongside the eval score with its confidence interval. A cost cut that drops quality isn't a saving.

This lesson covers single runs. The Production path's Cost and Latency section takes it to live traffic: latency percentiles across thousands of requests, time to first token for streaming UIs, caching across users, batching, fallbacks between providers and load testing, ending with the Cut the Bill project.

### On other providers

Where the tokens go is the same everywhere. Every major provider's chat API is stateless, so an agent on any of them resends its history, tool definitions and tool results on each step, and the total grows the same way. Traces, cost per completed task, budgets, per-step model choice and the parallelism trade-offs all carry over unchanged. What differs is caching and the usage fields. The `cache_control` argument, the 1.25 times write price and the 5-minute lifetime described above are Claude features. OpenAI caches long prompt prefixes automatically (its [Prompt caching guide](https://platform.openai.com/docs/guides/prompt-caching) explains the rules and options) and reports cached tokens *inside* its input total, as `usage.prompt_tokens_details.cached_tokens` in Chat Completions, while Claude's `input_tokens` leaves cache reads and writes out. Map the fields before you price them, as below, and add a `PRICES` row with that provider's rates. With open models through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), there's no per-token bill at all: cost becomes your hardware and electricity, and latency, the tokens per second your machine can produce, is usually the number to watch.

```python
def openai_usage_fields(usage) -> dict:
    """Map an OpenAI Chat Completions usage object onto the fields cost_report.py reads."""
    details = usage.prompt_tokens_details
    read = (details.cached_tokens or 0) if details else 0
    written = (getattr(details, "cache_write_tokens", None) or 0) if details else 0
    return {"input_tokens": usage.prompt_tokens - read - written,  # fresh input only, like Claude's
            "cache_read": read, "cache_write": written,
            "output_tokens": usage.completion_tokens}
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) in the Claude docs.
   - Focus on how the cache prefix is built (tools, then system, then messages), automatic caching, pricing, the minimum cacheable length, and "what invalidates the cache."
1. Read the "Model pricing" and "Prompt caching" parts of the [Claude pricing page](https://platform.claude.com/docs/en/about-claude/pricing), and update `PRICES` in `cost_report.py` if anything has changed.
1. Read the section on optimizing tool responses for token efficiency in Anthropic's [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents). It explains how pagination, filtering and truncation keep tool results from bloating every later step.
1. Practice: measure before you optimize.
   - Add `cache_write` and `cache_read` to your agent from Agent Tracing and Debugging (or use `lean_agent.py`), and run it on five goals with caching off and five with caching on. Produce reports with `cost_report.py` and write down the cost per completed task and the cache hit rate for each.
   - Put the current time in the system prompt and run again. Use the report to show the cache breaking, then fix it.
1. Practice: budgets and model choice.
   - Give your agent a goal that makes it read a large file several times, and set a dollar budget low enough to fire. Check that the run ends with `budget` and returns a partial answer.
   - Run your eval goals on the [cheap model](#/models) and the [capable model](#/models). Compare success rate, cost per completed task and average wall time in a small table, and write two sentences on which you'd ship.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why do input tokens usually dominate an agent's bill, and why does doubling the steps roughly quadruple them?](#where-an-agent-s-tokens-go)
- [What is cost per completed task, and why is it a better measure than cost per run?](#measuring-a-run-from-its-traces)
- [Which parts of an agent run make it slow, and which levers cut latency most?](#where-the-time-goes)
- [Why do agent loops benefit so much from prompt caching, and what silently breaks the cache?](#prompt-caching-in-agent-loops)
- [Why should you switch models at step boundaries rather than on alternate turns?](#choosing-a-model-for-each-step)
- [Which kind of parallelism saves money as well as time, and which only saves time?](#parallelism-trades-money-for-time)
- [What three budgets should an agent run have, and how do you choose their limits?](#budgets-for-steps-tokens-and-dollars)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) from Anthropic explains why smaller, sharper context makes agents both cheaper and better. It previews Context Engineering for Agents in the Memory section.
- [Prompt caching](https://platform.openai.com/docs/guides/prompt-caching) in the OpenAI docs shows how automatic caching works on another provider, with the same prefix-first rules.
- [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) in the Claude docs shows how to measure a prompt's size, tools included, before you send it.
