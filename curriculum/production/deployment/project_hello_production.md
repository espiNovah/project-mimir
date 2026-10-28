### Introduction

Your LLM-Powered API works, but only you can use it, and only while your laptop is on. In this project you will containerize it and deploy it to a free host so that anyone with the URL can call it. This is a small project with a big payoff: every later project in this path, and your capstone, builds on having a repeatable way to ship.

You will practice writing a Dockerfile, running an app with one command, reading configuration from the environment, keeping secrets out of your code and debugging a deploy you can't touch directly.

### Before you start

- Create a new GitHub repo named `mimir-hello-production`, or keep working in your LLM-Powered API repo on a new branch. Either is fine, as long as the deployed version is on GitHub.
- You need Docker Desktop installed and working (`docker run hello-world` should succeed).
- Create a free account on [Render](https://render.com/docs/free) or [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-overview). Both work; pick one.
- Have your `ANTHROPIC_API_KEY` (or your provider's key) ready to paste into the host's secret settings. Set a low monthly spend limit in your provider's console before anything goes public.

<div class="lesson-note lesson-note--critical" markdown="1">

#### A public URL is a public bill

Once your API is on the internet, anyone who finds it can make it call the model on your key. Keep the API key authentication you added in the LLM-Powered API project, set a spend limit with your provider, and never paste your model key into your repo, Dockerfile or README.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Write a `Dockerfile` and `.dockerignore` for your LLM-Powered API.
   - Use a slim Python 3.12+ base image and install dependencies with `uv`.
   - Copy dependency files before source code so rebuilds use the cache.
   - `.dockerignore` must exclude `.env`, `.venv`, `.git` and caches.
1. Make local startup a single command.
   - `docker compose up` (or one `docker run` line in your README) must start the app with keys loaded from a local `.env` that is listed in `.gitignore`.
   - If your app uses a database, Compose should start it too.
1. Read all configuration from environment variables.
   - At minimum: the model API key, the model name and the port. Your app should exit with a clear error message if the API key is missing.
1. Add a `GET /health` endpoint that returns `200` with a small JSON body (for example `{"status": "ok", "version": "..."}`) without calling the model.
1. Deploy the container to a free host.
   - The app must be reachable at a public HTTPS URL.
   - The model key must be stored only in the host's secret or environment settings.
1. Prove it works with evidence.
   - Add a script or test (for example `scripts/smoke_test.py` or a `pytest` test that takes a base URL) that calls `/health` and one real endpoint on the deployed URL and checks the responses.
   - Run it against your live URL and paste the output into your README.
   - Confirm with `docker history` or `git log` that no secret was ever committed or baked into the image.
1. Push to GitHub with a README that includes the live URL, a one-command local run, step-by-step deploy instructions someone else could follow, the free-tier caveats (such as cold starts) and what you learned.

#### Extra credit

- Use a multi-stage build and report your image size before and after.
- Add a GitHub Actions workflow that builds the image on every push so a broken Dockerfile is caught before deploy.
- Deploy the same image to a second host and note the differences in your README.

</div>

### Submitting your work

A strong submission lets a reviewer go from zero to a working local copy in under five minutes, and see the live version in under one. Lead your README with the live URL and an example `curl` command. Show the smoke test output against the deployed app. Be honest about limitations: if the first request is slow because of a cold start, say so and say why.
