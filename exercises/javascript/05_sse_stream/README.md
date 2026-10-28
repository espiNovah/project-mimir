# 05 · Reading a server-sent event stream

**Lessons:** [JavaScript Fundamentals](https://espinovah.github.io/project-mimir/#/lessons/core/javascript-fundamentals), [Streaming in the Browser](https://espinovah.github.io/project-mimir/#/lessons/core/streaming-in-the-browser)

## Task

A streaming chat endpoint sends a `text/event-stream` body like this:

```text
event: token
data: "Hello"

: keep-alive

event: done
data: {"stop_reason": "end_turn"}

```

`response.body` is a `ReadableStream` of bytes, and the chunks don't line up with messages: one chunk may hold three messages, half of one, or half of a multi-byte character. The tests build fake streams like that, so no server is needed.

In `sse_stream.js`, write:

1. `readEvents(stream)`, an **async generator** (`async function*`) that yields one `{ event, data }` object per complete message:
   - Decode the bytes with `TextDecoderStream`, add each chunk to a buffer, split on the blank line `"\n\n"`, and keep the last unfinished piece for the next chunk.
   - `event:` sets the name. Without one, the name is `"message"`.
   - `data:` sets the data, as a string (don't parse it here). Remove one space after the colon, if there is one. If a message has several `data:` lines, join their values with `"\n"`.
   - Ignore comment lines (they start with `:`) and any other fields. Skip a message that has no `data:` line at all, like a keep-alive ping.
   - If the stream ends in the middle of a message (no blank line after it), drop that unfinished message.
2. `collectAnswer(stream)`, which uses `readEvents` to build the final answer:
   - `token`: the data is a JSON string; append it to the text.
   - `done`: return `{ text, stopReason }`, where `stopReason` is the `stop_reason` from the data's JSON.
   - `error`: throw an `Error` whose message is the `message` from the data's JSON.
   - Ignore other events. If the stream ends with no `done` or `error`, throw an `Error` with the message `"stream ended before done"`.

## Coming from Python

An async generator is the async version of a Python generator: `async def f(): ... yield x` in Python, `async function* f() { ... yield x; }` in JavaScript. You consume it with `for await (const x of f())`, like Python's `async for`.

## Hints

- `stream.pipeThrough(new TextDecoderStream())` gives a stream of strings. You can loop over it with `for await (const chunk of textStream)`, or use `getReader()` and `reader.read()` as the lesson does.
- `const parts = buffer.split("\n\n"); buffer = parts.pop();` keeps the unfinished tail.
- For each line, `line.indexOf(":")` finds the field name. A line that starts with `:` has the colon at index 0.
- This parser is fine for streams you control. For anyone else's stream (which may use `\r\n` line endings), use a tested library such as `eventsource-parser`.

## Run the tests

```bash
cd exercises
npm test -- javascript/05_sse_stream
```

Stuck? Make the tests pass first, then compare with `solution/`.
