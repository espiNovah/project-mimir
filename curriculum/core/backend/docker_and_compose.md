### Introduction

"It works on my machine" is the oldest excuse in software. The summarizer API you built in FastAPI Basics runs on your laptop because your laptop happens to have the right Python version, the right packages and the right environment variables. A server somewhere else has none of that. Docker solves this by packaging your app together with everything it needs into a single image that runs the same way everywhere. Nearly every hosting platform accepts a Docker image, so learning it once unlocks all of them.

Docker also solves a second problem you're about to have. From the next lesson on, this curriculum stores data in PostgreSQL (usually just called Postgres), a real database server. Installing and configuring Postgres by hand on every laptop is tedious and error-prone. With Docker Compose, one command starts your API *and* a fresh Postgres next to it. That's why this lesson comes before Persisting Data with Postgres.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What images, containers and Dockerfiles are, and how they relate.
- How to write a Dockerfile for a Python app that uses `uv`.
- How layer caching makes rebuilds fast.
- How to keep secrets and junk files out of your image.
- How to run your container locally with environment variables and port mapping.
- How Docker Compose starts an app and its database with one command.

### Images and containers

Three words do most of the work in Docker:

- A **Dockerfile** is a recipe: a text file listing the steps to build your app's environment. Start from a base system, copy in some files, install packages, and say which command starts the app.
- An **image** is the result of following that recipe. It's a frozen, read-only snapshot of a small Linux file system with Python, your packages and your code inside. `docker build` turns a Dockerfile into an image.
- A **container** is a running copy of an image. `docker run` starts one. A container has its own file system, its own network address and its own processes, isolated from your laptop and from other containers.

The relationship is like a class and its objects from Classes and Objects: one image, as many containers as you like. You can start three copies of your API from the same image, and each one starts in exactly the same state.

A container is not a virtual machine. It doesn't boot a whole operating system. It shares your computer's kernel (on a Mac or Windows, Docker Desktop runs one small Linux virtual machine and puts all your containers inside it), so containers start in about a second and use little memory.

Every image starts `FROM` a **base image** that someone else published. Pick a slim, official one such as `python:3.12-slim`. Smaller images build, upload and start faster, and they contain fewer programs that could have security holes. Avoid the full `python:3.12` image (around a gigabyte) unless you need its extra system tools.

### A Dockerfile for a uv app

Here is a complete setup for a FastAPI app with a `pyproject.toml`, a `uv.lock` and a `main.py`, like your summarizer from FastAPI Basics. It has two files: a `Dockerfile` that builds the API image, and a `compose.yaml` that runs it next to Postgres. Put both in your project's root folder.

```dockerfile
# Dockerfile
# (1) Start from a slim, official Python image.
FROM python:3.12-slim

# (2) Copy the uv binary out of uv's own image.
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

# (3) Work inside /app, and tell uv how to behave in an image.
WORKDIR /app
ENV UV_NO_DEV=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1

# (4) Dependency files only, so this slow layer stays cached.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

# (5) Now your code, which changes often.
COPY . .
RUN uv sync --locked

# (6) Use the project's virtual environment. (7) Don't run as root.
ENV PATH="/app/.venv/bin:$PATH"
RUN useradd --create-home app
USER app

# (8) The command every container runs when it starts.
EXPOSE 8000
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
```

Docker reads `#` as a comment only at the start of a line, which is why each comment sits on its own line.

```yaml
# compose.yaml
services:
  api:
    build: .                     # (9) build the Dockerfile in this folder
    ports:
      - "8000:8000"              # laptop port : container port
    env_file: .env               # (10) ANTHROPIC_API_KEY arrives at run time
    environment:
      DATABASE_URL: postgresql+psycopg://mimir:mimir@db:5432/mimir   # (11) "db" is a hostname
    depends_on:
      db:
        condition: service_healthy   # (12) wait until Postgres accepts connections

  db:
    image: postgres:17           # (13) an official image; no Dockerfile needed
    environment:
      POSTGRES_USER: mimir
      POSTGRES_PASSWORD: mimir   # fine for local development only
      POSTGRES_DB: mimir
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data   # (14) data survives container restarts
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mimir -d mimir"]
      interval: 2s
      retries: 15

volumes:
  pgdata:
```

Walking through the numbered lines:

1. The base image gives you Debian Linux with Python 3.12 already installed.
1. `COPY --from=` copies a file out of *another* image. uv publishes a tiny image that contains only its binary, so this is the quickest way to get uv. Pin a version (the same one you use locally) so builds don't change under you.
1. `WORKDIR` creates `/app` and makes it the current folder. The `ENV` lines tell uv to skip dev dependencies such as pytest, to skip keeping a download cache (it would only bloat the image), and to precompile Python files so the app starts faster.
1. Only the two dependency files are copied, and then `uv sync --no-install-project` installs every dependency but not your own code. The next section explains why this split matters.
1. `COPY . .` copies the rest of your project into `/app`, and a second `uv sync` finishes the install. `--locked` makes the build fail if `uv.lock` is out of date, instead of quietly installing different versions than you tested with.
1. uv installed everything into `/app/.venv`. Putting its `bin` folder first on the `PATH` means `fastapi` and `python` refer to the project's environment, with no `uv run` needed.
1. Containers run as the all-powerful `root` user unless you say otherwise. A plain user limits the damage if someone ever breaks into your app.
1. `CMD` is the command a container runs when it starts. `fastapi run` is the production version of the `fastapi dev` command you've been using, without auto-reload. It comes with `fastapi[standard]`, which you installed in FastAPI Basics. Write `CMD` as a JSON list (the *exec form*) so your app receives stop signals directly and shuts down cleanly. `--host 0.0.0.0` is explained in [Running a container](#running-a-container).

The Compose half is covered in [Compose: your app and Postgres together](#compose-your-app-and-postgres-together).

### Layer caching

Each instruction in a Dockerfile produces a **layer**, a saved snapshot of the file system after that step. When you rebuild, Docker walks down the file and reuses every layer whose inputs haven't changed. The moment one step's inputs change, that step and *every step after it* run again.

That's why the order in step 4 matters. Installing dependencies is the slow part, often a minute or more for an AI app. If you wrote `COPY . .` first and then installed, every edit to `main.py` would change the copied files, invalidate the cache, and reinstall every package. By copying only `pyproject.toml` and `uv.lock` first, the expensive layer depends only on those two files. Edit your Python code and rebuild, and Docker prints `CACHED` for the install step and finishes in seconds. Add a package with `uv add`, and the lock file changes, so the install runs again, which is exactly what you want.

The general rule: put the things that change least at the top and the things that change most at the bottom.

### Keeping secrets out

**Never bake secrets into an image.** Anyone who can pull an image can open it and read every file inside, and deleting a file in a later layer doesn't remove it from the earlier one. The classic accident is `COPY . .` sweeping your `.env` file, and your API key with it, into the image.

The defense is a `.dockerignore` file next to your Dockerfile. It works like `.gitignore`: anything listed is never sent to the build at all.

```text
# .dockerignore
.env
.venv
.git
__pycache__/
.pytest_cache/
.ruff_cache/
```

Excluding `.venv` matters too. Your laptop's virtual environment was built for your operating system and would break inside Linux. The image builds its own.

Secrets are passed when the container *starts* instead, as environment variables. Your code already reads `os.environ["ANTHROPIC_API_KEY"]`, as you learned in API Keys and Secrets, so it doesn't care whether the variable came from a `.env` file on your laptop or from Docker.

### Running a container

Build the image and give it a name (a *tag*) with `-t`:

```bash
docker build -t summarizer .
docker run --rm -p 8000:8000 --env-file .env summarizer
```

- `--rm` deletes the container when it stops, so stopped containers don't pile up.
- `--env-file .env` reads your `.env` file on your laptop and sets each line as an environment variable inside the container. The file itself never enters the image. To pass a single variable, use `-e ANTHROPIC_API_KEY` instead, which copies its value from your current shell.
- `-p 8000:8000` *publishes* a port: requests to port 8000 on your laptop are forwarded to port 8000 inside the container. Without it, the container is unreachable from your browser.

Now open `http://localhost:8000/docs`. This is also where `--host 0.0.0.0` from the Dockerfile matters. Inside a container, `localhost` (also written `127.0.0.1`) means "this container only." A server listening on `localhost` inside a container ignores the forwarded traffic, because that traffic arrives on the container's network interface. `0.0.0.0` means "listen on every interface," so forwarded requests get through. If you ever see "connection refused" or an empty reply from a container that looks healthy, check the host first.

To confirm no secret slipped in, list the files in the image: `docker run --rm summarizer ls -a /app`. You should see your code and `.venv`, and no `.env`.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Containers are disposable

Anything a container writes to its own file system disappears when the container is removed. Treat containers like paper cups: replace them freely, and keep anything valuable somewhere else, either in a *volume* (storage Docker manages outside the container) or in a database. That's why the Postgres service below uses a volume.

</div>

### Compose: your app and Postgres together

Real apps are several programs working together: an API, a database, and later a job queue worker. Starting each one with a long `docker run` command and wiring them together by hand gets old fast. **Docker Compose** describes the whole set in one `compose.yaml` file. Each entry under `services` becomes a container. Back to the numbered lines:

9. `build: .` tells Compose to build the `api` image from the Dockerfile in this folder.
9. `env_file` does the same job as `--env-file` above: your key reaches the container at run time.
9. Compose puts every service on a private network where each **service name works as a hostname**. Your API reaches the database at `db:5432`, not `localhost:5432`, because `localhost` inside the API container is the API container itself. The `DATABASE_URL` packs the driver, username, password, host, port and database name into one string. Your app doesn't use it yet. In the next lesson, SQLModel reads it to connect.
9. `depends_on` with `service_healthy` makes Compose wait until the database's health check passes before starting the API. Without it, the API can start first and crash because Postgres is still booting.
9. The `db` service uses the official `postgres` image straight from Docker Hub. Its `POSTGRES_*` variables create a user, a password and an empty database on first start. These throwaway credentials are fine on your laptop; real deployments use a managed database with a strong password, which you'll set up in Deploying Your API.
9. A **named volume**, `pgdata`, holds the database files. Stop and restart everything, and your data is still there.

The `healthcheck` runs `pg_isready`, a small tool inside the Postgres image, every two seconds until it reports that the database accepts connections. The `5432:5432` port mapping on `db` is optional, but it lets tools on your laptop, such as a database GUI, connect at `localhost:5432`.

The everyday commands:

```bash
docker compose up --build        # build the api image, start both services, stream their logs
docker compose exec db psql -U mimir -c "select version();"   # run a command in a running service
docker compose down              # stop and remove the containers (the volume stays)
docker compose down -v           # ...and delete the volume too, for a completely fresh database
```

`docker compose up` is the "one-command local run" every good README promises. Someone who clones your repository needs only Docker and a `.env` file to have your whole system running, with the same Postgres version you used.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Rebuild after you change code

The `api` container runs the code that was copied in when the image was built. After editing `main.py`, run `docker compose up --build` again (it's quick, thanks to layer caching). While actively developing, many people run only `db` in Compose and the API on their laptop with `uv run fastapi dev main.py`, pointing `DATABASE_URL` at `localhost:5432`.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through [Docker's Get started guide](https://docs.docker.com/get-started/) to learn the core vocabulary and install Docker Desktop.
   - Do the "Introduction" and "Docker concepts" parts. You can skip anything about Docker Hub publishing for now.
1. Follow [Docker's Python language guide](https://docs.docker.com/guides/python/), which containerizes a real Python web app step by step.
   - Do the "Containerize your app" and "Develop your app" sections. Notice how it uses Compose to add a database, the same pattern as this lesson.
1. Read [Using uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/), because the rest of this curriculum installs packages with `uv`.
   - Focus on "Installing a project," "Caching" and "Intermediate layers." Compare its examples with the Dockerfile in this lesson.
1. Skim [Docker's building best practices](https://docs.docker.com/build/building/best-practices/) for the rules behind small, fast, safe images.
   - Read the sections on choosing a base image, multi-stage builds, `.dockerignore` and leveraging the build cache.
1. Read [Control startup order in Compose](https://docs.docker.com/compose/how-tos/startup-order/), which explains `depends_on` and health checks in more depth.
1. Practice: containerize the summarizer API from FastAPI Basics.
   - Write a `Dockerfile` and `.dockerignore`, build the image, and run it with your API key passed through `--env-file`. Call `POST /summarize` from `/docs`.
   - Change one line of Python and rebuild. Confirm the dependency install step says `CACHED`.
   - Run `docker run --rm summarizer ls -a /app` and confirm no `.env` file is inside the image.
   - Add the `compose.yaml` from this lesson, run `docker compose up --build`, and connect to the database with `docker compose exec db psql -U mimir`. Run `\l` to list databases, then `\q` to quit. Keep this setup: the next lesson stores your summaries in this database.
   - Add a "Run it locally" section to your README with the two or three commands someone needs.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between an image and a container?](#images-and-containers)
- [Why does the Dockerfile copy pyproject.toml and uv.lock before the rest of the code?](#layer-caching)
- [How do you keep your .env file out of an image, and how does the key reach the app instead?](#keeping-secrets-out)
- [Why must the server listen on 0.0.0.0 inside a container, and what does -p 8000:8000 do?](#running-a-container)
- [Why does the API connect to the database at db:5432 rather than localhost:5432?](#compose-your-app-and-postgres-together)
- [What do depends_on with a health check and a named volume each do in a Compose file?](#compose-your-app-and-postgres-together)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/) explains the FastAPI-specific choices, such as how many workers to run and why the exec form of `CMD` matters.
- [Docker Compose overview](https://docs.docker.com/compose/) is the reference for `compose.yaml` once you need more than one service.
- [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/) explains how service names become hostnames.
- [Compose Watch](https://docs.docker.com/compose/how-tos/file-watch/) syncs code changes into running containers, so you can develop inside Compose without rebuilding by hand.
- The [official Postgres image page](https://hub.docker.com/_/postgres) documents every `POSTGRES_*` variable and how the image initializes a database.
