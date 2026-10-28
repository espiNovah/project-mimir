### Introduction

So far your API has only run on your laptop, where `localhost:8000` is reachable by exactly one person: you. **Deploying** means running it on a computer that's always on and reachable from the internet, with its own database, so anyone with the URL can use it. A deployed project is worth far more in a portfolio than a repository, because a reviewer can try it in ten seconds.

You already have most of what a deploy needs. Docker and Docker Compose packaged your app into an image, Persisting Data with Postgres moved your data into Postgres, Migrations with Alembic made the schema reproducible, and Job Queues and Workers split slow work into a separate worker process that talks to Redis. In this lesson you'll put that whole stack (API, worker, Postgres and Redis) on **Render**, a hosting platform that builds your Dockerfile, runs it and manages the database for you. You'll configure it with environment variables, run migrations on every release, add a health check, read logs, and prove it works with a smoke test.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a managed platform does for you, and what Render and Fly.io honestly cost.
- How to get an app ready for production: configuration, the port and a real health check.
- How to describe the API, worker, Postgres and Redis in one `render.yaml` file.
- How to handle environment variables and secrets on a host.
- How to run `alembic upgrade head` on every release.
- How to read logs and smoke test a deployment.
- What to check first when a deploy fails.

### What a managed platform does

You could rent a bare Linux server and install everything on it yourself, and the optional lesson [A Server of Your Own](#/lessons/production/a-server-of-your-own) shows how. A **managed platform** (sometimes called a PaaS, "platform as a service") does that work for you. You connect a GitHub repository, and on every push the platform builds your image, starts it, gives it an HTTPS address such as `https://mimir-api.onrender.com`, restarts it if it crashes and keeps its logs. A **managed database** is the same idea for Postgres: the platform installs, runs and patches it, and hands you a connection URL.

Each part of your Compose file becomes one piece on the platform:

| In `compose.yaml` | On Render | Reachable from |
| --- | --- | --- |
| `api` | a web service | the internet, over HTTPS |
| `worker` | a background worker | nowhere; it only makes outgoing connections |
| `db` | Render Postgres | your other services, over Render's private network |
| `redis` | Render Key Value (Redis-compatible) | your other services, over the private network |

The **private network** connects services in the same Render account and region. Your database and Redis don't need to be on the public internet at all, which is safer.

### What it costs

Prices change often, so check the links in the Assignment before you sign up. As of October 2026:

- **Render** has a free plan for web services, Postgres and Key Value, with real limits. A free web service **spins down** (goes to sleep) after 15 minutes without traffic and takes about a minute to wake up on the next request. A free Postgres database holds 1 GB, has no backups, and **expires 30 days after you create it**, with a 14-day grace period to upgrade before it's deleted. A free Key Value instance keeps its data in memory only, so a restart erases queued jobs. **Background workers have no free plan**: the cheapest is $7 a month. The cheapest always-on web service is also $7, and the cheapest Postgres that doesn't expire is $6 a month.
- **Fly.io** has no free plan for new accounts, only a short trial. Small machines are cheap, about $2 a month for the smallest that runs all the time, but its managed Postgres starts at $38 a month.

This lesson uses Render, because it can run your whole stack for **about $7 a month** (a paid worker, everything else free) and the setup is the gentlest. Render bills paid services by the second, so if you run the worker only while you build and demo the project and then suspend it, you pay a fraction of that. To keep the database past 30 days, upgrade it to the $6 plan, which brings the total to about $13 a month. The tip at the end of [Running migrations on release](#running-migrations-on-release) covers Fly.

<div class="lesson-note lesson-note--warning" markdown="1">

#### A public URL can spend your money

Once your API is on the internet, anyone who finds it can call it, and every model call costs you. Deploy only with the login from User Accounts and Auth and the rate limits from Timeouts, Retries and Rate Limits switched on. Set a monthly spend limit in your model provider's console as well, so a mistake can't cost more than you planned.

</div>

### Getting the app ready

Three small changes make the app happy on a host. First, **all configuration comes from environment variables**. You've done this since API Keys and Secrets, and it pays off now: the same image runs on your laptop and on Render, and only the variables differ. There's one wrinkle. Render (like most hosts) hands out database URLs that start with `postgresql://`, without naming a driver. Recent SQLAlchemy versions assume psycopg for those, but older ones don't, so make `database.py` spell it out:

```python
# database.py
import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://mimir:mimir@localhost:5432/mimir"
)
# Hosts hand out URLs that start with postgresql:// (or the older postgres://).
# Spell out the driver so SQLAlchemy always uses psycopg, whatever its version.
for prefix in ("postgres://", "postgresql://"):
    if DATABASE_URL.startswith(prefix):
        DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL.removeprefix(prefix)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)  # test connections before use


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
```

`pool_pre_ping=True` makes the engine check that a pooled connection is still alive before handing it out. Managed databases restart for maintenance now and then, and without it your app would fail on the first request after each restart. Alembic's `env.py` imports this same `DATABASE_URL`, so migrations get the fixed URL too.

Second, **the port**. Render sends traffic to the port in the `PORT` environment variable, which defaults to 10000. Your Dockerfile's `CMD` listens on 8000, so you'll set `PORT` to `8000` in the next section. The `--host 0.0.0.0` from Docker and Docker Compose is required here too.

Third, **a health check that means something.** The `/health` route from FastAPI Basics returns `ok` as long as Python is running. A better one also checks the thing your app can't work without, the database:

```python
# main.py (add to your app)
import logging
import os

from fastapi.responses import JSONResponse
from sqlmodel import text

from database import SessionDep

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("api")


@app.get("/health")
def health(session: SessionDep):
    """Public. Says whether this process is up and can reach the database."""
    try:
        session.exec(text("SELECT 1"))
    except Exception:
        logger.exception("health check: database unreachable")
        return JSONResponse({"status": "error", "database": "unreachable"}, status_code=503)
    commit = os.environ.get("RENDER_GIT_COMMIT", "dev")[:7]  # which version is running
    return {"status": "ok", "database": "ok", "version": commit}
```

`SELECT 1` is the cheapest query there is; it only proves the connection works. On failure the route returns `503 Service Unavailable`, so the platform (and you) can tell something is wrong. Render sets `RENDER_GIT_COMMIT` to the Git commit it deployed, so `/health` also tells you which version is live. Keep `/health` public and fast, and never put secrets or user data in it. The logging setup is the one from Debugging and Logging: platforms collect whatever your app writes to standard output and standard error, so log there, not to a file.

### Describing the stack in render yaml

You could click each service together in Render's dashboard, but then your setup lives only in your memory. A **Blueprint** is a `render.yaml` file in your repository's root that describes every service, the same way `compose.yaml` does locally. This one matches the four services in the LLM-Powered API project:

```yaml
# render.yaml
databases:
  - name: mimir-db
    plan: free                     # $0, 1 GB, expires after 30 days; 0.1c-256mb is about $6/month
    databaseName: mimir
    user: mimir
    postgresMajorVersion: "17"     # match the postgres:17 you use in Compose

services:
  - type: keyvalue                 # Redis-compatible
    name: mimir-redis
    plan: free                     # $0, 25 MB, in memory only
    ipAllowList: []                # no connections from outside Render

  - type: web
    name: mimir-api
    runtime: docker                # build the Dockerfile in the repo root
    plan: free
    healthCheckPath: /health
    dockerCommand: /bin/sh -c "alembic upgrade head && exec fastapi run main.py --host 0.0.0.0 --port 8000"
    envVars:
      - key: PORT
        value: "8000"
      - key: DATABASE_URL
        fromDatabase:
          name: mimir-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: keyvalue
          name: mimir-redis
          property: connectionString
      - key: ANTHROPIC_API_KEY
        sync: false                # Render asks you for the value; it never goes in Git
      - key: AUTH_SECRET
        generateValue: true        # Render generates a long random value once

  - type: worker
    name: mimir-worker
    runtime: docker                # the same image as the API...
    plan: 0.5c-512mb               # ...on the cheapest worker plan, about $7/month (no free plan)
    dockerCommand: arq worker.WorkerSettings   # your worker command from Job Queues and Workers
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: mimir-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: keyvalue
          name: mimir-redis
          property: connectionString
      - key: ANTHROPIC_API_KEY
        sync: false
```

The pieces worth slowing down for:

- **`runtime: docker`** makes Render build your existing Dockerfile. Both services build the same image, just as `api` and `worker` share one in your Compose file, and **`dockerCommand`** replaces the image's `CMD` with a different start command. If you use RQ instead of arq, the worker's command is your `rq worker` line instead.
- **`fromDatabase` and `fromService`** fill in connection URLs for you. They're private-network URLs, so they only work from inside Render. `ipAllowList: []` keeps Redis completely off the internet.
- **`healthCheckPath`** tells Render to call `/health` repeatedly. A new version gets no traffic until its health check passes, and a running instance that keeps failing it is restarted. Workers have no health check path, since they don't serve HTTP.
- The service names (`mimir-api` and so on) must be unused in your Render account. The API's name also becomes its URL, `https://mimir-api.onrender.com` unless someone already took it.

### Environment variables and secrets

Every value in `envVars` reaches your container as an environment variable, exactly like `env_file` in Compose. Three kinds appear above:

- **Plain values** such as `PORT` are fine to commit, because they aren't secret.
- **References** (`fromDatabase`, `fromService`) contain passwords, but Render fills them in itself, so the passwords never appear in your repository.
- **Secrets you own** use `sync: false`. When you first create the Blueprint, Render asks you to paste each value, and stores it encrypted. Later pushes don't touch it. To change one, edit it on the service's **Environment** page in the dashboard, which restarts the service with the new value. `generateValue: true` is for secrets nobody needs to type, such as the key your auth code signs tokens with.

The rules from API Keys and Secrets still hold: no secret in Git, in your image or in a log line. Keep a `.env.example` with placeholder values so others know which variables exist. If a key ever leaks, revoke it in the provider's console and create a new one; deleting the commit is not enough.

### Running migrations on release

New code often expects a new schema, so `alembic upgrade head` has to run **before** the new version starts serving, and exactly once. The `render.yaml` above does that in the free way. The API's `dockerCommand` runs the migrations and then, only if they succeed (that's what `&&` means), replaces the shell with the web server (that's `exec`, which lets stop signals reach the server directly). Running migrations on every start is safe because Alembic skips everything that's already applied, so waking from sleep costs a fraction of a second. If a migration fails, the server never starts, the health check never passes, and Render keeps the previous version running.

That approach has one limit, which Migrations with Alembic warned about: it's only safe while one copy of the API runs. Once you run several copies, or pay for any web service, use Render's **pre-deploy command** instead. It runs once per deploy, after the build and before the new version starts, and a failure cancels the deploy. It's available only on paid services, so it costs $7 a month for the web service. Swap the `dockerCommand` line for this one:

```yaml
    preDeployCommand: alembic upgrade head   # paid plans only; then the Dockerfile's CMD starts the app
```

Whichever you use, the worker never migrates. It's always the API's job, so two processes never race to change the schema.

<div class="lesson-note lesson-note--tip" markdown="1">

#### The same ideas on Fly.io

On Fly you describe the app in `fly.toml` and deploy with the `fly` command-line tool. Migrations go in `release_command` under `[deploy]`, which runs once on a temporary machine before each release. A worker is a second entry under `[processes]` that runs from the same image. Postgres comes from Fly's Managed Postgres, and Redis from Upstash through Fly. The steps differ, but the shape doesn't: one image, two start commands, two managed data stores, migrations before release, and secrets set with `fly secrets set`.

</div>

### Deploying and reading logs

With `render.yaml` committed and pushed to GitHub:

1. Create a free Render account and connect your GitHub account.
1. In the dashboard, choose **New**, then **Blueprint**, and pick your repository. Render reads `render.yaml` and lists every service it will create, with its plan.
1. Paste a value for each `sync: false` variable, then approve. Render creates the database and Redis, builds your image, and starts the API and the worker. The worker's plan needs a payment method on file.
1. Open the `mimir-api` service. Its **Events** page shows each deploy, and its **Logs** page shows build output, then your migration output (`Running upgrade ... -> ...`), then the server starting.

From now on, every push to your main branch deploys automatically. The **Logs** page streams what each service writes, and you can search it, so this is where you look first when anything misbehaves. Check the worker's logs too: a job stuck at `pending` almost always means the worker crashed or can't reach Redis, and its logs say why. Python can hold back `print` output in a buffer when it isn't writing to a terminal, so prefer `logging`, which writes to standard error straight away, or set `PYTHONUNBUFFERED=1`.

### Smoke testing the deployment

A **smoke test** is a quick check, run right after a deploy, that the most basic things work. If it fails, there's no point testing anything else. (The name comes from hardware: switch it on and see whether it smokes.) Save this as `smoke.py`:

```python
"""Smoke test a running deployment: uv run python smoke.py https://your-app.onrender.com"""

import sys
import time

import httpx

base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
failures = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global failures
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    failures += not ok


# A free instance may be asleep, so allow up to a minute and a half for the first request.
with httpx.Client(base_url=base_url, timeout=90) as client:
    start = time.perf_counter()
    r = client.get("/health")
    check("GET /health is 200", r.status_code == 200, f"{r.status_code} in {time.perf_counter() - start:.1f}s")
    check("database is reachable", r.json().get("database") == "ok", r.text)

    r = client.get("/docs")
    check("GET /docs is 200", r.status_code == 200)

    r = client.get("/this-route-does-not-exist")
    check("unknown route is 404", r.status_code == 404)

print("all checks passed" if failures == 0 else f"{failures} check(s) failed")
sys.exit(1 if failures else 0)
```

`httpx` came with `fastapi[standard]`. Run it against your laptop first (`uv run python smoke.py`), then against the real URL. The script exits with code 1 when anything fails, so a later CI job can run it after each deploy and go red. For the project, extend it with the real flow: register, log in, submit a job, poll until it's `done`, and check that a request without a token gets `401`.

### When a deploy fails

Most first deploys fail at least once. Read the logs from the top, and check these first:

- **"No open ports detected" or a timed-out deploy.** The server isn't listening on `0.0.0.0` and the `PORT` Render expects.
- **`ModuleNotFoundError: No module named 'psycopg2'`.** The `postgresql://` URL wasn't rewritten to use psycopg. Check `database.py`.
- **`connection refused` or `could not translate host name`.** A service is using the database's internal URL from another region, or an old URL you pasted by hand. Use `fromDatabase` so it's always correct.
- **A migration error.** Fix the migration, test it locally on a fresh database with `uv run alembic upgrade head`, and push again. The old version keeps serving in the meantime.
- **The first request takes a minute.** That's a free service waking up, not a bug.

### Where this goes next

This is a beginner's deploy on purpose: one platform, one region, one environment. The Production path goes much further. [One Real Cloud](#/lessons/production/one-real-cloud) deploys to a major cloud with proper permissions and a secrets manager, [Environments and Releases](#/lessons/production/deploying-to-the-cloud) adds a staging copy and rollbacks, [Managed Postgres and Backups](#/lessons/production/managed-postgres-and-backups) covers backups and restoring them, and [Logging and Tracing](#/lessons/production/logging-and-tracing) makes your logs searchable across services. Everything you set up here (an image, environment configuration, migrations on release and a health check) carries straight over.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Render's free instances page](https://render.com/docs/free) and skim [Render's pricing](https://render.com/pricing) before you create anything, so you know exactly what's free, what expires and what each piece costs today.
1. Read Render's [Blueprint YAML reference](https://render.com/docs/blueprint-spec), which documents every field in this lesson's `render.yaml`.
   - Read the sections on services, environment variables, databases and Key Value. Skip the parts about previews and projects.
1. Read Render's guides on [pre-deploy commands](https://render.com/docs/deploys#pre-deploy-command), [health checks](https://render.com/docs/health-checks) and [background workers](https://render.com/docs/background-workers), to see how releases, health checks and workers behave in detail.
1. Read [FastAPI's deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/), which explains, provider-neutrally, what every deploy has to handle: HTTPS, running on startup, restarts, replication and steps before starting, such as migrations.
1. Practice: deploy your summarizer API.
   - Add the `database.py` changes and the `/health` route from this lesson, and confirm `smoke.py` passes against `docker compose up`.
   - Write a `render.yaml` with the API, a free Postgres and migrations on start, and deploy it as a Blueprint. Leave out the worker and Redis for now if your API doesn't use them yet; the LLM-Powered API project adds them.
   - Run `smoke.py` against your public URL and save the output. Add the URL and the output to your README.
   - Break it on purpose: push a migration with a typo in its SQL. Watch the deploy fail in the logs, confirm the old version is still serving, then fix it and redeploy.
   - Put a reminder in your calendar for day 25, to upgrade or delete the free database before it expires.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How does each service in your Compose file map onto a managed platform, and why are Postgres and Redis kept on the private network?](#what-a-managed-platform-does)
- [Which parts of this stack are free on Render, what are their limits, and which part always costs money?](#what-it-costs)
- [Why does database.py rewrite the URL, and what does pool_pre_ping protect you from?](#getting-the-app-ready)
- [What should a good health check test, and what status code should it return when that test fails?](#getting-the-app-ready)
- [What is the difference between sync false, generateValue and fromDatabase in render.yaml?](#environment-variables-and-secrets)
- [Why must migrations run before the new version serves traffic, and when should you use a pre-deploy command instead of running them at startup?](#running-migrations-on-release)
- [What is a smoke test, and why does smoke.py exit with a nonzero code on failure?](#smoke-testing-the-deployment)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Render's FastAPI guide](https://render.com/docs/deploy-fastapi) deploys a minimal FastAPI app without Docker, a useful comparison if your Docker build gives you trouble.
- [Render's Key Value docs](https://render.com/docs/key-value) explain connecting to Redis, persistence, and what happens on the free plan.
- [Fly.io's pricing page](https://docs.fly.io/about/pricing) and [Fly's Python docs](https://fly.io/docs/python/) are the place to start if you'd rather deploy to Fly.
- [The Twelve-Factor App](https://12factor.net/) is a short, classic description of how to build apps that deploy cleanly. Its "Config", "Backing services", "Logs" and "Admin processes" sections match this lesson.
