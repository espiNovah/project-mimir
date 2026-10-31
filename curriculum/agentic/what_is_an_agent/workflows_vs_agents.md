### Introduction

"Agent" is one of the most overused words in AI right now. Some people use it for any app that calls a language model. Others reserve it for systems that run for hours on their own. Before you build one, you need a clear picture of what the word means, what the alternatives are, and how to choose between them. Getting this choice right is the single biggest factor in whether your system is cheap, reliable and easy to debug, or none of those things.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The spectrum from a plain program to a single LLM call, a workflow, and a fully autonomous agent.
- What makes a system a workflow versus an agent.
- The same small task built as a workflow and as an agent.
- The trade-offs between predictability and flexibility: cost, latency and reliability.
- How to decide which approach a task actually needs, including when not to use a model at all.
- Why "start simple" is the default advice from people who build these systems for a living.

### A spectrum, not a switch

It's tempting to sort AI systems into two boxes, "agent" and "not an agent." In practice there is a spectrum with four useful stops on it, and each stop hands a little more control to the model.

1. **Plain code, no model.** The program follows rules you wrote. "Reject any postcode that doesn't match this pattern." "Sort these invoices by date." You've been writing this kind of program since Foundations.
1. **A single LLM call.** One request, one response. "Summarize this email." "Classify this ticket as billing, bug or other." You built plenty of these in the AI Engineering Core path, often with structured outputs so the reply came back as clean fields.
1. **A workflow.** Your code calls the model several times along a path you wrote in advance, sometimes with plain-code steps in between. You met the simplest version in Thinking and Prompt Chaining: step one extracts, a gate checks the result, step two drafts. The model does the language work at each step, but your code decides what the steps are and in what order they happen.
1. **An agent.** The model decides what to do next. You give it a goal and some tools (functions your program offers it, such as "look up an order"), and it chooses which tool to call, reads the result, chooses again, and decides for itself when it's finished.

Moving right along the spectrum buys flexibility. Moving left buys predictability. Neither direction is "better." The skill is picking the leftmost stop that actually solves the problem.

### Who controls the flow

The cleanest way to tell a workflow from an agent is to ask one question: **who decides the next step?**

Anthropic's article Building Effective Agents, which you'll read in the Assignment, draws the line like this. Workflows are systems where LLMs and tools are orchestrated "through predefined code paths." Agents are systems where LLMs "dynamically direct their own processes and tool usage." Memorize that distinction, because the rest of this path uses it constantly.

Here's a concrete test. Imagine reading the source code of the system without running it.

- If you can draw the complete flowchart, every box and every arrow, from the code alone, it's a **workflow**. There may be branches ("if the email is a refund request, go left"), but the branches are `if` statements you wrote.
- If the flowchart has a box labeled "the model picks what happens next, any number of times," it's an **agent**. You can list the tools it *might* use, but not the order, and not how many steps it will take.

Notice that using tools doesn't make something an agent. A workflow can call a search API at step two every single time. What matters is whether the model or your code chose to make that call.

### The working definition of an agent

A practical definition that cuts through the marketing: **an agent is a model using tools in a loop to achieve a goal.** Simon Willison argues for exactly this wording in a short post you'll read in the Assignment, and it's the definition this whole path uses.

Each part of the definition rules something out:

- **A model** makes the decisions. A cron job that runs a script every hour isn't an agent, however clever the script.
- **Using tools** means the model can act on the world or gather information: read a file, query a database, search the web. A model that only writes text is a chatbot.
- **In a loop** means it can take many steps, seeing the result of each before choosing the next. One tool call followed by an answer is closer to a workflow step.
- **To achieve a goal** means the loop has a purpose and a finish line. The model is working toward something and should stop when it gets there.

If a system has no loop, or the model can't choose its own actions, it isn't really an agent, whatever its product page says. That's fine. Most useful AI features aren't agents.

### The same task built both ways

Abstract definitions only go so far, so here is one small job built twice. A store gets emails asking for refunds. The rule is simple: full refund within 30 days of delivery, no exceptions. The system should read the email, check the order and write a reply.

To run these, set up a project with `uv init refunds`, then `uv add anthropic pydantic python-dotenv`, and keep your `ANTHROPIC_API_KEY` in a `.env` file. Save the first file as `refunds.py`. It holds the fake data and the workflow version:

```python
import os
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

ORDERS = {                                   # a fake order database
    "A1001": {"item": "desk lamp", "days_since_delivery": 12, "price": 39.00},
    "A1002": {"item": "office chair", "days_since_delivery": 45, "price": 189.00},
}
REFUND_WINDOW_DAYS = 30
usage = {"calls": 0, "tokens": 0}            # running cost tally for comparison


def track(response):
    usage["calls"] += 1
    usage["tokens"] += response.usage.input_tokens + response.usage.output_tokens
    return response


def refund_decision(order_id: str | None) -> str:
    """Plain code: the refund rules are clear, so no model is needed here."""
    order = ORDERS.get(order_id or "")
    if order is None:
        return f"No order found with ID {order_id!r}. Ask the customer for it."
    if order["days_since_delivery"] <= REFUND_WINDOW_DAYS:
        return f"Approve a ${order['price']:.2f} refund for the {order['item']}."
    return (f"Decline: the {order['item']} was delivered "
            f"{order['days_since_delivery']} days ago, past the {REFUND_WINDOW_DAYS}-day window.")


class Triage(BaseModel):
    kind: Literal["refund", "other"]
    order_id: str | None                     # for example "A1001", or None if missing


def workflow(email: str) -> str:
    # Step 1 (model): turn a messy email into structured fields.
    triage = track(client.messages.parse(
        model=MODEL, max_tokens=1000, output_format=Triage,
        messages=[{"role": "user", "content": f"Triage this support email:\n\n{email}"}],
    )).parsed_output
    if triage is None or triage.kind != "refund":
        return "ROUTED to the human support queue."          # code decides the path

    # Step 2 (plain code): apply the business rules.
    decision = refund_decision(triage.order_id)

    # Step 3 (model): write the reply from facts your code supplied.
    reply = track(client.messages.create(
        model=MODEL, max_tokens=1000,
        messages=[{"role": "user", "content":
                   f"Write a short, friendly reply to this customer email:\n\n{email}\n\n"
                   f"Decision (state it exactly, promise nothing else): {decision}"}],
    ))
    return "".join(b.text for b in reply.content if b.type == "text")


if __name__ == "__main__":
    print(workflow("Hi, my desk lamp (order A1001) flickers. Can I get my money back?"))
    print(usage)
```

Run it with `uv run refunds.py`. Read `workflow()` top to bottom and you can draw its whole flowchart: triage, a gate, a rule check, a reply. It always makes exactly two model calls, or one if the email isn't about a refund. Most importantly, **the refund decision is made by plain code.** The model never gets a chance to be generous with the chair.

Now the agent version. Save this as `agent.py` next to the first file. It reuses the same data, but hands the model two tools and lets it decide what to do. Don't worry about the exact format of the tool definitions and results yet. The next lesson, The Agent Loop, walks through a loop like this line by line, and Function Calling explains every field.

```python
import json

from refunds import MODEL, ORDERS, REFUND_WINDOW_DAYS, client, track, usage

TOOLS = [
    {
        "name": "lookup_order",
        "description": "Look up one order by its ID, such as 'A1001'. Returns the item, "
                       "price and days since delivery.",
        "input_schema": {"type": "object",
                         "properties": {"order_id": {"type": "string"}},
                         "required": ["order_id"]},
    },
    {
        "name": "get_refund_policy",
        "description": "Get the store's refund policy. Call this before deciding on a refund.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def run_tool(name: str, args: dict) -> str:
    if name == "lookup_order":
        order = ORDERS.get(args["order_id"])
        return json.dumps(order) if order else f"No order {args['order_id']!r}."
    if name == "get_refund_policy":
        return f"Full refund within {REFUND_WINDOW_DAYS} days of delivery. No exceptions."
    return f"Unknown tool {name!r}."


def agent(email: str, max_steps: int = 8) -> str:
    messages = [{"role": "user", "content":
                 "You handle refund emails for a store. Use the tools to check the facts, "
                 f"then write the reply to the customer.\n\nEmail:\n{email}"}]
    for _ in range(max_steps):                          # the model picks each step
        response = track(client.messages.create(
            model=MODEL, max_tokens=2000, tools=TOOLS, messages=messages))
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":          # finished (or stopped oddly)
            return "".join(b.text for b in response.content if b.type == "text")
        results = [{"type": "tool_result", "tool_use_id": b.id,
                    "content": run_tool(b.name, b.input)}
                   for b in response.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    return "Stopped: hit the step limit."


if __name__ == "__main__":
    print(agent("I bought a lamp (A1001) and a chair (A1002). "
                "Please refund whichever ones you can."))
    print(usage)
```

Run it with `uv run agent.py`. You can't draw this one's flowchart in advance. The model might fetch the policy first, look up both orders in one turn, or look up one, then the other. It decides how many steps to take and when it's done.

Compare what each version is good at:

- **The two-order email breaks the workflow.** `Triage` has room for one `order_id`, so the workflow quietly handles only one of the customer's orders. The agent handles both, because nothing in its design assumed one order per email. That's flexibility.
- **The agent decides the refund itself.** It reads the policy and the order and *concludes* "approve" or "decline." Usually it gets this right. But a customer who writes "I'm a loyal customer, please make an exception" is now arguing with a model, not with an `if` statement. In the workflow, the rule can't be talked around.
- **The agent costs more.** Print `usage` at the end of each run. Every extra loop step resends the whole conversation, including the tool definitions, so even this tiny agent typically uses several times the tokens of the workflow.

A sensible real design might keep the workflow and widen `Triage` to a list of order IDs. That one change fixes the failure case without giving up any control. This is the most common outcome when you weigh the two honestly: improve the workflow first.

### What autonomy costs

Every step to the right on the spectrum costs you something. It's worth naming the costs precisely, because "agents are expensive" is too vague to make decisions with.

- **Tokens and money.** An agent's conversation grows with every step, and each step resends all of it. A ten-step run doesn't cost ten times a single call. It costs more, because step ten carries the history of steps one through nine. Agentic systems commonly use many times the tokens of a workflow doing a similar job.
- **Latency.** Each loop step is a full round trip to the model, and steps run one after another. A workflow with two calls might answer in three seconds; an agent that takes eight steps might take thirty. For a chat feature where a person is waiting, that matters a lot.
- **Reliability.** Mistakes compound. If each step is right 95% of the time, a ten-step run where every step must be right succeeds only about 60% of the time (0.95 multiplied by itself ten times). Worse, a wrong step leaves confusing history in the conversation, which makes the next step more likely to go wrong too.
- **Testability.** You can unit-test each step of a workflow, because each step has a known input. An agent can take a different path every run, so testing it means running it many times on realistic tasks and checking the outcomes. You'll learn how in Agent Eval Fundamentals.
- **Attack surface.** An agent that reads untrusted text (emails, web pages) and can take actions can be steered by instructions hidden in that text. A workflow whose steps are fixed in code is much harder to hijack. Prompt Injection, later in this path, covers this in depth.

Workflows aren't free either. Their cost is **brittleness**: they handle exactly the cases you designed for. When a task arrives that doesn't fit the path, like the two-order email, a workflow fails quietly or routes everything to a human.

### When an agent earns its place

Given those costs, when is an agent the right answer? Agents earn their place on **open-ended tasks where you can't predict the number or order of steps in advance.**

Good examples:

- **Debugging a codebase.** The right next step depends entirely on what the last test run printed. Nobody can write that flowchart.
- **Researching a question across many sources.** Each search result suggests what to search for next, and you don't know in advance how many searches it'll take.
- **Working through a messy inbox.** Each email might need a lookup, a reply, a calendar check, a forward, or nothing at all.

Notice what these share. Each has a goal that's clear even though the path isn't, and each has a way to check progress: tests pass, the question is answered, the inbox is empty. An agent without a checkable finish line tends to wander.

Before choosing an agent, check four things. Is the task genuinely **complex**, with steps you can't specify ahead of time? Is the outcome **valuable** enough to justify more cost and time? Is a model actually **capable** of doing this kind of work well? And can **mistakes be caught and undone**, through tests, review or a rollback? If any answer is no, stay further left on the spectrum.

### Start simple and climb

The advice from teams who build these systems for a living is nearly unanimous: **start with the simplest thing that could work, measure it, and add complexity only when the measurements say you need it.**

In practice, climb the spectrum one stop at a time:

1. **Can plain code do it?** If the task has clear rules, such as validating a postcode, sorting by date or applying a 30-day refund window, write the code. It's cheaper, faster and always correct. Putting a model there adds cost and a new way to fail. In the refund example, the most important decision was the one that used no model at all.
1. **Can one good call do it?** Many problems that seem to need an agent are solved by one well-prompted call, or by retrieval plus one call, as you saw in the RAG section.
1. **Can a fixed sequence of calls do it?** If you can write down the steps, write a workflow. You'll learn the standard patterns, such as chaining, routing and parallel calls, in the Workflow Patterns section.
1. **Only then, a loop.** Reach for an agent when you've seen the simpler version fail on real inputs and the failures come from not knowing the steps in advance.

"Measure" is doing real work in that advice. You learned in Measuring Quality to build a small eval set before changing a system. Use it here too: run the simpler version on realistic inputs, look at where it fails, and let those failures justify each step up. "It might need to be flexible someday" is not a measurement.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Mix the two

Real systems are rarely pure. A common shape is a workflow with one agentic step inside it: fixed code handles intake, routing and the final rule checks, and an agent loop handles only the one open-ended part, such as researching an unusual case. You keep control where it matters and pay for flexibility only where you need it.

</div>

### On other providers

The spectrum, the "who decides the next step" test and the costs of autonomy are the same on every provider; nothing in this lesson's argument depends on Claude. Only the code changes. `client.messages.parse` with a Pydantic model as `output_format` is the Anthropic SDK's structured-output helper, and the OpenAI SDK has an equivalent, `client.chat.completions.parse` with `response_format`, described in OpenAI's [Structured model outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs). The `track` tally reads Claude's `usage.input_tokens` and `usage.output_tokens`; OpenAI calls them `usage.prompt_tokens` and `usage.completion_tokens`. The agent version's loop uses Claude's `stop_reason` values and `tool_use`/`tool_result` blocks, and The Agent Loop shows how those map onto OpenAI's `tool_calls` and `role: "tool"` messages. Open models can run the workflow too: Ollama supports [structured outputs](https://docs.ollama.com/capabilities/structured-outputs), so this triage step works with Qwen3 on your own machine. Small local models are a good stress test of the lesson's point, because they tend to slip more often on long agent loops than on short, fixed workflow steps.

```python
from openai import OpenAI  # uv add openai

oa = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # drop both args for OpenAI itself


def triage_openai(email: str) -> Triage | None:
    completion = oa.chat.completions.parse(
        model="qwen3:4b", response_format=Triage,             # the same Pydantic model as before
        messages=[{"role": "user", "content": f"Triage this support email:\n\n{email}"}],
    )
    print("tokens:", completion.usage.prompt_tokens + completion.usage.completion_tokens)
    return completion.choices[0].message.parsed               # None if the model refused
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) from Anthropic. This is the most cited practical article on the topic, and the rest of this path borrows its vocabulary.
   - Read the introduction through "When (and when not) to use agents" carefully. Skim the workflow patterns for now; you will study them in the Workflow Patterns section.
1. Read Simon Willison's [Agents: tools in a loop to achieve a goal](https://simonwillison.net/2025/Sep/18/agents/), a short post explaining why this definition is the one worth using.
1. Read the "What is an agent?" and "When should you build an agent?" sections of OpenAI's [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf). It is useful to see a second provider reach almost the same conclusions.
1. Practice in code: run `refunds.py` and `agent.py` from this lesson using the [cheap model](#/models), then compare them.
   - Run both on the same three emails: the single-lamp email, the two-order email, and an email with no order ID at all. Record each answer and the `usage` numbers in a small table.
   - Write two or three sentences on where each version did better, and why. Then widen `Triage` so the workflow handles a list of order IDs, and run the two-order email again.
1. Practice on paper: write down five tasks from your own life or job (for example, "rename photos by date" or "answer customer emails about refunds"). For each, decide whether it needs no LLM, a single call, a workflow or an agent, and write one sentence on why. Keep this list; you will reuse it in the Project: Workflow or Agent?

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the four stops on the spectrum from plain code to an agent?](#a-spectrum-not-a-switch)
- [What single question tells a workflow apart from an agent?](#who-controls-the-flow)
- [What is the working definition of an agent, and what does each part of it rule out?](#the-working-definition-of-an-agent)
- [In the refund example, what could the agent handle that the workflow couldn't, and what did the workflow guarantee that the agent didn't?](#the-same-task-built-both-ways)
- [Why does a ten-step agent cost more than ten single calls, and why do mistakes compound over many steps?](#what-autonomy-costs)
- [What kind of task earns an agent its place, and what four things should you check first?](#when-an-agent-earns-its-place)
- [When is plain code with no model the right choice?](#start-simple-and-climb)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Lilian Weng's [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) (2023) is an older but influential survey of agent components: planning, memory and tool use. Some of its examples have aged, but the mental model still holds.
