### Introduction

You've already met most of the ways an AI app gets attacked. Prompt Injection and the Lethal Trifecta showed how text the model reads can take over an agent. Secure Design Patterns, Guardrails in Production and Approvals and Permissions showed how to build an agent that stays safe even when the model is fooled. What you haven't done yet is check a whole system, end to end, against a list, and write down what you found.

That is a **security review**. You walk through a known list of risks, decide which ones apply to your app, say what you did about each, and point to the test or setting that proves it. The list protects you from your own memory: the risk you forget to think about is usually the one that bites. This lesson uses the OWASP Top 10 for LLM Applications as the checklist. For the risks earlier lessons already taught, it points back to them. It spends its time on the gaps those lessons didn't cover: secrets, dependencies, auth on every endpoint, data leaking through logs and traces, attacks on your bill, and what happens to model output after it leaves the model.

You'll finish with a `SECURITY.md` for a real project and a test file that keeps it true. The Ship It project asks for both.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a security review is and what it produces.
- Using the OWASP Top 10 for LLM Applications as a checklist.
- Keeping secrets out of code, prompts, history and logs.
- Dependency and supply-chain risk, including hallucinated packages.
- Checking that every endpoint requires a login, and that logs and traces don't leak data.
- Denial of wallet: protecting your bill from abuse.
- Handling model output safely, and tests that keep a review true.

### What a security review is

A security review answers three questions about a system, in writing:

1. **What could go wrong?** This is the **threat model** you started in Secure Design Patterns: what the system can touch, who can talk to it, and what an attacker would want.
1. **What did we do about it?** For each risk, the **mitigation**: the design choice, setting or code that reduces it. "We told the model not to" is not a mitigation.
1. **How do we know it works?** The **evidence**: a test, a CI check, a screenshot of a setting, a log line. A mitigation with no evidence is a hope.

The output is usually a short document kept in the repo, often named `SECURITY.md`, plus tests. It's not a one-time event. You redo the relevant rows whenever you add a tool, a data source, an endpoint or a dependency, which is why the tests matter more than the document.

A review also records **residual risk**: what's still possible after your mitigations, and why you accept it. "A user can still get the agent to write a rude email draft, but every send needs approval" is an honest residual risk. Reviewers trust a document that admits what it doesn't cover far more than one that claims everything is solved.

### The OWASP checklist

**OWASP** (the Open Worldwide Application Security Project) publishes the Top 10 for LLM Applications. The 2025 list is the checklist for this lesson. Here it is, with where this curriculum already taught each risk and what to check during a review:

| ID | Risk | Taught in | Check during review |
| --- | --- | --- | --- |
| LLM01 | Prompt injection | Prompt Injection and the Lethal Trifecta; Secure Design Patterns | No agent has all three trifecta legs; injection cases in the eval set |
| LLM02 | Sensitive information disclosure | Guardrails in Production; this lesson | Output screens; logs and traces hold no secrets or raw PII |
| LLM03 | Supply chain | This lesson | Locked, audited dependencies; known sources for models and MCP servers |
| LLM04 | Data and model poisoning | Prompt Injection (poisoned documents); this lesson | Who can add documents to your index; where model weights come from |
| LLM05 | Improper output handling | Frontend lessons; this lesson | Output is escaped, validated or parameterized before use |
| LLM06 | Excessive agency | Approvals and Permissions; Sandboxing Agents | Fewest tools, scoped credentials, approval on risky actions |
| LLM07 | System prompt leakage | Guardrails in Production (canaries) | No secrets or access rules live only in the prompt |
| LLM08 | Vector and embedding weaknesses | User Accounts and Auth; this lesson | Retrieval filters by owner, so one user's documents never reach another |
| LLM09 | Misinformation | Citations and Grounding; Evals in Practice | Answers cite sources; groundedness is measured |
| LLM10 | Unbounded consumption | Agent Cost and Latency; this lesson | Auth, rate limits, per-user budgets and a provider spend limit |

For agents, add the **OWASP Top 10 for Agentic Applications (2026)**, which you met in the Prompt Injection lesson. Most of its risks, such as goal hijack and tool misuse, map onto LLM01 and LLM06 above, so review them together and cite both IDs in your table.

Two rows deserve a sentence more, because they're easy to miss. For **LLM08**, a multi-user RAG app must filter the vector search by the user's ID inside the SQL query, as you filtered every query by `owner_id` in User Accounts and Auth. Filtering after retrieval is too late: the other user's chunk is already in the prompt. For **LLM07**, assume your system prompt will be extracted, because it usually can be. That's fine if it holds only instructions. It's a problem if it holds an API key, an internal URL, or the only copy of an access rule like "never show salaries to non-managers." Access rules belong in code.

The rest of this lesson covers the parts of the checklist that earlier lessons didn't teach.

### Secrets

You learned the basics in API Keys and Secrets: keys live in environment variables, `.env` is in `.gitignore`, and a deployed app reads them from the host's secret store. A review checks that this is still true, and adds four habits.

- **Scan for secrets automatically.** People make mistakes, and coding agents happily paste a key into a test file. [Gitleaks](https://github.com/gitleaks/gitleaks) is a free scanner that looks for key-shaped strings. Add it to the pre-commit setup you built in Linting, Formatting and CI, and it blocks the commit before the key exists anywhere but your laptop. On GitHub, also turn on **push protection** for secret scanning, which is free for public repositories and rejects a push that contains a known key format.

```yaml
# .pre-commit-config.yaml (add to your existing repos list)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```

Run `gitleaks git -v` once in each existing repo to scan its full history, not just new commits.

- **One key per environment.** Development, CI and production each get their own key with its own spending limit, so a leaked CI key can't drain production's budget, and you can revoke one without taking the others down.
- **The model never holds a credential.** A tool that sends email uses a token your server holds. The model asks for the action; your code attaches the credential. That's the scoped-credentials idea from Approvals and Permissions, and it means a prompt injection can't print a key the model never saw.
- **Know your leak drill.** If a key leaks: revoke it first, then create a new one, then check the provider's usage page for spending you don't recognize, then clean up the history. Deleting the commit doesn't help, because copies are already in forks, caches and scrapers within minutes. Put this drill in your runbook.

### Dependencies and the supply chain

Your app runs a few hundred packages you didn't write. The **supply chain** is everything you install and trust: Python packages, GitHub Actions, Docker base images, model weights and MCP servers. Any of them can have a known vulnerability, or be malicious.

`uv` already gives you the most important defense. `uv.lock` pins every package, including dependencies of dependencies, to an exact version with a hash, and `uv sync --locked` in CI and your Dockerfile refuses to install anything that doesn't match. Three more checks complete it:

```bash
# 1. The lockfile matches pyproject.toml (fails if someone edited one without the other)
uv lock --check

# 2. No installed version has a published vulnerability
uv export --format requirements-txt --no-hashes --no-emit-project -o audit-requirements.txt
uvx pip-audit -r audit-requirements.txt
```

[pip-audit](https://github.com/pypa/pip-audit) looks up each version in public vulnerability databases and exits with an error if it finds one, so it works as a CI step. Newer releases of `uv` also have a `uv audit` command that does the same in one step, but at the time of writing it's marked experimental. The third check is **Dependabot**, GitHub's free bot that opens pull requests when a dependency has an update or a security fix. It understands `uv` projects and GitHub Actions directly, through a `.github/dependabot.yml` file. Treat its pull requests like any other: CI must pass, and someone reads the changelog.

AI tools add a new supply-chain risk. A model asked for code sometimes imports a package that doesn't exist. Attackers watch for commonly hallucinated names and publish real packages under them, with malware inside. This is sometimes called **slopsquatting**. A 2024 study of 16 code models, [We Have a Package for You!](https://arxiv.org/abs/2406.10279), found that at least 5.2% of recommended packages from commercial models, and 21.7% from open models, didn't exist. The defense is a review habit: before you add any package an assistant suggested, look it up on PyPI and check that it's the well-known project you expected, with a real history. The Code Review lesson that follows makes this part of every review.

The same applies to everything else you install. Pin GitHub Actions to versions or commit hashes, as in Prompt Versioning and CI Evals. Download open-model weights in the `safetensors` format from the official publisher, not an unknown re-upload. And treat a third-party MCP server as code you're running, because it is.

### Auth on every endpoint

User Accounts and Auth taught you to protect a route with a `CurrentUser` dependency and to filter every query by owner. A review checks that you did it **everywhere**, which is exactly where people slip. The usual gaps are a debug route added in a hurry, an admin page, a webhook, a file download, or the streaming endpoint written later than the others. The OWASP API Security Top 10 lists broken authentication and broken object-level authorization near the top for a reason.

Don't check this by reading routes one by one. Write a test that walks every route in the app and fails if one isn't public on purpose and doesn't depend on `get_current_user`. Then a route added next month, by you or by an agent, can't skip auth quietly. You'll see that test below.

Two more checks belong here. **CORS** (the browser rule about which websites may call your API) should list your frontend's domain, not `*`, for any route that uses cookies or tokens. And your `/health` endpoint should say "ok" and nothing else, not your config, version list or database status, because it's public.

### Leaks through logs and traces

Logging and Tracing covered redacting content before export. A review checks the paths that redaction doesn't see:

- **Headers.** Logging "the request" often logs its `Authorization` header, which is a working credential. Log the user ID, never the token.
- **Error reports.** A crash report or a traceback can include the local variables at the crash, which may hold the user's message or a key. Check what your error tracker captures.
- **Third-party backends.** Sending traces to a hosted tracing service means sending user data to another company. That's often fine, but it's a decision, and your privacy notes should say so.
- **Model inputs in logs.** It's tempting to log the full prompt "for debugging." Put content in traces, on purpose, redacted and with a retention limit, and keep plain logs to metadata: user ID, route, sizes, timings, status.

As with auth, test it. Plant a canary string and a fake card number in a request, run it through the app, and assert that neither appears in the captured logs or in your span file.

### Denial of wallet

A normal denial-of-service attack tries to take your site down. A **denial-of-wallet** attack keeps it up and makes you pay. Every request to an LLM app costs real money, so a bot, a leaked demo link or one enthusiastic user with a script can run up a bill of hundreds of dollars overnight. OWASP calls this unbounded consumption (LLM10).

You already have some of the layers. Agent Cost and Latency added step, token and dollar budgets **per run**, and Timeouts, Retries and Rate Limits added a per-user limit on **requests**. Neither is enough alone. A rate limit of 5 requests a minute still allows 7,200 requests a day, and each could be a long agent run. A per-run budget doesn't stop a user from starting thousands of runs. The full set is:

1. **Authentication**, so every request has a user to charge.
1. **Input limits**, so nobody can send a 900-page document to a route meant for questions.
1. **Output caps**, a `max_tokens` on every call and a step budget on every agent.
1. **A per-user daily budget** in dollars, checked before each call.
1. **A spend limit in the provider's console**, the backstop that works even when your code is wrong, plus the cost alert from Alerting and Incidents.

Here's the per-user daily budget. Save it as `wallet.py`:

```python
# wallet.py: limits that stop one user from draining your account.
import os
from datetime import date

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
PRICE_PER_MTOK = {"input": 0.10, "output": 0.50}  # from the pricing page; goes stale
MAX_INPUT_CHARS = 8_000  # (1) refuse huge inputs before they cost anything
MAX_OUTPUT_TOKENS = 1_024  # (2) cap every answer, thinking included
DAILY_BUDGET_USD = 0.50  # (3) per user, per day


class BudgetExceeded(Exception):
    pass


class Ledger:
    """Dollars spent per user per day. Keep it in Redis or Postgres in production."""

    def __init__(self, today=date.today):
        self.today = today  # injectable, so tests can change the date
        self.spent: dict[tuple[str, date], float] = {}

    def check(self, user_id: str) -> None:
        if self.spent.get((user_id, self.today()), 0.0) >= DAILY_BUDGET_USD:
            raise BudgetExceeded(user_id)

    def charge(self, user_id: str, usage) -> float:
        cost = (
            usage.input_tokens * PRICE_PER_MTOK["input"]
            + usage.output_tokens * PRICE_PER_MTOK["output"]
        ) / 1_000_000
        key = (user_id, self.today())
        self.spent[key] = self.spent.get(key, 0.0) + cost
        return cost


def ask(client, ledger: Ledger, user_id: str, question: str) -> str:
    if len(question) > MAX_INPUT_CHARS:
        raise ValueError(f"question is longer than {MAX_INPUT_CHARS} characters")
    ledger.check(user_id)  # (4) before the call: refuse once today's budget is spent
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        messages=[{"role": "user", "content": question}],
    )
    ledger.charge(user_id, response.usage)  # (5) after: charge what was really used
    return "".join(b.text for b in response.content if b.type == "text")


if __name__ == "__main__":
    ledger = Ledger()
    question = "What is a denial-of-wallet attack? One sentence."
    print(ask(anthropic.Anthropic(), ledger, "user-1", question))
    print(ledger.spent)
```

Run it with `uv add anthropic` and `uv run wallet.py`. The numbered comments:

1. The input check runs before anything is spent. Pick a limit from your real traffic: comfortably above your longest legitimate input.
1. `max_tokens` bounds a single answer. On current Claude models it includes any thinking, so a cap that's too tight cuts answers off; check `stop_reason` in your traces.
1. The budget is in dollars because that's what you actually care about, and it stays meaningful when you change models. Set it from data, as you set run budgets: well above what your heaviest real users spend.
1. The check runs **before** the call, so a user who's over budget costs nothing more.
1. The charge runs **after**, from `usage`, because only the response knows what was spent. This means one call can overshoot the budget, by at most one capped call. That's why the output cap and the budget work together.

The ledger lives in memory here, so it resets on restart and isn't shared between processes. In production, keep it where you kept your rate-limit counters: Redis or Postgres. Return `429` with a clear message when the budget is spent, as the app below does. A free public demo might use a budget of a few cents and a login. An internal tool might use dollars.

### Output handling

Model output is untrusted input, as you learned in the frontend lessons: in the browser it goes in with `textContent` or JSX, never `innerHTML` or `dangerouslySetInnerHTML`. A review checks every other place output goes, too. Trace each one from the model to where it's used:

- **HTML and Markdown.** If you render Markdown, use a sanitizer, and block images and links to domains you don't control. A Markdown image is the exfiltration route you saw in the Prompt Injection lesson: the browser fetches the URL, with whatever data the attacker put in it.
- **SQL.** Never build a query by putting model text into a string. Use parameters, as SQLModel does for you, or have the model fill a structured object and build the query in code.
- **Shell, files and code.** Never pass output to `subprocess` with `shell=True`, to `eval` or `exec`, or use it as a file path without checking it against an allowlist. Code a model writes runs in a sandbox (Sandboxing Agents), not on your server.
- **Other systems.** An email body, a CRM field or a webhook payload filled from output is output too. Validate it against a Pydantic schema before it's sent, and keep the approval step for anything that leaves your system.

The pattern is the same everywhere: validate the shape, then escape or parameterize it for the place it's going.

### Tests that keep the review true

A security review written once goes out of date the first time someone adds a route. Tests don't. Here's a small app and a test file that checks three rows of the review on every push, with a fake model client and no real API calls. Save the app next to `wallet.py` as `app.py`:

```python
# app.py: a small API with auth on every costly route and no content in its logs.
import logging
from typing import Annotated

import anthropic
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from wallet import BudgetExceeded, Ledger, ask

log = logging.getLogger("app")
app = FastAPI()
ledger = Ledger()
PUBLIC_PATHS = {"/health", "/docs", "/docs/oauth2-redirect", "/openapi.json", "/redoc"}


def get_current_user(authorization: Annotated[str, Header()] = "") -> str:
    # Stand-in: use the real dependency from User Accounts and Auth.
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"})
    return authorization.removeprefix("Bearer ")


def get_client():
    return anthropic.Anthropic()


class Question(BaseModel):
    text: str


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/ask")
def ask_route(
    body: Question,
    user: Annotated[str, Depends(get_current_user)],
    client: Annotated[object, Depends(get_client)],
) -> dict:
    # Log facts about the request, never its content or the headers.
    log.info("ask user=%s chars=%d", user, len(body.text))
    try:
        return {"answer": ask(client, ledger, user, body.text)}
    except BudgetExceeded:
        raise HTTPException(
            status_code=429, detail="Daily limit reached. Try again tomorrow."
        )
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))
```

And the tests, in `test_security.py`:

```python
# test_security.py: security checks that run on every push, with no real API calls.
from types import SimpleNamespace

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import app as service
from wallet import DAILY_BUDGET_USD


class FakeClient:
    """Stands in for the Anthropic client: same shape, no network, no cost."""

    def __init__(self):
        self.messages = self

    def create(self, **kwargs):
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text="An answer.")],
            usage=SimpleNamespace(input_tokens=20_000, output_tokens=1_000),
        )


def dependency_calls(dependant):
    """Every function a route depends on, including dependencies of dependencies."""
    for dep in dependant.dependencies:
        yield dep.call
        yield from dependency_calls(dep)


def test_every_route_requires_login():
    for route in service.app.routes:
        if isinstance(route, APIRoute) and route.path not in service.PUBLIC_PATHS:
            assert service.get_current_user in dependency_calls(route.dependant), (
                route.path
            )


def test_logs_hold_no_content(caplog):
    service.app.dependency_overrides[service.get_client] = FakeClient
    secret_text = "my card is 4111 1111 1111 1111 CANARY-91c2"
    with caplog.at_level("DEBUG"):
        r = TestClient(service.app).post(
            "/ask",
            json={"text": secret_text},
            headers={"Authorization": "Bearer alice"},
        )
    assert r.status_code == 200
    assert "CANARY-91c2" not in caplog.text
    assert "Bearer" not in caplog.text


def test_budget_stops_a_user_but_not_others():
    service.app.dependency_overrides[service.get_client] = FakeClient
    client = TestClient(service.app)
    service.ledger.spent.clear()
    statuses = [
        client.post(
            "/ask", json={"text": "hi"}, headers={"Authorization": "Bearer bob"}
        ).status_code
        for _ in range(300)
    ]
    assert 429 in statuses  # bob hit his daily budget...
    spent = sum(service.ledger.spent.values())
    assert spent < DAILY_BUDGET_USD + 0.01  # ...and overshot by at most one call
    other = client.post(
        "/ask", json={"text": "hi"}, headers={"Authorization": "Bearer carol"}
    )
    assert other.status_code == 200  # ...and carol is unaffected


def test_missing_token_is_rejected():
    r = TestClient(service.app).post("/ask", json={"text": "hi"})
    assert r.status_code == 401
```

Run `uv add "fastapi[standard]" pytest` and then `uv run pytest -q`. All four pass. Now make sure they can fail, the habit from Testing with pytest: change the log line to include `body.text`, and add a `GET /admin/usage` route without the user dependency. Two tests go red, each naming the problem. `dependency_calls` walks FastAPI's own record of each route's dependencies, so it also catches auth that's missing from a nested dependency. Each fake call costs $0.0025 at these prices, so bob hits his 50-cent budget after 200 requests.

Add a test like these for each row of your review that code can check, and your prompt-injection cases to the eval set, as in Break Your Own Agent. Then CI enforces the review.

### Writing SECURITY.md

The document itself should be short and specific. Start with a paragraph describing the system: what it does, who can use it, what data and tools it touches. Then a table with one row per OWASP item, for both lists if you have an agent:

```markdown
| ID | Applies? | Mitigation | Evidence |
| --- | --- | --- | --- |
| LLM01 / ASI01 | Yes: reads customer emails | Planner never reads email bodies; send needs approval | `tests/test_gate.py`; 12 injection cases in `evals/`, 0/36 succeeded |
| LLM08 | Yes: per-user documents | Vector search filters by `owner_id` in SQL | `test_retrieval_is_scoped_to_owner` |
| LLM10 | Yes: public demo | Login, 5 req/min, $0.50/user/day, $20/month provider limit | `test_budget_stops_a_user_but_not_others`; console screenshot |
| LLM04 | No: we don't fine-tune, and only admins add documents | n/a | Upload route is admin-only, `test_every_route_requires_login` |
```

Add the extra rows this lesson covered (secrets, dependencies, logs) if they don't fit under an OWASP ID; they map to LLM02 and LLM03. End with **residual risks** and a **reporting** line saying how someone should report a vulnerability to you. GitHub shows a file named `SECURITY.md` in the repo's security tab, so that last line is where security researchers will look.

"No" is a fine answer, with a reason. Don't mark a row "Yes" with a mitigation you haven't tested. Write "partly" and say what's missing.

### On other providers

The review itself is provider-neutral: the OWASP lists, secrets handling, dependency checks, auth tests and output handling are identical whichever model you call. What changes is the shape of usage reporting and the name of the output cap. With OpenAI's Chat Completions API, the cap is `max_completion_tokens`, and usage comes back as `usage.prompt_tokens` and `usage.completion_tokens`, so map them before charging the ledger. Remember that cached and reasoning tokens are reported differently by each provider, as Agent Cost and Latency explained, so check how yours counts them before you trust a dollar figure. Every major provider has a console spend limit or project budget; set one wherever you have a key. OpenAI's [safety best practices](https://platform.openai.com/docs/guides/safety-best-practices) recommend the same layers this lesson does, such as rate limits, input length limits and identifying users. With an open model served locally through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), there's no bill to drain, but the same attack becomes denial of service against your GPU, so auth, input limits and per-user limits still apply.

```python
from types import SimpleNamespace

response = client.chat.completions.create(  # an OpenAI() client
    model=MODEL,
    max_completion_tokens=MAX_OUTPUT_TOKENS,
    messages=[{"role": "user", "content": question}],
)
usage = SimpleNamespace(
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens,
)
ledger.charge(user_id, usage)
answer = response.choices[0].message.content
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) and open each of the ten risk pages.
   - For each one, write one sentence on whether it applies to an agent you've built. Read the prevention sections of [LLM05 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/), [LLM03 Supply Chain](https://genai.owasp.org/llmrisk/llm032025-supply-chain/) and [LLM10 Unbounded Consumption](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/) closely, since this lesson introduced them.
1. Revisit the [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) and map each of its risks onto the LLM list, noting which ones the LLM list doesn't cover.
1. Read the OWASP [Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), the "Secret Lifecycle" section (creation, rotation, revocation) and the section on CI/CD, and the "Data to exclude" section of the [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).
   - Then read GitHub's [About push protection](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection) and check that it's on for your public repos.
1. Reread Simon Willison's [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) and check whether any agent you've built combines all three ingredients.
1. Practice: write a security review for your Workflow Automation Agent.
   - Add `SECURITY.md` with a system description, one row per OWASP LLM Top 10 item (and the agentic IDs that apply), residual risks and a reporting line.
   - Add gitleaks to your pre-commit hooks and scan the repo's history. Add `uv lock --check` and the pip-audit step to CI, and a `.github/dependabot.yml` for `uv` and `github-actions` using GitHub's [Dependabot options reference](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file).
   - Adapt `test_security.py` to the agent's API: the route test, a log and span test with a canary (read your `SPANS_FILE` too), and a per-user budget test.
   - Add at least three new attack prompts to the agent's eval set, and record whether they succeed.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What three things does a security review write down for each risk, and why is "we told the model not to" not enough?](#what-a-security-review-is)
- [Why should a multi-user RAG app filter by owner inside the vector search rather than after it?](#the-owasp-checklist)
- [What should you do, in order, when an API key leaks?](#secrets)
- [What is slopsquatting, and what habit defends against it?](#dependencies-and-the-supply-chain)
- [Why isn't a per-user request rate limit enough to prevent denial of wallet?](#denial-of-wallet)
- [Where can model output cause harm besides the browser, and what's the general fix?](#output-handling)
- [How can a test catch a route that someone forgot to protect with a login?](#tests-that-keep-the-review-true)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Mitigating jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks) in the Claude docs gives concrete techniques such as harmlessness screens and input validation.
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) is a good reminder that the simplest design is usually the easiest one to secure.
- The [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) covers the web API risks around your model calls, such as broken authorization and unrestricted resource consumption.
- [We Have a Package for You!](https://arxiv.org/abs/2406.10279) is the study behind the package hallucination numbers in this lesson, with the mitigations the authors tested.
- [pip-audit](https://github.com/pypa/pip-audit) and [Gitleaks](https://github.com/gitleaks/gitleaks) both have READMEs that show their CI setups and options for ignoring a finding you've judged safe.
