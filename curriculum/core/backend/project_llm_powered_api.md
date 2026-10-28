### Introduction

In this project you will turn your Messy-Text Extractor into a real web service. Clients will send messy text to an authenticated endpoint and get validated JSON back. Every result will be stored in a database and retrievable by ID, and long documents will be processed as background jobs that clients can poll. This is the shape of a large number of production AI features: a model call wrapped in validation, storage, auth and an API contract.

### Before you start

- Create a new GitHub repository called `mimir-llm-powered-api` as a `uv` project. Add `fastapi[standard]`, `sqlmodel`, `"psycopg[binary]"`, `anthropic` and `pydantic`, plus `pytest` as a dev dependency.
- Bring in your extractor from the Messy-Text Extractor project. You can copy the `extractor/` package, or install your earlier repo as a dependency with `uv add git+https://github.com/<you>/mimir-messy-text-extractor`. Either way, the API should call the same `extract()` function and use the same schema.
- Use Postgres as your database, as in Persisting Data with Postgres. Add a `Dockerfile`, a `.dockerignore` and a `compose.yaml` with an `api` service and a `db` service, as in Docker and Docker Compose, so `docker compose up --build` starts everything. Keep the connection string in a `DATABASE_URL` environment variable (for example `postgresql+psycopg://mimir:mimir@db:5432/mimir`) that your SQLModel engine reads.
- Put your API key settings in environment variables: `ANTHROPIC_API_KEY` for the model and something like `SERVICE_API_KEYS` for the keys your own clients will use.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Fake the model in tests

Your tests should never call a real model. Make the extractor a FastAPI dependency (or pass it in some other way) so tests can swap in a fake that returns a fixed result instantly. Then your test suite is fast, free, and gives the same answer every time.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Create `POST /extractions` that accepts `{"text": "..."}`, runs your extractor and returns `201` with the stored record: an ID, the validated extraction (matching your Pydantic schema), the model name, token counts and a timestamp.
   - Reject empty input or text over a size limit you choose with a `422`.
   - If extraction fails after all retries, store the failure and return a clear error, not a stack trace.
1. Store every extraction in Postgres with SQLModel, including the input text, the parsed result, the raw model output, the status and any error message.
1. Create `GET /extractions/{id}` that returns a stored extraction, and `404` if it does not exist.
1. Protect every endpoint except `/docs` and a `GET /health` endpoint with API-key auth via a request header. Requests with a missing or wrong key must get `401`. Each record should belong to the key that created it, and one key must not be able to read another key's records (return `404` in that case).
1. Add a background job flow for long inputs:
   - `POST /jobs` accepts text, creates a job with status `pending`, returns `202` with the job ID immediately, and runs the extraction in a background task.
   - `GET /jobs/{id}` returns the status (`pending`, `running`, `done` or `failed`) and, when done, the extraction result.
   - A job that errors must end as `failed` with a stored error message.
1. Make sure the OpenAPI docs at `/docs` are useful: every endpoint has a summary, request and response models, and example values.
1. Write tests with FastAPI's `TestClient`, a fake extractor and a throwaway database (an in-memory SQLite database via a dependency override, as in Persisting Data with Postgres), covering at least: a successful extraction, invalid input, a `404`, a missing key, a wrong key, cross-key access, and a job moving from `pending` to `done` and another moving to `failed`. All tests must pass with `uv run pytest`.
1. Push your project to GitHub with a README that explains what it does, how to run it with `docker compose up`, and what you learned.

#### Extra credit

- Add rate limiting per API key, returning `429` when a key exceeds a limit you choose.
- Point your test fixture at a separate Postgres test database instead of in-memory SQLite, and confirm your tests still pass.
- Add a `GET /stats` endpoint that reports, per key, the number of extractions, failure rate and total tokens used, computed with a SQL query.

</div>

### Submitting your work

A strong README includes a short architecture diagram or description (client, API, database, background job, model), copy-pasteable `curl` examples for each endpoint including the auth header, a screenshot of the `/docs` page, and the output of your test run. Explain one design decision you made, such as how you scoped records to keys, and one limitation of using in-process background tasks.
