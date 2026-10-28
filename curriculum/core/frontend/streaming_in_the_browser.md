<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A model answer that takes ten seconds feels broken if the screen stays blank, and fast if words start appearing after half a second. In the Streaming Responses lesson you printed tokens to a terminal as they arrived. Now you will carry that stream all the way to a web page: from the model, through your FastAPI backend, to the browser. The standard tool for this one-way flow from server to browser is *server-sent events* (SSE), the same mechanism model providers use for their own streaming APIs.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why streaming matters for perceived speed.
- How server-sent events work and what the event format looks like.
- How to stream model output from a FastAPI endpoint.
- How to read a stream in the browser with EventSource or fetch.
- How to send extra data, such as citations, alongside the text.
- How to handle errors, cancellation and the end of a stream.

### Key ideas

- **Time to first token is what users feel.** Total generation time barely changes with streaming, but the wait before anything appears drops from seconds to a fraction of a second. For chat interfaces, streaming is expected.
- **SSE is plain text over a long-lived HTTP response.** The server sets the `text/event-stream` content type and keeps writing messages. Each message is lines such as `event: token` and `data: ...`, followed by a blank line. It works over normal HTTP, so it passes through most proxies and needs no special server.
- **FastAPI can stream.** A route can return a streaming response built from a generator, async or not, that yields SSE-formatted chunks as the model produces them. Inside, you iterate over the provider SDK's stream and forward each text delta.
- **Two ways to read in the browser.** `EventSource` is the built-in SSE client: it handles parsing and reconnection, but only supports `GET` requests and cannot set custom headers such as an API key. `fetch` with a streaming body reader supports `POST` and headers, but you parse the SSE lines yourself. For chat apps that send a question in a `POST` body, the fetch approach is common.
- **Use named events for structure.** Send different event types for different data: `token` events for text, a `citations` event with JSON for sources, a `done` event at the end and an `error` event if something fails. The browser handles each type differently.
- **Plan for the unhappy paths.** Streams can fail halfway. Show partial output with an error notice, let users stop generation (an `AbortController` cancels a fetch), and make sure the server stops the model call when the client disconnects, so you do not pay for tokens nobody reads.
- **Escape streamed text.** Append model output with `textContent` or render Markdown with a library that sanitizes HTML. Model output is untrusted input, just like user input.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) on MDN.
   - Read the whole page, especially the event stream format and the examples of named events.
1. Read [FastAPI's server-sent events tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/) and the streaming section of [FastAPI's custom response guide](https://fastapi.tiangolo.com/advanced/custom-response/).
   - Focus on how a generator becomes a streamed response.
1. Read [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming) in the Claude docs, to see SSE from the provider's side and the event types it sends.
   - Read the Python SDK examples and the event types section. You will forward these deltas to your own clients.
1. Read [Using readable streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams) on MDN, up to and including consuming a fetch response body as a stream.
1. Practice: build a FastAPI endpoint `POST /chat/stream` that streams a model's answer as SSE `token` events and ends with a `done` event. Write a plain HTML and JavaScript page that sends a question with `fetch`, reads the stream, and appends tokens to the page as they arrive. Add a Stop button that cancels the request.

</div>
