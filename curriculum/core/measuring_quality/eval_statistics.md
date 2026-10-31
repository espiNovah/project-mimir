### Introduction

In the Prompt Lab, one variant scored 13 out of 15 and another scored 12. Was the first one better? Almost certainly you can't tell. Change two test emails and the ranking could flip. Every eval score is a **measurement made on a sample**: you tested some cases, not every input your users will ever send, and a model's output can change between runs as well. So every score carries some uncertainty, and the honest thing is to say how much.

This lesson gives you the small amount of statistics that AI engineers use every week. You'll learn to break a score into the kinds of mistakes behind it, put an error bar on a pass rate, use the bootstrap to get an error bar on almost anything, compare two prompts fairly, and work out how many test cases you need. None of it needs more math than square roots and averages. All of it changes what you're willing to claim, and interviewers notice an engineer who says "82%, plus or minus 11 points, on 50 cases" instead of "82%."

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The confusion matrix, and why accuracy can hide the mistakes that matter.
- Precision, recall, F1 and macro-F1.
- The standard error of a pass rate, and 95% confidence intervals.
- Bootstrap confidence intervals for any statistic.
- Paired comparisons between two prompts, and run-to-run noise.
- How many test cases you need.
- How to report a score honestly.

### The confusion matrix

Start with a yes-or-no question, such as "is this output a failure?", asked by some checker: a regex, a classifier, an LLM judge, or your Prompt Lab prompt deciding "is this a billing email?" Compare its answers with the correct labels (your own, from Error Analysis and Labeling). Every case lands in one of four boxes. First, pick which answer is the **positive class**: the thing you're trying to detect. For a judge, that's usually FAIL.

| | checker says positive | checker says negative |
| --- | --- | --- |
| **actually positive** | true positive (TP) | false negative (FN): a miss |
| **actually negative** | false positive (FP): a false alarm | true negative (TN) |

That table is the **confusion matrix**. **Accuracy**, the share of cases in the two "true" boxes, squashes it into one number, and that can be badly misleading. If 90% of outputs pass, a judge that always says PASS is 90% accurate and catches nothing. Looking at the four boxes separately shows you what kind of wrong a system is, and the two kinds usually cost different amounts. A missed failure ships a bad answer to a user; a false alarm wastes someone's time.

### Precision, recall and F1

Two rates summarize the matrix from the positive class's point of view:

- **Precision** = TP / (TP + FP). When the checker says positive, how often is it right? Low precision means many false alarms.
- **Recall** = TP / (TP + FN). Of the real positives, how many did it catch? Low recall means many misses. Recall is also called the **true positive rate (TPR)**, the name you'll see in Code Checks and LLM-as-Judge, where the matching rate for negatives is the **true negative rate (TNR)** = TN / (TN + FP).

The two pull against each other. A checker that flags everything has perfect recall and poor precision; one that flags almost nothing has the reverse. **F1** combines them: `2 * precision * recall / (precision + recall)`. It's a *harmonic* mean, which stays low if either one is low, so you can't buy a good F1 with one great number and one terrible one.

A classifier with several labels has a confusion matrix per label: treat each label in turn as "positive" and all the others as "negative." Here is that for 20 support emails:

```python
# metrics.py: per-label precision, recall and F1 for a classifier, in plain Python.
from collections import Counter

LABELS = ["billing", "bug", "feature_request", "other"]

expected = (["billing"] * 8 + ["bug"] * 6 + ["feature_request"] * 4 + ["other"] * 2)
predicted = (["billing"] * 6 + ["other"] * 2              # 2 refunds labeled other
             + ["bug"] * 5 + ["billing"]                  # 1 bug labeled billing
             + ["feature_request"] * 2 + ["bug"] * 2      # 2 requests labeled bug
             + ["other"] * 2)


def scores_for(label: str) -> dict:
    """Treat `label` as the positive class and everything else as negative."""
    pairs = Counter((e == label, p == label) for e, p in zip(expected, predicted))
    tp, fn, fp = pairs[(True, True)], pairs[(True, False)], pairs[(False, True)]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


accuracy = sum(e == p for e, p in zip(expected, predicted)) / len(expected)
print(f"accuracy {accuracy:.2f}\n")
print(f"{'label':16} tp fp fn  prec  rec   f1")
f1s = []
for label in LABELS:
    s = scores_for(label)
    f1s.append(s["f1"])
    print(f"{label:16} {s['tp']:2} {s['fp']:2} {s['fn']:2}  {s['precision']:.2f}  {s['recall']:.2f}  {s['f1']:.2f}")
print(f"\nmacro-F1 {sum(f1s) / len(f1s):.2f}")
```

```text
accuracy 0.75

label            tp fp fn  prec  rec   f1
billing           6  1  2  0.86  0.75  0.80
bug               5  2  1  0.71  0.83  0.77
feature_request   2  0  2  1.00  0.50  0.67
other             2  2  0  0.50  1.00  0.67

macro-F1 0.73
```

Each counting pair `(is it really this label?, did we predict this label?)` lands in one box. The table tells a story accuracy can't: the classifier never mislabels anything *as* a feature request (precision 1.00), but it misses half of the real ones (recall 0.50), and "other" is a dumping ground for refunds. **Macro-F1** is the plain average of the per-label F1 scores. It gives a rare label the same weight as a common one, so a model can't score well by getting only the big label right. You'll use it again in Beat the Baseline.

### The standard error of a pass rate

Now the uncertainty. Suppose 41 of 50 cases pass: a pass rate `p` of 0.82. If you ran the same system on 50 *different* cases of the same kind, you'd get a somewhat different rate. The **standard error** (SE) estimates how much that rate typically moves from sample to sample:

```text
SE = sqrt(p * (1 - p) / n)
```

where `n` is the number of cases. A **95% confidence interval** is roughly `p - 1.96 * SE` to `p + 1.96 * SE`. Informally, it's the range of true pass rates that are believable given what you measured. The number 1.96 comes from the normal distribution, the bell curve: 95% of its area lies within 1.96 standard errors of the center.

```python
# interval.py: the standard error of a pass rate, and how it shrinks with n.
import math


def pass_rate_ci(passed: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    p = passed / n
    se = math.sqrt(p * (1 - p) / n)
    return p, max(0.0, p - z * se), min(1.0, p + z * se)


p, low, high = pass_rate_ci(41, 50)
print(f"41/50: {p:.0%} (95% CI {low:.0%} to {high:.0%})\n")

print("   n   95% CI half-width at p = 0.8")
for n in [20, 50, 100, 200, 400, 1000]:
    p, low, high = pass_rate_ci(round(0.8 * n), n)
    print(f"{n:4}   +/- {(high - low) / 2:.1%}")
```

```text
41/50: 82% (95% CI 71% to 93%)

   n   95% CI half-width at p = 0.8
  20   +/- 17.5%
  50   +/- 11.1%
 100   +/- 7.8%
 200   +/- 5.5%
 400   +/- 3.9%
1000   +/- 2.5%
```

Two lessons hide in that table. On 50 cases, your 82% is honestly "somewhere from 71% to 93%," so a one- or two-point change means nothing. And because `n` sits under a square root, halving the interval takes **four times** as many cases.

<div class="lesson-note lesson-note--warning" markdown="1">

#### The formula breaks at the edges

If every case passes, `p * (1 - p)` is zero and the formula claims you're certain, which you aren't: 20 out of 20 is quite consistent with a true rate of 90%. The same problem makes the interval unreliable when `n` is small or `p` is near 0 or 1. In those cases use the bootstrap below, or the **Wilson interval**, a formula built for exactly this case. It never goes below 0% or above 100%, and for 20 out of 20 it gives roughly 84% to 100% instead of a single point. You don't need to derive it: `statsmodels` computes it with `proportion_confint(successes, n, method="wilson")`, and later projects that report pass rates on small samples ask for it.

</div>

### Bootstrap confidence intervals

The SE formula only covers a simple pass rate. What about the F1 score above, a judge's TPR, or the median latency? The **bootstrap** gives an interval for almost any statistic, with no formula:

1. Treat your sample as a stand-in for the whole population.
1. Draw a new sample of the same size from it **with replacement** (so some cases appear twice and others not at all), and compute the statistic.
1. Repeat thousands of times. The middle 95% of the results (from the 2.5th to the 97.5th percentile) is your interval.

The spread between resamples mimics the spread you'd see between fresh test sets. Always use a **fixed random seed**, so your report gives the same interval every time you rerun it. You'll see the bootstrap in action in the next section, where it does something the SE formula can't.

### Comparing two prompts

You change your prompt and the pass rate goes from 70% to 80% on 60 cases. Is B better? A tempting check is to compute each prompt's interval and see whether they overlap. That rule is overly cautious (the evals exercise set has you implement it so you can see how rarely it says yes), and it ignores a big advantage you have: both prompts ran on **the same cases**.

Because the cases are shared, compare them case by case. This is a **paired comparison**. Most cases pass under both prompts or fail under both, and they tell you nothing about which prompt is better. The evidence is in the cases where the prompts disagree. Bootstrapping the per-case *difference* uses exactly that:

```python
# compare.py: is prompt B really better than prompt A?   setup: uv add numpy
import numpy as np

# 1 = pass, 0 = fail. Both prompts ran on the SAME 60 test cases, in the same order.
a = np.array([1] * 41 + [1] * 1 + [0] * 7 + [0] * 11)  # prompt A: 42/60 = 70%
b = np.array([1] * 41 + [0] * 1 + [1] * 7 + [0] * 11)  # prompt B: 48/60 = 80%
n = len(a)

rng = np.random.default_rng(seed=0)  # fixed seed: same intervals every run


def bootstrap(stat, n_resamples: int = 10_000) -> tuple[float, float]:
    """95% percentile interval. Each resample picks n case indices with replacement."""
    idx = rng.integers(0, n, size=(n_resamples, n))
    values = stat(idx)
    return tuple(np.percentile(values, [2.5, 97.5]))


# Each prompt on its own: the two intervals overlap a lot.
for name, x in [("A", a), ("B", b)]:
    low, high = bootstrap(lambda idx: x[idx].mean(axis=1))
    print(f"prompt {name}: {x.mean():.0%} (95% CI {low:.0%} to {high:.0%})")

# Paired: resample CASES, and compute B - A on the same cases each time.
diff = b - a  # +1 where only B passed, -1 where only A passed, 0 where they agree
low, high = bootstrap(lambda idx: diff[idx].mean(axis=1))
print(f"\nB - A: {diff.mean():+.0%} (95% CI {low:+.0%} to {high:+.0%})")
print(f"cases where they disagree: B only {np.sum(diff == 1)}, A only {np.sum(diff == -1)}")
```

```text
prompt A: 70% (95% CI 58% to 82%)
prompt B: 80% (95% CI 70% to 90%)

B - A: +10% (95% CI +2% to +20%)
cases where they disagree: B only 7, A only 1
```

`rng.integers` draws all 10,000 resamples at once as a grid of case indices, and `x[idx].mean(axis=1)` scores each row, which is NumPy doing in one line what a loop would do slowly. The separate intervals overlap from 70% to 82%, so the overlap rule says "can't tell." The paired interval for the difference sits entirely above zero, because B fixed seven cases and broke only one. That's real evidence for B, though a lower end of +2% is close to zero, and eight disagreeing cases is a thin base. Before betting much on it, add cases. And always read the one case B broke.

There's a second source of noise: the model itself. Run the same prompt twice on the same cases and the score can move by a few points. Before you trust any difference, run each version at least twice and see how big the run-to-run wobble is. If the difference between prompts is no bigger than the difference between two runs of the same prompt, you haven't found anything. Averaging several runs per case reduces this noise.

### How many examples you need

Turn the SE formula around to plan a test set. To get a 95% interval of plus or minus `m` around a pass rate near `p`:

```text
n = 1.96**2 * p * (1 - p) / m**2
```

At `p = 0.8`, plus or minus 10 points needs about 62 cases, plus or minus 5 points needs about 246, and plus or minus 2 points needs about 1,500. Detecting a *difference* between two prompts needs more again, although pairing helps a lot. Some rules of thumb:

- **20 to 50 cases** catch big problems and big wins, a 15- or 20-point change. That's enough for early prompt iteration.
- **100 to 300 cases** let you trust differences of about 5 to 10 points. That's where a serious eval set for a shipped feature should be.
- **Slices are smaller than the whole.** If you report a pass rate per failure category, each category has its own `n`. Ten cases of "two topics" give you an interval of roughly plus or minus 25 points.
- **Judges need labels too.** To measure a judge's TPR you need enough real failures, not just enough cases: practitioners suggest around 100 labeled examples per failure mode.

When you can't get more cases, don't pretend. Report the interval and say what it can and can't tell you.

### Reporting a score honestly

Put these together and every number you report has the same shape: the estimate, the interval, the method and the size. "Faithfulness 82% (95% bootstrap CI 71% to 93%, n = 50)." When you compare, give the paired difference with its interval, the number of cases that changed in each direction, and the run-to-run noise. Report precision and recall, not just accuracy, whenever the two kinds of mistake cost different amounts. From the LLM-Powered API project on, every project's evidence includes an eval score with a confidence interval, so this format becomes a habit.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Classification: Accuracy, recall, precision, and related metrics](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall) from Google's Machine Learning Crash Course. It shows the confusion matrix and the precision-recall trade-off with interactive examples.
1. Read [A statistical approach to model evaluations](https://www.anthropic.com/research/statistical-approach-to-model-evals) from Anthropic. It's a short, readable version of this lesson's main ideas for model evals: standard errors, paired differences, reducing noise by resampling answers, and power analysis for deciding how many questions you need.
   - For the full detail, the paper it summarizes, [Adding Error Bars to Evals](https://arxiv.org/abs/2411.00640) by Evan Miller, is optional. Read only the abstract and the recommendations.
1. Read [How many examples do I need for an eval?](https://hamel.dev/blog/posts/evals-faq/how-many-examples-do-i-need-for-an-eval.html) from the AI evals FAQ by Hamel Husain and Shreya Shankar. It gives practitioner numbers for each stage, from error analysis to validating a judge.
1. Practice with the [evals exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals), running each from the `exercises/` folder:
   - `uv run pytest evals/04_pass_rate_se`: the standard error, a 95% interval and a cautious "is this gain real?" rule.
   - `uv run pytest evals/05_confusion_matrix`: TP, FP, FN, TN, precision, recall, F1 and TNR, including a judge that always says PASS.
   - `uv run pytest evals/06_bootstrap_ci`: a general bootstrap with a fixed seed that works for any statistic you pass in.
1. Practice: re-score your Prompt Lab with confidence intervals.
   - Grow your test set to at least 50 cases, using the tagged cases you added in Error Analysis and Labeling.
   - For each variant, report accuracy with a 95% bootstrap interval, plus per-label precision, recall and F1, and macro-F1.
   - Compare your two best variants with a paired bootstrap of the difference. Run each variant twice and report the run-to-run change.
   - Update your README's results table to show the intervals, and write two sentences on whether your original "winner" still holds up.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the four boxes of a confusion matrix, and why can accuracy be misleading?](#the-confusion-matrix)
- [What do precision and recall measure, and why is F1 a harmonic mean?](#precision-recall-and-f1)
- [What is the standard error of a pass rate, and how many more cases do you need to halve a confidence interval?](#the-standard-error-of-a-pass-rate)
- [How does the bootstrap produce a confidence interval, and why use a fixed seed?](#bootstrap-confidence-intervals)
- [Why is a paired comparison more powerful than checking whether two intervals overlap?](#comparing-two-prompts)
- [About how many cases do you need to trust a 5-point difference, and why do slices need extra care?](#how-many-examples-you-need)
- [What four things should every reported eval score include?](#reporting-a-score-honestly)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [OpenIntro Statistics](https://www.openintro.org/book/os/) is a free, complete introductory statistics textbook. Its chapters on inference for proportions explain standard errors and confidence intervals in more depth.
- [Seeing Theory: Frequentist Inference](https://seeing-theory.brown.edu/frequentist-inference/index.html) from Brown University has interactive visualizations of confidence intervals and the bootstrap.
- [Binomial proportion confidence interval on Wikipedia](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval) compares the simple interval from this lesson with the Wilson interval, which behaves better for small samples and rates near 0% or 100%.
- [McNemar's test on Wikipedia](https://en.wikipedia.org/wiki/McNemar%27s_test) is the classic statistical test for paired pass/fail results, built on the same idea as the paired comparison here: only the disagreeing cases count.
- [How Not To Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html) by Evan Miller explains why checking results repeatedly and stopping when they look good produces false wins, a trap that applies to eval iterations too.
