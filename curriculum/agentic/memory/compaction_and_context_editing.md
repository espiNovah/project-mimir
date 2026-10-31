### Introduction

Every turn of an agent loop adds to the conversation: the model's reasoning, tool calls and, above all, tool results. A long task can fill even a very large context window, and well before it does, quality and cost start to suffer. Context Engineering for Agents showed you how to keep each addition small. This lesson covers what to do when the history is too big anyway: **context editing**, which removes specific content the agent no longer needs, like stale tool results, and **compaction**, which replaces older history with a summary.

Both are easy to get subtly wrong. A clumsy summary can drop the one detail the agent needed, and the agent carries on confidently without it. So alongside each technique, you'll learn what to keep word for word, and how to test that a compaction step didn't lose anything important.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why agent conversations grow so quickly, and how to measure it.
- Clearing old tool results, and why it's the lightest-touch fix.
- Compaction: summarizing older turns and carrying on.
- What a good summary keeps word for word, and when to compact.
- Claude's server-side context editing and compaction features.
- How these techniques interact with memory and prompt caching.
- Testing that compaction doesn't lose critical facts.

### Why the history grows so fast

Tool results are usually the biggest cost. A single file read or search result can be thousands of tokens, and as you saw in Context Engineering for Agents, every one of them is resent on every later turn. The model's own text is small by comparison: a tool call is a few dozen tokens, and its reasoning is often a few hundred.

You already have two ways to measure this. The API reports `usage.input_tokens` on every response, and your traces store it per step, so `context_report.py` from Context Engineering for Agents shows the history growing. The token counting endpoint lets you check a request's size *before* you send it. That's handy right before a step you suspect will be large.

When the numbers say the context is getting too big, you have three options, and many long-running agents use all three:

| Technique | What it does | What's lost |
| --- | --- | --- |
| **Clearing** (context editing) | Replaces old tool results with a short placeholder | The raw text of those results; the agent's reasoning about them stays |
| **Compaction** | Replaces older turns with a summary | Everything the summary doesn't mention |
| **Memory** (next to both) | Saves important facts to a file before they leave the context | Nothing, if the agent saved the right things |

### Clearing old tool results

Clearing is the simplest and safest technique. Once the agent has read a tool result and acted on it, it rarely needs the raw text again. Its reasoning ("the config file sets the timeout to 30 seconds, so the bug isn't there") stays in its own messages. So you can replace the result with a placeholder and keep everything else exactly as it was. Anthropic calls this one of the safest, lightest-touch forms of compaction.

Here's a client-side version. It keeps the most recent results, never clears results from tools you mark as important, and reports what it saved. Save it as `context_edit.py`:

```python
# context_edit.py: clear old tool results on the client
PLACEHOLDER = "[Old tool result cleared to save space. Call the tool again if you need it.]"


def field(block, key):
    """Blocks are dicts we wrote or SDK objects the API returned; read either."""
    return block.get(key) if isinstance(block, dict) else getattr(block, key, None)


def strip_thinking(messages: list[dict]) -> list[dict]:
    """Drop thinking blocks from assistant turns (see the warning below)."""
    return [{**m, "content": [b for b in m["content"]
                              if field(b, "type") not in ("thinking", "redacted_thinking")]}
            if m["role"] == "assistant" and isinstance(m["content"], list) else m
            for m in messages]


def clear_old_tool_results(messages: list[dict], keep: int = 3,
                           exclude: tuple[str, ...] = ()) -> tuple[list[dict], int, int]:
    """Return (new messages, results cleared, characters cleared). Never mutates the input."""
    names = {field(b, "id"): field(b, "name") for m in messages if m["role"] == "assistant"
             for b in m["content"] if field(b, "type") == "tool_use"}
    positions = [(i, j) for i, m in enumerate(messages)
                 if m["role"] == "user" and isinstance(m["content"], list)
                 for j, b in enumerate(m["content"]) if field(b, "type") == "tool_result"]
    to_clear = positions[:-keep] if keep else positions
    new = [dict(m, content=list(m["content"])) if isinstance(m["content"], list) else m
           for m in messages]
    cleared = chars = 0
    for i, j in to_clear:
        block = new[i]["content"][j]
        if block["content"] == PLACEHOLDER or names.get(block["tool_use_id"]) in exclude:
            continue
        chars += len(str(block["content"]))
        new[i]["content"][j] = {**block, "content": PLACEHOLDER}
        cleared += 1
    return new, cleared, chars
```

In your agent loop, after appending the tool results, check the size and clear when it passes a threshold:

```python
if response.usage.input_tokens > CLEAR_AT:
    messages, cleared, chars = clear_old_tool_results(messages, keep=3, exclude=("read_notes",))
    if cleared:
        messages = strip_thinking(messages)
        print(f"cleared {cleared} tool results, about {chars // 4:,} tokens")
```

The placeholder text matters. It tells the model that something was there and how to get it back, so the model calls the tool again instead of guessing what the result said. Keep `is_error` and the `tool_use_id` on each cleared block, as the code does, because every `tool_use` must still have a matching `tool_result`.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Editing history invalidates thinking blocks

Thinking blocks are the model's hidden reasoning, which Claude returns with each response and which your loop sends back. Newer Claude models check that nothing *before* a thinking block has changed since it was written, and on many accounts they reject the request if it has. Clearing an old tool result is exactly such a change. That's why the code calls `strip_thinking` whenever it clears something, just as `replay.py` did in Agent Tracing and Debugging. Stripping thinking once in a while costs little; doing it every turn throws away reasoning and resets the prompt cache each time. Other providers have their own rules for replaying reasoning, so check before you edit history. Claude's server-side features, below, avoid the problem entirely.

</div>

### Compaction: summarize and continue

Clearing only removes tool results. When the agent's own messages, reasoning and many small results add up too, you need **compaction**: replace the older part of the conversation with a summary of what matters (the goal, decisions made, progress so far and open problems), and let the agent continue from there. Done well, the agent barely notices. Done badly, it forgets a key detail and repeats work, or worse, makes a different decision the second time.

A do-it-yourself version is one extra model call. You send the older history with a "summarize this for your future self" prompt, then rebuild the conversation as the summary plus the last few steps, word for word. Add this to `context_edit.py`:

```python
SUMMARY_PROMPT = """Pause the task. A fresh copy of you will continue it without seeing the
conversation above, using only your summary. Write the summary under these headings:
GOAL: the user's request, copied word for word.
CONSTRAINTS: every rule, limit or preference the user gave, word for word.
DONE: what is finished, with exact file names, IDs, numbers and commands.
DECISIONS: choices made, and why.
OPEN PROBLEMS: unsolved errors, with the exact error text.
NEXT STEPS: what to do next.
Do not call any tools. Reply with the summary only."""


def compact(client, model: str, system: str, tools: list[dict], messages: list[dict],
            keep_steps: int = 3) -> tuple[list[dict], str | None]:
    """Summarize all but the last `keep_steps` steps. Returns (messages, summary or None)."""
    starts = [i for i, m in enumerate(messages) if m["role"] == "assistant"]
    if len(starts) <= keep_steps:
        return messages, None                       # nothing old enough to summarize
    cut = starts[-keep_steps]                       # kept part starts with an assistant turn
    older = messages[:cut]                          # ends with a user turn of tool results
    last = older[-1]["content"]
    last = last if isinstance(last, list) else [{"type": "text", "text": last}]
    request = older[:-1] + [{"role": "user", "content": [*last,
                                                         {"type": "text", "text": SUMMARY_PROMPT}]}]
    response = client.messages.create(model=model, max_tokens=8000, system=system,
                                      tools=tools, messages=request)
    summary = "".join(b.text for b in response.content if b.type == "text").strip()
    if response.stop_reason != "end_turn" or not summary:
        return messages, None                       # no usable summary; try again later
    first = {"role": "user", "content": (
        f"<goal>\n{messages[0]['content']}\n</goal>\n\n"
        f"<progress_summary>\n{summary}\n</progress_summary>\n\n"
        "Continue the task from where the summary leaves off.")}
    return [first, *strip_thinking(messages[cut:])], summary
```

Walk through the important choices:

- **The cut is at a step boundary.** The kept part starts with an assistant message, so every `tool_use` it contains still has its `tool_result` after it. Cutting between a tool call and its result would make the request invalid.
- **The summary request reuses the history as is.** It adds the summary prompt to the end instead of rewriting anything, and it sends the same system prompt and tools, so the model sees what it saw while working.
- **The goal is pasted in word for word**, not left to the summary. It's the one thing you can never afford to paraphrase.
- **The kept steps lose their thinking blocks**, for the reason in the warning above: they were written when the full history was in front of them.
- **A failed summary changes nothing.** If the call is cut off or calls a tool, the function returns the history unchanged, and the loop can try again later.

Compacting the same conversation again later is fine. The new summary covers the old summary plus everything since. Each round loses a little detail, though, which is one more reason to save important facts to memory as you go.

### What to keep word for word

A summary is a lossy copy, so decide in advance what must survive exactly:

- **The goal and the user's constraints.** "Don't email the customer," "keep it under $1,200," "use Python 3.12." A paraphrase like "be careful with the customer" isn't good enough.
- **Identifiers.** File paths, record IDs, URLs, branch names, version numbers. The agent will use them in tool calls, and a single wrong character breaks the call.
- **Exact error messages** for problems that aren't solved yet.
- **Decisions and their reasons**, so the agent doesn't reopen a settled question.
- **The most recent steps.** The model usually needs exact details from the last few turns, such as the output it just got, so keep them as they are.

What can go: raw tool output that's already been acted on, failed attempts that were fully resolved (keep a one-line "tried X, didn't work because Y"), and the back-and-forth of exploration. The headings in `SUMMARY_PROMPT` encode this list, and writing your own prompt for your task is worth the effort. A coding agent needs file names and test results; a research agent needs sources and open questions.

### Choosing when to compact

Compact well before the hard limit, for example at 50 to 70 percent of the window or of the context budget you set in Context Engineering for Agents. Leave room for the summary call itself, which has to read the whole history, and for a large tool result arriving just before you check.

Three more rules of thumb:

- **Compact between steps, never in the middle of one.** Only run it after all of a step's tool results have been appended.
- **Prefer clearing first.** Clearing old tool results often frees most of the space at almost no risk. Compact when clearing is no longer enough.
- **Log every compaction**: when it happened, the tokens before and after, and the summary itself. When a run goes wrong after a compaction, the summary in your trace is the first thing to read.

### Server-side options on Claude

Everything above works with any provider. Some providers now do these jobs on the server, and Claude offers both. The features below are **specific to the Claude API** and in **beta**, which means names and details can change, so check the docs linked in the Assignment before relying on them.

**Context editing** clears old tool results (and, separately, old thinking blocks) for you. You pass rules in a `context_management` parameter and keep sending your full history; the API applies the edits before the model sees it. Because the check described in the warning compares the history *as you sent it*, server-side clearing doesn't invalidate thinking blocks.

**Compaction** comes in two forms. With **on-demand compaction**, your code decides when: you send the conversation with a `compaction` parameter, and instead of a reply you get back a single `compaction` block holding the summary. That block then replaces the messages it summarized, as the first item in your history. With **threshold compaction**, you add a compaction edit to `context_management`, and the API summarizes automatically when the input passes a token threshold you set. Anthropic recommends the on-demand form wherever it's available.

```python
# server_side.py: Claude-only beta features (check the docs for current names)
CLEARING = {"edits": [{
    "type": "clear_tool_uses_20250919",
    "trigger": {"type": "input_tokens", "value": 30_000},   # start clearing above this
    "keep": {"type": "tool_uses", "value": 3},               # keep the 3 newest results
    "clear_at_least": {"type": "input_tokens", "value": 10_000},
    "exclude_tools": ["read_notes"],                         # never clear these
}]}


def step_with_clearing(client, model, system, tools, messages):
    response = client.beta.messages.create(
        model=model, max_tokens=16000, system=system, tools=tools, messages=messages,
        betas=["context-management-2025-06-27"], context_management=CLEARING)
    for edit in (response.context_management.applied_edits
                 if response.context_management else []):
        print(f"cleared {edit.cleared_tool_uses} results, {edit.cleared_input_tokens:,} tokens")
    return response


def compact_on_demand(client, model, system, tools, messages, instructions):
    response = client.beta.messages.create(
        model=model, max_tokens=8000, system=system, tools=tools, messages=messages,
        betas=["compact-2026-09-04"],
        compaction={"type": "summarize", "instructions": instructions})
    if response.stop_reason != "compaction":
        return messages                                      # no summary; try again later
    block = [b.model_dump(exclude_none=True) for b in response.content]
    return [{"role": "assistant", "content": block},        # the summary goes first
            {"role": "user", "content": "Continue the task."}]
```

A few rules from the docs that are easy to miss:

- **Send the compaction block back exactly as it came**, including its signature, on every later request, and with the same beta header. Remove the messages it summarized; if they stay in front of the block, the request fails.
- **Count tokens from `usage.iterations`.** The summarization work is reported there, not in the top-level `input_tokens` and `output_tokens`.
- **Use one kind at a time.** A compaction request can't also carry `context_management`. Start with one technique, measure it, and add the other only if you need it.
- **Write your own `instructions`** when the default summary drops something your task needs. They replace the default prompt entirely, so include "do not call tools," as `SUMMARY_PROMPT` does.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Let a tool runner do it

If you use the SDK's tool runner instead of your own loop, it can send the on-demand compaction request for you when you ask it to. See the "Compact in a loop" part of the on-demand compaction docs.

</div>

### Pair clearing with memory

Clearing and compaction both throw information away. Before that happens, the agent can save anything important to a memory file or progress notes, so nothing essential is lost. The simplest version is a `save_note` tool, plus a line in the system prompt: "Before you finish with a large tool result, save any fact you'll need later with save_note." Mark the notes tool with `exclude_tools` (or `exclude` in the client-side version) so its results are never cleared.

Claude's context editing can also warn the model when the context approaches the clearing threshold, if you give it the built-in memory tool, so it has a chance to save what matters first. Short- and Long-Term Memory covered where notes like these can live, and you'll combine them with compaction in the next project.

### Editing context and prompt caching

Prompt caching saves money by reusing an unchanged *prefix* of the conversation. Clearing or compacting changes earlier content, so everything after the change must be processed fresh at full price, plus a cache write. Clear rarely and in big chunks, not a little on every turn. That's what `clear_at_least` is for: if a clearing wouldn't free enough tokens to be worth breaking the cache, the API skips it. In your client-side version, a high trigger and a small `keep` have the same effect.

Two more caching habits help. Put a cache breakpoint at the end of the system prompt, so a compaction that rewrites the history doesn't also throw away the cached system prompt and tools. And keep the system prompt and tools identical across compactions; change them and nothing is reused.

### Test that compaction keeps critical facts

A compaction step can fail without any error. The run continues, and twenty steps later the agent emails the customer you told it not to email, because "do not email" didn't make it into the summary. You catch this the same way you catch any quality problem: with an eval.

The idea is simple. Take real transcripts, list the facts each one must preserve, compact, and check. Two checks catch different failures:

1. **Exact check.** Does the summary contain each fact's key string, such as the file path, the amount or the date? Cheap, strict and good for identifiers.
1. **Probe check.** Ask the model a question using only the compacted context, and check the answer. This catches facts that were kept but garbled.

Save this as `probe_compaction.py`. It reuses `rebuild_messages` from Agent Tracing and Debugging to turn a saved trace into a message list:

```python
# probe_compaction.py: did compaction keep the facts that matter?
import os
import sys

import anthropic

from agent import SYSTEM, TOOLS            # your traced agent from Agent Tracing and Debugging
from context_edit import compact
from debug import load, rebuild_messages

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

MUST_KEEP = {                              # fact -> (string the summary must contain, probe)
    "budget": ("$1,200", "What is the most we may spend?"),
    "no email": ("do not email", "Are we allowed to email the customer?"),
    "output file": ("reports/q3_final.md", "Which file must the report be saved to?"),
}


def probe(summary: str, question: str) -> str:
    response = client.messages.create(model=MODEL, max_tokens=2000, messages=[{
        "role": "user",
        "content": f"{summary}\n\nUsing only the notes above, answer in one sentence: {question}"}])
    return "".join(b.text for b in response.content if b.type == "text")


spans = load(sys.argv[1])
step = int(sys.argv[2])                    # compact the history as it was before this step
messages = rebuild_messages(spans, before_step=step)
compacted, summary = compact(client, MODEL, SYSTEM, TOOLS, messages, keep_steps=2)
if summary is None:
    sys.exit("No summary produced; try a later step.")

kept = 0
for fact, (needle, question) in MUST_KEEP.items():
    exact = needle.lower() in summary.lower()
    kept += exact
    print(f"{fact:<12} exact={'yes' if exact else 'NO '}  probe: {probe(summary, question)}")
print(f"{kept}/{len(MUST_KEEP)} facts kept word for word")
```

Run the agent once with a goal that states these facts, then run `uv run probe_compaction.py traces/run-....jsonl 6`. Read the probe answers yourself, or grade them with the LLM judge you built in Evals in Practice. One transcript proves little. Collect ten or twenty from real runs, compact each a few times (summaries vary from run to run), and report the share of facts kept with a confidence interval, as you learned in Eval Statistics. When a fact goes missing, fix the summary prompt or move that fact to memory, and rerun. Once you have this test, you can try a different summary prompt, a cheaper summarizing model or the server-side feature, and know whether it's safe.

### On other providers

The client-side techniques in this lesson work with any provider, because they only rewrite a list of messages. What changes is the message shape. In OpenAI's Chat Completions format, each tool result is its own message with `"role": "tool"` and a `tool_call_id`, so clearing is simpler: replace the content of all but the newest tool messages, as in the snippet below. The thinking-block warning is Claude-specific, but other providers that return reasoning have their own replay rules, so check them before editing history. Server-side features differ too. OpenAI's Responses API has [its own compaction](https://platform.openai.com/docs/guides/compaction), either automatic at a token threshold or through a separate compact endpoint, and it returns an encrypted compaction item you can't read. That means the exact-string check in `probe_compaction.py` can't inspect it; rely on the probe questions instead. Local open models served by [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) have no server-side compaction, so use `compact` and the clearing function from this lesson.

```python
# Clearing in the OpenAI Chat Completions message format
def clear_old_tool_messages(messages: list[dict], keep: int = 3) -> list[dict]:
    messages = list(messages)                                # don't mutate the caller's list
    tool_positions = [i for i, m in enumerate(messages) if m["role"] == "tool"]
    for i in tool_positions[:-keep] if keep else tool_positions:
        messages[i] = {**messages[i], "content": PLACEHOLDER}  # keeps tool_call_id
    return messages
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Reread the "Compaction" part of [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), paying attention to what it says a good summary should keep and what can safely be dropped.
1. Read the Claude [Compaction overview](https://platform.claude.com/docs/en/build-with-claude/compaction), including the table comparing compaction on demand, compaction at a token threshold and your own summarizer.
   - Then read "Continue from the summary" and "Write your own summarization prompt" in [Compaction on demand](https://platform.claude.com/docs/en/build-with-claude/compaction-on-demand).
1. Read the "Overview," "Server-side strategies" and "Context editing and prompt caching" sections of the Claude [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) docs.
1. Read the [context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) page to understand how the window fills up across turns, especially with tool use.
1. Practice: give the agent from Project: Agent Loop From Scratch a task that reads many large files. Log input tokens per turn and print them with `context_report.py`. Then add a simple client-side compaction step that triggers at a token threshold you choose, run the task again and compare the token totals and whether it still finished correctly.
   - Add clearing with `clear_old_tool_results` as a third setup, and compare all three.
1. Practice: run `probe_compaction.py` on at least five transcripts with facts of your own. Find one fact the default `SUMMARY_PROMPT` loses (try a long run, or compact twice), change the prompt to keep it, and show the before and after counts.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why is clearing old tool results safer than summarizing, and what should the placeholder say?](#clearing-old-tool-results)
- [Why must a compaction cut fall at a step boundary, and why is the goal pasted in word for word?](#compaction-summarize-and-continue)
- [Name four kinds of information a summary should keep exactly.](#what-to-keep-word-for-word)
- [When should an agent compact, and what should it try first?](#choosing-when-to-compact)
- [How does on-demand compaction on Claude differ from threshold compaction?](#server-side-options-on-claude)
- [Why should you clear context in large chunks rather than a little every turn?](#editing-context-and-prompt-caching)
- [How would you test that a compaction step doesn't lose critical facts?](#test-that-compaction-keeps-critical-facts)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Compaction at a token threshold](https://platform.claude.com/docs/en/build-with-claude/compaction-threshold) covers the automatic form, including pausing after compaction so you can re-insert recent turns.
- The [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) docs show how Claude's memory tool works alongside context editing, a preview of the next project.
