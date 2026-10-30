### Introduction

Logs, traces and dashboards tell you what happened, but only if someone is looking. Nobody watches a dashboard at 3 a.m. An **alert** is your system tapping a person on the shoulder: "something is wrong right now, and it needs you." Good alerts catch problems before users email you. Bad alerts wake people up for nothing, until everyone learns to ignore them, and then the real problem slips through.

LLM apps make this harder. A normal web app that breaks usually throws errors. An LLM app can fail while returning `200 OK` on every request: the provider gets slow, a prompt change makes answers worse, a loop in an agent burns through your budget, or the model starts refusing a whole category of questions. This lesson teaches you to decide what "working" means in numbers, alert only when those numbers are in danger, and handle an incident calmly when one arrives, from the first page to the blameless postmortem afterward.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- SLIs, SLOs and error budgets, and how they turn "reliable" into a number.
- Why you alert on symptoms users feel, not on causes.
- Burn-rate alerts that fire fast for big problems and stay quiet for small ones.
- Alerts specific to LLM apps: cost, latency, refusals and eval-score drift.
- A small script that checks SLOs from your logs and posts to a webhook.
- Alert fatigue, on-call basics and runbooks.
- Running an incident and writing a blameless postmortem.

### What an alert is for

An alert should mean exactly one thing: **a human needs to act, soon.** If nobody needs to do anything, it isn't an alert. It's information, and it belongs on a dashboard or in a daily report.

Teams usually sort notifications into three levels:

- **Page.** Interrupt someone now, even at night. Users are being hurt, or soon will be. Example: half of all requests are failing.
- **Ticket.** Someone should look within a day or two. Example: the error budget for the month is being spent a bit faster than planned.
- **Log or dashboard.** No notification at all. Example: one request timed out.

Most beginners page on everything. Every page should pass a simple test: is it urgent, is it real, and can the person who receives it actually do something about it? If you can't answer yes to all three, downgrade it.

### SLIs, SLOs and error budgets

To alert on "the app is broken," you first need to define "working" as a number. Google's Site Reliability Engineering (SRE) practice gives you three terms for this.

A **service level indicator (SLI)** is a measurement of how users experience your service, expressed as good events divided by all events. Examples:

- **Availability:** the share of requests that didn't fail with a server error.
- **Latency:** the share of requests whose first token arrived within 2 seconds.
- **Quality** (an LLM-specific one): the share of sampled answers that pass your eval judge.

A **service level objective (SLO)** is the target for an SLI over a time window, such as "99.5% of requests succeed, measured over 30 days." Notice that it isn't 100%. Nothing is 100% reliable, least of all an app that depends on someone else's model API. Users can't tell 99.9% from 100%, and chasing the last fraction costs a fortune.

The gap between the SLO and 100% is your **error budget**. With a 99.5% availability SLO and 1 million requests a month, you may fail 5,000 of them. The budget is a tool for decisions. While budget remains, ship features and experiment with new prompts. When it's nearly spent, slow down and work on reliability. It turns the old argument between "move fast" and "don't break things" into arithmetic.

An **SLA** (service level agreement) is a different thing: a contract with customers that says what happens, often refunds, if you miss a target. Your SLOs should be stricter than any SLA, so you notice trouble before it costs money. As a junior engineer you'll mostly work with SLOs.

Pick two or three SLOs per app, not twenty. For a typical chat or RAG app, start with availability, time to first token, and one quality SLI.

### Alert on symptoms, not causes

A **symptom** is something a user notices: errors, slowness, bad answers. A **cause** is something inside the system: high CPU, a full disk, a database connection pool at its limit, a provider returning `429`.

Alert on symptoms. High CPU that doesn't slow anyone down isn't an emergency, and paging on it trains people to ignore pages. Meanwhile, there are endless ways to break a system that no cause-based alert anticipated, but almost all of them show up as a symptom. If you alert on "too many failed requests" and "too slow," you catch the problems you predicted and the ones you didn't.

Causes still matter, as clues. Put them on the dashboard the on-call person opens after the page arrives. "Error rate is high" is the alert. "The provider is returning `529 overloaded`" is what the dashboard tells you next.

### Burn rates

The obvious alert, "page if the error rate is above 0.5%," works badly. One unlucky minute with 3 failures out of 200 requests fires it, even though that barely touches a month's budget. And a steady 0.6% error rate fires it constantly, when it really deserves a ticket.

The fix from the [Google SRE workbook](https://sre.google/workbook/alerting-on-slos/) is to alert on the **burn rate**: how fast you're spending the error budget compared with the rate that would use up exactly all of it by the end of the window.

```text
burn rate = error rate / (1 - SLO)
```

With a 99.5% SLO, an error rate of 0.5% is a burn rate of 1: you'll finish the month with exactly zero budget left. An error rate of 7.2% is a burn rate of 14.4, which spends 2% of the whole month's budget in a single hour. That deserves a page.

To keep alerts quick and quiet, check **two windows at once**: page only if the burn rate is above 14.4 over the last hour *and* over the last 5 minutes. The long window proves the problem is big enough to matter. The short window proves it's still happening, so the alert stops soon after you fix it. A slower burn, say above 1 over the last day, becomes a ticket instead of a page.

### Alerts specific to LLM apps

Errors and latency apply to any web service. LLM apps need a few more, because so many of their failures return `200 OK`:

- **Cost spikes.** A bug that loops an agent, a user who discovers your API, or a prompt change that doubles output length can multiply your bill overnight. Alert on spend per hour against a fixed limit, and set a hard spending cap in your provider's console as a backstop.
- **Latency, especially time to first token.** Provider slowdowns are common. Track time to first token (TTFT) for streaming apps and total time for everything else, as percentiles. A p95 latency of 4 seconds means 95% of requests finished within 4 seconds.
- **Upstream errors and rate limits.** Count `429`, `5xx` and timeout errors from the model API separately from your own errors. They often explain the symptom.
- **Refusals and odd stop reasons.** A sudden jump in refusals, or in responses cut off at the token limit, often means a prompt or model change went wrong. On the Claude API these show up as the `stop_reason` values `refusal` and `max_tokens`.
- **Eval-score drift.** Quality can decay with no error at all. Each day, sample production traces, score them with the judge you built in From Traces to Evals, and alert if the score falls below the lower end of your baseline's confidence interval (from Eval Statistics). This is usually a ticket, not a page.
- **Fallback rate.** If you route to a backup model when the main one fails, alert when the fallback fires much more often than usual. You're still up, but you're running on your spare tire.

### A small SLO checker

Real teams use tools like Prometheus with Alertmanager, Grafana or Datadog for this. They all do the same job, though, and you can understand that job by building a tiny version. The script below reads request logs, one JSON object per line like the structured logs you wrote in Logging and Tracing, checks four rules, and posts any alerts to a webhook. One difference: the checker expects one line per request with `status`, `ttft_ms`, `cost_usd` and `stop_reason` together. The app in Logging and Tracing splits those across its `answered` and `request done` lines and doesn't stream, so it has no time to first token. To alert on your own app, log one combined line at the end of each request, and record `ttft_ms` when the first streamed chunk arrives (you measured it in Streaming Responses). `fake_logs.py` writes that format, so you can try the checker first.

First, some fake logs to test against: an hour of healthy traffic that goes badly wrong in the last 10 minutes.

```python
# fake_logs.py: write an hour of request logs, with an incident in the last few minutes.
import json
import random
from datetime import UTC, datetime, timedelta

now = datetime.now(UTC)
with open("requests.jsonl", "w") as f:
    for second in range(3600, 0, -2):              # one request every 2 seconds
        ts = now - timedelta(seconds=second)
        incident = second < 600                    # the last 10 minutes go wrong
        failed = random.random() < (0.6 if incident else 0.002)
        f.write(json.dumps({
            "ts": ts.isoformat(),
            "route": "/ask",
            "status": 503 if failed else 200,
            "ttft_ms": random.gauss(4000 if incident else 700, 150),
            "cost_usd": 0.0004,
            "stop_reason": "refusal" if random.random() < 0.01 else "end_turn",
        }) + "\n")
print("wrote requests.jsonl")
```

Now the checker. Install its one dependency with `uv add httpx`.

```python
# slo_check.py: check SLOs from JSONL request logs and post any alerts to a webhook.
import argparse
import json
import os
import statistics
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx

SLO = 0.995               # 99.5% of requests succeed, measured over 30 days
PAGE_BURN = 14.4          # spending the 30-day budget 14.4x too fast = 2% of it per hour
TTFT_P95_MS = 2000        # 95% of answers start within 2 seconds
MAX_COST_PER_HOUR = 2.00  # dollars
MAX_REFUSAL_RATE = 0.05
QUIET_SECONDS = 1800      # don't repeat the same alert within 30 minutes
RUNBOOK = "https://github.com/YOU/YOUR-APP/blob/main/RUNBOOK.md"


def load(path: str, since: datetime) -> list[dict]:
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    return [r for r in rows if datetime.fromisoformat(r["ts"]) >= since]


def burn_rate(rows: list[dict]) -> float:
    """How many times faster than 'allowed' we are spending the error budget."""
    if not rows:
        return 0.0
    error_rate = sum(r["status"] >= 500 for r in rows) / len(rows)
    return error_rate / (1 - SLO)


def check(path: str) -> dict[str, str]:
    now = datetime.now(UTC)
    hour = load(path, now - timedelta(hours=1))
    recent = [r for r in hour if datetime.fromisoformat(r["ts"]) >= now - timedelta(minutes=5)]
    alerts = {}

    long_burn, short_burn = burn_rate(hour), burn_rate(recent)
    if long_burn > PAGE_BURN and short_burn > PAGE_BURN:  # both windows: real and still happening
        alerts["errors"] = f"Error budget burning {long_burn:.0f}x too fast (1h), {short_burn:.0f}x (5m)"

    ttfts = [r["ttft_ms"] for r in recent if r["status"] < 500]
    if len(ttfts) >= 20 and (p95 := statistics.quantiles(ttfts, n=100)[94]) > TTFT_P95_MS:
        alerts["latency"] = f"p95 time to first token is {p95:.0f} ms (SLO {TTFT_P95_MS} ms)"

    if (cost := sum(r["cost_usd"] for r in hour)) > MAX_COST_PER_HOUR:
        alerts["cost"] = f"Spent ${cost:.2f} in the last hour (limit ${MAX_COST_PER_HOUR:.2f})"

    if hour and (rate := sum(r["stop_reason"] == "refusal" for r in hour) / len(hour)) > MAX_REFUSAL_RATE:
        alerts["refusals"] = f"Refusal rate is {rate:.1%} over the last hour"
    return alerts


def notify(alerts: dict[str, str], state_file: Path = Path("alert_state.json")) -> None:
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    fresh = {k: v for k, v in alerts.items() if time.time() - state.get(k, 0) > QUIET_SECONDS}
    if not fresh:
        return
    text = "\n".join(fresh.values()) + f"\nRunbook: {RUNBOOK}"
    if url := os.environ.get("ALERT_WEBHOOK_URL"):
        httpx.post(url, content=text.encode(), timeout=10).raise_for_status()
    print(text)
    state.update({k: time.time() for k in fresh})
    state_file.write_text(json.dumps(state))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check SLOs from request logs.")
    parser.add_argument("log", help="path to a JSONL file of requests")
    alerts = check(parser.parse_args().log)
    if alerts:
        notify(alerts)
    else:
        print("All SLOs OK")
    raise SystemExit(1 if alerts else 0)
```

Run `uv run fake_logs.py`, then `uv run slo_check.py requests.jsonl`. You should see something like:

```text
Error budget burning 20x too fast (1h), 117x (5m)
p95 time to first token is 4291 ms (SLO 2000 ms)
Runbook: https://github.com/YOU/YOUR-APP/blob/main/RUNBOOK.md
```

The cost and refusal rules stay quiet, because those numbers are healthy. Run the checker a second time and it prints nothing: the state file remembers that it already sent those alerts, so it won't repeat them for 30 minutes. That small piece of memory is the difference between one useful message and one every minute until someone fixes the problem.

A few details worth noticing:

- `ALERT_WEBHOOK_URL` is where alerts go. A **webhook** is just a URL that accepts a `POST`. The script sends plain text, which is what [ntfy](https://docs.ntfy.sh/publish/) expects: a free, open-source service that pushes notifications to your phone, with no account needed. Slack's [incoming webhooks](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks) want JSON instead, so for Slack you'd send `json={"text": text}`.
- Every alert links to a runbook. More on that below.
- The exit code is `1` when something is wrong, so a scheduler or CI job can show the run as failed.

To run it for real, schedule it every few minutes: a `cron` entry on a server, a Cloud Scheduler job that triggers a Cloud Run job, or the `schedule` trigger in GitHub Actions (which can run several minutes late, so it's fine for tickets but slow for pages). Point `load()` at wherever your logs or traces actually live. If they're in Postgres, replace it with a SQL query over the last hour.

### Fighting alert fatigue

**Alert fatigue** is what happens when people get so many alerts, mostly unimportant, that they stop reacting to any of them. It is the most common way alerting fails. Every noisy alert spends trust, and you need that trust when the real one fires.

Habits that keep alerts meaningful:

- **Every page must be actionable.** If the response to an alert is "watch it and see," it shouldn't page.
- **Deduplicate and group.** One incident should produce one notification, not fifty. Repeat only while it's ongoing, and slowly.
- **Require it to last.** A condition that clears itself in 30 seconds shouldn't wake anyone. Burn-rate windows handle this for you.
- **Review your alerts regularly.** Once a month, list every alert that fired. For each one, ask whether someone acted on it. Delete or downgrade the ones nobody did.
- **Put the next step in the alert.** The current value, the threshold, and a link to the runbook and the dashboard.
- **Don't send pages to channels people mute.** A page goes to a phone, through a tool built for it. Tickets and reports can go to chat.

### On-call basics

Being **on call** means that for a set period, often a week, you are the person who answers pages. Many AI engineering jobs include an on-call rotation, so it's worth knowing the norms before your first one.

- **A rotation** shares the load. Teams take turns, with a primary and often a secondary who is paged if the primary doesn't respond within a few minutes (an **escalation policy**).
- **Acknowledge quickly.** Acknowledging a page tells everyone that you're on it and stops the escalation. You don't need a fix yet.
- **Mitigate first, then find the root cause.** Your first job is to stop the user pain: roll back the last deploy, switch to the fallback model, turn off the feature flag. Understanding why it happened can wait until users are fine.
- **Ask for help early.** Escalating isn't failing. A second pair of eyes after 15 minutes beats a lone hero after two hours.
- **Hand off cleanly.** At the end of a shift, write down what fired, what you did and what's still open.
- **Healthy teams protect on-call people.** Few pages per shift, time off after a bad night, and every page that turned out to be noise gets fixed. If on-call is miserable, the alerts are the bug.

Tools such as PagerDuty and Opsgenie handle rotations, escalation and phone calls. For a personal project, a phone notification from ntfy is plenty.

### Runbooks

A **runbook** is a short document that tells the on-call person what to do when a specific alert fires. It exists because at 3 a.m., under stress, nobody thinks clearly, and the person paged may not be the one who built the feature.

A runbook entry for each alert answers:

1. **What does this alert mean?** In one sentence, in user terms.
2. **How do I check how bad it is?** Links to the right dashboard and trace search.
3. **What are the likely causes, and how do I tell them apart?** For example: "check the provider's status page; check whether a deploy went out in the last hour."
4. **How do I mitigate?** Exact commands or clicks: roll back to the previous release, flip the flag that switches to the fallback model, lower the per-user rate limit.
5. **Who do I escalate to?**

Here is one entry for an LLM app:

```markdown
## Alert: error budget burning fast

Meaning: many /ask requests are failing. Users see "try again later".

Check: open the errors dashboard. Split failures by upstream status code.
- Mostly 429 or 529 from the model API -> provider limit or outage.
  Check the provider status page. Confirm FALLBACK_ENABLED=true and that
  fallback calls are succeeding in traces.
- Mostly our own 500s -> look at the last deploy. If it went out in the
  past 2 hours, roll back first (see "Rolling back" below), then investigate.

Escalate: if not mitigated within 30 minutes, page the secondary on-call.
```

Keep runbooks in the repo next to the code, update them after every incident, and test them occasionally by following them on purpose. You'll write a full `RUNBOOK.md` in the Ship It project.

### Running an incident

An **incident** is any event that hurts users enough that people drop their normal work to deal with it. Even on a small team, a little structure helps:

1. **Declare it.** Say clearly in a shared channel, "I'm declaring an incident: /ask is failing for about 50% of users." Declaring early is cheap; declaring late is costly.
2. **Assign roles.** On larger incidents, one **incident commander** coordinates and makes decisions but doesn't type fixes, while others investigate. On a two-person team you might hold several roles, but say which.
3. **Keep a timeline.** Write down what you saw, what you tried and when, as it happens. You'll need it for the postmortem, and memory is unreliable under stress.
4. **Communicate.** Update users or stakeholders at a steady rhythm, even if the update is "still investigating."
5. **Mitigate, confirm, close.** Stop the pain, confirm the SLI has recovered on the dashboard, and only then declare the incident over.

### Blameless postmortems

After an incident, the team writes a **postmortem** (also called an incident review): a document explaining what happened, why, and what will change so it doesn't happen again.

The key word is **blameless**. A blameless postmortem assumes that everyone acted reasonably given what they knew at the time, and asks how the system let a reasonable action cause harm. "Sam deployed a broken prompt" leads nowhere: Sam feels bad, and next time someone else deploys a broken prompt. "A prompt change could reach production without running the eval suite" leads to a fix: gate prompt changes on evals in CI, which you'll build in Prompt Versioning and CI Evals. Blame makes people hide mistakes. Blamelessness makes them report problems early, which is what you want.

A useful postmortem has:

- **Summary:** what happened and how users were affected, in a few sentences.
- **Impact:** how long, how many users or requests, how much error budget or money it cost.
- **Timeline:** from the change that triggered it, through detection, to recovery, with times.
- **Root causes and contributing factors:** usually several. Asking "why?" repeatedly helps you get past the first, shallow answer.
- **What went well and what went badly:** including how quickly the alert fired. Detection time is often the cheapest thing to improve.
- **Action items:** specific, each with an owner and a due date. "Be more careful" is not an action item. "Add a cost alert at $2 an hour" is.

For LLM incidents, one action item should almost always be: **add the failing inputs to your eval set**, exactly as you learned in From Traces to Evals, so the same failure can't come back silently.

### On other providers

Everything in this lesson except the field names is provider-neutral: SLOs, burn rates, runbooks and postmortems work the same whether you call Claude, OpenAI, Gemini or a model you host yourself. What changes is where you find the signals. On the Claude API, refusals and truncation show up as `stop_reason` values (`refusal`, `max_tokens`), described in [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons). OpenAI's Chat Completions API reports the same ideas through `finish_reason` (for example `length` when it hits the token limit, or `content_filter`), as shown in the [chat completion object reference](https://platform.openai.com/docs/api-reference/chat/object). Normalize these into one field such as `stop_reason` when you log, so your alert rules don't care which provider served the request. If you run open models yourself, for example with [Ollama](https://docs.ollama.com/api/openai-compatibility), there's no per-token bill to alert on, but there is a new failure to watch: your own model server running out of memory or GPU, which now belongs in your own SLOs.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) from Google's free *Site Reliability Engineering* book. It's the source of the SLI, SLO and error budget vocabulary used across the industry.
   - Read it all. Notice how they choose indicators from what users care about, not from what's easy to measure.
1. Read [Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) from the free *SRE Workbook*. It builds up from naive threshold alerts to multiwindow burn-rate alerts, one flaw at a time.
   - Focus on the six approaches and their trade-offs. Approach 6 is what `slo_check.py` does.
1. Read [Postmortem Culture: Learning from Failure](https://sre.google/sre-book/postmortem-culture/), then skim the [PagerDuty Incident Response guide](https://response.pagerduty.com/), a free, practical handbook for running incidents and being on call.
   - In the PagerDuty guide, read "Being On-Call" and the incident commander role.
1. Practice: run the SLO checker.
   - Run `fake_logs.py` and `slo_check.py` and get the alerts above. Then change `fake_logs.py` so that only the refusal rule fires, and so that a brief 1-minute blip fires nothing.
   - Send a real alert to your phone: install the ntfy app, pick a hard-to-guess topic name, set `ALERT_WEBHOOK_URL=https://ntfy.sh/<your-topic>` and run the checker again.
1. Practice: write SLOs and a runbook for one of your deployed projects (for example, your LLM-Powered API or Hello, Production).
   - Write two or three SLOs, each with its SLI, target and window, and the alert rule for each.
   - Write a runbook entry for each alert, in the format above.
   - Adapt `load()` to read your app's real logs or traces, and run the checker against them.
1. Practice: write a blameless postmortem for a real failure from one of your projects, even a small one, such as a broken deploy or a bad prompt change. Use the structure from this lesson, and end with at least two action items with owners and dates.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between a page, a ticket and a dashboard entry?](#what-an-alert-is-for)
- [What are an SLI, an SLO and an error budget, and why isn't the SLO 100%?](#slis-slos-and-error-budgets)
- [Why should you alert on symptoms rather than causes?](#alert-on-symptoms-not-causes)
- [What is a burn rate, and why check two time windows instead of one?](#burn-rates)
- [Which failures of an LLM app return 200 OK, and how would you alert on them?](#alerts-specific-to-llm-apps)
- [What should an on-call engineer do first when paged, and what can wait?](#on-call-basics)
- [What makes a postmortem blameless, and why does that lead to better fixes?](#blameless-postmortems)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) from the SRE book explains symptoms versus causes and the "four golden signals" (latency, traffic, errors, saturation).
- [My Philosophy on Alerting](https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q/preview) by Rob Ewaschuk is a short, much-quoted essay on making every page count.
- [The PagerDuty Postmortem guide](https://postmortems.pagerduty.com/) has a free template and advice on running a postmortem meeting.
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/) is the open-source tool many teams use for what `slo_check.py` does, with dashboards, silences and notification routing built in.
- [A list of public postmortems](https://github.com/danluu/post-mortems) collects real incident write-ups from many companies. Reading a few is the fastest way to learn what real postmortems look like.
