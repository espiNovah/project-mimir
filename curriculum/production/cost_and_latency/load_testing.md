### Introduction

Your app answers in 2 seconds when you try it. Will it still answer in 2 seconds when 200 people try it at once? You can't know by clicking around. **Load testing** means sending many simulated users at your app on purpose, measuring what happens to latency and errors as the load grows, and finding the part that breaks first, before real users find it for you.

LLM apps need load testing more than most, and they need it done differently. Each request is slow and streams for seconds. The real work happens at a model provider that rate-limits you. And every real request costs money, so a careless load test against the real API can cost more than a month of normal traffic. In this lesson you'll build a fake model server that behaves like the real thing for free, load-test your own service against it with Locust and k6, read the results as percentiles, find the bottleneck, and turn it all into a capacity estimate you can defend.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why LLM apps load-test differently from ordinary web apps.
- Using a fake model server to test your own service without paying.
- Writing and running load tests with Locust and k6.
- Reading p50, p95 and p99, and measuring time to first token.
- Closed and open load models, and why the difference changes your results.
- Finding the bottleneck: blocked event loops, concurrency limits and upstream rate limits.
- Making a simple capacity estimate with Little's law.

### Why LLM apps are different

A load test for an ordinary API sends thousands of fast requests and checks that the server keeps up. An LLM app breaks that picture in four ways:

- **Requests are slow and long-lived.** A typical web request finishes in 50 milliseconds. A streamed answer can take 5 to 30 seconds. So your app holds many more requests open at once, and limits that never mattered before, such as connections, worker slots and memory per request, suddenly do.
- **Streaming splits latency in two.** Users judge a chat app by how quickly the answer *starts*, the time to first token (TTFT), and then by how long it takes to finish. A load test that records only total time misses half the story.
- **The real bottleneck is often someone else's.** Your provider limits requests per minute and tokens per minute, as you saw in Tokens, Cost and Rate Limits and Batching, Rate Limits and Fallbacks. Past those limits you get `429` errors, however fast your own server is.
- **Real calls cost real money.** A 10-minute test at 20 requests per second is 12,000 model calls. Even with a cheap model and short prompts that can be tens of dollars, and with a large model, hundreds.

The answer to the last two is the same: for most load testing, **replace the model with a fake** that streams like the real one, at a speed and limit you choose. You're testing *your* code: your FastAPI app, your queue, your database, your concurrency limits. The provider has its own load testers.

### A fake model server

You met fakes in Testing with pytest and Timeouts, Retries and Rate Limits: stand-ins that behave like a slow or unreliable dependency. For a load test, the fake has to be a real HTTP server, because you want the real SDK, real network calls and real streaming. Here is one that speaks the same streaming format as the Claude Messages API, so the official SDK can call it without knowing the difference.

```python
# fake_model.py: a stand-in for a model API that streams like the real one, for free.
# It speaks the Messages API's streaming format, so the real anthropic SDK can call it.
import asyncio
import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

TTFT = float(os.environ.get("FAKE_TTFT_S", "0.6"))           # wait before the first token
TOKENS_PER_S = float(os.environ.get("FAKE_TOKENS_PER_S", "80"))
OUTPUT_TOKENS = int(os.environ.get("FAKE_OUTPUT_TOKENS", "150"))
MAX_IN_FLIGHT = int(os.environ.get("FAKE_MAX_IN_FLIGHT", "40"))  # a crude upstream limit

app = FastAPI()
in_flight = 0


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/v1/messages")
async def messages(request: Request):
    global in_flight
    body = await request.json()
    if in_flight >= MAX_IN_FLIGHT:  # behave like a provider that is rate-limiting you
        return JSONResponse(
            {"type": "error", "error": {"type": "rate_limit_error", "message": "fake 429"}},
            status_code=429, headers={"retry-after": "1"},
        )
    in_flight += 1
    if not body.get("stream"):  # a non-streaming call waits for the whole answer
        try:
            await asyncio.sleep(TTFT + OUTPUT_TOKENS / TOKENS_PER_S)
        finally:
            in_flight -= 1
        return {"id": "msg_fake", "type": "message", "role": "assistant", "model": body["model"],
                "content": [{"type": "text", "text": "tok " * OUTPUT_TOKENS}],
                "stop_reason": "end_turn", "stop_sequence": None,
                "usage": {"input_tokens": 20, "output_tokens": OUTPUT_TOKENS}}

    async def stream():
        global in_flight
        try:
            yield sse("message_start", {"type": "message_start", "message": {
                "id": "msg_fake", "type": "message", "role": "assistant",
                "model": body["model"], "content": [], "stop_reason": None,
                "stop_sequence": None, "usage": {"input_tokens": 20, "output_tokens": 0}}})
            yield sse("content_block_start", {"type": "content_block_start", "index": 0,
                                              "content_block": {"type": "text", "text": ""}})
            await asyncio.sleep(TTFT)                      # the model "reads the prompt"
            for i in range(OUTPUT_TOKENS):
                yield sse("content_block_delta", {"type": "content_block_delta", "index": 0,
                                                  "delta": {"type": "text_delta", "text": f"tok{i} "}})
                await asyncio.sleep(1 / TOKENS_PER_S)       # the model "writes"
            yield sse("content_block_stop", {"type": "content_block_stop", "index": 0})
            yield sse("message_delta", {"type": "message_delta",
                                        "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                                        "usage": {"output_tokens": OUTPUT_TOKENS}})
            yield sse("message_stop", {"type": "message_stop"})
        finally:
            in_flight -= 1                                  # runs even if the client hangs up

    return StreamingResponse(stream(), media_type="text/event-stream")
```

The event names are the server-sent events you saw in Streaming Responses. Three settings make it realistic: a delay before the first token, a steady token rate after that, and a cap on requests in flight that answers `429` with a `retry-after` header, like a provider's rate limit. Set them from what you've measured on the real API: look at the TTFT and tokens per second in your traces from the Observability section.

### The service under test

This is a stripped-down version of the kind of API you built in the Backend section: one endpoint that streams a model's answer back to the caller. It also has a second endpoint with a planted bug that you'll find with the load test.

```python
# app.py: the service under test. It streams a model's answer back to the caller.
import asyncio
import os

import anthropic
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
MAX_UPSTREAM = int(os.environ.get("MAX_UPSTREAM", "30"))  # stay under the provider's limit

# Both clients read ANTHROPIC_BASE_URL, so pointing them at the fake server costs nothing.
client = anthropic.AsyncAnthropic(timeout=60.0, max_retries=2)
sync_client = anthropic.Anthropic(timeout=60.0, max_retries=2)
upstream = asyncio.Semaphore(MAX_UPSTREAM)
app = FastAPI()


class Ask(BaseModel):
    question: str


@app.post("/ask")
async def ask(body: Ask):
    async def answer():
        # Requests beyond MAX_UPSTREAM wait at the semaphore instead of getting 429s.
        async with upstream, client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": body.question}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    return StreamingResponse(answer(), media_type="text/plain")


@app.post("/ask-blocking")
async def ask_blocking(body: Ask):
    # A planted bug: a synchronous call inside "async def" freezes the event loop,
    # so this worker can serve only one request at a time.
    response = sync_client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": body.question}],
    )
    return {"answer": "".join(b.text for b in response.content if b.type == "text")}
```

The trick that makes this free is `ANTHROPIC_BASE_URL`. The SDK sends its requests to whatever URL that variable holds, so you can point the exact code you deploy at the fake server without changing a line. The semaphore is the concurrency limit from Timeouts, Retries and Rate Limits: at most 30 calls to the model at once, with the rest waiting their turn.

Set up a project and start the two servers, each in its own terminal:

```bash
uv init loadtest && cd loadtest
uv add "fastapi[standard]" anthropic locust

# terminal 1: the fake model
uv run uvicorn fake_model:app --port 8001

# terminal 2: your service, pointed at the fake (the key only has to be non-empty)
ANTHROPIC_BASE_URL=http://localhost:8001 ANTHROPIC_API_KEY=fake uv run uvicorn app:app --port 8000
```

Check it with `curl -N -X POST localhost:8000/ask -H 'content-type: application/json' -d '{"question": "hi"}'`. The `-N` flag turns off buffering, so you should see `tok0 tok1 tok2 ...` stream in after a short pause.

### Load testing with Locust

[Locust](https://docs.locust.io/en/stable/) is a free load-testing tool where you describe user behavior in plain Python. Each simulated **user** runs your tasks in a loop, waiting a little between them, just as a real person reads an answer before asking the next question.

```python
# locustfile.py: simulated users who ask a question and read the streamed answer.
import os
import random
import time

from locust import HttpUser, between, task
from requests.exceptions import RequestException

QUESTIONS = [
    "What is your refund policy?",
    "How do I reset my password?",
    "Summarize the onboarding guide in three bullets.",
]
ASK_PATH = os.environ.get("ASK_PATH", "/ask")  # try /ask-blocking to see the bug


class ChatUser(HttpUser):
    wait_time = between(1, 3)  # "think time" between one user's requests

    def record(self, name: str, started: float, error: Exception | None = None) -> None:
        # Report a custom measurement so it gets its own row and percentiles in Locust.
        self.environment.events.request.fire(
            request_type="STREAM", name=name, response_time=(time.perf_counter() - started) * 1000,
            response_length=0, exception=error, context={},
        )

    @task
    def ask(self):
        started = time.perf_counter()
        got_first = False
        with self.client.post(ASK_PATH, json={"question": random.choice(QUESTIONS)},
                              stream=True, catch_response=True, name=f"{ASK_PATH} (headers)") as resp:
            if resp.status_code != 200:
                resp.failure(f"status {resp.status_code}")
                self.record("total", started, Exception(f"status {resp.status_code}"))
                return
            try:
                for chunk in resp.iter_content(chunk_size=None):
                    if chunk and not got_first:
                        got_first = True
                        self.record("time to first token", started)
            except RequestException as e:  # the stream broke after a 200: still a failure
                resp.failure(f"stream broke: {e!r}")
                self.record("total", started, e)
                return
            resp.success()
        self.record("total", started, None if got_first else Exception("empty answer"))
```

Why the custom measurements? With `stream=True`, Locust's own timer stops when the response *headers* arrive, and a streaming server sends its headers right away. That row, labeled "(headers)", would tell you every request takes 5 milliseconds. So the script times two things itself: when the first chunk of the answer arrives (TTFT) and when the last one does (total). It also counts a stream that breaks halfway as a failure, which matters more than you'd think, as you'll see below.

Run it in a third terminal with `uv run locust -f locustfile.py -H http://localhost:8000` and open `http://localhost:8089` for a live web UI with charts. For a repeatable run without the UI, which is what you'd put in a README or CI job:

```bash
uv run locust -f locustfile.py --headless -u 50 -r 10 -t 1m -H http://localhost:8000 --only-summary
```

That's 50 users (`-u`), started at 10 per second (`-r`, the ramp-up), for one minute (`-t`). Add `--csv results` to save the numbers to files.

### Reading percentiles

Here is part of the output from a 50-user run on a laptop:

```text
Name                   # reqs  # fails |  50%   90%   95%   99%  100%
time to first token       206        0 |  610   770   890  1100  1300
total                     186        0 | 2600  2700  2800  3100  3300
```

The columns are **percentiles**, in milliseconds. The 50th percentile (**p50**, the median) means half of the requests were faster than this. **p95** means 95% were faster, and 1 in 20 was slower. **p99** is the slowest 1 in 100. The last column is the single slowest request.

Always read percentiles, not the average. An average blends many fast requests with a few terrible ones into a number that describes nobody. And the slow tail matters more than it looks: a user who sends 20 messages in a session will very likely hit your p95 at least once, so p95 is close to "what every regular user experiences sometimes." Most teams set latency targets on p95 or p99.

In this run, TTFT p50 is 610 ms, close to the fake's 600 ms delay, so your service adds almost nothing. Total p50 is 2.6 seconds: 0.6 seconds of waiting plus 150 tokens at 80 per second. Nothing failed. At 50 users, this app is healthy.

Percentiles need enough samples to mean anything. With 40 requests, "p99" is just the slowest one or two, so run long enough to collect hundreds.

### Finding the bottleneck

Now push. Here's what happened on three more runs. These aren't hypothetical numbers; you can reproduce them with the scripts above.

**150 users.** No failures, but TTFT p50 jumped from 610 ms to 8,200 ms, and throughput flattened at about 11 requests per second, no matter how many users were added. That flat line is the signature of a bottleneck: some resource is full, and extra work waits in a queue. Here the resource is the semaphore. 30 slots, each held for about 2.6 seconds, can serve at most 30 / 2.6 = 11.5 requests per second. Everything beyond that waits, and the wait shows up as TTFT.

**150 users with `MAX_UPSTREAM=200`.** Raising the semaphore past the fake provider's limit of 40 removed the queue, and half of all requests failed. Worse, they failed *after* a `200 OK`. A streaming endpoint sends its status and headers before it calls the model, so when the provider answered `429` and the SDK's retries ran out, the app could only cut the stream short. A load test that checks only status codes would report zero errors here. (One fix is to wait for the model's first event before you start the response, so you can still return a proper `503` with `Retry-After`.)

**20 users on `/ask-blocking`.** Throughput collapsed to 0.4 requests per second, with p95 at 25 seconds. The synchronous SDK call inside an `async def` endpoint blocks the event loop, the single thread that serves every request in that worker, for the whole 2.5 seconds of each call. Every other request waits behind it. It is one of the most common performance bugs in FastAPI apps, and it's invisible when you test alone. The fix is the async client, as in `/ask`, or a plain `def` endpoint, which FastAPI runs in a thread pool.

Common bottlenecks in LLM services, roughly in the order you'll meet them:

- **Upstream limits:** the provider's requests-per-minute and tokens-per-minute limits, or your own semaphore in front of them.
- **Blocking calls in async code:** a sync model client, `requests`, or a slow database driver inside `async def`.
- **Worker and connection limits:** too few Uvicorn workers, or a database connection pool smaller than the number of requests in flight.
- **CPU-heavy work in the request path:** parsing big PDFs, computing embeddings locally or tokenizing huge documents.
- **Memory:** many long streams, each holding a big context, can exhaust a small container.

To find which one you've hit, change one thing at a time and rerun the same test. Watch the server while it runs: CPU and memory (`docker stats` if you run it under Compose), and your traces, which show where each request spent its time.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Make the load generator the fast part

Locust runs on one CPU core per process. If its CPU is near 100%, the load generator is the bottleneck and your numbers are wrong. Locust warns you about this in its output. Lower the user count, or run several worker processes with `--processes`.

</div>

### Open and closed load

Locust uses a **closed** model: a fixed number of users, each waiting for an answer before sending the next question. When your server slows down, Locust's users slow down with it, so the offered load drops just when the server struggles. That's polite, and it hides problems. Real traffic is **open**: new people arrive at the same rate whether or not you're slow.

[k6](https://grafana.com/docs/k6/latest/) is a free load-testing tool from Grafana Labs that makes an open model easy. You write the test in JavaScript and run it with the `k6` command-line tool.

```javascript
// load.js: send a steady 5 requests per second, whether or not the server keeps up.
import http from "k6/http";
import { check } from "k6";

export const options = {
  scenarios: {
    steady: {
      executor: "constant-arrival-rate", // an "open" model: new requests keep arriving
      rate: 5,
      timeUnit: "1s",
      duration: "1m",
      preAllocatedVUs: 20,
      maxVUs: 100,
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],        // fewer than 1% errors
    http_req_duration: ["p(95)<4000"],     // full answer within 4 s for 95% of requests
  },
};

export default function () {
  const res = http.post(
    "http://localhost:8000/ask",
    JSON.stringify({ question: "How do I reset my password?" }),
    { headers: { "Content-Type": "application/json" }, timeout: "60s" },
  );
  check(res, { "status is 200": (r) => r.status === 200, "has an answer": (r) => r.body.length > 0 });
}
```

Run it with `k6 run load.js`. At 5 requests per second the thresholds pass, with p95 at about 2.8 seconds. At 15 per second, more than the app's 11.5 ceiling, p95 rises to about 8 seconds, k6 reports **dropped iterations** (requests it wanted to send but had no free virtual user for), and the latency threshold fails. k6 exits with a non-zero code when a threshold fails, so the same script can gate a deploy in CI.

The trade-off: k6's `http.post` reads the whole response before returning, so it measures total time but not TTFT for a streamed answer. Use Locust when you need TTFT, and k6 when you want a fixed arrival rate and pass/fail thresholds. Both are fine tools; pick one and get good at it.

### A capacity estimate

Load testing tells you what your app can do. A **capacity estimate** tells you what it *needs* to do. Put the two together and you know whether you're ready for launch day.

The tool is **Little's law**: the average number of requests in flight equals the arrival rate times the average time each one takes.

```text
in flight = requests per second x seconds per request
```

A worked example. You expect 5,000 daily users, each asking about 6 questions, so 30,000 requests a day. Traffic isn't even: suppose the busiest hour carries 15% of the day, which is 4,500 requests, or 1.25 per second. Each request takes about 2.6 seconds, so on average 1.25 x 2.6 = about 3.3 requests are in flight. Plan for spikes of at least three times that, so about 4 requests per second and 10 in flight. The app above, capped at 30 upstream calls and 11.5 requests per second, has comfortable room.

Then check the provider's limits, because they're usually what binds first. Say each request sends 2,000 input tokens and gets 300 output tokens back. At 4 requests per second, that's 240 requests a minute, 480,000 input tokens a minute and 72,000 output tokens a minute. Compare those with your account's limits on the provider's rate limits page. If you're over, you'll need a higher tier, prompt caching (cached tokens often don't count toward input limits on the Claude API, but check your provider), shorter prompts, or a queue that smooths the spikes, as in Job Queues and Workers.

Finally, cost: 30,000 requests a day, times the cost per request from your traces, times 30. If that number surprises you, the Cut the Bill project is next.

### Testing against the real API

The fake answers questions about *your* system. Once in a while you also want to know how the real provider behaves at your expected load: its real TTFT under concurrency, and where its limits actually bite. Do this deliberately:

- **Estimate the cost first.** Requests per second x duration in seconds x cost per request. Write it down before you press start.
- **Keep it short and small.** A few minutes at your expected peak, not an hour at ten times it.
- **Use a separate API key and workspace** with a low spending limit, so a runaway test can't empty your main account.
- **Use the cheap model and short outputs** unless you specifically need to measure the expensive one.
- **Never load-test production.** Point the test at a staging environment, as in Environments and Releases, so real users don't share your rate limit with the test.

### On other providers

The load-testing method is provider-neutral: Locust, k6, percentiles, Little's law and the bottleneck hunt work the same whatever model sits behind your app. What changes is the fake. `fake_model.py` imitates the Claude Messages streaming format, so it works with the `anthropic` SDK. To test an app that uses the OpenAI SDK, the fake must instead serve `/v1/chat/completions` and stream `data:` lines of `chat.completion.chunk` objects ending with `data: [DONE]`, as described in OpenAI's [streaming guide](https://platform.openai.com/docs/guides/streaming-responses); you then point the client at it with `base_url`. Rate limits differ too: each provider measures requests and tokens per minute in its own way and reports them in different response headers, so set your fake's limit from your own provider's numbers. If you serve an open model yourself, for example with [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), the upstream is now your own hardware, so load-test it directly: tokens per second per request drops as concurrent requests share the GPU, and that curve is your real capacity.

```python
# The same app call with the OpenAI SDK, pointed at a fake or local server.
import os

from openai import AsyncOpenAI

MODEL = os.environ["MIMIR_MODEL"]  # an OpenAI or local model name
client = AsyncOpenAI(base_url="http://localhost:8001/v1", api_key="fake")

async def answer(question: str):
    stream = await client.chat.completions.create(
        model=MODEL, stream=True, messages=[{"role": "user", "content": question}],
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Locust's [Quick start](https://docs.locust.io/en/stable/quickstart.html) and [Writing a locustfile](https://docs.locust.io/en/stable/writing-a-locustfile.html). They explain users, tasks, wait times and `catch_response`, which the script above relies on.
   - Skim [Configuration](https://docs.locust.io/en/stable/configuration.html) for the headless and `--csv` options.
1. Read k6's [Open and closed models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/) page. It's the clearest short explanation of why a closed load test can hide a slow server.
1. Read FastAPI's [Concurrency and async / await](https://fastapi.tiangolo.com/async/) page, which explains exactly why `/ask-blocking` is slow and when to use `def` instead of `async def`.
1. Practice: reproduce the four runs in this lesson.
   - Run the 50-user and 150-user Locust tests, the `MAX_UPSTREAM=200` run, and `ASK_PATH=/ask-blocking`. Save each result with `--csv`, and write a short table of p50 and p95 TTFT, p95 total time, requests per second and failure rate.
   - Fix `/ask-blocking` with the async client, rerun the test, and show that its throughput now matches `/ask`.
1. Practice: load-test one of your own apps, such as your LLM-Powered API or Chat With Your Docs.
   - Point it at `fake_model.py` with `ANTHROPIC_BASE_URL`, with the fake's TTFT and token rate set from your real traces. If your app uses another provider's SDK, adapt the fake as described above.
   - Find the user count where p95 TTFT crosses 2 seconds, name the bottleneck, and write a one-paragraph capacity estimate for a launch with 1,000 daily users, including tokens per minute against your provider's limits.
   - Add the results table and the estimate to the project's README. Cut the Bill asks for a p95 load-test result, and this is where it comes from.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why do LLM apps need a different approach to load testing than ordinary web APIs?](#why-llm-apps-are-different)
- [How can you load-test your service's real code without paying for model calls?](#a-fake-model-server)
- [Why does the locustfile time the first token and the last token itself instead of trusting Locust's own timer?](#load-testing-with-locust)
- [What do p50, p95 and p99 mean, and why not report the average?](#reading-percentiles)
- [What does it look like when a test hits a bottleneck, and what were the three bottlenecks found in this lesson?](#finding-the-bottleneck)
- [What is the difference between an open and a closed load model?](#open-and-closed-load)
- [How do you use Little's law to estimate how many requests will be in flight at peak?](#a-capacity-estimate)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Constant arrival rate](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/) in the k6 docs explains every option of the executor used above, and links to the other executors, such as ramping arrival rate.
- [Thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/) in the k6 docs shows how to turn latency and error targets into pass/fail checks for CI.
- [Event hooks](https://docs.locust.io/en/stable/extending-locust.html) in the Locust docs covers the `request` event used to report TTFT, and other ways to extend Locust.
- [The USE Method](https://www.brendangregg.com/usemethod.html) by Brendan Gregg is a simple checklist for finding a bottleneck: for every resource, check utilization, saturation and errors.
- [Rate limits](https://platform.claude.com/docs/en/api/rate-limits) in the Claude docs lists how request and token limits are measured, which you need for the capacity estimate.
