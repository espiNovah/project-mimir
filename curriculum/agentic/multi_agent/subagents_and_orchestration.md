### Introduction

A **multi-agent system** splits work between several model instances, each with its own instructions, tools and context window. The most common shape is an orchestrator: a lead agent that breaks a task into parts and hands each one to a **subagent**. Subagents work in parallel and send back short summaries. Done well, this lets a system cover more ground than one context window can hold. Done badly, it multiplies cost and creates agents that work from different, conflicting assumptions.

You've already seen the workflow version of this. In Parallelization and Orchestrator-Workers, an orchestrator call planned subtasks once, your code ran the workers, and a synthesizer combined the results. This lesson takes the next step that lesson pointed to: the lead is a full agent that can delegate, read the results and delegate again, and each worker is a full agent with its own tools and loop. You'll also meet two other ways agents work together: **handoffs**, where one agent passes the whole conversation to another, and **A2A**, a protocol for agents built by different teams to talk over a network. Practitioners disagree in public about when any of this is worth it, and you'll read both sides.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How orchestrator-workers changes when the workers are agents.
- Why subagents help: separate context windows and parallel work.
- Why they hurt: lost context, conflicting decisions and token cost.
- Writing good delegation instructions, and what a subagent should send back.
- Handoffs: passing control instead of delegating a task.
- The A2A protocol for agents that run as separate services.
- Subagents in frameworks, and how to evaluate a multi-agent system.

### From workers to subagents

In the workflow from Parallelization and Orchestrator-Workers, each worker was a single model call. It received one file and one instruction, answered, and was done. A **subagent** is a worker that runs its own agent loop. It gets a task description, a system prompt and a set of tools, and it keeps calling tools until it has an answer. Then it returns that answer to the agent that started it, which is usually called the **lead** or **orchestrator**.

To the lead, a subagent looks like just another tool. The lead calls something like `delegate(objective="...")`, waits, and gets back a tool result. What happens inside (ten searches, five page reads, three dead ends) stays inside. That is the whole trick, and it's why subagents exist:

- **A subagent is a fresh context window.** It starts with only its system prompt, its tools and the task the lead wrote. It can read 50,000 tokens of pages and return 300 tokens of findings. The lead's context stays small and focused, which matters because, as you saw in Context Engineering for Agents, long contexts make models worse as well as more expensive.
- **Subagents can run in parallel.** When the lead delegates three independent questions in one turn, your code can run all three at once with `asyncio.gather` and a semaphore, exactly as in the workflow lesson. Wall-clock time is close to the slowest subagent, not the sum.
- **Subagents can be specialized.** Each can have a narrow system prompt, only the tools it needs and even a cheaper model. Agent Cost and Latency suggested switching models at exactly this kind of boundary.

### The cost of many agents

Multi-agent is a way to spend more tokens usefully, not a way to save them. Every subagent re-sends its own growing context on every step, and the lead pays again to read all the results. Anthropic's write-up of its multi-agent research system reported that agents use about four times the tokens of a chat, and multi-agent systems about fifteen times. On one browsing benchmark, token use alone explained 80 percent of the variation in performance. The system beat a single agent on broad research questions, but it was buying that quality with tokens.

The deeper problem is **lost context**. The lead knows the whole task: what the user really wants, what's already been tried, which sources are trustworthy. Each subagent knows only the few sentences the lead wrote. When subagents only *gather* information, that's fine: a missing detail means a less useful finding, which the lead can notice and correct. When subagents *make decisions*, it goes wrong. Ask three agents to each write a section of one document, or edit different files of one feature, and each will make reasonable assumptions the others can't see. One names the field `phone`, another `phone_number`; one writes in a formal tone, another casually. Nobody notices until the parts are put together.

This is the core of Cognition's essay "Don't Build Multi-Agents": actions carry implicit decisions, and agents that can't see each other's decisions will conflict. Their advice is a single thread with full context for anything that writes. Anthropic's research system and Cognition's coding agent look like they disagree, but they're built for different tasks. Research is **read-heavy** and splits into independent questions. Coding is **write-heavy**, and every edit depends on the others. A useful rule follows: keep subagents **read-only**, or give them tasks that truly don't overlap, and let one agent make the decisions.

### Writing the delegation

Delegation is a prompt-writing job. The lead writes the subagent's entire task, and the subagent has nothing else to go on. Anthropic found that early versions of their lead wrote instructions like "research the semiconductor shortage," and the subagents misread the task or ran the exact same searches as each other. A good delegation says:

- **The objective,** specific enough that two subagents wouldn't overlap: "Find SQLite's limits on concurrent writers," not "research SQLite."
- **The output format:** "at most 150 words, as bullet facts, each with its source."
- **Which tools and sources to use,** and which to prefer.
- **The boundaries:** what's out of scope, and what another subagent is already covering.
- **A budget:** how many tool calls, or when to stop and report what it has.

You put these rules in two places. The **lead's** system prompt tells it how to write delegations and how many to make. The **subagent's** system prompt tells it how to behave and what to return, so the format holds even when the lead forgets to ask.

The same prompt is where you **scale effort to the task**. Without a rule, a lead will happily start five subagents to answer "what year was Python released?" Anthropic's lead prompt includes explicit guidance: one agent and a few tool calls for simple fact-finding, a handful of subagents for comparisons, more only for clearly broad research. Write a rule like that into your orchestrator.

### What a subagent sends back

The subagent's answer becomes a tool result in the lead's context, so design it like any tool result from Designing Tools for Agents: return what the lead needs, not everything you found.

- **Condensed, structured findings.** Key facts with their sources, not page dumps. A short list of `fact [source]` lines is easy for the lead to merge and cite.
- **What's missing.** "The library had nothing on DuckDB's write locking" is as useful as a finding, because it tells the lead what to try next.
- **A pointer for big outputs.** If a subagent produces something large, such as a dataset, a draft or a long log, have it write the result to a file or database and return the path plus a summary. The lead reads the file only if it needs to. This also keeps the content intact; a summary of a summary loses detail at each step.

Then **cap it in code**. Even with a clear instruction, a subagent will sometimes return 2,000 words. Truncating at a limit, with a note saying so, protects the lead's context the same way the size cap in your tools does.

### An orchestrator with subagents

Here is a small, complete system. The lead has one tool, `delegate`. Each subagent has two read-only tools, `search` and `read`, over a tiny in-memory library, so the example runs without web access. When the lead delegates several objectives in one turn, they run in parallel. A shared token budget covers every agent, which is what the next project asks you to build. Set up a project with `uv init orchestra` and `uv add anthropic python-dotenv`, then save this as `orchestra.py`:

```python
# orchestra.py  (run with: uv run orchestra.py)
import asyncio
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.AsyncAnthropic(max_retries=4)
LIMIT = asyncio.Semaphore(3)      # at most 3 model calls in flight
BUDGET = {"tokens": 0, "max": 200_000, "subagents": 0, "max_subagents": 4}

LIBRARY = {  # a stand-in for the web, so this runs offline
    "sqlite.md": "SQLite is a file-based database. It allows many readers but only one writer at a time.",
    "postgres.md": "Postgres is a client-server database with many concurrent writers and rich SQL.",
    "duckdb.md": "DuckDB is an in-process database built for analytics: fast scans and aggregations.",
}


def tool(name: str, description: str, **props: str) -> dict:
    return {"name": name, "description": description, "input_schema": {"type": "object",
            "properties": {p: {"type": "string", "description": d} for p, d in props.items()},
            "required": list(props)}}


SUB_TOOLS = [tool("search", "Find documents mentioning any of the words.", query="search words"),
             tool("read", "Read one document by name.", doc="document name from search")]
LEAD_TOOLS = [tool("delegate", "Give one research objective to a read-only subagent. Call it several "
                   "times in one turn to run subagents in parallel.",
                   objective="what to find, what to return, and what is out of scope")]
SUB_SYSTEM = ("You are a research subagent with read-only tools. Return at most 150 words: bullet facts, "
              "each ending with its source like [sqlite.md], then one line on what you could not find.")
LEAD_SYSTEM = ("You lead research. Delegate one objective for a narrow question; for a broad one, delegate "
               "up to 3 non-overlapping objectives in the same turn. Then answer, citing only sources "
               "your subagents returned.")


async def search(query: str) -> str:
    words = query.lower().split()
    return ", ".join(n for n, t in LIBRARY.items() if any(w in t.lower() for w in words)) or "no matches"


async def read(doc: str) -> str:
    return LIBRARY.get(doc, f"error: no document named {doc!r}")


async def delegate(objective: str) -> str:
    if BUDGET["subagents"] >= BUDGET["max_subagents"]:  # (1) hard cap on fan-out
        return "error: subagent limit reached; answer with what you have"
    BUDGET["subagents"] += 1
    answer = await run_agent(SUB_SYSTEM, objective, SUB_TOOLS, {"search": search, "read": read}, steps=6)
    words = answer.split()  # (2) cap what comes back, and say so
    return " ".join(words[:200]) + (" [truncated]" if len(words) > 200 else "")


async def run_agent(system: str, task: str, tools: list, handlers: dict, steps: int) -> str:
    messages = [{"role": "user", "content": task}]
    for _ in range(steps):
        if BUDGET["tokens"] > BUDGET["max"]:  # (3) one budget shared by every agent
            return "stopped: token budget used up"
        async with LIMIT:
            response = await client.messages.create(model=MODEL, max_tokens=4000, system=system,
                                                    tools=tools, messages=messages)
        BUDGET["tokens"] += response.usage.input_tokens + response.usage.output_tokens
        messages.append({"role": "assistant", "content": response.content})
        calls = [b for b in response.content if b.type == "tool_use"]
        if not calls:
            return "".join(b.text for b in response.content if b.type == "text")
        outputs = await asyncio.gather(*(handlers[c.name](**c.input) for c in calls),
                                       return_exceptions=True)  # (4) parallel delegations
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": c.id, "content": str(o),
             "is_error": isinstance(o, Exception)} for c, o in zip(calls, outputs)]})
    return "stopped: step budget used up"


async def main() -> None:
    question = "Which database should a small analytics app use, and why? Compare SQLite, Postgres and DuckDB."
    print(await run_agent(LEAD_SYSTEM, question, LEAD_TOOLS, {"delegate": delegate}, steps=4))
    print(f"\nsubagents: {BUDGET['subagents']}, total tokens: {BUDGET['tokens']:,}")


asyncio.run(main())
```

Four things to notice:

1. **A hard cap on subagents,** enforced in the tool, not the prompt. A confused lead can't start fifty agents.
1. **A cap on what comes back.** The subagent's prompt asks for 150 words; the code enforces 200.
1. **One shared budget.** Every model call, lead or subagent, counts against the same total. Without this, each agent respects its own budget while the system as a whole overspends.
1. **Parallelism for free.** The lead's parallel tool calls become concurrent subagents through the same `gather` you used for tool calls. The semaphore keeps the whole system under your rate limits.

`run_agent` is the same function for the lead and the subagents. That's the point: a multi-agent system is ordinary agents, wired together with a tool. Change the question to "What is SQLite?" and check that the lead starts one subagent, not three. Then, to see the cost, write a single agent with `search` and `read` and compare its token count on both questions.

### Handoffs

Delegation is like a manager asking a colleague to look something up: the manager stays in charge and gets an answer back. A **handoff** is like a receptionist transferring your call. The first agent passes the *whole conversation* to another agent, and the new agent talks to the user directly. Control doesn't come back unless the new agent hands off again.

Handoffs fit conversations that move between specialties: a support assistant where a triage agent routes you to billing or technical support, each with its own instructions and tools. You built the workflow version of this in Chaining and Routing, where a classifier picked a handler once. A handoff lets *any* agent reroute at *any* point in the conversation. The OpenAI Agents SDK made the pattern popular, but it needs no framework. An agent is just a system prompt plus tools, and a handoff is a tool call that tells your code to switch which one is active:

```python
# handoff.py  (run with: uv run handoff.py)
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

AGENTS = {
    "triage": "Work out what the user needs and transfer them. Never answer the question yourself.",
    "billing": "You handle refunds, invoices and charges. Transfer anything else.",
    "tech": "You handle bugs, errors and setup problems. Transfer anything else.",
}
TRANSFER = {"name": "transfer", "description": "Hand the whole conversation to another agent, who will reply "
            "to the user directly. Use when the request is outside your job.",
            "input_schema": {"type": "object", "required": ["agent", "note"], "properties": {
                "agent": {"type": "string", "enum": list(AGENTS)},
                "note": {"type": "string", "description": "One sentence for the next agent: what the user "
                                                           "needs and what you already know"}}}}


def converse(text: str, active: str = "triage", max_hops: int = 3) -> str:
    messages = [{"role": "user", "content": text}]
    for _ in range(max_hops + 1):
        response = client.messages.create(
            model=MODEL, max_tokens=2000, system=AGENTS[active], tools=[TRANSFER], messages=messages,
            tool_choice={"type": "auto", "disable_parallel_tool_use": True})  # one transfer at a time
        messages.append({"role": "assistant", "content": response.content})
        call = next((b for b in response.content if b.type == "tool_use"), None)
        if call is None:  # no transfer: this agent answered the user
            return f"[{active}] " + "".join(b.text for b in response.content if b.type == "text")
        print(f"handoff {active} -> {call.input['agent']}: {call.input['note']}")
        active = call.input["agent"]
        messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": call.id,
                         "content": f"Transferred. You are now the {active} agent."}]})
    return "Too many transfers; a human will take over."  # stops agents passing the user in circles


print(converse("I was charged twice for my subscription this month."))
```

Every agent gets the same `transfer` tool, so any of them can pass the user on, and the conversation history travels with them. The `note` field is the handoff's version of a delegation: a one-sentence briefing so the next agent doesn't make the user repeat themselves. The hop limit is the step budget of a handoff system, and it catches the classic failure where two agents keep transferring a user back and forth.

Choose by asking who should talk to the user next. If the lead should keep the conversation and just needs information, delegate (agents as tools). If a specialist should take over, hand off.

### Agents across services with A2A

Everything so far runs inside one program. Sometimes the agents belong to different teams or companies: your travel assistant wants to ask an airline's booking agent for options, and you can't see or change the airline's code. The **Agent2Agent (A2A) protocol** is an open standard for this case. Google introduced it in 2025 and later gave it to the Linux Foundation, and many vendors have signed on.

A2A complements MCP rather than replacing it. MCP connects an agent to *tools and data*: the client sees each tool's schema and calls it directly. A2A connects an agent to *another agent* that stays **opaque**: you don't see its tools, prompts or memory, only what it's willing to do. The main pieces:

- **An Agent Card,** a JSON file the remote agent publishes at a well-known URL, describing its name, what skills it offers, where to reach it and how to authenticate. It's how one agent discovers what another can do.
- **Tasks,** the unit of work. A client agent sends a message that starts a task, and the task moves through states such as working, input-required, completed or failed. Long tasks can stream updates or send a notification when they're done, so the client doesn't have to wait on an open connection.
- **Messages and artifacts.** Agents exchange messages made of parts (text, files, structured data), and the remote agent returns its results as artifacts.

Under the hood it runs over HTTP, so everything you learned about APIs, auth and timeouts in the Backend section applies. And the security lesson from MCP applies twice over: a remote agent's output is untrusted input, just like a web page. Reach for A2A when you genuinely need to call an agent you don't control. Inside your own system, a function call or a subagent is simpler, faster and easier to debug.

### Subagents in frameworks

You don't have to build all of this by hand, though building it once teaches you what the frameworks do. The Claude Agent SDK, which you used in the Frameworks section, lets you define subagents with their own prompt, tools and model; the main agent calls them through a built-in tool, and only their final message returns. Claude Code uses the same mechanism to keep wide codebase searches out of its main context. The OpenAI Agents SDK offers both patterns by name: agents as tools for delegation, and handoffs for transfers. LangGraph models multi-agent systems as a graph whose nodes are agents. Whatever you use, check three things in its docs: how a subagent's tools are restricted, what exactly returns to the parent and whether the parent's budget includes the children's tokens.

### Evaluating the whole system

A multi-agent system has more parts to go wrong and more tokens to pay for, so it has to prove itself. Evaluate it the way you learned in Agent Eval Fundamentals, with one addition: **always compare against a single-agent baseline** on the same tasks with the same tools. Measure:

- final quality, scored with the same rubric or judge for both;
- total tokens and cost across *all* agents;
- wall-clock time;
- how often a budget was hit.

Break the results down by task type. You'll usually find multi-agent helps on broad, parallel questions and adds nothing (except cost) on narrow ones. Without the baseline, you can't tell whether the extra agents helped at all. Your traces need care too: give each subagent's spans a parent, as Agent Tracing and Debugging described, so you can see which delegation produced which finding. The next project, Research Agent, One vs Many, is exactly this comparison.

### On other providers

Nothing in this lesson depends on one provider. `orchestra.py` and `handoff.py` are ordinary tool calling, so they port to any provider with tools: on OpenAI's Chat Completions API you wrap each schema as `{"type": "function", "function": {...}}`, read calls from `message.tool_calls` (arguments arrive as a JSON string), return results as `role: "tool"` messages, and control parallel calls with `parallel_tool_calls`. Mixing providers is common in multi-agent systems, for example a capable model as the lead and a cheap or open model for read-only subagents; keep the delegation format plain text and the budget counting in your own code, and that works. The [OpenAI Agents SDK's multi-agent guide](https://openai.github.io/openai-agents-python/multi_agent/) describes the same two patterns as agents-as-tools and [handoffs](https://openai.github.io/openai-agents-python/handoffs/), and it can run other providers' models through adapters. Small local models via [Ollama's tool calling](https://docs.ollama.com/capabilities/tool-calling) can serve as subagents for simple lookups, but test them on your eval first; a subagent that returns confident nonsense poisons the lead. A2A is provider-neutral by design.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).
   - Focus on the prompting principles for the lead agent, the token cost discussion and the evaluation section. Compare their delegation advice with the checklist in this lesson.
1. Read Cognition's [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents), then their follow-up [Multi-Agents: What's Actually Working](https://cognition.com/blog/multi-agents-working).
   - Write a paragraph on where the two companies actually disagree and where they agree once you account for the kinds of tasks they build for.
1. Read the [Claude Agent SDK subagents guide](https://code.claude.com/docs/en/agent-sdk/subagents) and the [OpenAI Agents SDK handoffs page](https://openai.github.io/openai-agents-python/handoffs/).
   - Note how a subagent's tools are restricted and how its result returns to the parent, and how a handoff differs from both.
1. Read the overview pages of the [A2A protocol docs](https://a2a-protocol.org/latest/), up to the key concepts. Note what an Agent Card contains and how A2A's role differs from MCP's.
1. Practice: extend `orchestra.py` and measure it.
   - Add a fourth document to the library and three questions of your own, one narrow and two broad. Log, per question, how many subagents the lead started, the total tokens and the time.
   - Write a single-agent version that has `search` and `read` directly, run it on the same questions and put both sets of numbers in a table.
   - Change the lead's prompt so it skips delegation entirely for narrow questions, and check that the token count on the narrow question drops.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How does a subagent differ from a worker in the orchestrator-workers workflow, and why does its separate context help?](#from-workers-to-subagents)
- [Why do parallel subagents work well for research but conflict when they write code or documents?](#the-cost-of-many-agents)
- [What five things should a good delegation include, and where do you put the rule for scaling effort?](#writing-the-delegation)
- [What should a subagent send back, and what should it do with a large output?](#what-a-subagent-sends-back)
- [Why should the token budget be shared across all agents instead of set per agent?](#an-orchestrator-with-subagents)
- [How does a handoff differ from delegation, and when would you choose each?](#handoffs)
- [What problem does A2A solve that MCP doesn't, and what is an Agent Card?](#agents-across-services-with-a2a)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) shows how a coding agent uses subagents to keep its main context clean.
- The [A2A specification on GitHub](https://github.com/a2aproject/A2A) has the full protocol, sample agents and SDKs in several languages, if you need to build or call an A2A agent.
