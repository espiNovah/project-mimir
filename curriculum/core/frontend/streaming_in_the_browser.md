### Introduction

A model answer that takes ten seconds feels broken if the screen stays blank, and fast if words start appearing after half a second. In the Streaming Responses lesson you printed tokens to a terminal as they arrived. Now you will carry that stream all the way to a web page: from the model, through your FastAPI backend, to the browser. The standard tool for this one-way flow from server to browser is *server-sent events* (SSE), the same mechanism model providers use for their own streaming APIs.

In Next.js and the AI SDK, a library did this plumbing for you. This lesson opens the box. Knowing what travels over the wire lets you stream from any backend, including the Python APIs you built in the Backend section, and lets you debug the stream when a library's version of it misbehaves.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why streaming matters for perceived speed.
- How server-sent events work and what the event format looks like.
- How to stream model output from a FastAPI endpoint.
- How to read a stream in the browser with EventSource or fetch.
- How to send extra data, such as citations, alongside the text.
- How to handle errors, cancellation and the end of a stream.

### Why stream to the browser

Remember the two numbers from Streaming Responses: **time to first token** (how long until anything appears) and **total time** (how long until the answer is complete). Streaming barely changes the total time, but it cuts the wait before anything appears from seconds to a fraction of a second. People read along while the model writes, so the app feels fast. For chat interfaces, users now expect it.

In a web app there are three hops: the model provider streams to your server, your server streams to the browser, and the browser updates the page. If any hop waits for the full answer before passing it on, the user sees no benefit. A FastAPI route that calls the model, collects the whole reply and *then* returns it throws away all the streaming the provider did. So each hop has to forward pieces as they arrive.

### The event stream format

SSE is plain text sent over one long-lived HTTP response. The server sets the content type `text/event-stream`, keeps the connection open, and writes messages one after another. Each message is a few `field: value` lines, followed by a blank line that marks the end of the message:

```text
event: token
data: "Hello"

event: token
data: " world"

event: done
data: {"stop_reason": "end_turn"}

```

- `data:` carries the payload. This is the only field you must send.
- `event:` gives the message a name. If you leave it out, the event type is `message`.
- Lines starting with `:` are comments. Servers send them as keep-alive pings so proxies don't close a quiet connection, and clients ignore them.
- There are also `id:` and `retry:` fields, used for reconnecting after a dropped connection. You won't need them for a chat answer.

Notice that the text tokens are sent as JSON strings, in quotes. That matters because a raw newline inside `data:` would end the line, and a blank line would end the whole message. Model output is full of newlines (Markdown paragraphs, code blocks), so encoding each piece as JSON turns a newline into the two characters `\n` and keeps the format safe.

Because SSE is ordinary HTTP, it passes through most proxies and load balancers and needs no special server. That's its main advantage over *WebSockets*, a two-way protocol you'd only need if the browser had to send messages continuously in the middle of the stream.

### Use named events for structure

A chat answer is more than text. You might want to send the sources a RAG answer used, token usage, a final status, or an error. Named events keep these apart, so the browser can handle each one differently:

| Event | Data | What the browser does |
| --- | --- | --- |
| `token` | a JSON string | appends it to the answer |
| `citations` | a JSON list of sources | shows them under the answer |
| `done` | JSON with `stop_reason` and usage | re-enables the input box |
| `error` | JSON with a safe message | shows the error next to the partial answer |

Every stream should end with exactly one `done` or `error` event. If the connection closes without either, the client knows something went wrong in between, for example a crashed server or a dropped network.

### A streaming endpoint and a fetch reader

Here is a complete working pair: a FastAPI app with a streaming `POST /chat/stream` route, and a page that reads it. Create a project with `uv init chat-stream`, run `uv add "fastapi[standard]" anthropic`, and put your `ANTHROPIC_API_KEY` in the environment as in Your First API Call.

```python
import os

import anthropic
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.AsyncAnthropic()  # (1) async client: doesn't block the server
app = FastAPI()

class ChatRequest(BaseModel):
    question: str = Field(min_length=1)  # an empty question gets a 422

@app.post("/chat/stream", response_class=EventSourceResponse)  # (2)
async def chat_stream(req: ChatRequest):
    messages = [{"role": "user", "content": req.question}]
    try:
        async with client.messages.stream(model=MODEL, max_tokens=4000, messages=messages) as stream:  # (3)
            async for text in stream.text_stream:
                yield ServerSentEvent(event="token", data=text)  # (4) JSON-encoded for you
        yield ServerSentEvent(event="done", data={})
    except anthropic.APIError:
        yield ServerSentEvent(event="error", data={"message": "The model call failed."})  # (5)

app.mount("/", StaticFiles(directory="static", html=True))  # (6) serves static/index.html
```

1. `AsyncAnthropic` is the async version of the client you've used since Your First API Call. While one request waits on the model, the server can handle others, as you learned in Async Basics.
1. `response_class=EventSourceResponse` (added in FastAPI 0.135) tells FastAPI that this route is a *generator*, a function that `yield`s values one at a time (see Pythonic Python), and that each yielded value is one SSE message. FastAPI sets the `text/event-stream` header, sends keep-alive pings and disables proxy buffering for you.
1. `client.messages.stream` is the same helper from Streaming Responses, in its async form: `async with` and `async for`. It and `text_stream` belong to the Anthropic SDK. Other SDKs stream with different objects, shown in [On other providers](#on-other-providers).
1. Each text delta from the model is forwarded the moment it arrives. `data=` is always encoded as JSON, which gives you the newline safety described above. Pydantic models and dictionaries work too.
1. When the model finishes, a `done` event tells the browser the answer is complete. If the model call fails, the browser gets a clear `error` event instead. It says nothing about the internal error, because error details can leak information. Log the real exception on the server, as in Debugging and Logging.
1. Serving the page from the same app means the page and the API share an *origin* (the same scheme, host and port), so the browser allows the request without any CORS setup. The mount goes last so it doesn't shadow your API routes.

Now the browser side. Create `static/index.html` with a form, a Stop button and a place for the answer. (`white-space: pre-wrap` keeps the model's line breaks visible.)

```html
<form id="ask"><input id="q"> <button>Ask</button> <button type="button" id="stop">Stop</button></form>
<p id="answer" style="white-space: pre-wrap"></p>
```

Below those two lines, add the script that sends the question and reads the stream. Then run `uv run fastapi dev main.py` and open `http://localhost:8000`.

```html
<script>
  const answer = document.querySelector("#answer");
  let controller;  // (7) lets us cancel the request
  document.querySelector("#stop").onclick = () => controller?.abort();
  document.querySelector("#ask").onsubmit = async (e) => {
    e.preventDefault();
    answer.textContent = "";
    controller = new AbortController();
    try {
      const res = await fetch("/chat/stream", {
        method: "POST", headers: { "Content-Type": "application/json" }, signal: controller.signal,
        body: JSON.stringify({ question: document.querySelector("#q").value }),
      });
      const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();  // (8)
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += value;
        const messages = buffer.split("\n\n");  // (9) a blank line ends a message
        buffer = messages.pop();                // keep the unfinished part for later
        for (const msg of messages) {
          const event = msg.match(/^event: (.*)$/m)?.[1];  // (10) parse one message
          const data = msg.match(/^data: (.*)$/m)?.[1];
          if (event === "token") answer.textContent += JSON.parse(data);  // (11) never innerHTML
          if (event === "error") answer.textContent += `\n[${JSON.parse(data).message}]`;
        }
      }
    } catch (err) {  // a deliberate Stop throws AbortError, which we ignore
      if (err.name !== "AbortError") answer.textContent += `\n[${err.message}]`;
    }
  };
</script>
```

7. An `AbortController` is the browser's standard way to cancel a `fetch`. Calling `controller.abort()` closes the connection and makes the pending `await` throw an `AbortError`, which the `catch` deliberately ignores.
1. `res.body` is a *readable stream*: the response body, delivered in chunks as they arrive over the network, instead of all at once like `await res.json()`. The chunks are raw bytes. `TextDecoderStream` turns them into text, decoding correctly even when a multi-byte character such as an emoji is split across two chunks. `reader.read()` waits for the next chunk and returns `{ value, done }`.
1. Network chunks don't line up with SSE messages. One chunk may hold three messages, or half of one. So the code adds each chunk to a buffer, splits on the blank line, handles every complete message, and keeps the last, possibly unfinished, piece for next time. This buffering is the part people most often get wrong.
1. Two regular expressions (the same idea as Python's `re` module from Regular Expressions; the `m` flag makes `^` and `$` match at each line) pull out the `event:` name and the `data:` JSON. This short parser relies on FastAPI putting each payload on a single `data:` line, which its JSON encoding guarantees. A stream from another server might split data over several lines, so for those, use a small, tested parser library such as [eventsource-parser](https://github.com/rexxars/eventsource-parser).
1. Model output is untrusted input, just like user input. Setting `textContent` displays it as plain text. Setting `innerHTML` would let a model that was tricked into writing `<img src=x onerror=...>` run code in your user's browser. If you want to render Markdown, use a Markdown library together with a sanitizer such as DOMPurify.

That's the whole mechanism. A React version keeps the same reading loop and appends each token to a state variable instead of to `textContent`.

### EventSource or fetch

Browsers have a built-in SSE client called `EventSource`. It's simpler than the code above: it parses messages for you, fires a separate listener per event name, and reconnects automatically if the connection drops.

```javascript
const source = new EventSource("/notifications/stream");
source.addEventListener("token", (e) => console.log(JSON.parse(e.data)));
```

But `EventSource` can only send `GET` requests, and it can't set custom headers such as `Authorization`. A chat request usually sends a question, a conversation history and an auth token, so it needs `POST` with a JSON body and headers. That's why chat apps use `fetch` with a stream reader and parse SSE by hand, or with a small library. Automatic reconnection also does more harm than good for a chat answer: reconnecting would start a new, paid model call from the beginning.

Use `EventSource` for simple `GET` feeds, such as job progress or notifications. Use `fetch` for anything that sends data.

### Errors and cancellation

Streams fail in ways normal requests don't, because the status code is sent *before* the body. Once the server has sent `200 OK` and the first tokens, it can't change its mind and send a `500`. Problems halfway through have to travel inside the stream, which is why the endpoint sends an `error` event. Three situations to plan for:

- **The request is rejected before streaming starts**, for example a `422` for an empty question or a `401` for a missing login. FastAPI answers these with an ordinary JSON error, not a stream, so the example's reader would find no events and show nothing. Add ``if (!res.ok) throw new Error(`HTTP ${res.status}`);`` right after the `fetch`, so the `catch` shows the problem.
- **The model fails mid-answer**, for example from an overloaded error. Keep the partial text on screen and add a visible error notice, so the user knows the answer is incomplete and can retry.
- **The user stops or leaves.** When the browser aborts the request or the tab closes, the connection drops. FastAPI notices and closes your generator, which exits the `async with` block, which closes the SDK's connection to the model provider. The model stops generating, and you stop paying for tokens nobody will read. This only works because the model call lives *inside* the generator. You can check it yourself: put a `print` in a `finally:` block around the loop, click Stop, and watch your server log.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Test your stream with curl

You can watch the raw stream without a browser. The `-N` flag turns off `curl`'s output buffering, so you see each message as it arrives:

`curl -N -X POST localhost:8000/chat/stream -H "Content-Type: application/json" -d '{"question": "Count to ten"}'`

If the messages appear all at once at the end, something between the model and you is buffering the response.

</div>

### On other providers

Every major provider streams over SSE, but each one sends its own event names and payloads. Claude sends named events such as `content_block_delta` and `message_stop`. OpenAI's Chat Completions API sends unnamed `data:` messages, each holding a JSON "chunk" whose new text is in `choices[0].delta.content`, and ends with a literal `data: [DONE]`. OpenAI's newer Responses API uses named events such as `response.output_text.delta`, described in [OpenAI's streaming guide](https://developers.openai.com/api/docs/guides/streaming-responses). The Chat Completions chunk format is in the [Chat Completions API reference](https://developers.openai.com/api/reference/resources/chat). This is one more reason your endpoint translates the provider's stream into your *own* small set of events. The browser code, the buffering, the `done` and `error` events and cancellation stay the same whatever model sits behind the server. Only the generator changes. Here it is for OpenAI, or for a local open model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), which streams in the same chunk format:

```python
import openai  # uv add openai
MODEL = os.environ.get("MIMIR_MODEL", "qwen3:8b")
client = openai.AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # AsyncOpenAI() for OpenAI

@app.post("/chat/stream", response_class=EventSourceResponse)
async def chat_stream(req: ChatRequest):
    messages = [{"role": "user", "content": req.question}]
    try:
        async with await client.chat.completions.create(model=MODEL, messages=messages, stream=True) as stream:
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:  # some chunks carry no text
                    yield ServerSentEvent(event="token", data=chunk.choices[0].delta.content)
        yield ServerSentEvent(event="done", data={})
    except openai.APIError:
        yield ServerSentEvent(event="error", data={"message": "The model call failed."})
```

The `async with` matters here too: it closes the connection to the provider when the user clicks Stop. Two details differ for the practice task. The stop reason is called `finish_reason` (`"stop"` or `"length"`) and arrives in the last chunk, and token usage only appears in the stream if you pass `stream_options={"include_usage": True}`. If you build in TypeScript instead, the Vercel AI SDK from [Next.js and the AI SDK](#/lessons/core/nextjs-and-the-ai-sdk) hides all of these differences behind one `streamText` call, and switching providers is a one-line change.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) on MDN.
   - Read the whole page, especially the event stream format and the examples of named events.
1. Read [FastAPI's server-sent events tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/) and the streaming section of [FastAPI's custom response guide](https://fastapi.tiangolo.com/advanced/custom-response/).
   - Focus on how a generator becomes a streamed response, `ServerSentEvent`, and the "SSE with POST" section.
1. Read [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming) in the Claude docs, to see SSE from the provider's side and the event types it sends.
   - Read the Python SDK examples and the event types section. Notice that the provider's stream is itself SSE: your endpoint is translating one event stream into another.
1. Read [Using readable streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams) on MDN, up to and including consuming a fetch response body as a stream.
1. Practice: build the `POST /chat/stream` endpoint and page from this lesson, then extend them.
   - Get the example running and test it with `curl -N` and in the browser.
   - Add the `res.ok` check from [Errors and cancellation](#errors-and-cancellation), then submit an empty question and confirm the page shows the error.
   - Call `await stream.get_final_message()` after the loop and put its `stop_reason` and token usage in the `done` event, as in the table above. Add a `done` handler that shows them and re-enables the Ask button, which you disable while a stream is running.
   - Send the conversation history in the request body, so follow-up questions work, as in System Prompts and Conversations.
   - Add a `finally:` block that logs when the generator closes. Click Stop mid-answer and confirm in the log that the model call ended.
   - Write a test with `TestClient` that replaces the model call with a fake async generator (see Testing with pytest) and checks that the response body contains `event: token` messages and ends with `event: done`.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why does every hop from the model to the page need to stream?](#why-stream-to-the-browser)
- [What does one SSE message look like, and why are the tokens JSON-encoded?](#the-event-stream-format)
- [What is each named event in a chat stream for?](#use-named-events-for-structure)
- [Why does the browser code keep a buffer instead of handling each chunk directly?](#a-streaming-endpoint-and-a-fetch-reader)
- [Why should streamed model output be added with textContent rather than innerHTML?](#a-streaming-endpoint-and-a-fetch-reader)
- [When would you use EventSource, and when fetch with a stream reader?](#eventsource-or-fetch)
- [What happens to the model call when the user clicks Stop, and why does that matter?](#errors-and-cancellation)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [HTML specification's section on server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html) is the precise definition of the format, including how parsers treat every edge case.
- MDN's [AbortController page](https://developer.mozilla.org/en-US/docs/Web/API/AbortController) covers cancelling `fetch` requests in more detail.
- [DOMPurify](https://github.com/cure53/DOMPurify) is the widely used sanitizer for rendering model-written Markdown as HTML safely.
