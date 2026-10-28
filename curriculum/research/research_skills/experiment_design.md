<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

In the Evals and Evaluating Agents sections you learned to measure whether a system works. Research asks a sharper question: is my method better than the alternatives, by how much, and why? Answering it honestly means designing experiments that rule out other explanations, running them enough times to separate the effect from noise, and reporting everything someone else would need to check your work. This lesson covers baselines, ablations, seeds, statistics and reproducibility, with special attention to agent experiments, which are expensive and noisy.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Turning a claim into a testable hypothesis.
- Choosing strong baselines.
- Ablations: finding which part of a method causes the gain.
- Seeds, variance and how many runs you need.
- Confidence intervals, paired comparisons and significance tests for evals.
- Designing agent experiments: tasks, graders, trials and cost.
- Reproducibility checklists and honest reporting.

### Key ideas

- **Start with a falsifiable hypothesis.** "Our memory module improves agent performance" is too vague to test. "Adding the memory module raises pass@1 on our 50 multi-session tasks by at least 5 points with the same model and budget" can be shown false. Write the hypothesis and the metric down before running anything.
- **A result is only as good as its baseline.** Compare against the simplest thing that could work (a plain prompt, a single agent, the previous method) and tune it as carefully as your own method. A weak baseline is the most common way papers overstate gains.
- **Ablations explain where the gain comes from.** Remove or replace one component at a time while keeping everything else fixed. If the full method beats the baseline but removing the "key" component changes nothing, the gain came from somewhere else, such as a longer prompt or more tokens.
- **Every run is a sample.** Model sampling, random seeds, data order and even API-side changes make results vary. Run multiple seeds or trials, report the mean with a confidence interval, and show the spread. For LLM evals, the standard error of a pass rate shrinks with the square root of the number of tasks, so small eval sets give wide intervals.
- **Use paired comparisons when you can.** When two systems run on the same tasks, analyze per-task differences instead of comparing two averages. Pairing removes the variation that comes from some tasks being harder than others and often turns a "no difference" result into a clear one, or the reverse.
- **Agent experiments have extra moving parts.** You are measuring a task, a harness (tools, prompts, limits), a grader and a model together. Isolate trials from each other so leftover state cannot leak, read transcripts to check that graders reward real success, report pass@k or pass^k depending on whether you care about one success or consistent success, and track cost and latency alongside accuracy.
- **Report so others can reproduce.** Share code, configs, seeds, model versions and dates, prompts, the exact dataset, compute and cost, and negative results. Checklists such as Joelle Pineau's ML Reproducibility Checklist and the NeurIPS paper checklist make this routine.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), a practical guide to designing tasks, graders and trials for agent evaluations.
   - Read it in full. Note its definitions of task, trial, grader and transcript, and its advice on pass@k versus pass^k.
1. Read [Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640) by Evan Miller. Anthropic's [summary of the paper](https://www.anthropic.com/research/statistical-approach-to-model-evals) is a shorter entry point.
   - Read sections on the central limit theorem, clustered standard errors, paired differences and power analysis. Work through one formula numerically with your own numbers.
1. Read [Joelle Pineau's Machine Learning Reproducibility Checklist](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist.pdf) and the [NeurIPS paper checklist guidelines](https://neurips.cc/public/guides/PaperChecklist). For context on why they exist, read the introduction of [Improving Reproducibility in Machine Learning Research](https://arxiv.org/abs/2003.12206), the report on the NeurIPS 2019 reproducibility program.
1. Read [Deep Reinforcement Learning that Matters](https://arxiv.org/abs/1709.06560) by Henderson and colleagues. It shows how seeds, hyperparameters and implementations can change RL conclusions, and the lessons carry over directly to agents.
1. Practice: take results from a project you have already completed, such as Research Agent, One vs Many or Train an RL Agent. Rerun the key comparison with enough trials to compute 95% confidence intervals, do a paired analysis, and estimate how many tasks you would need to detect a 3-point difference reliably. Fill in the reproducibility checklist for that project and fix the gaps it reveals.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Deep Learning Tuning Playbook](https://github.com/google-research/tuning_playbook) from Google Research describes a systematic process for tuning and comparing models.
- [A Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/) by Andrej Karpathy is a practitioner's guide to building experiments step by step and catching silent bugs.
