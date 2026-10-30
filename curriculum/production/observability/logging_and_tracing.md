### Introduction

When a normal web app fails, it usually throws an error you can see. When an LLM app fails, it often returns a confident, well-formatted, wrong answer with a `200 OK`. An agent might take twelve steps, call four tools and go wrong at step three. Without a record of every step, you are guessing. **Observability** means being able to answer "what happened on this request, and why?" from the data your app records, without adding new code and redeploying first.

You've already built the pieces at small scale. In Debugging and Logging you used Python's `logging` module. In Why Evals Matter you wrote `traced_call`, and in Agent Tracing and Debugging you built a JSONL tracer with trace IDs, span IDs and parent IDs. Those work on your laptop. A deployed service is different: many requests run at once, logs from all of them end up mixed together, and nobody is going to open a JSONL file on a server. This lesson is the production step up. You'll make logs machine-readable and tie each line to its request, switch your hand-made tracer to **OpenTelemetry**, the standard that every serious tracing tool accepts, and send traces to a real backend you can run for free.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What logs, metrics and traces are each for in a running service.
- Structured JSON logs with a request ID and trace ID on every line.
- The core OpenTelemetry ideas: tracer providers, spans, attributes, exporters and context propagation.
- The OpenTelemetry GenAI semantic conventions for model and tool calls.
- Instrumenting a FastAPI service and an agent.
- Sending traces to Jaeger, Arize Phoenix or Langfuse.
- Sampling, and keeping personal data and cost under control.

### Logs, metrics and traces

Observability data comes in three kinds, often called the three **signals**. Each answers a different question.

- A **log** is a timestamped record of one event: "model call failed with a 529", "request done in 1,840 ms". Logs are cheap to write and good for "what exactly happened at 14:02?"
- A **metric** is a number tracked over time: requests per minute, error rate, p95 latency, dollars spent per hour. Metrics are tiny to store and good for "is something wrong right now?" They're what alerts watch, which is the subject of the next lesson but one, Alerting and Incidents.
- A **trace** is the story of one request from start to finish, as a tree of timed **spans**. Traces are good for "why was *this* request slow, expensive or wrong?"

For LLM apps, traces carry most of the weight, because the interesting failures live inside a request: the retrieval step that returned the wrong chunk, the tool call with a bad argument, the model call that ran out of tokens. But the three work together. A metric tells you the error rate jumped at 14:00. Logs from 14:00 show which requests failed. Each log line carries a trace ID, so you click through to the full trace of one failing request and see the step that broke. That chain only works if every log line knows which request and which trace it belongs to, which is where we start.

### Structured logs with request IDs

The log format you used in Foundations, `2026-10-30 14:02:11 INFO quiz: answered 'Capital of France?'`, is written for humans. In production, logs from every copy of your service stream into one place (Cloud Run's log viewer, Grafana Loki, Datadog), and you search them with queries like "all lines where `status` is 500 and `path` is `/ask`." That needs **structured logs**: one JSON object per line, with named fields instead of a sentence you'd have to pick apart with regular expressions.

Two fields make structured logs useful:

- A **request ID**, a unique string for each incoming HTTP request. Every log line written while handling that request carries it, so you can pull one request's lines out of thousands. If the caller sends an `X-Request-ID` header (load balancers and API gateways often add one), reuse it; otherwise make a new one. Send it back in the response, so a user reporting a bug can quote it.
- A **trace ID**, the ID of the trace this request belongs to. With it, a log line links straight to the trace in your tracing tool.

How does a log call deep inside your code know the current request ID without passing it through every function? Python's `contextvars` module solves this. A `ContextVar` holds a value that's private to the current request, even when many requests run at once in the same process. Your middleware sets it at the start of a request, and the log formatter reads it on every line. OpenTelemetry uses the same mechanism to track the current span, so the formatter can ask it for the trace ID too.

The other rule for production logs: **log metadata, not content.** A line saying the model call used 412 input tokens and cost $0.00009 is safe to keep for months. A line containing the user's question may hold their name, address or medical history. Content belongs in traces, where you control redaction, access and retention in one place, as you'll see below.

### OpenTelemetry in five ideas

**OpenTelemetry** (OTel) is an open standard and set of libraries for producing traces, metrics and logs, and for sending them anywhere. You met its vocabulary in Agent Tracing and Debugging. Here are the five ideas you need to use it in a service:

1. **The API and the SDK are separate.** Your code and libraries use the small OTel *API* to create spans: `tracer.start_as_current_span("answer_question")`. On its own, the API does nothing. Your app installs the *SDK* once at startup, which decides what happens to spans. Libraries can therefore add tracing without forcing it on anyone.
1. **A tracer provider is the central object.** You create one `TracerProvider` at startup and register it globally. It carries a **resource**, attributes describing the service itself, most importantly `service.name`, so a backend can tell your API's spans apart from your worker's.
1. **Spans carry attributes and a status.** An **attribute** is a key-value fact on a span, such as `gen_ai.usage.input_tokens = 412`. A span's **status** is unset, OK or ERROR. A **span kind** says what role the span plays: `SERVER` for handling an incoming request, `CLIENT` for calling another service such as a model API, `INTERNAL` for work inside your process.
1. **Exporters send spans somewhere.** A **span processor** collects finished spans and hands them to an **exporter**. The `BatchSpanProcessor` sends them in batches from a background thread, so tracing doesn't slow your requests. The exporter you'll use most speaks **OTLP**, the OpenTelemetry Protocol, which almost every backend accepts. Switching backends means changing a URL, not your code.
1. **Context propagation joins services together.** When your API calls another service, OTel adds a `traceparent` HTTP header holding the trace ID and the current span ID, following the W3C Trace Context standard. The receiving service reads it and makes its spans children of yours, so one trace can cross many services. The Anthropic SDK does this with the API, which is how Claude's server-side spans can join your traces.

Finally, **instrumentation libraries** create spans for popular frameworks so you don't have to. `opentelemetry-instrumentation-fastapi` makes a `SERVER` span for every request. Some model SDKs instrument themselves: the Anthropic Python SDK creates a span for each `messages.create` call as soon as a tracer provider is registered (a Claude feature, in beta).

### Setting up logging and tracing

Put all of the setup in one module that your app imports first. Create a project with `uv init askbot`, then `uv add "fastapi[standard]" anthropic opentelemetry-sdk opentelemetry-exporter-otlp-proto-http opentelemetry-instrumentation-fastapi`, and save this as `obs.py`:

```python
# obs.py: JSON logs with request and trace IDs, plus OpenTelemetry tracing.
import json
import logging
import os
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

request_id: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    """One JSON object per line, with the request ID and trace ID on every line."""

    def format(self, record: logging.LogRecord) -> str:
        ctx = trace.get_current_span().get_span_context()
        line = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id.get(),
            "trace_id": format(ctx.trace_id, "032x") if ctx.is_valid else None,
        }
        line |= getattr(record, "fields", {})          # extra={"fields": {...}}
        if record.exc_info:
            line["exc"] = self.formatException(record.exc_info)
        return json.dumps(line, default=str)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)       # platforms collect stdout
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)


class JsonlSpanExporter(SpanExporter):
    """Append finished spans to a local file: a free, Docker-free trace store."""

    def __init__(self, path: str):
        self.path = path

    def export(self, spans) -> SpanExportResult:
        with open(self.path, "a", encoding="utf-8") as f:
            for s in spans:
                f.write(json.dumps({
                    "trace_id": format(s.context.trace_id, "032x"),
                    "span_id": format(s.context.span_id, "016x"),
                    "parent_id": format(s.parent.span_id, "016x") if s.parent else None,
                    "name": s.name,
                    "start": s.start_time, "end": s.end_time,   # nanoseconds
                    "status": s.status.status_code.name,
                    "attributes": dict(s.attributes or {}),
                }, default=str) + "\n")
        return SpanExportResult.SUCCESS


def setup_tracing(service: str, sample_ratio: float = 1.0) -> None:
    provider = TracerProvider(
        resource=Resource.create({"service.name": service,
                                  "deployment.environment.name": os.environ.get("APP_ENV", "dev")}),
        # Keep `sample_ratio` of new traces; a child always follows its parent's decision.
        sampler=ParentBased(TraceIdRatioBased(sample_ratio)),
    )
    if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):   # Jaeger, Phoenix, Langfuse...
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    if path := os.environ.get("SPANS_FILE"):            # e.g. spans.jsonl
        provider.add_span_processor(BatchSpanProcessor(JsonlSpanExporter(path)))
    trace.set_tracer_provider(provider)
```

A few things to notice:

- **The formatter does the joining.** Any logger anywhere in your app, including library loggers, writes JSON with the request ID and trace ID, because they all pass through this one formatter. Extra fields go in `extra={"fields": {...}}`.
- **Logs go to standard output.** Cloud platforms like Cloud Run and Render collect whatever your process prints, so you don't manage log files yourself.
- **Two exporters, chosen by environment variables.** `OTLPSpanExporter()` reads `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS` from the environment, which are standard OTel settings. `JsonlSpanExporter` is a 20-line exporter of your own that writes spans to a file. It's handy in tests, on machines without Docker, and in the next lesson, where you'll read that file to pick traces for review.

### Instrumenting a FastAPI service

Here's a small question-answering service built on the API you made in FastAPI Basics. Save it as `app.py` next to `obs.py`:

```python
# app.py
import logging
import os
import re
import time
import uuid

import anthropic
from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import BaseModel

from obs import request_id, setup_logging, setup_tracing

setup_logging()
setup_tracing("askbot", sample_ratio=float(os.environ.get("TRACE_SAMPLE_RATIO", "1.0")))

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
PROMPT_VERSION = "ask-v3"
PRICE_PER_MTOK = {"input": 0.10, "output": 0.50}   # USD; copy from your provider's pricing page
log = logging.getLogger("askbot")
tracer = trace.get_tracer("askbot")
client = anthropic.Anthropic()                     # uses the tracer provider registered above
app = FastAPI()
FastAPIInstrumentor.instrument_app(app, exclude_spans=["receive", "send"])  # one span per request

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def redact(text: str) -> str:
    return PHONE.sub("[PHONE]", EMAIL.sub("[EMAIL]", text))


@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex
    token = request_id.set(rid)                    # every log line in this request gets it
    start = time.perf_counter()
    try:
        response = await call_next(request)
        response.headers["x-request-id"] = rid       # give both IDs back to the caller
        response.headers["x-trace-id"] = format(
            trace.get_current_span().get_span_context().trace_id, "032x")
        log.info("request done", extra={"fields": {
            "method": request.method, "path": request.url.path, "status": response.status_code,
            "latency_ms": round((time.perf_counter() - start) * 1000)}})
        return response
    finally:
        request_id.reset(token)


class Ask(BaseModel):
    question: str


@app.post("/ask")
def ask(body: Ask) -> dict:
    with tracer.start_as_current_span("answer_question") as span:
        span.set_attribute("app.prompt.version", PROMPT_VERSION)
        span.set_attribute("app.question", redact(body.question)[:2000])
        try:
            response = client.messages.create(
                model=MODEL, max_tokens=1000,
                system="Answer briefly and say so when you don't know.",
                messages=[{"role": "user", "content": body.question}])
        except anthropic.APIError as exc:      # the span records it and is marked ERROR on exit
            log.error("model call failed", extra={"fields": {"error": type(exc).__name__}})
            raise
        answer = "".join(b.text for b in response.content if b.type == "text")
        usage = response.usage
        cost = (usage.input_tokens * PRICE_PER_MTOK["input"]
                + usage.output_tokens * PRICE_PER_MTOK["output"]) / 1_000_000
        span.set_attributes({                      # the SDK's child span already has gen_ai.usage.*
            "app.stop_reason": response.stop_reason,
            "app.cost_usd": round(cost, 6),
            "app.answer": redact(answer)[:4000],
        })
        log.info("answered", extra={"fields": {
            "model": MODEL, "prompt_version": PROMPT_VERSION, "stop_reason": response.stop_reason,
            "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens,
            "cost_usd": round(cost, 6)}})                # metadata only: no question, no answer
        return {"answer": answer}
```

Run it with `SPANS_FILE=spans.jsonl uv run fastapi dev app.py` and send a question from the `/docs` page. One request produces a trace with three spans:

```text
POST /ask                    SERVER  (FastAPI instrumentation: method, route, status code)
└── answer_question          INTERNAL (yours: prompt version, redacted question and answer, cost)
    └── anthropic.messages.create   CLIENT (Anthropic SDK: model, tokens, response ID)
```

And two log lines, both carrying the same `request_id` and `trace_id`:

```json
{"ts": "2026-10-30T14:02:11.384+00:00", "level": "INFO", "logger": "askbot", "msg": "answered", "request_id": "abc123", "trace_id": "2dd1247dd2f38d02504249d052158c99", "model": "claude-haiku-5-5", "prompt_version": "ask-v3", "stop_reason": "end_turn", "input_tokens": 20, "output_tokens": 12, "cost_usd": 8e-06}
{"ts": "2026-10-30T14:02:11.385+00:00", "level": "INFO", "logger": "askbot", "msg": "request done", "request_id": "abc123", "trace_id": "2dd1247dd2f38d02504249d052158c99", "method": "POST", "path": "/ask", "status": 200, "latency_ms": 15}
```

The span you wrote yourself, `answer_question`, holds what only your app knows: the prompt version (Prompt Versioning and CI Evals, later in this path, builds on it), the cost, and the content, redacted. The SDK's span holds the standard model-call facts. Because the SDK already records token counts on its span, your span doesn't repeat them; a backend that sums `gen_ai.usage.input_tokens` across spans would otherwise count every token twice.

The `x-trace-id` response header is small but powerful. Your frontend can attach it to a thumbs-up or thumbs-down button, so user feedback lands on the exact trace it's about. You'll use that in From Traces to Evals.

### The GenAI semantic conventions

OTel's **semantic conventions** are agreed names for attributes, so that every tool reads `http.response.status_code` the same way. The **GenAI semantic conventions** do the same for model calls, agents and tools. You mapped your JSONL fields onto them in Agent Tracing and Debugging. The ones you'll meet most on an inference (model call) span are:

| Attribute | Meaning |
| --- | --- |
| `gen_ai.operation.name` | What kind of call: `chat`, `embeddings`, `execute_tool`, `invoke_agent` |
| `gen_ai.provider.name` | Who served it: `anthropic`, `openai`, `gcp.gen_ai` and so on |
| `gen_ai.request.model`, `gen_ai.response.model` | The model you asked for, and the one that answered |
| `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` | Token counts, for cost and context tracking |
| `gen_ai.response.finish_reasons` | Why generation stopped, such as `end_turn` or `max_tokens` |
| `gen_ai.response.id`, `gen_ai.conversation.id` | The provider's response ID, and your own conversation ID if you have one |
| `error.type` | The error class, when the call failed |

The conventions recommend naming an inference span `{operation} {model}`, that is, `chat` followed by the model ID, with kind `CLIENT`. Instrumentation libraries don't always follow the naming rule (the Anthropic SDK names its span `anthropic.messages.create` and puts the standard attributes on it), so filter on attributes, not span names.

The prompts and responses themselves have names too, `gen_ai.input.messages`, `gen_ai.output.messages` and `gen_ai.system_instructions`, but they're **opt-in**: the conventions say instrumentation must not record content unless you turn it on, because it often contains personal data. The Anthropic SDK follows this. By default its spans are "metadata only", and you'd pass `Anthropic(open_telemetry={"traces": {"content_mode": "content"}})` to include full prompts. The code above leaves that off and puts *redacted* content on its own span instead.

Keep in mind that the GenAI conventions are still marked "Development", meaning names can change between versions. In 2025, for example, `gen_ai.system` was renamed `gen_ai.provider.name`. When you build a dashboard on these names, check the current spec and pin your library versions.

### Instrumenting an agent

An agent is a loop of model calls and tool calls, so its trace is deeper. Change the files agent from Agent Tracing and Debugging so it uses OTel instead of `tracer.py`. Only the run and tool spans need code; the SDK makes the model-call spans on its own, and they nest under whichever span is current:

```python
# agent_otel.py: the files agent with OTel; read_file, TOOLS, client and MODEL are as before
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from obs import setup_logging, setup_tracing

setup_logging()
setup_tracing("files-agent")
tracer = trace.get_tracer("files-agent")


def run_tool(call) -> dict:
    with tracer.start_as_current_span(f"execute_tool {call.name}") as span:
        span.set_attributes({"gen_ai.operation.name": "execute_tool",
                             "gen_ai.tool.name": call.name, "gen_ai.tool.call.id": call.id})
        try:
            return {"type": "tool_result", "tool_use_id": call.id, "content": read_file(**call.input)}
        except Exception as exc:                       # report it to the model, mark the span
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            span.set_attribute("error.type", type(exc).__name__)
            return {"type": "tool_result", "tool_use_id": call.id,
                    "content": str(exc), "is_error": True}


def run_agent(goal: str, max_steps: int = 10) -> str:
    with tracer.start_as_current_span("invoke_agent files-agent") as run:
        run.set_attributes({"gen_ai.operation.name": "invoke_agent",
                            "gen_ai.agent.name": "files-agent"})
        messages = [{"role": "user", "content": goal}]
        for step in range(1, max_steps + 1):
            # The SDK's model-call span appears here, as a child of invoke_agent.
            response = client.messages.create(model=MODEL, max_tokens=16000,
                                              tools=TOOLS, messages=messages)
            messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason != "tool_use":
                break
            calls = [b for b in response.content if b.type == "tool_use"]
            messages.append({"role": "user", "content": [run_tool(c) for c in calls]})
        run.set_attributes({"app.steps": step, "app.end_reason": response.stop_reason})
        return "".join(b.text for b in response.content if b.type == "text")
```

A tool that fails is caught and reported to the model, as you learned in Tool Errors and Parallel Calls, so the `with` block never sees an exception. That's why the code sets the span's status to ERROR by hand: otherwise the trace would show a failed tool as a success. If the agent runs inside your FastAPI service, `invoke_agent` becomes a child of the `POST` span and the whole request is one tree.

### Choosing a backend

A **tracing backend** stores spans and shows them as searchable trees. Because your code speaks OTLP, you can try several without changing it. All of these are free:

- **Jaeger** is a general-purpose, open-source tracing backend from the Cloud Native Computing Foundation. Run it with Docker (`docker run --rm -p 16686:16686 -p 4318:4318 cr.jaegertracing.io/jaegertracing/jaeger:2.22.0`), set `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318`, and open `http://localhost:16686`. It shows span trees and timings well, but knows nothing about prompts or tokens. It keeps traces in memory by default, so they disappear when it stops.
- **Arize Phoenix** is built for LLM apps and runs without Docker: `uvx arize-phoenix serve`, then set the endpoint to `http://localhost:6006` and open the same address. It adds LLM-specific views, annotations and datasets. Phoenix's richest views use its own OpenInference attribute names, so check what it shows for `gen_ai.*` spans.
- **Langfuse** is open source (MIT core) with a free cloud tier, or self-hosted with Docker Compose. Point the endpoint at `https://cloud.langfuse.com/api/public/otel` (or your own server) and add an `Authorization` header built from your project keys in `OTEL_EXPORTER_OTLP_HEADERS`. It has prompt, dataset and scoring features that the next lesson uses.

For the Trace Detective project, any of them works. Keep `SPANS_FILE` on as well: the next lesson's scripts read that file, and Phoenix gives you the trace-tree screenshot the project asks for even on a machine without Docker. Managed clouds have their own trace viewers that accept OpenTelemetry data too, such as Google Cloud Trace for a service on Cloud Run. Whichever you pick, give each service a meaningful `service.name`, and put the backend's keys in your platform's secret settings, never in code.

### Sampling

Every span costs a little CPU, network and storage. At 10 requests a minute, keep everything. At 1,000 requests a second, storing every trace becomes expensive, and you start **sampling**: keeping only some traces.

**Head sampling** decides at the start of a trace, before anything has happened. `TraceIdRatioBased(0.1)` keeps a trace when its random trace ID falls in the lowest 10%, so the choice is consistent: every span of a kept trace is kept. `ParentBased` makes child spans, and other services that receive your `traceparent` header, follow the parent's decision, so you never get half a trace. If you don't pass a sampler in code, the standard variables `OTEL_TRACES_SAMPLER=parentbased_traceidratio` and `OTEL_TRACES_SAMPLER_ARG=0.1` do the same thing.

The weakness of head sampling is that it's blind. Drop 90% of traces and you drop 90% of your errors, slow requests and thumbs-down answers, which are exactly the ones you want to read. **Tail sampling** decides after the trace is finished: keep every trace with an error, every trace slower than 10 seconds, plus 5% of the rest. It needs all of a trace's spans in one place before deciding, which usually means running the **OpenTelemetry Collector**, a separate service that receives spans, filters them and forwards them to your backend.

A practical rule for LLM apps: keep 100% of traces until volume or cost forces you to sample, since model calls are expensive enough that tracing them is cheap by comparison. When you do sample, note that logs are not sampled. The trace ID is still on every log line even when that trace wasn't kept, so metrics and logs stay complete.

### Privacy and cost

Traces of an LLM app are full of what users typed and what the model said back. Treat them as user data:

- **Decide what you store.** Metadata (tokens, latency, model, status) is always safe to keep. Content is where the value and the risk both live. Record it on purpose, in known attributes, not by accident in a log line.
- **Redact before export.** The `redact` function above masks email addresses and phone numbers with regular expressions. That's a start, not a guarantee. Names and addresses slip through simple patterns, so for sensitive domains use a dedicated tool such as [Microsoft Presidio](https://microsoft.github.io/presidio/), or don't store content at all. Langfuse and Phoenix can also mask data on the client side before it leaves your app.
- **Never record secrets.** API keys, passwords and authorization headers must never be in a span or a log. The OWASP Logging Cheat Sheet lists what to exclude.
- **Set retention and access.** Keep content for as long as you need it to debug and build evals, perhaps 30 days, and limit who can read it. Say what you store in your privacy notes.
- **Cap the size.** One agent trace can hold megabytes of tool results. Truncate long attributes (the `[:4000]` above), as the Anthropic SDK does with its content limit, so a single request can't blow up your storage bill.

Cost runs in two directions here. Your traces *measure* cost: with token counts and prices on every span, you can answer "which route, user or prompt version costs the most?", which the Cost and Latency section builds on. Note that the price table in `app.py` is a copy that goes stale; keep it in one place and update it when prices change. Your traces also *have* a cost: storage and the backend's own pricing. Sampling, truncation and retention limits are how you keep that second bill small.

### On other providers

Everything in this lesson except the SDK's built-in spans is provider-neutral. Structured logs, request IDs, OTel spans, exporters, sampling and redaction work the same whatever model you call. The GenAI conventions exist precisely so that a trace from OpenAI, Gemini or a local model looks the same in your backend: only `gen_ai.provider.name` and the model names change. What differs is who creates the model-call span. OpenAI's Python SDK doesn't trace itself; you add the `opentelemetry-instrumentation-openai-v2` package, or OpenInference's instrumentors, and call its `instrument()` method once at startup. Content capture is opt-in there too, through an environment variable. Token counts also live in different places: OpenAI's Chat Completions API reports `usage.prompt_tokens` and `usage.completion_tokens`, so read them carefully when you compute cost by hand. A local model behind [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) can be traced with the same OpenAI instrumentation, which makes it a free way to practice this lesson. See the [OpenAI text generation guide](https://platform.openai.com/docs/guides/text) for the response and usage shapes.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [OpenTelemetry observability primer](https://opentelemetry.io/docs/concepts/observability-primer/) for the core vocabulary.
   - Read the whole page, especially the parts on logs, spans and distributed traces.
1. Work through the [OpenTelemetry Python getting started guide](https://opentelemetry.io/docs/languages/python/getting-started/). It builds a small instrumented app step by step and shows spans in the console before you connect a backend.
   - Then read [Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) and [Sampling](https://opentelemetry.io/docs/concepts/sampling/). The sampling page explains head and tail sampling with diagrams.
1. Read the [GenAI client inference conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/client-inference.md) to see the standard span and attribute names for model calls.
   - Find the attributes for tokens, model name, finish reasons and errors, and the section on capturing content. Note the "Development" status labels; you don't need to memorize anything.
1. Read [OpenTelemetry in the Claude docs](https://platform.claude.com/docs/en/manage-claude/opentelemetry) to see which spans the Anthropic SDK creates, and how its content mode works.
1. Pick a backend and send it traces:
   - Locally, follow [Get started with Phoenix](https://arize.com/docs/phoenix/get-started) (no Docker needed) or [Jaeger's getting started page](https://www.jaegertracing.io/docs/latest/getting-started/).
   - Or follow the [Langfuse getting started guide](https://langfuse.com/docs/observability/get-started) and its [OpenTelemetry endpoint page](https://langfuse.com/integrations/native/opentelemetry) to use the free cloud tier.
1. Practice: build `obs.py` and `app.py` from this lesson, then extend them.
   - Send 20 questions, including one with a made-up email address in it. Find a trace in your backend by the `x-trace-id` header, and find all its log lines by `request_id`. Confirm the email address appears in neither the logs nor the spans.
   - Make the model call fail (set a wrong API key) and check that the logs show an ERROR line and the trace shows red spans.
   - Add tracing with OTel to your Agent Loop From Scratch project, following the agent example. Run five queries and find the slowest span in each trace.
   - Set `TRACE_SAMPLE_RATIO=0.25`, send 40 requests, and count how many traces arrive.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What question does each of logs, metrics and traces answer best?](#logs-metrics-and-traces)
- [Why should every log line carry a request ID and a trace ID, and how does a ContextVar help?](#structured-logs-with-request-ids)
- [What are a tracer provider, an exporter and context propagation for?](#opentelemetry-in-five-ideas)
- [Why doesn't the answer_question span repeat the token counts?](#instrumenting-a-fastapi-service)
- [Why are prompt and response attributes opt-in in the GenAI conventions?](#the-genai-semantic-conventions)
- [What's the difference between head and tail sampling, and why is head sampling risky for finding failures?](#sampling)
- [What should you never store in traces, and how do you limit what you do store?](#privacy-and-cost)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [OpenTelemetry for Python](https://opentelemetry.io/docs/languages/python/) is the reference for creating spans by hand, and its [instrumentation page](https://opentelemetry.io/docs/languages/python/instrumentation/) covers span events, links and status.
- The [FastAPI instrumentation docs](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html) list its options, such as excluding health-check URLs from tracing.
- The [OTLP exporter configuration page](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/) lists every `OTEL_EXPORTER_OTLP_*` environment variable.
- The [W3C Trace Context specification](https://www.w3.org/TR/trace-context/) defines the `traceparent` header, if you want to see exactly what crosses the wire.
- The [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) covers what to log, what never to log, and how to protect logs.
- [Langfuse masking](https://langfuse.com/docs/observability/features/masking) shows how to redact data on the client before traces leave your app.
- [OpenInference](https://github.com/Arize-ai/openinference) provides instrumentation for many model SDKs and frameworks, used by Phoenix and others.
- [Langfuse self-hosting](https://langfuse.com/self-hosting) explains how to run Langfuse on your own machine with Docker if you'd rather not send data to a cloud service.

