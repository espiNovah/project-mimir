<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

The Claude Agent SDK is one of several popular ways to build agents. Job listings and open-source projects also use the OpenAI Agents SDK, LangGraph, Pydantic AI and Google's Agent Development Kit (ADK). Each one makes different choices about how much it hides, how you describe control flow and which model providers it supports. You don't need to master all of them. You need to recognize the core ideas well enough to read any of them, and to pick one on purpose.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The shared core every agent framework implements.
- The OpenAI Agents SDK: agents, handoffs, guardrails and tracing.
- LangGraph: agents as explicit graphs with state and checkpoints.
- Pydantic AI: typed tools and validated outputs.
- Google ADK: multi-agent apps with built-in evaluation and deployment tools.
- How to compare frameworks without being swayed by marketing.

### Key ideas

- **Every framework wraps the same loop.** Under the branding, each one sends messages to a model, runs requested tools and repeats until a stop condition. If you can find where a framework does those three things, you can debug it.
- **The OpenAI Agents SDK keeps a small set of primitives.** An agent is instructions plus tools. Handoffs pass control to another agent. Guardrails check inputs and outputs. Tracing is on by default. It works with many model providers, not only OpenAI.
- **LangGraph makes control flow explicit.** You define nodes (steps) and edges (what runs next) over a shared state object. Checkpoints let a run pause, resume or wait for a human. It is the most verbose option, and the most precise when you need exact branching.
- **Pydantic AI leans on types.** Tool arguments and final outputs are Pydantic models, so bad model output fails validation instead of leaking into your app. This builds directly on the structured outputs section.
- **Google ADK is built around multi-agent apps and tooling.** It ships agent types for sequential, parallel and loop workflows, plus a local web UI, an evaluation runner and deployment helpers.
- **Compare on things you can measure.** Lines of code for the same task, tokens per run, how easy a failed trace is to read, provider lock-in and how often the API changes. Benchmarks published by the frameworks themselves are not evidence.
- **Abstractions leak.** The 12-Factor Agents essay argues that most good production agents own their prompts, context and control flow even when they use a framework for parts of the work.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [OpenAI Agents SDK documentation](https://openai.github.io/openai-agents-python/) home page and quickstart.
   - Find the equivalent of your loop, your tool dispatch and your stop condition.
1. Read the [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) and its quickstart.
   - Sketch your "Agent Loop From Scratch" agent as a graph on paper: which nodes, which edges, what state.
1. Read the [Pydantic AI overview](https://pydantic.dev/docs/ai/overview/) and skim the [Google ADK docs](https://adk.dev/).
   - For each, note how tools are declared and how the final output is typed or validated.
1. Read [12-Factor Agents](https://github.com/humanlayer/12-factor-agents), at least the README and factors 1 through 8.
   - Write three sentences on which factors your favorite framework makes easy and which it makes hard.
1. Pick one of these four frameworks and rebuild one tool and one task from "Agent Loop From Scratch" in it. You will reuse this in "Port Your Agent".

</div>
