<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Some tasks are naturally made of independent pieces: review this code for security issues *and* style issues, or analyze the impact of a change on customers, employees *and* investors. Running those pieces at the same time makes a system faster, and sometimes more accurate. Other tasks can be split up too, but you cannot know how until you see the input. In this lesson you will learn **parallelization**, where your code splits the work, and **orchestrator-workers**, where a model decides how to split it.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Sectioning: splitting a task into independent subtasks that run at once.
- Voting: running the same task several times and combining the answers.
- Running model calls concurrently in Python.
- The orchestrator-workers pattern and how it differs from parallelization.
- How results from many calls are combined.
- Where these patterns sit between workflows and agents.

### Key ideas

- **Parallelization comes in two flavors.** *Sectioning* gives each call a different part of the job (one call checks facts, another checks tone). *Voting* gives several calls the same job and combines their answers, which is useful when you want higher confidence, for example flagging content only if two out of three reviewers agree.
- **Separate calls often focus better than one big call.** A model asked to check ten things at once tends to do each one less carefully than ten models asked to check one thing each. Guardrails are a classic example: one call answers the user while a second screens the request.
- **Concurrency is a code concern.** Independent calls can run at the same time using the async client and `asyncio.gather`, so total time is close to the slowest call, not the sum of all of them. Watch your provider's rate limits when you fan out.
- **Orchestrator-workers lets a model plan the split.** A central "orchestrator" call reads the task, decides which subtasks are needed, and sends each one to a "worker" call. The orchestrator then combines the results. Use it when the subtasks depend on the input, such as deciding which files in a codebase need changes.
- **The difference is who decides the pieces.** In parallelization, your code defines the subtasks in advance. In orchestrator-workers, the model does. That makes orchestrator-workers more flexible, but also less predictable and harder to test.
- **This is a step toward multi-agent systems.** Orchestrator-workers is the workflow version of what the Multi-Agent Systems section covers with full subagents. The same trade-offs apply: more calls, more tokens and more coordination to get right.
- **Combining results needs care.** A final synthesis step must resolve disagreements and duplicates between workers. Give it clear instructions and test it like any other step.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read "Workflow: Parallelization" and "Workflow: Orchestrator-workers" in [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents).
1. Run Example 2 (parallelization) in the [basic workflows notebook](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/basic_workflows.ipynb), then work through the [orchestrator-workers notebook](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/orchestrator_workers.ipynb).
   - In the orchestrator notebook, find the exact prompt the orchestrator uses to plan subtasks and the code that parses its plan.
1. Read the "Running Tasks Concurrently" section of the Python docs on [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html).
1. Practice: write a script that reviews a short paragraph of product copy with three parallel calls (grammar, tone and factual claims) and one final call that merges their feedback. Time it running sequentially and concurrently, and write down both numbers.

</div>
