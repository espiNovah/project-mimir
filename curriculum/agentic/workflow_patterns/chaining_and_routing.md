<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Most useful LLM systems in production are not autonomous agents. They are workflows: a handful of model calls arranged in a fixed order by ordinary code. In this lesson you will learn the two simplest and most common patterns. **Prompt chaining** breaks a task into steps where each call builds on the last, with checks in between. **Routing** looks at an input first and sends it to the handler best suited to it. Together they solve a surprising share of real problems, at a fraction of an agent's cost.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What the "augmented LLM" building block is.
- How prompt chaining works, and when to use it.
- Programmatic gates: checking an intermediate result with code before moving on.
- How routing works, and what makes a good classifier step.
- Routing to different models to save money.
- How to tell a chain or router is better than a single prompt.

### Key ideas

- **The building block is an augmented LLM:** a model call that can use retrieval, tools and memory. Every workflow pattern is a way of wiring several of these together with code.
- **Prompt chaining splits one big task into a sequence of smaller ones.** Each call does one job (outline, then draft, then translate) and passes its output to the next. Smaller, focused prompts are easier to get right and easier to debug, at the cost of extra latency.
- **Gates keep a chain on track.** Between steps, plain code checks the intermediate output: Is it valid JSON? Is it under 200 words? Does it mention a required ID? If the check fails, retry or stop, instead of passing a bad result down the chain.
- **Routing classifies first, then specializes.** A first step decides what kind of input this is (refund request, bug report, sales question) and code sends it to a handler with a prompt, tools or data designed for that category. Without routing, tuning one prompt for one kind of input often makes it worse for the others.
- **The classifier can be small and cheap.** Routing works well with a fast model, a structured output with a fixed list of categories, and an "other" or "unsure" category that falls back to a safe default or a human.
- **Routing can also choose the model.** Send easy, common questions to a small model and hard ones to a larger model.
- **Measure against a baseline.** A chain or router is only worth it if it beats one well-written prompt on accuracy, cost or latency. Keep a set of test inputs from the Evals section approach so you can tell.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the sections "Building block: The augmented LLM," "Workflow: Prompt chaining" and "Workflow: Routing" in [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents). Note the examples it gives for when each pattern fits.
1. Open the [basic workflows notebook](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/basic_workflows.ipynb) from the Claude Cookbooks and run Example 1 (the chain) and Example 3 (the router) yourself.
   - Read the helper functions in `util.py` in the [same folder](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents) first so the notebook code makes sense.
1. Read the "Orchestration" section of OpenAI's [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) for another view of when a fixed flow beats a single agent.
1. Practice: build a two-step chain that turns a messy meeting transcript into (1) a list of decisions and then (2) a short email summarizing them. Add a gate in code that checks the list is valid JSON with at least one item before the second step runs.

</div>
