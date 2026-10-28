<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

You now have three ways to build an agent: your own loop on top of a model API, an agent SDK like the Claude Agent SDK, and a general framework like LangGraph or Pydantic AI. None is always right. Frameworks save time on the boring parts and cost you visibility into the parts that break. This lesson gives you a way to choose, and to explain your choice in a design review or a job interview.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What frameworks give you: tools, retries, tracing, state and integrations.
- What frameworks hide: prompts, context assembly and control flow.
- Signs you should drop down to a raw loop.
- Signs you should adopt a framework or SDK.
- Managed agent runtimes as a third option.
- How to keep a framework replaceable.

### Key ideas

- **Frameworks help most with plumbing.** Streaming, retries, tracing, tool schemas from type hints, checkpoints and ready-made integrations are tedious to build and easy to get wrong.
- **Frameworks hurt most with the things that decide quality.** If you can't see the exact prompt and context the model received, you can't fix a bad step. Before you adopt one, make sure you can print the full request for any turn.
- **Start simple and add structure when you feel the pain.** A single model call or a fixed workflow beats an agent for many tasks. A raw loop beats a framework until you need features you'd otherwise rebuild, such as human approval with pause and resume, durable state or many integrations.
- **Pick an agent SDK when the agent needs a computer.** If the job involves files, shells, code or long sessions, a harness like the Claude Agent SDK gives you those tools, permissions and compaction already tested.
- **Managed runtimes move the harness to the provider.** Hosted agent services (for example, Claude Managed Agents) run the loop and sandbox for you. They trade control and portability for less infrastructure.
- **Keep the core yours.** Put your prompts, tool functions and eval suite in plain code you own, and keep the framework at the edges. Then switching frameworks means rewriting glue, not your agent.
- **Decide with numbers.** Lines of code, success rate on the same tasks, tokens per task and the time it takes to diagnose a failed run are better arguments than popularity.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Reread the "When (and when not) to use agents" and "When and how to use frameworks" parts of [Building effective agents](https://www.anthropic.com/research/building-effective-agents).
1. Read [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) factors 2, 3 and 8 (own your prompts, own your context window, own your control flow).
   - For each, write one sentence on whether the Claude Agent SDK and your chosen framework let you do it.
1. Reread the parts of the [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) that compare the SDK with the plain Client SDK and with Claude Code.
1. Take one failed run from a framework you tried in the previous lesson and find the exact prompt the model saw. Time how long that takes, and note what tool or setting made it possible.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) shows what a hosted agent runtime takes off your plate.
