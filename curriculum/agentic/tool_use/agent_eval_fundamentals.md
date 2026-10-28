<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

In the core evals section you tested single model calls: given this input, is the output good? Agents are harder. They take many steps, call tools that change the world and can reach the right answer by a wrong path, or the wrong answer through steps that each looked fine. They are also not deterministic, so one passing run proves little. This lesson covers the pieces of an agent eval: tasks, graders, transcripts and environment checks, and the metrics that tell you whether an agent is reliable enough to ship.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a task, a trial, a grader and a transcript are in agent evaluation.
- Grading the outcome versus grading the path.
- Checking the final state of the environment.
- Code-based, model-based and human graders for agents.
- Why you run each task many times.
- pass@k versus pass^k.

### Key ideas

- **A task is an input plus a way to judge success.** A trial is one run of the agent on a task. The transcript (or trace) is the full record of that run: every message, tool call and result. You need all three to evaluate and debug.
- **Grade the outcome in the environment.** The strongest check looks at what the agent actually changed: is the ticket closed, is the row in the database, do the tests pass? An agent that says "Done!" without doing it should fail.
- **Grade the path when it matters.** Some failures only show in the transcript: calling a forbidden tool, taking 40 steps for a 5-step job or skipping a required approval. Add checks on the trace for these, but don't demand one exact sequence of steps, because there's often more than one good path.
- **Use the cheapest grader that works.** Code checks (exact match, state queries, tests) are fast and reliable. LLM judges handle fuzzy qualities like tone or completeness, but must be checked against human labels. Humans are the final reference and are expensive.
- **Read transcripts.** Your error analysis comes from reading real runs, noting failure types and turning the common ones into new tasks. Metrics tell you that something broke. Transcripts tell you why.
- **Run every task several times.** Agents vary from run to run. pass@k is the chance that at least one of k trials succeeds, which is useful when a person can pick the best try. pass^k is the chance that all k trials succeed, which measures consistency. For an agent that acts alone, pass^k is usually the number that matters, and it drops quickly as k grows.
- **Track cost and steps alongside success.** A change that raises success by 2% while doubling tokens may not be worth it.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) in full. It is the main resource for this section.
   - Write down the definitions of task, trial, grader, transcript and outcome in your own words.
   - Work out pass@3 and pass^3 by hand for an agent that succeeds 80% of the time on a task.
1. Read the questions about agents, traces and error analysis in Hamel Husain and Shreya Shankar's [LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/).
1. Read Hamel Husain's [field guide to rapidly improving AI products](https://hamel.dev/blog/posts/field-guide/), focusing on the parts about looking at your data.
1. Read the [Inspect agents docs](https://inspect.aisi.org.uk/agents.html) to see how an open-source eval framework runs agents in tasks with scorers.
1. Take an agent you've built, write five tasks with environment-state checks and run each one five times. Report pass@1, pass@5 and pass^5, and read every failed transcript.

</div>
