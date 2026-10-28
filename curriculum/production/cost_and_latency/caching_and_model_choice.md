<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

An agent that costs a few cents per run feels free while you are testing it. At a thousand users a day, it is a real bill, and a ten-second wait is a real reason for people to leave. The good news is that most LLM apps waste a lot: they resend the same long instructions on every call and use the biggest model for steps a small model handles fine. This lesson covers the two biggest levers, prompt caching and choosing the right model for each step, plus how to measure what a task actually costs so you know whether a change helped.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to measure cost per task with token accounting.
- How to measure latency, including p50, p95 and time to first token.
- How prompt caching works and how to structure prompts to benefit from it.
- How to pick a model by capability, speed and price.
- Routing: sending each step to the smallest model that does it well.
- Why every optimization must be checked against your evals.

### Key ideas

- **Measure cost per task, not per call.** An agent run makes many calls. Add up input and output tokens across all of them (the API returns a `usage` object on every response), multiply by your model's published prices, and record the total per task. Output tokens usually cost several times more than input tokens, so long answers and long reasoning add up fast. Your traces from the Observability section already hold these numbers.
- **Report latency as percentiles.** The average hides the slow requests users complain about. p50 is the median; p95 is the time 95% of requests finish under. For chat, time to first token matters as much as total time, which is why streaming helps perceived speed.
- **Prompt caching reuses work on a repeated prefix.** If many requests start with the same long system prompt, tool definitions or document, the provider can cache that prefix. Cached input tokens are billed at a fraction of the normal price and processed faster. Caching matches from the start of the prompt, so put stable content first and anything that changes (the user's question, timestamps) last. On the Claude API you mark the cache point with `cache_control`; some other providers cache automatically. Check `usage` for cache read and cache write tokens to confirm it is working.
- **Caches expire.** Cached prefixes live for minutes, not days, so caching pays off for busy apps and multi-turn conversations, not one request an hour.
- **Choose models deliberately.** Bigger models are smarter, slower and pricier. Start with a capable model to see what's possible, then try smaller ones on each step and keep the cheapest one that passes your evals.
- **Route steps, not whole apps.** Classification, extraction and simple tool selection often work well on a small, fast model, while planning or the final answer may need a larger one. This is the routing pattern from Workflow Patterns, applied to cost.
- **No eval, no optimization.** A cheaper setup that quietly gets worse is not a win. Re-run your eval set after every change.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [prompt caching guide](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) in the Claude docs.
   - Focus on how cache prefixes are built, cache lifetime, pricing and how to read cache usage in the response. Other providers' caching works on the same idea.
1. Read [Choosing the right model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) for a practical way to trade off capability, speed and cost.
   - Then open the [models overview](https://platform.claude.com/docs/en/models/overview) and the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing), and note the price per million input and output tokens for a small and a large model.
1. Read the [token counting guide](https://platform.claude.com/docs/en/build-with-claude/token-counting) to learn how to estimate the cost of a prompt before you send it.
1. Read the model routing and caching sections of Chip Huyen's [Building A Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html), which shows where these pieces sit in a real system.
1. Practice: take one agent you've built and compute its cost per task.
   - Run 10 tasks, sum tokens from each response's `usage`, and compute the average cost and p50 latency.
   - Move your system prompt and tool definitions to the front, add a cache point, run again and compare cache read tokens and cost.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming) is the reference for streaming responses, which cuts time to first token even when total time stays the same.
