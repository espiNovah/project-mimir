### Introduction

In [One Real Cloud](#/lessons/production/one-real-cloud) you deployed your API to Cloud Run with a single command. That's fine for a demo, but look at what it means for a real product: every change goes straight to the users, tested only on your laptop, and if it breaks, your only fix is to write another change in a hurry. Teams that ship every day without drama aren't more careful typists. They have a **release process**: a safe place to try each change first, a written checklist, a way to give a new version a little traffic before all of it, and a rollback that takes seconds.

This lesson builds that process for your API. You'll run two copies of it, **staging** and **production**, configured from the environment, release the same image to both, use Cloud Run's revisions to test a new version before anyone sees it, and practice rolling back until it's boring. The project that follows, [Hello, Production](#/lessons/production/project-hello-production), asks you to prove your deploy works, and this is how you'll do it with confidence.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an environment is, and what a staging environment catches.
- How to lay out staging and production on Cloud Run, each with its own identity, secrets and database.
- How to keep configuration per environment in one validated settings object.
- Why you build an image once and deploy that same image everywhere.
- How revisions, tags and traffic splitting let you test and roll out gradually.
- How to roll back, and what a rollback doesn't undo.
- How to write a release checklist and a release script.

### Why a staging environment

An **environment** is one complete, running copy of your system: the app, its configuration, its secrets and its data. You already have two. **Development** ("dev") is your laptop running Docker Compose, and **production** ("prod") is the copy real users rely on. A **staging** environment sits between them: a copy that runs in the cloud, set up as much like production as you can manage, where every change lands first.

Staging catches the problems that only appear in the cloud. Your laptop has a `.env` file, a local Postgres, an ARM processor and no service account. The cloud has none of those, so whole classes of bugs never show up locally: a secret the service account can't read, a migration that's slow on real data, an image that builds on your Mac but not in Cloud Build, a missing environment variable, a dependency that behaves differently on Linux. Each of those found in staging is an outage that didn't happen.

The goal is **parity**: staging should differ from production only where it must. Same image, same Cloud Run settings, same Postgres major version, same migration path. The differences should be deliberate and written down, such as a smaller rate limit, a separate database with fake data, and a model API key with a low spend limit. Every difference you didn't intend is a place where staging can pass and production can still fail.

### Two environments on Cloud Run

Big companies usually give each environment its own Google Cloud **project**. That's the strongest separation: separate permissions, separate budgets, and no way for a staging script to touch production by accident. For a learning project, one project holding two services is enough, as long as nothing is shared between them:

| | Staging | Production |
| --- | --- | --- |
| Cloud Run service | `mimir-api-staging` | `mimir-api-production` |
| Service account | `mimir-staging` | `mimir-production` |
| Secrets | `anthropic-api-key-staging` and so on | `anthropic-api-key-production` and so on |
| Database | its own free Postgres, fake data | its own Postgres, real data |
| Model API key | a separate key, low spend limit | a separate key, normal limit |

Separate service accounts with access only to their own secrets mean that a bug in staging can't read production's database password, even by mistake. Separate model keys mean you can revoke one, or watch its spending, without touching the other. Both services scale to zero, so staging costs nothing while you aren't using it, and both fit inside the same free tier. Six secrets with one version each is exactly the 6 free active versions, so delete the three unsuffixed secrets from One Real Cloud once you've copied their values into the new names.

### Config per environment

The Twelve-Factor rule from Deploying Your API still holds: anything that differs between environments comes from environment variables, so one image runs everywhere. What changes now is that you have three environments, and a typo in one of them should fail loudly at startup, not on the first request at 2 a.m. **pydantic-settings** (`uv add pydantic-settings`) reads environment variables into a typed class and validates them:

```python
# settings.py
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Every setting the app reads. Field names match env vars, ignoring case."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  # .env only on your laptop

    app_env: Literal["dev", "staging", "production"] = "dev"
    app_version: str = "dev"            # the Git commit, set by the release script
    database_url: str                   # no default: if it's missing, startup fails
    anthropic_api_key: SecretStr        # SecretStr prints as ********** in logs
    mimir_model: str = "claude-haiku-5-5"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    rate_limit_per_minute: int = 10
    inline_jobs: bool = False           # "true", "1" and "yes" all become True


@lru_cache                              # read the environment once, then reuse the object
def get_settings() -> Settings:
    return Settings()
```

Call `get_settings()` once when the app starts and log `app_env`, `app_version` and `mimir_model` (never the key), so the first log line of every instance says exactly what's running. Try breaking it: unset `DATABASE_URL`, or set `APP_ENV=prod`, and run `uv run python -c "from settings import get_settings; get_settings()"`. You'll get a `ValidationError` that names the bad field. On Cloud Run, an instance that crashes at startup never passes its startup check, so the bad revision never receives traffic.

The non-secret values for each environment live in your repository, one small YAML file each, which `gcloud run deploy --env-vars-file` reads. Secrets don't go in these files; they stay in Secret Manager. Your repository records only their names and pinned versions, which reveal nothing:

```yaml
# deploy/staging.yaml (plain settings; quote every value, Cloud Run wants strings)
APP_ENV: "staging"
LOG_LEVEL: "DEBUG"
RATE_LIMIT_PER_MINUTE: "5"
INLINE_JOBS: "true"
```

```text
# deploy/staging.secrets (secret names and versions, never values)
ANTHROPIC_API_KEY=anthropic-api-key-staging:1,DATABASE_URL=database-url-staging:1,AUTH_SECRET=auth-secret-staging:1
```

`deploy/production.yaml` and `deploy/production.secrets` look the same with production's values. Now a pull request that changes a setting or rotates a key shows up as a diff, and a reviewer can see it.

### Build once, deploy everywhere

In One Real Cloud, `--source .` built a fresh image on every deploy. With two environments that's a trap: if staging and production each build their own image, production runs something staging never tested. A base image could have changed in between, or a dependency could resolve differently. The fix is **build once, deploy many**. You build one image per commit, label it with the commit's short hash (`api:3f9c2ab`), push it to Artifact Registry, and deploy that exact image to staging, then to production. The environment variables are the only things that change.

This needs your own Artifact Registry repository instead of the automatic one:

```bash
gcloud artifacts repositories create mimir --repository-format docker --location us-central1
```

Give it a cleanup policy that keeps the newest few images, so it stays inside the free 0.5 GB. The commit hash also goes into the container as `APP_VERSION`, so `GET /health` reports which commit is live. Point your `/health` route at `get_settings().app_version` instead of `K_REVISION`.

### Revisions and tags

Every deploy to Cloud Run creates a new **revision**: an immutable snapshot of the image *and* its configuration, meaning environment variables, secret versions, service account and limits. Revisions are named like `mimir-api-production-00012-kav`, and old ones stay around, which is what makes rollbacks instant. A service's **traffic** setting says which revisions get what share of requests.

Normally a deploy sends 100% of traffic to the new revision. Two flags change that. `--no-traffic` creates the revision without sending it any requests, and `--tag candidate` gives it its own URL, such as `https://candidate---mimir-api-production-abc123-uc.a.run.app`. Now you can smoke test the exact revision that's about to go live, against production's real configuration and database, while users keep hitting the old one. If the smoke test fails, nobody saw it. You only need to fix it and release again. One catch: the very first deploy of a new service can't use `--no-traffic`, so create each service once with a plain deploy.

### Gradual rollouts

When the candidate passes, you could send it everything. A more careful release is a **canary**: give the new revision a small share first, watch, then give it the rest. The name comes from the canaries miners carried, which got sick before the miners did.

```bash
gcloud run services update-traffic mimir-api-production --to-revisions LATEST=10   # 10% to the new revision
# ...watch the logs and error rate for a while...
gcloud run services update-traffic mimir-api-production --to-latest                # then all of it
```

Cloud Run picks a revision for each request at random by those percentages, and requests already in progress finish where they started. Be honest about what a canary can tell you, though. It needs enough traffic to show a difference: at a few requests an hour, 10% might be zero requests. For a portfolio app, the tag URL test does the real work, and the canary is practice for a job where traffic is real. Deciding which *users* see a change, rather than which random requests, is a different tool, covered in [Feature Flags and A/B Tests](#/lessons/production/feature-flags-and-ab-tests).

One behavior surprises everyone once. After you pin traffic to particular revisions, by splitting or by rolling back, Cloud Run keeps that pattern for every later deploy. New revisions get no traffic until you run `--to-latest` again.

### Rolling back

A **rollback** sends traffic back to a revision that worked. Because that revision still exists, with its image and its configuration, a rollback is one command and takes seconds. Nothing is rebuilt:

```bash
gcloud run revisions list --service mimir-api-production --limit 5        # newest first
gcloud run services update-traffic mimir-api-production \
  --to-revisions mimir-api-production-00011-xog=100                       # the last good one
```

Write that command down before every production release, with the previous revision's real name filled in, so that when something breaks you're running a command, not reading docs. The rule of thumb is **roll back first, debug second**: restore service, then find the bug in staging, where nobody is waiting. Shipping a quick fix instead ("rolling forward") is right only when the fix is tiny and certain.

A rollback restores code and configuration. It doesn't undo anything outside the revision:

- **Database migrations.** If the new release dropped or renamed a column, the old code breaks too. That's why each migration must work with both the old and the new code, for example adding a column in one release and removing the old one in a later release. [Managed Postgres and Backups](#/lessons/production/managed-postgres-and-backups) covers safe migrations properly.
- **Data the new version wrote.** Rows in a new format stay in that format.
- **Secrets you destroyed.** Pinned versions are why the old revision still finds the old key, so don't destroy a secret's previous version until the release is stable.
- **The outside world.** If your model provider retired a model, an older revision won't help.

### A release checklist

Pilots use checklists because memory fails under pressure, and releases are no different. Keep yours in the repository as `RELEASE.md`, and copy it into the description of each release:

1. **Before.** CI is green (ruff and pytest). Migrations are backward compatible. The release notes say what changed, how you'll know it works, and the exact rollback command with the current production revision's name.
1. **Staging.** Release the commit to staging. The smoke test passes on the candidate URL. Try the main flow once by hand, including one real model call.
1. **Production.** Release the same image. The smoke test passes on the candidate URL. Canary at 10%, watch the logs for a few minutes, then send all traffic. `/health` reports the new commit.
1. **Stop rule.** Decide in advance what triggers a rollback, such as a failed smoke test, any 5xx errors in the canary, or `/health` reporting the wrong version, so it's not a judgment call made in a panic.
1. **After.** Note the new revision in your release notes, and clean up old images.

The commands are the same every time, so script them. Migrations now run once per release as a **Cloud Run job**: a container that runs a command to completion instead of serving requests, which is safe however many instances your service has. Take the `alembic upgrade head &&` part back out of your Dockerfile's `CMD` once the job exists.

```bash
#!/usr/bin/env bash
# release.sh: ship the current commit.   Usage: ./release.sh staging   or   ./release.sh production
set -euo pipefail
ENV="${1:?usage: ./release.sh staging|production}"
PROJECT=$(gcloud config get-value project)
REGION=us-central1
SHA=$(git rev-parse --short HEAD)
IMAGE="$REGION-docker.pkg.dev/$PROJECT/mimir/api:$SHA"
SERVICE="mimir-api-$ENV"
SA="mimir-$ENV@$PROJECT.iam.gserviceaccount.com"

# 1. Release only committed code, so the image tag says exactly what ships.
[ -z "$(git status --porcelain)" ] || { echo "Commit your changes first."; exit 1; }

# 2. Build once. Production may only use an image that staging already has.
if ! gcloud artifacts docker images describe "$IMAGE" >/dev/null 2>&1; then
  [ "$ENV" = staging ] || { echo "Release $SHA to staging first."; exit 1; }
  gcloud builds submit --tag "$IMAGE" .
fi

# 3. Migrate this environment's database with the new image, once.
gcloud run jobs deploy "mimir-migrate-$ENV" --image "$IMAGE" --region "$REGION" \
  --service-account "$SA" --set-secrets "DATABASE_URL=database-url-$ENV:1" \
  --command alembic --args upgrade,head
gcloud run jobs execute "mimir-migrate-$ENV" --region "$REGION" --wait

# 4. Deploy a candidate revision with no traffic, at its own tagged URL.
ENV_FILE=$(mktemp)
{ cat "deploy/$ENV.yaml"; echo "APP_VERSION: \"$SHA\""; } > "$ENV_FILE"
gcloud run deploy "$SERVICE" --image "$IMAGE" --region "$REGION" --port 8000 \
  --service-account "$SA" --env-vars-file "$ENV_FILE" \
  --set-secrets "$(grep -v '^#' "deploy/$ENV.secrets")" \
  --max-instances 2 --no-traffic --tag candidate
CANDIDATE=$(gcloud run services describe "$SERVICE" --region "$REGION" --format json | python3 -c \
  "import json,sys; print(next(t['url'] for t in json.load(sys.stdin)['status']['traffic'] if t.get('tag') == 'candidate'))")

# 5. Smoke test the candidate. If it fails, set -e stops here and users never see it.
uv run python smoke.py "$CANDIDATE"

# 6. Shift traffic: all of it in staging, a 10% canary in production.
if [ "$ENV" = staging ]; then
  gcloud run services update-traffic "$SERVICE" --region "$REGION" --to-latest
else
  gcloud run services update-traffic "$SERVICE" --region "$REGION" --to-revisions LATEST=10
  echo "Canary at 10%. When it looks healthy: gcloud run services update-traffic $SERVICE --region $REGION --to-latest"
fi
```

The migration job reads only `DATABASE_URL`, so `database.py` must still get it straight from the environment rather than through the full settings object. The job's service account is the environment's own, so staging's job can't reach production's database. Later you can run this from GitHub Actions, deploying to staging on every push to `main` and to production only after someone approves. That needs a keyless login from GitHub to Google Cloud, linked in Additional resources.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [The Twelve-Factor App: Config](https://12factor.net/config), a short page on why configuration belongs in the environment. Then read the [Dev/prod parity](https://12factor.net/dev-prod-parity) factor, which is this lesson's argument for staging in a few paragraphs.
1. Read the [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) up to and including "Parsing environment variable values", to see how a settings class reads and validates the environment.
1. Read Google Cloud's [Rollbacks, gradual rollouts, and traffic migration](https://cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration), the reference for every traffic command in this lesson, including tags.
1. Read the [Release Engineering chapter](https://sre.google/sre-book/release-engineering/) of Google's free *Site Reliability Engineering* book, for how a large company thinks about repeatable, hermetic releases.
   - Focus on "Philosophy" and "Continuous Build and Deployment". Skim the rest.
1. Practice: add staging and a release process to your API.
   - Add `settings.py` and the `deploy/` files. Show that a missing `DATABASE_URL` stops the app at startup with a clear error.
   - Create the staging and production service accounts, secrets and databases. Release one commit to staging, then the same image to production with `release.sh`, and check that `/health` reports the same commit in both.
   - Break it on purpose: release a commit whose `/health` returns 500. Watch the smoke test stop the release before any traffic moves.
   - Practice a rollback: release a visible change (for example, a new field in `/health`) to production, roll back to the previous revision with `update-traffic`, time how long it takes, then resume with `--to-latest`.
   - Write `RELEASE.md` with your checklist and stop rule, and add the rollback timing to your README.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What kinds of bugs does a staging environment catch that your laptop can't, and what does parity mean?](#why-a-staging-environment)
- [Why give staging and production separate service accounts, secrets and model keys?](#two-environments-on-cloud-run)
- [Why should a missing or misspelled setting crash the app at startup, and where do secret names and versions live?](#config-per-environment)
- [Why build an image once and deploy that same image to every environment?](#build-once-deploy-everywhere)
- [What is a revision, and how do no-traffic and a tag let you test a release before users see it?](#revisions-and-tags)
- [What can a canary tell you, and why might it tell you little on a low-traffic app?](#gradual-rollouts)
- [How do you roll back on Cloud Run, and what does a rollback not undo?](#rolling-back)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Martin Fowler's note on canary releases](https://martinfowler.com/bliki/CanaryRelease.html) is a short description of the pattern, with its trade-offs.
- [Execute jobs](https://cloud.google.com/run/docs/execute/jobs) covers Cloud Run jobs, which this lesson uses for migrations.
- [Artifact Registry cleanup policies](https://cloud.google.com/artifact-registry/docs/repositories/cleanup-policy) shows how to keep only your newest images, so storage stays free.
- [GitHub's guide to deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments) explains required reviewers, so production deploys from Actions wait for a human.
- [Google's auth action for GitHub](https://github.com/google-github-actions/auth) logs a GitHub Actions workflow into Google Cloud with Workload Identity Federation, so you never store a long-lived key in GitHub.
