### Introduction

In [Deploying Your API](#/lessons/core/deploying-your-api) you put your API and its database on Render. That was the right first step: one dashboard, one `render.yaml`, and a public URL in an afternoon. Most companies that hire AI engineers, though, run on one of the three big clouds: Amazon Web Services (AWS), Google Cloud or Microsoft Azure. People call these **hyperscalers**, because they run data centers at a scale that lets them offer hundreds of services, from plain virtual machines to managed AI models. Job postings say "experience with AWS or GCP" far more often than they name any smaller host.

In this lesson you'll deploy the same container to **Google Cloud Run**, Google Cloud's service for running containers. You'll give it its own identity with **IAM**, keep its keys in **Secret Manager**, connect it to Postgres, and read its logs. Just as important, you'll learn to do all of this inside Google Cloud's free tier, with a budget, an alert, a spend cap and a teardown script, so a mistake can't turn into a surprise bill.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why a hyperscaler is worth learning after a simple platform, and how Cloud Run compares to Render.
- How to set up a Google Cloud project that stays inside the free tier, with a budget, alerts and a spend cap.
- What IAM is: principals, roles and service accounts, and why your app gets its own.
- How to store secrets in Secret Manager and hand them to Cloud Run.
- How to deploy a container to Cloud Run from your repository and read its logs.
- The basics of connecting Cloud Run to Postgres.
- How to shut everything down so nothing keeps billing you.

### Why a hyperscaler

Render made choices for you. It decided where your app runs, who can change it, how secrets are stored and how services talk to each other. On a hyperscaler you make those choices yourself, and that's exactly the skill employers are paying for. Three ideas show up on every big cloud, under different names:

- **Identity and access management (IAM).** Every person and every program has an identity, and every action, such as "read this secret" or "deploy this service", needs a permission. On Render, anyone with your dashboard login could do anything. On a hyperscaler, your app runs as an identity that can do only what you allowed.
- **Building blocks instead of a bundle.** Render's web service included the build, the image storage, the logs and the secrets page. On Google Cloud those are separate services (Cloud Build, Artifact Registry, Cloud Logging, Secret Manager) that you connect. More pieces, but each one is more capable, and you can swap any of them.
- **Usage-based billing.** You pay per second of compute, per request and per gigabyte stored. That's why a small app can cost nothing, and also why a mistake can cost something. Watching cost is part of the job.

We use **Cloud Run** because it's the gentlest way into a hyperscaler. It runs any container that listens for HTTP on a port, so your existing Dockerfile works unchanged. It **scales to zero**: when nobody is calling your API, no instance runs and you pay nothing, then it starts one when a request arrives. And its free tier covers a portfolio project comfortably. AWS and Azure have close equivalents, covered in a tip at the end, and once you've learned one, the others are mostly new names for familiar ideas.

Here's how the pieces you know from Render map onto Google Cloud:

| On Render | On Google Cloud |
| --- | --- |
| A web service | A **Cloud Run service** |
| Render builds your Dockerfile | **Cloud Build** builds it |
| Render stores your image | **Artifact Registry** stores it |
| The Environment page and `sync: false` | Environment variables on the service, plus **Secret Manager** |
| Your dashboard login | **IAM**, for people and for programs |
| The Logs page | **Cloud Logging** |
| Render Postgres | **Cloud SQL**, or any Postgres you can reach |

### Setting up without surprise bills

Everything in Google Cloud lives in a **project**: a container for services, permissions and billing, with a unique **project ID** such as `mimir-prod-4821`. Each project is linked to a **billing account**, which holds your payment method. Google Cloud needs a billing account even for free usage, so you'll add a card. Two programs keep the bill at zero:

- The **Free Tier** never expires. Each month, per billing account, Cloud Run gives you 2 million requests, 180,000 vCPU-seconds and 360,000 GiB-seconds of memory, which is roughly 50 hours of one full CPU. Secret Manager gives you 6 active secret versions and 10,000 reads, Artifact Registry 0.5 GB of image storage, and Cloud Build 2,500 build-minutes. The free amounts are priced at the rates of the cheapest regions, so deploy to one of those, such as `us-central1`.
- The **Free Trial** gives new accounts $300 of credit to spend over 90 days. You aren't charged during the trial, even if you go over the free tier, until you choose to upgrade to a paid account.

Before you deploy anything, set up three guards in the console under **Billing**:

1. **A budget with alerts.** Create a budget of, say, $5 a month for the whole billing account, with email alerts at 50%, 90% and 100%. Know its limit: an ordinary budget only *sends email*. It never stops anything, and billing data can lag by a day.
1. **A spend cap on Cloud Run.** Google Cloud now offers spend cap budgets for a few services, Cloud Run among them. When a project's estimated Cloud Run cost for the month passes the cap, new Cloud Run usage in that project is paused until the next month or until you lift it. The cap counts list prices before free-tier discounts, so a low cap may pause your service a little before you'd actually owe anything. That's the safe direction to be wrong in.
1. **A ceiling in the service itself.** You'll deploy with `--max-instances 1`, so even a flood of requests can't start a fleet of copies. Leave **minimum instances** at its default of 0. An always-on instance is the most common way learners leave the free tier.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Your model bill is separate

Cloud Run's free tier covers the container, not the model calls it makes. A public URL can still spend your model provider credit, so keep the login and rate limits from the LLM-Powered API switched on, and keep the spend limit you set in your provider's console.

</div>

Then install the [gcloud CLI](https://cloud.google.com/sdk/docs/install), the command-line tool for Google Cloud, and point it at your project:

```bash
gcloud auth login                              # opens a browser so you can sign in
gcloud config set project YOUR_PROJECT_ID      # every later command uses this project
gcloud config set run/region us-central1       # a cheap region where the free tier is priced

# Turn on the services this lesson uses. A new project has almost everything switched off.
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com
```

### IAM and service accounts

IAM answers one question over and over: *can this identity do this action on this resource?* It has three parts:

- A **principal** is who is asking: a person's Google account, a group, or a **service account**, which is an identity for a program rather than a person. Its email looks like `mimir-api@YOUR_PROJECT_ID.iam.gserviceaccount.com`.
- A **role** is a named bundle of permissions. `roles/secretmanager.secretAccessor` can read secret values; `roles/run.invoker` can call a Cloud Run service.
- A **binding** attaches a role to a principal on a resource: a whole project, or one secret.

Every Cloud Run service runs *as* a service account, and any Google Cloud API your code calls is checked against that account's roles. If you don't choose one, Cloud Run uses the project's **Compute Engine default service account**, which in many projects has the Editor role: it can change almost anything in the project. If your app had a security hole, an attacker would inherit all of that. The fix is the **principle of least privilege**: give each program a dedicated service account with only the roles it needs. Your API needs to read three secrets and, if you use Cloud SQL, connect to the database. That's all.

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format 'value(projectNumber)')

# The identity your API will run as. It starts with no permissions at all.
gcloud iam service-accounts create mimir-api --display-name "Mimir API runtime"
RUNTIME_SA="mimir-api@$PROJECT_ID.iam.gserviceaccount.com"

# Deploying from source builds your image with the default service account,
# which needs the Cloud Run Builder role to do that (it can take a minute to apply).
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role roles/run.builder
```

You'll grant `mimir-api` access to each secret in the next section, one secret at a time rather than to the whole project.

### Secrets in Secret Manager

**Secret Manager** stores secrets encrypted, controls who can read each one with IAM, and keeps **versions**: when you rotate a key, you add version 2, and version 1 stays until you disable or destroy it. That beats a dashboard text box, because you can see who read a secret and roll back to an earlier version.

```bash
# printf (not echo) so no newline sneaks into the secret. The value comes from your
# shell, never from a file in the repo. Paste your key into this variable first.
printf '%s' "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key --data-file=-
printf '%s' "$DATABASE_URL"      | gcloud secrets create database-url --data-file=-
openssl rand -hex 32 | tr -d '\n' | gcloud secrets create auth-secret --data-file=-

# Let the runtime account read exactly these three secrets, and nothing else.
for s in anthropic-api-key database-url auth-secret; do
  gcloud secrets add-iam-policy-binding "$s" \
    --member "serviceAccount:$RUNTIME_SA" --role roles/secretmanager.secretAccessor
done
```

`auth-secret` is the key your auth code signs tokens with, the one Render generated for you with `generateValue`. If you use a different model provider, store its key the same way under a name like `openai-api-key`. Three secrets with one version each uses half of the 6 free active versions, so when you rotate a key, destroy the old version (`gcloud secrets versions destroy 1 --secret anthropic-api-key`) once nothing uses it.

Cloud Run can hand a secret to your container as an environment variable or as a file. The environment variable is simplest, and your code doesn't change: it still reads `os.environ["ANTHROPIC_API_KEY"]`. One detail matters. An environment variable is read once, when an instance starts, so Google recommends **pinning** a version number (`anthropic-api-key:1`) rather than `latest`. Then you always know which key a running revision uses, and rotating a key becomes a deliberate deploy. The next lesson, Environments and Releases, depends on that.

### Deploying the container

Your Dockerfile from [Docker and Docker Compose](#/lessons/core/docker-and-compose) works as is. Cloud Run sets a `PORT` environment variable and sends traffic there. It defaults to 8080, but you can tell it your container listens on 8000. One small change to your app's `/health` route helps. Render told you the deployed commit through `RENDER_GIT_COMMIT`; Cloud Run sets `K_REVISION` instead, the name of the running **revision** (one immutable deployed version of your service):

```python
# main.py: inside health(), replace the RENDER_GIT_COMMIT line
version = os.environ.get("K_REVISION", "dev")    # e.g. mimir-api-00003-xyz on Cloud Run
return {"status": "ok", "database": "ok", "version": version}
```

Keep the route at `/health`. Cloud Run [reserves a few paths](https://cloud.google.com/run/docs/known-issues) for itself, including some that end in `z`, so the `/healthz` name you may see in other tutorials can fail there. Now deploy from the root of your repository:

```bash
gcloud run deploy mimir-api \
  --source . \
  --port 8000 \
  --service-account "$RUNTIME_SA" \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:1,DATABASE_URL=database-url:1,AUTH_SECRET=auth-secret:1" \
  --set-env-vars "INLINE_JOBS=true,LOG_LEVEL=INFO" \
  --max-instances 1 \
  --allow-unauthenticated
```

Line by line:

- **`--source .`** uploads your code to Cloud Build, which builds your Dockerfile and stores the image in an Artifact Registry repository named `cloud-run-source-deploy`. gcloud skips the files listed in your `.gitignore` (or a `.gcloudignore`), and your `.dockerignore` keeps `.env` out of the image anyway. The first deploy asks to create that repository; say yes.
- **`--port 8000`** matches the port in your Dockerfile's `CMD`.
- **`--service-account`** runs the app as `mimir-api` instead of the over-powered default.
- **`--set-secrets`** maps each environment variable to a pinned secret version. Cloud Run checks at deploy time that the service account can read each one, so a missing permission fails the deploy instead of the first request.
- **`--set-env-vars`** sets plain, non-secret configuration. `INLINE_JOBS=true` runs jobs in the API process, just as on Render's free plan.
- **`--max-instances 1`** caps the bill and, for now, keeps startup migrations safe (see the next section).
- **`--allow-unauthenticated`** grants `roles/run.invoker` to `allUsers`, so the whole internet can reach the URL. Without it, only callers with an IAM identity could. Your app's own login still protects the routes that matter.

A couple of minutes later, gcloud prints a URL ending in `.run.app`, served over HTTPS. If you'd rather build on your laptop and push the image yourself, that works too, with one trap: Macs with Apple Silicon build ARM images by default, and Cloud Run needs `docker build --platform linux/amd64`.

### Connecting to Postgres

Your API needs a `DATABASE_URL`, and you already stored one as a secret. The question is which database it points to. There are two common answers, and only one is free:

- **A managed Postgres outside Google Cloud.** Any provider that gives you a connection string reachable from the internet works, such as Neon's free plan, or the external URL of a Render database. It's free, and nothing changes in your code. The connection crosses the public internet, so require TLS (most providers add `?sslmode=require` to the URL for you) and use a strong password.
- **Cloud SQL**, Google Cloud's managed Postgres. It's the normal choice in production, but it's *not* part of the free tier. New projects can create one 30-day free trial instance, which is enough to practice.

On Cloud Run, Cloud SQL connections don't go through an IP address. You attach the instance to the service, and Cloud Run opens an encrypted connection and exposes it as a **Unix socket**, a file-like connection point, at `/cloudsql/PROJECT:REGION:INSTANCE`:

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:$RUNTIME_SA" --role roles/cloudsql.client   # may connect to Cloud SQL

gcloud run services update mimir-api \
  --add-cloudsql-instances "$PROJECT_ID:us-central1:mimir-db"
# The DATABASE_URL secret then looks like (note the empty host after the @):
# postgresql://mimir:PASSWORD@/mimir?host=/cloudsql/PROJECT_ID:us-central1:mimir-db
```

Your `database.py` from Deploying Your API already rewrites `postgresql://` to use psycopg, and psycopg reads the socket path from `host=`, so the code doesn't change either way. Creating the instance, sizing it, and backing it up are the subject of [Managed Postgres and Backups](#/lessons/production/managed-postgres-and-backups). Here, connecting is enough.

Migrations still run at startup, through the `alembic upgrade head && exec fastapi run ...` command from Deploying Your API. Put that line in your Dockerfile's `CMD` (wrapped in `/bin/sh -c`), because Cloud Run starts whatever the image says. Startup migrations are only safe while one copy runs, which `--max-instances 1` guarantees. Environments and Releases moves them into a separate step.

### Logs and a smoke test

Everything your app writes to standard output and standard error lands in **Cloud Logging**, tagged with the service and revision. The console's **Logs** tab on your service is the easiest view, and you can read recent lines from the terminal too:

```bash
gcloud run services logs read mimir-api --limit 50
URL=$(gcloud run services describe mimir-api --format 'value(status.url)')
uv run python smoke.py "$URL"        # the smoke test from Deploying Your API
```

Anything your app writes to its own disk is gone when the instance stops, and Cloud Run stops instances whenever traffic drops. A JSONL trace file inside the container is lost the same way. Keep traces where they outlive the instance: write them to standard output so they land in Cloud Logging, or into a Postgres table.

The first request after a quiet spell is slower, because Cloud Run has to start an instance. That's a **cold start**, usually a few seconds for a Python app, much shorter than Render's free-plan wake-up. If the deploy fails, the usual causes match Render's: the app isn't listening on `0.0.0.0` and the right port, a secret the service account can't read (the error names it), or a database URL that doesn't work from the cloud.

### Shutting it down

A hyperscaler bills for what *exists*, not only for what you use. A stopped project with leftover images, a forgotten Cloud SQL instance or an extra secret version can add cents or dollars every month. Keep a teardown script in your repo and run it when you're done with a demo:

```bash
#!/usr/bin/env bash
# teardown.sh: delete everything this lesson created. Safe to run twice.
set -uo pipefail                 # no -e: keep going if something is already gone
REGION=us-central1

gcloud run services delete mimir-api --region "$REGION" --quiet
gcloud artifacts repositories delete cloud-run-source-deploy --location "$REGION" --quiet
for s in anthropic-api-key database-url auth-secret; do
  gcloud secrets delete "$s" --quiet
done
gcloud sql instances delete mimir-db --quiet 2>/dev/null   # only if you made one
echo "Done. Check Billing > Reports tomorrow to confirm the spend is zero."
```

The bigger hammer is `gcloud projects delete YOUR_PROJECT_ID`. It stops billing for everything in the project at once, and the project can be restored for 30 days. Short of tearing down, the other habit that keeps you free is cleaning up images: each deploy stores a new one of a few hundred megabytes, so the 0.5 GB of free storage fills fast. Delete old images in Artifact Registry, or set a **cleanup policy** on the repository that keeps only the newest few.

<div class="lesson-note lesson-note--tip" markdown="1">

#### The same ideas on AWS and Azure

On AWS, the closest match is **Amazon ECS on Fargate**: your image goes in ECR, secrets in AWS Secrets Manager, permissions in IAM roles, and logs in CloudWatch. On Azure it's **Azure Container Apps**, with Azure Container Registry, Key Vault, managed identities and Azure Monitor. The names change; a container, a runtime identity with least privilege, secrets in a manager, and logs you can search do not. Google Cloud also hosts models (Gemini, and Claude models too) through Vertex AI, where your service account calls the model with IAM instead of an API key. That's one reason companies already on a cloud often buy models through it.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Google Cloud's [Free Tier and Free Trial page](https://cloud.google.com/free/docs/free-cloud-features) before you create anything, so you know exactly what's free and for how long.
   - Read the Free Trial section and the Cloud Run, Secret Manager, Artifact Registry and Cloud Build rows of the Free Tier table.
1. Read [Create, edit, or delete budgets and budget alerts](https://cloud.google.com/billing/docs/how-to/budgets) and [Manage spend cap budgets](https://cloud.google.com/billing/docs/how-to/budgets-spend-caps), to learn the difference between an alert and a cap.
   - From the second page, read "How spend cap budgets work" and "Limitations".
1. Read [Introduction to service identity](https://cloud.google.com/run/docs/securing/service-identity), Google's own explanation of why each Cloud Run service should have its own service account.
1. Read [Configure secrets for services](https://cloud.google.com/run/docs/configuring/services/secrets), which covers secrets as environment variables versus files, and why you pin versions.
1. Skim the [Cloud Run container runtime contract](https://cloud.google.com/run/docs/container-contract), the rules every container must follow: the port, the environment variables Cloud Run sets, and how instances start and stop.
1. Practice: put your LLM-Powered API on Cloud Run.
   - Create a project, set up the budget, the alerts and the Cloud Run spend cap, and enable the four services. Take a screenshot of the budget for your README.
   - Create the `mimir-api` service account and the three secrets, and grant access per secret.
   - Deploy with `--max-instances 1`, connected to a free Postgres. Run `smoke.py` against the `.run.app` URL and save the output.
   - Open IAM in the console and confirm the `mimir-api` account holds no project-wide roles beyond what you granted.
   - Commit `teardown.sh`. When you're finished with the project that follows, run it and check that the Billing report shows $0.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What does a hyperscaler make you decide that Render decided for you?](#why-a-hyperscaler)
- [What is the difference between a budget alert, a spend cap and max instances, and which of them actually stops spending?](#setting-up-without-surprise-bills)
- [What are a principal, a role and a binding, and why shouldn't your app run as the default service account?](#iam-and-service-accounts)
- [Why pin a secret version like anthropic-api-key:1 instead of using latest?](#secrets-in-secret-manager)
- [What does each flag in the gcloud run deploy command do, and what does allow-unauthenticated grant?](#deploying-the-container)
- [How does a Cloud Run service reach a Cloud SQL database, and what's a free alternative?](#connecting-to-postgres)
- [Why can a Google Cloud project keep costing money after your service stops getting traffic?](#shutting-it-down)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Cloud Run pricing](https://cloud.google.com/run/pricing) explains request-based versus instance-based billing and lists the free tier for services and jobs.
- [Deploy services from source code](https://cloud.google.com/run/docs/deploying-source-code) covers what `--source` does behind the scenes and the roles it needs.
- [Connect from Cloud Run to Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres/connect-run) is the full guide to the Unix socket and connector options.
- [The Cloud SQL free trial instance](https://cloud.google.com/sql/docs/postgres/free-trial-instance) explains the 30-day trial and what happens when it ends.
- [Hugging Face's Docker Spaces guide](https://huggingface.co/docs/hub/spaces-sdks-docker) is another free way to host a container, best for demos with a user interface.
