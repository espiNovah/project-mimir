<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Some tasks are too hard to answer in one go. A person solving a tricky problem thinks it through, or breaks it into smaller jobs. Language models are the same. In this lesson you will learn two ways to handle hard tasks: give the model room to reason before it answers, and split one big prompt into a chain of smaller prompts where each step's output feeds the next. Prompt chaining is also your first taste of the workflow patterns you will build in the Agentic Systems path.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why letting a model reason before answering improves accuracy on hard tasks.
- The difference between prompting for step-by-step reasoning and using a model's built-in thinking feature.
- How to keep reasoning separate from the final answer so your code can parse it.
- What prompt chaining is and when to use it.
- How to pass outputs between steps and check them along the way.
- The cost and latency trade-offs of both techniques.

### Key ideas

- **Reasoning takes tokens.** A model produces its answer one token at a time, so it can only "think" by writing. Asking it to work through the problem first, for example inside `<thinking>` tags, gives it space to reason before committing to `<answer>`. This helps most on math, logic, multi-step analysis and judgment calls, and barely matters for simple lookups.
- **Built-in thinking does this for you.** Reasoning models (covered in Foundations) have a thinking mode the API can turn on. With Claude this is *extended thinking* or *adaptive thinking*, where the model decides how much to think. Prefer the built-in feature when it is available; use manual step-by-step prompts for models or settings without it.
- **Guide thinking with high-level hints, not scripts.** "Think carefully about edge cases before deciding" usually works better than dictating every step. Read the model's reasoning when outputs go wrong; it often shows exactly where the prompt misled it.
- **Prompt chaining splits a task into steps.** Instead of one giant prompt that extracts, analyzes and writes, you run three prompts in sequence. Each step is simpler, so each is more accurate and easier to debug, and you can inspect or validate the output between steps.
- **Chains give you control points.** Between steps your code can check the output (is it valid JSON? is the list empty?), stop early, or branch. This is called a *gate*, and it is a big reason chains are more reliable than one long prompt.
- **A common chain is draft, critique, revise.** One call produces a draft, a second call reviews it against criteria, and a third fixes the issues found. You will meet this again as the evaluator-optimizer pattern.
- **Nothing is free.** Thinking and chaining both add tokens and wait time. Use them where measurement shows they help, which is exactly what the Prompt Lab project asks you to check.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the reasoning and chaining parts of [Anthropic's prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
   - Focus on the sections about thinking and about chaining or multi-step work.
1. Read the [extended thinking docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) and the [adaptive thinking docs](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking) to see how built-in reasoning is turned on through the API.
   - Read the overview and the first code example on each page. Note how thinking content comes back as separate blocks from the final text.
1. Read the "prompt chaining" part of [Building effective agents](https://www.anthropic.com/research/building-effective-agents) by Anthropic.
   - Read up to the end of the "Workflow: Prompt chaining" section. The rest belongs to the Agentic Systems path.
1. Complete chapter 6 ("Precognition: Thinking Step by Step") of [Anthropic's interactive prompt engineering tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) if you skipped it in the last lesson, then the appendix notebook on chaining prompts (10.1).
1. Practice: write a two-step chain in Python. Step one extracts the key facts from a news article as a bullet list. Step two writes a three-sentence summary using only those facts. Print the intermediate output, and add a check that stops the chain if step one returns fewer than three bullets.

</div>
