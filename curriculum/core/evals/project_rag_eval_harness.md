### Introduction

Your Chat With Your Docs system works on the questions you tried, and your Messy-Text Extractor scored well on 20 examples. Do they work on the inputs your users will send? Will they still work after next week's prompt change? In this project you will build one evaluation harness that answers both questions with numbers, for both systems.

The harness is *generic*: the same runner, graders, statistics and report code evaluate the extractor and the RAG system. Each system plugs in through a small adapter that says how to run one test case and which graders apply. You will build a RAG dataset of 50 or more questions, including trick and out-of-scope ones, measure retrieval and answers separately, prove that your LLM judges agree with you, report every score with a bootstrap confidence interval, and run the whole thing in GitHub Actions so a regression fails the build. Then you'll make one change to the RAG system and show exactly how the scores moved.

This is the project that proves you can improve an AI system on purpose instead of by luck. Hiring managers look for it.

### Before you start

- Create a new GitHub repository called `mimir-eval-harness` as a `uv` project. Install your earlier projects as dependencies (for example `uv add git+https://github.com/<you>/mimir-chat-with-your-docs` and the same for your extractor) so the harness calls the same code your apps use. If you need to change that code, change it in the original repo.
- Make sure your RAG system can return, for any question, the answer, the cited sources and the list of retrieved chunk IDs (the stable `chunk_id` values from Chunking and Vector Databases, such as `handbook.pdf:p2:0`, not auto-numbered database IDs), and that your extractor returns the validated object plus the number of retries. The harness needs all of these.
- Re-read Code Checks and LLM-as-Judge for judge validation, Evaluating RAG and Catching Regressions for the metrics and the CI gate, and Eval Statistics for the bootstrap.
- Decide whether to write the harness in plain Python, with promptfoo, with Ragas, or a mix. Plain Python is the most instructive; tools save time. Any choice is fine as long as you can explain every number it produces.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Write questions before you run them

Write the questions, reference answers and human labels from the documents, not from your system's outputs. If you write questions by looking at what the system already answers well, your scores will flatter it.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### A generic harness

1. Design one core that knows nothing about RAG or extraction. Define a small interface (for example a `Protocol` or an abstract base class) for a *task adapter* with methods such as `load_cases()`, `run(case)` and `graders()`. The core loads cases, runs them, applies each grader, saves per-case results and aggregates them. Write two adapters: `rag` and `extractor`.
1. Make the harness runnable with one command per task, for example `uv run harness rag` and `uv run harness extractor`, and record the token cost of a full run of each.
1. Write every model call the harness makes (system calls and judge calls) to a JSONL trace file with the case ID, prompt version, model, input, output, token usage and latency.

#### The datasets

1. Build a RAG dataset of at least 50 questions in `data/rag/eval_set.jsonl`. Each entry has an ID, the question, a type, the stable IDs of the chunk or chunks that contain the answer (`relevant_ids`), an exact quote from each of those chunks (`evidence`), and a short reference answer, as in Evaluating RAG and Catching Regressions. Include at least:
   - 30 normal answerable questions, a mix of easy and hard.
   - 8 trick questions, such as false premises ("Why does version 2 remove feature X?" when it does not), questions that need two passages, or questions using different words from the docs.
   - 8 out-of-scope questions the documents can't answer, where the correct response is "I don't know."
1. Use your extractor's labeled examples as `data/extractor/`, and grow the set to at least 40 examples so its confidence intervals are useful.

#### The metrics

1. RAG retrieval, with code: hit rate at 5, recall at 5 and MRR over the answerable questions. Before scoring, check that every `relevant_ids` entry exists in the current index and stop with a clear error if any is missing. Also report hit rate at 5 at the document and page level (the `location` of each ID), which survives a change to the chunker. (When the chunker changes, in Evaluating RAG and Catching Regressions)
1. RAG answers:
   - **Faithfulness:** whether every claim is supported by the retrieved passages, using an LLM judge with a binary verdict and a reason.
   - **Correctness:** whether the answer matches the reference answer, using an LLM judge or code where possible.
   - **Refusal accuracy:** the share of out-of-scope questions that got "I don't know," and the share of answerable questions that were wrongly refused.
1. Extractor: per-field accuracy, overall accuracy, schema-validity rate and retry rate, all with code graders.
1. Report **every** score with a 95% bootstrap confidence interval, and break each RAG score down by question type.

#### Validate your judges

1. Label at least 40 RAG outputs yourself for faithfulness and correctness before looking at the judges' verdicts. Split them into a dev set for tuning and a test set for measuring.
1. Report each judge's true positive rate and true negative rate on the test set, with bootstrap confidence intervals. Revise a judge's prompt at least once if either rate is below 85%, using only dev-set disagreements, and report the new numbers on the test set.

#### Regressions in CI

1. Commit a baseline results file for each task. Write a comparison script that prints per-case changes (what broke and what got fixed) and exits non-zero when a metric drops more than a tolerance below the baseline or below an absolute floor. Choose the tolerance from the run-to-run variation you measured, and explain it in the README.
1. Add a GitHub Actions workflow that runs ruff and pytest on every push, and runs the harness and comparison on every pull request, using a repository secret for your API key. Keep the CI eval small enough to finish in a few minutes. Open a pull request with a deliberately bad change (for example, retrieving only one chunk) and show that the build fails.

#### Improve one thing on purpose

1. Produce a results report (Markdown or HTML generated by the harness) with every metric and its confidence interval, plus a list of the failing cases with their outputs.
1. Run error analysis on the RAG failures: categorize them, count each category, and choose one change aimed at the largest category (for example, chunk size, contextual retrieval, the number of reranked results, or the answer prompt).
1. Make that one change, rerun the full harness, and add a before-and-after table to your report. If the change touches chunking, re-ingest, run your `relabel` script to map the labels to the new chunk IDs, fix the cases it can't map by hand, commit the relabeled dataset, and compare the two versions on location-level hit rate as well as chunk-level. List the questions that improved and the ones that regressed. Run both versions at least twice and say whether the difference is larger than the run-to-run variation and whether the confidence intervals overlap.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Evidence

Your README must show:

- A passing GitHub Actions badge, and a workflow that runs ruff and pytest on every push. Pytest covers the metric functions and graders with fakes, without calling a model.
- A link to a failed CI run from your deliberately bad pull request, with the comparison output that explains why it failed.
- A table of every metric for both tasks, each with a 95% confidence interval and the number of cases.
- Each judge's TPR and TNR on held-out labels, with confidence intervals, before and after you revised the prompt.
- A link to a committed sample of JSONL traces from one full run, and the run's total token cost.

#### Extra credit

- Run the harness in the Chat With Your Docs repo's own CI too, so a change there is gated without touching this repo.
- Compare two models for answer generation, ideally from different providers, on quality and cost per question, with confidence intervals.
- Generate extra test questions with a model, then review and fix every one by hand, and report how many generated questions you had to throw away.
- Add a third adapter for any other model-powered script you've written, and note how little code it took.

</div>

### Submitting your work

A strong README leads with the before-and-after table and a one-paragraph explanation of what you changed and why. It includes your judge TPR and TNR, a few example failures with your error categories, the link to the failed CI run, and clear instructions for reproducing a run. A short section on the adapter interface shows reviewers you designed for reuse. Readers should come away trusting your numbers because you showed how you checked them.
