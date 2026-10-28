<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Traces tell you what happened. Evals tell you whether a change made things better. The most valuable habit in LLM engineering connects the two: read real traces, find the failures, and turn each one into a test case so it can never silently come back. This lesson shows you how to go from a pile of traces to a growing eval set that reflects how your app actually fails, not how you imagined it would.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why reading real traces beats guessing at failure modes.
- How to review and label traces efficiently.
- Error analysis: grouping failures into categories and counting them.
- How to turn labeled failures into a dataset of test cases.
- Choosing the right check for each failure type.
- Closing the loop: fix, re-run and confirm.

### Key ideas

- **Look at your data first.** Before writing any eval, read 30 to 100 real traces end to end. Practitioners consistently report that this one habit finds more problems than any dashboard. Synthetic test cases miss the strange things real users type.
- **Label as you read.** For each trace, mark pass or fail and write a short note on what went wrong in plain words ("used last year's price," "called search three times with the same query"). Don't invent categories in advance.
- **Error analysis turns notes into priorities.** After labeling, group similar notes into categories and count them. A table like "wrong tool: 9, ignored retrieved doc: 6, formatting: 2" tells you what to fix first. Fix the biggest category, not the most interesting one.
- **Every failure becomes a test case.** Save the input (and any context the trace shows, such as retrieved documents or tool results) along with what a correct output looks like. Langfuse and similar tools let you add a trace to a dataset with one click; a JSONL file in your repo works just as well.
- **Match the check to the failure.** Use code checks where possible (did it call the right tool, is the JSON valid, does it contain the right number). Use an LLM-as-judge only for fuzzy qualities, and validate the judge against your own labels first, as you did in the Evals section.
- **Prove the fix.** Run the dataset before your change, make the change, run it again. Keep the old failing cases in the set forever as regression tests, so the next prompt tweak can't quietly undo the fix.
- **This is a loop, not a one-time task.** New traces bring new failures. Schedule regular review sessions and keep growing the set.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Hamel Husain's [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/), the classic write-up of the trace-review-eval loop.
   - Focus on the sections about looking at your data and building unit tests from failures.
1. Read [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) for a practical error analysis workflow.
   - Pay special attention to the parts on error analysis and building simple data viewers.
1. Read the [Langfuse datasets documentation](https://langfuse.com/docs/evaluation/experiments/datasets) to learn how to save traces as dataset items and run experiments against them.
   - Note how a dataset run links each new output back to the original item, so you can compare versions.
1. Skim the [LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/) for answers to common questions such as how many traces to review and when to use an LLM judge.
1. Practice: using the traced agent from the previous lesson, review 20 traces, label pass or fail with a note on each, and group your notes into failure categories with counts.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Using LLM-as-a-Judge for evaluation](https://hamel.dev/blog/posts/llm-judge/) walks through building a judge that agrees with a human expert, which is useful when a failure category can't be checked with code.
- [What We Learned from a Year of Building with LLMs](https://applied-llms.org/) collects lessons from practitioners, including many on evaluation and monitoring.
