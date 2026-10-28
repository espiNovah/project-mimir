<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Real tools fail. Networks time out, files are missing, and models send arguments that do not make sense. A well-built agent treats these failures as information and recovers; a badly built one crashes or loops forever. Models can also ask for several tools at once, and running those calls together can make your agent much faster. This lesson covers both: how to report errors the model can act on, and how to handle multiple tool calls in a single turn.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The kinds of errors an agent meets: bad arguments, tool failures and timeouts.
- Returning errors as tool results instead of crashing.
- Writing error messages that tell the model what to do next.
- What parallel tool calls are and how to return their results.
- When to run tool calls concurrently and when to run them one at a time.

### Key ideas

- **Catch errors and send them back to the model.** If your tool raises an exception, do not let it crash the loop. Return a `tool_result` with the error text and `is_error: true`. The model then sees what happened and can retry, change approach or tell the user.
- **Make errors instructive.** "Failed" teaches nothing. "File `notes.txt` not found. Available files: `todo.txt`, `ideas.md`" lets the model fix its own mistake on the next turn. Include what went wrong, why, and a suggested next step.
- **Validate inputs early.** Check arguments before doing anything expensive or irreversible, and return a clear error if they are wrong. Strict schemas prevent many bad arguments in the first place.
- **Guard against error loops.** A model can keep retrying the same broken call. Count consecutive failures per tool and stop or change strategy after a few. Your overall step cap is the last line of defense.
- **A single turn can contain several tool calls.** When the tasks are independent ("get the weather in Paris and in London"), the model may return several `tool_use` blocks at once. You must return one `tool_result` for each, matched by ID, all together in the next user message.
- **You decide how to execute them.** Independent, read-only calls are usually safe to run concurrently, for example with Python's `asyncio.gather`, which cuts waiting time. Calls with side effects or that depend on each other are safer to run in order. If you skip a call, still return a result for it, marked as an error, explaining why.
- **Timeouts are errors too.** Give every tool a time limit, and report a timeout as an error result rather than letting the whole agent hang.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls), which explains the exact format of tool results.
   - Read "Handling errors with is_error" closely, including the tip on writing instructive error messages.
1. Read [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use).
   - Read "Execution semantics" and "Maximizing parallel tool use." Skim the rest.
1. Work through Rings 3 and 4 of the [Tutorial: Build a tool-using agent](https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent), which add multiple tools, parallel calls and error handling to the loop you built in the last lesson.
1. Read the "Coroutines and Tasks" section of the Python docs page on [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html), up to and including "Running Tasks Concurrently," so that `asyncio.gather` is not a mystery.
1. Practice: add a tool that reads a file from a single sandbox folder. Ask the agent to summarize a file that does not exist. Make the tool return an instructive error listing the files that do exist, and confirm in the printed trace that the agent recovers and picks a real file.

</div>
