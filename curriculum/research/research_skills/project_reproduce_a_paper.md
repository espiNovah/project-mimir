### Introduction

In this project you will pick a paper from The Agentic AI Reading List, reproduce one of its headline results at small scale, and write up what matched, what did not, and why, in a 2 to 4 page report formatted as a paper. This is the capstone of the Research Track and uses every skill in it: reading a paper closely, designing a fair experiment, controlling seeds and cost, and writing clearly.

Reproduction is one of the most useful things a new researcher can do. It is how many graduate students start their first project, it often turns up details the paper left out, and a careful reproduction report is strong evidence for admissions committees and research hiring managers. A reproduction that only partly succeeds, with a clear explanation, is a perfectly good outcome.

### Before you start

- Create a new repo named `mimir-reproduce-<paper>`, for example `mimir-reproduce-reflexion`. Set it up with `uv init` and add only the dependencies you need.
- Choose a paper with public code or a clearly described method, and a result that can be tested at small scale. Good options:
   - [ReAct](https://arxiv.org/abs/2210.03629) ([code](https://github.com/ysymyth/ReAct)): ReAct versus chain of thought and acting alone on a subset of HotpotQA.
   - [Reflexion](https://arxiv.org/abs/2303.11366) ([code](https://github.com/noahshinn/reflexion)): the effect of self-reflection across attempts on a subset of HumanEval-style coding problems.
   - [Tree of Thoughts](https://arxiv.org/abs/2305.10601) ([code](https://github.com/princeton-nlp/tree-of-thought-llm)): Tree of Thoughts versus chain of thought on the Game of 24.
   - [tau-bench](https://arxiv.org/abs/2406.12045) ([code](https://github.com/sierra-research/tau-bench)): how pass^k falls as k grows for one domain.
   - [DPO](https://arxiv.org/abs/2305.18290) ([code](https://github.com/eric-mitchell/direct-preference-optimization)): DPO versus the supervised fine-tuned model on a small model with a free GPU, using the [TRL DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer) and LoRA from LoRA Fine-Tuning.
   - [LLM+P](https://arxiv.org/abs/2304.11477) ([code](https://github.com/Cranial-XIX/llm-pddl)): LLM+P versus LLM-only planning, which pairs well with your LLM vs Classical Planner project.
- Your reproduction will almost certainly use a different, newer model than the paper did. That is fine, and is itself an interesting variable, but you must say so and discuss what it changes.
- Set a cost budget before you start (for example 20 US dollars of API usage, or the free GPU quota of Colab or Kaggle) and enforce it in code. Run a small pilot to estimate the full cost.
- Write the report in LaTeX on Overleaf using a conference template, as practiced in Writing Up Research.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Write `PLAN.md` before running experiments. It must state the exact claim you are reproducing (quote the paper and cite the table or figure), the original setup (model, dataset, metric, number of examples, settings), your planned setup and every difference from the original, your success criterion (for example, "the ranking of methods matches, and the gap is within 5 points"), and your cost estimate.
1. Do a third-pass reading of the paper, in the sense of Reading Papers. In your report, list every detail you needed that the paper did not specify, and what you chose.
1. Implement or adapt the method. If you use the authors' code, record the commit you used and every change you made, and explain why. If you reimplement, write tests for the parts that can be checked without a model, such as parsers, graders and scoring.
1. Implement the baseline or baselines from the paper's comparison, under exactly the same conditions as the method.
1. Run on a fixed, documented subset of the paper's evaluation data (at least 50 examples where the task allows), with at least 3 seeds or trials per condition. Save configs, seeds, model identifiers, dates and raw outputs.
1. Report results with 95% confidence intervals and a paired comparison between method and baseline, using what you learned in Experiment Design and Reproducibility.
1. Run one ablation or extension the paper did not, for example a newer model, a cheaper model, or removing one component of the method.
1. Track and report the total cost (tokens and dollars, or GPU hours) and the cost per example for each condition.
1. Write a 2 to 4 page report in paper format: abstract, introduction (what you reproduced and why), original claim, setup and differences, results (a main table or figure, with error bars), analysis of what matched and what did not, with your best explanations, limitations, and a reproducibility statement. Include the PDF in the repo.
1. Push your project to GitHub with a README that summarizes the result in three sentences, links the report, and explains how to rerun every experiment with one command each. Include the filled-in [ML Reproducibility Checklist](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist.pdf).

#### Extra credit

- Contact the paper's authors, or open a GitHub issue on their repo, about a discrepancy you found, and include the response (or lack of one) in your report.
- Reproduce a second result from the same paper, or the same result on a second dataset.
- Run a cost-accuracy analysis across three models and plot accuracy against dollars spent.
- Post your report as a blog post or a short write-up linked from your portfolio site.

</div>

### Submitting your work

A strong submission reads like a short workshop paper. A reader learns within the first paragraph what was reproduced, whether it held up, and how confident you are. Every difference from the original setup is listed, the main result has error bars and a baseline run under the same conditions, and the analysis gives specific, testable explanations for mismatches instead of "the model was different." Anyone should be able to clone the repo and rerun your experiments within the stated budget. An honest partial reproduction with a careful explanation is better than a claimed success that nobody can check.
