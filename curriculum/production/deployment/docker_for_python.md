<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

"It works on my machine" is the oldest excuse in software. Your LLM-Powered API runs on your laptop because your laptop happens to have the right Python version, the right packages and the right environment variables. A server somewhere else has none of that. Docker solves this by packaging your app together with everything it needs into a single image that runs the same way everywhere. Nearly every hosting platform accepts a Docker image, so learning it once unlocks all of them.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What images, containers and Dockerfiles are, and how they relate.
- How to write a Dockerfile for a Python app that uses `uv`.
- How layer caching makes rebuilds fast.
- How to keep secrets and junk files out of your image.
- How to run your container locally with environment variables and port mapping.
- How Docker Compose starts an app and its database with one command.

### Key ideas

- **An image is a recipe's result; a container is a running copy of it.** A `Dockerfile` lists the steps (start from a base image, copy files, install packages, set the start command). `docker build` turns it into an image, and `docker run` starts a container from that image. You can run many containers from one image.
- **Start from a slim, official base image** such as `python:3.12-slim`, or one of the images published by `uv`. Smaller images build, upload and start faster, and they contain fewer things that can have security holes.
- **Order your Dockerfile for caching.** Docker reuses any layer whose inputs have not changed. Copy `pyproject.toml` and `uv.lock` first, install dependencies, and only then copy your source code. Editing a Python file then rebuilds in seconds instead of reinstalling every package.
- **Never bake secrets into an image.** Anyone who can pull the image can read every file in it, including an `.env` file you copied by accident. Add a `.dockerignore` (listing `.env`, `.venv`, `.git`, `__pycache__`) and pass keys at run time with `docker run -e ANTHROPIC_API_KEY` or `--env-file .env`.
- **Bind to `0.0.0.0`, not `localhost`.** Inside a container, `localhost` means "only this container." Start Uvicorn with `--host 0.0.0.0` and publish the port with `-p 8000:8000` so your browser can reach it.
- **Containers are disposable.** Anything written inside a container disappears when it is replaced. Data you want to keep, like a SQLite file, belongs in a volume or, better, a managed database.
- **Compose describes a multi-container app in one file.** A `compose.yaml` can start your API and a Postgres database together with `docker compose up`, which is the "one-command local run" every good README promises.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through [Docker's Get started guide](https://docs.docker.com/get-started/) to learn the core vocabulary and install Docker Desktop.
   - Do the "Introduction" and "Docker concepts" parts. You can skip anything about Docker Hub publishing for now.
1. Follow [Docker's Python language guide](https://docs.docker.com/guides/python/), which containerizes a real Python web app step by step.
   - Do the "Containerize your app" and "Develop your app" sections. Notice how it uses Compose to add a database.
1. Read [Using uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/), because the rest of this curriculum installs packages with `uv`.
   - Focus on "Installing a project," "Caching" and "Intermediate layers." Copy the pattern that installs dependencies before copying your source code.
1. Skim [Docker's building best practices](https://docs.docker.com/build/building/best-practices/) for the rules behind small, fast, safe images.
   - Read the sections on choosing a base image, multi-stage builds, `.dockerignore` and leveraging the build cache.
1. Practice: containerize the FastAPI app from your LLM-Powered API project.
   - Write a `Dockerfile` and `.dockerignore`, build the image, and run it with your API key passed through `--env-file`.
   - Change one line of Python and rebuild. Confirm the dependency layer came from cache.
   - Run `docker history` on your image and confirm no `.env` file is inside it.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/) explains the FastAPI-specific choices, such as how many workers to run and why the exec form of `CMD` matters.
- [Docker Compose overview](https://docs.docker.com/compose/) is the reference for `compose.yaml` once you need more than one service.
