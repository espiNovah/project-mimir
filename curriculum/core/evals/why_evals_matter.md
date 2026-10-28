<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

You have already measured things: prompt accuracy in the Prompt Lab, field accuracy in the Messy-Text Extractor, hit rate in the RAG lessons. Evaluations, or *evals*, make that habit systematic. Practitioners consistently say that the teams who succeed with AI products are the ones with good evals, because evals turn "I think it's better" into a number, and let you change prompts, models and retrieval without fear. This lesson covers where evals come from: real data, careful reading, and a well-built set of test cases.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an eval is and why AI systems need them more than ordinary software.
- What traces are and why reading them comes first.
- How error analysis turns traces into a list of real failure modes.
- How to build a golden dataset.
- Why generic metrics often mislead.
- How evals fit into the development loop.

### Key ideas

- **An eval is a test for behavior that varies.** Ordinary unit tests check that code gives exactly one right output. Model outputs vary between runs and have many acceptable answers, so evals score outputs against criteria across a whole dataset and report rates, not just pass or fail.
- **Start by looking at your data.** A *trace* is the full record of one interaction: the input, the prompt, retrieved context, model output and any tool calls. Reading 30 to 100 traces yourself, slowly, is the single most valuable eval activity, and the one people most often skip.
- **Error analysis finds what actually goes wrong.** As you read traces, write a short note on each failure (*open coding*), then group the notes into categories and count them. The categories with the biggest counts tell you what to fix and what to measure. This is better than starting from a generic list of metrics.
- **Generic metrics are a trap.** Off-the-shelf scores like "helpfulness" or "coherence" sound useful but rarely match the failures your users hit. Prefer specific, binary checks tied to your error categories, such as "Did the answer cite a source?" or "Did it mention a price not in the docs?"
- **A golden dataset is your fixed exam.** It is a set of inputs with known good answers or clear pass criteria, built from real traces, your error categories, and hand-written edge cases. Include easy cases, hard cases, adversarial cases and out-of-scope cases. Keep it under version control and grow it whenever you find a new failure.
- **Evals have levels.** Fast code checks run on every change; model-graded checks run less often; human review and A/B tests on real users sit at the top. Most of your iteration happens at the cheap levels.
- **Evals drive the loop.** Find failures, add them to the dataset, change the system, rerun the eval, compare. Without the eval, you cannot tell whether a fix for one failure broke something else.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) by Hamel Husain.
   - Read the whole post. It walks through a real case study and introduces the levels of evaluation.
1. Read [LLM Evals: Everything You Need to Know](https://hamel.dev/blog/posts/evals-faq/), the evals FAQ by Hamel Husain and Shreya Shankar.
   - Read the questions about getting started, error analysis, and how many examples you need. Skim the rest and come back to it as questions arise.
1. Read [Task-Specific LLM Evals that Do & Don't Work](https://eugeneyan.com/writing/evals/) by Eugene Yan.
   - Read the introduction and the sections on classification and extraction, summarization and factual consistency. They show which metrics hold up in practice.
1. Read [Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) in the Claude docs for a practical guide to designing test cases and grading methods.
1. Practice: run your Chat With Your Docs system on 30 questions and save each full trace (question, retrieved chunks, answer) to a file. Read every one and write a one-line note on anything wrong. Group the notes into categories, count them, and write down the top three failure modes.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) by Hamel Husain expands on error analysis and on building simple tools to view your data.
