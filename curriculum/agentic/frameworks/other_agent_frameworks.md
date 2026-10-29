### Introduction

The Claude Agent SDK is one of many ways to build agents. Job listings and open-source projects also use LangGraph, the OpenAI Agents SDK, Pydantic AI, Google's Agent Development Kit (ADK), CrewAI and Microsoft Agent Framework. Each makes different choices about how much it hides, how you describe control flow and which model providers it supports.

You don't need to master all of them. This lesson teaches one in depth, **LangGraph**, because it's provider-neutral, widely used in production, and makes the agent loop *more* visible rather than less. Then it gives you a fair, dated map of the rest, so you can read any of them and pick one on purpose. You'll build the same small agent you ported to the Claude Agent SDK, this time as a graph, and you'll reuse it in "Port Your Agent".

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The shared core every agent framework implements.
- LangGraph's building blocks: state, nodes, edges and reducers.
- Building a tool-using agent as a graph, and testing it without a model.
- Checkpointers, threads and resuming a run.
- Human-in-the-loop approval with interrupts.
- The wider ecosystem, and which frameworks lock you to one provider.
- How to compare frameworks without being swayed by marketing.

### Every framework wraps the same loop

Under the branding, every agent framework does the three things your from-scratch loop did. It **sends** the history and tool definitions to a model. It **runs** the tools the model asks for and adds the results to the history. It **repeats** until a stop condition: the model answers without a tool call, or a limit is hit. If you can find where a framework does those three things, you can debug it.

What frameworks add on top falls into a few buckets: turning Python functions into tool schemas, adapters for many model providers, saving and resuming state, pausing for a human, tracing, and patterns for several agents working together. What differs between them is mostly *how you describe control flow*. Some give you one agent object and run the loop for you. Some let agents hand a conversation to each other. LangGraph makes you draw the loop yourself, as a graph.

### LangGraph in one picture

LangGraph is an open-source library (MIT license) from the company behind LangChain. It describes an agent as a **state graph**, which has three parts:

- **State** is a shared data object that flows through the graph, usually a `TypedDict`. For a chat agent, the state is mainly a list of messages, exactly like your `messages` list.
- **Nodes** are ordinary Python functions. Each one receives the current state and returns an *update*: a dictionary with only the keys it wants to change.
- **Edges** say which node runs next. A normal edge always goes from A to B. A **conditional edge** calls a small function that looks at the state and picks the next node, for example "if the last message asked for tools, go to the tools node, otherwise finish."

How does an update get merged into the state? Each key can have a **reducer**, a function that combines the old value with the new one. Without one, the new value replaces the old. The built-in `MessagesState` gives the `messages` key a reducer that *appends*, so a node can return `{"messages": [reply]}` and the reply is added to the history instead of replacing it. That one detail confuses many beginners: if your history keeps vanishing, check the reducer.

There are two special node names: `START`, where every run begins, and `END`, where it stops. An agent is then just this: `START → agent → (tools → agent)* → END`. The loop you wrote with `for` and `if` becomes a cycle in a graph.

### The same agent as a graph

Here is the calculator-and-notes agent from The Claude Agent SDK lesson, rebuilt in LangGraph. It reuses the same framework-free `tools.py` from that lesson, unchanged, so copy that file into a new project. Then run `uv add langgraph langchain langchain-anthropic python-dotenv`, put `ANTHROPIC_API_KEY` in `.env`, and save this as `graph_agent.py`:

```python
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

import tools as plain  # the same framework-free functions as every other version

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
PROVIDER = os.environ.get("MIMIR_PROVIDER", "anthropic")  # or "openai", "ollama", ...


@tool
def calculate(a: float, op: str, b: float) -> str:
    """Apply one arithmetic operation (+, -, *, /) to two numbers. Use it for all math."""
    return plain.calculate(a, op, b)


@tool
def save_note(filename: str, text: str) -> str:
    """Save text to a Markdown note in the workspace. Pass a bare name like 'answer.md'."""
    answer = interrupt({"question": f"Save {filename}?", "text": text})  # (1) pause here
    if answer != "yes":
        return "The user declined to save the note. Give them the answer in chat instead."
    return plain.save_note(filename, text)


TOOLS = [calculate, save_note]
model = init_chat_model(MODEL, model_provider=PROVIDER, max_tokens=16000).bind_tools(TOOLS)  # (2)


def call_model(state: MessagesState) -> dict:  # (3) a node: state in, update out
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(TOOLS))  # runs every tool call in the last message
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)  # (4) tool calls? "tools" : END
builder.add_edge("tools", "agent")  # (5) the loop: results go back to the model
graph = builder.compile(checkpointer=InMemorySaver())  # (6) save state after every step


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo-1"}, "recursion_limit": 20}  # (7)
    task = "What is 17.5% of 2,340? Save the answer to answer.md."
    result = graph.invoke({"messages": [{"role": "user", "content": task}]}, config)
    while "__interrupt__" in result:  # (8) the graph stopped to ask a human
        request = result["__interrupt__"][0].value
        reply = input(f"{request['question']} {request['text']!r} [yes/no] ")
        result = graph.invoke(Command(resume=reply), config)
    for message in result["messages"]:
        message.pretty_print()
```

Run it with `uv run graph_agent.py`, answer `yes`, and you'll see the whole conversation printed: your question, a `calculate` call and its result `409.5`, a `save_note` call and its result, and the final answer.

Walk through the numbered comments:

1. **`interrupt`** pauses the whole graph and hands a value (here, what's about to be saved) to whoever is running it. More on this below.
1. **`init_chat_model`** picks a chat model by name and provider, and **`bind_tools`** attaches the tool schemas. LangChain built those schemas from each function's type hints and docstring, the same idea as the `@tool` decorator in the Agent SDK. Changing `PROVIDER` is all it takes to switch providers, as long as that provider's integration package is installed.
1. **The model node** is your "think" step. It returns only the new message, and the `MessagesState` reducer appends it.
1. **`tools_condition`** is a prebuilt conditional edge: if the last message has tool calls it routes to `"tools"`, otherwise to `END`. That's your `stop_reason` check.
1. **The edge back to `"agent"`** closes the loop. `ToolNode` ran every requested tool, matched each result to its call ID and appended them as tool messages, which is your dispatch code from Tool Errors and Parallel Calls.
1. **The checkpointer** saves the state after every step, which is what makes pausing and resuming possible.
1. **`recursion_limit`** is your step cap. It counts graph steps (each node run), not model calls, so 20 allows about 10 rounds of model plus tools. When it's hit, LangGraph raises `GraphRecursionError`, which you should catch and report, just like your graceful step-limit message.
1. **The resume loop** handles the pause, shown in the next sections.

You could get this exact graph from one call, `langchain.agents.create_agent(model, tools)`, which builds the same agent-and-tools cycle for you. Build it by hand first: when something goes wrong in the prebuilt version, you'll know what's inside.

#### Test the graph without a model

Because `call_model` looks up the global `model` each time it runs, a test can swap in a scripted fake, using the `monkeypatch` technique from Testing with pytest. This test runs in under a second, with no API key and no cost. Run `uv add --dev pytest` and save it as `test_graph_agent.py`:

```python
import os

os.environ.setdefault("ANTHROPIC_API_KEY", "not-used")  # the real model is never called
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langgraph.types import Command

import graph_agent


class ScriptedModel(GenericFakeChatModel):  # replays fixed replies, in order
    def bind_tools(self, tools, **kwargs):
        return self


def test_saves_after_approval(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(graph_agent, "model", ScriptedModel(messages=iter([
        AIMessage("", tool_calls=[{"name": "calculate", "id": "1",
                                   "args": {"a": 2340, "op": "*", "b": 0.175}}]),
        AIMessage("", tool_calls=[{"name": "save_note", "id": "2",
                                   "args": {"filename": "answer.md", "text": "409.5"}}]),
        AIMessage("Saved: 409.5"),
    ])))
    config = {"configurable": {"thread_id": "test"}}
    result = graph_agent.graph.invoke({"messages": [("user", "go")]}, config)
    assert result["__interrupt__"]                      # paused before saving
    assert graph_agent.graph.get_state(config).next == ("tools",)
    result = graph_agent.graph.invoke(Command(resume="yes"), config)
    assert (tmp_path / "workspace" / "answer.md").read_text() == "409.5"
    assert result["messages"][-1].content == "Saved: 409.5"
```

Run it with `uv run pytest`. This tests your *wiring* (routing, tool dispatch, the pause, the file write), not the model's judgment. You test judgment with evals, as in Agent Eval Fundamentals. Both matter, and the graph structure makes the first kind easy.

### Checkpointers and threads

A **checkpointer** saves a snapshot of the graph's state after every step. Snapshots are grouped into **threads**: each run you start with a new `thread_id` gets its own history, and invoking again with the same `thread_id` continues where it left off. A thread is LangGraph's word for a conversation or session.

`InMemorySaver` keeps snapshots in memory, which is fine for learning and tests but lost when the program exits. For real use, install a database-backed one: `langgraph-checkpoint-sqlite` provides `SqliteSaver` and `langgraph-checkpoint-postgres` provides `PostgresSaver`, and Postgres is the default database you've used since the Core path. With either, a run paused in one process can be resumed by a completely different process, even after a deploy or a crash. This is the durable pause from the Durable Execution lesson, with the step log written for you.

Checkpoints also make a run inspectable. `graph.get_state(config)` returns the latest snapshot: its `values` (the messages so far) and `next` (the nodes that will run next). `graph.get_state_history(config)` lists every snapshot in the thread, newest first. You can even resume from an older snapshot to replay a run from a chosen step, which LangGraph calls **time travel**. It's the replay technique from Agent Tracing and Debugging, built in.

### Human in the loop with interrupt

Calling `interrupt(value)` inside a node (or inside a tool that `ToolNode` runs) stops the graph, saves a checkpoint and returns control to your code. The value you passed shows up in the result under `"__interrupt__"`. Nothing is running while the graph waits, so a person can take minutes or days to decide. When they do, you call `graph.invoke(Command(resume=answer), config)` with the same `thread_id`, and `interrupt(...)` returns `answer` inside the node.

There's one rule that catches everyone. **On resume, the node runs again from its first line**, not from the `interrupt` call. LangGraph doesn't freeze the middle of a Python function. It reruns the node, and this time `interrupt` returns the saved answer instead of pausing. So any code *before* the `interrupt` runs twice. In `save_note`, the `interrupt` is the first line and the file write comes after it, so nothing happens twice. If you charged a card and then asked for approval, you'd charge it twice. That's the same idempotency lesson from Durable Execution: put side effects after the pause, or make them safe to repeat.

Compare this with the Claude Agent SDK's approval hook. The hook waits *inside* a running process, which is simple but dies with the process. The interrupt saves the state and exits, which takes more code but survives restarts. Which one you need depends on how long a human might take to answer.

### The wider ecosystem

Here's a map of the main frameworks as of October 2026. This field moves monthly, so check each project's docs and release dates before you rely on any row.

| Framework | Languages | What it's for | Providers |
| --- | --- | --- | --- |
| **LangGraph** | Python, JavaScript | Explicit graphs, checkpoints, interrupts. Precise control flow, at the cost of more code. | Any, through LangChain's model integrations |
| **Claude Agent SDK** | Python, TypeScript | Claude Code's full harness: file and shell tools, permissions, hooks, sessions, subagents. | **Claude only** |
| **OpenAI Agents SDK** | Python, TypeScript | A small set of primitives: agents, handoffs between agents, guardrails, sessions, built-in tracing. | Any, through adapters; some hosted tools work only with OpenAI models |
| **Pydantic AI** | Python | Type-safe agents: tool arguments and final outputs are Pydantic models, so bad output fails validation. | Any |
| **Google ADK** | Python, TypeScript, Go, Java, Kotlin | Workflow agents (sequential, parallel, loop), a local web UI, an evaluation runner, deployment to Google Cloud. | Any, but Gemini-first; some built-in tools are Gemini-only |
| **CrewAI** | Python | "Crews" of agents with roles and goals, plus event-driven Flows. Quick multi-agent prototypes. | Any |
| **Microsoft Agent Framework** | Python, .NET, Go (preview) | The successor to AutoGen and Semantic Kernel: agents plus graph-based workflows. | Any, Azure-first |
| **smolagents** | Python | Hugging Face's small library for "code agents" that write Python as their actions. | Any, including open models |

In TypeScript, you already met the Vercel AI SDK in the Frontend section. It and Mastra are the common choices there.

**Lock-in** comes in degrees. The Claude Agent SDK is the only one here tied to a single provider. The others call themselves model-agnostic, but check the features you rely on: a built-in web search tool, a hosted file store or default tracing that sends your data to a vendor's dashboard may only work with, or only go to, one company. The lowest lock-in comes from keeping your tools, prompts and evals in plain code, as `tools.py` does, so changing frameworks means rewriting glue.

### Comparing frameworks fairly

Every framework's homepage claims it's the simplest and the most powerful. Compare on things you can measure instead:

- **Lines of glue code** for the same agent, excluding the shared tools.
- **Success rate** on the same set of tasks, run several times each.
- **Tokens and time per task.** Some frameworks add long system prompts or extra model calls.
- **Debuggability.** Break a tool on purpose and time how long it takes you to find the cause from the logs.
- **Lock-in and churn.** Which providers it supports, and how often its API broke in the last year. A pre-1.0 version number is a warning.

Benchmarks published by a framework's own company aren't evidence. Independent tests often find that for a simple agent, the model matters far more than the framework, and that the frameworks differ mainly in speed, install size and how easy they are to debug.

Keep one more idea in mind: **abstractions leak**. An abstraction leaks when you have to understand what it hides in order to fix it. The 12-Factor Agents essay argues that good production agents own their prompts, their context window and their control flow, even when a framework does the plumbing. LangGraph fits that well, because you write the nodes and edges yourself. "Port Your Agent" is where you'll test these claims with your own numbers.

### On other providers

LangGraph itself doesn't call any model. The model node does, so switching providers changes one line. To use OpenAI, run `uv add langchain-openai`, set `MIMIR_PROVIDER=openai` and `MIMIR_MODEL` to an OpenAI model name, and put `OPENAI_API_KEY` in `.env`. To use a free local open model, install [Ollama](https://docs.ollama.com/api/openai-compatibility), pull a model that supports tool calling, such as [Qwen3](https://ollama.com/library/qwen3), and point the OpenAI integration at Ollama's OpenAI-compatible endpoint:

```python
model = init_chat_model(
    "qwen3:8b", model_provider="openai",                   # OpenAI-style API...
    base_url="http://localhost:11434/v1", api_key="ollama",  # ...served by local Ollama
).bind_tools(TOOLS)
```

The graph, `ToolNode`, the checkpointer and the interrupt don't change, because LangChain converts every provider's tool calls into the same `tool_calls` list. What does change is behavior. Small local models call tools less reliably, sometimes skip a tool and guess, and may reuse simple call IDs, so run your test tasks several times before you trust them. See OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) for what LangChain is translating to underneath, and Running Open Models, later in this section, for choosing a local model.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) and [Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph), then work through the [quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart).
   - Before you start the quickstart, sketch your "Agent Loop From Scratch" agent as a graph on paper: which nodes, which edges, what state.
1. Read LangGraph's [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) and [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) pages.
   - In Interrupts, find the rules for code that runs before an interrupt, and connect them to idempotency.
   - In Persistence, read about threads, checkpoints and `get_state_history`. Skim the rest.
1. Practice: build `graph_agent.py` and `test_graph_agent.py` from this lesson, then change them.
   - Answer `no` at the prompt and check the final answer.
   - Write a second test where the fake model asks for `calculate` forever, and assert that a low `recursion_limit` raises `GraphRecursionError` (import it from `langgraph.errors`).
   - Run `uv add langgraph-checkpoint-sqlite` and switch to `SqliteSaver.from_conn_string("checkpoints.db")` (it's a context manager, so use `with`). Start a run, stop the program at the approval prompt, and resume the same `thread_id` from a fresh program.
1. Read [12-Factor Agents](https://github.com/humanlayer/12-factor-agents), at least the README and factors 1 through 8, as your one critical read on the ecosystem.
   - Then skim the docs home page of one other framework: the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/), [Pydantic AI](https://pydantic.dev/docs/ai/overview/) or [Google ADK](https://adk.dev/). Find its equivalent of your loop, your tool dispatch and your stop condition, and note how it declares tools and validates output.
   - Write three sentences on which factors LangGraph makes easy and which it makes hard.
1. Rebuild one tool and one task from "Agent Loop From Scratch" in LangGraph, reusing your tool function unchanged. You'll extend this in "Port Your Agent".

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What three things does every agent framework do under the branding?](#every-framework-wraps-the-same-loop)
- [What are state, nodes and edges in LangGraph, and what does a reducer do?](#langgraph-in-one-picture)
- [In the graph version of the agent, what replaces your stop_reason check and your step cap?](#the-same-agent-as-a-graph)
- [What does a checkpointer save, and what is a thread?](#checkpointers-and-threads)
- [Why must code that runs before an interrupt be safe to run twice?](#human-in-the-loop-with-interrupt)
- [Which framework in the survey works with only one provider, and what other kinds of lock-in should you check for?](#the-wider-ecosystem)
- [Name four things you can measure to compare two frameworks fairly.](#comparing-frameworks-fairly)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- LangChain's [agents guide](https://docs.langchain.com/oss/python/langchain/agents) covers `create_agent`, the prebuilt version of the graph you built by hand, including middleware for approvals and context trimming.
- LangGraph's [time travel guide](https://docs.langchain.com/oss/python/langgraph/use-time-travel) shows how to replay a thread from an earlier checkpoint.
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/), [CrewAI](https://docs.crewai.com/) and [smolagents](https://huggingface.co/docs/smolagents/index) are worth a skim if a job posting names them.
- Geekflare's [Best Open Source AI Agent Frameworks in 2026](https://geekflare.com/open-source/ai-agent-frameworks/) builds the same research agent in seven frameworks with one model. Read it for the method, not the rankings: its test tools are the publisher's own products, and some of its numbers don't match its own tables.
