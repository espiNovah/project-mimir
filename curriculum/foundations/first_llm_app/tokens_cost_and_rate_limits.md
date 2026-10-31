### Introduction

So far you've treated API calls as if they always succeed and cost nothing. Real applications can't. Every call has a price measured in tokens, and every provider limits how fast you can make calls. At some point, often at the worst possible moment, a request will fail because the service is overloaded, your network drops or you've hit a limit.

The difference between a weekend demo and software people can rely on is mostly in how it handles these things. In this lesson you'll learn to measure what each call costs, estimate costs before you spend them, and handle API errors with retries so that a temporary hiccup doesn't crash your app.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How API pricing works: input tokens, output tokens and price per million.
- How to calculate the cost of a call from its `usage`.
- How to count tokens before you send a request.
- What rate limits are and how they're measured.
- Which API errors are worth retrying and which aren't.
- How to retry with exponential backoff and jitter.

### How pricing works

Model APIs charge separately for:

- **Input tokens:** everything you send, including the system prompt, the whole conversation history and any documents.
- **Output tokens:** everything the model generates, including any thinking. Output is typically about five times more expensive per token than input.

Prices are quoted per million tokens (MTok) and vary hugely by model, often by 20 times or more between a provider's smallest and largest models. At the time of writing, Claude Haiku 5.5 costs $0.10 per million input tokens and $0.50 per million output tokens (for prompts up to 100,000 tokens), while Claude Sonnet 5.5 costs $2 and $10. Prices change, so always check the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) and never hard-code a price without noting where it came from.

Every response tells you exactly what you used, so calculating the cost of a call is simple arithmetic:

```python
# USD per million tokens. Source: platform.claude.com pricing page, checked 2026-10-28.
PRICES = {
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
}


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICES[model]
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


# After a call:
#   cost = cost_usd(response.model, response.usage.input_tokens, response.usage.output_tokens)
print(f"${cost_usd('claude-haiku-5-5', 1_200, 400):.6f}")   # $0.000320
```

That number looks tiny, and for one call it is. But multiply it by every turn of every conversation of every user, remember that a 30-turn conversation resends its entire history 30 times, and cost becomes one of the main constraints on what you build. Measuring it from the start is a professional habit.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Set a spend limit

In the Claude Console you can set a monthly spend limit for your organization. Do it now, at a level you're comfortable losing, such as $10. If a bug ever puts your code into an infinite loop of API calls, the limit stops the damage. Other providers offer similar controls.

</div>

### Counting tokens before you send

Sometimes you need to know the size of a request *before* sending it: to check that a long document fits in the context window, or to estimate what a batch of 10,000 requests will cost. As you learned in Tokens and Tokenization, each provider has its own tokenizer, so a tool like `tiktoken` only gives a rough idea for Claude. Anthropic provides a free token-counting endpoint that gives the exact count for a given model:

```python
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

with open("notes.txt", encoding="utf-8") as f:
    document = f.read()

count = client.messages.count_tokens(
    model="claude-haiku-5-5",
    system="Summarize the user's notes in five bullet points.",
    messages=[{"role": "user", "content": document}],
)
print(count.input_tokens)
```

It takes the same `model`, `system` and `messages` you would send to `messages.create()` and returns the number of input tokens the request would use. It can't tell you the output tokens, since nothing has been generated yet; for that, you estimate from `max_tokens` or from past responses.

### Rate limits

To share capacity fairly, every provider limits how much each account can use in a period of time. Anthropic measures limits in **requests per minute (RPM)**, **input tokens per minute (ITPM)** and **output tokens per minute (OTPM)**, separately for each model class. New accounts start with low limits that rise automatically as you spend more over time.

When you exceed a limit, the API rejects the request with a `429` status code and a `rate_limit_error`. The response usually includes a **`retry-after`** header saying how many seconds to wait. Response headers starting with `anthropic-ratelimit-` report your limits and how much you have left.

For your own learning projects, you'll rarely hit these limits. They show up when you start sending many requests at once, such as running an evaluation over hundreds of examples, which is exactly when the async semaphore from Async Basics comes in handy.

### Which errors to retry

From How the Web Works, you know the basic split: 4xx means *you* did something wrong, 5xx means *they* did. The SDK raises a different exception class for each kind of failure, so your code can react appropriately:

| Error | Status | What it means | Retry? |
| --- | --- | --- | --- |
| `anthropic.BadRequestError` | 400 | Something in your request is invalid | No, fix the request |
| `anthropic.AuthenticationError` | 401 | Missing or invalid API key | No, fix the key |
| `anthropic.NotFoundError` | 404 | For example, a misspelled model ID | No, fix the request |
| `anthropic.RateLimitError` | 429 | Too many requests or tokens per minute | Yes, after waiting |
| `anthropic.InternalServerError` | 500+ | A problem on the server side | Yes |
| `anthropic.OverloadedError` | 529 | The API is temporarily overloaded (an Anthropic-specific code) | Yes |
| `anthropic.APIConnectionError` | none | Network failure or timeout; no response at all | Yes |

All the errors with a status code are subclasses of `anthropic.APIStatusError`, which has a `.status_code` and the original `.response`. All of them, including connection errors, are subclasses of `anthropic.APIError`.

Here's a pleasant surprise: **the SDK already retries** (OpenAI's Python SDK has the same default) connection errors, 408, 409, 429 and 5xx errors twice by default, waiting a little longer each time. You can change that with `anthropic.Anthropic(max_retries=5)`, or turn it off with `max_retries=0`. For many apps, the defaults plus good error messages are enough.

### Retrying with exponential backoff

Still, it's worth understanding and writing retry logic yourself, because you'll need it for every other API you use, and because you sometimes want control the SDK doesn't give you (more patience for a batch job, a message to the user while waiting, a fallback to a different model).

The standard pattern is **exponential backoff with jitter**:

- **Exponential backoff:** wait 1 second, then 2, then 4, then 8. If the service is struggling, hammering it with instant retries makes things worse for everyone.
- **Jitter:** add a small random amount to each wait, so that a thousand clients that failed at the same moment don't all retry at the same moment too.
- **Respect `retry-after`** when the server sends it. It knows better than your guess.
- **Give up eventually** and report a clear error.

```python
import random
import time

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(max_retries=0)   # we handle retries ourselves in this example

RETRYABLE = (
    anthropic.RateLimitError,
    anthropic.InternalServerError,
    anthropic.OverloadedError,
    anthropic.APIConnectionError,
)


def create_with_retry(max_attempts: int = 5, **request):
    for attempt in range(1, max_attempts + 1):
        try:
            return client.messages.create(**request)
        except RETRYABLE as e:
            if attempt == max_attempts:
                raise
            wait = min(2 ** (attempt - 1), 30) + random.uniform(0, 1)
            if isinstance(e, anthropic.APIStatusError):
                retry_after = e.response.headers.get("retry-after")
                if retry_after is not None:
                    wait = float(retry_after)
            print(f"[{type(e).__name__}; retrying in {wait:.1f}s (attempt {attempt}/{max_attempts})]")
            time.sleep(wait)


try:
    response = create_with_retry(
        model="claude-haiku-5-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": "Say hello in French."}],
    )
    print("".join(b.text for b in response.content if b.type == "text"))
except anthropic.AuthenticationError:
    print("Your API key is missing or invalid. Check ANTHROPIC_API_KEY in your .env file.")
except anthropic.APIStatusError as e:
    print(f"The API returned an error ({e.status_code}): {e.message}")
except anthropic.APIConnectionError:
    print("Couldn't reach the API. Check your internet connection and try again.")
```

Notice the two layers. `create_with_retry` handles *temporary* problems by waiting and trying again. The `try`/`except` around it handles *permanent* problems, and anything that's still failing after all the retries, by telling the user something useful instead of showing a traceback. The order of the `except` clauses matters: Python uses the first one that matches, so specific classes like `AuthenticationError` must come before their parent class `APIStatusError`.

One caveat for streaming: a stream can fail after it has already printed part of the answer. If you retry, the user sees the start of the answer twice. A simple approach is to print a note like "[connection lost, retrying]" before starting again.

### On other providers

Almost everything here carries over: every provider bills input and output tokens separately per million, returns a `429` with a `retry-after` header when you go too fast, and deserves the same backoff-with-jitter retries. The names differ. In the OpenAI Chat Completions format, the usage fields are `usage.prompt_tokens` and `usage.completion_tokens`, so your `cost_usd` function stays the same and you just pass it different fields. OpenAI's rate-limit headers start with `x-ratelimit-` (for example `x-ratelimit-remaining-tokens`) rather than `anthropic-ratelimit-`, and its limits are counted in requests and tokens per minute (and for some limits per day), without Anthropic's split between input and output tokens; see OpenAI's [rate limits guide](https://developers.openai.com/api/docs/guides/rate-limits). The `openai` package raises errors with the same class names, such as `openai.RateLimitError`, `openai.AuthenticationError` and `openai.APIConnectionError`, so `create_with_retry` ports over almost line for line. The 529 overloaded code is Anthropic's alone; on OpenAI an overloaded server shows up as a 503 or another 5xx, which your retry list already covers. For counting tokens before you send, OpenAI has its own [token counting endpoint](https://developers.openai.com/api/docs/guides/token-counting) for its Responses API. A local model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) costs nothing per token and has no rate limits, but it still reports usage, and the token counts are a good habit to log because they tell you whether a hosted model would be affordable for the same job.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing).
   - Read "Model pricing" and find the input and output prices for the current Haiku, Sonnet and Opus models. Skim the sections on prompt caching and batch processing; you'll use both in the Production path.
1. Read the [token counting guide](https://platform.claude.com/docs/en/build-with-claude/token-counting), focusing on the basic usage example and the section on pricing and rate limits for the endpoint itself.
1. Read the [API errors reference](https://platform.claude.com/docs/en/api/errors) and the [rate limits page](https://platform.claude.com/docs/en/api/rate-limits).
   - On the errors page, read "HTTP errors" and "Error shapes" carefully.
   - On the rate limits page, read "About rate limits," "Spend limits" and "Rate limits," and look at the table of response headers. Then find your own organization's current limits in the Console.
1. Put it into practice.
   - Add cost tracking to your streaming conversation loop: after each reply, print that turn's cost and the running total for the session.
   - Use `count_tokens` to measure a long text file of your choice, then estimate what it would cost to send it with Haiku and with Sonnet.
   - Trigger errors on purpose and confirm your code prints a helpful message for each: an invalid API key (temporarily change one character in `.env`), a misspelled model name, and no internet connection.
   - Read the "Handling errors," "Retries" and "Timeouts" sections of the [Python SDK documentation](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) and compare the SDK's built-in behavior with the `create_with_retry` function above.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How do you calculate the cost of a call from its usage?](#how-pricing-works)
- [Why do output tokens usually matter more for cost than input tokens?](#how-pricing-works)
- [How can you count tokens before sending a request?](#counting-tokens-before-you-send)
- [What are rate limits, and what are they measured in?](#rate-limits)
- [Which API errors are worth retrying, and which aren't?](#which-errors-to-retry)
- [Why retry with exponential backoff and jitter instead of retrying immediately?](#retrying-with-exponential-backoff)
- [What changes in cost tracking and retries when you use an OpenAI-compatible API?](#on-other-providers)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- MDN's [Retry-After header reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After) explains the header's two possible formats.
- The [Claude status page](https://status.claude.com/) shows current incidents. Check it when you see a burst of 5xx or 529 errors.
