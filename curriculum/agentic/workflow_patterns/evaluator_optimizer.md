<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Good writers rarely get it right on the first draft. They write, reread, spot problems and revise. The **evaluator-optimizer** pattern gives an LLM system the same habit: one call generates a response, another evaluates it against clear criteria, and the feedback drives a revision. Used well, it can lift quality noticeably. Used carelessly, it burns tokens on endless loops of tiny changes. This lesson covers how to get the first without the second.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How the generate, evaluate, revise loop works.
- When the pattern helps, and when it does not.
- Writing evaluation criteria a model can apply consistently.
- Combining model feedback with code checks.
- Stopping the loop: iteration caps and "good enough" thresholds.

### Key ideas

- **Two roles, one loop.** The *generator* (optimizer) produces a draft. The *evaluator* reviews it and returns a verdict, such as pass or fail, plus specific feedback. If it fails, the generator revises using that feedback. The two roles can be the same model with different prompts.
- **It works when criteria are clear and feedback actually helps.** A good sign is that a human could improve the output by giving written feedback, and that a model can give similar feedback. Literary translation, code that must pass tests and search tasks that need several rounds are good fits. Vague goals like "make it better" are not.
- **Structured evaluator output makes the loop controllable.** Ask the evaluator for JSON with fields like `passed`, `score` and `feedback`, so your code can decide what to do next without parsing prose.
- **Mix code checks with model judgment.** If something can be checked by code (word count, required fields, tests passing), check it with code. Use the model evaluator for what code cannot judge, like tone or accuracy. This is the same split you learned in the Code Checks and LLM-as-Judge lesson.
- **Always cap the iterations.** Set a maximum (for example, three rounds) and stop early when the evaluator passes the draft. Without a cap, a picky evaluator can loop forever, and later rounds often make only tiny or even harmful changes.
- **Keep the best draft, not the last one.** Track scores across rounds and return the highest-scoring version, in case a revision gets worse.
- **Measure the gain.** Compare first drafts against final drafts on a test set. If quality barely improves, the extra calls are not worth their cost.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read "Workflow: Evaluator-optimizer" and "Combining and customizing these patterns" in [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents).
1. Work through the [evaluator-optimizer notebook](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/evaluator_optimizer.ipynb) in the Claude Cookbooks.
   - Notice how the evaluator's response is parsed and how the loop decides when to stop. Change it so the loop stops after at most three iterations.
1. Read the "Guardrails" section of OpenAI's [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf). Guardrails are closely related: an evaluator that checks output before it reaches the user.
1. Practice: build a loop that writes a product description under 80 words that mentions three given features. Use a code check for length and features and a model evaluator for tone. Log each round's score and draft, and note on which round it passed.

</div>
