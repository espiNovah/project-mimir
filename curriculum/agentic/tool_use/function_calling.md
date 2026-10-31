### Introduction

A language model on its own can only produce text. It cannot check the weather, read a file or send an email. **Function calling** (also called **tool use**) is how you give it those abilities: you describe functions your code can run, the model replies with a structured request to run one, and your code does the work and reports back. This is the "act" step of the agent loop, and it is the mechanism underneath every agent you will build in this path.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a tool definition contains and why the description matters so much.
- The request, tool call, tool result round trip.
- How to tell when the model wants a tool and when it is finished.
- The difference between client tools (your code runs them) and server tools (the provider runs them).
- Forcing or forbidding tool use with tool choice settings.
- How the same idea looks across different providers.

### What a tool definition contains

In The Agent Loop you used a `guess` tool without looking closely at how it was described. Now it's time to look. A tool definition has three parts:

- **`name`**: what the model writes when it wants the tool, like `get_weather`. Use lowercase letters, digits and underscores.
- **`description`**: plain English explaining what the tool does, when to use it and what it returns.
- **`input_schema`**: the arguments the tool accepts, written in **JSON Schema**. You used JSON Schema in the Structured Outputs section to describe the shape of data you wanted back. Here it describes the shape of the arguments the model must send.

```python
weather_tool = {
    "name": "get_weather",
    "description": "Get the current weather for one city. Use this whenever the user "
                   "asks about weather, temperature or rain. Returns a short summary.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, for example 'Lagos'"},
        },
        "required": ["city"],
    },
}
```

The key thing to understand is that **the model never sees your Python code.** It doesn't know your `get_weather` function calls a weather service, or that it fails when the city is misspelled. All it knows is this definition. The definition is effectively a prompt, so everything you learned about prompting applies. A vague description like "weather tool" leaves the model guessing when to use it. A clear one that says when to use the tool and what comes back gets it used correctly. You'll go much deeper on this in the next lesson, Designing Tools for Agents.

### The tool use round trip

Using a tool takes two API calls, not one. Here is the whole round trip, step by step:

1. You send the user's message **plus the list of tool definitions**.
1. The model decides a tool would help. Instead of an answer, its reply contains a **`tool_use` block**: the tool's name, the arguments as a dictionary and a unique ID such as `toolu_01A09q90qw90lq917835lq9`. The reply's `stop_reason` is `"tool_use"`. (`tool_use`, `tool_result` and `stop_reason` are Claude's names. Other providers carry the same information under different names, covered in "On other providers" below.)
1. Your code reads that block and calls your real function. **The model doesn't run anything.** Your code decides whether to run the tool at all.
1. You append the model's reply to the conversation, then add a **user** message containing a **`tool_result` block**. It carries the same ID as the request and the tool's output, usually as text.
1. You call the API again with the longer conversation. Now the model can read the result and answer.

Here is that round trip as a complete script. Set up a project with `uv add anthropic python-dotenv`, keep `ANTHROPIC_API_KEY` in `.env`, and save this as `weather.py`:

```python
import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

weather_tool = {                                 # 1. the only part the model sees
    "name": "get_weather",
    "description": "Get the current weather for one city. Use this whenever the user "
                   "asks about weather, temperature or rain. Returns a short summary.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"],
    },
}

def get_weather(city: str) -> str:               # a fake; real code would call an API
    fake = {"lagos": "31°C, humid, 60% chance of rain", "oslo": "4°C, clear skies"}
    return fake.get(city.lower(), f"No weather data for {city}.")

messages = [{"role": "user", "content": "Do I need an umbrella in Lagos today?"}]

# 2. First call: the model asks for a tool instead of answering.
first = client.messages.create(model=MODEL, max_tokens=4000,
                               tools=[weather_tool], messages=messages)
print("first stop_reason:", first.stop_reason)
if first.stop_reason != "tool_use":
    raise SystemExit("The model answered without using the tool.")

# 3. Keep the WHOLE reply (thinking, text and tool_use blocks) in the history.
messages.append({"role": "assistant", "content": first.content})

# 4. Run each requested tool and answer it by ID, all in ONE user message.
results = []
for block in first.content:
    if block.type == "tool_use":
        print("tool_use:", block.id, block.name, json.dumps(block.input))
        output = get_weather(block.input["city"])
        results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
messages.append({"role": "user", "content": results})

# 5. Second call: same tools, longer history. Now the model can answer.
final = client.messages.create(model=MODEL, max_tokens=4000,
                               tools=[weather_tool], messages=messages)
print("final stop_reason:", final.stop_reason)
print("".join(b.text for b in final.content if b.type == "text"))
```

Run it with `uv run weather.py`:

```text
first stop_reason: tool_use
tool_use: toolu_01A09q90qw90lq917835lq9 get_weather {"city": "Lagos"}
final stop_reason: end_turn
Yes, take an umbrella. It's 31°C and humid in Lagos with a 60% chance of rain.
```

By the second call, the `messages` list looks like this (shortened, and converted to JSON):

```json
[
  {"role": "user", "content": "Do I need an umbrella in Lagos today?"},
  {"role": "assistant", "content": [
    {"type": "thinking", "thinking": "", "signature": "EqQBCgIYAh..."},
    {"type": "tool_use", "id": "toolu_01A09q90qw90lq917835lq9",
     "name": "get_weather", "input": {"city": "Lagos"}}
  ]},
  {"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
     "content": "31°C, humid, 60% chance of rain"}
  ]}
]
```

A few details in the script are easy to get wrong:

- **The tools go on both calls.** The second call needs `tools=[weather_tool]` too, because the history mentions a tool and the model may want to call it again.
- **Append `first.content`, not just its text.** The reply may include thinking blocks and text alongside the `tool_use` block, and the API expects to see the assistant turn exactly as it was sent.
- **The IDs must match.** Every `tool_use_id` in your results must be the `id` of a `tool_use` block in the previous assistant message. That's how the model knows which result belongs to which request.
- **One result per request, in one message.** The model can ask for several tools in a single reply, for example the weather in Lagos *and* Oslo. That's called **parallel tool use**. Loop over all the blocks, as the script does, and put every result in the same user message. You'll handle errors and parallel calls properly in Tool Errors and Parallel Calls.
- **The result is a string.** If your function returns a dictionary, turn it into text with `json.dumps` first.

### Knowing when the model is finished

The `stop_reason` field tells you what to do next:

- **`"tool_use"`**: the model is waiting for one or more tool results. Run them, send them back and call again.
- **`"end_turn"`**: the model has given its final answer. Stop.
- **Anything else**, such as `"max_tokens"`, means something unusual happened. Don't run a tool request that might have been cut off.

Put the round trip from the script inside a loop that repeats while `stop_reason` is `"tool_use"`, and you have the agent loop from The Agent Loop. That's genuinely all an agent is underneath: this exchange, repeated, with a step cap on top. The cap still matters. A model that keeps asking for tools would otherwise keep your loop running forever.

### Client tools and server tools

Everything above uses **client tools**: you write the definition, and your code runs the function. Most tools you build will be like this, because only your code can reach your database, your files or your company's internal APIs.

Some providers also offer **server tools**, which run on the provider's own machines. Claude, for example, offers web search, web fetch and code execution as server tools. You add them to the `tools` list by type, and the provider runs them and returns the results inside the same response. There's no `tool_result` for you to write, because there's no function on your side to call.

Server tools are convenient: you get web search without signing up for a search API. The trade-offs are that they cost extra per use, you can't see or change how they work, and each provider offers a different set with different names. Server tools are provider-specific, while client tools work everywhere. In the Agent Loop From Scratch project, you'll be allowed to use either for web search.

### Controlling tool choice

By default, the model decides whether to call a tool at all. That setting is called `auto`, and it's what you want almost all of the time. The `tool_choice` parameter lets you change it:

- **`{"type": "auto"}`**: the model may call any tool, or none (the default).
- **`{"type": "any"}`**: the model must call *some* tool.
- **`{"type": "tool", "name": "get_weather"}`**: the model must call that specific tool.
- **`{"type": "none"}`**: the model may not call tools on this request, even though they're defined.

For years, forcing a specific tool was the standard trick for getting structured data out of a model: define a tool whose schema is the data you want, force the model to call it, and read the arguments. It still works on many models, but several newer Claude models, including the [capable model](#/models), reject `any` and `tool` with an error. You already know the better options from the Structured Outputs section: use native structured outputs when you just want data, or use `auto`, name the tool in your prompt ("Use the get_weather tool"), set `"strict": True` on the tool definition so its arguments always match the schema (strict tool schemas exist on Claude and OpenAI, but not on every provider or open-model server, so validate arguments in your code there), and check whether a `tool_use` block actually came back. `none` works everywhere, and it's useful when you want a final summary without the model wandering off to call more tools.

### On other providers

Every major provider works this way. OpenAI, Google Gemini and open-model servers such as Ollama use slightly different field names, but the shape is identical: definitions in, structured call out, result back in. In OpenAI's Chat Completions format, which most open-model servers copy, a tool definition is wrapped in `{"type": "function", "function": {...}}` and its JSON Schema goes in `parameters` instead of `input_schema`. Requests arrive in the reply's `tool_calls` list with arguments as a JSON *string*, each result goes back as its own `{"role": "tool", "tool_call_id": ...}` message instead of a `tool_result` block, and `finish_reason` is `"tool_calls"` where Claude's `stop_reason` is `"tool_use"`. Tool choice exists there too, spelled `"auto"`, `"required"` (Claude's `any`), `{"type": "function", ...}` for one named tool, and `"none"`, and `strict: true` goes inside the `function` object. Server tools differ the most: OpenAI calls them built-in tools, such as its own web search, and each provider offers a different set, while open models running locally have none, so you write those tools yourself. OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) covers all of this, and Ollama's [tool calling page](https://docs.ollama.com/capabilities/tool-calling) shows open models such as Qwen3 doing the same round trip on your own machine. Here is this lesson's tool and round trip in that format:

```python
openai_weather_tool = {"type": "function", "function": {    # an extra wrapper object
    "name": "get_weather",
    "description": weather_tool["description"],
    "parameters": weather_tool["input_schema"],             # the same JSON Schema, a new key
}}
# reply = client.chat.completions.create(model=..., messages=messages,
#                                        tools=[openai_weather_tool]).choices[0].message
# messages.append(reply)
# for call in reply.tool_calls or []:                       # not tool_use blocks
#     args = json.loads(call.function.arguments)            # a JSON string, not a dict
#     messages.append({"role": "tool", "tool_call_id": call.id,
#                      "content": get_weather(**args)})     # one message per result
```

Once you understand one provider's round trip, learning another takes half an hour with its docs: the names change, but the loop doesn't.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) for the big picture of how tool calls flow between your code and the model.
   - Focus on the difference between client tools and server tools.
1. Read [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) to learn exactly what goes into a tool definition.
   - Read the sections on tool definitions and on forcing tool use with `tool_choice`. Skim the rest. Remember that some newer models reject forced tool choice, as explained in this lesson.
1. Work through Rings 1 and 2 of the [Tutorial: Build a tool-using agent](https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent). Type the code yourself rather than copying it, and run it.
   - Ring 1 is a single tool call; Ring 2 turns it into a loop. Stop there for now. You will come back for later rings in the next two lessons.
   - Use the [cheap model](#/models) instead of the model in the tutorial to keep costs low.
1. Skim OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) and list three differences in naming between its format and Claude's. Seeing a second provider makes it clear which parts are universal.
1. Practice: write a tool called `get_word_length` that returns the number of letters in a word. Ask the model "How many letters are in 'strawberry' and 'banana' combined?" Print the raw `tool_use` blocks it sends and the final answer.
   - Start from the round-trip script in this lesson, but wrap it in a loop with a step cap, as in The Agent Loop, because the model may need more than one round.
   - Did the model ask for both words in one reply (parallel tool use) or one at a time? Did it add the numbers itself or ask you to? Write down what you saw.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the three parts of a tool definition, and why does the description matter so much?](#what-a-tool-definition-contains)
- [Who actually runs a tool, the model or your code?](#the-tool-use-round-trip)
- [What goes into a tool_result block, and how does the model know which request it answers?](#the-tool-use-round-trip)
- [Which stop reason means the model wants a tool, and which means it is finished?](#knowing-when-the-model-is-finished)
- [What is the difference between a client tool and a server tool?](#client-tools-and-server-tools)
- [What are the tool choice options, and what should you do instead of forcing a tool on models that reject it?](#controlling-tool-choice)
- [What stays the same about function calling across different providers?](#on-other-providers)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) shows every shape a `tool_result` can take, including errors and images.
- [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) lists every `stop_reason` value and what your code should do with each one.
