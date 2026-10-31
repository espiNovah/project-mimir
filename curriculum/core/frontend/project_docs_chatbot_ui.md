### Introduction

Your Chat With Your Docs system answers with citations, and your RAG Eval Harness proves how well it works. Now you will give it a face that anyone can use from a link. In this project you will build a web app where people log in, ask questions, watch answers stream in, click a citation to read the source passage, and rate each answer with a thumbs-up or thumbs-down that feeds back into your evals. It will be deployed somewhere public.

The real deliverable is a **TypeScript and React front end** calling a **FastAPI backend** that wraps your Chat With Your Docs package. That's the architecture recommended in Next.js and the AI SDK, because your retrieval, citations, traces and evals are already tested Python code, and the front end's job is to display them well. A Streamlit prototype is an optional first step, not the finished product.

When you finish this project, you have built a working, measured, shareable AI application from the ground up.

### Before you start

- Create a new GitHub repository called `mimir-docs-chatbot-ui` with two folders:
  - `api/`, a `uv` project with `"fastapi[standard]"`, `sqlmodel`, `"psycopg[binary]"`, `alembic`, `anthropic` and the token and password libraries from User Accounts and Auth. Install your Chat With Your Docs project as a dependency (`uv add git+https://github.com/<you>/mimir-chat-with-your-docs`) so the backend calls the same `retrieve`, answer and citation-checking code your evals measure. If that code needs to change, change it in the original repo.
  - `web/`, a React and TypeScript app created with Vite, as in React Essentials. Next.js is also fine; if you choose it, keep the model call and retrieval in FastAPI and let Next.js be the front end (see Choosing Your Architecture in Next.js and the AI SDK).
- Run Postgres with pgvector in Docker Compose, as in Chunking and Vector Databases, so one database holds your chunks, users and feedback. Create the user and feedback tables with Alembic migrations, as in Migrations with Alembic.
- In development, use Vite's proxy so the browser sends `/api/*` to FastAPI without any CORS setup, as in React Essentials.
- Optional prototype: if you haven't already, build the Streamlit app from Prototyping with Streamlit and Gradio over your `retrieve` function. An afternoon with it will show you which citation display and feedback flow you want before you write any React.

<div class="lesson-note lesson-note--critical" markdown="1">

#### A public link spends your money

Anyone who can sign up can make your app call a model on your API key. Before you share the link, set a spending limit in your provider's console, cap the length of questions, and rate limit each user. Never put the API key in front-end code: everything in `web/` ends up in the user's browser.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### The backend

1. Add user accounts, as in User Accounts and Auth: `/register`, `/token` and `/me`, with Argon2 password hashes and JWTs. Every route except `GET /health` and the static front end requires a logged-in user, and a missing, invalid or expired token gets `401`.
1. Create a streaming `POST /api/chat/stream` route with `EventSourceResponse`, as in Streaming in the Browser. It takes the question and the recent conversation, retrieves chunks, calls the model with the async client and sends named events: `token` for each piece of text, `citations` with each cited chunk's ID, source, page, section and text, and exactly one `done` (with the stop reason, token usage and whether the answer was a refusal) or `error` (with a safe message) at the end. Run your `check_answer` from Citations and Grounding on the finished answer and include its result in `done`.
1. Keep the model call inside the generator, so when the browser disconnects the model call stops too. Log when the generator closes. (Streaming in the Browser, Errors and Cancellation)
1. Create `POST /api/feedback`, which stores a thumbs-up or thumbs-down, an optional comment, the question, the answer, the cited chunk IDs, the prompt version, the user's ID and a timestamp in Postgres. Users can only rate their own answers.
1. Protect your money and your server, as in Timeouts, Retries and Rate Limits: a maximum question length (`422` when exceeded), a timeout on every model call, retries with backoff for `429` and `5xx` errors from the provider, and a per-user rate limit that returns `429` with a `Retry-After` header.

#### The front end

1. Build a login and registration screen. Keep the token in React state (memory) and send it as an `Authorization: Bearer` header on every request. When any request returns `401`, send the user back to the login screen. In the README, explain why you didn't put the token in `localStorage`, and what User Accounts and Auth says production apps do instead.
1. Build the chat screen with typed components, as in React Essentials: a message list with stable keys, an input that's disabled while an answer streams, and the conversation history. Write TypeScript types that mirror your Pydantic request and response models and your stream's event payloads, and validate the `citations` and `done` payloads with zod at the boundary. (TypeScript Basics)
1. Stream answers token by token with `fetch` and a stream reader, buffering partial messages as in Streaming in the Browser. Check `res.ok` before reading. Display model output as text, never as raw HTML; if you render Markdown, sanitize it.
1. Add a Stop button that aborts the request with an `AbortController`, keeps the partial answer on screen, and marks it as stopped.
1. Show citations for every answer. Each `[n]` marker or source entry is clickable and reveals the passage text, the document and, for PDFs, the page number. Show "I don't know" answers differently from normal ones, and show a visible warning when `check_answer` found problems.
1. Add thumbs-up and thumbs-down buttons to each finished answer, with an optional comment box, that call `/api/feedback` and show that the rating was saved.
1. Handle errors in the interface: a failed request, an `error` event, a `429` or a network drop shows a readable message next to the answer (with the time to wait, for a `429`), and the rest of the conversation stays intact.

#### Feedback, deployment and tests

1. Write a script that turns thumbs-down feedback into candidate test cases in your RAG Eval Harness's dataset format (ID, question, type, the stable chunk IDs you believe hold the answer, an evidence quote from each, a reference answer), left with blank fields for you to fill in and review by hand, so real use grows your eval set.
1. Deploy for free to Render, as in Deploying Your API: the API as a web service with a free Postgres (enable the `vector` extension there and run ingestion against it). Serve the built `web/dist/` files from FastAPI with `StaticFiles` so the page and the API share an origin, or deploy the front end as a Render static site and add `CORSMiddleware` with its exact origin. Confirm it works from a device other than your own computer.
1. Write backend tests with `TestClient`, fake retrieval and a fake streaming model, as in Testing with pytest and Streaming in the Browser, covering at least: the stream contains `token` events and ends with one `done`, a failing model ends with an `error` event, a missing or bad token gets `401`, an overlong question gets `422`, the rate limiter returns `429`, feedback is stored for the right user, and one user can't rate another's answer.
1. Push your project to GitHub with a README that explains what it does, how to run it locally with `docker compose up` and `npm run dev`, the live link, and what you learned.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Fitting into a free instance

A free Render web service has 512 MB of memory, and an embedding model plus a cross-encoder can use most of it. Check the memory your API uses locally first. If it doesn't fit, add a setting that turns the reranker off in the deployed version, run your RAG Eval Harness with that setting, and report both sets of numbers. Remember that a free Postgres expires after 30 days, so keep your ingestion command handy.

</div>

#### Evidence

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` for `api/`, and `npm ci` and `npm run build` (which type-checks) for `web/`, on every push, and the latest run on `main` passes. Show its status badge at the top of the README. Use [`actions/setup-node`](https://github.com/actions/setup-node) to install Node in the workflow. (Linting, Formatting and CI)
- Traces: every model call from the deployed app writes one trace, as a JSONL line or a row in a `trace` table, with a trace ID, the user ID, the prompt version, the model, the question, the retrieved and cited chunk IDs, the answer, token counts, time to first token and total latency. Commit a sample of at least 20 traces with private data removed.
- An eval score with a confidence interval: run your RAG Eval Harness against the exact configuration you deployed, and report its retrieval and answer metrics with 95% confidence intervals and the prompt version. If the deployed configuration differs from your local one (for example, no reranker), report both.
- A live link at the top of the README, and a short GIF or video showing login, a streamed answer, a citation being opened, the Stop button and a feedback click.
- A transcript against the deployed URL: `GET /health`, a `curl -N` to the stream with a valid token showing the raw events, the same request without a token getting `401`, and a burst of requests getting `429`.
- A sample of the feedback table, and the candidate test cases your script produced from it.

#### Extra credit

- Move the token into a secure, HTTP-only cookie set by the backend, and explain what changes for CSRF.
- Store conversations per user in Postgres, so a user can reload the page and pick up where they left off.
- Show a simple admin page with feedback counts over time and the most recent thumbs-down answers, available only to an admin user (`403` for everyone else).
- Get five people to use your app, add at least five new cases to your eval set from their feedback, rerun your RAG Eval Harness, and report what changed.

</div>

### Submitting your work

A strong submission puts the live link and the GIF at the top of the README. Explain your architecture in a few lines (browser, React app, FastAPI, Postgres with pgvector, model provider) and which events travel over the stream. Report your latest eval numbers with their confidence intervals, and include a sample of the feedback log. If the free host puts the app to sleep when idle, say so, and how long the first load takes. Name one thing you would change before real customers used it, such as how the token is stored or how the per-user limit is set.
