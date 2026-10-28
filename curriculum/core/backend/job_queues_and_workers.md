### Introduction

A model call that summarizes a paragraph takes a second or two. One that extracts fields from a 40-page contract can take a minute, and if the provider is busy, longer. Doing that work inside an HTTP request causes trouble. The client sits waiting with an open connection, proxies and browsers give up after 30 to 100 seconds, a restart of your API kills every request that's in flight, and while a request is waiting it holds a database connection and a slot your server could be using for someone else.

The standard fix is to take slow work out of the request. The API writes down what needs doing, puts a small message on a **job queue**, and answers immediately: "accepted, here's your job ID." A separate program called a **worker** takes jobs off the queue one at a time, does the slow part, and stores the result. The client checks back with the ID until the job is finished. In this lesson you'll build exactly that with **Redis** as the queue and **arq** as the queue library, track every job in a Postgres table, retry failures a limited number of times, make the worker safe to run twice, and run the whole thing in Docker Compose.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- When work should leave the request, and the shape of the job pattern.
- What Redis is and why queues are built on it.
- How to track jobs in Postgres with pending, running, done and failed statuses.
- How to enqueue a job from FastAPI with arq, and how RQ compares.
- How to write a worker with limited retries.
- What idempotency means and how to make a job safe to run twice.
- How to add a worker and Redis to Compose, and how to test jobs without either.

### When work should leave the request

Not everything needs a queue. A model call that reliably finishes in a few seconds is fine inside an `async def` route, as you've been doing. Reach for a queue when any of these is true:

- **The work is slow or unpredictable**, such as long documents, multi-step chains or batch processing.
- **The work must survive a restart.** A job in Redis waits for a worker; a request in a crashed process is simply gone.
- **The work should be retried later** if it fails, without the client having to resend anything.
- **You need to control how much runs at once**, for example to stay under your model provider's rate limit. Ten workers mean at most ten model calls at a time, however many requests arrive.

The pattern always has the same three steps:

1. `POST /jobs` stores a job row with status `pending`, puts the job's ID on the queue, and returns **`202 Accepted`** with the ID. `202` means "I've accepted your request, but it isn't finished."
1. The worker takes the ID off the queue, marks the row `running`, does the work, and marks it `done` with the result, or `failed` with an error.
1. The client **polls** `GET /jobs/{id}`, asking every couple of seconds until the status is `done` or `failed`.

Polling is simple and works everywhere. Later, in the Frontend section, you'll see streaming, which pushes updates to the client instead.

### Redis in five minutes

**Redis** is a database that keeps its data in memory, which makes it extremely fast, and it's the most common place to put a job queue. Where Postgres stores rows in tables, Redis stores **keys** whose values can be strings, lists, sets, hashes and a few other structures. Start one with Docker and open its command-line client:

```bash
docker run --name mimir-redis -d -p 6379:6379 redis:8
docker exec -it mimir-redis redis-cli
```

Then try a few commands at the `127.0.0.1:6379>` prompt:

```text
SET greeting "hello"          # store a string under a key
GET greeting                  # "hello"
EXPIRE greeting 60            # delete it automatically in 60 seconds
LPUSH queue job-1 job-2       # push two items onto a list
RPOP queue                    # "job-1": first in, first out
```

That last pair is a queue in two commands: producers push onto one end of a list and consumers pop from the other. Queue libraries build on ideas like this, adding sorted sets for jobs scheduled in the future and extra keys for results and retry counts. You won't write Redis commands yourself in this lesson; arq does that. But knowing that it's all just keys in memory explains two things. Redis is fast, and **Redis is not where your important data lives**. A Redis that restarts without saving to disk loses everything, and the free Redis on Render keeps data only in memory. That's why the job's status and result go in Postgres. Redis only carries the message "job 42 needs doing."

Its URL looks like `redis://localhost:6379`, and like `DATABASE_URL`, it belongs in an environment variable called `REDIS_URL`.

### Job rows in Postgres

Each job gets a row that records everything about it. Add this to `models.py`, next to your `User` table from User Accounts and Auth:

```python
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user_account.id", index=True)
    input_text: str
    status: str = Field(default="pending", index=True)  # pending, running, done or failed
    attempts: int = 0
    result: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))


class JobCreate(SQLModel):
    text: str = Field(min_length=1, max_length=50_000)


class JobPublic(SQLModel):
    id: int
    status: str
    attempts: int
    result: str | None
    error: str | None
```

The status moves in one direction: `pending` → `running` → `done` or `failed`, with one exception you'll see under retries, where a failed attempt goes back to `pending` to wait for another try. `attempts` counts how many times the worker has started the job, and `error` keeps the last error message, so a `failed` job explains itself. The index on `status` makes it quick to ask "how many jobs are stuck in `running`?", a question you'll want answered on a bad day. Add the table with `uv run alembic revision --autogenerate -m "add job table"`, review the draft, and run `uv run alembic upgrade head`.

### Enqueueing from FastAPI

Install arq (it brings the `redis` client library with it):

```bash
uv add arq
```

**arq** is a small, `asyncio`-based job queue written by the author of Pydantic. It fits FastAPI well, because your job functions are `async def` functions, just like your routes, and can use the same async model client. The main alternative is **RQ** ("Redis Queue"), which is older, very popular and uses ordinary synchronous functions; the tip at the end of this section shows how it compares.

Every job goes through one function, `submit_job`. Deploying Your API, two lessons from now, explains why: the free host there has no worker, so a setting called `INLINE_JOBS` makes `submit_job` run the job inside the API process instead of queuing it. Building it that way from the start means nothing changes when you deploy. Save this as `jobs.py`:

```python
import os

from arq import Retry
from fastapi import BackgroundTasks
from sqlmodel import Session

import llm
from database import engine
from models import Job, utcnow

INLINE_JOBS = os.environ.get("INLINE_JOBS") == "true"
MAX_TRIES = 3                                     # the worker's settings use this too


async def submit_job(job_id: int, background: BackgroundTasks, pool) -> None:
    """Queue a job for the worker, or run it in this process when there's no worker."""
    if INLINE_JOBS:
        background.add_task(process_job, job_id)  # runs right after the response is sent
    else:
        await pool.enqueue_job("run_job", job_id, _job_id=f"job-{job_id}")  # one queue entry per job


async def process_job(job_id: int, *, last_try: bool = True) -> None:
    """Do the work for one job row. Safe to call more than once for the same job."""
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if job is None or job.status == "done":   # idempotency: never redo finished work
            return
        job.status, job.attempts, job.updated_at = "running", job.attempts + 1, utcnow()
        session.commit()                          # clients can now see "running"

        try:
            summary = await llm.summarize(job.input_text)
        except Exception as exc:
            job.error = f"{type(exc).__name__}: {exc}"
            job.status = "failed" if last_try else "pending"  # pending = waiting for a retry
            job.updated_at = utcnow()
            session.commit()
            if not last_try:
                raise                             # tell the worker to try again later
            return

        job.result, job.error, job.status, job.updated_at = summary, None, "done", utcnow()
        session.commit()


async def run_job(ctx, job_id: int) -> None:
    """The worker's entry point. arq passes ctx, which includes the attempt number."""
    try:
        await process_job(job_id, last_try=ctx["job_try"] >= MAX_TRIES)
    except Exception:
        raise Retry(defer=ctx["job_try"] * 10)    # wait 10 s, then 20 s, before trying again
```

`llm.summarize` is your async model call from the summarizer API, moved into its own `llm.py` module. Importing the module (`import llm`) and calling `llm.summarize` rather than importing the function directly lets tests swap it out with `monkeypatch`, as you'll see.

The names are the same ones Deploying Your API uses. **`process_job`** does the real work and doesn't know or care who called it. **`run_job`** is the thin wrapper the worker calls; arq always passes a `ctx` dictionary as the first argument, and `ctx["job_try"]` is the attempt number, starting at 1. Deploying Your API shows `run_job` without the retry logic, to keep that lesson short. This is the full version.

Notice what goes on the queue: only the job's ID. The text, the owner and the status all live in Postgres, where they're safe and queryable. Small messages also mean nothing breaks when you change the `Job` table later.

Now the routes, in `main.py`:

```python
import os
from contextlib import asynccontextmanager
from typing import Annotated, Any

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request

from auth import CurrentUser
from database import SessionDep
from jobs import INLINE_JOBS, submit_job
from models import Job, JobCreate, JobPublic

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # One Redis connection pool for the whole app, opened at startup. None when inline.
    app.state.queue = None if INLINE_JOBS else await create_pool(RedisSettings.from_dsn(REDIS_URL))
    yield
    if app.state.queue is not None:
        await app.state.queue.aclose()


app = FastAPI(title="Summaries", lifespan=lifespan)


def get_queue(request: Request):
    return request.app.state.queue


QueueDep = Annotated[Any, Depends(get_queue)]


@app.post("/jobs", status_code=202, response_model=JobPublic)
async def create_job(
    body: JobCreate, user: CurrentUser, session: SessionDep, queue: QueueDep, background: BackgroundTasks
):
    job = Job(owner_id=user.id, input_text=body.text)
    session.add(job)
    session.commit()                       # commit first, so the worker can find the row
    session.refresh(job)
    await submit_job(job.id, background, queue)
    return job


@app.get("/jobs/{job_id}", response_model=JobPublic)
def read_job(job_id: int, user: CurrentUser, session: SessionDep):
    job = session.get(Job, job_id)
    if job is None or job.owner_id != user.id:  # another user's job looks missing
        raise HTTPException(status_code=404, detail="Job not found")
    return job
```

The order inside `create_job` matters: **commit the row, then enqueue.** Enqueue first, and a fast worker can pick up the ID before the row exists. `create_pool` opens the Redis connection once, at startup, in the `lifespan` function you met in Persisting Data with Postgres, and `get_queue` hands it to routes as a dependency, so tests can replace it. The ownership check is the one from User Accounts and Auth.

<div class="lesson-note lesson-note--tip" markdown="1">

#### The same thing with RQ

With RQ, jobs are plain `def` functions and the queue is a `Queue` object: `queue = Queue(connection=Redis.from_url(REDIS_URL))`, then `queue.enqueue(run_job, job_id, job_id=f"job-{job_id}", retry=Retry(max=2, interval=[10, 30]))`, and you start workers with `rq worker`. RQ retries any exception automatically when you pass `retry`, and a separate package, rq-dashboard, gives you a web page for watching queues. Choose RQ if your job code is synchronous; choose arq if it's async, like the code here. The pattern, and everything else in this lesson, is the same.

</div>

### The worker and retries

The worker is a separate process running the same code as the API. arq finds everything it needs in a settings class. Save this as `worker.py`:

```python
import os

from arq.connections import RedisSettings

from jobs import MAX_TRIES, run_job


class WorkerSettings:
    """Start with: arq worker.WorkerSettings"""

    functions = [run_job]
    redis_settings = RedisSettings.from_dsn(os.environ.get("REDIS_URL", "redis://localhost:6379"))
    max_tries = MAX_TRIES            # arq stops retrying after this many tries
    job_timeout = 120                # seconds; a stuck model call can't hold the worker forever
    max_jobs = 10                    # how many jobs one worker runs at the same time
```

Start Redis and Postgres, then run `uv run arq worker.WorkerSettings` in one terminal and `uv run fastapi dev main.py` in another. Post a job at `/docs` and watch the worker's terminal log it starting and finishing, then fetch it with `GET /jobs/{id}`.

Now look at how retries work. In arq, a job function that raises an ordinary exception **fails for good**. To get another try, it must raise arq's `Retry`, optionally with `defer`, the number of seconds to wait first. `run_job` turns every failure into a `Retry` and waits a little longer each time (10 seconds, then 20), which gives a busy provider room to recover. Waiting longer after each failure is called **backoff**, and Timeouts, Retries and Rate Limits, the next lesson, makes it smarter.

Retries must have a **limit**. Some errors never fix themselves, such as a document the model can't handle or a bug in your code, and a job that retries forever wastes money and hides the problem. Here `max_tries = 3`, and on the third try `run_job` passes `last_try=True`, so `process_job` records `failed` with the error message and returns normally instead of asking for another try. The row in Postgres always ends in `done` or `failed`, and a human can read why.

Two smaller settings protect the worker. `job_timeout` cancels a job that runs too long, so one hung model call can't occupy a slot forever. Give your model client its own, shorter timeout too (the next lesson covers this), so the job's own error handling runs and records the failure. `max_jobs` caps how many jobs run at once in one worker, which is also how you keep under your provider's rate limit. Need more throughput? Start more workers.

### Idempotency

Here's an uncomfortable fact about every job queue: **a job can run more than once.** A worker can crash after calling the model but before marking the job `done`, and the queue will hand the job to another worker. Network hiccups, deploys that restart workers mid-job, and a client that clicks "submit" twice all produce the same effect. Queues promise "at least once", not "exactly once".

So jobs must be **idempotent**: running one twice has the same effect as running it once. The word comes from math, and you've already met the idea. `alembic upgrade head` is idempotent, because running it again finds nothing to do. This job gets there in three ways:

1. **It checks before it works.** `process_job` loads the row and returns straight away if the status is already `done`. A second run finds the result and stops, without a second model call or bill.
1. **The result lives on the job row.** The job overwrites `result` on its own row instead of inserting a new row somewhere else. Even if two runs overlapped, there would still be exactly one result. If your job must insert into another table, put a unique constraint on the job ID there, so the database refuses a duplicate.
1. **The queue entry has a fixed ID.** `_job_id=f"job-{job_id}"` tells arq that this job has a name. While a job with that ID is queued or running, or its result is still stored, `enqueue_job` with the same ID does nothing and returns `None` instead of adding a duplicate.

Notice what the check deliberately allows: a job found in `running` runs again. That's the crashed-worker case, and running it again is the whole point. What idempotency can't undo is a side effect outside your database, such as sending an email or charging a card, which is why such steps either go last, after a check, or use the provider's own idempotency key.

### Adding the worker to Compose

Your `compose.yaml` from Migrations with Alembic has `api`, `migrate` and `db`. Add `redis` and `worker`:

```yaml
services:
  api:
    # ...everything from before, plus:
    environment:
      DATABASE_URL: postgresql+psycopg://mimir:mimir@db:5432/mimir
      REDIS_URL: redis://redis:6379
    depends_on:
      migrate:
        condition: service_completed_successfully
      redis:
        condition: service_healthy

  worker:
    build: .                                   # the same image as the API...
    command: ["arq", "worker.WorkerSettings"]  # ...with a different start command
    env_file: .env                             # the worker calls the model, so it needs the key
    environment:
      DATABASE_URL: postgresql+psycopg://mimir:mimir@db:5432/mimir
      REDIS_URL: redis://redis:6379
    depends_on:
      migrate:
        condition: service_completed_successfully
      redis:
        condition: service_healthy

  redis:
    image: redis:8
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]       # answers PONG when ready
      interval: 2s
      retries: 15

  # migrate and db stay as they were
```

The worker uses the same image as the API, so they always run the same code, and only the `command` differs. It never runs migrations; that stays the job of `migrate`. Redis has no `ports` entry because nothing on your laptop needs to reach it, only the other containers, at the hostname `redis`. Run `docker compose up --build`, post a job, and run `docker compose logs -f worker` to watch it work. Then try `docker compose up --scale worker=3` to start three workers sharing one queue.

Running the worker on a host costs money on most platforms. Deploying Your API shows how to deploy for free by setting `INLINE_JOBS=true`, which runs the same `process_job` inside the API with FastAPI's `BackgroundTasks`, and what you give up by doing so.

### Testing jobs without Redis

You don't need Redis or a running worker to test any of this. Call the job function directly, the way you'd test any other function, and fake the parts that reach outside: the model, the queue and the database. Save this as `test_jobs.py`:

```python
import asyncio
import os

os.environ.setdefault("AUTH_SECRET", "test-secret-at-least-32-bytes-long!!")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import jobs
import llm
from auth import get_current_user
from database import get_session
from main import app, get_queue
from models import Job, User


@pytest.fixture
def engine(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    monkeypatch.setattr(jobs, "engine", engine)   # process_job opens its own sessions
    with Session(engine) as session:
        session.add(User(id=1, email="ada@example.com", hashed_password="x"))
        session.commit()
    return engine


@pytest.fixture
def fake_model(monkeypatch):
    async def fake_summarize(text: str) -> str:
        return "short"

    monkeypatch.setattr(llm, "summarize", fake_summarize)


class FakeQueue:
    def __init__(self):
        self.calls = []

    async def enqueue_job(self, name, *args, **kwargs):
        self.calls.append((name, *args))


def post_job(engine, queue) -> dict:
    """POST /jobs as user 1, with a fake queue. No 'with TestClient', so no Redis."""
    with Session(engine) as session:
        app.dependency_overrides[get_session] = lambda: session
        app.dependency_overrides[get_queue] = lambda: queue
        app.dependency_overrides[get_current_user] = lambda: session.get(User, 1)
        response = TestClient(app).post("/jobs", json={"text": "some long text"})
    app.dependency_overrides.clear()
    assert response.status_code == 202
    return response.json()


def load(engine, job_id: int) -> Job:
    with Session(engine) as session:
        return session.get(Job, job_id)


def test_post_jobs_enqueues_and_returns_202(engine):
    queue = FakeQueue()
    job = post_job(engine, queue)
    assert job["status"] == "pending"
    assert queue.calls == [("run_job", job["id"])]


def test_inline_mode_runs_the_job_in_the_api(engine, fake_model, monkeypatch):
    monkeypatch.setattr(jobs, "INLINE_JOBS", True)
    job = post_job(engine, queue=None)            # the background task runs before this returns
    assert load(engine, job["id"]).status == "done"


def test_process_job_moves_job_to_done(engine, fake_model):
    job_id = post_job(engine, FakeQueue())["id"]
    asyncio.run(jobs.process_job(job_id))         # call the job function directly
    job = load(engine, job_id)
    assert (job.status, job.result, job.attempts) == ("done", "short", 1)

    asyncio.run(jobs.process_job(job_id))         # running it again changes nothing
    assert load(engine, job_id).attempts == 1


def test_failure_retries_then_fails(engine, monkeypatch):
    async def broken(text: str) -> str:
        raise TimeoutError("model took too long")

    monkeypatch.setattr(llm, "summarize", broken)
    job_id = post_job(engine, FakeQueue())["id"]
    with pytest.raises(jobs.Retry):               # try 1 of 3: ask arq to retry
        asyncio.run(jobs.run_job({"job_try": 1}, job_id))
    assert load(engine, job_id).status == "pending"

    asyncio.run(jobs.run_job({"job_try": 3}, job_id))  # the last try: give up and record why
    job = load(engine, job_id)
    assert (job.status, job.attempts) == ("failed", 2)
    assert "model took too long" in job.error
```

Each fake replaces one outside thing. `FakeQueue` has the one method `submit_job` calls, `enqueue_job`, and records what it was given. `monkeypatch` swaps the model call and points `process_job` at the in-memory database. `asyncio.run` runs an async function from a normal test, as in Async Basics. And `run_job` is just a function, so a test hands it a pretend `ctx` with whatever `job_try` it wants to check: the first try asks for a retry, the last one records `failed`. These tests cover enqueueing, the inline path, success, idempotency and limited retries in about a second, which is most of what the LLM-Powered API project asks you to prove.

What they don't cover is arq and Redis themselves. That's fine: those are well-tested libraries. Check the real thing by hand once with `docker compose up`, and trust your tests for your own logic. If you want an automated end-to-end test later, the `fakeredis` package provides an in-memory Redis that most clients can talk to.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through [Redis's data types overview](https://redis.io/docs/latest/develop/data-types/) with `redis-cli` open, so the "it's all just keys" picture is concrete.
   - Read the sections on strings, lists and sorted sets, and try each example command.
1. Read the [arq documentation](https://arq-docs.helpmanual.io/), which is one page, top to bottom. It's short and covers everything in this lesson in more detail.
   - Pay attention to "Retrying jobs and cancellation", "Job Uniqueness" and the `Worker` reference, which lists every setting `WorkerSettings` can hold.
1. Read FastAPI's [Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) page, which is how the inline path runs jobs. Note its own warning that heavy work belongs in a real queue.
1. Skim the [RQ documentation](https://python-rq.org/docs/), especially "Jobs" and "Workers", so you can recognize the other common Python queue.
1. Practice: move your summarizer API's long summaries onto a queue.
   - Add the `Job` table with a migration, `jobs.py`, `worker.py`, and the two routes. Keep `POST /summarize` for short texts, and send texts over 2,000 characters to `POST /jobs`.
   - Add `redis` and `worker` to your `compose.yaml` and run `docker compose up --build`. Submit a job, poll it until it's `done`, and save the `curl` commands and output for your README.
   - Make your fake model fail twice and then succeed, and check that the job ends `done` with `attempts` equal to 3. Then make it always fail and check that it ends `failed` with an error message.
   - Stop the worker with `docker compose stop worker`, submit a job, and watch it stay `pending`. Start the worker again and watch it finish. That's the queue doing its job.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [When should work leave the request, and what status code does the API return when it accepts a job?](#when-work-should-leave-the-request)
- [Why does a job's status and result live in Postgres instead of Redis?](#redis-in-five-minutes)
- [Why must the API commit the job row before it enqueues the job, and why does only the ID go on the queue?](#enqueueing-from-fastapi)
- [How does a job get another try in arq, and why must retries have a limit?](#the-worker-and-retries)
- [Why can a job run more than once, and what three things make this one safe to repeat?](#idempotency)
- [Why do the API and the worker use the same image, and which service runs migrations?](#adding-the-worker-to-compose)
- [How can you test a worker's job function without Redis or a running worker?](#testing-jobs-without-redis)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Brandur Leach's "Implementing Stripe-like Idempotency Keys in Postgres"](https://brandur.org/idempotency-keys) goes deep on making an API, not just a worker, safe to call twice.
- [The fakeredis documentation](https://fakeredis.readthedocs.io/) shows how to run an in-memory Redis in tests when you want an end-to-end test of your queue.
- [Redis's persistence docs](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) explain when Redis writes to disk, and so what a restart can lose.
