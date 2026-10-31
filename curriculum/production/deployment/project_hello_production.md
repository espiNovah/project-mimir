### Introduction

Your LLM-Powered API already runs on Render, where one push deploys it straight to users. In this project you'll move it onto a hyperscaler and run it the way a careful team would: on Google Cloud Run, as its own least-privilege identity, with its keys in Secret Manager, a **staging** service where every change lands first, a **production** service that only ever receives an image staging has already run, a release you can test before anyone sees it, and a rollback you've practiced and timed. You'll also make sure it can't surprise you with a bill: budget alerts, a spend cap, and a `teardown.sh` that deletes everything.

This project puts One Real Cloud and Environments and Releases into practice, so keep both open as you work. Everything here is something an employer will expect you to have done before: "I deployed to Cloud Run with separate staging and production, released through a tagged revision, and rolled back in 20 seconds" is a sentence that holds up in an interview. Later projects build on it: Ship It deploys your agent with this same setup.

### Before you start

- Keep working in your `mimir-llm-powered-api` repository on a new branch, or copy it into a new repository named `mimir-hello-production`. Either is fine, as long as the deployed code is on GitHub.
- You need the gcloud CLI installed and logged in, as in One Real Cloud, and a Google Cloud project with billing linked. The Free Trial's credit plus the Free Tier covers this whole project; you shouldn't spend real money. If you already created a project in One Real Cloud, reuse it.
- You need two Postgres databases you can reach from the internet, one for staging and one for production, as in [Connecting to Postgres](#/lessons/production/one-real-cloud). Two free Neon projects work. A free Render database also works but is deleted after 30 days, so use it only for staging. Cloud SQL's 30-day trial instance is extra credit.
- Create **two model API keys**, one for staging and one for production, each with a low monthly spend limit in your provider's console.
- Your API keeps the login and rate limits from the LLM-Powered API. Jobs run inline (`INLINE_JOBS=true`), as in One Real Cloud, so you don't need Redis or a worker in the cloud. Your Compose setup still runs the real worker locally.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Guards first, deploy second

Set up the budget, its alerts and the Cloud Run spend cap *before* your first deploy, not after. Remember what each one does: a budget only sends email, the spend cap pauses Cloud Run, and `--max-instances` stops a flood of requests from starting a fleet of copies. None of them limits your model bill, which is why each environment has its own key with its own spend limit.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### The cloud project

1. Set up the guards from [Setting up without surprise bills](#/lessons/production/one-real-cloud): a budget of $5 a month or less with email alerts at 50%, 90% and 100%, and a Cloud Run spend cap on the project. Deploy only to a free-tier region such as `us-central1`.
1. Enable the Cloud Run, Cloud Build, Artifact Registry and Secret Manager APIs. Create your own Artifact Registry repository named `mimir`, as in Build Once, Deploy Everywhere, with a cleanup policy that keeps only the newest few images so storage stays inside the free 0.5 GB.

#### Identities and secrets

1. Create two dedicated service accounts, `mimir-staging` and `mimir-production`. Neither may use the Compute Engine default service account's permissions, and neither may hold a project-wide role, except `roles/cloudsql.client` if you use Cloud SQL.
1. Store six secrets in Secret Manager, three per environment: `anthropic-api-key-staging`, `database-url-staging` and `auth-secret-staging`, and the same three ending in `-production` (use your provider's name if it isn't Anthropic). Grant `roles/secretmanager.secretAccessor` per secret, so each service account can read only its own environment's three. Delete the unsuffixed secrets from One Real Cloud once you've copied their values, so you stay within the 6 free active versions.
1. Pin every secret version (`anthropic-api-key-production:1`), never `latest`, so each revision records exactly which key it uses.

#### Configuration

1. Add `settings.py` from [Config per environment](#/lessons/production/deploying-to-the-cloud): one pydantic-settings class that reads every setting, with `app_env` limited to `dev`, `staging` and `production`, no default for `database_url`, and the model key as a `SecretStr`. The app must refuse to start, with a `ValidationError` naming the field, when a required setting is missing or misspelled.
1. Commit `deploy/staging.yaml`, `deploy/production.yaml`, `deploy/staging.secrets` and `deploy/production.secrets`. The YAML files hold plain settings, and the `.secrets` files hold secret names and pinned versions only, never values.
1. Make `GET /health` return `{"status": "ok", "database": "ok", "version": ...}`, where `version` is the `APP_VERSION` your release script sets to the commit hash. Return `503` when the database is unreachable, as in Deploying Your API.
1. Log one line at startup with `app_env`, `app_version` and the model name, and never the key.

#### Releasing

1. Write `release.sh` following [A release checklist](#/lessons/production/deploying-to-the-cloud). It must:
   - refuse to release uncommitted changes;
   - build each commit's image once, tagged with the short commit hash, and refuse to deploy to production an image that staging hasn't released;
   - run `alembic upgrade head` as a Cloud Run job, using that environment's service account and database secret;
   - deploy a candidate revision with `--no-traffic --tag candidate`, run your smoke test against the candidate URL, and stop if it fails;
   - in staging, send all traffic to the new revision; in production, send 10% first and print the command that sends the rest.
1. Extend `smoke.py` with the real flow from the LLM-Powered API: `/health` reports the expected commit, register and log in, submit a job and poll it until it's `done`, and a request without a token gets `401`.
1. Create both services once with a plain deploy (the first deploy of a service can't use `--no-traffic`), then release one commit to staging and the same image to production with `release.sh`.
1. Write `RELEASE.md`: your checklist, with the before, staging, production, stop-rule and after steps, and the exact rollback command to fill in before each release.
1. Break it on purpose. Release a commit whose `/health` returns `500` to staging, and show that the smoke test stopped the release before any traffic moved. Then revert the commit.

#### Rolling back and cleaning up

1. Practice a rollback in production. Release a visible change (for example a new field in `/health`), then send all traffic back to the previous revision with `gcloud run services update-traffic`, and time how long it takes until `/health` shows the old version. Then return to the new one with `--to-latest`.
1. Extend One Real Cloud's `teardown.sh` to cover everything this project creates: both services, both migration jobs, the `mimir` and `cloud-run-source-deploy` repositories, all six secrets and both service accounts. Give it an argument, `./teardown.sh staging` or `./teardown.sh all`, and keep it safe to run twice.
1. Prove it works and that your setup is reproducible: run `./teardown.sh staging`, then recreate staging from scratch with your setup steps and `release.sh`, and show the smoke test passing again.
1. Push to GitHub with a README that leads with the production URL and an example `curl`, then explains the architecture (a small diagram or table of the two environments is enough), how to set up the project from nothing, how to release and roll back, what it costs, and what you learned.

#### Evidence

Your README must show:

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. (Linting, Formatting and CI) Tests must never call the model or the cloud, so CI passes with no keys: include a test that a missing `DATABASE_URL` raises a `ValidationError`, a test that `APP_ENV=prod` is rejected, and a test that `/health` reports `APP_VERSION`, using a fake database session as in Testing with pytest.
- Traces from the deployed service. Cloud Run's file system lives in memory and disappears when an instance stops, so a JSONL file inside the container won't survive. Keep the `trace` table in Postgres from the LLM-Powered API (or send each trace as one JSON log line to Cloud Logging), and add `app_env` and `app_version` to every trace. Commit an export of at least 20 production traces with private data removed, and show that each one names the commit that served it.
- An eval score with a confidence interval. Run your `evaluate.py` against the staging candidate URL before you promote a release, and against production after it. Report field accuracy for each with a 95% bootstrap confidence interval and its `n`, as in Eval Statistics, along with the prompt version and the commit from `/health`. The two scores come from the same image, so their intervals should overlap; if they don't, find the configuration difference and explain it.
- The guards: a screenshot of the budget with its three thresholds and of the Cloud Run spend cap, and the `--max-instances` value in `release.sh`.
- The identities: the output of `gcloud projects get-iam-policy` filtered to your two service accounts, showing no project-wide roles, and `gcloud secrets get-iam-policy` for one production secret, showing only `mimir-production`. Show `gcloud secrets list` too (names only; it never prints values).
- One full release: the `release.sh` output for staging and then production, the candidate URL's smoke test passing, and `gcloud run services describe` showing traffic at 10% and then 100%. Name the revisions.
- The stopped release: the failing smoke test output, and the traffic split showing the old revision still at 100%.
- The rollback: the command you ran, the revision names before and after, and the time it took, with a timestamped log or terminal output.
- Teardown: the output of `./teardown.sh staging` and of the recreated staging passing its smoke test. When you finish the project (or after your portfolio review), run `./teardown.sh all`, and add a screenshot of the next day's Billing report showing $0.
- A prompt-injection test run against staging, as in the Agent Loop From Scratch project. The LLM-Powered API has no tools, but it still reads text a user controls: send at least 10 requests that try to override its instructions (for example, to reveal the system prompt or to return a different JSON shape), check what the API *returned*, and report how many succeeded. If you deploy an agent instead, plant the instruction in content the agent reads and check what it *did*.

#### Extra credit

- Run the same image on a server of your own, as in the optional [A Server of Your Own](#/lessons/production/a-server-of-your-own) lesson: Docker Compose with restart policies, Caddy with automatic HTTPS, and ufw. Run `smoke.py` against it, and add a short comparison to your README: cost, cold starts, deploy and rollback steps, and what you had to do yourself.
- Release from GitHub Actions: deploy to staging on every push to `main`, and to production only after a required reviewer approves, using a keyless login with [Google's auth action](https://github.com/google-github-actions/auth) and Workload Identity Federation. Never store a service account key in GitHub.
- Put staging and production in two separate Google Cloud projects, each with its own budget.
- Use Cloud SQL's 30-day trial instance for production, connected through the Unix socket, and note what it would cost after the trial.
- Use a multi-stage Docker build and report the image size and the cold start time before and after.

</div>

### Submitting your work

A strong submission lets a reviewer check three things in a few minutes: that the production URL works (a `curl` they can paste), that the release process is real (the release output, the stopped release and the rollback timing), and that nothing can run up a bill (the budget, the spend cap, the per-secret permissions and the teardown output). Show commands and their actual output rather than describing them. Be honest about limits: if the first request after a quiet spell takes a few seconds because of a cold start, or if your canary at 10% saw only two requests, say so and say why. A reviewer trusts a README that names its rough edges far more than one that claims to have none.
