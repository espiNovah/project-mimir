<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Model APIs are shared services. They limit how much you can send, they occasionally get overloaded, and sometimes they go down. A production app has to keep working, or fail politely, when that happens. This lesson covers how to push lots of work through an API cheaply with batching, how to respond to rate limits with retries and backoff, and how to degrade gracefully with fallback models when retries aren't enough.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How rate limits work: requests per minute and tokens per minute.
- Which API errors are worth retrying and which are not.
- Exponential backoff with jitter, and why it beats retrying immediately.
- Fallback models and graceful degradation.
- Batch APIs for large jobs that don't need an instant answer.
- Timeouts and concurrency limits in your own code.

### Key ideas

- **Rate limits cap requests and tokens over time.** Providers limit requests per minute and tokens per minute (often input and output separately), and the limits depend on your account tier. When you exceed one, the API returns HTTP `429 Too Many Requests`, often with a `retry-after` header that tells you how long to wait.
- **Retry the right errors.** `429` (rate limited), `529` or `503` (overloaded) and `500` (server error) are usually temporary, so retrying makes sense. `400` (bad request) and `401` (bad key) will fail the same way every time, so retrying only wastes time. Always set a timeout on each call.
- **Use exponential backoff with jitter.** Wait 1 second, then 2, then 4, and so on, plus a small random amount (jitter) so many clients don't retry at the same instant. Cap the number of attempts. If the server sends `retry-after`, respect it. The official SDKs, including `anthropic`, already retry some errors with backoff; know what `max_retries` does before adding your own loop on top.
- **Fallbacks keep you up when retries run out.** After the last retry, switch to a different model (or a different provider) instead of returning an error. Fallbacks need their own evals, since a backup model may behave differently, and they should be logged so you know how often they fire.
- **Degrade gracefully.** If nothing works, return a clear message, a cached answer or a simpler non-LLM response. A friendly "try again in a minute" is better than a stack trace.
- **Batch work that can wait.** Batch APIs accept thousands of requests at once and return results within hours at a large discount (on the Claude API, half the normal price). They are ideal for nightly evals, bulk classification or backfilling data, not for chat.
- **Limit your own concurrency.** Sending 500 requests at once just turns into 500 rate-limit errors. A semaphore or a worker queue (from Job Queues and Workers) keeps you under the limit.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Claude API rate limits page](https://platform.claude.com/docs/en/api/rate-limits) to see how limits are measured and which response headers report them.
   - Focus on the request and token limits and the `retry-after` and rate-limit headers.
1. Read the [Claude API errors page](https://platform.claude.com/docs/en/api/errors) and make a two-column list: errors you would retry, and errors you would not.
1. Work through the OpenAI cookbook's [How to handle rate limits](https://developers.openai.com/cookbook/examples/how_to_handle_rate_limits), a provider-neutral explanation of backoff with runnable examples.
   - Read the sections on retrying with exponential backoff and on batching requests. The ideas apply to any provider.
1. Read the [batch processing guide](https://platform.claude.com/docs/en/build-with-claude/batch-processing) to learn when a batch job is the right tool and how to submit and collect one.
1. Practice: write a `call_with_fallback()` function that retries with exponential backoff and jitter, then switches to a smaller fallback model.
   - Test it against a fake client that raises a `429` error on the first three calls, and check that it waits, retries, falls back and logs each step.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Building A Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html) by Chip Huyen shows where gateways, fallbacks and caches sit in a larger system.
- [Locust](https://docs.locust.io/en/stable/) is a free Python load-testing tool you can use to send many requests at your deployed app and watch how it behaves near its limits.
