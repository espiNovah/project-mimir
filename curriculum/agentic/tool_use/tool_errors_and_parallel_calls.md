### Introduction

Real tools fail. Networks time out, files are missing, and models send arguments that do not make sense. A well-built agent treats these failures as information and recovers; a badly built one crashes or loops forever. Models can also ask for several tools at once, and running those calls together can make your agent much faster. This lesson covers both: how to report errors the model can act on, and how to handle multiple tool calls in a single turn.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The kinds of errors an agent meets: bad arguments, tool failures and timeouts.
- Returning errors as tool results instead of crashing.
- Writing error messages that tell the model what to do next.
- What parallel tool calls are and how to return their results.
- When to run tool calls concurrently and when to run them one at a time.

### Three kinds of failure

When your agent calls a tool, three different things can go wrong, and it helps to name them.

1. **Bad arguments.** The model asked for something your tool can't do: a file name with a path in it, a date in the wrong format, a negative quantity. The tool is fine; the request is wrong.
1. **Tool failures.** The arguments were fine, but the world wasn't. The file was deleted, the API returned a 500 error, the database was locked.
1. **Timeouts.** The tool never answered. A slow website or a stuck query can hang forever unless you put a limit on it.

A fourth category is a bug in your own tool code, such as a `KeyError` you didn't expect. You should fix those, but your agent still shouldn't crash when one happens in the middle of a task.

All four have the same cure: catch the problem in your code, turn it into text, and hand that text back to the model.

### Errors are tool results

In Function Calling you learned the round trip: the model sends a `tool_use` block with an `id`, and you reply with a `tool_result` block that carries the same `tool_use_id`. An error uses exactly the same shape, with one extra field:

```python
{
    "type": "tool_result",
    "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
    "content": "File 'notes.txt' not found. Available files: ideas.md, todo.txt.",
    "is_error": True,
}
```

`is_error: True` tells the model "this call didn't work." (`is_error` is a Claude field. Providers without one, such as OpenAI, take only the text, so make the message itself say it failed.) The model reads the message on its next turn and decides what to do: retry with different arguments, try another tool, or explain the problem to the user. This is the big idea of the lesson. **An exception that crashes your loop ends the task. An exception reported as a tool result is just another observation**, the same way a person who opens the wrong drawer simply opens a different one.

There's a rule here worth memorizing: **every `tool_use` block must get exactly one `tool_result` back.** If the model asked for three things and one failed, you still send three results, one of them marked as an error. If you leave one out, the API rejects your next request.

### Writing errors the model can use

The model can only fix what it understands. Compare these two messages for the same failure:

- `Error`
- `File 'notes.txt' not found. Available files: ideas.md, todo.txt. Pass one of these names.`

The first teaches nothing, so the model will probably guess again, or give up. The second contains everything needed to succeed on the next turn. A good error message answers three questions:

1. **What went wrong?** "File 'notes.txt' not found."
1. **Why, or what is true instead?** "Available files: ideas.md, todo.txt."
1. **What should happen next?** "Pass one of these names."

Write error messages for the model the way you'd write them for a new colleague: specific, short, and pointing at the fix. Never put secrets or full stack traces in them. The model doesn't need your server's file paths, and anything in a tool result may end up in front of the user.

### Validate early, and set time limits

The cheapest error is one you catch before doing any work. Check arguments at the top of the tool, before you call a paid API, write to a database or send a message. "Quantity must be between 1 and 100, got -3" costs nothing; refunding a bad order costs a lot.

Your schema is the first line of validation. Setting `"strict": True` on a tool definition (with `"additionalProperties": False` and a `required` list in the schema) makes the API guarantee that the arguments match your schema's types and fields. Strict tool schemas are a feature of some providers, including Claude and OpenAI; elsewhere, check the arguments' types in your code too. A schema can't express every rule, though. "The file must be inside the sandbox folder" is a rule your code has to check.

**Timeouts are errors too.** Give every tool a time limit and report the timeout as an error result: "search_web timed out after 10 seconds. Try a narrower query." Without a limit, one slow website freezes the whole agent. In Python's `asyncio`, `asyncio.wait_for(some_coroutine, timeout=10)` raises `TimeoutError` when time runs out, which you can catch like any other exception.

### Stopping error loops

Sometimes the model keeps making the same broken call, getting the same error, and trying again. Each attempt costs money and time. Protect against this in two layers:

- **Count consecutive failures per tool.** After, say, three errors in a row from the same tool, stop running it and return a firmer message: "read_file has failed 3 times. Stop using it and tell the user what went wrong." Reset the count when the tool succeeds.
- **Keep your step cap.** The overall limit on loop iterations from The Agent Loop is the last line of defense. Whatever else goes wrong, the loop ends.

A small dictionary is enough for the first layer:

```python
from collections import Counter

failures: Counter[str] = Counter()

def record(tool_name: str, result: dict) -> dict:
    if result.get("is_error"):
        failures[tool_name] += 1
        if failures[tool_name] >= 3:
            result["content"] += f" {tool_name} has now failed 3 times in a row. Stop calling it and tell the user."
    else:
        failures[tool_name] = 0
    return result
```

### Several calls in one turn

Ask an agent "What's the weather in Paris and in London?" and it will often reply with **two** `tool_use` blocks in a single response, one per city. This is called **parallel tool use**: the model noticed the two lookups don't depend on each other and asked for both at once, rather than waiting a whole extra round trip.

Handling this correctly takes three rules:

1. Loop over **every** `tool_use` block in the response, not just the first one.
1. Return **one `tool_result` per call, matched by `tool_use_id`**. The ID is what connects each answer to its question. Order in the list doesn't matter to the API, but a mismatched ID does: if you swap two IDs, the model will believe London's weather belongs to Paris.
1. Put **all** the results in **one** user message. Splitting them across several messages is a common mistake, and it quietly teaches the model to stop making parallel calls. This rule is Claude's; OpenAI-style APIs want one `role: "tool"` message per result instead, all placed straight after the assistant message.

Parallel tool use is on by default with Claude, and its `disable_parallel_tool_use` setting (inside `tool_choice`) limits a turn to one call. Other providers have their own switch, such as OpenAI's `parallel_tool_calls: false`.

### Running calls concurrently

The model *asks* for several calls at once; whether they actually *run* at once is up to you.

**Concurrency** means starting several pieces of work and letting them wait at the same time. Most tool time is waiting: for a web server, a database, a disk. If three lookups each take two seconds, running them one after another takes six seconds; running them concurrently takes about two. Python's `asyncio.gather` starts several coroutines (functions defined with `async def`) together and returns their results in the same order you passed them in.

Concurrency is safe when the calls are **independent and read-only**: fetching pages, reading files, looking things up. Run calls **one at a time** when:

- they have **side effects** (sending an email, charging a card, deleting a file), where you'd rather stop after the first failure than discover three half-finished actions;
- one call **depends on** another, such as "create the folder" and "write a file into it";
- they compete for a **shared resource**, such as a rate-limited API.

If you decide not to run a call, for example because an earlier one in the same turn failed, you still owe it a result. Mark it as an error and say why: "Skipped because create_folder failed. Retry after fixing that."

### Walkthrough: errors and parallel calls

Here is a small agent that reads files from a `sandbox` folder. It validates arguments, reports every failure as an instructive error, enforces a timeout, and runs parallel calls concurrently. Create a project with `uv init`, run `uv add anthropic python-dotenv`, make a `sandbox` folder with a couple of text files in it, and save this as `main.py`:

```python
import asyncio
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
SANDBOX = Path("sandbox")
client = anthropic.AsyncAnthropic()  # the async client, so we can await calls

TOOLS = [{
    "name": "read_file",
    "description": "Read a text file from the sandbox folder. Pass a bare file name such as 'notes.txt'.",
    "input_schema": {"type": "object", "properties": {"name": {"type": "string"}},
                     "required": ["name"], "additionalProperties": False},
    "strict": True,  # the API guarantees `name` exists and is a string
}]

class ToolError(Exception):
    """A failure we expect, with a message written for the model."""
async def read_file(name: str) -> str:
    path = SANDBOX / name
    if path.parent != SANDBOX:  # (1) validate first: no "../secrets" or sub-folders
        raise ToolError(f"'{name}' is not a bare file name. Pass just the name, like 'notes.txt'.")
    if not path.is_file():
        available = ", ".join(sorted(p.name for p in SANDBOX.iterdir()))
        raise ToolError(f"File '{name}' not found. Available files: {available}.")
    return await asyncio.to_thread(path.read_text)  # disk work off the event loop

HANDLERS = {"read_file": read_file}
async def run_one(call) -> dict:
    result = {"type": "tool_result", "tool_use_id": call.id}  # (2) the ID links answer to question
    try:
        result["content"] = await asyncio.wait_for(HANDLERS[call.name](**call.input), timeout=10)
    except ToolError as e:  # (3) expected failure: pass the instructive message on
        result |= {"content": str(e), "is_error": True}
    except TimeoutError:
        result |= {"content": f"{call.name} timed out after 10 seconds.", "is_error": True}
    except Exception as e:  # a bug in our code: report it, don't crash the loop
        result |= {"content": f"Unexpected {type(e).__name__} in {call.name}.", "is_error": True}
    return result

async def main(question: str) -> None:
    messages = [{"role": "user", "content": question}]
    for _ in range(10):  # step cap: the last line of defense
        response = await client.messages.create(
            model=MODEL, max_tokens=16000, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            break
        calls = [b for b in response.content if b.type == "tool_use"]
        results = await asyncio.gather(*(run_one(c) for c in calls))  # (4) run concurrently
        for call, result in zip(calls, results):
            print(f"  {call.name}({call.input}) error={result.get('is_error', False)}")
        messages.append({"role": "user", "content": results})  # (5) all results, one message
    print("".join(b.text for b in response.content if b.type == "text"))

asyncio.run(main("Summarize notes.txt and todo.md, then tell me which is longer."))
```

Walk through the numbered comments:

1. **Validate first.** `SANDBOX / name` builds a path. If the model sends `../.env` or `/etc/passwd`, the parent folder isn't `sandbox`, so the tool refuses before touching the disk. The message says what to pass instead.
1. **The ID links answer to question.** Every result starts life with the `tool_use_id` of the call it answers, so even if results finished in a different order, nothing could get mixed up.
1. **Expected and unexpected errors.** `ToolError` is our own exception type for failures we planned for, and its text is written for the model. The final `except Exception` catches surprises (including an unknown tool name, which raises `KeyError`) and reports them without leaking details. Every path sets `is_error: True`.
1. **Run concurrently.** `asyncio.gather` starts every `run_one` at once and returns results in the same order as `calls`. That's safe here because `read_file` only reads.
1. **One message for all results.** Every result goes back together, satisfying the "one result per call" rule.

Try it with a file name that doesn't exist. In the printed trace you should see `error=True`, then a second call with a real file name, because the error message told the model what was available.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Print the trace while you learn

The `print` inside the loop is a tiny trace: which tools ran, with which arguments, and whether they failed. Agents are hard to debug from the final answer alone. You'll turn this habit into proper tooling in Agent Tracing and Debugging, later in this section.

</div>

### On other providers

The three kinds of failure, instructive error messages, early validation, timeouts, failure counters and the choice between concurrent and one-at-a-time execution are all yours, in your code, on any provider. The "exactly one result per call" rule holds on OpenAI too: an assistant message with `tool_calls` must be followed by a `role: "tool"` message for every `tool_call_id`, or the next request fails. Three things differ. There's no `is_error` field, so the error has to say so in its text. Each result is a separate `role: "tool"` message rather than one user message holding every result. And arguments arrive as a JSON string, which small open models sometimes get wrong, so a parse failure is one more bad-arguments error to send back. OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) covers `parallel_tool_calls` and strict mode, and Ollama's [tool calling page](https://docs.ollama.com/capabilities/tool-calling) shows open models such as Qwen3 making parallel calls. Here is `run_one` for an OpenAI-style call, reusing this lesson's `HANDLERS` and `ToolError`:

```python
import json

async def run_one_openai(call) -> dict:
    result = {"role": "tool", "tool_call_id": call.id}     # one message per call
    try:
        args = json.loads(call.function.arguments)        # a string; may be invalid JSON
        result["content"] = await asyncio.wait_for(HANDLERS[call.function.name](**args), timeout=10)
    except (ToolError, json.JSONDecodeError) as e:
        result["content"] = f"Error: {e}"                 # no is_error: say it in the text
    except TimeoutError:
        result["content"] = f"Error: {call.function.name} timed out after 10 seconds."
    except Exception as e:
        result["content"] = f"Error: unexpected {type(e).__name__} in {call.function.name}."
    return result
# messages.extend(await asyncio.gather(*(run_one_openai(c) for c in reply.tool_calls)))
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls), which explains the exact format of tool results, including the rules for where `tool_result` blocks must go in a message.
   - Read "Handling errors with is_error" closely, including the tip on writing instructive error messages.
1. Read [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) to see how the model decides to batch calls and how to encourage it.
   - Read "Execution semantics" and "Maximizing parallel tool use." Skim the rest.
1. Work through Rings 3 and 4 of the [Tutorial: Build a tool-using agent](https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent), which add multiple tools, parallel calls and error handling to the loop you built in Function Calling.
1. Read the "Coroutines and Tasks" section of the Python docs page on [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html), up to and including "Running Tasks Concurrently," so that `asyncio.gather` is not a mystery.
   - Also read the "Timeouts" part of that page for `asyncio.wait_for`.
1. Practice: build the walkthrough agent with a `sandbox` folder of two or three files, then break it on purpose.
   - Ask it to summarize a file that does not exist. Confirm in the printed trace that it gets an error listing the real files and then picks one.
   - Ask it to read `../main.py`. Confirm the validation refuses it.
   - Add the failure counter from "Stopping error loops," and make `read_file` always raise. Check that the agent stops after three tries instead of using all ten steps.
   - Ask it to compare two files and check that both reads appear in the same step of the trace.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What three kinds of failure can a tool call run into?](#three-kinds-of-failure)
- [Why should a tool failure become a tool result with is_error instead of an exception that stops the loop?](#errors-are-tool-results)
- [What three things should a good error message tell the model?](#writing-errors-the-model-can-use)
- [Why validate arguments before doing any real work, and how should a timeout be reported?](#validate-early-and-set-time-limits)
- [How can you stop a model from retrying the same broken call forever?](#stopping-error-loops)
- [When the model sends several tool_use blocks, how must you return the results?](#several-calls-in-one-turn)
- [When is it safe to run tool calls concurrently, and when should they run one at a time?](#running-calls-concurrently)
