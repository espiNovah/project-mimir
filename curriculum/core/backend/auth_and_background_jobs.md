<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Two problems show up the moment an AI API leaves your laptop. First, every request costs you money in model calls, so you cannot let just anyone call it. Second, model calls are slow: a long extraction can take tens of seconds, which is longer than many clients will wait for a response. This lesson covers the standard fixes for both: authentication with API keys, and moving slow work into background jobs that clients can check on.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The difference between authentication and authorization.
- How to protect endpoints with API keys using FastAPI dependencies.
- How to store keys safely.
- Why slow model calls do not belong in the request path.
- The submit, poll, fetch pattern for long-running jobs.
- How FastAPI background tasks work and when you need a real job queue.

### Key ideas

- **Authentication is who you are; authorization is what you may do.** An API key proves identity (authentication). Checking that the key's owner may read a particular record is authorization. Both matter: one user should not be able to fetch another user's results by guessing IDs.
- **API keys are the simplest auth for machine clients.** The client sends a secret in a header, such as `X-API-Key`. A FastAPI dependency reads the header, checks it, and raises `401 Unauthorized` if it is missing or wrong. Attach the dependency to every protected route or to the whole router.
- **Treat keys like passwords.** Generate long random keys (Python's `secrets.token_urlsafe`), never commit them, load them from environment variables, and store only a hash in the database if you issue many. Compare with `secrets.compare_digest` to avoid timing attacks. For user logins in browsers, look at OAuth2 and tokens in the FastAPI security docs.
- **Do not make clients wait on slow work.** Instead of holding the connection open for 40 seconds, accept the job, return `202 Accepted` with a job ID immediately, and do the work in the background. The client then *polls* a status endpoint such as `GET /jobs/{id}` until the status is `done` or `failed`, and fetches the result.
- **Status lives in the database.** Store each job with a status field (`pending`, `running`, `done`, `failed`), timestamps, the result when finished and the error message when not. This also gives you a history of every job for debugging.
- **FastAPI background tasks are a starting point.** `BackgroundTasks` runs a function after the response is sent, in the same process. That is fine for learning and light loads, but jobs are lost if the server restarts. Production systems use a separate worker and queue (such as Celery, RQ, or a cloud queue service); you will revisit this in the Production path.
- **Plan for failure.** Model calls time out and hit rate limits. Catch errors in the job, record them, and mark the job as failed rather than leaving it stuck in `running` forever.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [FastAPI's security introduction](https://fastapi.tiangolo.com/tutorial/security/) to learn the vocabulary (OAuth2, tokens, scopes) and how FastAPI models security as dependencies.
   - Read the intro page and "Security - First Steps." The full OAuth2 password flow is optional for now.
1. Read the [FastAPI dependencies tutorial](https://fastapi.tiangolo.com/tutorial/dependencies/), since API-key checks are written as dependencies.
   - Read the first page and "Dependencies in path operation decorators."
1. Read [FastAPI's background tasks guide](https://fastapi.tiangolo.com/tutorial/background-tasks/), including the caveat about when to use a bigger tool.
1. Practice: add API-key auth to your summarizer API using a key from an environment variable. Then add `POST /jobs` that returns `202` with a job ID immediately and summarizes the text in a background task, and `GET /jobs/{id}` that returns the status and, when done, the result. Write tests for a missing key (`401`), a wrong key (`401`) and a job that moves from `pending` to `done`.

</div>
