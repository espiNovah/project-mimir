### Introduction

In Measuring Quality and Evals in Practice you tested single model calls: given this input, is the output good? Agents are harder. They take many steps, call tools that change the world, and can reach the right answer by a wrong path, or the wrong answer through steps that each looked fine. They are also not deterministic, so one passing run proves little.

This lesson covers the pieces of an agent eval: tasks, trials, graders, transcripts and environment checks, and the metrics that tell you whether an agent is reliable enough to ship. You'll build a small eval that checks what an agent actually *did* to a database, runs each task several times, and reports pass^k. The Agent Loop From Scratch project at the end of this section asks for exactly this kind of eval.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a task, a trial, a grader and a transcript are in agent evaluation.
- Grading the outcome versus grading the path.
- Checking the final state of the environment.
- Code-based, model-based and human graders for agents.
- Why you run each task many times.
- pass@k versus pass^k.
- Tracking cost and steps alongside success.

### Tasks, trials and transcripts

Agent evals need a few words that single-call evals could skip.

- A **task** is an input plus a way to judge success. "Close every refund ticket with a note to the customer," together with a check that the right tickets are closed, is one task.
- A **trial** is one run of the agent on a task. Because the agent behaves a little differently each time, you run several trials of the same task.
- The **environment** is the world the agent acts on: a database, a folder of files, a fake inbox, a test repository. Each trial needs its own fresh copy, so one trial can't leave a mess for the next.
- The **transcript** (or trace) is the full record of a trial: every message, tool call and tool result. In Agent Tracing and Debugging you learned to record these. Here they become evidence.
- The **outcome** is the state of the environment when the trial ends. Did the row change? Does the file exist? Do the tests pass?
- A **grader** is the code, model or person that looks at the outcome, the transcript, or both, and returns a verdict.

You need all of these to evaluate an agent and to debug it. A pass/fail number with no transcript behind it tells you something broke but not why. A pile of transcripts with no grader tells you a story but not a score.

### Grade the outcome in the environment

The strongest check looks at what the agent actually changed. Is the ticket closed? Is the row in the database? Do the tests pass? This is called an **environment-state check**, and it should be the first grader you write for any agent that has tools that change things.

Why not just read the agent's final message? Because agents claim success they didn't achieve. A model that says "Done! I've closed both refund tickets" may have closed one, closed the wrong one, or never called the tool at all. An LLM judge reading that final message would likely be fooled too, since the message sounds confident and complete. The database can't be fooled. An agent that says "Done!" without doing it should fail.

Environment checks also free the agent to find its own path. Maybe it searches for "refund" and closes both tickets. Maybe it lists every ticket first and picks the right ones. If the final state is correct, both paths pass.

Good state checks test two things:

1. **The thing that should have changed did change**, in the right way. The refund tickets are closed *and* each has a note.
2. **The things that should not have changed didn't.** The password-reset ticket is still open. An agent that "closes every refund ticket" by closing every ticket must fail. This second half is the one beginners forget, and it catches the most dangerous bugs.

### When to grade the path

Some failures only show in the transcript. The final state can look right even when the agent:

- called a tool it was forbidden to use, such as deleting a record and re-creating it instead of updating it;
- skipped a required step, such as asking for approval before sending an email;
- took 40 steps for a 5-step job, which is slow and expensive even if it ends well;
- followed an instruction hidden in a tool result, the prompt-injection failure from the Prompt Injection lesson.

Add checks on the transcript for these. Count tool calls, look for forbidden tool names, check that an approval call came before a send call. But don't demand one exact sequence of steps. There's usually more than one good path, and a grader that insists on yours will fail an agent that found a better one. Check *constraints* on the path (never do X, always do Y before Z, finish within N steps), not the path itself.

### Choosing a grader

The three kinds of graders from Code Checks and LLM-as-Judge apply to agents too, and the rule is the same: use the cheapest grader that works.

- **Code graders** run SQL queries against the environment, check that files exist, run the test suite, or count tool calls in the transcript. They're fast, free and perfectly consistent. Most agent tasks with tools can be graded mostly by code.
- **Model graders** (LLM judges) handle fuzzy qualities: was the note to the customer polite and specific? Did the research summary cover the main points? Like any judge, an agent judge must be checked against your own labels, with TPR and TNR measured, before you trust it.
- **Human graders** are the final reference. You read transcripts, decide pass or fail, and use those labels to check the other two graders. It's slow, so you do it on a sample.

A single task often combines them: a code check on the database state, plus a judge on the tone of the note it wrote.

### A grader that checks the environment

Here's a complete small eval. First, the agent: a support bot with two tools that act on a SQLite database of tickets. It's the same kind of manual loop you wrote in The Agent Loop, with a step limit. Install the SDK with `uv add anthropic` and save this as `agent.py`:

```python
# agent.py: a tiny support agent that works on a SQLite ticket table.
import json
import os

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

TOOLS = [
    {"name": "find_tickets",
     "description": "List open tickets whose subject contains a search term.",
     "input_schema": {"type": "object", "properties": {"term": {"type": "string"}},
                      "required": ["term"]}},
    {"name": "close_ticket",
     "description": "Close one ticket by ID, with a short note to the customer.",
     "input_schema": {"type": "object",
                      "properties": {"ticket_id": {"type": "integer"}, "note": {"type": "string"}},
                      "required": ["ticket_id", "note"]}},
]


def run_tool(db, name, args):
    if name == "find_tickets":
        rows = db.execute("SELECT id, subject FROM tickets WHERE status = 'open' AND subject LIKE ?",
                          (f"%{args['term']}%",)).fetchall()
        return json.dumps([{"id": i, "subject": s} for i, s in rows])
    if name == "close_ticket":
        cur = db.execute("UPDATE tickets SET status = 'closed', note = ? WHERE id = ?",
                         (args["note"], args["ticket_id"]))
        db.commit()
        return "closed" if cur.rowcount else f"error: no ticket {args['ticket_id']}"
    return f"error: unknown tool {name}"


def run_agent(task, db, max_steps=10):
    """Run one trial against db and return the transcript."""
    messages = [{"role": "user", "content": task}]
    for _ in range(max_steps):
        response = client.messages.create(model=MODEL, max_tokens=4000, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            break
        results = [{"type": "tool_result", "tool_use_id": b.id, "content": run_tool(db, b.name, b.input)}
                   for b in response.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    return messages
```

Notice that `run_agent` takes the database as a parameter instead of opening a fixed file. That's the dependency injection habit from Testing with pytest, and it's what lets the eval hand every trial its own fresh environment. Now the eval itself, in `evaluate.py`:

```python
# evaluate.py: run each task N times in a fresh environment and grade the final state.
import sqlite3
from math import comb

from agent import run_agent

SEED = [(1, "Refund for order 1001", "open"), (2, "Password reset loop", "open"),
        (3, "Refund for order 1002", "open"), (4, "Dark mode request", "open")]


def fresh_db():
    db = sqlite3.connect(":memory:")  # 1. a brand-new, throwaway environment per trial
    db.execute("CREATE TABLE tickets (id INTEGER PRIMARY KEY, subject TEXT, status TEXT, note TEXT)")
    db.executemany("INSERT INTO tickets (id, subject, status) VALUES (?, ?, ?)", SEED)
    return db


def grade_close_refunds(db, transcript):
    rows = {i: (status, note) for i, status, note in db.execute("SELECT id, status, note FROM tickets")}
    refunds_done = all(rows[i][0] == "closed" and rows[i][1] for i in (1, 3))  # 2. what should change
    others_untouched = all(rows[i][0] == "open" for i in (2, 4))               # 3. what must not change
    tool_calls = sum(1 for m in transcript if m["role"] == "assistant"
                     for b in m["content"] if b.type == "tool_use")
    return refunds_done and others_untouched and tool_calls <= 6               # 4. a path constraint


TASKS = [{"id": "close-refunds", "grader": grade_close_refunds,
          "prompt": "All pending refunds have been issued. Close every refund ticket "
                    "with a short note telling the customer."}]


def pass_at_k(n, c, k):    # chance that at least one of k trials passes
    return 1 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n, c, k):   # chance that all k trials pass
    return comb(c, k) / comb(n, k)


N, K = 5, 3
for task in TASKS:
    results = []
    for trial in range(N):
        db = fresh_db()
        transcript = run_agent(task["prompt"], db)
        results.append(task["grader"](db, transcript))  # 5. grade the database, not the agent's words
    c = sum(results)
    print(f"{task['id']}: {c}/{N} passed  pass@{K}={pass_at_k(N, c, K):.2f}  pass^{K}={pass_hat_k(N, c, K):.2f}")
```

Run it with `uv run evaluate.py`. Walking through the numbered comments:

1. `fresh_db()` builds the environment from scratch for every trial. SQLite's `:memory:` database is perfect here because it's free and instant to create. With Postgres you'd do the same thing with a throwaway test database or a container; the idea is identical.
1. The grader queries the database for the tickets that should have changed, and checks both the status and that a note exists.
1. It also checks that tickets 2 and 4 are still open. An agent that closes everything fails.
1. One path constraint from the transcript: a job this small shouldn't need more than six tool calls.
1. The grader never reads the agent's final message. "Done!" earns nothing on its own.

The note's *quality* isn't checked. If it matters, add a validated judge on the `note` column, alongside the code checks.

### Run every task several times

Run the script twice and you may get different counts. The model samples its words, so the same task can succeed on one trial and fail on the next: it searches for "Refund" one time and "refund ticket" another, and the second search finds nothing. One passing trial tells you the agent *can* do the task, not that it *will*.

So you run each task several times and count. From Eval Statistics you know a pass rate from five trials has a wide confidence interval: 4 out of 5 is consistent with a true rate anywhere from about 38% to 96%. Five trials are enough to spot a task that's flaky; to compare two versions of an agent you need more tasks, more trials, or both.

### pass@k and pass^k

Two metrics summarize repeated trials, and they answer different questions.

- **pass@k** is the chance that *at least one* of k trials succeeds. It's the right number when someone can pick the best attempt: a coding assistant that offers three suggestions, or a pipeline that runs tests and keeps the first passing patch.
- **pass^k** (read "pass hat k" or "pass power k") is the chance that *all* k trials succeed. It measures consistency. If a customer asks your agent the same thing on three different days, pass^3 is the chance it gets it right all three times.

If an agent succeeds with probability *p* on a single trial, pass^k is roughly *p* to the power k. An agent that succeeds 90% of the time has a pass^3 of about 0.73 and a pass^10 of about 0.35. pass@k moves the other way and climbs toward 1. That's why the two numbers can tell opposite stories about the same agent.

For an agent that acts alone, with nobody picking the best try, pass^k is usually the number that matters, and it drops fast as k grows. The functions in `evaluate.py` use the standard estimates from *n* trials with *c* successes: `comb(c, k) / comb(n, k)` is the chance that k trials drawn from your n are all passes. Run n at least as large as k, and report both n and k next to the number.

### Read the transcripts

Metrics tell you that something broke. Transcripts tell you why. After every eval run, read the failed transcripts, and a few passing ones too, since agents sometimes pass for the wrong reason.

This is the same error analysis you did in Error Analysis and Labeling, applied to runs instead of single answers. Note each failure in a few words ("searched with the wrong term", "closed ticket 2 by mistake", "stopped after one ticket"), group the notes into types, and count them. The most common type tells you what to fix next. Each new failure type you find is also a candidate for a new task, so your eval grows from real mistakes instead of imagined ones.

### Track cost and steps too

Success isn't the only number. For every trial, record the number of steps, the tool calls and the tokens used, all of which your traces already contain. Then report them next to the pass rate.

A prompt change that raises success by 2% while doubling tokens may not be worth it. A model swap that keeps success flat but halves the steps is a real improvement. You'll go deeper into this in Agent Cost and Latency; for now, make sure your eval output has a column for it.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Start with a handful of tasks

You don't need 200 tasks on day one. Five to ten real tasks, each with a state check and run five times, will catch most of the problems in a new agent. Add tasks whenever a transcript shows a new kind of failure.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) in full. It is the main resource for this section and uses the same vocabulary as this lesson.
   - Write down the definitions of task, trial, grader, transcript and outcome in your own words.
   - Work out pass@3 and pass^3 by hand for an agent that succeeds 80% of the time on a task.
1. Read the questions about agents, traces and error analysis in Hamel Husain and Shreya Shankar's [LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/). They show how practitioners turn transcripts into failure categories.
1. Read Hamel Husain's [field guide to rapidly improving AI products](https://hamel.dev/blog/posts/field-guide/), focusing on the parts about looking at your data. It makes the case for reading transcripts better than any metric can.
1. Read the [Inspect agents docs](https://inspect.aisi.org.uk/agents.html) to see how an open-source eval framework runs agents in tasks with scorers. Compare its task, solver and scorer to the task, agent and grader in this lesson.
1. Practice: run the eval from this lesson, then extend it.
   - Add three more tasks to `TASKS`, each with its own state-checking grader. Include one where the right action is to do nothing, such as a request to close a ticket that doesn't exist.
   - Break the agent on purpose (for example, rename `find_tickets` to something unhelpful) and confirm your graders fail it.
   - Take an agent you've built, write five tasks with environment-state checks and run each one five times. Report pass@1, pass@5 and pass^5, and read every failed transcript.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between a task, a trial and a transcript?](#tasks-trials-and-transcripts)
- [Why is checking the environment stronger than reading the agent's final message?](#grade-the-outcome-in-the-environment)
- [What two things should a good state check test?](#grade-the-outcome-in-the-environment)
- [What kinds of failures only show up in the transcript, and why shouldn't you require one exact sequence of steps?](#when-to-grade-the-path)
- [Why does each trial need a fresh environment?](#a-grader-that-checks-the-environment)
- [When is pass@k the right metric, and when is pass^k?](#pass-k-and-pass-k)
- [Why should you report cost and steps next to the success rate?](#track-cost-and-steps-too)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [τ-bench paper](https://arxiv.org/abs/2406.12045) introduced pass^k for agents and shows how fast it falls for real models on customer-service tasks. Its [code is on GitHub](https://github.com/sierra-research/tau-bench). You'll meet benchmarks like it in Evaluating Agents at Scale.
- [Inspect's scorers docs](https://inspect.aisi.org.uk/scorers.html) show many ready-made graders, including model-graded ones, that you can compare with your own.
