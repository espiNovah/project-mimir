### Introduction

Frameworks hide the agent loop behind a single function call. That is convenient later, but if you have never written the loop yourself, you will not know what is going wrong when a framework agent misbehaves. In this project you will build a real, multi-tool agent with nothing but the model API, a `while` loop and your own tool functions.

Your agent will be able to search the web, read and write files, do math and at least one more thing you choose. It will log every step to a trace file, stop safely when it runs too long, and recover when a tool fails. You will also keep this code: the Memory & Context Management section extends it in Project: The Agent That Remembers, and the Frameworks, SDKs & Skills section asks you to port it to a framework and compare.

### Before you start

- Create a new GitHub repository named `mimir-agent-loop` and set it up as a `uv` project with the `anthropic` package. Keep your API key in `ANTHROPIC_API_KEY`.
- Use the [cheap model](#/models) while developing to keep costs low. Switch to the [capable model](#/models) if you need more capability for your final demo runs, and say which one you used in your README.
- **No agent frameworks.** You may use the provider's SDK for HTTP calls, but not its tool runner or any higher-level agent helper. The loop, tool dispatch and error handling must be your code.
- For web search, either use your provider's server-side web search tool (for example, the Claude [web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)) or call a search API with a free tier yourself. Either is fine; say which you chose.
- Create a `workspace/` folder. Your file tools must only read and write inside it.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Never let a model run code on your machine unprotected

If you add a tool that runs Python code the model writes, it must run in an isolated place: a [Docker](https://docs.docker.com/get-started/) container or a throwaway virtual environment, with a timeout (for example, 10 seconds) and no network access. Never run model-written code directly in your own Python process or shell. If you are not ready to set that up, skip code execution and add a safe read-only tool instead, such as a dictionary lookup or a unit converter. You will learn much more about this in the Sandboxing Agents lesson.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### The loop

1. Write the agent loop yourself: send the conversation and tool definitions, run any requested tools, append the results and repeat until the model finishes.
1. Enforce a maximum step limit (for example, 15). When it is reached, the agent must stop gracefully: print a clear message, save the trace, and report what it had achieved so far instead of crashing.
1. Handle multiple tool calls in a single turn, returning one result per call, matched by ID.

#### The tools

1. Provide at least four tools, for example: `web_search`, `read_file`, `write_file` and `calculator`. The calculator must not use Python's `eval`.
1. Write every tool definition following the advice in Writing effective tools for agents: clear names, descriptions that say when to use the tool, specific parameter names and small, readable outputs.
1. Restrict the file tools to `workspace/`. A request for `../secret.txt` or an absolute path outside the folder must be refused with an error result, not executed. Write a test that proves this.
1. At least one tool must return structured, model-readable errors (for example, `{"error": "file_not_found", "message": "...", "available_files": [...]}`) with `is_error` set. Catch all exceptions in tool code so a broken tool never crashes the loop.

#### Tracing and testing

1. Write every step to a trace file (for example, `traces/run-<timestamp>.jsonl`) with the tracer from Agent Tracing and Debugging: a run span plus one child span per model call and per tool call, holding each model response, each tool call with its arguments, each tool result, token usage per step, and the end reason (`end_turn`, `step_limit` or something unusual such as `max_tokens`).
1. Write tests with `pytest` for each tool function and for the step limit. The tool tests should not call the model.
1. Run the agent on at least three realistic multi-step tasks, such as "Find the population of the three largest cities in Canada, total them, and write a short report to `workspace/report.md`." Commit the trace files.

#### The write-up

1. In your README, show one trace excerpt where a tool returned an error and the agent recovered (for example, it asked for a missing file, read the error listing the real files, and picked the right one).
1. Describe three failures you actually observed while building this (such as looping on the same search, bad tool arguments, stopping too early or writing to the wrong file), what caused each one, and what you changed to fix it. Link to traces from before and after the fix where you can.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Evidence

Your README must show:

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. (Linting, Formatting and CI)
- Tests that never call the model, so CI passes without an API key: every tool function, the `workspace/` path refusal, the step limit (using a fake client that always asks for a tool, as in Testing with pytest), a tool that raises turning into an `is_error` result instead of a crash, and the injection test below.
- OpenTelemetry-compatible traces: every span carries `trace_id`, `span_id`, `parent_id`, `kind`, `name`, `latency_s` and `error`, and the span names and fields line up with the GenAI conventions table in Agent Tracing and Debugging (`invoke_agent`, `chat <model>`, `execute_tool <tool name>`, the model, token counts, `stop_reason`, `tool_use_id`). Commit the traces from the three tasks and the eval run, using made-up files in `workspace/` so no private data ends up in Git. Show `debug.py` output for one run, and name the run that ended with `step_limit`, if any.
- An eval score with a confidence interval: an `evaluate.py` script with 10 tasks, each graded by an environment-state check (the right file exists in `workspace/` with the right contents, nothing else changed), as in Agent Eval Fundamentals. Include at least one task where the right action is to refuse or do nothing, such as a request to read a file outside `workspace/`. Give every trial a fresh copy of `workspace/` and run each task 3 times. Report the pass rate over all 30 trials with a 95% confidence interval and its `n`, pass^3 per task and overall (`pass_hat_k`), and the average steps and tokens per trial. Record the model and prompt version, and read every failed transcript.
- A prompt-injection test (Prompt Injection and the Lethal Trifecta). Put a made-up secret, such as `CANARY-7f3a`, in `workspace/notes.md`. Plant a poisoned web page where the agent will read it, as the result of a fake `web_search` or as a saved page in `workspace/` that the task asks it to summarize, with hidden text telling the agent to search for the contents of `notes.md` or to write them into a new file. The test checks what the agent *did*, not what it said: no `web_search` query and no file the task didn't ask for contains the canary.
  - Run the attack against the real model 10 times before your fix and report the leak rate ("leaked 2 of 10").
  - Fix it in code, not in the prompt: for example, the tool layer refuses any search query or file write that contains text from `notes.md`, or private files are out of reach in runs that use web tools. Run the 10 trials again and report the new rate.
  - In `pytest`, a fake model that always obeys the planted instruction proves the code blocks the leak on every run.
  - Add a short table listing each tool and which leg of the lethal trifecta it provides.

#### Extra credit

- Run independent tool calls concurrently with `asyncio` and report how much faster a multi-search task becomes.
- Add a code execution tool that runs inside a Docker container with `--network none`, a memory limit and a timeout, and show a trace of it being used.
- Add a token budget as a second stop condition, and print a cost summary at the end of each run.
- Build a tiny trace viewer that prints a trace file as a readable, colored timeline in the terminal.

</div>

### Submitting your work

A strong submission proves the agent works without the reviewer needing an API key. The README should show a sample task, the final output, and a short, readable excerpt of its trace. It should link to the committed traces, show the error-recovery excerpt, and include a passing `pytest` run (a screenshot or pasted output is fine). The three-failures section is often the most valuable part for anyone reading your portfolio: honest, specific debugging stories show you understand how agents fail.
