### Introduction

Some tasks are too big for one sitting, for a person or an agent. Building a full web app, migrating a codebase or summarizing a library of 40 long documents can take many hours and far more context than any window holds. Compaction helps, but it is not enough on its own: summaries lose detail, and an agent that forgets where it was will redo work or declare victory too early. In this lesson you will learn how **harnesses** (the code and files around an agent) let it work across many sessions, picking up exactly where the last one left off, the way a well-run engineering team hands off between shifts. You will build a small multi-session runner with budgets, a progress file and a rule for handing problems back to a human, and test it without spending a cent.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why long tasks fail even with compaction.
- The harness: the scaffolding around the agent loop.
- Initializer sessions, task lists and progress files.
- The routine every later session follows, and how a run resumes.
- Verifying work before marking it done, and using Git as a record.
- Budgets, and when to hand the task back to a human.
- Testing long runs cheaply with fakes.

### Why long tasks fail

Give an agent a big goal ("summarize all 40 chapters into one report") and a single conversation, and it tends to fail in one of two predictable ways.

**It tries to do everything at once.** It reads chapter after chapter, each tool result piling into the context, until the window fills up or a step limit fires halfway through. The run ends with eleven half-written summaries and no record of which ones are finished. The next attempt starts from zero.

**It stops too early.** After some progress, the model looks at the conversation, sees a lot of activity and a few good summaries, and concludes the job is done. In The Agent Loop you met this as "declaring success too early." On long tasks it is the most common failure of all, because the evidence of what's left is buried far back in the context, or was summarized away by compaction.

Both failures have the same root cause: **there is no shared, written state** that says exactly what the task is, what is finished and what is next. Inside one conversation, the only state is the message list, and on a long task the message list is exactly the thing you can't keep.

### The harness carries the state

A **harness** is everything around the agent loop that you write: the runner that starts sessions, the files the agent reads and writes, the tests that check its work and the rules about how each session begins and ends. The model is stateless; the harness is what makes it act like a persistent worker.

The core idea is to split one huge task into many **sessions**. A session is one fresh conversation, started with an empty message list, that works on a small piece of the task and then ends. Nothing carries over between sessions except files on disk. That sounds like a limitation, but it is the point: each session starts with a clean, small context, and the files are an exact record instead of a lossy summary.

Think of a hospital shift change. The night nurse doesn't remember the day shift; she reads the chart. The chart says what was done, what is pending and what to watch for. Your harness keeps the chart.

### The initializer session

The first session is special. It doesn't try to solve the task. It sets things up so every later session can make progress safely. It typically:

1. Sets up the environment (folders, a project skeleton, a script to run the tests).
1. Breaks the goal into a detailed list of small subtasks, each with a "done" flag, and writes it to a file.
1. Writes a progress file for later sessions to read and append to.
1. Makes a first Git commit, if the work happens in a repository.

The task list should be **structured**, not prose. A JSON file like this one is easy for your code to read and check, and hard for the agent to quietly rewrite into "everything looks fine":

```json
[
  {"id": 1, "description": "Summarize chapter 1 into out/ch01.md (title + summary under 100 words)", "done": false, "attempts": 0},
  {"id": 2, "description": "Summarize chapter 2 into out/ch02.md (title + summary under 100 words)", "done": false, "attempts": 0},
  {"id": 41, "description": "Combine out/*.md into report.md with a table of contents", "done": false, "attempts": 0}
]
```

The progress file is for things a checklist can't hold: decisions, surprises and warnings. Markdown works well, because both you and the model read it easily:

```text
# Progress

## Decisions
- Summaries use the chapter's own title, not a generated one.

## Known problems
- Chapter 17 is mostly a table; summarize the table's conclusion only.

## Session log
(the runner appends one entry per session below)
```

You can have the model write both files in its initializer session, using a structured-output call or its file tools, or you can write them yourself. For tasks where the split is obvious, like "one item per file," generating the list in plain Python is cheaper and more reliable. Either way, read the list before running anything else. A bad plan makes every later session worse.

### The session routine

Every session after the first follows the same routine, and the harness enforces it rather than hoping the model remembers:

1. **Get your bearings.** Read the progress file and the task list (and `git log`, if there is one).
1. **Check that things still work.** Run the tests or the checker. If a previous session left something broken, fixing it is the first job.
1. **Pick one unfinished item.** One, not five. Small steps keep each session well inside its context window.
1. **Do it, then verify it** with a real check.
1. **Leave a clean state.** Update the task list and the progress file, and commit.

Notice that resuming is not a special feature. A run that crashed, ran out of budget or was stopped by you on Friday afternoon resumes on Monday exactly the same way a normal session starts: by reading the files. If the files are always up to date, there is nothing else to recover.

### A multi-session runner

Here is the runner. It doesn't call a model itself. You pass it two functions: `work_on`, which runs one agent session on one task and returns a handoff note and the tokens it used, and `verify`, which checks a task with code. Passing functions in like this is the dependency injection you learned in Testing with pytest, and you'll see why it matters when you test it.

```python
# harness.py: run an agent across many sessions, carrying state in files
import json
import os
from datetime import datetime
from pathlib import Path

STATE = Path("state")
TASKS = STATE / "tasks.json"
PROGRESS = STATE / "PROGRESS.md"
MAX_SESSIONS = 20             # hard stop for the whole run
MAX_TOTAL_TOKENS = 2_000_000  # hard stop on spend, across all sessions
MAX_ATTEMPTS = 3              # tries per task before a human has to look


def save_json(path: Path, data) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, path)                 # atomic, so a crash can't corrupt the checklist


def log(text: str) -> None:
    with PROGRESS.open("a") as f:
        f.write(text + "\n")


def next_task(tasks: list[dict]) -> dict | None:
    for task in tasks:
        if not task["done"] and task["attempts"] < MAX_ATTEMPTS:
            return task
    return None


def run(work_on, verify) -> str:
    """work_on(task, notes) -> (handoff_note, tokens). verify(task) -> bool."""
    total_tokens = 0
    for session in range(1, MAX_SESSIONS + 1):
        tasks = json.loads(TASKS.read_text())          # 1. read state from disk, every time
        task = next_task(tasks)
        if task is None:
            stuck = [t["id"] for t in tasks if not t["done"]]
            if stuck:
                log(f"\n## Needs a human\nTasks {stuck} failed {MAX_ATTEMPTS} times.")
                return f"handed back: {stuck}"
            return "finished"
        if total_tokens >= MAX_TOTAL_TOKENS:
            log("\n## Stopped\nToken budget used up.")
            return "stopped: token budget"

        note, tokens = work_on(task, PROGRESS.read_text())   # 2. one fresh session, one task
        total_tokens += tokens
        task["attempts"] += 1
        task["done"] = verify(task)                    # 3. your code decides "done", not the agent
        save_json(TASKS, tasks)                        # 4. checkpoint before anything else
        status = "DONE" if task["done"] else "NOT DONE"
        log(f"\n## Session {session} ({datetime.now():%Y-%m-%d %H:%M}), "
            f"task {task['id']}: {status}, {tokens} tokens\n{note.strip()}")
    return "stopped: session limit"
```

Walk through the important lines:

- **The task list is re-read from disk at the start of every session.** The loop keeps nothing important in Python variables except a running token total. If the process dies, the files are the truth.
- **`save_json` writes atomically,** the same trick as `memory.py` in Short- and Long-Term Memory. After each session the task list is saved before anything else, so it works as a **checkpoint**: a saved point you can safely restart from.
- **`attempts` is counted per task.** A task that fails verification is retried in a fresh session, which often succeeds because the agent sees the previous session's handoff note explaining what went wrong. After three failures it stops being retried.
- **The handoff note goes into the progress file,** so the next session reads what this one learned. Here the runner appends the note; in Anthropic's write-up the agent edits the progress file itself with its file tools. Both work. Having the runner write the log means a session can't forget to.

And here is a `work_on` that runs a real agent session. It is the loop from The Agent Loop, with the progress notes in the first message and a per-session token budget:

```python
# session.py: one fresh agent session that works on one task
import os

import anthropic
from dotenv import load_dotenv

from tools import TOOLS, run_tool      # your tools from Project: Agent Loop From Scratch

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()
MAX_STEPS = 30
SESSION_TOKEN_BUDGET = 300_000

SYSTEM = """You are one session in a long task that runs over many sessions.
You remember nothing from earlier sessions except the progress notes you are given.
Work only on the task you are given. Check your work before you finish.
End with a short handoff note for the next session: what you did, how you checked it,
and anything that is broken or still unclear. If you are blocked, start the note with BLOCKED."""


def work_on(task: dict, notes: str) -> tuple[str, int]:
    messages = [{"role": "user", "content":
                 f"<progress_notes>\n{notes}\n</progress_notes>\n\n"
                 f"Your task this session: [{task['id']}] {task['description']}"}]
    used = 0
    for _ in range(MAX_STEPS):
        response = client.messages.create(model=MODEL, max_tokens=8000, system=SYSTEM,
                                          tools=TOOLS, messages=messages)
        used += response.usage.input_tokens + response.usage.output_tokens
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text"), used
        if response.stop_reason != "tool_use":
            return f"Session stopped early: {response.stop_reason}", used
        if used > SESSION_TOKEN_BUDGET:
            return "Session ran out of its token budget before finishing.", used
        results = [{"type": "tool_result", "tool_use_id": b.id, "content": run_tool(b.name, b.input)}
                   for b in response.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    return "Session hit its step limit before finishing.", used
```

Put the two together in a few lines: `print(harness.run(session.work_on, verify))`, with a `verify` function for your task (the next section shows one). Notice that `work_on` never edits or trims its conversation. It only appends, then throws the whole thing away when the session ends. That is deliberate: as you saw in Compaction and Context Editing, changing earlier turns invalidates the thinking blocks newer Claude models send back, and some accounts get an error. Starting a fresh session is the cleanest way to reset context. If a single session still grows too long, use the server-side context editing or compaction from that lesson, or strip thinking blocks from any turns your own code edits, rather than quietly rewriting the history here.

### Only verified work counts

The single most important rule in this lesson: **a task is done when your code has checked it, not when the agent says so.** Agents are optimistic. A coding agent will write a feature, glance at it and mark it complete without ever running it. A summarizing agent will claim it wrote 100-word summaries that are actually 300 words.

So write `verify` as real code that checks the result the way a user would:

```python
from pathlib import Path


def verify(task: dict) -> bool:
    """Done means: the file exists, has a title line and a summary under 100 words."""
    if task["id"] == 41:
        return Path("report.md").exists()
    path = Path(f"out/ch{task['id']:02d}.md")
    if not path.exists():
        return False
    title, _, summary = path.read_text().partition("\n")
    return title.startswith("# ") and 0 < len(summary.split()) <= 100
```

For a coding task, `verify` might run `pytest` on that feature's tests, or drive the app end to end. Anthropic's write-up found that agents testing web features only with unit tests often missed bugs a real browser would catch. The closer your check is to what a user experiences, the less your agent can fool itself. Ask the agent to verify its own work too (the system prompt above does), but treat that as a first draft. The harness has the final word.

### Budgets and limits

A long run can spend a lot of money while you're asleep. Put limits at every level, as you did with the step cap in The Agent Loop and the per-run budgets in Agent Cost and Latency:

- **Per session:** a step cap and a token budget, so one confused session can't loop forever.
- **Per task:** a maximum number of attempts, so one impossible item can't eat the whole run.
- **Per run:** a maximum number of sessions and a total token (or dollar) budget.

When a limit fires, stop *gracefully*: save the state, write why you stopped into the progress file and return a clear status. A run that stops cleanly at 60% can be resumed; a run that crashes at 60% may have left a half-written file that the next session trusts.

### When to hand back to a human

A good long-running agent knows when to stop and ask. Hand the task back to a person when:

- **The same item keeps failing.** Three failed attempts usually means the task is ambiguous, the environment is broken or the check itself is wrong. More retries just burn money.
- **The agent says it is blocked.** Missing credentials, a file that doesn't exist, a requirement that contradicts another. The `BLOCKED` convention in the system prompt gives your harness a simple signal to look for.
- **A decision is needed that the agent shouldn't make.** Anything irreversible or costly, such as deleting data, sending email to customers or spending money, should wait for approval. You'll design approval flows properly in Approvals and Permissions.
- **A budget is nearly gone** and the task isn't close to finished.

"Handing back" should mean a clear, specific report, written to the progress file and shown to the user: which items are stuck, what was tried, and what the agent needs. That turns a failed run into a ten-minute fix instead of an afternoon of digging through traces.

### Git as memory and undo

If the agent works inside a Git repository, Git does two jobs for free. A commit after every verified item, with a descriptive message ("Add chapter 12 summary; verified word count"), gives each new session a readable history with `git log --oneline`. And if a session breaks something that used to work, the next session, or you, can return to the last good commit with the tools from Undoing Mistakes in Git. Committing only *after* verification means every commit in the history is a known-good state.

The ideas reach well beyond coding. A research agent can keep a sources list and a findings file. A data-cleaning agent can keep a list of processed files. A support agent working through a backlog can keep a ticket list with statuses. The shape is always the same: a structured list of items, a log of what happened and a check for each item.

### Testing long runs cheaply

A real 40-item run might take an hour and cost several dollars. You can't debug the harness that way. Instead, test the harness with a **fake agent**: a function that returns a canned handoff note instantly. Because `run` takes `work_on` as a parameter, swapping in a fake is one argument:

```python
# test_harness.py: test a long run in milliseconds, without a model
import json

import harness


def setup_state(tmp_path, monkeypatch, n_tasks: int) -> None:
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "TASKS", tmp_path / "tasks.json")
    monkeypatch.setattr(harness, "PROGRESS", tmp_path / "PROGRESS.md")
    tasks = [{"id": i, "description": f"item {i}", "done": False, "attempts": 0}
             for i in range(1, n_tasks + 1)]
    harness.save_json(harness.TASKS, tasks)
    harness.PROGRESS.write_text("# Progress\n")


def fake_work(task, notes):                   # a scripted "agent": instant and free
    return f"Worked on {task['id']}.", 1000


def test_resumes_where_it_stopped(tmp_path, monkeypatch):
    setup_state(tmp_path, monkeypatch, 5)
    monkeypatch.setattr(harness, "MAX_SESSIONS", 2)        # simulate running out of time
    assert harness.run(fake_work, verify=lambda t: True) == "stopped: session limit"
    monkeypatch.setattr(harness, "MAX_SESSIONS", 20)       # a brand-new run picks up
    seen = []
    harness.run(lambda t, n: (seen.append(t["id"]) or ("ok", 10)), verify=lambda t: True)
    assert seen == [3, 4, 5]                               # nothing was redone


def test_hands_back_a_task_that_keeps_failing(tmp_path, monkeypatch):
    setup_state(tmp_path, monkeypatch, 3)
    result = harness.run(fake_work, verify=lambda t: t["id"] != 2)
    assert result == "handed back: [2]"
    tasks = json.loads(harness.TASKS.read_text())
    assert tasks[1]["attempts"] == harness.MAX_ATTEMPTS
    assert "Needs a human" in harness.PROGRESS.read_text()


def test_token_budget_stops_the_run(tmp_path, monkeypatch):
    setup_state(tmp_path, monkeypatch, 10)
    monkeypatch.setattr(harness, "MAX_TOTAL_TOKENS", 2500)
    assert harness.run(fake_work, verify=lambda t: True) == "stopped: token budget"
```

These tests run in a fraction of a second and cover the behaviors that matter most: resuming without redoing work, giving up on a stuck item and respecting the budget. Test `session.py` the same way, with a fake client that returns scripted responses, using the fakes from Testing with pytest. After that, a few more cheap habits:

- **Shrink the task.** Run the real agent on 3 items before 40.
- **Use the [cheap model](#/models)** for harness development, and switch up only when the harness itself is solid.
- **Kill it on purpose.** Press Ctrl+C in the middle of a session, run it again and check that it resumes cleanly. A process dying halfway through a tool call is the hardest case; Durable Execution, the next lesson, goes deeper into surviving crashes.
- **Keep traces.** Your tracer from Agent Tracing and Debugging, with a session id on every span, lets you read what each session saw and did.

### On other providers

Nothing in this lesson depends on one provider. The harness, the task list, the progress file, verification, budgets and the hand-back rules are all plain Python and files, so they work with any model. Only `work_on` changes: on OpenAI, you'd call the Responses or Chat Completions API with tools defined using `parameters` instead of `input_schema`, read token counts from the response's `usage` field (the field names differ), and check its own finish signal instead of `stop_reason`. Open models served through Ollama's OpenAI-compatible API work with that same OpenAI-style code by changing the base URL, though small local models are much worse at long, multi-step tasks, which makes strict verification even more important. Some providers also offer hosted agents that keep state for you, such as OpenAI's Agents SDK sessions; these save code, but the advice to keep a structured task list and verify every item still applies. See OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) and Ollama's [OpenAI compatibility docs](https://docs.ollama.com/api/openai-compatibility).

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) from Anthropic. This is the core reading for the lesson, and Project: The Agent That Remembers is based on its approach.
   - Note what goes into the initializer session, the progress file and the feature list, and the routine each later session follows. Compare it with the runner in this lesson: what does their agent do itself that this lesson's harness does in code?
1. Read "Multisession software development pattern" in the Claude [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) docs, a short summary of the same pattern using memory files.
1. Reread the "Structured note-taking" part of [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents), including the example of an agent keeping notes while playing a long game.
1. Practice: write the files an initializer session would produce for a task of your choice, such as "build a command-line to-do app with five features." Write a `features.json` with each feature and a `passes: false` field, a `PROGRESS.md` template with sections for decisions, known problems and the session log, and a list of the steps every later session must follow.
1. Practice in code: build the runner from this lesson and make it pass the tests.
   - Copy `harness.py` and `test_harness.py`, run `uv run pytest`, and add a fourth test of your own: a session whose handoff note starts with `BLOCKED` must stop the run and hand back to a human immediately. Change `harness.py` until it passes.
   - Write a `verify` function for your task from the previous item, then run the real agent on a three-item version of it. Stop it with Ctrl+C halfway, run it again and confirm in `PROGRESS.md` that it resumed instead of starting over.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the two common ways long tasks fail, and what do they have in common?](#why-long-tasks-fail)
- [What is a harness, and what carries over from one session to the next?](#the-harness-carries-the-state)
- [What does an initializer session do, and why should the task list be structured rather than prose?](#the-initializer-session)
- [What routine does every later session follow, and how does a stopped run resume?](#the-session-routine)
- [Who decides that a task is done, and why?](#only-verified-work-counts)
- [Name four situations in which a long-running agent should hand the task back to a human.](#when-to-hand-back-to-a-human)
- [How can you test a harness for a long run without calling a model?](#testing-long-runs-cheaply)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Harness design for long-running application development](https://www.anthropic.com/research/harness-design-long-running-apps) from Anthropic goes further: a planner, generator and evaluator working together over multi-hour coding runs, and why a clean context reset with a handoff file can beat compaction.
