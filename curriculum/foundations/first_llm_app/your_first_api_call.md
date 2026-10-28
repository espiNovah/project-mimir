### Introduction

This is the moment the whole Foundations path has been building toward. You know Python, you know how HTTP requests work, you know how to keep a secret out of Git, and you have a mental model of what a language model does. Now you'll put them together and get a model to answer you from your own code.

Every AI application, from a simple chatbot to a team of autonomous agents, is built on the call you'll make in this lesson. Get comfortable with it and with the response it returns, because you'll make it thousands of times.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to create a Claude API account and API key, and what it costs.
- How to install and configure the official Python SDK.
- How to send a message with `client.messages.create`.
- The structure of a response: content blocks, stop reason and usage.
- How the SDK call maps onto the raw HTTP request underneath.
- Free alternatives for running models locally.

### Getting an API key

This curriculum uses Claude for its examples, but every major provider (OpenAI, Google, Mistral and others) works the same way: create an account, add a payment method or credit, create a key, and call an HTTP API. The code differs in small details, and the ideas transfer directly.

1. Go to the [Claude Console](https://platform.claude.com/) and create an account.
1. New accounts usually receive a small amount of free credit to try the API. When it runs out, add a small amount of prepaid credit in the billing settings. API usage is billed separately from any Claude chat subscription.
1. On the API keys page, click **Create key**, give it a name like `mimir-learning`, and select a workspace (the default workspace is fine). Copy the key, which starts with `sk-ant-`. The Console only shows it once.
1. Store it exactly as you learned in API Keys and Secrets: in a `.env` file that's listed in `.gitignore`.

```text
# .env
ANTHROPIC_API_KEY=sk-ant-api03-...your-key...
```

How much will this cost? Very little, if you use a small model. Prices are quoted per million tokens (MTok). At the time of writing, Claude Haiku 5.5 costs $0.10 per million input tokens and $0.50 per million output tokens for prompts up to 100,000 tokens. A typical short question and answer uses maybe 50 input tokens and 300 output tokens, which works out to well under a tenth of a cent. A few dollars of credit will comfortably last through this whole section. Check the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) for current numbers.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Can't pay? Run a model locally for free

[Ollama](https://ollama.com/) runs open models on your own computer at no cost, and it can imitate the Claude Messages API. Install it, run `ollama pull llama3.2:3b`, and then create your client with `anthropic.Anthropic(base_url="http://localhost:11434", api_key="ollama")` and use `model="llama3.2:3b"`. Almost all of the code in this section then works unchanged. Small local models are much less capable than hosted ones and need a reasonably modern computer, but they're perfect for learning. See [Ollama's Anthropic compatibility guide](https://docs.ollama.com/api/anthropic-compatibility) for details.

</div>

### Your first call

Create a project and install the official SDK (software development kit: a library that wraps the HTTP API in friendly Python functions):

```bash
uv init hello-claude
cd hello-claude
uv add anthropic python-dotenv
```

Make sure your `.env` file is in this folder and `.env` is in `.gitignore`. Then put this in `main.py`:

```python
import anthropic
from dotenv import load_dotenv

load_dotenv()                    # copies ANTHROPIC_API_KEY from .env into the environment
client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY automatically

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=2000,
    messages=[
        {"role": "user", "content": "Explain what an API is in two sentences."},
    ],
)

for block in response.content:
    if block.type == "text":
        print(block.text)
```

Run it with `uv run main.py`. If you see two sentences about APIs, congratulations: you've built your first LLM app.

The three required arguments:

- `model` picks which model answers. Smaller, cheaper models like Haiku are fast and great for most simple tasks; larger ones like Sonnet and Opus are more capable and more expensive. The [models overview](https://platform.claude.com/docs/en/about-claude/models/overview) lists the current ones and their exact IDs.
- `max_tokens` caps how many tokens the response may contain, including any thinking. It's a safety limit, not a target: the model stops when it's finished, or when it hits this cap.
- `messages` is a list of messages, each with a `role` (`"user"` or `"assistant"`) and `content`. Here there's just one user message. You'll build longer lists in the next lesson.

### Reading the response

Add `print(response)` to see the whole object. Converted to JSON, it looks like this (shortened):

```json
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "model": "claude-haiku-5-5",
  "content": [
    {"type": "thinking", "thinking": "", "signature": "EqQBCgIYAh..."},
    {"type": "text", "text": "An API is a set of rules that lets one program..."}
  ],
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 16, "output_tokens": 212}
}
```

- **`content`** is a *list* of **content blocks**, not a single string. A `text` block holds the answer. Current Claude models think adaptively (see Reasoning Models), so the list may begin with a `thinking` block, and on other requests it won't. That's why the code loops over the blocks and checks `block.type` rather than reaching for `response.content[0].text`, which would break whenever a thinking block comes first. Later you'll meet other block types, such as `tool_use` for agents.
- **`stop_reason`** says why the model stopped. `"end_turn"` means it finished naturally. `"max_tokens"` means it ran out of room and the answer is cut off, so you should raise `max_tokens` or ask for something shorter.
- **`usage`** reports exactly how many tokens you were billed for. `output_tokens` includes any thinking. You'll use these numbers to calculate costs in Tokens, Cost and Rate Limits.

### What's underneath

The SDK is a convenience. Underneath, it's sending exactly the kind of `POST` request you studied in the Web section. You can make the same call with `curl`, which is a great way to see that there's no magic here:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-haiku-5-5",
    "max_tokens": 2000,
    "messages": [{"role": "user", "content": "Explain what an API is in two sentences."}]
  }'
```

A URL, a method, headers carrying your key and the API version, and a JSON body. The response is the JSON shown above. (For `curl`, the key needs to be a real environment variable: run `export ANTHROPIC_API_KEY=...` in your terminal first, or `source .env` with care.)

<div class="lesson-note lesson-note--warning" markdown="1">

#### Never share your key while asking for help

When a call fails and you paste your code or terminal output into a forum or chat to ask for help, check that your key isn't in it. A key in a screenshot is just as leaked as a key on GitHub.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through Anthropic's [Get started guide](https://platform.claude.com/docs/en/get-started) using the Python tab.
   - It installs the SDK with `pip`; use `uv add anthropic` in your project instead.
   - The guide uses a larger model in its example. Use the [cheap model](#/models) while you're learning to keep costs tiny.
1. Read the "Basic request and response" section of [Working with the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) to see the full request and response shapes. You'll read the rest of this page in the next lesson.
1. Skim the [models overview](https://platform.claude.com/docs/en/about-claude/models/overview) and note the current model families, their relative speed and cost, and their context window sizes.
1. Optional: enroll in Anthropic Academy's free [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api) course. It requires a free Skilljar account, so it's optional; this lesson and the [Claude API docs](https://platform.claude.com/docs/en/get-started) cover everything you need. If you take it, you'll use it throughout this section.
   - Complete the opening lessons that cover setting up and making your first request. Stop when the course moves on to multi-turn conversations; that's the next lesson here.
1. Experiment with your `main.py`:
   - Print `response.stop_reason` and `response.usage`. Then set `max_tokens=20` and ask for a long story. What happens to `stop_reason` and to the text?
   - Run the same prompt three times. Are the answers identical? Connect what you see to the Context Windows and Sampling lesson.
   - Change `model` to the [capable model](#/models) and compare the answer, the speed and the `usage` numbers.
   - Make the same call with `curl` and find each field from this lesson in the raw JSON.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Where should your API key live, and how does the SDK find it?](#getting-an-api-key)
- [What do you have to pass to client.messages.create?](#your-first-call)
- [Why is a response's content a list of blocks rather than a single string?](#reading-the-response)
- [What do stop_reason and usage tell you about a response?](#reading-the-response)
- [What HTTP request does the SDK send for you?](#what-s-underneath)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [Messages API reference](https://platform.claude.com/docs/en/api/messages) lists every parameter and response field.
- The [Python SDK documentation](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) covers installation, async usage, streaming, error handling, retries and timeouts.
- [Ollama's quickstart](https://docs.ollama.com/quickstart) walks through installing Ollama and running your first local model.
