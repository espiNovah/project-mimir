<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A project that only runs on your laptop is hard to show anyone. In this lesson you will put a container on the internet with a public URL, using a free hosting tier. Along the way you will learn the habits that separate a demo from a deployed service: configuration that comes from the environment, secrets that never touch your repo, and a health check that tells the host your app is alive.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a platform as a service (PaaS) does for you, and what free tiers trade away.
- How to deploy a Dockerized FastAPI app from a GitHub repo.
- Why configuration belongs in environment variables (the Twelve-Factor approach).
- How hosts store secrets, and how your code should read them.
- What a health check endpoint is and why hosts need one.
- How to read deploy logs when something goes wrong.

### Key ideas

- **A PaaS runs your container so you don't manage servers.** Services like Render and Hugging Face Spaces watch your GitHub repo, build your image on every push, run it, give it an HTTPS URL and restart it if it crashes. You trade fine control for not having to patch operating systems.
- **Free tiers have catches you should design around.** For example, Render's free web services spin down after 15 minutes without traffic, so the first request after a quiet period can take close to a minute. Free instances also have limited memory and no persistent disk. Mention cold starts in your README so a reviewer doesn't assume your app is broken.
- **Config lives in the environment, not in code.** The Twelve-Factor rule: anything that changes between your laptop and production (API keys, database URLs, model names, log levels) is read from environment variables. The same image then runs everywhere. `pydantic-settings` can load and validate these into a typed settings object, and fail loudly at startup if one is missing.
- **Secrets go in the host's secret store.** Every host has a dashboard page for environment variables and secrets. Paste your `ANTHROPIC_API_KEY` there, never in your Dockerfile, repo or a committed `.env`. If a key ever lands in Git history, rotate it immediately; deleting the file is not enough.
- **Listen on the port the host gives you.** Many hosts set a `PORT` environment variable. Start your server with that value and bind to `0.0.0.0`.
- **Add a `/health` endpoint.** It should return quickly with `200 OK` and not call the model. The host uses it to decide whether a new deploy is ready and whether a running one has died.
- **Logs are your first debugging tool.** Build logs show failures in `docker build`; runtime logs show crashes and stack traces. Print a clear startup line (version, model name, never the key) so you can confirm what actually deployed.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [The Twelve-Factor App: Config](https://12factor.net/config), a short page that explains why configuration belongs in the environment.
   - Read the whole page. Then skim the rest of the twelve factors from the site's home page; most are now standard practice.
1. Follow [Render's guide to deploying FastAPI](https://render.com/docs/deploy-fastapi) to see a full deploy from a GitHub repo.
   - Note where the start command and environment variables are set. You will deploy your own Docker image instead of the sample app.
1. Read [Render's free instance limits](https://render.com/docs/free) so you know exactly what "free" means.
   - Pay attention to spin-down after inactivity, monthly instance hours and the lack of persistent disk.
1. Read [Render's guide to environment variables and secrets](https://render.com/docs/configure-environment-variables) to learn how hosts store keys outside your code.
1. Read the [Hugging Face Spaces overview](https://huggingface.co/docs/hub/spaces-overview) and the [Docker Spaces guide](https://huggingface.co/docs/hub/spaces-sdks-docker) as a second free option, especially good for demos with a UI.
   - Note how Spaces handles secrets and which port your container must listen on.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) shows how to load environment variables into a validated settings class, so a missing key fails at startup instead of on the first request.
