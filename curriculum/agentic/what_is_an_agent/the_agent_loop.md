<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Every agent, from a ten-line script to a coding assistant that runs for an hour, is built around the same small idea: a loop. The model looks at the situation, picks an action, your code carries it out, and the result goes back to the model. Then it happens again. In this lesson you will learn the parts of that loop, where it goes wrong, and, most importantly, how to make it stop.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The think, act, observe cycle and where it came from.
- What the model sees on each turn of the loop.
- Stop conditions: how an agent decides it is done, and how you stop it when it is not.
- Why agents get stuck, repeat themselves or wander off.
- How to design a loop around a clear goal and a way to check progress.

### Key ideas

- **The loop has three steps.** *Think*: the model reasons about what to do next. *Act*: it requests an action, such as calling a tool. *Observe*: your code runs the action and adds the result to the conversation. The 2022 ReAct paper ("Reasoning and Acting") showed that interleaving reasoning with actions works better than doing either alone, and almost every agent since uses this shape.
- **The conversation is the agent's state.** The model has no memory between API calls. On each turn your code sends the whole history: the goal, every earlier action and every result. That is why long-running agents eventually fill up their context window, a problem you will tackle in the Memory & Context Management section.
- **Your code, not the model, runs the loop.** The model only *requests* actions. Your program decides whether to execute them, what to send back and whether to go around again. This gives you the control points for safety, logging and limits.
- **There are two kinds of stop conditions.** The *natural* stop is when the model says it is finished (for example, it replies with text and no tool request). The *safety* stops are limits you enforce no matter what: a maximum number of steps, a token or cost budget, a time limit, or a human saying "stop." Never ship a loop without at least a step cap.
- **Agents need ground truth.** A loop works best when each observation tells the model something real about its progress: a test passed, a file now exists, a search returned nothing. Without this feedback, the model guesses, and errors compound.
- **Common failure modes** include repeating the same action, calling a tool with bad arguments over and over, declaring success too early, and drifting away from the original goal. Printing every step of the loop is the cheapest way to spot all of them.
- **Designing the loop is a real skill.** Good loops have a clear goal, tools that give useful feedback, a safe environment to act in, and a defined finish line the agent can check for itself.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Simon Willison's [Designing agentic loops](https://simonwillison.net/2025/Sep/30/designing-agentic-loops/). It is a practical look at what makes a loop productive: clear goals, the right tools and a safe place to run them.
   - Pay attention to his points about running agents in a safe environment ("YOLO mode") and about giving the agent a way to test its own work.
1. Read the abstract and introduction of [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629). You do not need to follow the experiments. The goal is to see where the think, act, observe pattern comes from.
   - Look at the figure comparing "Reason only," "Act only" and "ReAct" and notice what each one gets wrong.
1. Reread the "Agents" section of Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) and note every stop condition and checkpoint it mentions.
1. Practice: on paper, trace an agent loop for the goal "Find out tomorrow's weather in my city and tell me whether to bring an umbrella." Write each think, act and observe step. Then write down two things that could make the loop run forever, and the stop condition that would catch each one.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Lilian Weng's [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) covers ReAct alongside other early planning techniques, with clear diagrams.
