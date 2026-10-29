### Introduction

A chatbot reply takes a few seconds. An agent run can take minutes or hours: dozens of model calls, tools that hit real APIs, maybe a pause while a person signs off on something. The longer a run lasts, the more likely something kills it partway through.

When that happens, a plain agent loop loses everything it held in memory. Running it again starts from step 1, pays for every model call a second time and, worst of all, may repeat actions that already changed the world: a second refund, a second email to the customer. **Durable execution** is the fix. Each step's result is saved as soon as the step finishes, so a run that dies can carry on from where it stopped. In this lesson you'll build that by hand with a database table, make side effects safe to repeat, survive a human-approval pause, and then meet the engines that do all of this for you.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why agent runs fail midway, and the difference between restarting and resuming.
- Checkpointing each step's result in a step log.
- A hand-rolled durable agent loop with the database as the step log.
- Idempotency keys for tool calls with side effects.
- Retries per step, and pauses for human approval that survive a restart.
- Durable execution engines and how they fit Python.
- When a job queue plus a step log is all you need.

### Why agent runs die midway

Plenty of things can stop a run between its first step and its last:

- **Crashes.** A bug in a tool, or a worker killed for using too much memory.
- **Deploys.** Shipping new code stops the old worker processes, however healthy the runs inside them were.
- **Timeouts.** arq's `job_timeout` from Job Queues and Workers ends a job that runs too long, and long agent runs do.
- **Rate limits and outages.** A `429` or `529` can outlast the retries you set up in Timeouts, Retries and Rate Limits.
- **Waiting on people.** An approval might take hours. Nobody keeps a process sitting in memory overnight for that, and the next deploy would kill it anyway.

A 30-minute run on a team that deploys ten times a day will regularly get cut off. "The process might die mid-run" isn't an edge case. It's normal operating conditions.

### Restart or resume

**Restart** means running the whole thing again from the goal. For a short, read-only run that's fine. For long runs it's bad three ways: you pay again for every model call, the model may take a different path the second time, and every **side effect** (anything that changes the world outside your program, like a payment, an email or a write to someone else's system) happens again.

**Resume** means carrying on from the last step that finished. That needs every finished step's result written somewhere that outlives the process. Saving progress like this is called **checkpointing**, and the saved record of finished steps is a **step log**.

You learned in The Agent Loop that an agent's whole state is its message list. If you save every model reply and every tool result as it happens, you can rebuild that list at any time. A resumed run walks the loop from the top, but finished steps return their saved results instantly. When it reaches the first step with no saved result, it's back where it died, and carries on for real.

You've seen half of this before: in Agent Tracing and Debugging, `rebuild_messages` rebuilt the history from a trace to replay one step. A trace records what happened for a person to read; a step log records it for the program to *reuse*. Long-Running Agents works at a different level, with notes the model writes for its own future sessions. The two fit together: progress files help the model find its place in a big task, and a step log makes sure the code never loses or repeats a step.

### The step log

The step log is one table: "in run R, the step named K finished, and here is its output." Postgres is the default database from Core on, so that's where it goes in production. The code uses SQLAlchemy, the library underneath SQLModel, so the same file also runs on a local SQLite file while you learn. Install with `uv add anthropic python-dotenv sqlalchemy`, plus `psycopg[binary]` for Postgres. Save this as `store.py`:

```python
# store.py: a step log in the database, so a run can pick up where it stopped
import json
import os

from sqlalchemy import create_engine, text

engine = create_engine(os.environ.get("DATABASE_URL", "sqlite:///runs.db"))

SCHEMA = [  # in a real app these come from an Alembic migration
    """CREATE TABLE IF NOT EXISTS runs (
         id TEXT PRIMARY KEY, goal TEXT NOT NULL,
         status TEXT NOT NULL DEFAULT 'running', note TEXT)""",
    """CREATE TABLE IF NOT EXISTS steps (
         run_id TEXT NOT NULL REFERENCES runs(id), key TEXT NOT NULL,
         output TEXT NOT NULL, PRIMARY KEY (run_id, key))""",
    """CREATE TABLE IF NOT EXISTS approvals (
         run_id TEXT NOT NULL REFERENCES runs(id), key TEXT NOT NULL,
         approved BOOLEAN NOT NULL, PRIMARY KEY (run_id, key))""",
]


def init_db() -> None:
    with engine.begin() as conn:
        for sql in SCHEMA:
            conn.execute(text(sql))


def sql(query: str, **params):
    with engine.begin() as conn:  # one transaction per call: committed, or not at all
        result = conn.execute(text(query), params)
        return result.mappings().first() if result.returns_rows else None


def start_run(run_id: str, goal: str) -> None:
    sql("INSERT INTO runs (id, goal) VALUES (:id, :goal) ON CONFLICT (id) DO NOTHING",
        id=run_id, goal=goal)


def set_status(run_id: str, status: str, note: str | None = None) -> None:
    sql("UPDATE runs SET status = :s, note = :n WHERE id = :id", s=status, n=note, id=run_id)


def step(run_id: str, key: str, fn):
    """Run fn() once per (run_id, key). Every later call returns the saved output."""
    row = sql("SELECT output FROM steps WHERE run_id = :r AND key = :k", r=run_id, k=key)
    if row is not None:
        return json.loads(row["output"])          # done in an earlier attempt: skip it
    output = fn()                                 # not done yet: do it now...
    sql("INSERT INTO steps (run_id, key, output) VALUES (:r, :k, :o) "
        "ON CONFLICT (run_id, key) DO NOTHING",   # ...and checkpoint the result
        r=run_id, k=key, o=json.dumps(output))
    return output


def decision(run_id: str, key: str) -> bool | None:
    row = sql("SELECT approved FROM approvals WHERE run_id = :r AND key = :k", r=run_id, k=key)
    return None if row is None else bool(row["approved"])


def decide(run_id: str, key: str, approved: bool) -> None:
    sql("INSERT INTO approvals (run_id, key, approved) VALUES (:r, :k, :a) "
        "ON CONFLICT (run_id, key) DO NOTHING", r=run_id, k=key, a=approved)
```

The heart is `step`. If the log already has a row for this run and key, it returns the saved output without calling the function. Otherwise it calls the function, saves the output and returns it. The `runs` table holds each run's goal and status, and `approvals` is for human sign-off. In a real app these tables come from an Alembic migration.

Two details matter. **Outputs are JSON**, so anything a step returns must survive `json.dumps`; that's why the agent stores model replies as dictionaries, not SDK objects. And **step keys must be the same on every attempt**, or a resumed run can't find its old results. Model calls are named by position (`model-0`, `model-1`) and tool calls by the ID the model gave them, which lives in the saved reply, so it's identical after a resume. A key built from a timestamp would break this.

### A durable agent loop

The agent handles refund requests: it looks up an order, issues a refund (only with a human's approval) and emails the customer. The payments and email services are fakes. Save this as `services.py`:

```python
# services.py: stand-ins for a payments API and an email API
import json
import uuid
from pathlib import Path

ORDERS = {"A100": {"email": "ada@example.com", "total": 42.00, "note": "arrived broken"}}
LEDGER = Path("provider.json")   # what the "provider" remembers, on its side


def _provider(kind: str, idempotency_key: str, payload: dict) -> str:
    """Like Stripe: the same key twice returns the first result instead of acting twice."""
    seen = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    if idempotency_key in seen:
        return seen[idempotency_key]["id"]
    record_id = f"{kind}_{uuid.uuid4().hex[:8]}"
    seen[idempotency_key] = {"id": record_id, "kind": kind, **payload}
    LEDGER.write_text(json.dumps(seen, indent=2))
    print(f"    [provider] {kind} {payload}")      # this line is the real-world side effect
    return record_id


def lookup_order(order_id: str) -> str:
    order = ORDERS.get(order_id)
    return json.dumps(order) if order else f"No order {order_id}. Known orders: {list(ORDERS)}"


def issue_refund(order_id: str, amount: float, idempotency_key: str) -> str:
    refund_id = _provider("refund", idempotency_key, {"order": order_id, "amount": amount})
    return f"Refund {refund_id} issued for ${amount:.2f}."


def send_email(to: str, body: str, idempotency_key: str) -> str:
    email_id = _provider("email", idempotency_key, {"to": to, "chars": len(body)})
    return f"Email {email_id} sent to {to}."
```

Like a real payment API, `_provider` remembers every **idempotency key** it has seen and returns the first result when a key repeats. `provider.json` stands in for the provider's own servers.

The loop is the one from The Agent Loop with two changes: every model call and tool call goes through `store.step`, and a tool that needs approval can pause the run. Save this as `agent.py`:

```python
# agent.py: an agent loop that checkpoints every step, so it resumes instead of restarting
import os
import sys

import anthropic
from dotenv import load_dotenv

import services
import store

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
MAX_STEPS = 10
CRASH_AT = int(os.environ.get("CRASH_AT", "-1"))   # for practice: die after this model step
client = anthropic.Anthropic(max_retries=3)        # the SDK retries 429s and 5xx inside a step

def schema(**props: str) -> dict:
    return {"type": "object", "required": list(props),
            "properties": {name: {"type": kind} for name, kind in props.items()}}

TOOLS = [
    {"name": "lookup_order", "description": "Get an order's email, total and note.",
     "input_schema": schema(order_id="string")},
    {"name": "issue_refund", "description": "Refund an order. A human must approve it.",
     "input_schema": schema(order_id="string", amount="number")},
    {"name": "send_email", "description": "Email a customer.",
     "input_schema": schema(to="string", body="string")},
]
FUNCS = {"lookup_order": services.lookup_order, "issue_refund": services.issue_refund,
         "send_email": services.send_email}
SIDE_EFFECTS = {"issue_refund", "send_email"}      # these change the world outside our database
NEEDS_APPROVAL = {"issue_refund"}

class WaitingForApproval(Exception):
    pass

def call_model(messages: list) -> dict:
    response = client.messages.create(model=MODEL, max_tokens=16000, tools=TOOLS, messages=messages)
    return {"stop_reason": response.stop_reason,   # plain JSON, so it fits in the step log
            "content": [b.model_dump(mode="json", exclude_none=True) for b in response.content]}

def run_tool(run_id: str, call: dict) -> str:
    name, args = call["name"], dict(call["input"])
    if name in NEEDS_APPROVAL:
        approved = store.decision(run_id, call["id"])
        if approved is None:
            raise WaitingForApproval(call["id"])    # stop here; nothing is saved for this step
        if not approved:
            return "A human declined this action. Do not try it again."
    if name in SIDE_EFFECTS:
        args["idempotency_key"] = f"{run_id}:{call['id']}"   # same call, same key, every attempt
    return FUNCS[name](**args)

def run_agent(run_id: str) -> None:
    run = store.sql("SELECT goal, status FROM runs WHERE id = :id", id=run_id)
    if run["status"] in ("done", "failed"):
        return print(f"{run_id} is already {run['status']}.")
    store.set_status(run_id, "running")
    messages = [{"role": "user", "content": run["goal"]}]
    for i in range(MAX_STEPS):
        reply = store.step(run_id, f"model-{i}", lambda: call_model(messages))
        messages.append({"role": "assistant", "content": reply["content"]})
        if i == CRASH_AT:
            os._exit(1)                             # like a deploy or OOM kill: no cleanup at all
        if reply["stop_reason"] == "end_turn":
            answer = "".join(b["text"] for b in reply["content"] if b["type"] == "text")
            store.set_status(run_id, "done", answer)
            return print(answer)
        if reply["stop_reason"] != "tool_use":
            return store.set_status(run_id, "failed", f"stop_reason={reply['stop_reason']}")
        results = []
        for call in (b for b in reply["content"] if b["type"] == "tool_use"):
            try:
                output = store.step(run_id, f"tool-{call['id']}", lambda call=call: run_tool(run_id, call))
            except WaitingForApproval:
                store.set_status(run_id, "waiting", f"approve {call['id']}: {call['input']}")
                return print(f"Paused. Approve with: python agent.py approve {run_id} {call['id']}")
            results.append({"type": "tool_result", "tool_use_id": call["id"], "content": output})
        messages.append({"role": "user", "content": results})
    store.set_status(run_id, "failed", f"hit the {MAX_STEPS}-step limit")

if __name__ == "__main__":
    store.init_db()
    command, run_id, *rest = sys.argv[1:]
    if command == "start":
        store.start_run(run_id, rest[0])
    elif command in ("approve", "deny"):
        store.decide(run_id, rest[0], approved=command == "approve")
    run_agent(run_id)                               # "resume" is just running it again
```

What changed from the plain loop:

- **`call_model` returns plain JSON.** `model_dump(mode="json", exclude_none=True)` turns each content block into a dictionary the log can store and the API accepts back.
- **The message list is rebuilt, not saved.** On a resume, the early `store.step` calls return saved results, so the list grows back exactly as it was. Because history is only ever appended to, Claude's rule that earlier thinking blocks must not change (a Claude feature; other providers have their own rules for replaying reasoning) is respected too.
- **Every exit sets a status**: `done`, `failed` or `waiting`, with a `note` saying why.
- **Resuming is just running it again.** There's no separate recovery path, so the recovery code is tested every time the agent runs.

Try it. Put `ANTHROPIC_API_KEY` in `.env` and run:

```bash
CRASH_AT=1 uv run agent.py start run-1 "Order A100 arrived broken. Refund it in full and email the customer."
uv run agent.py resume run-1
uv run agent.py approve run-1 toolu_...   # paste the ID it printed
```

The first command dies right after its second model call; `os._exit` skips all cleanup, like an out-of-memory kill. The second resumes: the first two model calls and the order lookup come from the log, with no new API calls, and the run pauses at the refund. The third records your approval and resumes; the refund and email each happen once and the answer prints. `sqlite3 runs.db "SELECT key FROM steps"` shows every checkpoint.

<div class="lesson-note lesson-note--warning" markdown="1">

#### There is still a gap

`step` runs the function, *then* saves the result. If the process dies between those two lines, the step ran but the log doesn't know, so the resume does it again. No checkpointing can close this gap alone, because your database and the outside world can't be updated in one transaction. The next section is how you live with it.

</div>

### Side effects and idempotency keys

Because of that gap, any tool might run twice. For `lookup_order` that's harmless; for `issue_refund` it's a double refund. The fix is the one from the end of Job Queues and Workers: give the outside service an **idempotency key**, a unique name for this one action, and let it refuse to do the same action twice. Stripe, for example, takes an `Idempotency-Key` header and answers a repeat with the saved result of the first request.

The key must be **the same on every retry of the same action** and **different for different actions**. `run_tool` builds it from the run ID and the tool call's ID. A resume produces the same key, while a genuinely new refund later in the run gets a new tool call ID and a new key. Test it: delete the refund's `tool-...` row from `steps` and resume. The tool runs again, but no `[provider] refund` line prints, because the provider already knows the key.

When a service doesn't accept keys, **check before you act** ("is there already a refund for A100?"), or **record intent first** (write "about to send email X", send, then mark it sent, so a crash leaves a visible half-done step for a human), or design the tool to **set** a state ("mark order refunded") rather than **change** one ("add $42"), since setting is safe to repeat.

### Retries belong to steps

If step 31 hits a `429`, retry step 31, not the whole run. Here the client has `max_retries=3`, so the SDK retries rate limits, server errors and dropped connections inside `call_model`, as in Timeouts, Retries and Rate Limits. The log only records a step once it succeeds.

If a step still fails, the exception ends the process and the run stays `running`. Nothing is lost: the job queue retries the job, and the resume only reruns the failed step. In arq, `process_job` becomes a call to `run_agent(run_id)`, and arq's limited retries become cheap resumes. Keep a limit, though. A step that fails the same way every time needs a human, so mark the run `failed` with the error. And don't stack retry loops: if you add tenacity, set the SDK's `max_retries=0`.

### Pausing for a human

Waiting for a person inside a running process doesn't work: the wait might be hours, and any restart loses the run. A durable pause stops the run completely, and the decision arrives later as data.

`run_tool` checks the `approvals` table before `issue_refund`. With no decision yet, it raises `WaitingForApproval`; the loop marks the run `waiting` and returns. No process runs while it waits, so a deploy can't hurt it. When a person approves (here with `approve`; in a real app, a button that writes the same row), the run resumes, everything before the refund comes from the log, and the check now passes. A denial becomes a clear tool result the model can act on. The decision is checked outside `store.step`, so the step's output is only saved once the tool really ran. The Safety section covers approval design in depth.

### Keep the workflow deterministic

Resuming expects finished steps to come up in the same order with the same keys. That only holds if the code *between* steps makes the same decisions every time. This property is called **determinism**: given the same step outputs, the code takes the same path.

So anything that varies goes *inside* a step, where its result is saved: the current time, random numbers and new IDs, reads of anything that might change, and every model and tool call. Write `if datetime.now().hour > 17: skip_email()` between steps, and a run that crashed at 5:59 p.m. and resumed at 6:01 p.m. takes a different path whose keys don't match the log. Every durable execution engine has this rule. The same goes for deploys: if new code asks for steps in a different order, in-flight runs can't resume cleanly. Let them finish on the old version, or only add steps at the end.

### Durable execution engines

**Durable execution engines** sell everything you just built: you write ordinary-looking functions, and the engine records each step and resumes after failures. The main ones, as of late 2026:

| Engine | How it runs | License | Fit for Python |
| --- | --- | --- | --- |
| **DBOS** | A library in your app; step log in Postgres (SQLite in development). No extra server. | MIT | Decorators on plain functions; closest to what you built. |
| **Temporal** | A Temporal server stores the history; your workers run the code. | MIT; paid cloud optional | Mature SDK; the most battle-tested, and the most moving parts. |
| **Restate** | A server your services register with. | Server source-available (BSL); SDKs open | Python SDK for durable handlers. |
| **Inngest** | An Inngest server calls your functions over HTTP and keeps the state. | Server source-available (SSPL, later Apache 2.0); free cloud tier | Python SDK with step functions. |
| **LangGraph checkpointers** | Save a LangGraph graph's state after each step, to Postgres, SQLite or memory. | MIT | Only for LangGraph agents; see LangGraph and the Wider Ecosystem. |

**Source-available** means you may read and self-host the code, but the license limits selling it as a hosted service. All five are free for learning and your own projects. An engine handles edge cases you haven't hit yet (timers that survive restarts, child workflows, dashboards, restarting a run from a chosen step) in exchange for a dependency, its rules and, for Temporal, Restate and Inngest, another server to run.

### A short look at DBOS

DBOS is the same design as yours, packaged as a library. Install it with `uv add dbos`. This version reuses the tools and `call_model` from `agent.py`:

```python
# dbos_agent.py: the same agent on DBOS, which keeps the step log for you
import os
import sys

from dbos import DBOS, SetWorkflowID

import agent  # reuse TOOLS, FUNCS, call_model and the tool sets from agent.py

DBOS(config={
    "name": "refund-agent",
    "system_database_url": os.environ.get("DBOS_SYSTEM_DATABASE_URL", "sqlite:///dbos.sqlite"),
})

@DBOS.step(retries_allowed=True, max_attempts=4, backoff_rate=2.0)   # retries per step
def model_step(messages: list) -> dict:
    return agent.call_model(messages)

@DBOS.step()
def tool_step(call: dict) -> str:
    args = dict(call["input"])
    if call["name"] in agent.SIDE_EFFECTS:
        args["idempotency_key"] = f"{DBOS.workflow_id}:{call['id']}"
    return agent.FUNCS[call["name"]](**args)

@DBOS.workflow()
def refund_agent(goal: str) -> str:
    messages = [{"role": "user", "content": goal}]
    for _ in range(agent.MAX_STEPS):
        reply = model_step(messages)                 # checkpointed: never re-sent after a crash
        messages.append({"role": "assistant", "content": reply["content"]})
        if reply["stop_reason"] != "tool_use":
            return "".join(b.get("text", "") for b in reply["content"])
        results = []
        for call in (b for b in reply["content"] if b["type"] == "tool_use"):
            output = "A human declined this action. Do not try it again."
            if call["name"] not in agent.NEEDS_APPROVAL:
                output = tool_step(call)
            else:
                print(f"Waiting: python dbos_agent.py approve {DBOS.workflow_id} {call['id']}")
                if DBOS.recv(topic=call["id"], timeout_seconds=7 * 24 * 3600):  # durable wait
                    output = tool_step(call)
            results.append({"type": "tool_result", "tool_use_id": call["id"], "content": output})
        messages.append({"role": "user", "content": results})
    return "Stopped at the step limit."

if __name__ == "__main__":
    DBOS.launch()                    # also restarts any workflow that was cut off mid-run
    command, run_id, *rest = sys.argv[1:]
    if command == "start":
        with SetWorkflowID(run_id):  # the run ID doubles as an idempotency key for the run
            DBOS.start_workflow(refund_agent, rest[0])
    elif command == "approve":
        DBOS.send(run_id, True, topic=rest[0])
    print(DBOS.retrieve_workflow(run_id).get_result())   # wait for the run to finish
```

Map it onto what you built:

- **`@DBOS.step()`** is `store.step`, and `retries_allowed=True` gives it retries with backoff.
- **`@DBOS.workflow()`** is `run_agent`, and it must be deterministic.
- **`SetWorkflowID(run_id)`** names the run; starting an ID that already exists doesn't start a second copy.
- **`DBOS.recv`** is the approval pause. `DBOS.send` from another process delivers the message, which is stored in the database, so it waits for the workflow even if nothing is running.
- **`DBOS.launch()`** finds interrupted workflows and resumes them from their last finished step. That replaces your `resume` command.

Run `start`, press Ctrl+C while it waits for approval, then run `approve` with the printed ID: the new process recovers the workflow, skips finished model calls and completes. Set `DBOS_SYSTEM_DATABASE_URL` to a Postgres URL for production. Notice `tool_step` still passes an idempotency key. DBOS has the same gap between "step ran" and "step recorded" that you do; every engine does. Engines promise each step runs **at least once** and finished steps aren't repeated. Making a payment happen exactly once is still your job.

### When a queue and a step log are enough

Often you don't need an engine. If runs are short and read-only, just retry the whole job. If the agent is a loop like this one, with a few tools and an occasional approval, around 150 lines you understand and can test with fakes is fine, and if you already run Postgres and a queue, the step log is one more table.

Adopt an engine when your code starts growing engine-shaped features: timers that fire days later, runs that fan out into child runs and wait for all of them, many workflow types needing the same recovery logic, or an operations team that needs to inspect, cancel and restart thousands of runs. At that point you'd be rebuilding Temporal or DBOS, badly. Either way, having built it once by hand, you'll recognize what an engine does underneath.

### On other providers

Durable execution barely depends on the model provider. The step log, step keys, idempotency keys, durable pauses and every engine above wrap *any* function, so only `call_model` changes. With OpenAI's Chat Completions API, or an open model through Ollama's OpenAI-compatible endpoint, the reply is a `message` with a `tool_calls` list, the stop signal is `finish_reason == "tool_calls"`, and tool results go back as `role: "tool"` messages. Store the reply as plain JSON, as before:

```python
def call_model(messages: list) -> dict:          # OpenAI SDK, or Ollama via base_url
    response = client.chat.completions.create(model=MODEL, tools=TOOLS, messages=messages)
    choice = response.choices[0]
    return {"finish_reason": choice.finish_reason,
            "message": choice.message.model_dump(mode="json", exclude_none=True)}
```

See OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) for the message shapes, and [Ollama's OpenAI compatibility page](https://docs.ollama.com/api/openai-compatibility) to run the same code on a free local model. One thing to check: if your provider's tool call IDs aren't unique across a run, build step keys and idempotency keys from the step number and the call's position instead.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the DBOS [Workflows tutorial](https://docs.dbos.dev/python/tutorials/workflow-tutorial) and [Steps tutorial](https://docs.dbos.dev/python/tutorials/step-tutorial). They are short and show a real engine's version of this lesson's ideas.
   - In the Workflows tutorial, read "Workflow IDs and Idempotency," "Determinism" and "Workflow Guarantees," and compare the guarantees with what your `store.step` promises.
   - In the Steps tutorial, read about retries and note how `should_retry` skips retries for errors that will never succeed.
1. Read Stripe's [Idempotent requests](https://docs.stripe.com/api/idempotent_requests) to see how a real payments API handles a repeated key, then Brandur Leach's [Implementing Stripe-like Idempotency Keys in Postgres](https://brandur.org/idempotency-keys) for the server side.
   - In Brandur's post, focus on "atomic phases" and "recovery points." They are a step log by another name.
1. Read Temporal's [The definitive guide to Durable Execution](https://temporal.io/blog/what-is-durable-execution) for the big picture, then skim LangGraph's [Durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution) page.
   - Notice LangGraph's advice to wrap side effects and non-deterministic operations in tasks. It's this lesson's determinism rule again.
1. Practice: build the durable agent from this lesson, crash it and prove it resumed.
   - Run it with `CRASH_AT=0`, `1` and `2`, resuming each time. Log each model call and show that none happened twice.
   - Write a pytest test with a fake client, as in Testing with pytest: the fake raises an exception on its third call the first time, the test resumes the run, and it asserts the fake was called exactly once per model step and that `provider.json` holds one refund.
   - Delete the refund's `tool-...` row from `steps` and resume. Confirm there was no second refund, and explain why in two sentences.
1. Practice: put the agent behind the job queue from Job Queues and Workers. Make `process_job` call `run_agent`, add an `approve` route that writes to `approvals` and resubmits the job, and check that a `waiting` run isn't treated as a failure and retried.
1. Optional: port the agent to DBOS with the example above, point `DBOS_SYSTEM_DATABASE_URL` at your Compose Postgres, and write a short comparison: lines of code, what you no longer had to write, and what you still did.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between restarting and resuming a run, and why does resuming need a step log?](#restart-or-resume)
- [Why must step keys be the same on every attempt, and how does the example choose them?](#the-step-log)
- [Why can a tool still run twice even with checkpointing, and how does an idempotency key keep that safe?](#side-effects-and-idempotency-keys)
- [Why should retries happen per step rather than per run?](#retries-belong-to-steps)
- [How can a run wait hours for a human's approval without a process running the whole time?](#pausing-for-a-human)
- [What does it mean for workflow code to be deterministic, and what has to go inside a step because of it?](#keep-the-workflow-deterministic)
- [When is a job queue plus a step log enough, and when should you adopt a durable execution engine?](#when-a-queue-and-a-step-log-are-enough)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [DBOS architecture](https://docs.dbos.dev/architecture) explains how DBOS checkpoints workflows in Postgres and recovers them without a separate server.
- [Understanding Temporal](https://docs.temporal.io/evaluate/understanding-temporal) is Temporal's overview of its server, workers and event history, useful if your team is weighing it up.
- The [Temporal Python getting-started course](https://learn.temporal.io/getting_started/python/) runs a Temporal server and a first workflow locally.
- [Restate's durable execution concepts](https://docs.restate.dev/concepts/durable_execution) and [Inngest's how functions are executed](https://www.inngest.com/docs/learn/how-functions-are-executed) show two designs built around servers that call your code.
- LangGraph's [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) page covers checkpointers and resuming a graph after an interrupt, ahead of the LangGraph lesson.
