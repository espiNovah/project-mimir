### Introduction

In this project you will build a small coding agent that does a complete job safely. It will receive a repository with a failing test, find and fix the bug, run the tests, start the app and check in a real browser that the fix works. Then it will ask you before pushing anything. It runs inside a sandbox with no access to your files and a short list of allowed network destinations, and it keeps a trace of every step plus a budget on steps and cost.

This combines everything from this section: the coding agent loop, sandboxing and browser automation. You can build it on the Claude Agent SDK, another framework from "Port Your Agent", or your own loop from "Agent Loop From Scratch".

### Before you start

- Create a GitHub repository named `mimir-sandboxed-coding-agent` for the agent itself.
- Create a second, small target repository, such as `mimir-buggy-todo-app`. It should be a tiny web app (for example FastAPI or Flask with one HTML page) with a `pytest` test suite. Plant one bug that makes a test fail and that is visible in the browser, such as a todo list that shows items in the wrong order or a counter that is off by one.
- Install Docker. You'll run the agent's work inside a container. If you prefer an OS-level sandbox, [sandbox-runtime](https://github.com/anthropics/sandbox-runtime) is an acceptable alternative.
- Install Playwright for Python (`uv add playwright`, then `uv run playwright install chromium`) or set up [Playwright MCP](https://github.com/microsoft/playwright-mcp).
- Keep your `ANTHROPIC_API_KEY` (or other provider key) on the host. Only the process that calls the model needs it. Never copy it into the target repository.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Never give the sandbox your push credentials

The agent must not be able to push on its own. Keep your Git credentials outside the sandbox. Pushing should be done by a small trusted script on the host, and only after you type "yes".

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Write a sandbox setup (a `Dockerfile` plus a run script, or a sandbox-runtime config) that:
   - mounts only a copy of the target repository, read-write,
   - has no access to your home directory or any other host folder,
   - blocks all network traffic except an allowlist you define, such as the model API host, your package registry and `localhost`.
1. Prove the sandbox works with a script `sandbox_check.sh` that tries to read a file in your home directory, write outside the project and reach a non-allowlisted domain. All three attempts must fail, and the script output goes in your README.
1. Give the agent tools to read files, edit files, run shell commands inside the sandbox and drive a browser with Playwright or Playwright MCP.
1. Make the agent complete this task from a single instruction such as "The test suite is failing. Fix the bug and confirm the fix in the browser.":
   - run the tests and read the failure,
   - find and fix the bug without deleting or weakening any test,
   - rerun the tests until they pass,
   - start the app inside the sandbox and use the browser to check that the page now shows the correct behavior,
   - save a screenshot of the fixed page as evidence.
1. Add a human approval gate before any `git push`. The agent can commit inside the sandbox, but pushing goes through a host-side function that prints the diff and the commit message and waits for you to type "yes". Any other answer cancels the push.
1. Enforce a step budget (for example, at most 40 tool calls) and a cost budget (for example, at most $1.00 per run, computed from token usage). When either budget runs out, the agent stops and reports what it got done.
1. Record a trace of every run to a JSON Lines file: each model turn, each tool call with its arguments and result (truncated if long), tokens used and the running cost.
1. Run the agent five times from a clean copy of the target repository. Report how many runs fixed the bug and passed the browser check, the average number of steps and the average cost.
1. Push your project to GitHub with a README that explains what it does, how to run it, how the sandbox is set up and what you learned.

#### Extra credit

- Add a second planted bug that only shows up in the browser, not in the tests, and see whether your agent finds it.
- Add a prompt-injection trap: a comment in the target code that tells the agent to send the repository to an outside URL. Show that the network allowlist blocks it even if the agent tries.
- Make the trace viewable as a simple HTML timeline.

</div>

### Submitting your work

A strong README opens with a short demo: a recording or a sequence of screenshots showing the failing test, the fix, the passing tests, the browser check and the approval prompt. It includes the output of `sandbox_check.sh`, the five-run results table and one full trace file. Explain the design choices you made about the sandbox and the approval gate, and describe at least one run where the agent did something you didn't expect.
