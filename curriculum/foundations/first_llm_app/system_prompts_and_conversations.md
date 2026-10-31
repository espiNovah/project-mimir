### Introduction

A single question and answer is useful, but most AI applications need two more things. They need a way to set the model's role, tone and rules once, rather than repeating them in every message. That's the **system prompt**. And they need to hold a **conversation**, where the model can refer back to what was said earlier.

You might expect the API to remember your conversation for you. It doesn't. In this lesson you'll see why, and you'll write the small amount of code that gives a model a memory of the conversation and a personality.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a system prompt is and how it differs from a user message.
- What makes a good system prompt.
- Why the Messages API is stateless.
- How to build a multi-turn conversation by keeping a message history.
- The rules for ordering user and assistant messages.
- How conversation length affects cost.

### System prompts

The `system` parameter holds instructions that apply to the whole conversation: who the model should be, how it should behave, what it should and shouldn't do. It's separate from the `messages` list. A separate `system` field is how Anthropic's API does it; OpenAI-style APIs put the system prompt inside the list instead, as you'll see in [On other providers](#on-other-providers).

```python
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")  # one place to change models

response = client.messages.create(
    model=MODEL,
    max_tokens=2000,
    system=(
        "You are a patient Python tutor for complete beginners. "
        "Explain ideas with everyday analogies, keep answers under 150 words, "
        "and end each answer with one short question that checks understanding."
    ),
    messages=[{"role": "user", "content": "What is a variable?"}],
)

print("".join(block.text for block in response.content if block.type == "text"))
```

Run it with and without the `system` argument and compare. The question is identical, but the answers will be very different.

What belongs in a system prompt:

- **A role and audience.** "You are a support assistant for a bike shop, talking to customers who aren't mechanics."
- **Behavior and tone.** Length, formality, formatting ("no Markdown, this is shown in a terminal").
- **Rules and boundaries.** What to do when a question is off-topic, or when it doesn't know.
- **Background information** the model needs for every turn, such as shop opening hours.

Write it the way you'd brief a smart new colleague on their first day: clear, specific and with the reasons behind your rules. "Keep answers short because customers read them on their phones" works better than "BE BRIEF." You'll study this craft properly in the Prompt and Context Engineering section.

### The API is stateless

Here's a surprise for most people. Try this:

```python
first = client.messages.create(
    model=MODEL,
    max_tokens=2000,
    messages=[{"role": "user", "content": "My name is Ada. Please remember it."}],
)
second = client.messages.create(
    model=MODEL,
    max_tokens=2000,
    messages=[{"role": "user", "content": "What's my name?"}],
)
```

The second call has no idea your name is Ada. Each request is completely independent, just like the HTTP requests in How the Web Works. The model has no memory between calls; it only sees what's in the request.

So how do chat apps remember? They send **the entire conversation so far** with every new message. The `messages` list alternates between `user` messages (what the person said) and `assistant` messages (what the model replied):

```python
messages = [
    {"role": "user", "content": "My name is Ada. Please remember it."},
    {"role": "assistant", "content": "Nice to meet you, Ada! I'll remember that."},
    {"role": "user", "content": "What's my name?"},
]
```

Send that, and the model answers "Ada," because the earlier turns are right there in its context window. The assistant messages don't even have to be things the model really said; you can write them yourself. That's occasionally useful for showing the model an example of the kind of answer you want.

### A conversation loop

Put those pieces together and you have a working chatbot in about 25 lines:

```python
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")  # one place to change models

SYSTEM_PROMPT = "You are a friendly, concise assistant. Answer in plain text without Markdown."
history: list[dict] = []


def reply_text(response) -> str:
    return "".join(block.text for block in response.content if block.type == "text")


while True:
    user_input = input("you> ").strip()
    if user_input.lower() in {"quit", "exit"}:
        break
    if not user_input:
        continue

    history.append({"role": "user", "content": user_input})
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=history,
    )
    answer = reply_text(response)
    history.append({"role": "assistant", "content": answer})

    print(f"bot> {answer}")
    print(f"     ({response.usage.input_tokens} tokens in, {response.usage.output_tokens} out)")
```

Each time around the loop, you add the user's message to `history`, send the whole history, then add the model's answer. The next request includes everything.

A few rules the `messages` list must follow on Anthropic's API (other providers have similar but not identical rules):

- It must start with a `user` message and end with a `user` message (the one you want answered).
- In between, roles should alternate `user`, `assistant`, `user`, `assistant`.
- The system prompt goes in the `system` parameter, not in the list.

<div class="lesson-note" markdown="1">

#### Why store just the text?

The loop above saves only the text of each reply. That's the simplest approach, and it works well for chat: the model sees everything that was said, and any thinking blocks from earlier turns are left out. When you build agents that use tools, you'll append the full `response.content` (every block, unchanged) instead, because the API needs to see its earlier tool calls and thinking exactly as it produced them.

</div>

### Conversations get more expensive

Watch the `input_tokens` number in the loop as you chat. It grows every turn, because every turn resends everything before it. Turn 1 might send 30 tokens; turn 20 might send 4,000. You're paying for the whole history on every request, and eventually a very long conversation would fill the context window.

For now, that's fine; a learning chat costs fractions of a cent. But it's the reason real applications trim old messages, summarize long conversations or use features like prompt caching (which makes resending the same prefix much cheaper; most major providers offer it, but the details differ). You'll handle all of these in later sections, starting with the Memory and Context Management section of the Agentic Systems path.

### On other providers

Everything important in this lesson carries over unchanged: every major chat API is stateless, every chat app works by resending the whole history, and longer conversations cost more everywhere. What differs is where things go. In the OpenAI Chat Completions format, which OpenAI, Ollama and many other providers accept, there's no separate `system` argument. The system prompt is simply the first message in the list, with the role `"system"` (OpenAI's newer models also accept the name `"developer"` for the same job). Each reply is read from `response.choices[0].message.content`, and you append it to the history as an `assistant` message exactly as before. OpenAI's API is also more relaxed about ordering, so it won't reject two user messages in a row, but keeping the strict user/assistant alternation works everywhere. Here's one turn of the loop against a free local model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility); see OpenAI's [conversation state guide](https://developers.openai.com/api/docs/guides/conversation-state) for the hosted version:

```python
from openai import OpenAI  # uv add openai

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # for OpenAI itself: OpenAI()
history = [{"role": "system", "content": "You are a friendly, concise assistant."}]  # system goes first

history.append({"role": "user", "content": "My name is Ada. What's a variable?"})
response = client.chat.completions.create(model="llama3.2:3b", messages=history)
answer = response.choices[0].message.content
history.append({"role": "assistant", "content": answer})
print(answer, f"({response.usage.prompt_tokens} tokens in)")
```

That conversation guide also describes an option that's specific to OpenAI: its Responses API can store the conversation on OpenAI's servers, so you send only the new message and an ID pointing at the previous one. It's a convenience, not a change in how models work. The model still reads the full history every turn, and you still pay for those input tokens.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the "Multiple conversational turns" section of [Working with the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) to see the official examples of a multi-turn request.
1. Read Anthropic's guide on [giving Claude a role with a system prompt](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/system-prompts).
   - Read the whole page. Pay attention to the examples showing how the same question gets a very different answer depending on the role.
1. Optional: if you enrolled, continue Anthropic Academy's [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api) course.
   - Complete the lessons on multi-turn conversations and system prompts, including any exercises.
1. Build and experiment with the conversation loop from this lesson.
   - Give it a strong personality in the system prompt (a pirate, a strict editor, a cheerful gardening expert) and chat for at least ten turns. Does it stay in character?
   - Tell it a fact about yourself in turn 1 and ask about it in turn 10.
   - Record the `input_tokens` for every turn and make a quick table or chart in your learning journal. Describe the pattern you see.
   - Comment out the line that appends the assistant's answer to `history`. What changes, and why?

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How is a system prompt different from a user message?](#system-prompts)
- [What makes a good system prompt?](#system-prompts)
- [What does it mean that the Messages API is stateless?](#the-api-is-stateless)
- [How do you keep a conversation going, and what are the rules for ordering user and assistant messages?](#a-conversation-loop)
- [Why does each turn of a long conversation cost more than the last?](#conversations-get-more-expensive)
- [Where does the system prompt go in the OpenAI Chat Completions format?](#on-other-providers)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [Messages API reference](https://platform.claude.com/docs/en/api/messages) documents the exact format of `system` and `messages`, including content given as a list of blocks rather than a string.
