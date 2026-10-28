<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

When a normal web app fails, it usually throws an error you can see. When an LLM app fails, it often returns a confident, well-formatted, wrong answer with a `200 OK`. An agent might take twelve steps, call four tools and go wrong at step three. Without a record of every step, you are guessing. Observability means being able to answer "what happened on this request, and why?" from the data your app records. This lesson teaches the vocabulary (logs, traces, spans) and the tools built for LLM apps.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The difference between logs, metrics and traces.
- What a span is, and how spans nest into a trace.
- What to record on every model call and tool call.
- What OpenTelemetry is and what its GenAI conventions standardize.
- How LLM observability tools like Langfuse and Arize Phoenix fit in.
- Privacy and cost concerns when you store prompts and outputs.

### Key ideas

- **Logs, metrics and traces answer different questions.** A log is a timestamped line about one event ("tool call failed"). A metric is a number over time (requests per minute, p95 latency). A trace is the full story of one request, start to finish. For LLM apps, traces are the most useful of the three.
- **A trace is a tree of spans.** A span is one timed unit of work with a name, start time, duration and attributes. The root span is the whole request; child spans are each model call, retrieval step and tool call inside it. Seeing the tree shows you where time and tokens went, and which step went wrong.
- **Record the same fields on every model call.** Model name, input and output tokens, latency, stop reason, the prompt (or its version) and the response. On tool calls: tool name, arguments, result or error, and duration. With token counts you can compute cost per request later.
- **Use structured logs, not print statements.** Log JSON with a request or trace ID on every line, so you can filter one request's logs out of thousands.
- **OpenTelemetry (OTel) is the vendor-neutral standard.** It defines how to create spans and export them to any backend. Its GenAI semantic conventions name the attributes for LLM calls, such as `gen_ai.request.model` and `gen_ai.usage.input_tokens`, so different tools can read the same data.
- **LLM observability platforms add the views you need.** Langfuse and Arize Phoenix are open source and can be self-hosted or used on a free cloud tier. They show traces as trees, let you add scores and comments to traces, and connect traces to datasets and evals. Most SDKs instrument common clients with a decorator or one line of setup.
- **Traces contain user data.** Prompts and outputs may include personal information. Decide what you store, mask what you must, and say so in your privacy notes. Sampling (tracing only a fraction of requests) also keeps storage costs down at scale.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [OpenTelemetry observability primer](https://opentelemetry.io/docs/concepts/observability-primer/) for the core vocabulary.
   - Read the whole page, especially the parts on logs, spans and distributed traces.
1. Skim the [OpenTelemetry semantic conventions for generative AI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) to see the standard attribute names for model calls.
   - Look at the spans page for model calls and note which attributes cover tokens, model name and errors. You don't need to memorize them.
1. Follow the [Langfuse getting started guide](https://langfuse.com/docs/observability/get-started) to send your first traces.
   - Instrument one script that calls a model and one tool. Open the trace in the Langfuse UI and find the token counts and latency for each span.
1. Read the [Arize Phoenix LLM tracing overview](https://arize.com/docs/phoenix/tracing/llm-traces) as an alternative that runs fully locally.
   - Compare how it presents a trace with Langfuse. Either tool is fine for the projects that follow.
1. Practice: add tracing to your Agent Loop From Scratch project.
   - Every model call and every tool call must appear as its own span with tokens and latency.
   - Run five different queries and find the slowest span in each trace.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [OpenTelemetry for Python](https://opentelemetry.io/docs/languages/python/) is the reference if you want to create spans by hand or export to a backend other than an LLM-specific tool.
- [Langfuse self-hosting](https://langfuse.com/self-hosting) explains how to run Langfuse on your own machine with Docker if you'd rather not send data to a cloud service.
