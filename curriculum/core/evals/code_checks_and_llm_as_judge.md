<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Once you know what to measure, you need a *grader*: something that looks at an output and says pass or fail. The best grader is plain code, because it is fast, free and never changes its mind. Some qualities, such as whether an answer is faithful to its sources, are too fuzzy for code, so people use another language model as the grader, a setup called *LLM-as-judge*. Judges are powerful but can be wrong in sneaky ways, so this lesson also covers how to check that your judge agrees with you.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The three kinds of graders: code, model and human.
- How to write code-based checks for format, content and rules.
- When an LLM judge is the right choice.
- How to write a judge prompt that gives reliable verdicts.
- Why binary pass/fail beats 1-to-5 scales.
- How to validate a judge against human labels.
- Common judge biases and how to reduce them.

### Key ideas

- **Use code whenever you can.** Exact match, regular expressions, JSON schema validation, "does it contain a citation," "is it under 100 words," "is the label one of the allowed values," and "does the cited ID exist" are all code. Code checks are cheap enough to run on every commit.
- **Use a model judge for judgment calls.** Faithfulness, whether an answer addresses the question, tone, and whether two answers mean the same thing are hard to express in code. A judge model gets the question, the output and clear criteria, and returns a verdict.
- **One criterion per judge, with a binary answer.** A judge asked "Is every claim in the answer supported by the sources? Answer PASS or FAIL with a one-sentence reason" is far more consistent than one asked to rate "overall quality" from 1 to 5. Binary verdicts are easier to validate, and asking for the reason first, or alongside, helps both the model and you.
- **Your judge is a model, so it needs its own eval.** Label 50 to 100 outputs yourself, run the judge on the same outputs, and compare. Report agreement, and more usefully, how often the judge catches real failures (true positive rate) and how often it wrongly flags good outputs. Iterate on the judge prompt until it agrees with you, using examples from your disagreements.
- **Split your labels to stay honest.** Use some labeled examples to write and tune the judge prompt, and keep others aside to measure it. Otherwise you are grading the judge on its own training examples.
- **Watch for known biases.** Judges tend to favor longer answers, answers in the first position when comparing two, and outputs from their own model family. Compare in both orders, ask for specific criteria rather than general preference, and consider a judge from a different provider.
- **Humans stay in the loop.** A domain expert's judgment is the ground truth that both code checks and judges approximate. Plan regular time to review samples, especially after big changes.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Using LLM-as-a-Judge For Evaluation](https://hamel.dev/blog/posts/llm-judge/) by Hamel Husain.
   - Read the whole guide. It covers working with a domain expert, writing critiques, and iterating until the judge agrees with the expert.
1. Read [Evaluating the Effectiveness of LLM-Evaluators](https://eugeneyan.com/writing/llm-evaluators/) by Eugene Yan.
   - Read the introduction, the sections on use cases and on scoring approaches, and the key takeaways. Skim the summaries of individual papers.
1. Read the grading section of [Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) in the Claude docs.
   - Compare code-based, human and model-based grading, and read the tips for model-based grading.
1. Practice: take the 30 traces from the last lesson. Write two code checks (for example, "has at least one citation" and "every cited ID was retrieved") and one LLM judge for faithfulness. Label each trace PASS or FAIL for faithfulness yourself first, then run the judge, and report how often it agreed with you. Change the judge prompt once based on the disagreements and report the new agreement on traces you did not use to tune it.

</div>
