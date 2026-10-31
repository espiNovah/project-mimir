### Introduction

Every agent, from a ten-line script to a coding assistant that runs for an hour, is built around the same small idea: a loop. The model looks at the situation, picks an action, your code carries it out, and the result goes back to the model. Then it happens again. In this lesson you will learn the parts of that loop, where it goes wrong, and, most importantly, how to make it stop.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The think, act, observe cycle and where it came from.
- What the model sees on each turn of the loop.
- Stop conditions: how an agent decides it is done, and how you stop it when it is not.
- Why agents get stuck, repeat themselves or wander off.
- How to design a loop around a clear goal and a way to check progress.

### Think, act, observe

In the last lesson you met a working definition: an agent is a model using tools in a loop to achieve a goal. The loop has three steps, and they repeat until the job is done.

1. **Think.** The model reads everything so far and reasons about what to do next. "The user wants tomorrow's weather. I don't know their city yet, so I should look up their location first."
1. **Act.** The model requests an action, such as calling a tool. A **tool** is just a function your program offers the model, like `get_location()` or `search_web(query)`. The model can't run it. It can only ask for it by name, with arguments.
1. **Observe.** Your code runs the action and adds the result to the conversation: "Location: Nairobi." That result is called an **observation**.

Then the model thinks again, now knowing more than it did a moment ago. It might ask for the forecast, observe "70% chance of rain," and finally answer "Yes, bring an umbrella," at which point the loop ends.

This shape comes from a 2022 paper called ReAct, short for "Reasoning and Acting." A model that only *reasons* can't check facts, so it makes them up. A model that only *acts* calls tools without a plan and loses track of its goal. ReAct showed that interleaving the two works better than either alone: reasoning picks a useful action, and each result grounds the next round of reasoning in real information. Almost every agent since uses this shape.

### The conversation is the state

Here is a fact that surprises many people: the model remembers nothing between API calls. You learned this in the Foundations path when you built a multi-turn chat. Each request is independent, so to have a conversation you send the whole history every time.

Agents work exactly the same way. The **state** of an agent, meaning everything it knows about the task so far, *is* the list of messages. On every turn of the loop your code sends:

- the goal (the user's original request);
- every action the model has requested so far;
- every observation your code sent back.

The model reads that list from the top, every time, and decides the next step. If an observation isn't in the list, the model doesn't know it happened.

This has two consequences. First, agents are easy to inspect: print the message list and you see exactly what the model knew at each point. Second, the list only grows. Every step adds at least two messages, and a tool that returns a whole web page can add thousands of tokens at once. Long-running agents eventually fill their context window, and each loop iteration costs more than the one before it. You'll tackle this in the Memory & Context Management section.

### Your code runs the loop

It's tempting to picture the model as the one "running" the agent. It isn't. The model is a function: messages go in, a reply comes out. The `while` loop, the tool functions and the decision to go around again all live in **your** program.

That's good news, because every pass through the loop goes through code you control. Between the model's request and the actual action you can:

- **log** the request, so you can debug the run later;
- **check** it, for example refusing to delete a file outside a safe folder;
- **ask a human** before doing anything risky, like sending an email;
- **count** steps, tokens and seconds, and stop when a limit is reached.

These are your control points. Agent frameworks hide the loop behind one function call, but they do exactly this underneath.

### A minimal agent loop

Here is a complete agent with one tool and real stop conditions. Its job is to find a secret number between 1 and 100 using a `guess` tool that answers "too low," "too high" or "correct." It's a toy, but it has everything a real agent has: a goal, a tool that gives honest feedback, a loop and limits.

You'll learn the exact format of tool definitions and tool results in the next lesson, Function Calling. For now, focus on the shape of the loop. Set up a project with `uv init agent-loop`, run `uv add anthropic python-dotenv`, make sure your `.env` file holds `ANTHROPIC_API_KEY`, and save this as `main.py`:

```python
import os
import random

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
MAX_STEPS = 10                     # safety stop: the loop can never run forever
client = anthropic.Anthropic()
SECRET = random.randint(1, 100)

TOOLS = [{
    "name": "guess",
    "description": "Guess the secret whole number between 1 and 100. "
                   "Returns 'too low', 'too high' or 'correct'.",
    "input_schema": {
        "type": "object",
        "properties": {"number": {"type": "integer"}},
        "required": ["number"],
    },
}]

def guess(number: int) -> str:     # the real action; the model never sees this code
    if number < SECRET:
        return "too low"
    if number > SECRET:
        return "too high"
    return "correct"

def run_agent(goal: str) -> str:
    messages = [{"role": "user", "content": goal}]          # the state starts as the goal
    for step in range(1, MAX_STEPS + 1):
        response = client.messages.create(                  # THINK
            model=MODEL, max_tokens=4000, tools=TOOLS, messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        print(f"step {step}: stop_reason={response.stop_reason}")

        if response.stop_reason == "end_turn":              # natural stop: model is done
            return "".join(b.text for b in response.content if b.type == "text")
        if response.stop_reason != "tool_use":              # max_tokens, refusal, ...
            return f"Stopped early: {response.stop_reason}"

        results = []
        for block in response.content:                      # ACT
            if block.type == "tool_use":
                observation = guess(int(block.input["number"]))
                print(f"  guess({block.input['number']}) -> {observation}")
                results.append({"type": "tool_result",
                                "tool_use_id": block.id, "content": observation})
        messages.append({"role": "user", "content": results})  # OBSERVE
    return f"Stopped: reached the {MAX_STEPS}-step limit without finishing."

print(run_agent("Find the secret number with the guess tool, then tell me what it is."))
```

Run it with `uv run main.py`. You should see something like this:

```text
step 1: stop_reason=tool_use
  guess(50) -> too high
step 2: stop_reason=tool_use
  guess(25) -> too low
step 3: stop_reason=tool_use
  guess(37) -> correct
step 4: stop_reason=end_turn
The secret number is 37.
```

Walk through it piece by piece:

- **`MAX_STEPS`** is set before anything else. A smart guesser needs at most 7 guesses for 100 numbers, so 10 leaves room without allowing a runaway.
- **`messages`** starts as just the goal. Everything the agent learns gets appended to it. This list is the agent's entire memory.
- **`for step in range(...)`** is the loop, and it's a `for`, not a `while True`. That one choice means the step limit can't be forgotten: when the range runs out, the loop ends.
- **Think:** `client.messages.create` sends the whole history plus the tool list. Notice that the reply is appended *whole*, as `response.content`, not just its text. It may contain thinking blocks (a Claude feature: the model's reasoning, which must be passed back unchanged) and tool requests, and the model needs to see all of it on the next turn.
- **`stop_reason`** is how the API tells you *why* the model stopped writing. `"tool_use"` means "I'm waiting for a tool result." `"end_turn"` means "I'm finished." Anything else, such as `"max_tokens"` (the reply was cut off) or `"refusal"` (the model declined), means something unusual happened, so the code stops rather than guessing what to do. These field and value names are Claude's; other providers have the same signal under other names, as you'll see in "On other providers" below.
- **Act:** the code finds each `tool_use` block (Claude's name for a tool request inside a reply), runs the real `guess` function and prints what happened. Printing every step costs nothing and is how you'll spot most bugs.
- **Observe:** the results go back as a new user message, each one tagged with the ID of the request it answers. Then the loop goes around again.
- **The last `return`** only runs if the range is exhausted. It's the safety stop, and it returns a clear message instead of crashing.

<div class="lesson-note lesson-note--tip" markdown="1">

#### See the safety stop fire

Change `MAX_STEPS` to `3` and run the script a few times. Most runs will end with the step-limit message. Testing that your limits actually work is as important as testing that the agent succeeds.

</div>

### Stop conditions

An agent loop needs a way to end. There are two kinds of stop conditions, and you need both.

The **natural stop** is when the model says it's finished. In the Claude API, that's a reply with `stop_reason` set to `"end_turn"` and no tool requests. Other providers use different names, but every API has an equivalent signal. The natural stop is what you hope for on every run.

The **safety stops** are limits *you* enforce no matter what the model thinks:

- **A step cap:** a maximum number of loop iterations, like `MAX_STEPS` above.
- **A token or cost budget:** every response has a `usage` field with token counts. Add them up as you go and stop when the total passes a limit.
- **A time limit:** record the start time and stop after, say, five minutes.
- **A human saying "stop":** in an interactive app, a cancel button that ends the loop between steps.

Why do you need safety stops if the model knows when it's done? Because sometimes it doesn't. It might keep searching for something that doesn't exist, or retry a broken tool forever, and a loop with no cap can burn through a budget overnight. **Never ship a loop without at least a step cap.** When a safety stop fires, end gracefully: say which limit was hit and report what was achieved so far, so the run isn't wasted.

The odd cases matter too. A `"max_tokens"` stop in the middle of a tool request means the request was cut off, so running it would be a mistake. Treat every stop reason you don't explicitly handle as "stop and report," never as "keep going."

### Why agents get stuck

Agents fail in a handful of recognizable ways. Learn their names, because you'll see all of them.

- **Repeating the same action.** The model searches for "Nairobi weather," gets a result it doesn't like, and searches for exactly the same thing again. And again.
- **Bad arguments, over and over.** The model calls a tool with a misspelled file name, gets an unhelpful error, and tries again with the same mistake.
- **Declaring success too early.** The model says "Done! The tests pass" without ever running the tests.
- **Drifting from the goal.** Ten steps in, the model is fixing something interesting but unrelated, and the original request is buried far up the message list.

What these have in common is missing or weak **ground truth**: real, checkable information about progress. The guessing game works because every observation is honest and useful: "too high" tells the model exactly which half of the range to drop. A tool that just says "error" gives the model nothing to reason about, so it guesses, and each wrong step adds confusing history that makes the next one worse.

So when an agent gets stuck, look at the observations before you blame the model. Would *you* know what to do next if that was all you could see? Printing every step is the cheapest way to find out. Later in this section, Agent Tracing and Debugging turns those prints into proper trace files.

### Designing a good loop

Writing the loop is easy. Designing a *productive* one is a real skill, and it mostly happens before you write any code. A good loop has four things.

1. **A clear goal.** "Make the failing test in `test_cart.py` pass" is a goal. "Improve the code" isn't, because there's no way to know when it's met.
1. **Tools that give useful feedback.** Each tool should return information the model can act on: what happened, what went wrong and what the options are. "File not found. Files in this folder: `notes.md`, `todo.md`" is far better than "Error."
1. **A safe environment to act in.** If the agent can change things, let it change things that don't matter: a copy of the project, a test database or a container. Then a mistake costs a retry, not a disaster.
1. **A finish line the agent can check for itself.** The best goals come with a test: run the test suite, check that the file exists, compare the total with a known answer. When the agent can verify its own work, it stops claiming success too early.

The guessing game ticks every box: the goal is precise, the tool's feedback is perfect, guessing is harmless and "correct" is an unambiguous finish line. Real tasks are messier, but these four questions are the ones to ask every time you design an agent.

### On other providers

Everything in this lesson except the field names carries over unchanged: the think, act, observe cycle, the message list as the agent's whole state, your code running the loop, the step cap and the other safety stops. On OpenAI's Chat Completions API, and on every server that copies it, the loop maps like this. The reply is `choices[0].message`, and you append it to `messages` whole, just as you append `response.content` here. Tool requests arrive in `message.tool_calls` instead of `tool_use` blocks, and each call's arguments are a JSON *string* you parse with `json.loads`. Each observation goes back as its own `{"role": "tool", "tool_call_id": ..., "content": ...}` message instead of a `tool_result` block inside one user message. The stop signal is `finish_reason`: `"tool_calls"` plays the part of `"tool_use"`, `"stop"` the part of `"end_turn"`, and `"length"` the part of `"max_tokens"`, while token counts are `usage.prompt_tokens` and `usage.completion_tokens`. OpenAI's newer Responses API renames the pieces again (`function_call` and `function_call_output` items) but runs the same loop, as its [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) shows. Here is the guessing-game loop against a free open model, Qwen3, running on your machine through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility); it reuses `MAX_STEPS` and `guess` from `main.py`:

```python
import json
from openai import OpenAI  # uv add openai
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # drop both for OpenAI itself
TOOLS = [{"type": "function", "function": {"name": "guess", "description": "Guess the secret "
          "whole number between 1 and 100. Returns 'too low', 'too high' or 'correct'.",
          "parameters": {"type": "object", "properties": {"number": {"type": "integer"}}, "required": ["number"]}}}]
messages = [{"role": "user", "content": "Find the secret number with the guess tool, then tell me what it is."}]
for step in range(1, MAX_STEPS + 1):                      # the same safety stop
    reply = client.chat.completions.create(model="qwen3:4b", messages=messages, tools=TOOLS).choices[0].message
    messages.append(reply)                                # THINK: keep the whole reply
    if not reply.tool_calls:                              # finish_reason "stop" (done) or "length" (cut off)
        break
    for call in reply.tool_calls:                         # ACT, then OBSERVE: one "tool" message per call
        observation = guess(int(json.loads(call.function.arguments)["number"]))
        messages.append({"role": "tool", "tool_call_id": call.id, "content": observation})
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Simon Willison's [Designing agentic loops](https://simonwillison.net/2025/Sep/30/designing-agentic-loops/). It is a practical look at what makes a loop productive: clear goals, the right tools and a safe place to run them.
   - Pay attention to his points about running agents in a safe environment ("YOLO mode") and about giving the agent a way to test its own work.
1. Read the abstract and introduction of [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629). You do not need to follow the experiments. The goal is to see where the think, act, observe pattern comes from.
   - Look at the figure comparing "Reason only," "Act only" and "ReAct" and notice what each one gets wrong.
1. Reread the "Agents" section of Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) and note every stop condition and checkpoint it mentions.
1. Practice on paper: trace an agent loop for the goal "Find out tomorrow's weather in my city and tell me whether to bring an umbrella." Write each think, act and observe step. Then write down two things that could make the loop run forever, and the stop condition that would catch each one.
1. Practice in code: run the guessing-game agent from this lesson, then extend it.
   - Add a token budget as a second safety stop. Add up `response.usage.input_tokens` and `response.usage.output_tokens` on every step, and stop gracefully when the total passes 20,000.
   - Make the tool unhelpful: change `guess` to return `"wrong"` instead of "too low" or "too high." Run it and watch what happens to the number of steps. Write two sentences connecting what you see to ground truth.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What happens in each of the think, act and observe steps?](#think-act-observe)
- [Why does your code send the whole message history on every turn of the loop?](#the-conversation-is-the-state)
- [Who actually runs the tools and decides whether to go around again, the model or your code?](#your-code-runs-the-loop)
- [What do the stop reasons "tool_use" and "end_turn" mean, and what should the loop do with any other stop reason?](#a-minimal-agent-loop)
- [What is the difference between a natural stop and a safety stop, and which safety stop should every loop have?](#stop-conditions)
- [Name three common ways agents get stuck. What do they have in common?](#why-agents-get-stuck)
- [What four things does a well-designed agent loop have?](#designing-a-good-loop)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Lilian Weng's [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) covers ReAct alongside other early planning techniques, with clear diagrams.
