### Introduction

You now have several ways to build an agent: your own loop on top of a model API, an agent SDK like the Claude Agent SDK, a general framework like LangGraph or Pydantic AI, and, as you'll see in this lesson, a managed runtime where the provider runs the agent for you. You can also run any of them against an open model on your own machine, as you did in Running Open Models. None of these is always right. Frameworks save time on the boring parts and cost you visibility into the parts that break.

This lesson gives you a way to choose, and to explain your choice in a design review or a job interview. "Should we use a framework?" is one of the most common questions in agent engineering interviews, and "it depends" is only a good answer if you can say on what. You'll also build a small tool that shows you the exact request any framework sends to the model, which is the single most useful habit for keeping a framework honest. "Port Your Agent", next, is where you test all of this with your own numbers.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The options, from a raw loop to a managed runtime.
- What frameworks give you: tools, retries, tracing, state and integrations.
- What frameworks hide: prompts, context assembly and control flow.
- How to see the exact request any framework sends.
- Signs you should stay with a raw loop, and signs you should adopt a framework or SDK.
- Managed agent runtimes as a further option.
- How to keep a framework replaceable, and how to decide with numbers.

### The options

Line up everything you've met so far by one question: **who writes the loop, and who runs it?**

| Option | You write | Someone else provides | Example |
| --- | --- | --- | --- |
| Raw loop | The loop, tool dispatch, history, limits, tracing | Only the model API | Your "Agent Loop From Scratch" project |
| SDK helper | Your tools | A small loop over your tools | The Anthropic SDK's tool runner |
| General framework | Tools, plus nodes or agent definitions | Loop, state, checkpoints, provider adapters | LangGraph, OpenAI Agents SDK, Pydantic AI |
| Agent SDK (harness) | Options and policy | A full harness: file and shell tools, permissions, compaction, sessions | Claude Agent SDK |
| Managed runtime | Agent configuration and your custom tools | The harness *and* the servers and sandbox it runs on | Claude Managed Agents |

Moving down the table, you write less code and control less. That's the whole trade. Notice that the model and your tools appear in every row. The framework only changes the glue between them.

There's also a row above the table: **no agent at all**. Remember Workflows vs Agents. A single model call, or a fixed chain of calls, solves many problems that people reach for agents to solve. Before choosing a framework, ask whether the task needs a loop.

### What frameworks give you

Frameworks are best at **plumbing**: code that every agent needs, that has nothing to do with *your* problem, and that's tedious to write and easy to get subtly wrong. You've written much of it by hand already, so you know how much time it takes:

- **Tool schemas from type hints.** You wrote JSON Schema by hand in Function Calling. Frameworks build it from a function's signature and docstring.
- **Retries and timeouts.** Backoff on rate limits and server errors, as in Timeouts, Retries and Rate Limits.
- **Tracing.** One span per model call and tool call, often exported to OpenTelemetry, which you set up by hand in Agent Tracing and Debugging.
- **State and checkpoints.** Saving after every step so a run survives a crash or waits days for a human, the hard part of Durable Execution.
- **Human approval.** Pausing for a person and resuming later, such as LangGraph's `interrupt`.
- **Integrations.** Adapters for many model providers, vector stores and MCP servers.
- **Harness features.** In an agent SDK: file and shell tools, permissions, compaction and subagents, already tested by many users.

Each of these is a week of work done well, or an afternoon done badly. When you need several of them, a framework is often the right call.

### What frameworks hide

Frameworks are worst at the things that decide **quality**. The 12-Factor Agents essay you read in LangGraph and the Wider Ecosystem names three:

- **The prompt.** Many frameworks add their own system prompt, tool-use instructions or output-format text around yours. If a framework's built-in prompt says "think step by step and always use a tool", your agent will call tools it doesn't need, and you won't know why.
- **The context window.** Something decides which messages, tool results and retrieved documents go into each request, in what order and how they're trimmed. You learned in Context Engineering for Agents that this assembly is most of what makes an agent good. In a framework, it may happen in code you've never read, including automatic compaction that drops the one fact the agent needed.
- **The control flow.** When to call a tool, when to stop, when to retry and when to ask a human. If the framework decides, a bad decision is buried inside it.

When an agent makes a bad step, you fix it by looking at exactly what the model saw and asking "would a smart person have done better with this input?" If you can't see that input, you're guessing. So here's the rule this lesson is built around: **before you adopt a framework, make sure you can print the full request for any turn.**

Some frameworks make that easy: in LangGraph the state *is* the message list, and checkpoints let you read every step. Others make it harder: the Claude Agent SDK writes its own system prompt (unless you replace it) and decides when to compact. Either way, there's one method that always works.

### See the exact request

Every SDK and framework ends up sending an HTTP request to a model API, and almost all of them let you change the API's address, called the **base URL**. So you can put a tiny **proxy**, a program that sits in the middle and passes traffic along, between your agent and the API. It writes every request body to a file and forwards it unchanged. It works with any framework, because it doesn't care who made the request.

Save this as `recorder.py`. It uses only the Python standard library:

```python
"""A recording proxy: log every request body, then forward it unchanged."""
import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = os.environ.get("UPSTREAM", "https://api.anthropic.com")  # the real API
DROP = {"host", "content-length", "connection", "accept-encoding", "transfer-encoding"}


class Recorder(BaseHTTPRequestHandler):
    def forward(self) -> None:
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if body:  # (1) the exact bytes the framework built, as JSON
            with open("requests.jsonl", "a") as log:
                entry = {"at": datetime.now().isoformat(), "path": self.path,
                         "request": json.loads(body)}
                log.write(json.dumps(entry) + "\n")
        headers = {k: v for k, v in self.headers.items() if k.lower() not in DROP}
        request = urllib.request.Request(UPSTREAM + self.path, data=body or None,
                                         headers=headers, method=self.command)
        try:
            upstream = urllib.request.urlopen(request, timeout=600)
        except urllib.error.HTTPError as error:  # (2) pass API errors through untouched
            upstream = error
        self.send_response(upstream.status)
        for key, value in upstream.headers.items():
            if key.lower() not in DROP:
                self.send_header(key, value)
        self.end_headers()
        while chunk := upstream.read1(8192):  # (3) relay streamed replies as they arrive
            self.wfile.write(chunk)
            self.wfile.flush()

    do_GET = do_POST = forward


if __name__ == "__main__":
    print(f"Recording on http://localhost:8787 -> {UPSTREAM}")
    ThreadingHTTPServer(("localhost", 8787), Recorder).serve_forever()
```

Start it in one terminal with `python3 recorder.py`. Then point your agent at it, in another terminal:

- **Anthropic SDK (your raw loop):** `anthropic.Anthropic(base_url="http://localhost:8787")`.
- **Claude Agent SDK:** add `env={"ANTHROPIC_BASE_URL": "http://localhost:8787"}` to `ClaudeAgentOptions`.
- **LangGraph:** pass `base_url="http://localhost:8787"` to `init_chat_model`.

Run one task, then open `requests.jsonl`. Each line is one model call: the full system prompt, every message, every tool definition and every setting. Notes on the numbered comments:

1. **The log** holds the request exactly as sent. Pretty-print one line with `python3 -m json.tool`, or load the file with pandas to count tokens per turn.
1. **Errors pass through** so the framework's own retry logic still sees a real 429 or 500.
1. **Streaming** works because the proxy relays each chunk as soon as it arrives.

The first time you run this against a framework, read the system prompt carefully. You'll often find instructions you didn't write. It's also the fastest way to find out why a run got slow: compare the request size on turn 2 with turn 20.

<div class="lesson-note lesson-note--warning" markdown="1">

#### The log contains secrets and data

The proxy drops nothing from request bodies, so `requests.jsonl` holds everything your users typed and every tool result. API keys travel in headers, which the proxy forwards but doesn't log. Keep the log out of Git (add it to `.gitignore`), and only run the proxy on your own machine.

</div>

### Signs you should stay with a raw loop

A raw loop, perhaps with a small SDK helper, is the better choice when:

- **The agent is small.** A handful of tools, one model, runs that finish in a minute. Your loop is under 100 lines, and every line is readable. A framework would add more concepts than it removes.
- **Quality depends on context assembly.** If your edge comes from exactly what goes into each request (a careful retrieval step, a trimmed history, cache-friendly ordering), you want that code in front of you.
- **You need exact, stable requests.** Prompt caching needs a byte-identical prefix, as you saw in Agent Cost and Latency. Audits and regulated industries may need to show exactly what was sent. A framework that reorders or rewrites messages works against both.
- **The team must debug it at 3 a.m.** Fewer layers means a shorter path from a bad output to its cause.
- **Dependencies are a cost.** Every framework adds a version to pin, breaking changes to absorb and a security surface. Many agent frameworks are still before version 1.0.

### Signs you should adopt a framework or SDK

Switch when you notice you're **rebuilding a framework badly**. The signals:

- **You need a durable pause.** Human approval that may take hours, across restarts and deploys. Checkpointing done right is hard, and LangGraph or a durable workflow engine gives it to you.
- **The agent needs a computer.** If the job involves files, shells, code or long sessions, an agent SDK like the Claude Agent SDK gives you those tools, plus permissions and compaction, already tested by many users. Writing a safe file-editing tool and a shell sandbox yourself takes weeks.
- **You need many integrations.** Several providers, MCP servers, vector stores and tracing backends. Adapters are pure plumbing.
- **Several agents must coordinate.** Handoffs, shared state and parallel branches are where graph frameworks earn their keep. You'll design these in Subagents and Orchestration.
- **Your team already uses one.** A shared framework means shared knowledge, shared tracing and code that colleagues can review. That counts for a lot.

Choosing between an agent SDK and a general framework mostly comes down to two questions. Does the agent need a computer? Then an agent SDK. Must it run on more than one provider, or on an open model? Then a provider-neutral framework or your own loop, because the Claude Agent SDK runs Claude models only.

### Managed agent runtimes

A **managed runtime** moves the harness, and the servers it runs on, to the provider. With Claude Managed Agents (a Claude feature, in beta at the time of writing), you store an agent's configuration (model, system prompt, tools, skills) with Anthropic, then start **sessions**. Each session gets its own sandboxed container with a shell and files, Anthropic's servers run the loop, and your code reads a stream of events and answers calls to your own tools. Other providers offer similar services, such as Google's Vertex AI Agent Engine and Amazon Bedrock AgentCore, each with its own design.

What you gain: no loop to host, no sandbox to secure, no scheduler, sessions that keep running when your laptop closes, and an event log the provider stores for you. What you give up: control over the harness, portability (your configuration only runs there), and some visibility, because the loop runs on someone else's servers. Your data and tool results also pass through the provider's systems, which matters for privacy rules.

A managed runtime makes sense for long-running or scheduled agents when you'd otherwise spend weeks on infrastructure, and when you're comfortable with one provider. It's a poor fit when you need an open model, strict data residency the service doesn't offer, or exact control of every request.

### Keep the core yours

Whatever you choose, you can make switching cheap. Put the parts that decide quality in plain Python you own, with no framework imports, and keep each framework at the edges as thin glue. You already did this with `tools.py` earlier in this section. Do the same for your prompts and your context assembly:

```python
"""core.py: the parts that decide quality. Plain Python, no framework imports."""
SYSTEM_PROMPT = (
    "You are a careful research assistant. Use the tools to check facts. "
    "If the notes don't answer the question, say so instead of guessing."
)


def build_messages(task: str, notes: list[str], max_notes: int = 5) -> list[dict]:
    """Decide exactly what the model sees for this task."""
    recent = notes[-max_notes:]  # your trimming rule, not the framework's
    context = "\n".join(f"- {note}" for note in recent) or "(no notes yet)"
    return [{"role": "user", "content": f"<notes>\n{context}\n</notes>\n\n{task}"}]


# The edges: each version is a few lines of glue around the same core.
#
# raw loop:  client.messages.create(model=MODEL, max_tokens=16000, system=SYSTEM_PROMPT,
#                                   tools=TOOLS, messages=build_messages(task, notes))
# LangGraph: graph.invoke({"messages": [{"role": "system", "content": SYSTEM_PROMPT},
#                                       *build_messages(task, notes)]}, config)
# Agent SDK: query(prompt=build_messages(task, notes)[0]["content"],
#                  options=ClaudeAgentOptions(system_prompt=SYSTEM_PROMPT, ...))
```

Because `build_messages` is a plain function, you can test it with pytest in milliseconds: assert that only the last five notes appear, that an empty list gives "(no notes yet)", and that the task comes last. And your eval suite, from Agent Eval Fundamentals, belongs in the core too: the same tasks and graders run against every version. With prompts, context, tools and evals in code you own, changing frameworks means rewriting glue, not your agent. That's exactly how "Port Your Agent" is set up.

### Decide with numbers

Popularity, GitHub stars and a framework's own benchmarks are weak arguments. Strong ones are measured on *your* tasks:

- **Lines of glue code**, excluding the shared core.
- **Success rate** on the same tasks, run several times each. Report it with a confidence interval, as in Eval Statistics, because ten tasks run three times gives a wide one.
- **Tokens and time per task.** The recording proxy shows you where extra tokens come from.
- **Minutes to diagnose a failure.** Break a tool on purpose and time how long it takes to find the cause from each version's logs or traces.
- **Lock-in and churn.** Which providers each option supports, and how often its API broke in the last year.

Then write the decision down in a few lines, the way a team would in a design review: the options you considered, the numbers, what you chose, and **what would make you change your mind** ("if we need approvals that survive restarts, we move the approval step to LangGraph"). That last line shows a reviewer, or an interviewer, that you chose on purpose and know where your choice stops working.

### On other providers

Everything in this lesson's method is provider-neutral. The recording proxy works with any API that uses HTTP and JSON. For OpenAI, start it with `UPSTREAM=https://api.openai.com` and pass `base_url="http://localhost:8787/v1"` to the `OpenAI` client, or to any framework that uses it. For a local open model, start it with `UPSTREAM=http://localhost:11434` and point your OpenAI-style client at `http://localhost:8787/v1`, so you can see exactly what a framework sends to [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility). Request shapes differ, so read the logs with the right docs open: OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) describes its `tools` and `tool_calls` fields, which play the role of Claude's `tools` and `tool_use` blocks. The framework choice itself changes with providers: the Claude Agent SDK and Claude Managed Agents run Claude only, while LangGraph, Pydantic AI and the OpenAI Agents SDK can run open models, as you saw in Running Open Models. If an open model is in your plans, that alone may decide the question.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Reread the "When (and when not) to use agents" and "When and how to use frameworks" parts of [Building effective agents](https://www.anthropic.com/research/building-effective-agents).
   - Write down the one sentence from each part that you'd quote in a design review.
1. Read [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) factors 2, 3 and 8 (own your prompts, own your context window, own your control flow).
   - For each, write one sentence on whether the Claude Agent SDK and your chosen framework let you do it.
1. Reread the parts of the [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) that compare the SDK with the plain Client SDK and with Claude Code.
   - Then skim the [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) and list three things it takes off your plate and one thing it takes away from you.
1. Practice: build `recorder.py` and point two versions of the same agent at it, such as your raw loop and the LangGraph agent from LangGraph and the Wider Ecosystem.
   - Run the same task through each and compare the logged requests: system prompt length, number of model calls and the total size of the last request.
   - Find one instruction in a framework's request that you didn't write, or confirm there is none.
1. Take one failed run from a framework you tried in the previous lessons and find the exact prompt the model saw. Time how long that takes, and note what tool or setting made it possible.
1. Write a half-page decision record for an agent you'd like to build: the options, the numbers you'd measure, your choice and what would make you change your mind. Keep it for "Port Your Agent".

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Which kinds of work do frameworks do best, and why?](#what-frameworks-give-you)
- [Which three things that decide quality can a framework hide from you?](#what-frameworks-hide)
- [How can you see the exact request any framework sends to the model?](#see-the-exact-request)
- [Name three signs that a raw loop is the better choice.](#signs-you-should-stay-with-a-raw-loop)
- [When does an agent SDK beat a general framework, and when is it ruled out?](#signs-you-should-adopt-a-framework-or-sdk)
- [What does a managed runtime take off your plate, and what does it cost you?](#managed-agent-runtimes)
- [How do you keep a framework replaceable?](#keep-the-core-yours)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) shows what a hosted agent runtime takes off your plate.
- Hamel Husain's [essay on showing the prompt](https://hamel.dev/blog/posts/prompt/) uses an intercepting proxy, much like this lesson's recorder, to reveal the hidden prompts inside popular LLM libraries.
