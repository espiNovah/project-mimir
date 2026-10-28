### Introduction

In "Agent Loop From Scratch" you built an agent with nothing but a model API and a `while` loop. Now you will build the same agent two more times: once with the Claude Agent SDK and once with one other framework (the OpenAI Agents SDK, LangGraph, Pydantic AI or Google ADK). All three versions get the same four tools and the same ten test tasks, so you can compare them fairly. You will also package one capability as an Agent Skill.

The goal is not to crown a winner. It is to have real numbers and real experience behind your opinion, so that when someone asks "should we use a framework?" you can answer with evidence.

### Before you start

- Create a new GitHub repository named `mimir-port-your-agent`. Copy in (or link to) your agent from "Agent Loop From Scratch".
- Use `uv` to manage dependencies. Put each version in its own folder, such as `raw/`, `claude_sdk/` and `other/`, sharing one `tools/` package and one `tasks/` folder.
- Read your API keys from environment variables (`ANTHROPIC_API_KEY`, plus whatever your second framework's provider needs). Never commit a key.
- Use the same model in every version where you can, such as the [capable model](#/models), so model choice doesn't muddy the comparison. If your second framework runs on a different provider, say so in the README.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Keep the tools in one place

Write each tool once as a plain Python function with type hints and a docstring. Each version then wraps the same function in its own tool format. If you copy and tweak tools per framework, you are no longer comparing frameworks.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Pick exactly four tools for your agent, such as a file reader, a calculator, a web fetcher and a note writer. Put them in a shared `tools/` package with unit tests that pass.
1. Write ten test tasks in `tasks/tasks.json`. Each task has an input prompt and a check that decides pass or fail automatically, such as "the file `notes.md` contains the word Paris" or "the final answer equals 42". At least three tasks should need more than one tool call.
1. Build version 1, the raw loop, on the Messages API with no agent framework. Reuse your earlier project code where you can.
1. Build version 2 with the Claude Agent SDK. Register your four tools as custom tools and turn off every built-in tool you are not using, so all versions have the same abilities.
1. Build version 3 with one of the OpenAI Agents SDK, LangGraph, Pydantic AI or Google ADK.
1. Write one runner script that runs all ten tasks against any version, three times each, and records for every run:
   - pass or fail,
   - input and output tokens,
   - wall-clock time,
   - number of model turns.
1. Package one capability as an Agent Skill. Choose something procedural, such as "write a trip summary in our house format", and create a folder with `SKILL.md` (front matter with `name` and `description`) and at least one helper script or reference file. Load it in the Claude Agent SDK version, and show with one task that the agent uses it when relevant and ignores it otherwise.
1. Run a debuggability test. Break one tool on purpose (make it return a misleading error) and time how long it takes you to find the cause from each version's logs or traces.
1. Add a results table to your README with one row per version and these columns: lines of code (excluding the shared tools and tasks), success rate across 30 runs, average tokens per task, average time per task and minutes to diagnose the broken tool.
1. Write a one-page "When I'd use each" section. For each of the three approaches, describe a real project where you would choose it and one where you would not, and point to your numbers.
1. Push your project to GitHub with a README that explains what it does, how to run each version and the runner, and what you learned.

#### Extra credit

- Add a fourth version using a framework you skipped, and add it to the table.
- Turn on tracing in each version and include a screenshot of the same task's trace from all three.
- Run the same tasks on the [cheap model](#/models) and report how the success rate changes per version.

</div>

### Submitting your work

A strong submission lets a reviewer see the comparison in under a minute: the results table near the top of the README, followed by your "When I'd use each" page. Make the runner reproducible with a single command, and commit the raw results file (for example `results.csv`) so anyone can check your numbers. Be honest when a result surprised you or when a framework won for reasons you didn't expect. That honesty is what makes the write-up useful to others and convincing to employers.
