### Introduction

Coding agents such as Claude Code, OpenAI's Codex, Google's Gemini CLI, Cursor's agent mode and open-source tools such as Aider, OpenHands and mini-SWE-agent are the most widely used agents today. They read a codebase, edit files, run commands and tests, and keep going until the job is done. You first met them as a user in Working With AI Coding Assistants. This lesson opens the hood.

They are worth studying for two reasons. You'll use them every day as a developer, and you'll use them better once you know what they're doing between your prompt and their diff. And their design, a model with a file system, a shell and a way to check its own work, is a template for many agents you'll build. By the end of this lesson you'll have written a tiny coding agent of your own, which is the starting point for the Sandboxed Coding Agent project.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The core loop of a coding agent: gather context, act, verify.
- The four tools almost every coding agent has: read, edit, search and run.
- How to build a small coding agent with the Messages API.
- Why tests and other checks make coding agents reliable, and how agents game them.
- How context limits shape the tools and the way you work.
- Planning, permissions and reviewing what the agent wrote.

### A model with a computer

Strip away the branding and every coding agent is the loop you built in The Agent Loop: send the conversation to a model, run whatever tools it asks for, append the results, repeat until it stops. What makes it a *coding* agent is the tool set and the harness around it. (A **harness**, as you saw with the Claude Agent SDK, is all the code around the model: tool execution, permissions, history, limits and logging.)

The work falls into three phases that repeat, often many times in one task:

1. **Gather context.** The agent knows nothing about your repository when it starts. It lists folders, searches for names from the error message, and reads the files that look relevant.
1. **Act.** It edits files, creates new ones, or runs a command such as installing a package.
1. **Verify.** It runs the tests, the linter, the type checker or the program itself, and reads the output.

The output of verification becomes context for the next round. A failing test points at a line, the agent reads that line, makes another edit and runs the tests again. This is why coding agents can do work that one model call can't: each round, the real world (the interpreter, the test runner) corrects the model's guesses.

Different products put this loop in different places. Some run in your terminal or editor on your own files (Claude Code, Codex CLI, Gemini CLI, Aider). Others run in a cloud container and hand you a pull request (Codex cloud, Claude Code on the web, GitHub's Copilot coding agent). The loop is the same. What changes is whose computer the shell belongs to, which is the subject of the next lesson.

### The four core tools

Products differ in naming and details, but almost every coding agent ships the same four kinds of tool. How they are designed matters a lot. When the SWE-agent researchers studied this, they found that the **agent-computer interface** (the tools and the format of their output) changed results more than prompt wording did. That's the same lesson as Designing Tools for Agents, applied to code.

**Read.** A good read tool returns the file with line numbers and lets the agent ask for a range of lines. Line numbers let the model refer to exact places ("the bug is on line 42"), and ranges let it read a 3,000-line file in pieces instead of filling its context with all of it.

**Edit.** This is the trickiest one. Letting the model rewrite whole files is slow, costs many output tokens and quietly drops lines the model didn't mean to touch. So most agents use targeted edits:

- **Exact string replacement**: "replace this old text with this new text." The old text must appear exactly once, or the edit is refused and the agent must include more surrounding lines. Claude Code's Edit tool and Anthropic's text editor tool work this way.
- **Patches**: the model writes a diff-like patch that the harness applies. Codex uses its own `apply_patch` format.
- **Search/replace blocks or unified diffs**: Aider supports several edit formats and picks one per model, because models differ in which format they write reliably.

All of them have the same goal: small, checkable changes that fail loudly when the model's picture of the file is out of date.

**Search.** Before an agent can fix `average()`, it has to find it. Two styles exist. **Agentic search** uses ordinary tools such as `grep` (search file contents) and glob patterns (find files by name), called again and again as the agent narrows down. Claude Code leans on this style. **Indexed search** builds an embedding index of the codebase ahead of time, the RAG approach you learned in Core; Cursor does this. Aider adds a third idea, a **repo map**: a compact outline of the repository's classes and functions that goes into the prompt. Agentic search is simple and always up to date; an index can find code by meaning when the agent doesn't know the right word to grep for.

**Run.** A shell tool runs any command and returns its exit code and output. This single tool gives the agent tests, linters, package managers, git and the program itself. It's also the most dangerous tool by far, because "any command" includes `rm -rf` and `curl` to an attacker's server.

On top of these, most agents add a to-do list the model updates as it works, web fetch for documentation, and a way to start **subagents**: helper agents with their own fresh context, which you met in the Claude Agent SDK lesson.

### Build a tiny coding agent

The best way to see that there's no magic is to build one. This agent has the four tools and fixes a planted bug. First, a target project with a failing test:

```bash
uv init mini-coder && cd mini-coder
uv add anthropic python-dotenv pytest
mkdir -p demo/tests
printf 'def average(xs: list[float]) -> float:\n    return sum(xs) / (len(xs) + 1)\n' > demo/calc.py
printf 'from calc import average\n\ndef test_average():\n    assert average([2, 4]) == 3\n' > demo/tests/test_calc.py
(cd demo && uv run python -m pytest -q)   # 1 failed: the bug is planted
```

Put `ANTHROPIC_API_KEY` in `.env`. Then the tools, in `coder_tools.py`. They are plain Python functions that return strings, because tool results are text the model reads:

```python
# coder_tools.py: read, edit, search and run, all confined to one folder
import subprocess
from pathlib import Path

WORKDIR = Path("demo").resolve()
MAX_OUTPUT = 4000                      # characters of output the model gets to see


def _safe(path: str) -> Path:
    full = (WORKDIR / path).resolve()  # resolve() follows symlinks and ".."
    if not full.is_relative_to(WORKDIR):
        raise ValueError(f"{path} is outside the project folder")
    return full


def _clip(text: str) -> str:           # keep the start and the end, where errors usually are
    if len(text) <= MAX_OUTPUT:
        return text
    half = MAX_OUTPUT // 2
    return f"{text[:half]}\n...[{len(text) - MAX_OUTPUT} characters cut]...\n{text[-half:]}"


def read_file(path: str, start: int = 1, end: int = 200) -> str:
    lines = _safe(path).read_text().splitlines()
    shown = [f"{n:4} | {line}" for n, line in enumerate(lines[start - 1:end], start)]
    return "\n".join(shown) + f"\n({len(lines)} lines in file)"


def edit_file(path: str, old: str, new: str) -> str:
    target = _safe(path)
    if target.relative_to(WORKDIR).parts[0] == "tests":
        return "Error: tests are read-only. Fix the code, not the test."
    text = target.read_text()
    count = text.count(old)
    if count != 1:
        return (f"Error: the old text appears {count} times; it must appear exactly once. "
                "Read the file again and copy the text exactly, with more surrounding lines.")
    target.write_text(text.replace(old, new))
    return f"Edited {path}."


def search(pattern: str) -> str:
    result = subprocess.run(["grep", "-rnE", "--include=*.py", pattern, "."],
                            cwd=WORKDIR, capture_output=True, text=True)
    return _clip(result.stdout) or "No matches."


def run(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, cwd=WORKDIR,
                                capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return "Error: the command timed out after 60 seconds."
    return _clip(f"exit code {result.returncode}\n{result.stdout}{result.stderr}")
```

Notice the design choices from the last section: numbered lines with ranges, an exact-once edit rule with an error message that tells the model how to recover, output clipped to the start and end so a 10,000-line test log can't flood the context, and a 60-second timeout so a hung command can't stall the run. The tests folder is read-only, for a reason you'll see shortly.

Now the loop, in `coder.py`. It's the loop from Agent Loop From Scratch with a coding prompt:

```python
# coder.py: a tiny coding agent. Run it with: uv run coder.py
import os

import anthropic
from dotenv import load_dotenv

from coder_tools import edit_file, read_file, run, search

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
MAX_STEPS = 20
client = anthropic.Anthropic()


def tool(name: str, description: str, required: dict, optional: dict | None = None) -> dict:
    props = {key: {"type": kind} for key, kind in (required | (optional or {})).items()}
    return {"name": name, "description": description,
            "input_schema": {"type": "object", "properties": props, "required": list(required)}}


TOOLS = [
    tool("read_file", "Read a file with line numbers. Use start/end for long files.",
         {"path": "string"}, {"start": "integer", "end": "integer"}),
    tool("edit_file", "Replace old text with new text in a file. old must match exactly once.",
         {"path": "string", "old": "string", "new": "string"}),
    tool("search", "Search Python files for a regular expression. Returns file:line: text.",
         {"pattern": "string"}),
    tool("run", "Run a shell command in the project folder. Returns exit code and output.",
         {"command": "string"}),
]
HANDLERS = {"read_file": read_file, "edit_file": edit_file, "search": search, "run": run}
SYSTEM = """You are a coding agent in a small Python project.
Work in a loop: explore with search and read_file, make the smallest fix with edit_file,
then verify with run("python -m pytest -q"). Repeat until the tests pass.
Never change or delete tests. Finish with two sentences: the cause and the fix."""


def main(task: str) -> None:
    messages = [{"role": "user", "content": task}]
    for step in range(1, MAX_STEPS + 1):
        response = client.messages.create(model=MODEL, max_tokens=8000, system=SYSTEM,
                                          tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":          # done, or stopped for another reason
            print("".join(b.text for b in response.content if b.type == "text"))
            return
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"[{step}] {block.name} {block.input}")
            try:
                output = HANDLERS[block.name](**block.input)
            except Exception as error:                   # bad path, missing file, bad arguments
                output = f"Error: {error}"
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": output, "is_error": output.startswith("Error")})
        messages.append({"role": "user", "content": results})
    print(f"Stopped: used all {MAX_STEPS} steps.")


main("The test suite is failing. Find the bug and fix it.")
```

Run it with `uv run coder.py`. A typical run looks like this: `run` the tests and see `assert 2.0 == 3`, `search` for `def average`, `read_file` on `calc.py`, `edit_file` to remove the `+ 1`, `run` the tests again, then a two-sentence summary. Six model calls, and you've reproduced the core of a commercial coding agent in about 100 lines.

<div class="lesson-note lesson-note--critical" markdown="1">

#### This agent is not sandboxed

The path checks in `read_file` and `edit_file` protect files only from those two tools. The `run` tool executes any shell command with your user account's full power, so the model can read or delete anything you can. Only run this on a throwaway folder, keep the step budget, and watch every command it prints. The next lesson, Sandboxing Agents, moves `run` into a container.

</div>

### Tests are the feedback signal

Take the test away and the agent above can still edit `calc.py`, but it has no way to know whether the edit worked. It will say "Fixed!" either way. That is the single most important fact about coding agents: **an agent that can check its own work fixes its own mistakes, and an agent that can't is guessing.**

So the most valuable thing you can give a coding agent is a fast, trustworthy check:

- a test suite, ideally with a test that reproduces the bug before the fix;
- a type checker and linter, which catch whole classes of mistakes in seconds;
- a command that runs the program and shows its output;
- for user interfaces, a screenshot or a browser check, which you'll add in Browser and Computer Use.

This is also how coding agents are measured. **SWE-bench** gives an agent a real GitHub issue and the repository, then grades its patch with tests the agent never saw. Hidden tests matter, because agents optimize for whatever check they can see. Under pressure to make tests pass, a model may weaken an assertion, special-case the test's exact input, wrap the failing code in `try/except: pass`, or delete the test entirely. This is called **reward hacking**: satisfying the check without doing the job. It isn't malice. "Make the red text go away" is a goal that deleting a test satisfies.

You defend against it in layers. The prompt says "never change tests." The harness enforces it, as `edit_file` does by refusing anything under `tests/`. (A determined agent could still use `run` to rewrite a test with `sed`, which is one more reason the shell needs limits.) And you review the diff, checking specifically whether any test or check got weaker.

### Context is the scarce resource

Every file read, every search result and every test log stays in the conversation, and you send the whole conversation on every call. You studied the consequences in Context Engineering for Agents: cost and latency grow with each step, and quality drops as the window fills with stale material. Coding agents hit this hard, because code and logs are long. Many of their design choices are context management in disguise:

- **Ranges and clipping.** Reading 40 lines around a match instead of a whole file, and clipping a test log to its start and end, keep each tool result small.
- **Search before read.** `grep -n` returns a few matching lines with line numbers, so the agent can read just the right region.
- **Compaction.** When the window nears its limit, the harness summarizes older turns, as you did by hand in Compaction and Context Editing. Long runs keep going, at the cost of occasionally forgetting a detail.
- **Subagents.** A wide search ("find every place we parse dates") goes to a helper with a fresh context, and only its summary comes back.
- **Memory files.** A project file such as `AGENTS.md` (an open format several agents read) or `CLAUDE.md` (Claude Code's own file) is loaded at the start of every session. It holds the build and test commands and the rules the agent would otherwise get wrong, so the agent doesn't spend steps rediscovering them. Keep it short; every line is read on every run.
- **Fresh sessions.** When you switch to an unrelated task, start a new session. A clean context beats a full one.

The working habits that follow are the same across tools. Give one task at a time. Point at the relevant files when you know them. Clear the session between tasks. If a run goes in circles, stop it and restart with a better prompt rather than piling corrections onto a polluted context.

### Plan first, then let it act

For anything bigger than a one-line fix, the cheapest place to catch a wrong approach is before any code exists. Most agents have a **plan mode** or can be asked to "explore and propose a plan, but don't edit anything yet." You read the plan, correct it ("use the existing `parse_date` helper, don't add a new dependency"), then let the agent implement. Fixing a plan takes a sentence. Fixing a 400-line diff built on the wrong idea takes an hour.

**Permissions** decide how much the agent does without asking. Most agents offer a range of modes: ask before every edit and command; edit files freely but ask before running commands; or run fully on their own. They also let you allow or deny specific tools and commands, such as always allowing `uv run pytest` and never allowing `git push`. The more autonomy you grant, the more the environment itself has to be safe, because no human is reading each command. That's why "full auto" modes are meant for containers and cloud sandboxes, not your laptop.

### You own the result

Agent-written code looks finished. It's well formatted, has comments and passes the tests the agent ran. It can still be subtly wrong: correct for the test's input and wrong for others, quietly catching and hiding errors, adding a dependency you didn't want, or solving the problem with three times more code than needed. Before you merge, read the whole diff as if a stranger wrote it:

- Did any test, assertion, type hint or lint rule get weaker or disappear?
- Does the change do what was asked, and only that?
- Would you be able to explain every line in a code review?

If the answer to the last question is no, the change isn't ready, however green the tests are. You'll practice this formally in Code Review in the Production path.

### On other providers

Nothing in this design is Claude-specific. Codex, Gemini CLI, Aider and OpenHands all run the same gather-act-verify loop with read, edit, search and shell tools, and Aider and OpenHands can drive models from many providers, including local open models. Porting `coder.py` changes only the API shapes you met in Function Calling: with OpenAI's Chat Completions API, each tool goes inside `{"type": "function", "function": {...}}` with its schema under `parameters`, the model's requests arrive in `message.tool_calls` with arguments as a JSON string you must `json.loads`, the stop signal is `finish_reason == "tool_calls"`, and each result goes back as a separate `{"role": "tool", "tool_call_id": ..., "content": ...}` message. The tools in `coder_tools.py` don't change at all. Edit formats are where models differ most: Aider's docs report which formats each model handles reliably, so test your edit tool with the model you plan to use. See OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling), and for a local model, [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility); small local models struggle with long multi-step coding runs, so expect more failed runs.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Claude Code best practices](https://code.claude.com/docs/en/best-practices) from start to finish. Its advice applies to any coding agent, not only Claude Code.
   - Note the advice on giving the agent a way to verify its work, and on managing context. Compare it with the sections above.
1. Reread the agent-computer interface part of [Building effective agents](https://www.anthropic.com/research/building-effective-agents), including the appendix on prompt engineering your tools.
   - Connect it to the SWE-bench example: why did tool design matter more than the prompt?
1. Read the README of [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent), an open-source coding agent of about 100 lines that scores well on SWE-bench using only a shell, and skim its main agent file.
   - Compare its single-tool design with the four tools in `coder_tools.py`. What does it gain and lose by having only `bash`?
1. Skim the [SWE-bench site](https://www.swebench.com/) to see how coding agents are measured on real GitHub issues, and why the grading tests are hidden.
1. Practice: build `coder.py` and `coder_tools.py` from this lesson and run them on the planted bug.
   - Add a JSONL trace of every step, as in Agent Tracing and Debugging, and record the step count and the token usage from `response.usage`.
   - Plant a harder bug in a second function and add a test for it. Run the agent five times and count how many runs fix both bugs.
   - Remove the read-only rule for `tests/`, change the system prompt to "make the tests pass", and see whether the agent ever edits a test. Then put the rule back.
1. Use a coding agent of your choice on one of your earlier projects.
   - Ask it to explore and plan a small feature first, review the plan, then let it implement and run the tests.
   - Write down every point where you had to correct it, and what instruction would have prevented it. Put the useful ones in an `AGENTS.md` or your tool's memory file.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the three phases of a coding agent's loop, and how does each feed the next?](#a-model-with-a-computer)
- [Why do most coding agents edit files by exact string replacement or patches instead of rewriting whole files?](#the-four-core-tools)
- [What is the difference between agentic search and indexed search?](#the-four-core-tools)
- [Why does the tiny agent clip tool output, number lines and time out commands?](#build-a-tiny-coding-agent)
- [What is reward hacking in a coding agent, and how do you defend against it?](#tests-are-the-feedback-signal)
- [Name four techniques coding agents use to keep the context window from filling up.](#context-is-the-scarce-resource)
- [Why should you review a plan before letting an agent write code, and how do permission modes relate to sandboxing?](#plan-first-then-let-it-act)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793) is the research paper behind the agent-computer interface idea, with experiments on how tool design changes results.
- [Aider's edit formats](https://aider.chat/docs/more/edit-formats.html) and [repository map](https://aider.chat/docs/repomap.html) docs explain two design choices this lesson only touched on.
- The [OpenAI Codex CLI repository](https://github.com/openai/codex) is an open-source coding agent you can read end to end, including its patch-based edit tool and sandbox settings.
- [AGENTS.md](https://agents.md/) describes the open project-instructions format and lists the agents that read it.
- Anthropic's [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) explains why coding agents favor just-in-time search over loading everything up front.
