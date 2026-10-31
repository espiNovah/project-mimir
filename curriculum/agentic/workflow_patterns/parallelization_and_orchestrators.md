### Introduction

Some tasks are naturally made of independent pieces: review this code for security issues *and* style issues, or analyze the impact of a change on customers, employees *and* investors. Running those pieces at the same time makes a system faster, and sometimes more accurate. Other tasks can be split up too, but you cannot know how until you see the input. In this lesson you will learn **parallelization**, where your code splits the work, and **orchestrator-workers**, where a model decides how to split it.

In Chaining and Routing every step waited for the one before it. Here you'll fan out instead: start many calls at once, keep them under your provider's limits, and combine what comes back. You already used `asyncio.gather` in Tool Errors and Parallel Calls to run tool calls concurrently. This lesson uses the same tool on model calls, and adds the part that matters at scale: limits.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Sectioning: splitting a task into independent subtasks that run at once.
- Voting: running the same task several times and combining the answers.
- Running model calls concurrently in Python, with a semaphore and rate limits in mind.
- The orchestrator-workers pattern and how it differs from parallelization.
- How results from many calls are combined, including partial failures.
- The cost and latency trade-offs, and where these patterns sit between workflows and agents.

### Sectioning

**Sectioning** gives each call a different part of the job. Instead of one prompt that says "review this code for security, bugs and readability," you make three calls: one checks only security, one only bugs, one only readability. Your code then collects the three answers.

Why does this help? A model asked to check ten things at once tends to do each one less carefully than ten calls asked to check one thing each. Long checklists get skimmed. A narrow prompt also makes each piece easier to evaluate and improve: if the security reviewer misses SQL injection, you fix the security prompt without risking the readability one.

A classic use of sectioning is a **guardrail**, a check that runs beside the main work. One call answers the user's question while a second, independent call screens the request for abuse. Because they run at the same time, the screen adds almost no latency. If the screen flags the request, your code throws the answer away. Keeping the two jobs in separate calls also works better than asking one call to both answer and police itself, because each prompt has one clear goal.

Sectioning only works when the pieces are **independent**: no piece needs another's output. If the readability reviewer needs to know what the bug reviewer found, that's a chain, not a fan-out.

### Voting

**Voting** gives several calls the *same* job and combines their answers. The point is confidence. One model call that says "this content breaks our rules" might be a fluke; three out of three calls agreeing probably isn't.

You choose the **threshold** to match the cost of each kind of mistake, just as you did with judges in Evals in Practice. Flag content for human review if *any* of three voters says yes, when missing bad content is expensive. Block content automatically only if *all three* agree, when a false block would anger a real user. "Two out of three" sits in between.

Voting only helps if the voters can disagree. Three identical prompts to the same model often give identical answers, so the vote adds cost and no information. Some current models, including recent Claude models, no longer accept a `temperature` setting, so you can't simply turn up the randomness. Instead, vary the inputs: give each voter a different role ("security auditor," "penetration tester"), a different phrasing of the question, or a different model. Then check the payoff with an eval: does the vote actually beat a single call on your labeled examples, by enough to justify paying three times as much?

### Running calls concurrently

A model call spends almost all its time waiting for the provider's servers. That makes it a perfect fit for **concurrency**: start several calls, let them wait at the same time, and collect the results. With the async client, `asyncio.gather` does this. Three calls that each take four seconds take about twelve seconds one after another, but about four seconds together. The total is close to the **slowest** call, not the sum.

Starting everything at once has a catch. If you fan out over 500 documents, `gather` happily starts 500 requests in the same instant. Your provider will reject most of them with `429 Too Many Requests`, and your laptop may run out of network connections. You need a limit on how many calls are **in flight** (started but not finished) at once.

The tool for this is a **semaphore**: a counter that lets at most *n* tasks into a block of code at a time. `asyncio.Semaphore(5)` lets five calls run; the sixth waits at `async with` until one of the five finishes. Your code still starts all 500 tasks, but only five talk to the API at any moment.

A semaphore limits **concurrency**, not **rate**. Providers set rate limits as requests per minute and tokens per minute (input and output are often counted separately). Five concurrent calls that each finish in one second add up to 300 requests a minute, which can still exceed a small limit. So keep two defenses, both from Timeouts, Retries and Rate Limits: a concurrency cap you tune to your account's limits, and retries with backoff that respect the `retry-after` header on a `429`. The `anthropic` SDK already does the second one for you, as the OpenAI SDK does; the code below raises its retry count.

One more habit: by default, if any call inside `gather` raises an exception, `gather` raises it too, and you lose the other results. Pass `return_exceptions=True` to get exceptions back as values in the result list instead, so one failed call doesn't sink the other nine.

### Walkthrough: sectioning and voting

This script reviews a small function with three sectioned calls, runs a three-voter security vote at the same time, and times a sequential run for comparison. Set up a project with `uv init fanout`, run `uv add anthropic python-dotenv`, and save this as `fanout.py`:

```python
# fanout.py  (run with: uv run fanout.py)
import asyncio
import os
import time
from collections import Counter

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.AsyncAnthropic(max_retries=4)  # retries 429s, honoring retry-after
LIMIT = asyncio.Semaphore(5)  # (1) at most 5 requests in flight at once

CODE = '''
def login(username, password):
    query = f"SELECT * FROM users WHERE name = '{username}' AND pw = '{password}'"
    return db.execute(query).fetchone() is not None
'''


async def ask(system: str, user: str) -> str:
    async with LIMIT:  # the 6th caller waits here until a slot frees up
        response = await client.messages.create(
            model=MODEL, max_tokens=2000, output_config={"effort": "low"},
            system=system, messages=[{"role": "user", "content": user}])
    return "".join(b.text for b in response.content if b.type == "text")


ASPECTS = {  # (2) sectioning: each call gets one narrow job
    "security": "Review only for security problems. One line each, or say NONE.",
    "bugs": "Review only for bugs that give wrong results. One line each, or say NONE.",
    "readability": "Review only naming and clarity. At most three one-line suggestions.",
}
VOTERS = [  # (3) voting: the same question from different angles
    "You are a security auditor.",
    "You are a senior backend developer doing code review.",
    "You are a penetration tester looking for a way in.",
]
QUESTION = "Could an attacker exploit this code? Answer with only YES or NO.\n\n"


async def section(code: str) -> dict[str, str]:
    results = await asyncio.gather(*(ask(prompt, code) for prompt in ASPECTS.values()))
    return dict(zip(ASPECTS, results))  # gather keeps the order you passed in


async def vote(code: str, needed: int = 2) -> tuple[bool, Counter]:
    answers = await asyncio.gather(*(ask(v, QUESTION + code) for v in VOTERS),
                                   return_exceptions=True)  # (4) a failure becomes a value
    tally = Counter(
        "ERROR" if isinstance(a, Exception)
        else "YES" if a.strip().upper().startswith("YES")
        else "NO" if a.strip().upper().startswith("NO")
        else "UNCLEAR"
        for a in answers)
    return tally["YES"] >= needed, tally


async def main() -> None:
    start = time.perf_counter()
    for prompt in ASPECTS.values():  # one after another, for comparison
        await ask(prompt, CODE)
    print(f"sequential, 3 calls: {time.perf_counter() - start:.1f}s")

    start = time.perf_counter()
    review, (flagged, tally) = await asyncio.gather(section(CODE), vote(CODE))
    print(f"concurrent, 6 calls: {time.perf_counter() - start:.1f}s\n")
    for aspect, text in review.items():
        print(f"--- {aspect}\n{text}\n")
    print(f"flagged={flagged} votes={dict(tally)}")


asyncio.run(main())
```

Walk through the numbered comments:

1. **The semaphore.** Every call goes through `ask`, and `ask` takes a slot before calling the API. Raise the 5 if your account allows more; lower it if you see `429`s.
1. **Sectioning.** Three prompts, each with one job and an explicit "say NONE" so a clean result is easy to recognize.
1. **Voting.** Three different roles ask one yes/no question. The required answer format ("only YES or NO") makes the tally a string check instead of another model call.
1. **Partial failure.** With `return_exceptions=True`, a voter that fails after all its retries shows up as `ERROR` in the tally instead of crashing the run. Decide what an `ERROR` means for your threshold; here it simply doesn't count as a yes.

Run it and compare the two timings. The concurrent run makes twice as many calls and should still finish faster than the sequential three. It won't take quite as long as one call, though: six calls through a semaphore of five run in two waves. Change the limit to 6, then to 1, and watch the time move.

### Orchestrator-workers

In parallelization, *your code* decides the pieces in advance: always these three aspects, always these three voters. Many tasks can't be split that way. "Add a phone number to users" touches a different set of files in every codebase, and you can't know which until you read them. **Orchestrator-workers** lets a model plan the split:

1. An **orchestrator** call reads the task and returns a plan: a list of subtasks.
1. Your code sends each subtask to a **worker** call, usually concurrently.
1. A **synthesizer** call (sometimes the orchestrator again) combines the workers' results into one answer.

The difference from parallelization is only *who decides the pieces*. That makes orchestrator-workers more flexible, but also less predictable. The orchestrator might plan two subtasks today and seven tomorrow for a similar input, or invent a file that doesn't exist. Treat its plan like any other model output: give it a structured-output contract and put a gate on it, exactly as you learned in Chaining and Routing.

Here is a small orchestrator that plans changes to a pretend four-file codebase. Save it as `orchestrator.py` in the same project:

```python
# orchestrator.py  (run with: uv run orchestrator.py)
import asyncio
import os

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.AsyncAnthropic(max_retries=4)
LIMIT = asyncio.Semaphore(4)
MAX_WORKERS = 5

FILES = {  # a tiny pretend codebase
    "models.py": "class User:\n    name: str\n    email: str\n",
    "api.py": "@app.post('/users')\ndef create_user(name: str, email: str): ...\n",
    "emails.py": "def send_welcome(user):\n    send_email(user.email, f'Hi {user.name}')\n",
    "README.md": "# Users service\nCreate users with POST /users (name, email).\n",
}
TASK = "Add an optional phone number to users, and text new users a welcome if they gave one."


class Subtask(BaseModel):
    file: str
    instructions: str = Field(description="What to change in this file, for a developer")


class Plan(BaseModel):
    subtasks: list[Subtask] = Field(description="One entry per file that must change")


def text(response) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


async def orchestrate(task: str) -> list[Subtask]:
    listing = "\n\n".join(f"## {name}\n{body}" for name, body in FILES.items())
    response = await client.messages.parse(  # (1) the model decides the pieces
        model=MODEL, max_tokens=4000, output_format=Plan,
        system="You plan code changes. Pick only files that must change.",
        messages=[{"role": "user", "content": f"Task: {task}\n\nFiles:\n{listing}"}])
    if response.parsed_output is None:
        raise RuntimeError(f"No plan (stop_reason={response.stop_reason})")
    subtasks = [s for s in response.parsed_output.subtasks if s.file in FILES]  # (2) gate
    return subtasks[:MAX_WORKERS]  # and a hard cap on fan-out


async def work(sub: Subtask) -> str:
    async with LIMIT:  # (3) each worker sees one file and one instruction
        response = await client.messages.create(
            model=MODEL, max_tokens=4000, messages=[{"role": "user", "content":
                f"Change {sub.file} as follows: {sub.instructions}\n"
                f"Return only the full new file.\n\n{FILES[sub.file]}"}])
    return text(response)


async def synthesize(task: str, subs: list[Subtask], outputs: list) -> str:
    parts = "\n\n".join(
        f"<change file='{s.file}'>\n"
        + (f"FAILED: {o!r}" if isinstance(o, Exception) else o) + "\n</change>"
        for s, o in zip(subs, outputs))
    response = await client.messages.create(  # (4) check the pieces fit together
        model=MODEL, max_tokens=4000, messages=[{"role": "user", "content":
            f"Task: {task}\n\nProposed changes:\n{parts}\n\n"
            "First list any mismatches between files (names, arguments, missing pieces) "
            "and any FAILED change. Then write a one-paragraph pull request summary."}])
    return text(response)


async def main() -> None:
    subs = await orchestrate(TASK)
    for s in subs:
        print(f"plan: {s.file}: {s.instructions}")
    outputs = await asyncio.gather(*(work(s) for s in subs), return_exceptions=True)
    print("\n" + await synthesize(TASK, subs, outputs))


asyncio.run(main())
```

The numbered comments mark the four things that make this safe enough to run:

1. **A structured plan.** `Plan` is the contract, enforced with the Anthropic SDK's `messages.parse` helper as in Chaining and Routing. The orchestrator can't return a vague paragraph; it must return a list of `{file, instructions}` objects.
1. **A gate on the plan.** Subtasks for files that don't exist are dropped, and the fan-out is capped. Without the cap, one odd input could launch fifty workers. You could also make the gate stricter, for example by retrying the plan with feedback when it names an unknown file.
1. **Narrow workers.** Each worker gets only its file and its instruction, which keeps its context small and its job clear.
1. **A synthesizer with a checking job.** Workers can't see each other, so one might name the field `phone` and another `phone_number`. The synthesizer's first instruction is to look for exactly that kind of mismatch.

### Aggregating results

The last step of any fan-out is combining the results, and it deserves as much care as the fan-out itself. Pick the simplest method that works:

- **Code, when you can.** Voting tallies, merging lists, taking the maximum score or checking "did any reviewer say NONE?" are all plain Python. Code is free, instant and never misreads anything.
- **A synthesis call, when you must.** Merging three prose reviews into one, or checking that changes to four files agree, needs a model. Give it a clear job: remove duplicates, resolve disagreements and say how, flag gaps. Wrap each worker's output in labeled tags (`<change file='api.py'>`) so the synthesizer can tell them apart, and ask it to say which worker each point came from, which makes its output easy to check.

Decide in advance what happens when a worker fails. The orchestrator above passes failures through to the synthesizer as `FAILED`, so the summary can say "the README change failed" instead of silently leaving it out. Other systems retry the failed piece or stop the whole run. What matters is that a missing piece is never invisible.

Finally, test the aggregation step on its own, like any other step. Feed it hand-written worker outputs that disagree, overlap or include a failure, and check that it handles each case the way you want. This is cheaper and more reliable than hoping the full pipeline exercises those cases.

### Cost and latency trade-offs

Fan-out patterns trade money for time, and sometimes for quality. Before you reach for one, count the calls:

| Pattern | Calls per input | Latency is roughly |
| --- | --- | --- |
| One prompt | 1 | one call |
| Sectioning into *n* parts | *n* | the slowest part |
| Voting with *k* voters | *k* | the slowest voter |
| Orchestrator-workers | 1 + workers + 1 | plan, then the slowest worker, then the synthesis |

Every worker call also re-sends its own context, so tokens grow with the number of calls. Sectioning a 3,000-token document into three reviews sends that document three times. Orchestrator-workers also adds two steps that must run **one after another** (plan first, synthesize last), so it is rarely the fastest option, even though the workers run concurrently.

The semaphore adds one more effect: with 50 subtasks and a limit of 5, the work runs in about ten waves, so latency grows again. When the fan-out is large and nobody is waiting, such as tagging 10,000 documents overnight, consider a batch API instead. Many providers offer one at a discount; you'll meet the Message Batches API in the Production path.

The test is the same as in Chaining and Routing: run the pattern and a single-prompt baseline on the same labeled inputs, and compare quality, cost per input and latency. Fan-out is worth it when it buys accuracy you can measure, or speed a user actually feels.

### From workflows to agents

Orchestrator-workers is the last stop before agents. The orchestrator makes a real decision about the shape of the work, but only once: it plans, the workers run, and the workflow ends. If you let the orchestrator see the workers' results and plan again, as many times as it likes, you have built an agent that delegates to other model calls. That is what the Multi-Agent Systems section covers with full subagents that have their own tools and loops.

The trade-offs carry over and grow: more calls, more tokens, more coordination to get right, and more ways for one piece to drift from the others. The habits from this lesson carry over too. Give the planner a structured contract, gate its plan, cap the fan-out, limit concurrency, and make failures visible.

### On other providers

Sectioning, voting, the semaphore, `asyncio.gather` with `return_exceptions=True`, the gated plan and the aggregation step are plain Python, so they work with any provider's async client. Rate limits work the same way on OpenAI too: requests and tokens per minute, a `429` with a `Retry-After` header, and automatic retries in its SDK, as OpenAI's [rate limits guide](https://developers.openai.com/api/docs/guides/rate-limits) explains. The Claude-specific pieces in this lesson's code are `output_config={"effort": "low"}`, which becomes `reasoning_effort` on OpenAI's reasoning models, and `messages.parse` with `output_format=Plan`, which becomes `chat.completions.parse` with `response_format=Plan`, as shown in Chaining and Routing. A local open model changes the bottleneck: Ollama has no per-minute limit, but by default each model handles one request at a time and queues the rest, so a semaphore of 5 buys no speed until you raise `OLLAMA_NUM_PARALLEL` (see the [Ollama FAQ](https://docs.ollama.com/faq)), and a full queue answers with `503` rather than `429`. Mixing providers is also the easiest way to get voters that can disagree: one Claude voter, one OpenAI voter and one local model are far more independent than three copies of the same model. Here is `ask` from `fanout.py` for a local model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), using the same `LIMIT`:

```python
from openai import AsyncOpenAI  # uv add openai

local = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama", max_retries=4)

async def ask(system: str, user: str, model: str = "qwen3:4b") -> str:
    async with LIMIT:  # the same semaphore as before
        response = await local.chat.completions.create(model=model, messages=[
            {"role": "system", "content": system},  # the system prompt is a message here
            {"role": "user", "content": user}])
    return response.choices[0].message.content or ""
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read "Workflow: Parallelization" and "Workflow: Orchestrator-workers" in [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents). Note its examples of sectioning versus voting, and why it says orchestrator-workers fits tasks where you can't predict the subtasks.
1. Run Example 2 (parallelization) in the [basic workflows notebook](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/basic_workflows.ipynb), then work through the [orchestrator-workers notebook](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/orchestrator_workers.ipynb).
   - In the orchestrator notebook, find the exact prompt the orchestrator uses to plan subtasks and the code that parses its plan. Compare that parsing with the `Plan` model and gate in `orchestrator.py`: what happens in each when the plan is malformed?
   - The notebook's parallel example uses threads rather than `asyncio`. Both work for waiting on network calls; notice how each caps the number of workers.
1. Read the "Running Tasks Concurrently" section of the Python docs on [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html), then the `Semaphore` part of the docs on [asyncio synchronization primitives](https://docs.python.org/3/library/asyncio-sync.html).
1. Read the overview of Anthropic's [rate limits page](https://platform.claude.com/docs/en/api/rate-limits) to see how limits are measured (requests and tokens per minute) and what a `429` response tells you. Other providers use the same ideas with different numbers.
1. Practice: write a script that reviews a short paragraph of product copy with three parallel calls (grammar, tone and factual claims) and one final call that merges their feedback.
   - Time it running sequentially and concurrently, and write down both numbers.
   - Then run it over 20 paragraphs with a semaphore of 2, then 10, and record the total time and any `429`s for each setting.
   - Make one call fail on purpose (for example, pass a bad model ID to one aspect) and check that `return_exceptions=True` keeps the rest of the review alive and that the merge step reports the missing aspect.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is sectioning, and why do several narrow calls often beat one broad one?](#sectioning)
- [How do you choose a voting threshold, and how do you make voters able to disagree?](#voting)
- [What is the difference between limiting concurrency with a semaphore and staying under a rate limit?](#running-calls-concurrently)
- [How does orchestrator-workers differ from parallelization, and why should you gate the orchestrator's plan?](#orchestrator-workers)
- [When should results be combined with code instead of a synthesis call, and what should happen when a worker fails?](#aggregating-results)
- [Why is orchestrator-workers rarely the fastest pattern, even though its workers run concurrently?](#cost-and-latency-trade-offs)
- [What change would turn an orchestrator-workers workflow into an agent?](#from-workflows-to-agents)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html#task-groups) in the Python docs covers `TaskGroup`, a newer alternative to `gather` that cancels the remaining tasks when one fails, which is useful when partial results are worthless.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) from Anthropic describes an orchestrator that spawns parallel workers in production, including what it cost in tokens and what went wrong. It previews the Multi-Agent Systems section.
