### Introduction

In the "Agent Loop From Scratch" project you wrote every piece of an agent yourself: the loop, the tool dispatch, the message history, the stop conditions and the trace. That was the right way to learn. But production agents need much more than that loop, such as file and shell tools, permission checks, context compaction, subagents and the ability to resume a session tomorrow. The Claude Agent SDK packages the harness that powers Claude Code as a Python (and TypeScript) library, so you get all of that without writing it again.

This lesson shows what the SDK does for you, which parts of your hand-built loop map onto it, and where you still have to make the decisions. You'll port a small agent to it, and you'll learn when not to use it at all. Everything here prepares you for "Port Your Agent", where you rebuild your from-scratch agent on frameworks and compare the results with numbers.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an agent harness is, and how the Claude Agent SDK relates to Claude Code.
- How the SDK's loop maps onto the loop you wrote by hand.
- Built-in tools versus custom tools you register yourself.
- Permission modes, allowed tools and hooks as control points.
- Sessions, context compaction and subagents provided out of the box.
- Porting a small from-scratch agent to the SDK.
- When the SDK is the wrong fit compared to calling the Messages API directly.

### What a harness is

The model only ever does one thing: it reads a list of messages and writes the next one. Everything else you built in the Tool Use section was the **harness**: the code around the model that runs tools, checks permissions, keeps the history, counts steps, decides when to stop and records what happened. A harness is to a model what a car is to an engine.

Claude Code, Anthropic's coding agent, is a very complete harness. It has tools for reading, writing and editing files, running shell commands, searching code and fetching web pages. It asks before risky actions, summarizes old context when the window fills up, can hand subtasks to helper agents and saves every session to disk. The **Claude Agent SDK** (the `claude-agent-sdk` package on PyPI) exposes that harness as a library. When you call its `query()` function, you're not making one API call. You're starting a whole agent run, which may make dozens of model calls and tool calls before it finishes.

Under the hood, the Python package bundles the Claude Code program and runs it as a separate process that your code talks to. That's why the first call takes a moment to start, and why errors sometimes mention the CLI (command-line interface).

Don't confuse it with two neighbors you met earlier. The **tool runner** in the regular `anthropic` package runs a loop over tools you define, and nothing more: no built-in tools, no files, no permissions. **Managed Agents** go one step further than the Agent SDK: Anthropic runs the loop *and* hosts the sandbox for you. The Agent SDK sits in the middle. You get Claude Code's full harness, and you still host and run it yourself.

At the time of writing (October 2026), the Python package is at version 0.2.x and changes often. Pin the version in your `pyproject.toml` (uv does this in `uv.lock` for you) and read the changelog before upgrading.

### Your loop is still inside

Nothing about the SDK is magic. Every piece of your from-scratch loop has a counterpart:

| Your hand-built loop | In the Agent SDK |
| --- | --- |
| `messages = [...]`, appending every turn | The session, saved to disk with an ID |
| `TOOLS` list plus `HANDLERS` dispatch dictionary | Built-in tools plus your own tools in `mcp_servers` |
| `for step in range(MAX_STEPS)` | `max_turns` (and `max_budget_usd` for a cost cap) |
| `if stop_reason == "end_turn": return` | A final `ResultMessage` with a `subtype` saying why it ended |
| `print(...)` of every step, or your JSONL tracer | The stream of messages, plus hooks |
| Your path check that refuses `../secret.txt` | Permission rules, permission modes and hooks |
| Nothing yet | Compaction, subagents, session resume |

The big change is the shape of your code. Instead of writing the loop, you **consume a stream**. `query()` is an async generator: you loop over it with `async for`, and it yields messages as the run happens. An `AssistantMessage` holds what the model wrote, including `TextBlock` and `ToolUseBlock` objects with the same fields you know (`name`, `input`, `id`). A `UserMessage` carries tool results back. A `SystemMessage` reports setup events. The last message is always a `ResultMessage`, with the final text, the number of turns, the session ID, token usage and an estimated cost in dollars.

This is why you learned the loop first: when an SDK agent misbehaves, you'll recognize every step in that stream.

### A first agent with built-in tools

Here is a read-only research agent that answers questions about a folder of notes. It uses three built-in tools: `Read` opens a file, `Glob` finds files by pattern and `Grep` searches file contents. Create a project with `uv init sdk-notes`, run `uv add claude-agent-sdk python-dotenv`, put `ANTHROPIC_API_KEY` in `.env`, make a `notes` folder with a few text files in it, and save this as `notes_agent.py`:

```python
import asyncio
import os

from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, ToolUseBlock, query,
)
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")

options = ClaudeAgentOptions(
    model=MODEL,
    cwd="notes",                              # the folder the agent works in
    tools=["Read", "Glob", "Grep"],           # the only built-in tools that exist for it
    allowed_tools=["Read", "Glob", "Grep"],   # ...and they run without asking
    permission_mode="dontAsk",                # anything else is denied, never prompted
    max_turns=15,                             # the step cap
    setting_sources=[],                       # ignore CLAUDE.md and settings on this machine
)


async def main() -> None:
    task = "Which of these notes mention a deadline? List each file and its date."
    async for message in query(prompt=task, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"  tool: {block.name} {block.input}")
                elif isinstance(block, TextBlock):
                    print("claude:", block.text)
        elif isinstance(message, ResultMessage):
            print(f"[{message.subtype}] turns={message.num_turns} "
                  f"cost=${message.total_cost_usd or 0:.4f}")


asyncio.run(main())
```

Run it with `uv run notes_agent.py`. You should see a few `Glob` and `Grep` calls, some `Read` calls, the answer, and a last line such as `[success] turns=6 cost=$0.0030`. The exact steps vary from run to run, just as they did with your own loop.

Notice how little of this is about the loop. Almost every line is a decision: which folder, which tools, which need approval, how many turns. The mechanics are done for you, so your code is mostly *policy*.

### Permissions: who says yes

The SDK separates two questions that are easy to mix up.

**Which tools exist?** The `tools` option sets the built-in tools the model can see. `["Read", "Glob", "Grep"]` means only those three; `[]` removes every built-in, so the model can only use your own tools. Listing a bare name in `disallowed_tools`, such as `"Bash"`, also removes it. A tool the model can't see is one it can't even try to call.

**Which calls run without asking?** `allowed_tools` lists tools that are pre-approved. It does *not* hide the other tools. A call to a tool that's available but not allowed goes through the **permission flow**, which depends on the `permission_mode`:

- `"default"` asks for approval, through a `can_use_tool` callback function you provide. With no callback, there's nobody to ask.
- `"dontAsk"` denies anything not pre-approved. This is the safest choice for scripts that run with nobody watching.
- `"acceptEdits"` auto-approves file edits inside the working folder.
- `"plan"` lets the model look around and propose a plan without changing anything.
- `"auto"` lets a separate classifier model approve or deny each call.
- `"bypassPermissions"` approves everything. Only use it inside a throwaway sandbox, such as a container, never on your own laptop.

The SDK's design idea is "give the agent a computer": agents do best with the same tools a person uses at a terminal. The price is that you must constrain that computer. Start every agent with the narrowest `tools` list that does the job and `dontAsk`, and widen it only when a task needs more. You'll go much deeper in Sandboxing Agents and Approvals and Permissions later in this path.

### Hooks are your control points

In The Agent Loop you learned that every pass through the loop goes through code you control, so you can log, check, ask a human or count. Hooks give those control points back to you when the loop isn't yours anymore. A **hook** is a function the SDK calls at a named moment in the run:

- `PreToolUse` runs before a tool call. It can allow, deny or rewrite the call.
- `PostToolUse` runs after a tool call. It can log the result or add context for the model.
- `Stop`, `SubagentStop` and `PreCompact` run when the agent stops, when a helper agent finishes and just before old context is summarized.

You register hooks with `HookMatcher` objects. A matcher is a tool-name pattern such as `"Write|Edit"`, or nothing at all to match every tool. Each hook is an async function that receives a dictionary describing the event (`tool_name`, `tool_input` and so on), the tool call's ID and a reserved context argument. Returning `{}` means "no objection." To block a call, return a decision with a reason, and the reason goes back to the model as the tool result, exactly like an instructive error from Tool Errors and Parallel Calls. If several hooks disagree, "deny" wins.

Hooks run in your process, in ordinary Python, so they're the right place for anything that must happen every time: writing a trace line, refusing paths outside a folder, or asking a person before an action that can't be undone. A rule in the system prompt is a request. A hook is enforcement.

### Porting a small agent

Now port an agent you could have written in the Tool Use section. It has two tools, a calculator and a note writer, and a person must approve every note before it's saved. Following the advice in "Port Your Agent", the project at the end of this section, the tools are plain functions in their own file, with no framework imports, so every version of the agent can share them. Save this as `tools.py`:

```python
"""Plain tool functions, shared by every version of the agent. No framework imports."""
import operator
from pathlib import Path

WORKSPACE = Path("workspace")
OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}


def calculate(a: float, op: str, b: float) -> str:
    """Apply one arithmetic operation (+, -, *, /) to two numbers."""
    if op not in OPS:
        return f"Error: unknown operator {op!r}. Use one of + - * /."
    if op == "/" and b == 0:
        return "Error: division by zero. Check the numbers and try again."
    return str(OPS[op](a, b))


def save_note(filename: str, text: str) -> str:
    """Save text to a Markdown note in the workspace folder, replacing any old version."""
    path = WORKSPACE / filename
    if path.parent != WORKSPACE or path.suffix != ".md":
        return "Error: pass a bare file name ending in .md, such as 'answer.md'."
    WORKSPACE.mkdir(exist_ok=True)
    path.write_text(text)
    return f"Saved {len(text)} characters to {path}."
```

Then save this as `sdk_agent.py` in the same folder:

```python
import asyncio
import os

from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, HookMatcher, ResultMessage,
    TextBlock, create_sdk_mcp_server, query, tool,
)
from dotenv import load_dotenv

import tools as plain  # the same framework-free functions as the raw loop

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")


def as_result(text: str) -> dict:  # (1) wrap a plain string in the MCP result shape
    return {"content": [{"type": "text", "text": text}], "is_error": text.startswith("Error")}


@tool("calculate", "Apply one arithmetic operation (+, -, *, /) to two numbers. "
      "Use it for all math.", {"a": float, "op": str, "b": float})
async def calculate(args: dict) -> dict:
    return as_result(plain.calculate(args["a"], args["op"], args["b"]))


@tool("save_note", "Save text to a Markdown note in the workspace. "
      "Pass a bare name like 'answer.md'.", {"filename": str, "text": str})
async def save_note(args: dict) -> dict:
    return as_result(plain.save_note(args["filename"], args["text"]))


async def log_call(input_data, tool_use_id, context):  # (2) runs before EVERY tool call
    print(f"  -> {input_data['tool_name']} {input_data['tool_input']}")
    return {}  # an empty dict means "no objection"


async def ask_before_saving(input_data, tool_use_id, context):  # (3) a human approval gate
    name = input_data["tool_input"].get("filename")
    reply = await asyncio.to_thread(input, f"Save {name}? [yes/no] ")
    if reply.strip().lower() == "yes":
        return {}
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "The user declined. Give them the answer in chat instead.",
    }}


options = ClaudeAgentOptions(
    model=MODEL,
    system_prompt="You are a careful assistant. Use the calculate tool for all arithmetic.",
    tools=[],  # (4) no built-in tools at all: no Bash, Read, Write or WebFetch
    mcp_servers={"mimir": create_sdk_mcp_server(name="mimir", tools=[calculate, save_note])},
    allowed_tools=["mcp__mimir__calculate", "mcp__mimir__save_note"],  # (5) prefixed names
    permission_mode="dontAsk",
    hooks={"PreToolUse": [
        HookMatcher(hooks=[log_call]),  # no matcher: every tool
        HookMatcher(matcher="mcp__mimir__save_note", hooks=[ask_before_saving]),
    ]},
    max_turns=10,  # (6) the step cap you wrote by hand, now one option
    setting_sources=[],
)


async def main(task: str) -> None:
    try:
        async for message in query(prompt=task, options=options):  # (7) a stream
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print("claude:", block.text)
            elif isinstance(message, ResultMessage):  # (8) always last
                print(f"[{message.subtype}] turns={message.num_turns} "
                      f"cost=${message.total_cost_usd or 0:.4f} session={message.session_id}")
    except Exception as error:  # query() raises after an error result, such as max turns
        print("run failed:", error)


asyncio.run(main("What is 17.5% of 2,340? Save the answer to answer.md."))
```

Walk through the numbered comments:

1. **Custom tools are MCP tools.** The `@tool` decorator takes a name, a description and a schema (here a simple dictionary of types, which the SDK turns into JSON Schema). The handler receives the arguments as a dictionary and returns an MCP tool result: a `content` list plus `is_error`. You built exactly this shape in the MCP section. The difference is that `create_sdk_mcp_server` runs the server *inside your Python process*, so there's no separate program or transport to manage.
1. **A hook with no matcher** fires for every tool call. This one is a one-line trace. Swap the `print` for your JSONL tracer from Agent Tracing and Debugging and every port of your agent produces comparable traces.
1. **The approval gate** only matches `save_note`. It asks in the terminal (in a thread, so it doesn't freeze the async event loop) and denies with a reason the model can act on.
1. **`tools=[]`** removes every built-in tool, so this agent has the same abilities as your raw version and nothing more. That's what makes a comparison fair.
1. **MCP tool names get a prefix**: `mcp__<server key>__<tool name>`. Use the prefixed name in `allowed_tools`, `disallowed_tools` and hook matchers. A misspelled name here is the most common reason a custom tool "doesn't work."
1. **`max_turns`** replaces your `range(MAX_STEPS)`. Add `max_budget_usd` for a dollar cap.
1. **The stream** gives you every assistant message as it happens.
1. **The `ResultMessage`** tells you why the run ended. Its `subtype` is `"success"`, or an error such as `"error_max_turns"` or `"error_max_budget_usd"`. With a single `query()` call, the SDK yields that result and then raises an exception, which is why the loop sits inside `try`.

Count the lines. The tool definitions and the approval gate take about as many lines as in your raw loop, because they're decisions only you can make. What disappeared is the loop, the dispatch dictionary, the result matching by ID and the step-cap bookkeeping. With two tools that's a modest saving. The real gain shows up when you need what you'd otherwise build next: sessions, compaction and helper agents.

### Sessions, compaction and subagents

**Sessions.** Every run is saved as a session, and the `ResultMessage` carries its `session_id`. Pass `resume=session_id` in the options of a later `query()` call and the agent continues with the whole history, even after your program restarts. For a back-and-forth chat inside one program, `ClaudeSDKClient` keeps a session open: you `await client.query(...)` repeatedly and read each answer with `client.receive_response()`. In your from-scratch agent, this was the `messages` list you saved to a file in "The Agent That Remembers."

**Compaction.** When the history nears the context window, the harness summarizes older turns automatically, as you did by hand in Compaction and Context Editing. That keeps long tasks running, but it isn't free. Summarizing costs tokens, and details can be lost. When a long run makes a strange mistake late on, ask whether the fact it needed was summarized away. A `PreCompact` hook can save the full transcript first, so you can check.

**Subagents.** You can define helper agents with `agents={"reviewer": AgentDefinition(description=..., prompt=..., tools=[...])}`. The main agent hands a subtask to one through a built-in tool, and the helper works in its *own* fresh context and returns only its summary. That protects the main context from pages of search results. The cost is more model calls in total, and the main agent sees only the summary, not the helper's reasoning. Note that `AgentDefinition` fields use camelCase names, such as `maxTurns`, unlike the rest of the Python API. You'll design multi-agent systems properly in Subagents and Orchestration.

All three save you real work, and all three make runs harder to reason about, because more is happening than you wrote.

### When not to use it

Reach for the raw Messages API, or the tool runner, when:

- **The job is small and fixed.** A single call, a classifier or a three-step workflow doesn't need a harness. Remember Building Effective Agents: many problems need a workflow, not an agent.
- **You need a model from another provider.** The Agent SDK runs Claude models only (through Anthropic's API or a cloud platform such as Amazon Bedrock, Google Vertex AI or Microsoft Foundry). If your product must switch providers, or run an open model, use a provider-neutral framework or your own loop.
- **You need exact control of every request.** The harness writes its own system prompt (unless you replace it), loads tools on demand and compacts history when it decides to. If you must see and shape the exact bytes of each request, for example to keep a prompt cache stable or for an audit, your own loop is clearer.
- **The agent doesn't need a computer.** If none of the built-in tools apply and you'd turn them all off, you're carrying a bundled CLI and a subprocess for features you don't use.
- **You're shipping a product to other people.** Anthropic doesn't let third-party apps sign users in with their Claude.ai accounts; your app must use its own API key. Also check the branding rules on the overview page.

The SDK shines when the agent works with files, code or shells, runs for a long time, or needs approvals and resumable sessions.

### On other providers

The Claude Agent SDK is Claude-specific: it only runs Claude models, so nothing in this lesson's code runs against OpenAI or an open model. What carries over is the *shape*. OpenAI's [Agents SDK](https://openai.github.io/openai-agents-python/) has the same parts under different names: an `Agent` with instructions and tools, a `Runner` that runs the loop with a `max_turns` limit, guardrails that check inputs and outputs, and sessions. It has no built-in file or shell harness like Claude Code's, but it isn't tied to OpenAI: it can [run other providers' models](https://openai.github.io/openai-agents-python/models/), including open models. For the plain tool-calling round trip underneath, see OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling). For a local open model, [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) works with any framework that can talk to an OpenAI-style endpoint. The next lesson, LangGraph and the Wider Ecosystem, builds this same agent in a provider-neutral framework, and "Port Your Agent" asks you to run it on an open model too, with a second hosted provider as extra credit.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) to see what the SDK includes and how it compares with the CLI, the client SDK and Managed Agents.
   - Note which capabilities (tools, permissions, sessions, subagents, hooks, MCP) map to code you wrote by hand in "Agent Loop From Scratch".
1. Read [How the agent loop works](https://code.claude.com/docs/en/agent-sdk/agent-loop) and Anthropic's article [Building agents with the Claude Agent SDK](https://claude.com/resources/articles/building-agents-with-the-claude-agent-sdk) for the design reasoning behind the SDK.
   - In the article, focus on the "gather context, take action, verify work" loop. You'll see it again in coding agents and evals.
1. Work through the [Agent SDK quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart) and build its small agent.
   - Install the SDK with `uv add claude-agent-sdk` in a new project and read your key from `ANTHROPIC_API_KEY`. Use the [cheap model](#/models) through the `model` option.
   - Print every message in the stream so you can see each tool call and the final cost.
1. Read the [permissions guide](https://code.claude.com/docs/en/agent-sdk/permissions) and the [hooks guide](https://code.claude.com/docs/en/agent-sdk/hooks), and keep the [Python SDK reference](https://code.claude.com/docs/en/agent-sdk/python) open as you work.
   - Restrict your quickstart agent to read-only tools, then ask it to edit a file. Write down what happens with `dontAsk`, then with `default` and no callback.
1. Practice: build the ported agent from this lesson (`tools.py` plus `sdk_agent.py`), then change it.
   - Answer "no" at the approval prompt and check that the agent gives you the answer in chat instead.
   - Set `max_turns=1` and note the `subtype` of the result and the exception.
   - Print the `session_id`, then start a second run with `resume=` set to it and ask "What did you calculate last time?"
   - Port one more tool from your "Agent Loop From Scratch" project into `tools.py` and the SDK, and compare how many lines each version takes.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is an agent harness, and how does the Claude Agent SDK relate to Claude Code?](#what-a-harness-is)
- [Which parts of your hand-written loop does a call to query() replace, and how do you read what happened?](#your-loop-is-still-inside)
- [What is the difference between the tools option, allowed_tools and the permission mode?](#permissions-who-says-yes)
- [When does a PreToolUse hook run, and how does it block a call?](#hooks-are-your-control-points)
- [How do your own tools get into an SDK agent, and what names do they end up with?](#porting-a-small-agent)
- [What do sessions, compaction and subagents give you, and what do they cost?](#sessions-compaction-and-subagents)
- [Name three situations where the raw Messages API is a better choice than the Agent SDK.](#when-not-to-use-it)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Building effective agents](https://www.anthropic.com/research/building-effective-agents) is a reminder that many problems need a workflow, not a full harness.
- The SDK guides to [custom tools](https://code.claude.com/docs/en/agent-sdk/custom-tools), [sessions](https://code.claude.com/docs/en/agent-sdk/sessions) and [subagents](https://code.claude.com/docs/en/agent-sdk/subagents) go deeper on each feature this lesson introduced, including tool annotations and forking a session.
- The [claude-agent-sdk-python repository](https://github.com/anthropics/claude-agent-sdk-python) has the changelog and runnable examples. Read the changelog before you upgrade, because the API is still moving.
