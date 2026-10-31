### Introduction

An agent that costs a few cents per run feels free while you are testing it. At a thousand users a day, it is a real bill, and a ten-second wait is a real reason for people to leave. In Agent Cost and Latency you learned to measure one run, turn on prompt caching inside an agent loop, and pick a model for each step. This lesson takes those ideas to live traffic, where the questions change. You're no longer asking "how much did this run cost?" but "which part of the product costs the most, and what can I change without anyone noticing a drop in quality?"

Two levers do most of the work. The first is **caching**: reusing work you've already paid for, either part of a prompt (prompt caching, a provider feature) or a whole answer (response caching, which you build yourself). The second is **model choice**: sending each step to the cheapest model that still passes its evals, and routing between models when one size doesn't fit all requests. Both can quietly make your app worse, so this lesson pairs every saving with the measurement that proves it's safe.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to find which routes and steps drive cost and latency across live traffic.
- How to lay out prompts so many users share one cached prefix.
- Cache lifetimes, break-even math and hit rate as a production metric.
- Response caching, and why semantic caching is riskier than it looks.
- Choosing a model per step with an eval and a cost/quality table.
- Model routing and cascades, and what they cost you.
- Why every optimization must be checked against your evals.

### Where the money goes in production

Agent Cost and Latency gave you a report for one run. In production you have thousands of runs a day across several routes, and the first job is to find out which ones matter. Your traces from the Observability section already hold everything you need: each model span records the model, token counts (including cache reads and writes) and latency, and each request span records the route, such as `POST /ask` or `POST /summarize`.

Group the spans by route, and within a route by step, then compute three things for each group over the last day or week:

- **Total spend**, the sum of the cost of every call. This is where you look first. A route that costs a tenth of a cent per request but runs 200,000 times a day matters more than a monthly report that costs a dollar.
- **Cost per request at p50 and p95.** Cost has a tail, just like latency. A long conversation, a user who pastes a whole PDF or an agent that loops to its step limit can cost fifty times the median. The tail is often where the money goes.
- **Latency at p50 and p95**, including time to first token for streamed routes (Streaming Responses). Load Testing, later in this section, shows how to measure these under real load.

Then sort by total spend. In most apps, one or two steps account for most of the bill, and those are the only ones worth optimizing. Everything below is aimed at those steps. A useful habit is to write the target before you start: "cut the summarize route's cost per request by 40% with no drop in its eval score." A vague goal like "make it cheaper" never finishes.

### Prompt caching across users

Inside an agent loop, caching is easy: each step's request is the previous one plus a little more. Across users it takes design. **Prompt caching** (a provider feature; on the Claude API you mark cache points with `cache_control`) stores the processed start of a prompt so a later request that begins with exactly the same bytes reads it cheaply. If every user's request starts differently, nobody ever reads anyone else's cache.

So lay the prompt out in layers, from the content shared most widely to the content that changes most often:

1. **Global layer:** your instructions and tool definitions. The same for every request on the route.
1. **Tenant layer:** content shared by a group of users, such as one customer company's help docs or product catalog.
1. **Conversation layer:** this user's earlier turns.
1. **The new message:** the only part that is truly unique.

On the Claude API you can place up to four explicit breakpoints, one at the end of each layer you want to share. Two users from the same company then share the first two layers; users from different companies still share the first. The most common mistake is personalizing the top: "You are helping Ana, a Pro plan customer, on 30 October" in the system prompt makes every user's prefix unique. Move those details down into the user message, where they cost nothing to change.

```python
# cached_support.py  (run with: uv run cached_support.py)
# Needs two long text files: instructions.md (your system prompt) and docs/acme.md
# (one customer's help docs). Each should be well over the model's minimum
# cacheable length; a few pages of any text is enough to try it.
import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()
INSTRUCTIONS = Path("instructions.md").read_text(encoding="utf-8")


def build_request(tenant_docs: str, history: list[dict], question: str, user_note: str) -> dict:
    return {
        "model": MODEL,
        "max_tokens": 2000,
        "system": [
            {"type": "text", "text": INSTRUCTIONS,  # (1) global layer: every user, every tenant
             "cache_control": {"type": "ephemeral", "ttl": "1h"}},
            {"type": "text", "text": tenant_docs,   # (2) tenant layer: one company's users
             "cache_control": {"type": "ephemeral"}},
        ],
        # (3) everything personal goes after the last breakpoint
        "messages": [*history, {"role": "user", "content": f"{user_note}\n\n{question}"}],
    }


def cache_stats(usage) -> dict:
    read = usage.cache_read_input_tokens or 0
    write = usage.cache_creation_input_tokens or 0
    total = usage.input_tokens + read + write  # input_tokens is only the uncached part
    return {"fresh": usage.input_tokens, "write": write, "read": read,
            "hit_rate": round(read / total, 2) if total else 0.0}


def test_prefix_is_identical_for_two_users():
    # (4) a free check for CI: no timestamp or user detail has crept into the prefix
    docs = "Refunds take 5 days."
    a = build_request(docs, [], "Where is my order?", "User: Ana (Pro plan)")
    b = build_request(docs, [], "How do refunds work?", "User: Ben (Free plan)")
    assert json.dumps(a["system"], sort_keys=True) == json.dumps(b["system"], sort_keys=True)


if __name__ == "__main__":
    docs = Path("docs/acme.md").read_text(encoding="utf-8")
    for note, question in [("User: Ana (Pro plan)", "How do I get a refund?"),
                           ("User: Ben (Free plan)", "Do you ship to Canada?")]:
        response = client.messages.create(**build_request(docs, [], question, note))
        print(question, cache_stats(response.usage))
```

Run it and the first request should show a large `write` and no `read`; the second, from a different user with a different question, should read both layers. The numbered comments:

1. **A one-hour lifetime on the global layer.** Every request on the route shares it, so it's worth keeping warm even through quiet periods. The next section explains when the longer lifetime pays.
1. **The default five-minute lifetime on the tenant layer.** On the Claude API, longer-lived breakpoints must come before shorter ones, which this layout respects.
1. **No breakpoint on the question.** A breakpoint after unique content writes a cache entry nobody will ever read, and writes cost extra. For a multi-turn chat, add the top-level `cache_control={"type": "ephemeral"}` argument from Agent Cost and Latency, which moves a breakpoint along the growing conversation.
1. **A test that costs nothing.** It checks that two different users produce byte-identical prefixes. Silent invalidators, such as a timestamp, a user's name or a dictionary serialized in random order, get caught in CI instead of on your bill.

Two production details matter. On the Claude API, caches are isolated per workspace, so traffic split across two workspaces builds two separate caches. And cached reads don't count toward the input-tokens-per-minute rate limit on most Claude models, so caching raises your throughput as well as cutting cost. Batching, Rate Limits and Fallbacks, the next lesson, comes back to this.

### Cache economics and lifetimes

Caching isn't free. A cache **write** costs more than normal input, and only **reads** save money. On the Claude API at the time of writing, a write with the default 5-minute lifetime costs 1.25 times the normal input price, a write with the 1-hour lifetime costs 2 times, and a read costs about a tenth of the normal price (less on some models; check the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing)). Each read also resets the entry's timer.

Work out the **break-even**, the number of uses at which caching starts saving. With the 5-minute lifetime, two requests cost 1.25 + 0.1 = 1.35 times the base price, against 2 times without caching. So a prefix used twice within five minutes already saves money. With the 1-hour lifetime, two requests cost 2 + 0.1 = 2.1 against 2, a small loss, and three cost 2.2 against 3, a win. The rule that falls out: pick the lifetime by the gap between requests that share a prefix.

- **Requests less than 5 minutes apart** (any busy route): use the 5-minute lifetime. Every read refreshes it, so it stays warm all day at the cheaper write price.
- **Gaps of 5 to 60 minutes** (a small tenant whose users ask a few questions an hour, or a chat where people reply slowly): the 1-hour lifetime is the only one that survives the gap.
- **Gaps over an hour:** neither helps. Accept the miss, or for a very valuable prefix, send a tiny request on a schedule to keep it warm.

Your traces tell you the gaps. For each tenant, look at the time between consecutive requests and you know which lifetime to use.

In production, track the **cache hit rate**: cache-read tokens divided by all input tokens (fresh, written and read), per route, over time. Put it on your dashboard next to cost per request, and alert on a sudden drop, as you learned in Alerting and Incidents. A cache that breaks doesn't raise an error. Requests keep succeeding, and the bill quietly goes up. The usual cause is a deploy that changed how the prompt is assembled, so a hit-rate panel that falls off a cliff right after a release tells you exactly where to look. One more trap: requests that start at the same instant can't read each other's cache, because an entry is only readable once the request that writes it has started returning. A burst of fifty identical requests after a cold start all pay full price. For batch-like bursts, send one request first and the rest after it has begun answering.

### Response caching

Prompt caching makes a model call cheaper. A **response cache** skips the call entirely: you store the finished answer and return it the next time the same request arrives. A hit costs nothing and returns in milliseconds. It's built into no provider; you build it with the Redis you already run from Job Queues and Workers.

It works when the same question genuinely repeats and the answer genuinely shouldn't change: a public FAQ bot, extracting fields from a document that gets submitted twice, a product description generated once per product. It's wrong for anything personal, anything that depends on live data, and anything users expect to vary, such as "give me another idea."

The design lives in the **cache key**, the string that decides whether two requests count as the same:

```python
# response_cache.py: an exact-match cache for whole answers, stored in Redis.
# setup: uv add redis   (and uv add --dev fakeredis for tests)
import hashlib
import json
from collections.abc import Callable

import redis

PROMPT_VERSION = "support-v3"  # bump it when the prompt changes, and old entries stop matching


def cache_key(*, scope: str, model: str, question: str, params: dict) -> str:
    normalized = " ".join(question.lower().split())  # (1) only trivial normalization
    payload = json.dumps({"v": PROMPT_VERSION, "scope": scope, "model": model,
                          "q": normalized, "p": params}, sort_keys=True)
    return "answer:" + hashlib.sha256(payload.encode()).hexdigest()


def cached_answer(r: redis.Redis, generate: Callable[[str], dict], *, scope: str, model: str,
                  question: str, params: dict, ttl_s: int = 3600) -> dict:
    key = cache_key(scope=scope, model=model, question=question, params=params)
    if (hit := r.get(key)) is not None:
        return json.loads(hit) | {"cache": "hit"}
    answer = generate(question)  # your real model call; returns {"text": ..., "stop_reason": ...}
    if answer["stop_reason"] == "end_turn":  # (2) never cache a cut-off answer or a refusal
        r.set(key, json.dumps(answer), ex=ttl_s)  # (3) every entry expires
    return answer | {"cache": "miss"}


def test_second_identical_question_is_a_hit():
    import fakeredis
    r, calls = fakeredis.FakeRedis(), []

    def gen(question: str) -> dict:  # a fake model call that records each question
        calls.append(question)
        return {"text": "5 days", "stop_reason": "end_turn"}

    args = {"scope": "tenant:acme", "model": "m", "params": {"max_tokens": 500}}
    assert cached_answer(r, gen, question="How long do refunds take?", **args)["cache"] == "miss"
    assert cached_answer(r, gen, question="how long do  refunds take?", **args)["cache"] == "hit"
    assert cached_answer(r, gen, question="How long do refunds take?",
                         **(args | {"scope": "tenant:globex"}))["cache"] == "miss"
    assert len(calls) == 2
```

Every field in the key is there to prevent a specific bug. The **scope** keeps one tenant's (or one user's) answer from being served to another; for anything personal, the scope must be the user ID, and if you can't define a safe scope, don't cache. The **prompt version** and **model** mean a new prompt never serves answers written by the old one. The **params** cover settings like `max_tokens` that change the answer. The comments add three more rules: (1) normalize only in ways that can't change meaning, such as case and whitespace; (2) cache only complete answers, never a truncated one, an error or a refusal; and (3) give every entry an expiry, because the facts behind an answer go stale. Log `cache: hit` or `miss` on the request's trace, so your cost report can show how much the cache saved.

### Semantic caching and its risks

A **semantic cache** goes one step further. Instead of requiring the same text, it embeds each question (Embeddings, in the RAG section), finds the most similar cached question, and returns its answer if the similarity is above a threshold. "How long do refunds take?" and "When will I get my money back?" can then share an answer. Libraries such as RedisVL and GPTCache make this a few lines of code, and that ease is the danger.

Embeddings measure topic similarity, not whether two questions have the same answer. "How do I cancel my order?" and "How do I cancel my subscription?" sit very close together, and so do "Can I return opened items?" and "Can't I return opened items?" A semantic cache will happily answer one with the other, confidently and instantly, and nothing in your logs will look like an error. This is a **false hit**, and it's worse than a slow answer, because the user gets a wrong one.

If you still want one, treat the threshold as a classifier and measure it like one, with the tools from Eval Statistics. Collect a few hundred pairs of real questions, label each pair "same answer" or "different answer," and compute the precision of cache hits at several thresholds. A false-hit rate of 2% on a route serving 50,000 requests a day is a thousand wrong answers a day. Keep every rule from exact caching (scope, version, expiry) and add one more: send a sample of semantic hits to your review queue from From Traces to Evals. In practice, most teams get the bulk of the savings from prompt caching and exact response caching, and reserve semantic caching for public, high-volume, low-stakes questions.

### Choosing a model per step with evals

Model choice is the biggest lever after caching, and the riskiest, because it changes what the model can do. The method is the same one you used in Chaining and Routing, made rigorous: pick one expensive step, build or reuse an eval set for that step alone, run every candidate on the same cases, and put the results in a **cost/quality table**.

Candidates aren't just models. Reasoning **effort** (on models that support it) changes how much a model thinks, and with it cost and latency, without changing the model. Before stepping down to a smaller model, try the current model at lower effort, and check whether a newer model in the same tier is now cheaper per completed task. Here's a script for a classification step:

```python
# model_table.py  (run with: uv run model_table.py cases.jsonl)
# cases.jsonl has one {"text": ..., "label": ...} per line, at least 50 lines.
import json
import os
import sys
import time
from pathlib import Path

import anthropic
import numpy as np
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
CHEAP = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
CAPABLE = os.environ.get("MIMIR_CAPABLE_MODEL", "claude-sonnet-5-5")
PRICES = {CHEAP: (0.10, 0.50), CAPABLE: (2.00, 10.00)}  # $/M input, output; check the pricing page
CONFIGS = [(CAPABLE, "medium"), (CHEAP, "medium"), (CHEAP, "low")]  # the first is the baseline
PROMPT = ("Classify the support ticket as billing, bug, how_to or other. "
          "Reply with the label only.\n\n<ticket>\n{text}\n</ticket>")


def run_case(model: str, effort: str, text: str) -> tuple[str, float, float]:
    start = time.perf_counter()
    r = client.messages.create(model=model, max_tokens=4000, output_config={"effort": effort},
                               messages=[{"role": "user", "content": PROMPT.format(text=text)}])
    seconds = time.perf_counter() - start
    answer = "".join(b.text for b in r.content if b.type == "text").strip().lower()
    p_in, p_out = PRICES[model]
    return answer, (r.usage.input_tokens * p_in + r.usage.output_tokens * p_out) / 1e6, seconds


def bootstrap_ci(x: np.ndarray, n: int = 10_000, seed: int = 0) -> tuple[float, float]:
    idx = np.random.default_rng(seed).integers(0, len(x), size=(n, len(x)))
    low, high = np.percentile(x[idx].mean(axis=1), [2.5, 97.5])
    return float(low), float(high)


cases = [json.loads(line) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()]
results = {}
for model, effort in CONFIGS:
    rows = [run_case(model, effort, c["text"]) for c in cases]
    correct = np.array([a == c["label"] for (a, _, _), c in zip(rows, cases)], dtype=float)
    results[(model, effort)] = (correct, np.array([r[1] for r in rows]), np.array([r[2] for r in rows]))

base = results[CONFIGS[0]][0]
print(f"{'config':<28}{'accuracy (95% CI)':<22}{'vs baseline':<20}{'$/correct':>10}{'p50 s':>7}{'p95 s':>7}")
for (model, effort), (correct, cost, secs) in results.items():
    lo, hi = bootstrap_ci(correct)
    dlo, dhi = bootstrap_ci(correct - base)  # paired: same cases, resampled together
    print(f"{model + ' ' + effort:<28}{correct.mean():.0%} ({lo:.0%}-{hi:.0%})".ljust(50)
          + f"{dlo:+.0%} to {dhi:+.0%}".ljust(20)
          + f"{cost.sum() / max(correct.sum(), 1):>10.6f}"
          + f"{np.percentile(secs, 50):>7.2f}{np.percentile(secs, 95):>7.2f}")
```

The output is one row per configuration: accuracy with a bootstrap interval, the **paired** difference from the baseline (Eval Statistics showed why comparing the same cases is far more sensitive than comparing two separate intervals), cost per *correct* answer, and latency percentiles. The script runs the cases one at a time to keep latency honest and to stay well under rate limits; for a large set, run it as a batch job, as the next lesson shows.

Read the table as a set of trade-offs, not a ranking. Plot each configuration as quality against cost, and the ones worth considering lie on the **Pareto frontier**: no other configuration is both cheaper and better. Then apply your rule. A good one is: "switch to the cheapest configuration whose paired difference from the baseline has a lower bound above -2 points." That's a **non-inferiority** test: you're not trying to prove the cheap model is better, only that it isn't meaningfully worse. And look at the hard cases separately. On easy tickets every model looks the same, and the cheap one wins; the cost of a weaker model shows up in the hardest tenth, so read the cases that flipped from right to wrong before you switch.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Save the table

Commit the table with the date, the prompt version and the prices you used. Models and prices change several times a year, and the next time a new model comes out, rerunning one script tells you whether to switch.

</div>

### Model routing

Sometimes no single configuration is right for every request: the cheap model handles 85% of tickets perfectly and fumbles the rest. **Model routing** sends each request to a model chosen for that request. You built the simplest version in Chaining and Routing, a classifier or a rule that sends hard inputs to the capable model. Two more patterns are common in production.

A **cascade** tries the cheap model first and escalates only when a check fails. The check must be cheap and reliable: the output fails schema validation, a code check fails (tests don't pass, a cited passage doesn't contain the claim), or the model itself flags low confidence through a field you asked for in structured output. The appeal is that you pay for the capable model only on the requests that need it. The cost is easy to write down:

```text
cost per request = cheap cost + escalation rate x capable cost
```

With the cheap model at a twentieth of the capable model's price, a cascade that escalates 20% of requests costs 0.05 + 0.2 = 0.25 of the all-capable price. At 60% escalation it costs 0.65, and the escalated requests are also *slower*, because they made two calls. So measure the escalation rate on real traffic, and watch it after every prompt change.

A **learned router** is a small model trained to predict, from the request alone, which model will answer well. Research such as RouteLLM and FrugalGPT (see Additional resources) shows large savings on benchmarks, and gateways like LiteLLM offer routing as configuration. Treat them like any other model: measure the router's mistakes in both directions with your eval, because a router that sends a hard request to the cheap model produces exactly the quiet quality drop you're trying to avoid.

Every router has three hidden costs. **Caches are per model**, so splitting traffic across two models gives each a smaller, colder cache; switch models at step boundaries, never in the middle of a conversation. **Prompts are tuned per model**, so the cheap route may need its own prompt, with its own eval row. And **two models mean two sets of behaviors to monitor**: log which model served each request on its trace, and break your quality metrics down by route. A router you can't see into is a router you can't trust.

### On other providers

Everything in this lesson except the exact cache syntax is provider-neutral: layered prompts, hit-rate monitoring, response caching, cost/quality tables and routing work the same anywhere. Caching itself differs. The `cache_control` breakpoints, the 1.25 and 2 times write prices and the two lifetimes are Claude features. OpenAI caches long prompt prefixes automatically, with no breakpoints to place, and reports the reused part as `usage.prompt_tokens_details.cached_tokens` inside its prompt total; its [prompt caching guide](https://platform.openai.com/docs/guides/prompt-caching) lists the minimum length and options for improving hit rates. Google's Gemini API offers both automatic caching and explicit caches you create and pay to store by the hour, described in its [context caching docs](https://ai.google.dev/gemini-api/docs/caching). The layering advice is the same everywhere: shared content first, personal content last. Self-hosted open models served through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) or a server like vLLM reuse a prefix that's still in memory, with no per-token bill; there, caching saves time rather than money. In `model_table.py`, a second provider is one more entry in `CONFIGS` with a matching `run_case`:

```python
from openai import OpenAI

openai_client = OpenAI()  # reads OPENAI_API_KEY


def run_case_openai(model: str, text: str, prices: tuple[float, float]) -> tuple[str, float, float]:
    start = time.perf_counter()
    r = openai_client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": PROMPT.format(text=text)}])
    seconds = time.perf_counter() - start
    answer = (r.choices[0].message.content or "").strip().lower()
    cost = (r.usage.prompt_tokens * prices[0] + r.usage.completion_tokens * prices[1]) / 1e6
    return answer, cost, seconds
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [prompt caching guide](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) in the Claude docs, now as the owner of a busy service.
   - Focus on breakpoint placement with several breakpoints, the 1-hour lifetime and its ordering rule, pricing, and what invalidates the cache. Other providers' caching works on the same prefix idea.
1. Read [Choosing the right model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) for a practical way to trade off capability, speed and cost.
   - Then open the [models overview](https://platform.claude.com/docs/en/about-claude/models/overview) and the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing), and note the price per million input, output, cache-write and cache-read tokens for a small and a large model.
1. Read the [token counting guide](https://platform.claude.com/docs/en/build-with-claude/token-counting) to learn how to estimate the cost of a prompt before you send it, which helps you size the layers of a cached prompt.
1. Read the model routing and caching sections of Chip Huyen's [Building A Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html), which shows where routers, gateways and caches sit in a real system, including the semantic-cache trade-offs.
1. Practice: cache across users.
   - Take an app you've built with a long system prompt or shared documents, such as Chat With Your Docs, and restructure its prompt into layers with `build_request()` and the identical-prefix test from this lesson.
   - Send 20 requests from at least three simulated users and report the cache hit rate before and after. Then add `datetime.now()` to the system prompt, watch the test fail and the hit rate drop, and remove it.
1. Practice: build a cost/quality table.
   - Pick the most expensive step in that app, freeze 50 cases for it, and run `model_table.py` (adapted to your step) on at least three configurations, including a lower effort level and, if you can, a second provider.
   - Write two sentences on which configuration you would ship and why, quoting the paired difference. If you need a refresher on bootstrap intervals, redo `uv run pytest evals/06_bootstrap_ci` in the [evals exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals).

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How do you find which part of a production app is worth optimizing first?](#where-the-money-goes-in-production)
- [How should you lay out a prompt so that many users share one cached prefix, and what breaks the sharing?](#prompt-caching-across-users)
- [When does the 1-hour cache lifetime pay off, and why should you alert on the cache hit rate?](#cache-economics-and-lifetimes)
- [What must a response cache key include, and which answers should never be cached?](#response-caching)
- [What is a false hit in a semantic cache, and how would you measure the false-hit rate?](#semantic-caching-and-its-risks)
- [What goes in a cost/quality table, and what is a non-inferiority rule for switching to a cheaper configuration?](#choosing-a-model-per-step-with-evals)
- [How do you estimate the cost of a cascade, and what hidden costs does any model router add?](#model-routing)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming) is the reference for streaming responses, which cuts time to first token even when total time stays the same.
- [Cost optimization](https://platform.claude.com/docs/en/build-with-claude/cost-optimization) in the Claude docs walks through the levers in order (caching, effort, model choice, batching) with measured trade-offs.
- RedisVL's [LLM cache guide](https://redis.io/docs/latest/develop/ai/redisvl/user_guide/llmcache/) shows how a semantic cache is built, including the distance threshold you would need to measure.
- [RouteLLM](https://lmsys.org/blog/2024-07-01-routellm/) from LMSYS describes training a router between a strong and a weak model, with cost/quality curves.
- [FrugalGPT](https://arxiv.org/abs/2305.05176) is the research paper behind the LLM cascade idea: try cheap models first and escalate only when needed.
- LiteLLM's [routing docs](https://docs.litellm.ai/docs/routing) show how an open-source gateway expresses routing and fallbacks across providers as configuration.
