### Introduction

Run your chatbot from the last lesson and ask for something long, like a short story. You type your message, and then... nothing happens for several seconds, until the whole answer appears at once. It feels broken, even though it isn't.

Remember from Transformers and Attention that models generate text one token at a time. **Streaming** lets you show those tokens as they're produced, so text starts appearing within a fraction of a second and flows onto the screen as the model writes. It's why every chat app you've used feels responsive. In this lesson you'll add it to your own code, and see what's happening underneath.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why streaming improves the experience of using an LLM app.
- The difference between total response time and time to first token.
- How to stream with the SDK's `messages.stream` helper.
- How to get the complete message, with usage, at the end of a stream.
- What server-sent events are and the event types in a stream.
- How errors show up during a stream.

### Why stream?

Two measurements matter when someone is waiting for a model:

- **Time to first token (TTFT):** how long until the first piece of text appears.
- **Total time:** how long until the response is complete.

Streaming doesn't make the total time any shorter. The model takes just as long to write a 500-word answer either way. What changes is TTFT: instead of staring at a blank screen for 10 seconds, the user sees text after half a second and reads along as it's written. That makes an enormous difference to how fast an app *feels*.

There's a second, practical reason. Very long responses can take minutes, and long-running HTTP requests that send nothing back can hit timeouts along the way. A stream sends data continuously, which avoids that problem. For very large outputs, the Anthropic SDK actually requires streaming.

### Streaming with the SDK

The Python SDK's `client.messages.stream()` takes the same arguments as `messages.create()`, but you use it in a `with` block and loop over the text as it arrives:

```python
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-haiku-5-5",
    max_tokens=2000,
    messages=[{"role": "user", "content": "Write a four-line poem about debugging."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    final = stream.get_final_message()

print()
print(f"stop_reason={final.stop_reason}, "
      f"input_tokens={final.usage.input_tokens}, output_tokens={final.usage.output_tokens}")
```

The important details:

- `stream.text_stream` yields small chunks of text (often a word or part of a word) as soon as they arrive. It only yields *text*, so you don't have to worry about thinking blocks here.
- `print(text, end="", flush=True)` prints each chunk without a newline, and `flush=True` forces it onto the screen immediately instead of waiting for Python's output buffer to fill up.
- `stream.get_final_message()` waits for the stream to finish and returns the same complete message object that `messages.create()` would have returned, with `content`, `stop_reason` and `usage`. That's how you get token counts from a streamed response.
- The `with` block makes sure the connection is closed properly, even if your code raises an exception halfway through.

### Streaming in a conversation

To use streaming in a chatbot, you need the full reply text to add to your history. You can collect the chunks as you print them, or take the text from the final message:

```python
def stream_reply(history: list[dict], system: str) -> str:
    with client.messages.stream(
        model="claude-haiku-5-5",
        max_tokens=2000,
        system=system,
        messages=history,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        final = stream.get_final_message()
    print()
    return "".join(block.text for block in final.content if block.type == "text")
```

Swap this in for the `messages.create()` call in your conversation loop from System Prompts and Conversations, append the returned text to `history` as before, and your chatbot streams.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Let the user interrupt

When a model starts writing something long that the user doesn't want, they'll press Ctrl+C. That raises `KeyboardInterrupt` in the middle of your loop. Catch it around the streaming call, print a short note like "[stopped]", and return to the prompt instead of crashing. Decide whether to keep the partial answer in the history or drop it, and be consistent.

</div>

### What's underneath: server-sent events

Streaming uses a standard web format called **server-sent events (SSE)**, and every major provider uses it. The event names below are Anthropic's own; other providers use different names, as [On other providers](#on-other-providers) shows. Instead of one JSON response, the server keeps the HTTP connection open and sends a series of small events, each with a name and a JSON payload. Add `"stream": true` to the `curl` request from Your First API Call and you'll see them arrive:

```text
event: message_start
data: {"type": "message_start", "message": {"id": "msg_...", "content": [], "usage": {"input_tokens": 25, "output_tokens": 1}}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "!"}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 15}}

event: message_stop
data: {"type": "message_stop"}
```

On Anthropic's API, the flow is always the same: a `message_start`, then for each content block a `content_block_start`, many `content_block_delta` events carrying the new text, and a `content_block_stop`. Then a `message_delta` with the stop reason and final usage, and a `message_stop`. You may also see `ping` events, which just keep the connection alive. The SDK's `text_stream` is simply picking out the `text_delta` events for you, and `get_final_message()` assembles all the pieces.

You can loop over the raw events yourself with `for event in stream:` instead of `stream.text_stream`, and check `event.type`. You'll need that later for showing thinking or tool calls as they stream.

**Errors can happen mid-stream.** A request can start fine and then fail partway through, for example if the API becomes overloaded. In the raw stream that appears as an `error` event; in the SDK it raises an exception while you're iterating. So your error handling has to wrap the whole streaming loop, not just the line that starts it. You'll build that error handling in the next lesson.

### On other providers

The ideas in this lesson carry over to every provider: streaming improves time to first token but not total time, the wire format is server-sent events, you print each chunk with `flush=True`, and errors can arrive halfway through. What changes is the shape of the events. In the OpenAI Chat Completions format, which OpenAI, Ollama and many other servers accept, you pass `stream=True` to the ordinary `create()` call and loop over the result. Each chunk carries its new text in `chunk.choices[0].delta.content`, which can be `None`, so skip empty pieces. There are no named events like `message_start` here: each SSE line is just `data:` followed by a chunk, and the stream ends with `data: [DONE]`. Token usage isn't included unless you ask for it with `stream_options={"include_usage": True}`, and then it arrives in one last chunk with an empty `choices` list. OpenAI's newer Responses API streams named events instead, such as `response.output_text.delta`; see OpenAI's [streaming guide](https://developers.openai.com/api/docs/guides/streaming-responses). Here's the poem from this lesson streamed from a free local model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility):

```python
from openai import OpenAI  # uv add openai

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # for OpenAI itself: OpenAI()
stream = client.chat.completions.create(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Write a four-line poem about debugging."}],
    stream=True,
    stream_options={"include_usage": True},  # ask for a final chunk with token counts
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.usage:  # only on the last chunk
        print(f"\n{chunk.usage.prompt_tokens} in, {chunk.usage.completion_tokens} out")
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [streaming documentation](https://platform.claude.com/docs/en/build-with-claude/streaming).
   - Read "Streaming with SDKs" (Python tab), "Get the final message without handling events," "Event types" and "Content block delta types." Skim the full HTTP stream examples, and skip the tool use examples for now.
1. Optional: if you enrolled, continue Anthropic Academy's [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api) course and complete its lesson on streaming.
1. Measure the difference streaming makes.
   - Write a script that asks for a 300-word story twice: once with `messages.create()` and once with `messages.stream()`. Use `time.perf_counter()` to measure time to first token for the streamed version (the time when the first chunk arrives) and total time for both.
   - Record the numbers in your learning journal. Which number changed and which didn't?
1. Add streaming to the conversation loop you built in the last lesson, using the `stream_reply` function above.
   - Handle Ctrl+C during a response so it stops the answer and returns to the prompt, rather than crashing the program.
   - Print the token usage from the final message after each reply.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between total response time and time to first token, and why does streaming improve one but not the other?](#why-stream)
- [How do you stream text with the SDK and still get the complete message, with usage, at the end?](#streaming-with-the-sdk)
- [How do you add a streamed reply to the conversation history?](#streaming-in-a-conversation)
- [What are server-sent events, and which event types make up a stream?](#what-s-underneath-server-sent-events)
- [Why must your error handling wrap the whole streaming loop, not just the line that starts it?](#what-s-underneath-server-sent-events)
- [How do you read streamed text and token usage from an OpenAI-compatible API?](#on-other-providers)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The "Streaming responses" and "Async usage" sections of the [Python SDK documentation](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) show streaming with both the regular and async clients.
