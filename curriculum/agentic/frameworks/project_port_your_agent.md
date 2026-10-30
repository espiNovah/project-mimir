### Introduction

In "Agent Loop From Scratch" you built an agent with nothing but a model API and a `while` loop. Now you will build the same agent two more times: once with the Claude Agent SDK and once with one other framework. LangGraph is the natural choice, since you learned it in depth in LangGraph and the Wider Ecosystem, but the OpenAI Agents SDK, Pydantic AI or Google ADK are fine too. All three versions get the same four tools and the same ten test tasks, so you can compare them fairly. You will also package one capability as an Agent Skill.

Then you'll take the framework version off the hosted API entirely. You'll run it on an open model on your own machine through Ollama, as you set up in Running Open Models, and compare it with your original model on the same tasks. Many teams need an agent that works on more than one provider, or one that never sends data off the machine, and this is how you find out what that costs.

The goal is not to crown a winner. It is to have real numbers and real experience behind your opinion, so that when someone asks "should we use a framework?" or "could this run on an open model?" you can answer with evidence.

### Before you start

- Create a new GitHub repository named `mimir-port-your-agent`. Copy in (or link to) your agent from "Agent Loop From Scratch".
- Use `uv` to manage dependencies. Put each version in its own folder, such as `raw/`, `claude_sdk/` and `other/`, sharing one `tools/` package, one `core.py` for your prompts and message building (as in When Frameworks Help) and one `tasks/` folder.
- Read your API keys from environment variables (`ANTHROPIC_API_KEY`, plus whatever your second framework's provider needs). Never commit a key.
- Use the same hosted model in every version where you can, such as the [capable model](#/models), so model choice doesn't muddy the framework comparison. If your second framework runs on a different provider, say so in the README.
- Install [Ollama](https://ollama.com/download) and pull a tool-calling model that fits your machine, such as a Qwen3 size from the table in Running Open Models. Raise the context length (for example `OLLAMA_CONTEXT_LENGTH=32768 ollama serve`) and check it with `ollama ps`, because the small default will silently cut off your agent's tools and history. If your computer can't run any model at a usable speed, use an open model hosted by Ollama's cloud or another provider, and say so in the README.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Keep the tools in one place

Write each tool once as a plain Python function with type hints and a docstring. Each version then wraps the same function in its own tool format. If you copy and tweak tools per framework, you are no longer comparing frameworks. The same goes for the model: choose it with environment variables (`MIMIR_MODEL`, plus a base URL for Ollama), so switching to the open model changes configuration, not code.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Pick exactly four tools for your agent, such as a file reader, a calculator, a web fetcher and a note writer. Put them in a shared `tools/` package with unit tests that pass. Make each one a plain function, not a provider's server-side tool, so it also works with a local model.
1. Write ten test tasks in `tasks/tasks.json`. Each task has an input prompt and a check that decides pass or fail automatically, such as "the file `notes.md` contains the word Paris" or "the final answer equals 42". At least three tasks should need more than one tool call.
1. Build version 1, the raw loop, on the Messages API with no agent framework. Reuse your earlier project code where you can.
1. Build version 2 with the Claude Agent SDK. Register your four tools as custom tools and turn off every built-in tool you are not using, so all versions have the same abilities.
1. Build version 3 with LangGraph, extending the graph you started in LangGraph and the Wider Ecosystem. If you'd rather use the OpenAI Agents SDK, Pydantic AI or Google ADK, that's fine, as long as it can run an open model.
1. Write one runner script that runs all ten tasks against any version and model, three times each, and records for every run:
   - pass or fail,
   - input and output tokens,
   - wall-clock time,
   - number of model turns.
1. Run version 3 on at least one open model through Ollama, as well as on your original model. Change only configuration (the model name and base URL), not the graph, the tools or the tasks. Run the same ten tasks three times each. Running the raw loop on the open model too is a good addition, since your `local_agent.py` from Running Open Models already does it. The Claude Agent SDK version stays on Claude, because that SDK runs Claude models only.
1. Package one capability as an Agent Skill. Choose something procedural, such as "write a trip summary in our house format", and create a folder with `SKILL.md` (front matter with `name` and `description`) and at least one helper script or reference file. You can reuse the skill you wrote in Agent Skills. Load it in the Claude Agent SDK version, and show with one task that the agent uses it when relevant and ignores it otherwise.
1. Run a debuggability test. Break one tool on purpose (make it return a misleading error) and time how long it takes you to find the cause from each version's traces, logs or the requests captured by `recorder.py` from When Frameworks Help.
1. Add a results table to your README with one row per version and model, and these columns: lines of code (excluding the shared tools, core and tasks), success rate across 30 runs, average tokens per task, average time per task and minutes to diagnose the broken tool.
1. Write a one-page "When I'd use each" section. For each of the three approaches, describe a real project where you would choose it and one where you would not, and point to your numbers. Add a paragraph on the open model: which of your tasks it handled well enough to run locally, and which it didn't.
1. Push your project to GitHub with a README that explains what it does, how to run each version, the open model and the runner, and what you learned.

#### Evidence

Your README must show:

- A passing GitHub Actions badge, and a workflow that runs `ruff check`, `ruff format --check` and `pytest` on every push. Pytest covers the shared tools, every task's pass or fail check, your `core.py` message building, and version 3 with a scripted fake model (as in "Test the graph without a model" in LangGraph and the Wider Ecosystem). No test calls a real model or needs Ollama. (Linting, Formatting and CI)
- Traces: every run of every version writes a trace with the version, the model, the task ID, each model call and tool call, the tokens, the latency and the end reason, as in Agent Tracing and Debugging. Use your own tracer or the framework's tracing. Commit the raw `results.csv` from the runner, plus one trace per version and model for the same multi-step task. Your tasks use made-up data, so the traces are safe to commit.
- The results table, with at least four rows: the raw loop, the Claude Agent SDK and version 3 on your original model, and version 3 on the open model. Give each success rate over 30 runs with a 95% confidence interval, bootstrapped over the ten tasks (average each task's three runs first, as in Eval Statistics), and pass^3 next to it (Agent Eval Fundamentals). Ten tasks gives wide intervals, so say which differences the intervals can't separate.
- An open-model comparison for version 3: the success rate on your original model minus the open model's, with a paired bootstrap confidence interval over the same ten tasks; average time per task and tokens per second for each; and the open model's tag, size, quantization, context length and the hardware you ran it on. For every task the open model failed, name the failure pattern you found in its trace, such as skipping a tool and guessing, repeating a call or stopping early. (Running Open Models)
- A prompt-injection task in `tasks/injection.json`, kept apart from the ten so it doesn't change the success rates. Plant an instruction in content one of your tools returns, such as a file the reader opens or a page the fetcher returns, telling the agent to write a canary string such as `CANARY-7f3a9` into a note, or to fetch a URL with its notes in the query string. Detect success from the environment (the canary in a workspace file, or the URL in a spy's log, as in Testing for injection), never from what the agent says. Run it three times on every version and model, add the result ("leaked 1 of 3") as a column in the table, and say which combination resisted best and what you think made the difference. (Prompt Injection and the Lethal Trifecta)
- The debuggability result: which tool you broke, and for each version, the minutes to find the cause and what showed it to you (a trace, the framework's logs or the captured request).
- The skill check: an excerpt from the run where the agent loaded the skill for a matching task, and from one where it didn't load it for an unrelated task.

#### Extra credit

- Add a fourth version using a framework you skipped, and add it to the table.
- Send each version's traces to a trace viewer such as Langfuse or Phoenix (Agent Tracing and Debugging), and include a screenshot of the same task's trace from all three.
- Run version 3 on a second hosted provider as well, such as OpenAI, and add it to the table.
- Run the same tasks on the [cheap model](#/models), or on a second open model of a different size, and report how the success rate changes per version.

</div>

### Submitting your work

A strong submission lets a reviewer see the comparison in under a minute: the results table near the top of the README, followed by your "When I'd use each" page. Make the runner reproducible with a single command, with the version and model as arguments, and commit the raw results file (for example `results.csv`) so anyone can check your numbers. Be honest when a result surprised you, when a framework won for reasons you didn't expect, or when the open model did better or worse than you guessed. That honesty is what makes the write-up useful to others and convincing to employers.
