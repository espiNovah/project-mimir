### Introduction

In this project you will turn your Messy-Text Extractor into a real web service that runs on the internet. Users will sign up, log in, send messy text and get validated JSON back. Every result will be stored in Postgres and retrievable by ID, and long documents will go onto a job queue that a separate worker process handles while clients poll for the result. Model calls will have timeouts and retries, each user will be rate limited, and every call will leave a trace you can evaluate. This is the shape of a large number of production AI features: a model call wrapped in validation, storage, auth, a queue and an API contract.

Everything this project needs comes from the Backend for AI Apps section, so keep those lessons open as you work.

### Before you start

- Create a new GitHub repository called `mimir-llm-powered-api` as a `uv` project. Add `fastapi[standard]`, `sqlmodel`, `"psycopg[binary]"`, `alembic`, `anthropic` and `pydantic`, plus the queue library you used in Job Queues and Workers (`arq` or `rq`, with `redis`) and whatever User Accounts and Auth used for tokens or passwords. Add `pytest` and `ruff` as dev dependencies.
- Bring in your extractor from the Messy-Text Extractor project. You can copy the `extractor/` package, or install your earlier repo as a dependency with `uv add git+https://github.com/<you>/mimir-messy-text-extractor`. Either way, the API and the worker should call the same `extract()` function and use the same schema. Bring your 20 labeled examples too; you'll evaluate against them.
- Add a `Dockerfile`, a `.dockerignore` and a `compose.yaml`, as in Docker and Docker Compose, with four services: `api`, `worker` (the same image with a different command), `db` (Postgres) and `redis`. `docker compose up --build` should start everything.
- Keep all configuration in environment variables: `DATABASE_URL` (for example `postgresql+psycopg://mimir:mimir@db:5432/mimir`), `REDIS_URL`, `ANTHROPIC_API_KEY`, and the secret your auth setup signs tokens with. Commit a `.env.example` with placeholder values, never the real `.env`.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Fake the model in tests

Your tests should never call a real model. Make the extractor a FastAPI dependency (or pass it in some other way) so tests can swap in a fake that returns a fixed result instantly. Do the same for the queue, so a test can check that a job was enqueued without a running Redis. Then your test suite is fast, free, and gives the same answer every time.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Add user accounts, as in User Accounts and Auth. Users can register and log in, and every endpoint except `/docs` and `GET /health` requires a logged-in user. Requests with a missing, invalid or expired token get `401`. Every record belongs to the user who created it, and one user must not be able to read another user's records (return `404` in that case).
1. Create `POST /extractions` that accepts `{"text": "..."}`, runs your extractor and returns `201` with the stored record: an ID, the validated extraction (matching your Pydantic schema), the model name, the prompt version, token counts and a timestamp.
   - Reject empty input or text over a size limit you choose with a `422`.
   - If extraction fails after all retries, store the failure and return a clear error, not a stack trace.
1. Store every extraction in Postgres with SQLModel, including the input text, the parsed result, the raw model output, the status and any error message. Create every table with Alembic migrations, as in Migrations with Alembic, not with `create_all`. Commit the migration files, and include at least one migration that changes an existing table (for example, adding a column), so your history shows the schema evolving.
1. Create `GET /extractions/{id}` that returns a stored extraction, and `404` if it doesn't exist.
1. Move long inputs onto a job queue, as in Job Queues and Workers, using Redis with arq or RQ:
   - `POST /jobs` accepts text, creates a job row with status `pending`, enqueues it, and returns `202` with the job ID immediately. Send every job through one `submit_job` function, as in Deploying Your API, so a setting can switch between the queue and running inline. Locally, with the queue, the API process never runs the extraction itself.
   - The `worker` service picks up the job, sets it to `running`, runs the extraction, and stores the result.
   - `GET /jobs/{id}` returns the status (`pending`, `running`, `done` or `failed`) and, when done, the extraction result.
   - A job that errors is retried a limited number of times, then ends as `failed` with a stored error message.
   - Running the same job twice must not create two results. Make the worker idempotent (safe to repeat), for example by checking the job's status before doing the work.
1. Make model calls resilient, as in Timeouts, Retries and Rate Limits:
   - Every model call has a timeout.
   - Retry timeouts, `429` and `5xx` errors from the model provider with exponential backoff and jitter, up to a cap. Don't retry errors that won't fix themselves, such as a `400`.
   - Rate limit your own API per user, returning `429` with a `Retry-After` header when a user exceeds a limit you choose.
1. Deploy it for free, as in Deploying Your API, to Render's free plan with a free Postgres. Render has no free background workers, so set `INLINE_JOBS=true` on the deployed API: `submit_job` then runs the same job function in the API process instead of queuing it, and you don't deploy Redis. Locally, `docker compose up` still runs the real queue and worker. `GET /health` is public and reports whether the API can reach the database. Run `alembic upgrade head` as part of each deploy.
1. Make sure the OpenAPI docs at `/docs` are useful: every endpoint has a summary, request and response models, and example values.
1. Write tests with FastAPI's `TestClient`, a fake extractor, a fake queue and a throwaway database (an in-memory SQLite database via a dependency override, as in Persisting Data with Postgres), covering at least: a successful extraction, invalid input, a `404`, a missing token, a bad token, cross-user access, a `429` from your rate limiter, a retry that succeeds after a fake `429` from the model, a job being enqueued, a job running inline when `INLINE_JOBS` is on, and the worker function moving one job to `done` and another to `failed`. Call the worker function directly in tests; don't start a real worker.
1. Push your project to GitHub with a README that explains what it does, how to run it with `docker compose up`, the deployed URL, and what you learned.

#### Evidence

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. (Linting, Formatting and CI)
- Traces: every model call, from the API and the worker, writes one trace as in Why Evals Matter, as a JSONL line or a row in a `trace` table. Each trace has a trace ID, the prompt version ID, the model, the input, the output, token counts, latency, and the retry attempt number. Commit a sample of at least 20 traces with any private data removed.
- An eval score: run the text examples from your 20 labeled Messy-Text Extractor examples (the API accepts text, so leave out the image and PDF ones) through the deployed API with an `evaluate.py` script, and report overall field accuracy with a 95% bootstrap confidence interval, as in Eval Statistics. Record the prompt version the score belongs to.
- A transcript against the deployed URL: `curl` to `/health`, registering and logging in, a `POST /jobs` polled until `done`, a request without a token getting `401`, and a burst of requests getting `429`.
- The output of `alembic upgrade head` on an empty database, showing every migration applying in order.

#### Extra credit

- Deploy the real queue: add Render Key Value and a background worker as in the optional part of Deploying Your API, and set `INLINE_JOBS=false`. This costs about $7 a month, because Render has no free worker plan; suspend the worker when you're not demoing it.
- Run `evaluate.py` in GitHub Actions as a manual (`workflow_dispatch`) job, with your API key stored as a [repository secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions), and fail the job if accuracy drops below a threshold.
- Point your test fixture at a separate Postgres test database instead of in-memory SQLite, and build its tables with `alembic upgrade head`, so your tests also exercise your migrations.
- Add a `GET /stats` endpoint that reports, for the logged-in user, the number of extractions, failure rate and total tokens used, computed with a SQL query.

</div>

### Submitting your work

A strong README includes a short architecture diagram or description (client, API, Redis, worker, Postgres, model), copy-pasteable `curl` examples for each endpoint including the auth header, a screenshot of the `/docs` page, the output of your test run, and your eval score with its confidence interval. Explain one design decision you made, such as how you made the worker idempotent or chose your rate limit, and one limitation of your current setup, such as what happens to an inline job if the free instance spins down mid-job, or to queued jobs if Redis restarts.
