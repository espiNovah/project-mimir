### Introduction

You've written a new prompt. Your offline eval says it's better: on 200 golden cases, a paired bootstrap puts it 6 points ahead. Should you ship it to everyone at once? Real users send inputs your golden set never imagined, they react to tone and length in ways a judge can't predict, and a prompt that's 6 points better on your test set can be slower, pricier or more annoying in practice. If it goes wrong, you want to find out from 5% of your users, not all of them, and you want to switch it off in seconds without a deploy.

This lesson gives you two tools for that. **Feature flags** let you turn code paths on and off, for some users or all of them, without redeploying. **A/B tests** use the same machinery to show two versions to two random groups of real users and measure which one actually works better. Together they're how teams ship prompt and model changes with confidence. You'll build a small flag system in plain Python, wire a prompt experiment into a model call, and analyze its results with the confidence intervals you learned in Eval Statistics.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why separating deploying from releasing makes changes safer.
- How to write feature flags in code, and the different jobs flags do.
- How percentage rollouts use stable hashing so each user gets a consistent experience.
- What a kill switch is, and how to make flags fail safely.
- The open-source and hosted flag tools worth knowing, and the OpenFeature standard.
- How to run an A/B test on a prompt or model: metrics, sample size and analysis.
- Why online A/B tests complement offline evals instead of replacing them.

### Separate deploying from releasing

Until now, putting code on the server and turning it on for users have been the same event. Push to main, the platform deploys, everyone gets the new behavior. Feature flags split those apart. **Deploying** puts new code on the server. **Releasing** decides who it runs for. With a flag, you can deploy the new summarizer on Monday with the flag off, turn it on for yourself on Tuesday, for 5% of users on Wednesday, and for everyone next week, all without another deploy. If something looks wrong at any point, you turn the flag off and everyone is back on the old path within seconds.

This complements what you learn in Environments and Releases. A rollback replaces the whole running version and takes minutes; a flag switches one feature and takes seconds. Teams use both.

Flags do several different jobs, and it helps to name them, because they live for different lengths of time:

- **Release flags** hide unfinished or risky work while it rolls out. They should be deleted within weeks, once the feature is fully on.
- **Experiment flags** split users between versions for an A/B test. They're deleted when the test ends.
- **Operational flags**, including **kill switches**, let you turn off an expensive or fragile feature during an incident. They may live for years.
- **Permission flags** turn features on for particular users, such as beta testers or paying customers.

Every flag is an `if` statement that doubles the number of ways your code can run, so stale flags are real technical debt. When you add a release flag, write down when it should be removed, and remove it.

### Flags in code

A flag system needs only three things: a place to store flag settings, a function your code calls to ask "is this on for this user?", and a rule for what happens when the settings can't be read. Here's a complete one in the standard library. The settings live in a JSON file that the app rereads every 30 seconds, so editing the file (or pointing it at a mounted config, or swapping it for a database table later) changes behavior without a deploy:

```python
# flags.py: feature flags with stable percentage rollouts, using only the standard library.
import hashlib
import json
import os
import time
from pathlib import Path

FLAGS_FILE = Path(os.environ.get("FLAGS_FILE", "flags.json"))
RELOAD_SECONDS = 30                      # pick up edits without a redeploy
_cache: dict = {"loaded_at": float("-inf"), "flags": {}}


def load_flags() -> dict:
    """Read the flag file at most every RELOAD_SECONDS. On any error, keep the last good copy."""
    if time.monotonic() - _cache["loaded_at"] > RELOAD_SECONDS:
        try:
            _cache["flags"] = json.loads(FLAGS_FILE.read_text())
        except (OSError, json.JSONDecodeError):
            pass                         # unreadable file: keep the old flags (or none at all)
        _cache["loaded_at"] = time.monotonic()
    return _cache["flags"]


def bucket(flag_key: str, user_id: str) -> float:
    """A number in [0, 100) that depends only on the flag and the user, on every machine, forever."""
    digest = hashlib.sha256(f"{flag_key}:{user_id}".encode()).digest()
    return int.from_bytes(digest[:8]) / 2**64 * 100


def is_enabled(flag_key: str, user_id: str, default: bool = False) -> bool:
    flag = load_flags().get(flag_key)
    if flag is None:
        return default                   # unknown flag or no flag file: use the safe default
    if not flag.get("enabled", False):
        return False                     # the kill switch: off means off for everyone
    if user_id in flag.get("allow", []):
        return True                      # always on for these users, such as your own account
    return bucket(flag_key, user_id) < flag.get("rollout_percent", 0)


def variant(flag_key: str, user_id: str, default: str = "control") -> str:
    """Pick an experiment arm by weight, for example {"control": 50, "concise": 50}."""
    flag = load_flags().get(flag_key)
    if flag is None or not flag.get("enabled", False):
        return default
    point, cumulative = bucket(flag_key, user_id), 0.0
    for name, weight in flag["variants"].items():
        cumulative += weight
        if point < cumulative:
            return name
    return default
```

And the settings file it reads:

```json
{
  "new_summarizer": {"enabled": true, "rollout_percent": 10, "allow": ["user-ana"]},
  "summary_prompt_test": {"enabled": true, "variants": {"control": 50, "concise": 50}}
}
```

In your app, a flag check is just a branch: `if is_enabled("new_summarizer", user.id): ...`. Flags are checked on every request, so they have to be fast, which is why the file is cached rather than read each time. A hosted flag service does the same thing: its SDK downloads the rules in the background and evaluates them in memory, so checking a flag never waits on the network.

### Percentage rollouts with stable hashing

A percentage rollout needs to answer "is this user in the 10%?" with the same answer every time. If you used `random.random() < 0.10`, a user would see the new summarizer on one request and the old one on the next, which is confusing for them and makes any measurement useless. You could store each user's assignment in a database, but there's a neater trick: compute it.

`bucket()` feeds the flag name and the user's ID through **SHA-256**, a hash function that turns any input into a fixed-size number that looks random but is completely determined by the input. It turns that into a number between 0 and 100. The same user and flag always land on the same number, on every server and after every restart, so no assignments need to be stored. Users with the rollout percentage below their number are in. This gives you three useful properties:

- **Consistent.** A user in the 10% stays in the 10%.
- **Monotonic.** Raising the rollout from 10% to 50% keeps everyone who already had the feature and adds more. Nobody flips back and forth.
- **Independent between flags.** Because the flag name is part of the hash input, the users in one flag's 10% are a different random group from the users in another's. Otherwise the same unlucky 10% would get every risky change.

Don't use Python's built-in `hash()` for this. For strings, it's randomized each time Python starts, so two servers (or one server after a restart) would put the same user in different groups. Running a quick check on 10,000 made-up user IDs shows the buckets behave as promised:

```text
rollout 10%: 1015 of 10000 users
rollout 50%: 4958 of 10000 users
everyone from the 10% stage is still in at 50%: True
```

Hash on an ID that stays the same for the user: their account ID if they're logged in, or an anonymous ID kept in a cookie if not. Hashing on a request ID would bring back the inconsistency you were avoiding.

### Kill switches

A **kill switch** is a flag whose job is to turn something off fast: a new model, an expensive agent feature, a call to a third-party tool that's failing. Two design rules make kill switches work when you need them.

First, **decide what "off" means before you need it**. Off might mean falling back to the previous prompt, to a cheaper model, to a cached answer, or to a polite "this feature is paused" message. Write the fallback path when you write the feature, and test it, because a fallback that has never run probably doesn't work.

Second, **fail safe**. If the flag settings can't be read (the file is missing, the flag service is down), every check must still return something sensible. In `flags.py` an unknown flag returns the `default` you pass in, and a broken file keeps the last good copy. Choose defaults so that a broken flag system leaves the app in its known-good state: new features default to off, and features that are already live default to on.

### Flag tools

Hand-written flags are fine for a portfolio app and a great way to understand the idea. Teams usually adopt a tool once they need a web dashboard, an audit log of who changed what, or targeting rules such as "on for users in the EU on the paid plan." All of the following can be tried without paying:

- **OpenFeature** isn't a flag service. It's an open, vendor-neutral standard API for checking flags, hosted by the Cloud Native Computing Foundation. Your code calls OpenFeature's SDK, and a **provider** plugin connects it to whichever flag service you use. Switching services then means swapping the provider, not rewriting every flag check. Its own small service, **flagd**, reads flags from a file much like `flags.json`.
- **Unleash** is an open-source flag server you can run yourself with Docker Compose. It has a dashboard, gradual rollouts, and SDKs for Python and JavaScript.
- **GrowthBook** is open source too, and combines flags with an experiment analysis engine that reads your event data and computes results for you.
- Hosted services such as **PostHog** and **Flagsmith** have free tiers, and **LaunchDarkly** is the best-known commercial option. You don't need any of them for this lesson.

Whatever you choose, the concepts in this lesson (stable bucketing, safe defaults, logging which version each user saw) are the same, so you'll recognize them in the tool's settings.

### A/B tests for prompts and models

An **A/B test**, also called an online controlled experiment, randomly splits real users into groups, gives each group a different version (the **arms**: the current version is the **control**, the new one the **treatment**), and compares a metric between the groups. Because the split is random, the groups are alike in every other way on average, so a difference in the metric is caused by the change, apart from chance, which the statistics measure.

For an AI app, an arm is a full recipe: a prompt, a model, maybe a temperature or a retrieval setting. Change one thing per test if you can, so you know what caused the result. The code needs to do two things on every request: assign the user to an arm with `variant()`, and log an **exposure** record saying which arm they saw. Later, outcome events such as a thumbs-up are joined to exposures by request ID:

```python
# experiment.py: serve one of two summary prompts, and log which one each user saw.
# setup: uv add anthropic   (flags.py and flags.json from above sit next to this file)
import json
import os
import time
import uuid

import anthropic

from flags import is_enabled, variant

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

# Each arm is a full recipe. To test a model instead of a prompt, change "model" in one arm.
ARMS = {
    "control": {"model": MODEL, "system": "Summarize the user's text in 3 to 5 sentences."},
    "concise": {"model": MODEL, "system": "Summarize the user's text in at most 2 sentences. "
                                          "Lead with the single most important point."},
}


def log_event(record: dict) -> None:
    with open("events.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")


def summarize(user_id: str, text: str) -> dict:
    if not is_enabled("summaries", user_id, default=True):     # kill switch for the whole feature
        return {"request_id": None, "summary": None, "message": "Summaries are paused."}

    arm = variant("summary_prompt_test", user_id)
    recipe = ARMS[arm]
    start = time.perf_counter()
    response = client.messages.create(
        model=recipe["model"],
        max_tokens=1000,
        system=recipe["system"],
        messages=[{"role": "user", "content": text}],
    )
    summary = "".join(block.text for block in response.content if block.type == "text")

    request_id = str(uuid.uuid4())
    log_event({                     # the exposure: who saw which arm, and what it cost
        "event": "exposure", "request_id": request_id, "ts": time.time(),
        "experiment": "summary_prompt_test", "arm": arm, "user_id": user_id,
        "model": recipe["model"], "latency_ms": round((time.perf_counter() - start) * 1000),
        "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens,
    })
    return {"request_id": request_id, "summary": summary}


def record_feedback(request_id: str, thumbs_up: bool) -> None:
    """Called by your POST /feedback endpoint. Joined to the exposure later by request_id."""
    log_event({"event": "feedback", "request_id": request_id, "ts": time.time(),
               "thumbs_up": thumbs_up})
```

In your LLM-Powered API, `summarize` becomes the body of an endpoint, and the events go into the same traces table or JSONL file you already keep, with the arm added as one more field. Recording the arm on every trace pays off later: when someone reports a bad answer, you can see which version produced it.

### Choosing what to measure

Pick your metrics before the test starts, and write them down. Deciding afterwards lets you hunt through twenty numbers for the one that looks good, which is how false wins get shipped. A good plan has three kinds of metric:

- **One primary metric**, the one that decides the test. It should reflect what users actually value and respond to your change within the test's length. For a summarizer, the thumbs-up rate per rated summary is a reasonable choice. Others are task completion, whether the user copied or used the answer, whether a support conversation was resolved without a human, or whether the user came back the next week.
- **Guardrail metrics** that must not get worse: p95 latency, cost per request, error rate, refusal rate, and safety flags from your guardrails. A prompt that wins on thumbs-up but doubles the cost may not be worth shipping.
- **Diagnostic metrics** that help you understand the result, such as summary length or how often users ask for a retry.

Explicit feedback is honest but sparse: often only a few percent of responses get a thumbs-up or thumbs-down, and the people who rate aren't typical users. Implicit signals such as copying, retrying or abandoning are plentiful but noisier. Many teams also run an LLM judge on a sample of live responses from each arm. That's a useful extra signal, but remember it measures what the judge thinks, which you validated on your offline data, not what users think.

### How many users you need

Online tests need far more data than offline evals. In Eval Statistics, the same test cases ran through both prompts, so a paired comparison could ignore every case where they agreed. In an A/B test each user sees only one arm, so you're comparing two different groups of people, and differences between people add noise. The usual formula for the number of users per arm, for detecting a change in a rate from `p_base` to `p_base + lift` with 95% confidence and 80% **power** (the chance of detecting a real effect of that size), is:

```text
n per arm = (1.96 + 0.84)**2 * (p1 * (1 - p1) + p2 * (1 - p2)) / lift**2
```

where `p1` and `p2` are the two rates. To detect a thumbs-up rate moving from 60% to 64%, that's about **2,300 rated summaries per arm**. If only 5% of summaries get rated, it's about 46,000 summaries per arm. Halving the lift you want to detect quadruples the number, for the same square-root reason as in Eval Statistics.

Two practical consequences. First, **fix the sample size and the end date before you start, and don't stop early because the result looks good**. Checking every day and stopping at the first significant result produces false wins far more often than 5% of the time (Evan Miller's article in the Assignment shows how much). Run for at least a full week too, so weekday and weekend users are both included. Second, **be honest about small apps**. A portfolio project with 30 users can't detect a 4-point change, and no statistics fix that. At that scale, use a percentage rollout as a safety mechanism (watch the guardrail metrics and errors while the new version reaches 5%, then 25%, then everyone) and rely on offline paired evals to decide which version is better.

### Analyzing the result

When the test ends, check that the experiment ran correctly before you look at the outcome. The first check is the **sample ratio**. A 50/50 split should give nearly equal numbers of users in each arm. If it doesn't, something is broken, such as one arm crashing before it logs its exposure, or a bot that only hits one arm, and the results can't be trusted however good they look.

Then compute the lift with a confidence interval. The bootstrap from Eval Statistics works, with one change: **resample users, not ratings**. One enthusiastic user who rated 40 summaries isn't 40 independent observations, and treating them that way makes the interval too narrow. This script runs the whole analysis on simulated logs, so you can try it before you have traffic:

```python
# analyze.py: did the concise prompt really get more thumbs-up?   setup: uv add numpy
import math

import numpy as np

rng = np.random.default_rng(seed=2)      # fixed seed: the same report every run


def users_needed(p_base: float, lift: float) -> int:
    """Users per arm to detect `lift` with 95% confidence and 80% power (one rating per user)."""
    p_new = p_base + lift
    z_alpha, z_power = 1.96, 0.84
    variance = p_base * (1 - p_base) + p_new * (1 - p_new)
    return math.ceil((z_alpha + z_power) ** 2 * variance / lift**2)


def simulate_arm(n_users: int, true_rate: float) -> tuple[np.ndarray, np.ndarray]:
    """Stand-in for your logs: per user, how many summaries they rated, and how many got a thumbs-up."""
    rated = rng.integers(1, 6, size=n_users)               # each user rated 1 to 5 summaries
    taste = rng.beta(true_rate * 4, (1 - true_rate) * 4, size=n_users)  # some users like everything
    return rated, rng.binomial(rated, taste)


def rate(rated: np.ndarray, ups: np.ndarray) -> float:
    return ups.sum() / rated.sum()


def bootstrap_lift(a, b, n_resamples: int = 5_000) -> tuple[float, float]:
    """95% interval for rate(b) - rate(a). Resample USERS, keeping each user's ratings together."""
    lifts = np.empty(n_resamples)
    for i in range(n_resamples):
        ia = rng.integers(0, len(a[0]), size=len(a[0]))
        ib = rng.integers(0, len(b[0]), size=len(b[0]))
        lifts[i] = rate(b[0][ib], b[1][ib]) - rate(a[0][ia], a[1][ia])
    return tuple(np.percentile(lifts, [2.5, 97.5]))


def sample_ratio_ok(n_a: int, n_b: int) -> bool:
    """A 50/50 split should give nearly equal arms. |z| > 3 means assignment or logging is broken."""
    n = n_a + n_b
    return abs(n_a - n / 2) / math.sqrt(n / 4) < 3


print(f"Plan: {users_needed(0.60, 0.04):,} users per arm to detect 60% -> 64%")

control = simulate_arm(2_400, true_rate=0.60)
concise = simulate_arm(2_400, true_rate=0.64)

print(f"sample ratio ok: {sample_ratio_ok(len(control[0]), len(concise[0]))}")
print(f"control: {rate(*control):.1%} thumbs-up over {control[0].sum():,} ratings")
print(f"concise: {rate(*concise):.1%} thumbs-up over {concise[0].sum():,} ratings")
low, high = bootstrap_lift(control, concise)
print(f"lift:    {rate(*concise) - rate(*control):+.1%} (95% CI {low:+.1%} to {high:+.1%})")
```

```text
Plan: 2,305 users per arm to detect 60% -> 64%
sample ratio ok: True
control: 60.2% thumbs-up over 7,230 ratings
concise: 64.0% thumbs-up over 7,228 ratings
lift:    +3.8% (95% CI +1.8% to +5.8%)
```

The interval sits above zero, so the concise prompt really does earn more thumbs-up, by somewhere between about 2 and 6 points. Before shipping it, check the guardrails from the exposure logs (latency, cost per request, errors) the same way, and read a sample of thumbs-down responses from each arm, just as you read the failing cases in error analysis. Report the result in the same honest shape as an offline eval: the lift, the interval, the method, the number of users and ratings, and the test's dates.

### Why online tests complement offline evals

Offline evals and online tests answer different questions, and a careful team uses both, in order.

**Offline evals** run your golden set through both versions before anything ships. They're fast, cheap, repeatable and paired, so they detect small differences with a few hundred cases, and they never expose a user to a bad version. They catch regressions in CI. But they only measure the inputs you thought to include, graded by checks and judges that stand in for users.

**Online tests** measure real users with real inputs on the outcomes you actually care about, including things no offline set captures: whether a shorter answer feels more useful, whether a slower model makes people give up, how much the change costs at real volume. But they're slow, need lots of traffic, expose some users to the worse version, and only tell you *that* something changed, not *why*.

So the usual pipeline is: the offline eval acts as a gate (a version that fails it never reaches users); then a small percentage rollout watches for errors and guardrail problems; then, if you have enough traffic, an A/B test decides whether it's better; then a full rollout and removing the flag. Some teams add **shadow testing** before the rollout: the new version runs on a copy of live requests and its outputs are logged and judged, but never shown to users. And the loop closes: the interesting failures you find online become new golden cases for the offline set, which From Traces to Evals covers.

### On other providers

Flags, bucketing, exposure logs and the statistics are all provider-neutral, so everything in this lesson works the same with any model. The one piece that changes is the model call inside an arm. An A/B test is also the fairest way to compare providers on your own traffic, so an arm can just as well be "the same prompt on another provider's model." Two things need care when arms use different providers. First, log usage under one schema: the Anthropic SDK reports `usage.input_tokens` and `usage.output_tokens`, OpenAI's Chat Completions API reports `usage.prompt_tokens` and `usage.completion_tokens`, so convert both to the same fields and to cost per request before you compare guardrails. Second, system prompts move: Claude takes a top-level `system` parameter, while OpenAI-style APIs put it in the messages list as a `system` (or `developer`) message. See OpenAI's [Chat Completions API reference](https://platform.openai.com/docs/api-reference/chat) for the full shape. An open model run locally through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) makes a free extra arm for offline comparisons, though a laptop model shouldn't serve real users' traffic.

```python
# An arm that calls an OpenAI-compatible API instead (uv add openai).
import os

from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY; for Ollama: OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
response = client.chat.completions.create(
    model=os.environ.get("MIMIR_OPENAI_MODEL", "gpt-5-mini"),
    messages=[
        {"role": "system", "content": recipe["system"]},
        {"role": "user", "content": text},
    ],
)
summary = response.choices[0].message.content
input_tokens, output_tokens = response.usage.prompt_tokens, response.usage.completion_tokens
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Feature Toggles (aka Feature Flags)](https://martinfowler.com/articles/feature-toggles.html) by Pete Hodgson on Martin Fowler's site. It's the classic explanation of the kinds of flags, how long each should live, and how to keep flag code from turning into a mess.
   - Read up to and including "Implementation Techniques." Skim the rest.
1. Read [How Not To Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html) by Evan Miller. It shows with numbers why peeking at results and stopping early produces false wins.
   - Then try his [sample size calculator](https://www.evanmiller.org/ab-testing/sample-size.html) with your own app's numbers: your current thumbs-up rate and the smallest lift worth shipping.
1. Skim the [OpenFeature introduction](https://openfeature.dev/docs/reference/intro) and its [Python SDK page](https://openfeature.dev/docs/reference/sdks/server/python/), so you can recognize providers, evaluation context and hooks when you meet them in a real codebase.
   - Optionally, skim the [Unleash](https://docs.getunleash.io/) or [GrowthBook](https://docs.growthbook.io/) docs to see a full flag service. Both can run on your laptop with Docker.
1. Practice: add flags and an experiment to your LLM-Powered API.
   - Add `flags.py` and a `flags.json` with a kill switch for your main model-calling endpoint and an experiment with two prompt arms. Write the fallback for when the kill switch is off.
   - Write pytest tests: the same user always gets the same arm; raising `rollout_percent` never removes a user; a missing flag file returns the default; turning `enabled` off turns the feature off for everyone, including the allow list.
   - Log the arm on every trace, and add a `POST /feedback` endpoint that records a thumbs-up or thumbs-down by request ID.
1. Practice: analyze an experiment.
   - Run `analyze.py`, then change it to read your own `events.jsonl`: join feedback to exposures by `request_id`, and group by `user_id`. Generate a few hundred fake events with a script if you don't have real traffic, and say so in your README.
   - Add a guardrail check that reports p95 latency and average output tokens per arm.
   - If you haven't done it already, `uv run pytest evals/06_bootstrap_ci` in the [evals exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals) exercises the general bootstrap that `bootstrap_lift` builds on.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between deploying and releasing, and what four jobs do flags do?](#separate-deploying-from-releasing)
- [Why does a percentage rollout hash the flag name and user ID instead of using a random number or Python's hash function?](#percentage-rollouts-with-stable-hashing)
- [What is an exposure log, and why should every trace record the arm?](#a-b-tests-for-prompts-and-models)
- [What are primary, guardrail and diagnostic metrics, and why choose them before the test starts?](#choosing-what-to-measure)
- [Why does an A/B test need many more samples than an offline paired eval, and why shouldn't you stop it early?](#how-many-users-you-need)
- [Why should the bootstrap resample users rather than ratings, and what does a sample ratio check catch?](#analyzing-the-result)
- [What can online tests measure that offline evals can't, and the other way around?](#why-online-tests-complement-offline-evals)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Diagnosing Sample Ratio Mismatch in A/B Testing](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/) from Microsoft's experimentation team lists the many ways an experiment's split goes wrong, and how to find the cause.
- [flagd](https://flagd.dev/) is OpenFeature's small open-source flag service. It reads flags from a JSON file, like this lesson's `flags.py`, and serves them to any OpenFeature SDK.
- [GrowthBook's statistics documentation](https://docs.growthbook.io/statistics/overview) explains how a production experimentation tool computes results, including the choice between frequentist and Bayesian methods.
