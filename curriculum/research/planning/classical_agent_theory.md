<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

The word "agent" did not start with language models. Since the 1990s, AI researchers have defined agents formally, classified the environments they act in, and designed architectures for agents that hold beliefs, pursue goals and commit to plans. Master's courses on agents and multi-agent systems still teach this material, and it gives you precise vocabulary for describing what LLM agents do and what they lack. This lesson covers rational agents, environment types and belief-desire-intention (BDI) architectures.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The formal definition of an agent and of rationality.
- Properties of environments and why they matter for design.
- Reflex, model-based, goal-based and utility-based agents.
- Deliberative versus reactive architectures.
- The belief-desire-intention model and practical reasoning.
- How classical agent concepts map onto LLM agents.

### Key ideas

- **An agent maps percepts to actions.** An agent perceives its environment through sensors and acts on it through actuators. A *rational* agent picks the action expected to maximize its performance measure, given what it has perceived and what it knows. Rational does not mean all-knowing: it means doing the best with available information.
- **Environments differ along a few dimensions.** Fully or partially observable, deterministic or stochastic, episodic or sequential, static or dynamic, discrete or continuous, single-agent or multi-agent. A coding agent's environment is partially observable, sequential and mostly deterministic, and each property suggests different design choices.
- **Agent designs form a ladder.** Simple reflex agents use condition-action rules. Model-based agents keep internal state about parts of the world they cannot see. Goal-based agents plan toward goals. Utility-based agents weigh trade-offs between outcomes. Learning agents improve each of these from experience.
- **Pure deliberation is too slow and pure reaction is too shallow.** Early symbolic agents planned everything from first principles and could not keep up with a changing world. Reactive architectures such as Brooks's subsumption architecture skipped planning and could not pursue long-term goals. Hybrid, layered architectures combine both.
- **BDI agents separate wanting from committing.** Beliefs are what the agent thinks is true. Desires are states it would like to reach. Intentions are the desires it has committed to pursuing, along with a plan. Commitment matters: an agent that reconsiders every intention constantly never finishes anything, and one that never reconsiders keeps pursuing goals that have become impossible.
- **LLM agents are a new implementation of old ideas.** An agent's context window plays the role of beliefs, the task is its desire, and a todo list or plan file is a set of intentions. The cognitive architectures literature, such as the CoALA framework, makes this mapping explicit and helps you compare agent designs in a principled way.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [agents section of the Berkeley CS188 textbook](https://inst.eecs.berkeley.edu/~cs188/textbook/search/agents.html) for the definitions of rational agents, environment types and the PEAS (performance, environment, actuators, sensors) framework.
1. Read [BDI Agents: From Theory to Practice](https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf) by Anand Rao and Michael Georgeff (1995), the paper that connected BDI theory to working systems.
   - Read sections 1 to 3 for the motivation and the abstract interpreter. Skim the logic in the middle sections.
1. Read [Cognitive Architectures for Language Agents](https://arxiv.org/abs/2309.02427) (CoALA) by Sumers, Yao, Narasimhan and Griffiths, which describes LLM agents using concepts from cognitive science and classical AI.
   - Read sections 1 to 4, and look closely at the figure comparing existing agents in the CoALA framework.
1. Read the free [lecture slides for Michael Wooldridge's An Introduction to MultiAgent Systems](https://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/imas/distrib/pdf-index.html), a standard textbook for university agents courses. The book itself is not free, but the author publishes the slides.
   - Read lectures 2 to 5: intelligent agents, deductive reasoning agents, practical reasoning (BDI) agents, and reactive and hybrid agents.
1. Practice: pick an agent you built earlier, such as your Agent Loop From Scratch or Workflow Automation Agent project. Write a one-page analysis that gives its PEAS description, classifies its environment along each dimension, and maps its components onto beliefs, desires and intentions. Name one failure that the BDI idea of commitment and reconsideration would explain.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The belief-desire-intention software model on Wikipedia](https://en.wikipedia.org/wiki/Belief%E2%80%93desire%E2%80%93intention_software_model) gives a short overview with links to BDI programming languages and platforms.
- [Jason](https://jason-lang.github.io/) is an open-source interpreter for AgentSpeak, a BDI agent programming language still used in teaching and research.
