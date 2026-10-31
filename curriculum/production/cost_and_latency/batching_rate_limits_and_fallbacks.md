### Introduction

Model APIs are shared services. They limit how much you can send, they occasionally get overloaded, and sometimes they go down. In Timeouts, Retries and Rate Limits you learned to survive a single failed call: a deadline, a few retries with backoff and jitter, respect for `Retry-After`, and a per-user rate limit on your own API. That's the foundation, and this lesson doesn't repeat it.

This lesson is about the whole system under real load. Your live users, your nightly evals and your data backfills all draw from the same provider limits, so you need to pace your own traffic instead of bouncing off `429` errors. Work that can wait should go through a batch API at half the price. And when retries run out, a production app needs a plan: another model, another provider, or a smaller answer that is still useful, rather than an error page.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How provider rate limits are measured, and why all your traffic shares them.
- Client-side rate limiting with a token bucket, and reading rate-limit headers.
- Spend budgets per user and per feature.
- Batch APIs for large jobs that don't need an instant answer.
- Fallback chains across models and providers.
- Circuit breakers that stop you from hammering a failing dependency.
- Graceful degradation and load shedding.

### Throughput is a shared budget

Recall from Tokens, Cost and Rate Limits that providers limit **requests per minute (RPM)** and tokens per minute, and that Anthropic counts **input tokens per minute (ITPM)** and **output tokens per minute (OTPM)** separately, per model class. A few details matter once you run a real service:

- **The limit belongs to your organization, not your process.** Every worker, every API instance, the eval you started from your laptop and the backfill job someone forgot about all spend the same budget. A nightly eval that fires 2,000 requests at 2 a.m. can starve users in another time zone.
- **Limits refill continuously.** The Claude API uses a token bucket (the same algorithm you built for your own API in Timeouts, Retries and Rate Limits), so your capacity refills steadily rather than resetting at the top of each minute. A burst can use the whole bucket at once, and then you wait.
- **Not every token counts the same.** On most Claude models, cache reads don't count toward ITPM, so good prompt caching from Caching and Model Choice also raises your throughput. And Claude counts only the output tokens actually produced toward OTPM, so a high `max_tokens` costs you nothing there. Other providers count differently, and some reserve your full `max_tokens` against the limit up front, so read your provider's rules before you plan capacity.
- **The provider tells you where you stand.** Every Claude API response carries headers such as `anthropic-ratelimit-requests-remaining`, `anthropic-ratelimit-input-tokens-remaining` and `anthropic-ratelimit-input-tokens-reset`. The SDK hides headers by default, but `with_raw_response` exposes them:

```python
raw = await client.messages.with_raw_response.create(**request)  # async client
left = int(raw.headers.get("anthropic-ratelimit-input-tokens-remaining", "0"))
response = await raw.parse()  # the same Message that create() returns
```

Record the remaining numbers on your traces or as metrics. A graph of "input tokens remaining" that keeps touching zero at the same hour every day tells you to move work, cache more, or ask for a higher tier, long before users see errors.

### Pacing yourself on the client

The `429` path works, but it's wasteful. Each rejected request is a round trip that did nothing, and when a hundred workers all hit the limit, they all back off and come back together. A better plan is **client-side rate limiting**: your code keeps its own estimate of the budget and waits *before* sending, so requests leave at a rate the provider will accept.

You already have one tool for this. The `asyncio.Semaphore` from Async Basics caps how many calls are *in flight*. That protects you from opening 500 connections at once, but it doesn't cap tokens: ten requests in flight that each send 50,000 tokens of documents can blow through an input-token limit in seconds. To pace tokens, use a token bucket on the client too:

```python
# throttle.py: a client-side limiter that paces requests and input tokens per minute.
import asyncio
import json
import time


class TokenBudget:
    """Two token buckets (requests and input tokens) that refill continuously, like the provider's."""

    def __init__(self, rpm: int, itpm: int, clock=time.monotonic, sleep=asyncio.sleep):
        self.capacity = {"requests": float(rpm), "tokens": float(itpm)}
        self.level = dict(self.capacity)  # start full
        self.clock, self.sleep = clock, sleep
        self.updated = clock()
        self.lock = asyncio.Lock()

    def _refill(self) -> None:
        now = self.clock()
        for name, cap in self.capacity.items():
            self.level[name] = min(cap, self.level[name] + (now - self.updated) * cap / 60)
        self.updated = now

    async def acquire(self, tokens: int) -> None:
        tokens = min(tokens, int(self.capacity["tokens"]))  # a huge request must still be able to go
        async with self.lock:  # (1) waiters are served in order, so nobody starves
            while True:
                self._refill()
                short_r = 1 - self.level["requests"]
                short_t = tokens - self.level["tokens"]
                if short_r <= 0 and short_t <= 0:
                    self.level["requests"] -= 1
                    self.level["tokens"] -= tokens
                    return
                # (2) sleep exactly until both buckets have enough
                await self.sleep(60 * max(short_r / self.capacity["requests"],
                                          short_t / self.capacity["tokens"]))

    def settle(self, estimated: int, actual: int) -> None:
        """(3) Replace the estimate with real usage once the response arrives."""
        self.level["tokens"] = min(self.capacity["tokens"], self.level["tokens"] + estimated - actual)


def estimate_tokens(request: dict) -> int:
    return len(json.dumps(request)) // 3  # rough and deliberately high; count_tokens is exact


async def paced_call(client, budget: TokenBudget, upstream: asyncio.Semaphore, request: dict):
    estimated = estimate_tokens(request)
    await budget.acquire(estimated)
    async with upstream:  # still cap requests in flight with a semaphore
        response = await client.messages.create(**request)
    u = response.usage  # (4) cache reads don't count toward ITPM on most Claude models
    budget.settle(estimated, u.input_tokens + (u.cache_creation_input_tokens or 0))
    return response
```

The numbered comments:

1. **One waiter at a time.** The lock means the first caller waits for its tokens while the others queue behind it. Without it, a stream of small requests could keep jumping ahead of one big one forever.
1. **Sleep the exact shortfall.** If you're 6,000 tokens short on a 60,000-per-minute bucket, you need 6 seconds of refill. No polling, no guessing.
1. **Settle up.** You can't know the exact token count before sending. Estimate high, then give back the difference when the real `usage` arrives. For an exact count before sending, the token counting endpoint from Long Context and Context Engineering works too, at the cost of one extra (free) call.
1. **Count what the provider counts.** Fresh input and cache writes count toward Claude's ITPM; cache reads don't. If your provider counts differently, change this line.

Set the bucket to about 80% of your real limit, leaving headroom for the clock drift between your estimate and the provider's, and for anything else using the same key. Keep the SDK's own retries on (or your tenacity loop from Timeouts, Retries and Rate Limits) for the `429`s that still slip through; the limiter makes them rare, not impossible. And if several processes share the limit, they must share one bucket, which means keeping the counts in Redis, exactly as you did for your per-user limit.

Give interactive traffic priority. The simplest way is to split the budget: live requests get one bucket sized for your peak, and background work (evals, backfills, reindexing) gets a smaller one, or a separate workspace with its own limit. A backfill that takes twice as long is fine; a chat that stalls is not.

### Spend budgets per user and per feature

Rate limits protect throughput. **Spend budgets** protect your bank account. The per-user limit you built in Timeouts, Retries and Rate Limits counted requests, but requests vary wildly in cost: a user who pastes a 300-page PDF into every question can cost a hundred times more than one who asks short questions, at the same request rate.

So track dollars, not just requests. After each call, compute its cost from `usage` (you've done this since Agent Cost and Latency) and add it to a counter keyed by user and day, such as `spend:{user_id}:{date}` in Redis with a two-day expiry. Before each call, check the counter. Do the same per feature, so that one runaway feature can't eat the whole month's budget, and set an overall daily ceiling that pages someone when crossed, using the alerting from Alerting and Incidents.

What happens at the limit is a product decision, and the best answers are gentler than a hard "no":

- **Near the limit**, switch the user to the cheaper configuration from your cost/quality table, or shorten answers.
- **At the limit**, return a clear message with the time their budget resets, the way a `429` carries `Retry-After`.
- **For paying customers**, the limit might just trigger an alert and an email to sales.

Whatever you choose, log it on the trace. "Why was my answer worse today?" is a much easier support ticket when the trace says `budget_mode: reduced`.

### Batch APIs

Much of the work an AI team runs doesn't need an answer in seconds: nightly evals, classifying a million old support tickets, generating embeddings or summaries for a backfill, rerunning last month's traces through a new prompt. For this, providers offer **batch APIs**: you submit thousands of requests at once, the provider runs them when it has spare capacity, and you collect the results later, at a large discount.

On the Claude API this is the **Message Batches API** (a Claude feature; OpenAI's Batch API and Gemini's batch mode are the equivalents, covered below). At the time of writing, it costs 50% of the normal price, accepts up to 100,000 requests per batch, finishes most batches within an hour, and guarantees an answer within 24 hours or marks the request as expired. Prompt caching works inside a batch too, so a shared system prompt gets both discounts. The catch is the wait, so batches are for work no user is waiting on.

```python
# batch_eval.py  (run with: uv run batch_eval.py cases.jsonl)
# cases.jsonl has one {"id": ..., "input": ...} per line; prompt.md holds the system prompt.
import json
import os
import sys
import time
from pathlib import Path

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()
SYSTEM = [{"type": "text", "text": Path("prompt.md").read_text(encoding="utf-8"),
           "cache_control": {"type": "ephemeral"}}]  # caching and the batch discount combine


def make_request(case: dict) -> Request:
    return Request(custom_id=case["id"], params=MessageCreateParamsNonStreaming(
        model=MODEL, max_tokens=2000, system=SYSTEM,
        messages=[{"role": "user", "content": case["input"]}]))


def run_batch(cases: list[dict]) -> tuple[dict, list[dict]]:
    batch = client.messages.batches.create(requests=[make_request(c) for c in cases])
    print("submitted", batch.id)  # (1) save the ID: you can collect results later from any machine
    while batch.processing_status != "ended":
        time.sleep(60)
        batch = client.messages.batches.retrieve(batch.id)
        print(batch.request_counts)
    answers, retry, by_id = {}, [], {c["id"]: c for c in cases}
    for item in client.messages.batches.results(batch.id):  # (2) any order: key by custom_id
        result = item.result
        if result.type == "succeeded":
            answers[item.custom_id] = {
                "text": "".join(b.text for b in result.message.content if b.type == "text"),
                "usage": result.message.usage.model_dump()}
        elif result.type == "errored" and result.error.error.type == "invalid_request_error":
            print("fix this request, don't resubmit it:", item.custom_id)  # (3)
        else:  # a server error, or expired or canceled: safe to try again
            retry.append(by_id[item.custom_id])
    return answers, retry


if __name__ == "__main__":
    cases = [json.loads(line) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()]
    answers, retry = run_batch(cases)
    if retry:
        more, retry = run_batch(retry)  # one more round for the transient failures
        answers |= more
    Path("batch_answers.json").write_text(json.dumps(answers, indent=2), encoding="utf-8")
    print(f"{len(answers)}/{len(cases)} answered, {len(retry)} still failing")
```

Three things to notice. (1) A batch outlives your script: if your laptop sleeps, you can collect the results later by ID (the Claude API keeps them for 29 days). In production, store the ID in a job row, as in Job Queues and Workers, and let a scheduled task poll it. (2) Results come back in any order, so always match them by `custom_id`, never by position. (3) A request that was invalid will fail again, so only resubmit the transient failures.

Batch results include `usage`, so the cost comparison is easy: run the same eval live and as a batch, and compare. Remember that the batch discount means your cost report needs a "batch" flag per call, or it will overstate what your evals cost by a factor of two.

### Fallbacks when retries run out

Retries handle a blip. They don't handle a provider that's overloaded for twenty minutes, a model with an incident, or a rate limit you'll be stuck under until the next minute. A **fallback** is what you do when retries are exhausted: send the request somewhere else. A typical **fallback chain** looks like this:

1. **The primary**: your chosen model, with a short retry budget.
1. **Another model from the same provider**: often a smaller one, which runs on separate capacity and has separate rate limits. Easy to add, because the request format is identical.
1. **Another provider**: protects you from a whole-provider outage, at the price of maintaining a second prompt and a second SDK, as in Port Your Agent.
1. **A degraded response**: covered in the next section.

Only fall back on errors another route might not have: rate limits (`429`), overload (`529`, `503`), server errors and timeouts. A `400` means your request is wrong, and it will be just as wrong on every route. And split your patience: if a user will wait 30 seconds in total, two routes with one retry each fit; four retries on the primary don't leave time for anything else.

Fallbacks have costs you have to pay up front. The fallback model needs its own row in your cost/quality table from Caching and Model Choice, because a route you've never evaluated is a route you don't know is acceptable. Prompts tuned for one model often need adjusting for another. The fallback starts with a cold cache, so the first minutes on it are expensive. And you must log `route` on every trace and alert when the fallback rate rises, because a fallback that quietly serves 30% of traffic for a week is an outage nobody noticed. Streaming adds one catch: once a response has sent its first bytes to the user, you can't switch routes, so wait for the model's first event before you start your own response. Load Testing, the next lesson, shows what goes wrong when you don't.

Some providers offer a narrower kind of fallback built in. On recent Claude models, a request that a safety classifier declines comes back as a normal response with `stop_reason: "refusal"`, and the Claude API offers a server-side `fallbacks` option that reruns such requests on another model for you. That's a Claude feature for refusals only; it doesn't help when a model is overloaded or down, so you still need your own chain. Whatever your provider, check the stop reason before reading the content.

### Circuit breakers

A fallback chain alone has a flaw. If the primary is down, *every* request still tries it first, waits for its timeout and retries, and only then falls back. Each user pays the full delay, and your retries pile load onto a service that's already struggling.

A **circuit breaker**, named after the electrical part, fixes this. It watches each route's failures. After several failures in a row, it **opens**: requests skip that route entirely and go straight to the next one. After a cooldown it goes **half-open** and lets requests try the route again; one success **closes** it, and one more failure opens it again.

```python
# fallback.py: try routes in order, skip routes whose circuit is open, degrade when all fail.
import logging
import os
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import anthropic

log = logging.getLogger(__name__)
TRANSIENT = {408, 409, 429, 500, 502, 503, 504, 529}
DEGRADED = "Our assistant is very busy right now. Please try again in a minute."


@dataclass
class Breaker:
    threshold: int = 5  # failures in a row before the circuit opens
    cooldown_s: float = 30.0
    clock: Callable[[], float] = time.monotonic
    failures: int = 0
    opened_at: float | None = None

    def allow(self) -> bool:  # closed, or open long enough to try again (half-open)
        return self.opened_at is None or self.clock() - self.opened_at >= self.cooldown_s

    def record(self, ok: bool) -> None:
        if ok:
            self.failures, self.opened_at = 0, None
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = self.clock()  # open, or reopen after a failed half-open try


@dataclass
class Route:
    name: str
    call: Callable[[str], Awaitable[str]]
    breaker: Breaker = field(default_factory=Breaker)


def is_transient(exc: Exception) -> bool:
    if isinstance(exc, (anthropic.APIConnectionError, TimeoutError)):  # includes timeouts
        return True
    return getattr(exc, "status_code", None) in TRANSIENT  # works for other SDKs' errors too


async def answer(question: str, routes: list[Route]) -> dict:
    for route in routes:
        if not route.breaker.allow():
            log.warning("skipping %s: circuit open", route.name)
            continue
        try:
            text = await route.call(question)
        except Exception as exc:
            if not is_transient(exc):
                raise  # a bad request fails on every route: fix it instead
            route.breaker.record(ok=False)
            log.warning("route %s failed: %r", route.name, exc)
            continue
        route.breaker.record(ok=True)
        return {"text": text, "route": route.name, "fallback": route is not routes[0]}
    return {"text": DEGRADED, "route": "degraded", "fallback": True}


client = anthropic.AsyncAnthropic(max_retries=1, timeout=30.0)  # a small retry budget per route


def claude_route(model: str) -> Route:
    async def call(question: str) -> str:
        r = await client.messages.create(model=model, max_tokens=2000,
                                         messages=[{"role": "user", "content": question}])
        if r.stop_reason == "refusal":
            return "I can't help with that request."
        return "".join(b.text for b in r.content if b.type == "text")
    return Route(name=model, call=call)


ROUTES = [claude_route(os.environ.get("MIMIR_CAPABLE_MODEL", "claude-sonnet-5-5")),
          claude_route(os.environ.get("MIMIR_MODEL", "claude-haiku-5-5"))]
```

In your API route, call `await answer(question, ROUTES)` and put `route` and `fallback` on the trace. Because the routes are plain async functions, you test the chain with fakes, no network and no waiting, just as in Timeouts, Retries and Rate Limits:

```python
# test_fallback.py  (uv add --dev pytest pytest-asyncio, with asyncio_mode = "auto")
import anthropic
import httpx2

from fallback import Breaker, Route, answer


def overloaded():
    response = httpx2.Response(529, request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))
    return anthropic.APIStatusError("fake 529", response=response, body=None)


async def test_falls_back_then_skips_the_open_circuit():
    calls = []

    async def primary(q):
        calls.append("primary")
        raise overloaded()

    async def backup(q):
        calls.append("backup")
        return "ok"

    now = [0.0]
    routes = [Route("primary", primary, Breaker(threshold=2, clock=lambda: now[0])),
              Route("backup", backup)]
    for _ in range(3):
        assert (await answer("hi", routes))["route"] == "backup"
    assert calls == ["primary", "backup", "primary", "backup", "backup"]  # 3rd call skips primary
    now[0] = 31.0  # after the cooldown, the primary gets another chance
    await answer("hi", routes)
    assert calls[-2:] == ["primary", "backup"]
```

This version is deliberately small. Production libraries such as `pybreaker` add per-error-type rules, shared state across processes (in Redis again) and only one trial request while half-open. The ideas are the ones here.

### Graceful degradation

When every route fails, the worst response is a stack trace and the second worst is a spinner that never stops. **Graceful degradation** means planning, in advance, a sequence of smaller but still useful answers. For a docs assistant, the ladder might be:

1. The full answer from the capable model.
1. A shorter answer from the cheap model (your fallback route).
1. A cached answer to the same question, even if it's a little stale, clearly marked as such. The response cache from Caching and Model Choice can serve this role if you keep entries a little past their normal expiry for emergencies.
1. A non-LLM answer: the top search results from your hybrid search, with links, and no generated text at all.
1. An honest message with a time to try again, and a `503` with `Retry-After` for API clients.

Each step down must be designed and tested, not improvised during an outage. Write a test for each rung, and add a **kill switch** (Feature Flags and A/B Tests) that forces the app onto a lower rung, so that during an incident you can move all traffic deliberately rather than waiting for timeouts.

The other half of degradation is **load shedding**: when you're over capacity, refusing some work early so the rest succeeds. If your client-side limiter has a queue of requests that would wait 40 seconds, the users at the back will give up anyway; better to answer them immediately with "busy, try again" and keep the wait short for everyone else. Shed the least important work first: pause background jobs before you turn away live users, and turn away anonymous users before paying customers. A queue with a maximum length and a maximum wait is the simplest load shedder, and a load test, which the next lesson teaches, is how you check that it kicks in where you think it does.

### On other providers

The patterns in this lesson, pacing with a token bucket, spend budgets, fallback chains, circuit breakers and degradation ladders, are provider-neutral. The details differ. OpenAI reports limits in headers such as `x-ratelimit-remaining-requests` and `x-ratelimit-remaining-tokens`, and its [rate limits guide](https://platform.openai.com/docs/guides/rate-limits) explains how it counts tokens, including how `max_tokens` affects the count, so set your bucket from those rules. Its [Batch API](https://platform.openai.com/docs/guides/batch) takes an uploaded JSONL file of requests rather than a list in the call, and returns a results file within a 24-hour window at a discount; Gemini's [batch mode](https://ai.google.dev/gemini-api/docs/batch-mode) works in a similar way. The `openai` SDK raises its own error classes (`openai.RateLimitError`, `openai.APIConnectionError`), so add `openai.APIConnectionError` to `is_transient()`; its status errors have a `status_code` too, so the rest already works. Gateways such as LiteLLM can express a fallback chain across providers as configuration. A self-hosted open model has no rate limit except your hardware, which makes it a useful last route for simple tasks. Through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), it's one more route in the list:

```python
import openai

local = openai.AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


def local_route(model: str) -> Route:  # for example "llama3.2:3b"
    async def call(question: str) -> str:
        r = await local.chat.completions.create(
            model=model, messages=[{"role": "user", "content": question}])
        return r.choices[0].message.content or ""
    return Route(name=f"local:{model}", call=call)
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Claude API rate limits page](https://platform.claude.com/docs/en/api/rate-limits) again, this time for capacity planning.
   - Focus on the token bucket explanation, which tokens count toward ITPM and OTPM (especially cached tokens), and the full list of response headers.
1. Read the [Claude API errors page](https://platform.claude.com/docs/en/api/errors) and sort every error into three columns: retry, fall back to another route, or fix the request.
1. Work through the OpenAI cookbook's [How to handle rate limits](https://developers.openai.com/cookbook/examples/how_to_handle_rate_limits), a provider-neutral explanation with runnable examples.
   - You know backoff from Timeouts, Retries and Rate Limits, so focus on the sections about throttling parallel requests and batching, and compare them with `throttle.py`.
1. Read the [batch processing guide](https://platform.claude.com/docs/en/build-with-claude/batch-processing) to learn when a batch job is the right tool, how to submit one, and how results, errors and expiry work.
1. Read [Handling Overload](https://sre.google/sre-book/handling-overload/) from Google's free SRE book. It explains load shedding, request criticality and why retries can make overload worse, from a team that runs some of the world's largest services.
1. Practice: make one of your apps survive a bad day.
   - Add `fallback.py` to an app you've built, with at least two routes, and write the circuit-breaker test above plus one of your own: a `429` on the primary followed by a `400` on the next request, asserting the `400` is raised and doesn't trip the breaker.
   - Put a `TokenBudget` in front of your eval runner, run 100 cases with a deliberately low limit, and show from your traces that no `429`s occurred. Then run the same cases through `batch_eval.py` and compare the cost of the two runs.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why does a nightly eval affect your live users, and how can you see how close you are to a limit?](#throughput-is-a-shared-budget)
- [Why isn't a semaphore enough to stay under a tokens-per-minute limit, and how does a client-side token bucket help?](#pacing-yourself-on-the-client)
- [Why track spend per user in dollars rather than requests, and what can you do when a user hits the limit?](#spend-budgets-per-user-and-per-feature)
- [When is a batch API the right tool, and how should you handle results that errored or expired?](#batch-apis)
- [Which errors should trigger a fallback, and what must you do before a fallback route can be trusted?](#fallbacks-when-retries-run-out)
- [What problem does a circuit breaker solve, and what do the closed, open and half-open states mean?](#circuit-breakers)
- [What does a degradation ladder look like for a docs assistant, and what is load shedding?](#graceful-degradation)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Building A Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html) by Chip Huyen shows where gateways, fallbacks and caches sit in a larger system.
- [Locust](https://docs.locust.io/en/stable/) is a free Python load-testing tool you can use to send many requests at your deployed app and watch how its limiter, fallbacks and load shedding behave near their limits. Load Testing, the next lesson, uses it.
- Martin Fowler's [CircuitBreaker](https://martinfowler.com/bliki/CircuitBreaker.html) is the classic short explanation of the pattern, with a state diagram.
- [Using load shedding to avoid overload](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/) from the Amazon Builders' Library explains how to decide which work to drop, and how to test it.
- LiteLLM's [routing docs](https://docs.litellm.ai/docs/routing) show retries, fallbacks and cooldowns across providers configured in an open-source gateway.
- OpenAI's [Batch API guide](https://platform.openai.com/docs/guides/batch) shows the file-based batch workflow on another provider.
