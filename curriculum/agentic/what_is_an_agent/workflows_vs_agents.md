<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

"Agent" is one of the most overused words in AI right now. Some people use it for any app that calls a language model. Others reserve it for systems that run for hours on their own. Before you build one, you need a clear picture of what the word means, what the alternatives are, and how to choose between them. Getting this choice right is the single biggest factor in whether your system is cheap, reliable and easy to debug, or none of those things.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The spectrum from a plain program to a single LLM call, a workflow, and a fully autonomous agent.
- What makes a system a workflow versus an agent.
- The trade-offs between predictability and flexibility.
- How to decide which approach a task actually needs.
- Why "start simple" is the default advice from people who build these systems for a living.

### Key ideas

- **There is a spectrum, not a binary.** At one end is ordinary code with no model at all. Next is a single LLM call (for example, "summarize this email"). Then come **workflows**, where your code calls the model several times along a path you wrote in advance. At the far end are **agents**, where the model itself decides which step to take next and when it is finished.
- **The key question is who controls the flow.** In a workflow, your code decides the order of steps. In an agent, the model does. Anthropic's definition is a good one to memorize: workflows orchestrate LLMs and tools "through predefined code paths," while agents "dynamically direct their own processes and tool usage."
- **A practical working definition:** an agent is a model using tools in a loop to achieve a goal. If there is no loop, or the model cannot choose its own actions, it is not really an agent.
- **Autonomy costs something.** Agents use more tokens, take longer, are harder to test and can compound their own mistakes over many steps. Workflows are cheaper, faster and more predictable, but they break when a task does not fit the path you designed.
- **Agents earn their place on open-ended tasks** where you cannot predict the number or order of steps in advance: debugging a codebase, researching a question across many sources, or working through a messy inbox.
- **Start with the simplest thing that works.** Many problems that seem to need an agent are solved by one well-prompted call, or by retrieval plus one call. Add steps, then loops, only when you can measure that the simpler version falls short.
- **No-LLM is a real option.** If a task has clear rules (validate a postcode, sort by date), plain code is cheaper, faster and always correct. Using a model there adds cost and a new way to fail.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) from Anthropic. This is the most cited practical article on the topic, and the rest of this path borrows its vocabulary.
   - Read the introduction through "When (and when not) to use agents" carefully. Skim the workflow patterns for now; you will study them in the Workflow Patterns section.
1. Read Simon Willison's [Agents: tools in a loop to achieve a goal](https://simonwillison.net/2025/Sep/18/agents/), a short post explaining why this definition is the one worth using.
1. Read the "What is an agent?" and "When should you build an agent?" sections of OpenAI's [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf). It is useful to see a second provider reach almost the same conclusions.
1. Practice: write down five tasks from your own life or job (for example, "rename photos by date" or "answer customer emails about refunds"). For each, decide whether it needs no LLM, a single call, a workflow or an agent, and write one sentence on why. Keep this list; you will reuse it in the Project: Workflow or Agent?

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Lilian Weng's [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) (2023) is an older but influential survey of agent components: planning, memory and tool use. Some of its examples have aged, but the mental model still holds.
