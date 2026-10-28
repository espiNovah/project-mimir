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

1. Write every step to a trace file (for example, `traces/run-<timestamp>.jsonl`): each model message, each tool call with its arguments, each tool result, token usage per step, and why the run ended (finished, step limit or error).
1. Write tests with `pytest` for each tool function and for the step limit. The tool tests should not call the model.
1. Run the agent on at least three realistic multi-step tasks, such as "Find the population of the three largest cities in Canada, total them, and write a short report to `workspace/report.md`." Commit the trace files.

#### The write-up

1. In your README, show one trace excerpt where a tool returned an error and the agent recovered (for example, it asked for a missing file, read the error listing the real files, and picked the right one).
1. Describe three failures you actually observed while building this (such as looping on the same search, bad tool arguments, stopping too early or writing to the wrong file), what caused each one, and what you changed to fix it. Link to traces from before and after the fix where you can.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Run independent tool calls concurrently with `asyncio` and report how much faster a multi-search task becomes.
- Add a code execution tool that runs inside a Docker container with `--network none`, a memory limit and a timeout, and show a trace of it being used.
- Add a token budget as a second stop condition, and print a cost summary at the end of each run.
- Build a tiny trace viewer that prints a trace file as a readable, colored timeline in the terminal.

</div>

### Submitting your work

A strong submission proves the agent works without the reviewer needing an API key. The README should show a sample task, the final output, and a short, readable excerpt of its trace. It should link to the committed traces, show the error-recovery excerpt, and include a passing `pytest` run (a screenshot or pasted output is fine). The three-failures section is often the most valuable part for anyone reading your portfolio: honest, specific debugging stories show you understand how agents fail.
