### Introduction

In Long Context and Context Engineering you learned to treat the context window as a budget for a single call: put the documents first, cut what the model doesn't need, and cache what repeats. An agent makes that problem much harder. It makes twenty or fifty calls in one run, and each call carries everything the earlier calls produced. A tool result that arrives at step 3 is paid for again at steps 4, 5 and 6, and it competes for the model's attention until the run ends.

This lesson is about managing that budget across a whole run. You'll learn what fills an agent's context, why long contexts make agents worse and not only more expensive, how to measure context size step by step from the traces you already record, and the two habits that matter most: keeping tool results small, and fetching information when it's needed instead of loading everything up front. The rest of this section builds on these ideas: memory, compaction and long-running agents are all ways to keep the context small and useful.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why the context window is a budget for a whole run, not just one call.
- The five things that fill an agent's context, and which of them grow.
- Context rot: how long contexts make agents less accurate.
- Measuring context size per step from your traces.
- Shaping tool results so they stay small and useful.
- Just-in-time retrieval versus preloading, and agentic search versus vector RAG.

### A budget for the whole run

Recall from The Agent Loop that the conversation *is* the agent's state. Every turn, your code sends the whole message list again. That has a simple but important consequence: if each step adds about the same number of tokens, the input of each call grows in a straight line, and the **total** input you pay for across the run grows much faster.

Here is a small example. Say the system prompt and tool definitions take 3,000 tokens, and each step adds 2,000 tokens of tool calls and results.

| Step | Input tokens for this call | Total input paid so far |
| --- | --- | --- |
| 1 | 3,000 | 3,000 |
| 5 | 11,000 | 35,000 |
| 10 | 21,000 | 120,000 |
| 20 | 41,000 | 440,000 |

Twice the steps cost almost four times as much. Mathematicians call that growth **quadratic**: doubling the length roughly quadruples the total. A single step that adds 30,000 tokens, such as reading a whole log file, adds 30,000 tokens to *every later call*. That's why a tool that returns too much is one of the most expensive bugs an agent can have, even though nothing crashes.

Prompt caching, which you met in the Core path and in Agent Cost and Latency, softens the money side: an unchanged prefix of the conversation is billed at a much lower rate on the next call. It doesn't soften the quality side. The model still has to read every token, and as you'll see below, more tokens means worse attention. Some models also charge a higher rate per token once a prompt passes a size threshold, so check the pricing of the model you use.

So set a **context budget** for each agent: a number of input tokens per call you're happy to stay under, well below the model's maximum. The [Current Models](#/models) page lists each model's window, but a budget of a few tens of thousands of tokens is often a better target than the hundreds of thousands the window allows. You'll measure against that budget later in this lesson.

### What fills the context

On every call, an agent's context holds five kinds of content. It helps to know which ones are fixed and which ones grow.

1. **The system prompt.** Instructions, role and rules. Fixed for the run. Anthropic's advice is to find the "right altitude": specific enough to guide behavior, but not a long list of brittle if-then rules for every edge case.
1. **Tool definitions.** Fixed for the run, and often bigger than people expect. Scaling to Many Tools showed that fifty tools can cost tens of thousands of tokens before the user says a word.
1. **The message history.** The goal, the model's replies and reasoning, every tool call and every tool result. This is the part that grows, and tool results are usually the biggest piece of it.
1. **Retrieved data.** Documents, search hits or database rows the agent pulled in, usually as tool results. They're part of the history, but worth thinking about separately because you control how big they are.
1. **Scratch notes.** A plan, a to-do list or progress notes the agent keeps for itself. These can live in the context, or in a file the agent reads and writes, which keeps them from piling up. You'll build this in the next lessons.

Order matters too. Fixed content goes first and growing content goes last, which is exactly the order prompt caching needs. Rule of thumb: never change anything near the top of the context in the middle of a run, because everything after the change must be processed fresh.

### Context rot in long runs

The Core lesson introduced Chroma's "Context Rot" study: as inputs get longer, models get worse at using them, even on simple tasks. Researchers have also found that models use information at the start and end of a long input better than information in the middle. Anthropic describes the cause in terms of an **attention budget**. Every token attends to every other token, so the more tokens there are, the thinner the model's attention is spread.

Agents meet this in their own particular ways:

- **Goal drift.** The user's request sits at the very top. Thirty steps and 80,000 tokens later, it's buried in the middle, and the agent starts optimizing for whatever is freshest.
- **Distractors.** Old tool results that were relevant at step 4 still sit there at step 25. A search result about the wrong customer, or an outdated version of a file the agent has since edited, can mislead it.
- **Poisoned history.** A wrong conclusion or a failed attempt stays in the context and keeps influencing later steps. The model sees its own earlier mistake and repeats it, or treats a guess as a fact.
- **Slower and pricier steps.** Long inputs take longer to process, so each step gets slower as the run goes on.

The fix isn't a bigger window. It's the principle from the Core lesson, applied to every step: find the smallest set of high-signal tokens that lets the model take the next step well. Everything else in this lesson is a way to do that.

### Measure context size per step

You can't manage what you don't measure. The good news is that you already record what you need. The tracer from Agent Tracing and Debugging writes an `input_tokens` field on every model span, and every tool span holds the result text. Input tokens *are* the context size of that call, so a trace file gives you a step-by-step picture of the context.

This script reads one trace and prints the context size per step, how much it grew, and which tool results caused the growth. It needs nothing but the standard library. Save it as `context_report.py`:

```python
# context_report.py: context size per step from a trace
# usage: uv run context_report.py traces/run-....jsonl
import json
import sys

BUDGET = 40_000          # your per-call input budget; pick one for your agent
CHARS_PER_TOKEN = 4      # rough estimate for English text


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def context_size(span: dict) -> int:
    # With prompt caching, input_tokens only counts the uncached part, so add the cached parts.
    return (span.get("input_tokens", 0) + span.get("cache_read_input_tokens", 0)
            + span.get("cache_creation_input_tokens", 0))


def report(spans: list[dict]) -> None:
    models = sorted((s for s in spans if s["kind"] == "model"), key=lambda s: s["step"])
    tools = [s for s in spans if s["kind"] == "tool"]
    previous, total = 0, 0
    for span in models:
        size = context_size(span)
        total += size
        flag = "  <-- over budget" if size > BUDGET else ""
        print(f"step {span['step']:>2}  context {size:>7,}  (+{size - previous:>6,}){flag}")
        previous = size
        for tool in (t for t in tools if t["step"] == span["step"]):
            est = len(str(tool.get("output", ""))) // CHARS_PER_TOKEN
            if est > 1_000:  # only point at the big ones
                print(f"         {tool['name']}({json.dumps(tool['input'])[:40]}) "
                      f"returned ~{est:,} tokens")
    if models:
        print(f"peak context {max(map(context_size, models)):,}, "
              f"total input paid {total:,} over {len(models)} calls")


if __name__ == "__main__":
    report(load(sys.argv[1]))
```

A run that read a whole log file looks something like this:

```text
step  1  context   2,140  (+ 2,140)
step  2  context   2,410  (+   270)
         read_file({"name": "server.log"}) returned ~31,500 tokens
step  3  context  34,020  (+31,610)
step  4  context  34,390  (+   370)
step  5  context  34,700  (+   310)
peak context 34,700, total input paid 107,660 over 5 calls
```

Two things to notice. First, the jump appears on the step *after* the tool ran, because that's when the result is first sent to the model. The report lists each tool under the step that called it, right above the jump it caused. Second, one read cost about 31,000 tokens on each of the three later calls, roughly 90 percent of the run's total input. The fix is in the tool, not the model.

The trace tells you how big the context was. To see what it's *made of*, use the token counting endpoint you met in Scaling to Many Tools (a Claude feature; on other providers, see the end of this lesson). Count the same request with and without each part, and the difference is that part's share:

```python
# context_parts.py: how many tokens each part of the context costs
import os

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()


def count(messages: list[dict], system: str | None = None, tools: list[dict] | None = None) -> int:
    kwargs = {"system": system} if system else {}
    if tools:
        kwargs["tools"] = tools
    return client.messages.count_tokens(model=MODEL, messages=messages, **kwargs).input_tokens


def breakdown(system: str, tools: list[dict], messages: list[dict]) -> dict[str, int]:
    goal_only = messages[:1]                       # the first user message
    base = count(goal_only)
    with_system = count(goal_only, system)
    with_tools = count(goal_only, system, tools)
    everything = count(messages, system, tools)
    return {"goal": base, "system prompt": with_system - base,
            "tool definitions": with_tools - with_system, "history": everything - with_tools}
```

Call `breakdown(SYSTEM, TOOLS, messages)` inside your agent loop, every few steps, and print the result. You'll usually find that the system prompt and tools are fixed and modest, and that the history dominates after a handful of steps.

### Keep tool results compact

Tool results are the biggest and fastest-growing part of an agent's context, and they're entirely under your control, because you write the tools. Designing Tools for Agents taught you to return what the agent needs, not everything you have. In a long run, that rule is worth enforcing in code.

Four techniques cover most cases:

- **Return the fields that matter.** A customer record from a CRM API might have 80 fields. The agent probably needs five. Pick them in the tool.
- **Cap the size and say so.** Never return an unbounded result. When you cut something, say what you cut and how to get more, so the model doesn't think it saw everything.
- **Paginate.** Return the first 20 matches and a way to ask for the next 20, instead of all 2,000.
- **Return handles, not contents.** A search tool can return file paths, IDs or URLs with a one-line description. The agent then reads only the ones it needs.

Here are helpers that do the first two, plus a `read_file` tool that reads a range of lines. Save them as `shape.py`:

```python
# shape.py: keep tool results small, and say what was left out
MAX_CHARS = 4_000   # about 1,000 tokens; tune per tool


def pick(record: dict, fields: tuple[str, ...]) -> dict:
    """Keep only the fields the agent needs."""
    return {f: record[f] for f in fields if f in record}


def clip(text: str, hint: str, max_chars: int = MAX_CHARS) -> str:
    """Cut long text, and tell the model how to get the rest."""
    if len(text) <= max_chars:
        return text
    return (text[:max_chars] + f"\n[... cut: showing {max_chars:,} of {len(text):,} "
            f"characters. {hint}]")


def read_file(path: str, start_line: int = 1, max_lines: int = 100) -> str:
    """Tool: read part of a text file. Lines are numbered so the model can ask for more."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    end = min(start_line - 1 + max_lines, len(lines))
    body = "\n".join(f"{n}: {lines[n - 1]}" for n in range(start_line, end + 1))
    note = (f"\n[lines {start_line}-{end} of {len(lines)}. "
            f"Call read_file with start_line={end + 1} for more.]" if end < len(lines) else "")
    return clip(body + note, hint="Ask for fewer lines with max_lines.")
```

The bracketed notes are the important part. A silently cut result is worse than a long one, because the model will reason as if it saw the whole thing. A note like `[lines 1-100 of 4,210. Call read_file with start_line=101 for more.]` turns a dead end into a next step.

There's a judgment call in all of this: cut too much and the agent makes extra calls to get what it needs, each of which costs a model round trip. Anthropic's tool-writing guide suggests letting the agent choose, for example with a `response_format` parameter that accepts `"concise"` or `"detailed"`. Measure both ways with your traces and evals rather than guessing.

### Just-in-time retrieval versus preloading

There are two ways to get information to an agent. **Preloading** puts it in the context before the agent starts: paste the whole codebase, every relevant document or the full customer history into the first message. **Just-in-time retrieval** gives the agent lightweight references, such as file names, IDs or a search tool, and lets it load the details only when it decides it needs them.

People work the second way. You don't memorize a whole library; you know where the books are and fetch one when you need it. A coding agent that starts with a directory listing and has `grep` and `read_file` tools can find its way around a large codebase while holding only the few files it's working on. The file names, folder structure and timestamps carry information too: a file called `tests/test_billing.py` tells the agent what's inside before it opens it.

Each approach has a cost:

| | Preloading | Just-in-time |
| --- | --- | --- |
| Speed | Fast: no extra steps | Slower: each lookup is a tool call and a model round trip |
| Context size | Large from the first call | Small, grows only with what's used |
| Freshness | Can go stale during the run | Always reads the current version |
| Failure mode | Drowns the signal in noise | Agent may not look in the right place |

In practice, most good agents mix the two. Preload what's small, stable and almost always needed: the key instructions, a project's README or conventions file, the user's preferences. Retrieve the rest on demand. Claude Code works this way: a `CLAUDE.md` file is loaded at the start, and everything else is found with search tools. Agent Skills, later in this path, apply the same idea to instructions: only a short description is preloaded, and the full instructions load when a task needs them. This pattern is often called **progressive disclosure**.

### Agentic search or vector RAG

In the RAG section you built **vector RAG**: chunk documents, embed them, and retrieve the closest chunks for each question. **Agentic search** is the just-in-time alternative: the agent searches with tools such as `grep`, `glob`, a keyword search or a SQL query, reads what it finds, and searches again with better terms. Many coding agents rely on agentic search instead of a vector index.

Neither is always better. Choose based on the data and the questions:

- **Agentic search fits** when the data has structure the agent can navigate (code, folders, databases), when exact names matter (a function name, an error code, an invoice number), and when the data changes often, since there's no index to rebuild. It costs more steps, and it depends on the agent choosing good search terms.
- **Vector RAG fits** when the corpus is large, unstructured prose, when questions are phrased differently from the text ("how do I get my money back?" against a page titled "Refund policy"), and when you need one fast lookup rather than several. It costs an indexing pipeline and can return chunks that are similar but wrong.
- **You can combine them.** Give the agent your hybrid search from the RAG section as one tool among others, and let it decide when to use it and when to read a file directly.

Whichever you pick, the context rules are the same: return a short list of results with handles and snippets, not whole documents, and let the agent ask for more.

### Notes outside the window

Some information must survive the whole run but doesn't need to sit in every call: the plan, what's been done, what failed and why. Writing it to a file the agent can reread, sometimes called **structured note-taking**, keeps it safe without filling the context. A **subagent** goes one step further: it does a messy, token-hungry piece of work in its own fresh context and returns only a short summary to the main agent. You'll build notes and memory in the next lesson, compaction after that, and subagents in the Multi-Agent section.

### On other providers

Everything in this lesson except `context_parts.py` is provider-neutral: the budget, context rot, tool-result shaping, just-in-time retrieval and the trace report all work the same way with any model. Only the names change. OpenAI's Chat Completions API reports the context size as `usage.prompt_tokens` and its Responses API as `usage.input_tokens`, so record whichever your SDK returns in your model spans. Claude's token counting endpoint has no exact equivalent everywhere; on other providers, read `usage` after each call, or estimate before a call with the provider's tokenizer (OpenAI publishes `tiktoken`). For local open models, check the context length first: [Ollama sets a small default context on most laptops](https://docs.ollama.com/context-length) (raise it with the `OLLAMA_CONTEXT_LENGTH` setting), which an agent can outgrow within a few steps. OpenAI's [conversation state guide](https://platform.openai.com/docs/guides/conversation-state) covers how its APIs carry history and how that fills the window.

```python
# The same measurement through Ollama's OpenAI-compatible API (uv add openai)
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # key is ignored
response = client.chat.completions.create(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Say hello."}],
)
print("context size:", response.usage.prompt_tokens)   # record this in your model span
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Reread Anthropic's [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), which you first read in the Core path. This time focus on the agent parts.
   - Read "The anatomy of effective context" and "Context retrieval and agentic search" closely. Note what it says about the right altitude for system prompts and about loading data just in time.
   - Skim the long-horizon section. You'll study compaction and note-taking in the next two lessons.
1. Read the "Optimizing tool responses for token efficiency" part of Anthropic's [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents). It covers truncation, pagination, filtering and the `response_format` idea.
1. Read Drew Breunig's [How Long Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html). It names four ways long contexts go wrong (poisoning, distraction, confusion and clash), with examples from real agents.
1. Practice: measure and shrink the context of your agent from the Agent Loop From Scratch project.
   - Give it a task that reads several large files, run it with tracing on, and run `context_report.py` on the trace. Write down the peak context and the total input tokens.
   - Find the tool result that grows the context most. Rewrite that tool with the helpers in `shape.py` (a line range, a size cap with a note, or only the fields that matter).
   - Run the same task again three times and compare peak context, total input tokens and whether the task still succeeded. Report all three numbers before and after.
1. Practice: add `breakdown` from `context_parts.py` to your agent loop and print it every five steps. Write two sentences on which part of the context grew and which stayed fixed.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why does one large tool result early in a run cost far more than its own size?](#a-budget-for-the-whole-run)
- [What five kinds of content fill an agent's context, and which of them grow during a run?](#what-fills-the-context)
- [Name three ways long contexts make agents worse, not just more expensive.](#context-rot-in-long-runs)
- [How can you find the step that made the context jump, using only a trace file?](#measure-context-size-per-step)
- [Why should a tool say what it left out when it cuts a result?](#keep-tool-results-compact)
- [What should you preload, and what should an agent retrieve just in time?](#just-in-time-retrieval-versus-preloading)
- [When would you choose agentic search over vector RAG, and when the reverse?](#agentic-search-or-vector-rag)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Lance Martin's [Context Engineering for Agents](https://rlancemartin.github.io/2025/06/23/context_engineering/) groups the techniques into four families (write, select, compress and isolate), a handy map of this whole section.
- [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) is a practitioner's account of keeping the cache warm, using the file system as memory and keeping errors in the context.
- [Context Rot](https://research.trychroma.com/context-rot) from Chroma research is the study behind the "longer inputs, worse answers" finding, if you want to see the charts again.
