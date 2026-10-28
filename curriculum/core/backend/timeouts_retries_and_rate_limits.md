### Introduction

Your API now has users, a database and a job queue. It also has a dependency you don't control: the model provider. Some calls will take ten times longer than usual. Some will fail with a `529` because the provider is overloaded. And when you run an eval over 200 examples, some will come back `429` because you've hit your rate limit. On the other side, your own users can hurt you too: one script in a loop can spend your whole monthly budget in an afternoon.

In Tokens, Cost and Rate Limits you met the basics: which errors to retry, and a simple backoff loop. This lesson turns that into production habits for a web service. You'll put a deadline on every call, retry the right errors without stacking retry loops, respect what the server tells you, and give your own API a per-user rate limit that answers `429` with a `Retry-After` header. Then you'll test all of it with fakes, so you never have to wait for a real outage to know it works. The LLM-Powered API project requires every piece.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why every network call needs a timeout, and the difference between a read timeout and a total deadline.
- Which errors to retry, and which to fail on immediately.
- Exponential backoff with jitter, a cap, and a limit on attempts and total time.
- Respecting the `Retry-After` header, and failing fast when it asks for too long.
- The SDK's built-in retries compared with your own, using tenacity.
- Rate limiting your own API per user, in memory and with Redis.
- Testing timeouts, retries and limits with fakes.

### Why every call needs a timeout

A **timeout** is the longest you're willing to wait before giving up. Without one, a call that hangs (a dropped connection, a stuck server) waits forever, and so does whatever is waiting on it: the user's request, a worker slot, a database connection. A few hung calls can tie up every worker your API has, and then the whole service stops responding even though nothing has crashed. Engineers call this a **cascading failure**: one slow dependency takes down everything upstream of it.

Different libraries have different defaults, so never rely on them without checking:

- The `anthropic` SDK waits up to **10 minutes** by default. That suits a long generation, but it's far too long for a web request where the user gave up after 30 seconds.
- `httpx` times out after 5 seconds by default.
- `requests` has **no timeout at all** unless you pass one, such as `requests.get(url, timeout=(3, 10))`.

Timeouts come in parts. The **connect timeout** is how long to wait to open a connection. The **read timeout** is how long to wait for the *next chunk* of data, not for the whole response. That second point surprises people: a server that sends one byte every 50 seconds never trips a 60-second read timeout. So pair the per-read timeout with a **total deadline** for the whole operation. In Python 3.11 and later, `asyncio.timeout(90)` cancels everything inside it after 90 seconds, however many retries happened.

How long should a timeout be? Measure. Look at how long your model calls take (your traces from Why Evals Matter record latency), and set the timeout comfortably above the slowest normal calls, often 2 to 3 times the 99th percentile (the time that 99% of calls finish within). A short-answer extraction with the [cheap model](#/models) might normally take 2 to 5 seconds, so 30 to 60 seconds is generous. A long generation needs more, or streaming, which keeps data flowing so the read timeout never fires.

### Which errors to retry

A retry only helps if the next attempt might succeed. Sort failures into two groups:

| Retry | Why |
| --- | --- |
| Connection errors and timeouts | The request never got an answer. A fresh attempt may get through. |
| `408` Request Timeout, `409` Conflict | Temporary; the SDK retries these too. |
| `429` Too Many Requests | You're over a rate limit. Waiting fixes it. |
| `500`, `502`, `503`, `504`, `529` | The provider had a problem or is overloaded. Usually brief. |

| Don't retry | Why |
| --- | --- |
| `400` Bad Request, `413` Too Large, `422` | Your request is wrong. It fails the same way every time. |
| `401` Unauthorized, `403` Forbidden | Your key is missing, wrong or not allowed. |
| `404` Not Found | Usually a misspelled model ID. |

Retrying a `400` just burns time and, at scale, your rate limit. Worse, if the `400` is caused by user input that's too long, every retry also delays the useful error message the user needs.

A timeout deserves one more thought. When a call times out, the provider may have done all the work anyway and billed you for it. Retrying a timed-out generation can double its cost. That's another reason to cap attempts.

### Backoff, jitter and a cap

You know the shape from Foundations: wait about 1 second, then 2, then 4, and add **jitter** (a little randomness) so that a thousand clients that failed together don't all retry together. In a web service, three more limits matter:

1. **A cap on each wait.** Doubling forever gives you a 64-second sleep by the seventh attempt. Cap it, for example at 20 seconds.
1. **A cap on attempts.** Three or four attempts is typical. If the provider is still failing after that, it's having an outage, and hammering it doesn't help anyone.
1. **A cap on total time.** A user waiting on `POST /extractions` won't wait two minutes. Stop retrying once a time budget is spent, and return a clear error. For background jobs you can be more patient, because nobody is staring at a spinner.

There's a fourth rule: **if the server tells you how long to wait, do that.** A `429` from Anthropic, and many other APIs, includes a `Retry-After` header. It's usually a number of seconds, but the HTTP standard also allows a date, such as `Wed, 28 Oct 2026 09:30:00 GMT`. The server knows when your limit resets; your exponential guess doesn't. And if it asks you to wait longer than you're willing to, don't sleep through it. Fail fast, and tell your own client to come back later.

### The SDK's retries or yours

The `anthropic` SDK already retries connection errors, `408`, `409`, `429` and `5xx` responses, twice by default, with short exponential backoff that respects `Retry-After`. For a script or a notebook, the defaults are fine. You can tune them on the client, or for one call with `with_options`:

```python
client = anthropic.Anthropic(max_retries=4, timeout=30.0)
response = client.with_options(timeout=10.0).messages.create(...)
```

Write your own retry loop when you need something the SDK can't give you: recording the attempt number in your traces (the project requires it), a total time budget, logging each failure, or falling back to another model. When you do, **turn the SDK's retries off** with `max_retries=0`. Otherwise the two loops multiply: four attempts of yours, each making three SDK attempts, is twelve calls, and the timeouts multiply too. Pick one place where retries happen.

You could write the loop by hand, as you did in Foundations. In real projects, most Python teams use **tenacity**, a small library that does retries well and handles async code. Install it with `uv add anthropic tenacity`. Here is a call that combines everything so far:

```python
# resilient.py: one model call with a timeout, limited retries, backoff with jitter, and a cap
import asyncio
import email.utils
import logging
import os
import time

import anthropic
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential_jitter,
)

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
log = logging.getLogger(__name__)

RETRY_STATUSES = {408, 409, 429, 500, 502, 503, 504, 529}
MAX_WAIT = 20.0                     # never sleep longer than this between attempts
backoff = wait_exponential_jitter(initial=1, max=MAX_WAIT, jitter=1)   # ~1, 2, 4, 8 s, plus 0-1 s


def make_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(
        timeout=anthropic.Timeout(60.0, connect=5.0),  # 5 s to connect, 60 s for each read
        max_retries=0,                                  # we retry below; don't stack two retry loops
    )


def retry_after_seconds(exc: BaseException) -> float | None:
    """Read Retry-After, which is either a number of seconds or an HTTP date."""
    if not isinstance(exc, anthropic.APIStatusError):
        return None
    value = exc.response.headers.get("retry-after")
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        when = email.utils.parsedate_to_datetime(value)
        return max(0.0, when.timestamp() - time.time())


def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, anthropic.APIConnectionError):    # no response at all, including timeouts
        return True
    if isinstance(exc, anthropic.APIStatusError) and exc.status_code in RETRY_STATUSES:
        wait = retry_after_seconds(exc)
        return wait is None or wait <= MAX_WAIT          # asked to wait too long? fail fast instead
    return False                                          # 400, 401, 403, 404, 413...: fix the request


def wait_time(state) -> float:
    wait = retry_after_seconds(state.outcome.exception())
    return wait if wait is not None else backoff(state)  # the server's number beats our guess


async def call_model(client, *, sleep=asyncio.sleep, **request) -> tuple[anthropic.types.Message, int]:
    """Return the response and the attempt number that produced it (for your traces)."""
    async for attempt in AsyncRetrying(
        retry=retry_if_exception(is_retryable),
        wait=wait_time,
        stop=stop_after_attempt(4) | stop_after_delay(45),   # at most 4 tries, and stop after 45 s
        sleep=sleep,                                         # tests pass a fake that doesn't wait
        before_sleep=lambda s: log.warning("attempt %d failed: %r", s.attempt_number, s.outcome.exception()),
        reraise=True,                                        # raise the real error, not RetryError
    ):
        with attempt:
            response = await client.messages.create(model=MODEL, **request)
    return response, attempt.retry_state.attempt_number


async def main() -> None:
    client = make_client()
    async with asyncio.timeout(90):                          # a hard ceiling on the whole thing
        response, attempts = await call_model(
            client,
            max_tokens=1000,
            messages=[{"role": "user", "content": "Say hello in French."}],
        )
    print(f"(took {attempts} attempt(s))")
    print("".join(b.text for b in response.content if b.type == "text"))


if __name__ == "__main__":
    asyncio.run(main())
```

A few details worth noticing:

- **`APITimeoutError` is a subclass of `APIConnectionError`**, so one `isinstance` check covers both "couldn't connect" and "took too long."
- **The client is passed in.** Your FastAPI app creates one client at startup and hands it to `call_model`; tests hand it a fake. This is the dependency injection you learned in Testing with pytest.
- **`sleep` is passed in too.** Tenacity calls it between attempts, so a test can record the waits instead of actually waiting.
- **It's async**, because your routes and your `process_job` function from Deploying Your API are `async def`. Inside async code, never use the blocking `anthropic.Anthropic()` client or `time.sleep()`. If you use RQ with plain functions instead, tenacity's `Retrying` class works the same way without `async`.

When retries run out, the error still reaches your route. Catch it there and turn it into a deliberate response, as you learned in FastAPI Basics: a `503 Service Unavailable` (with a `Retry-After` of your own if the provider sent one) for rate limits and overloads, or a `504 Gateway Timeout` for a timeout. In a job, store the error message and mark the job `failed`. Never let a stack trace reach the client.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Two different kinds of retry

In Getting Structured Output you retried when the model's answer failed validation. That's a retry about *content*: the call worked, but the answer was wrong. This lesson's retries are about *transport*: the call itself failed. Keep them separate, cap each one, and log both. In the worst case they multiply (4 transport attempts for each of 3 validation attempts), so check that your worst case still fits your time budget.

</div>

### Rate limiting your own API

The provider rate-limits you. Now you need to rate-limit your users. Without a limit, one user (or one bug in a user's script) can make thousands of requests, each costing you money and each competing for your own provider rate limit with everyone else. A **per-user rate limit** caps how many requests each user can make in a period of time and answers anything over it with `429 Too Many Requests` and a `Retry-After` header, exactly the contract you just learned to respect as a client.

Two algorithms cover most needs:

- **Fixed window.** Count each user's requests per clock minute (or hour). When the count passes the limit, reject until the next window starts. It's simple, and you can build it with a single Redis counter. Its weakness is the edge: a user can send the full limit at 11:59:59 and again at 12:00:00, doubling the burst.
- **Token bucket.** Each user has a bucket that holds up to, say, 5 tokens and refills at a steady rate, such as 5 per minute. Each request spends a token, and an empty bucket means `429`. It allows short bursts but enforces the average rate smoothly, and it tells you exactly how long until the next token.

Here's an in-memory token bucket wired into FastAPI as a dependency. Install `uv add "fastapi[standard]"` if you haven't already:

```python
# ratelimit.py: a per-user token bucket, and a FastAPI dependency that enforces it
import math
import time
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


class TokenBucket:
    """Each key gets `capacity` tokens; one request spends one; tokens refill steadily."""

    def __init__(self, capacity: int, per_second: float, clock=time.monotonic):
        self.capacity, self.rate, self.clock = capacity, per_second, clock
        self.buckets: dict[str, tuple[float, float]] = {}   # key -> (tokens left, last update)

    def take(self, key: str) -> float:
        """Spend a token. Return 0.0 if allowed, or the seconds until one is available."""
        now = self.clock()
        tokens, last = self.buckets.get(key, (self.capacity, now))
        tokens = min(self.capacity, tokens + (now - last) * self.rate)   # refill since last time
        if tokens >= 1:
            self.buckets[key] = (tokens - 1, now)
            return 0.0
        self.buckets[key] = (tokens, now)
        return (1 - tokens) / self.rate


limiter = TokenBucket(capacity=5, per_second=5 / 60)     # bursts of 5, then 5 a minute


def get_current_user(x_user: Annotated[str, Header()]) -> str:
    return x_user    # stand-in: use the real dependency from User Accounts and Auth


def rate_limit(user: Annotated[str, Depends(get_current_user)]) -> None:
    wait = limiter.take(user)
    if wait:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Slow down.",
            headers={"Retry-After": str(math.ceil(wait))},   # whole seconds, rounded up
        )


app = FastAPI()


@app.post("/extractions", status_code=201, dependencies=[Depends(rate_limit)])
def create_extraction() -> dict:
    return {"status": "ok"}    # the real route calls your extractor here
```

The limit is keyed by **user ID**, not IP address, because your users are logged in, and many people can share one IP address (an office, a phone network). Put the limit on the expensive routes, the ones that call a model or enqueue a job, rather than on `GET /health`. The clock is injectable for the same reason the client was: tests can move time forward instantly. `time.monotonic()` is used instead of `time.time()` because it never jumps backward when the system clock changes.

**Where the counts live matters.** The bucket above lives in one Python process's memory. That works for a single process, such as one instance on Render's free plan, but the counts reset whenever the process restarts, and if you run two API processes, each has its own buckets and a user gets double the limit. To share counts between processes, store them in Redis, which you already run for the job queue in Job Queues and Workers. Here's a fixed window in Redis, using the async client from the `redis` package:

```python
# redis_limit.py: a fixed-window limit shared by every API process
import time

import redis.asyncio as redis   # the async client in the redis package, which arq installed in Job Queues and Workers


async def fixed_window(r: redis.Redis, key: str, limit: int, window: int) -> int:
    """Count one request for `key`. Return 0 if allowed, or seconds until the window resets."""
    now = int(time.time())
    window_key = f"ratelimit:{key}:{now // window}"     # e.g. ratelimit:42:29123456
    async with r.pipeline(transaction=True) as pipe:   # both commands run together
        count, _ = await pipe.incr(window_key).expire(window_key, window).execute()
    if count > limit:
        return window - now % window
    return 0
```

`INCR` adds one to a counter and returns the new value, atomically, so two processes can never both read 4 and both write 5. `EXPIRE` makes Redis delete the key once its window is over, so old counters never pile up. Your `rate_limit` dependency calls this instead of `limiter.take()` and raises the same `429`. On Render's free plan, where you set `INLINE_JOBS=true` and don't deploy Redis, the in-memory version is the honest choice; say so in your README.

Choosing numbers is a product decision. Start from cost: if one extraction costs a fifth of a cent and you're willing to spend $1 per user per day, that's 500 requests a day. Then add a short-term limit, such as 10 a minute, to stop runaway loops. Libraries like slowapi can do this for you, but writing it once shows you there's no magic.

### Testing with fakes

You can't wait for a real outage to test your retry code, and you shouldn't spend money on it either. Instead, build fake errors and a fake client. The SDK's error classes can be created directly from an HTTP response, so your fake raises exactly what the real SDK would. Install the test tools with `uv add --dev pytest pytest-asyncio`, and add `asyncio_mode = "auto"` under `[tool.pytest.ini_options]` in `pyproject.toml` so pytest runs `async def` tests:

```python
# test_resilient.py
import anthropic
import httpx2
import pytest

from resilient import call_model

URL = "https://api.anthropic.com/v1/messages"


def api_error(cls, status: int, headers: dict | None = None):
    """Build the same exception the SDK raises for a real HTTP error."""
    response = httpx2.Response(status, headers=headers or {}, request=httpx2.Request("POST", URL))
    return cls(f"fake {status}", response=response, body=None)


class FakeMessages:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)     # exceptions to raise, or a response to return
        self.calls = 0

    async def create(self, **request):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeClient:
    def __init__(self, outcomes):
        self.messages = FakeMessages(outcomes)


class FakeSleep:
    def __init__(self):
        self.waits = []

    async def __call__(self, seconds):
        self.waits.append(seconds)         # record the wait instead of waiting


async def test_retries_a_429_then_succeeds():
    client, sleep = FakeClient([api_error(anthropic.RateLimitError, 429, {"retry-after": "3"}), "ok"]), FakeSleep()
    response, attempts = await call_model(client, sleep=sleep, max_tokens=10, messages=[])
    assert response == "ok" and attempts == 2
    assert sleep.waits == [3.0]            # it waited exactly as long as Retry-After asked


async def test_backs_off_exponentially_on_5xx():
    error = api_error(anthropic.InternalServerError, 500)
    client, sleep = FakeClient([error, error, error, "ok"]), FakeSleep()
    await call_model(client, sleep=sleep, max_tokens=10, messages=[])
    assert [int(w) for w in sleep.waits] == [1, 2, 4]   # jitter adds less than a second


async def test_does_not_retry_a_400():
    client = FakeClient([api_error(anthropic.BadRequestError, 400)])
    with pytest.raises(anthropic.BadRequestError):
        await call_model(client, sleep=FakeSleep(), max_tokens=10, messages=[])
    assert client.messages.calls == 1


async def test_gives_up_after_four_attempts():
    timeout = anthropic.APITimeoutError(request=httpx2.Request("POST", URL))
    client = FakeClient([timeout] * 4)
    with pytest.raises(anthropic.APITimeoutError):
        await call_model(client, sleep=FakeSleep(), max_tokens=10, messages=[])
    assert client.messages.calls == 4
```

The `anthropic` SDK is built on `httpx2`, a maintained fork of `httpx` that installs along with it, so the fake responses use `httpx2` too. (FastAPI's `TestClient` still uses plain `httpx`; the two live happily side by side.)

The rate limiter gets the same treatment: a fake clock you move by hand, and `TestClient` to check the real HTTP response.

```python
# test_ratelimit.py
from fastapi.testclient import TestClient

import ratelimit
from ratelimit import TokenBucket


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_bucket_refills_over_time():
    clock = FakeClock()
    bucket = TokenBucket(capacity=2, per_second=0.5, clock=clock)
    assert bucket.take("ana") == 0 and bucket.take("ana") == 0
    assert bucket.take("ana") == 2.0          # empty: one token takes 2 s at 0.5/s
    clock.now += 2
    assert bucket.take("ana") == 0


def test_api_returns_429_with_retry_after(monkeypatch):
    monkeypatch.setattr(ratelimit, "limiter", TokenBucket(capacity=2, per_second=1 / 30, clock=FakeClock()))
    client = TestClient(ratelimit.app)
    for _ in range(2):
        assert client.post("/extractions", headers={"X-User": "ana"}).status_code == 201
    blocked = client.post("/extractions", headers={"X-User": "ana"})
    assert blocked.status_code == 429
    assert blocked.headers["Retry-After"] == "30"
    assert client.post("/extractions", headers={"X-User": "ben"}).status_code == 201   # others unaffected
```

For the Redis version, `fakeredis` (`uv add --dev fakeredis`) gives you an in-memory stand-in: `r = fakeredis.FakeAsyncRedis()` and pass it to `fixed_window`, so the test needs no running Redis. These are the "retry that succeeds after a fake `429`" and "`429` from your rate limiter" tests the LLM-Powered API project asks for.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) from the Amazon Builders' Library. It's the clearest explanation of how engineers at a very large company choose timeouts and why retries can make outages worse.
   - Read it all; it's about 15 minutes. Note how they pick a timeout from latency percentiles and why they limit retries to one layer.
1. Read the Claude docs on [rate limits](https://platform.claude.com/docs/en/api/rate-limits) and [errors](https://platform.claude.com/docs/en/api/errors) again, now as the owner of a service.
   - On the rate limits page, find the response headers and what `retry-after` means. On the errors page, note which errors the docs call retryable.
   - Then read the "Retries" and "Timeouts" sections of the [Python SDK documentation](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) to see exactly what the SDK does for you.
1. Read the [tenacity documentation](https://tenacity.readthedocs.io/en/latest/) from the start through "Error Handling," plus the "Retrying code block" and "Async and retry" sections (the lesson's `async for attempt in AsyncRetrying(...)` pattern comes from those two). It shows the other building blocks (`retry_if_exception_type`, `wait_random_exponential`, callbacks) you can combine.
1. Read Stripe's [Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters). It explains, from a company that runs a very large public API, why they use several kinds of limit and how they chose them.
1. Practice: add resilience to your API from the earlier Backend lessons.
   - Put `call_model` (or your own version) around every model call, with `max_retries=0` on the client and a total time budget. Record the attempt number in your trace.
   - Write the four retry tests above, then add one of your own: a `529` followed by a `500` followed by success, asserting two waits.
   - Add the token-bucket dependency to your model-calling routes. Write a test that a burst gets `429` with `Retry-After`, and that a different user isn't affected.
   - Bonus: switch the limiter to the Redis fixed window, test it with `fakeredis`, and run your Compose stack to check it against the real Redis.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why can a missing timeout take down a whole service, and why isn't a read timeout a total deadline?](#why-every-call-needs-a-timeout)
- [Which errors should you retry, and why is retrying a 400 a mistake?](#which-errors-to-retry)
- [What three caps should a retry loop in a web service have?](#backoff-jitter-and-a-cap)
- [What should you do when Retry-After asks for longer than you're willing to wait?](#backoff-jitter-and-a-cap)
- [Why set max_retries=0 on the SDK client when you write your own retry loop?](#the-sdk-s-retries-or-yours)
- [How does a token bucket differ from a fixed window, and when do you need Redis instead of memory?](#rate-limiting-your-own-api)
- [How can you test a retry after a 429 without waiting or calling the real API?](#testing-with-fakes)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The AWS blog post [Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) simulates several jitter strategies and shows why "full jitter" spreads retries out best.
- [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) from Google's free SRE book covers retry budgets, deadlines passed between services, and how overload spreads.
- HTTPX's [timeouts guide](https://www.python-httpx.org/advanced/timeouts/) explains connect, read, write and pool timeouts for the HTTP calls you make to other APIs.
- MDN's [429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429) and [Retry-After](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After) pages are the reference for the response your limiter sends.
- Redis's [rate limiting tutorial](https://redis.io/learn/howtos/ratelimiting) shows other Redis rate-limiting patterns, including the sliding window.
