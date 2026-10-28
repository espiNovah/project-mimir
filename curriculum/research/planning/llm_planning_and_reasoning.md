<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Every agent you have built so far plans in some sense: it decides which tool to call next, and in what order. But can a language model actually plan, in the sense the previous two lessons defined? The research answer is nuanced. LLMs are good at proposing plausible plans and translating between natural language and formal languages, and unreliable at guaranteeing that a long plan is correct. This lesson covers the main approaches to LLM planning and reasoning, the evidence about where they fail, and the hybrid designs that combine LLMs with classical planners and verifiers.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Chain-of-thought prompting and self-consistency.
- ReAct: interleaving reasoning with actions.
- Tree of Thoughts: search over reasoning steps.
- LLM+P: translating problems into PDDL for a classical planner.
- Evidence that LLMs struggle with autonomous planning.
- LLM-Modulo frameworks: LLMs as generators, verifiers as judges.
- How reasoning models change, and do not change, the picture.

### Key ideas

- **Chain of thought spends tokens on reasoning.** Prompting a model to write out intermediate steps improves accuracy on multi-step problems. Self-consistency samples several reasoning chains and takes a majority vote on the answer, trading cost for reliability.
- **ReAct interleaves thinking and acting.** The model alternates between a reasoning trace and an action (such as a search or tool call), and the observation from each action feeds the next thought. This is the pattern behind the agent loop you have been building since Tool Use.
- **Tree of Thoughts makes reasoning a search problem.** Instead of one chain, the model proposes several candidate next steps, evaluates them, and explores the tree with breadth-first or depth-first search, backtracking from dead ends. It brings the search algorithms from Search and Planning to LLM reasoning, at the cost of many more model calls.
- **LLM+P lets each system do what it is good at.** The LLM translates a natural-language problem into a PDDL problem file, a classical planner finds a provably correct plan, and the LLM translates the plan back. On standard benchmarks this beats asking the LLM for a plan directly, provided the translation is right.
- **LLMs alone are weak autonomous planners.** Benchmarks such as PlanBench show that models often produce plans that look right but violate preconditions, especially when object names are obfuscated so the model cannot rely on memorized examples. Kambhampati and colleagues argue that LLMs are better seen as approximate knowledge sources than as planners.
- **LLM-Modulo frameworks add a verifier loop.** The LLM proposes a plan, an external verifier (such as a plan validator, test suite or simulator) checks it and returns specific errors, and the LLM revises. Correctness comes from the verifier, not from the model. This is the same idea as running tests in a coding agent.
- **Reasoning models raise the ceiling, not the guarantee.** Models trained with RL on verifiable rewards plan much better than earlier models, but their accuracy still drops on longer problems, and they cost far more per problem than a classical planner. Measuring this trade-off is the point of the project in this section.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629).
   - Read sections 1 to 3 and look at the example trajectories. Compare the ReAct format with the agent loop you built in Agent Loop From Scratch.
1. Read [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601).
   - Read sections 1 to 4, focusing on how thoughts are generated, evaluated and searched. Note the cost per problem compared with chain of thought.
1. Read [LLM+P: Empowering Large Language Models with Optimal Planning Proficiency](https://arxiv.org/abs/2304.11477).
   - Read the method section and the results table. Note which domains the LLM-alone baseline fails on and why.
1. Read [LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks](https://arxiv.org/abs/2402.01817) by Kambhampati and colleagues.
   - Read it in full. Write down the roles it assigns to LLMs and to external critics, and one claim you think newer reasoning models might weaken.
1. Skim [PlanBench](https://arxiv.org/abs/2206.10498) to see how planning ability is measured, including the "Mystery Blocksworld" variant with obfuscated names. You will reuse this idea in the project.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) and [Self-Consistency Improves Chain of Thought Reasoning](https://arxiv.org/abs/2203.11171) are the original papers behind the first key idea.
- [On the Planning Abilities of Large Language Models: A Critical Investigation](https://arxiv.org/abs/2305.15771) gives detailed failure analyses of LLM plans in Blocksworld and related domains.
- [The LLMs-Planning repository](https://github.com/karthikv792/LLMs-Planning) contains the PlanBench code and problem instances.
- [The LLM+P code](https://github.com/Cranial-XIX/llm-pddl) shows exactly how the authors prompted the model to write PDDL.
