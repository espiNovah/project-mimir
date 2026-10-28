### Introduction

Network calls are slow. Not slow like a heavy calculation, where your computer is working hard, but slow like waiting for a letter in the mail: your program sends a request and then does nothing at all until the answer arrives. A weather lookup might take 200 milliseconds. A language model call might take 20 seconds.

If you need ten weather forecasts, or need to ask a model ten questions, doing them one after another means waiting for each in turn. **Async** programming lets your program start all ten requests and then wait for them together, so the total time is roughly the time of the slowest one instead of the sum of all of them. Agents lean on this constantly, for example when they run several tool calls at once. This lesson introduces Python's built-in async system, `asyncio`, at the level you need to use it confidently.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The difference between waiting (I/O-bound) and computing (CPU-bound) work.
- What coroutines, `async def` and `await` are.
- How the event loop runs many tasks on a single thread.
- Running tasks concurrently with `asyncio.gather` and `asyncio.TaskGroup`.
- Making async HTTP requests with `httpx.AsyncClient`.
- Limiting concurrency with a semaphore, and common async mistakes.

### Waiting versus working

Programs are slow for one of two reasons:

- **CPU-bound** work: the processor is busy calculating, such as resizing a thousand images.
- **I/O-bound** work: the program is waiting on input/output, such as a network response, a file on a slow disk or a database.

Async helps with I/O-bound work. While one request is waiting for a server, your program can send another one. It does *not* make CPU-bound work faster. Almost everything you'll do with model APIs is I/O-bound, so async is a great fit.

### Coroutines, async and await

Here's the smallest useful example. `asyncio.sleep` stands in for a slow network call:

```python
import asyncio
import time


async def fetch(name: str, seconds: float) -> str:
    print(f"start {name}")
    await asyncio.sleep(seconds)    # pretend this is a network request
    print(f"done  {name}")
    return f"{name} result"


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(
        fetch("A", 1.0),
        fetch("B", 1.0),
        fetch("C", 1.0),
    )
    print(results)
    print(f"took {time.perf_counter() - start:.1f}s")   # about 1.0s, not 3.0s


asyncio.run(main())
```

Three new pieces:

- `async def` defines a **coroutine function**. Calling `fetch("A", 1.0)` doesn't run it; it creates a **coroutine object**, a paused piece of work waiting to be started.
- `await` means "run this, and while it's waiting, let other work happen." You can only use `await` inside an `async def` function.
- `asyncio.run(main())` starts the **event loop**, the scheduler that runs coroutines, and runs `main` until it finishes. You normally call it once, at the very top of your program.

`asyncio.gather` takes several coroutines, runs them concurrently, and returns their results in the same order you passed them in, regardless of which finished first.

<div class="lesson-note" markdown="1">

#### One thread, many tasks

The event loop runs on a single thread. It is not doing three things at the same instant. Each coroutine runs until it hits an `await` on something slow, then hands control back to the loop, which picks another coroutine that's ready. Because all the time is spent waiting anyway, taking turns is enough to overlap the waits. This is called **concurrency**, as opposed to true **parallelism**.

</div>

### Async HTTP with HTTPX

Here's where HTTPX pays off: it has an async client with the same interface you already know. Compare the timing of sequential and concurrent requests to the GitHub API:

```python
import asyncio
import time

import httpx

USERS = ["octocat", "torvalds", "gvanrossum", "defunkt", "mojombo"]


async def fetch_user(client: httpx.AsyncClient, username: str) -> dict:
    response = await client.get(f"https://api.github.com/users/{username}")
    response.raise_for_status()
    return response.json()


async def main() -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        start = time.perf_counter()
        for username in USERS:                       # one at a time
            await fetch_user(client, username)
        print(f"sequential: {time.perf_counter() - start:.2f}s")

        start = time.perf_counter()
        users = await asyncio.gather(*(fetch_user(client, u) for u in USERS))
        print(f"concurrent: {time.perf_counter() - start:.2f}s")

    for user in users:
        print(user["login"], user["public_repos"])


asyncio.run(main())
```

Two details matter:

- `async with httpx.AsyncClient() as client` creates one client and reuses it for every request. A client keeps connections open between requests, which is faster, and the `async with` block closes them cleanly at the end.
- The `*` in `gather(*(...))` unpacks a generator of coroutines into separate arguments.

On a typical connection the concurrent version is several times faster, and the gap grows with the number of requests.

### Handling failures in concurrent code

By default, if any coroutine passed to `gather` raises an exception, `gather` raises that exception and you lose the other results. When you want "give me everything, including the failures," pass `return_exceptions=True`. Then each slot in the result list is either a value or an exception object:

```python
results = await asyncio.gather(
    *(fetch_user(client, u) for u in ["octocat", "no-such-user-12345"]),
    return_exceptions=True,
)
for username, result in zip(["octocat", "no-such-user-12345"], results):
    if isinstance(result, Exception):
        print(f"{username}: failed ({result})")
    else:
        print(f"{username}: {result['public_repos']} repos")
```

This is exactly the behavior you want in a tool that looks up several cities: one bad city name shouldn't stop the others from printing. Python 3.11 also added `asyncio.TaskGroup`, which does the opposite: if one task fails, it cancels the rest. Use it when the tasks only make sense together.

### Limiting concurrency

Firing off 500 requests at once is a good way to get rate limited (that `429` status code). An `asyncio.Semaphore` caps how many coroutines can be inside a block at the same time:

```python
limit = asyncio.Semaphore(5)


async def fetch_user_politely(client: httpx.AsyncClient, username: str) -> dict:
    async with limit:          # at most 5 requests in flight
        return await fetch_user(client, username)
```

You'll use this pattern again when you send many prompts to a model API.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Common async mistakes

- **Forgetting `await`.** `fetch_user(client, "octocat")` without `await` gives you a coroutine object, not a result, and Python warns "coroutine was never awaited."
- **Blocking the loop.** Calling `time.sleep()` or the regular `httpx.get()` inside an async function freezes every other task. Use `await asyncio.sleep()` and `AsyncClient` instead.
- **Calling `asyncio.run` repeatedly.** Call it once at the top; inside async code, just `await`.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the official Python HOWTO [A Conceptual Overview of asyncio](https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html). It explains the event loop, coroutines and tasks from first principles, with the mental model this lesson only sketched.
   - Read Part 1 carefully. Skim Part 2 on how `await` works under the hood; come back to it later if you're curious.
1. Read the [Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html) page of the asyncio docs as a reference.
   - Read the sections on "Coroutines," "Creating Tasks," "Task Groups," "Sleeping," "Running Tasks Concurrently" (`gather`) and "Timeouts."
1. Read HTTPX's [Async Support](https://www.python-httpx.org/async/) page, which shows how `AsyncClient` mirrors the regular API.
1. Measure the speedup yourself.
   - Run the sequential versus concurrent GitHub example from this lesson and record both timings.
   - Add 10 more usernames (real or made up) and use `return_exceptions=True` so made-up users are reported without crashing the run.
   - Add a semaphore with a limit of 3 and measure again. Write two or three sentences in your learning journal explaining why the timing changed.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why does async help with I/O-bound work but not with CPU-bound work?](#waiting-versus-working)
- [What is a coroutine, and what does await do?](#coroutines-async-and-await)
- [How can one thread run many tasks at once?](#coroutines-async-and-await)
- [How do you send many HTTP requests concurrently with httpx.AsyncClient?](#async-http-with-httpx)
- [What happens when one task fails in asyncio.gather compared with a TaskGroup?](#handling-failures-in-concurrent-code)
- [Why limit concurrency with a semaphore, and what happens if you forget to await a coroutine?](#limiting-concurrency)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [HTTPX exceptions page](https://www.python-httpx.org/exceptions/) applies equally to the async client, so the error handling you learned in Working with APIs carries over unchanged.
