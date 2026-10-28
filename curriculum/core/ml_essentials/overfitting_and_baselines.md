### Introduction

A model that scores 99% on the data it was trained on can still be useless on new data. That gap is called **overfitting**, and spotting it is one of the most practical skills in machine learning. The cure for fooling yourself is the same one you learned in Why Evals Matter: measure on data the model has never seen, and always compare against something simple.

This lesson is about two habits that carry straight over to LLM work. First, know how to detect and reduce overfitting. Second, build a cheap **baseline** before anything fancy, so you know whether the fancy thing is actually worth its cost. You'll continue with the 20 Newsgroups classifier from Supervised Learning, and finish by comparing two classifiers the way you'll compare a classic model and an LLM in Beat the Baseline: same cases, macro-F1, and a confidence interval on the difference.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Overfitting and underfitting, and the bias-variance tradeoff.
- Reading train versus validation scores to diagnose a model.
- Regularization and how it limits model complexity.
- Pipelines and cross-validation for small datasets.
- Data leakage and how it inflates scores.
- Trivial and simple baselines, and why they come first.
- Comparing a classic model with an LLM classifier, fairly.

### Overfitting and underfitting

A model's job is to **generalize**: to do well on examples it hasn't seen. Training only shows it the training set, so there are two ways to fail.

- **Overfitting** means memorizing instead of generalizing. The model fits noise and quirks in the training data, like a student who memorizes last year's exam answers and fails this year's paper. The telltale sign is a high training score with a much lower validation score.
- **Underfitting** is the opposite. The model is too simple, or too constrained, to capture the real pattern, so both scores are low. It's the student who skimmed the textbook.

These two failures pull against each other, and the tension has a name: the **bias-variance tradeoff**. **Bias** is error from a model that's too simple to represent the pattern (underfitting). **Variance** is error from a model so flexible that it changes a lot depending on which examples it happened to see (overfitting). Making a model more flexible lowers bias and raises variance. Your job is to find the setting in between that does best on new data.

You've met a version of this already. A prompt tweaked until it passes all 15 of your Prompt Lab cases may have "overfit" to those 15 cases. The fix is the same in both worlds: judge on data you didn't tune on.

### Reading train and validation scores

The gap between the training score and the validation score is your diagnostic:

| Training score | Validation score | Diagnosis | What to try |
| --- | --- | --- | --- |
| High | Much lower | Overfitting | Regularize more, simplify features, get more data |
| Low | Low | Underfitting | Regularize less, add features or a more flexible model |
| High | Close behind | Good shape | Stop tuning, evaluate on test |

Here's that diagnostic run for real. The script trains the same TF-IDF plus logistic regression classifier with six different settings of `C` (explained in the next section), and prints a trivial baseline first for reference. The official 20 Newsgroups test split stays sealed; a validation set is carved out of the training split.

```python
# tune.py: baselines, overfitting and cross-validation.   setup: uv add scikit-learn
from sklearn.datasets import fetch_20newsgroups
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline

CATEGORIES = ["comp.graphics", "rec.autos", "sci.med", "talk.politics.guns"]
CLEAN = ("headers", "footers", "quotes")
train = fetch_20newsgroups(subset="train", categories=CATEGORIES, remove=CLEAN, random_state=0)

# Train / validation split. The official "test" subset stays sealed until the end.
X_train, X_val, y_train, y_val = train_test_split(
    train.data, train.target, test_size=0.2, stratify=train.target, random_state=0)


def report(name, model):
    model.fit(X_train, y_train)
    tr = model.score(X_train, y_train)
    va = model.score(X_val, y_val)
    f1 = f1_score(y_val, model.predict(X_val), average="macro")
    print(f"{name:24} train {tr:.3f}   val {va:.3f}   val macro-F1 {f1:.3f}")


# 1. Trivial baseline: always predict the most common training label.
report("majority class", DummyClassifier(strategy="most_frequent"))

# 2. Overfitting and underfitting: sweep C (smaller C = stronger regularization).
for C in [0.01, 0.1, 1, 10, 100, 1000]:
    pipe = make_pipeline(TfidfVectorizer(min_df=2, stop_words="english"),
                         LogisticRegression(C=C, max_iter=2000))
    report(f"tfidf + logreg C={C}", pipe)

# 3. Five-fold cross-validation on the training split, for one setting.
#    The pipeline refits TF-IDF inside every fold, so no fold leaks into another.
pipe = make_pipeline(TfidfVectorizer(min_df=2, stop_words="english"),
                     LogisticRegression(C=10, max_iter=2000))
scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="f1_macro")
print(f"\n5-fold macro-F1 at C=10: {scores.round(3)}  mean {scores.mean():.3f} +/- {scores.std():.3f}")
```

```text
majority class           train 0.256   val 0.256   val macro-F1 0.102
tfidf + logreg C=0.01    train 0.757   val 0.698   val macro-F1 0.633
tfidf + logreg C=0.1     train 0.945   val 0.866   val macro-F1 0.867
tfidf + logreg C=1       train 0.974   val 0.899   val macro-F1 0.900
tfidf + logreg C=10      train 0.979   val 0.892   val macro-F1 0.893
tfidf + logreg C=100     train 0.979   val 0.890   val macro-F1 0.891
tfidf + logreg C=1000    train 0.979   val 0.886   val macro-F1 0.886

5-fold macro-F1 at C=10: [0.88  0.895 0.89  0.904 0.893]  mean 0.892 +/- 0.008
```

Read it top to bottom. The majority-class baseline gets 25.6%, which is just the share of the most common topic: anything below that is broken. At `C=0.01` both scores are low, so the model is underfitting. As `C` grows, the training score climbs to 0.979 and stops (it can't reach 1.0 because about 70 training posts are empty or nearly empty once headers are stripped). The validation score peaks at `C=1` and then slowly falls, while the gap between the two widens from 0.075 to 0.093. That widening gap is overfitting starting. You'd pick `C=1`, chosen by validation score alone.

The effect here is gentle, because logistic regression on TF-IDF is a fairly well-behaved model. On a small dataset with many classes, such as Banking77 in Beat the Baseline, the gap at a very large `C` is much more dramatic. You'll plot it.

### Regularization

**Regularization** penalizes complexity. Instead of minimizing only the loss, the model minimizes the loss plus a penalty for having large weights. **L2 regularization**, the default in scikit-learn, adds the sum of the squared weights to the loss. Large weights are what let a model latch onto a single rare word that happened to appear in one training post, so penalizing them pushes the model toward smaller, smoother weights spread across many words.

In scikit-learn's `LogisticRegression`, the parameter `C` is the *inverse* of regularization strength. This trips everyone up at first:

- **Small `C`** (0.01): strong regularization, a simple model, risk of underfitting.
- **Large `C`** (1000): weak regularization, a flexible model, risk of overfitting.

There are other ways to limit complexity. For text, the vectorizer's settings matter as much as `C`. `min_df=2` drops words seen in only one document. `max_features` caps the vocabulary size. `ngram_range=(1, 2)` adds two-word phrases such as "not working", which gives the model more to work with and more ways to overfit. Treat each one as a setting to choose on validation data.

### Pipelines and cross-validation

`tune.py` used `make_pipeline` to chain the vectorizer and the classifier into one object. A **pipeline** has `fit`, `predict` and `score` like any model. When you call `fit`, it fits the vectorizer on the training data, transforms it, and fits the classifier. When you call `predict`, it only transforms. That makes the "fit preprocessing on training data only" rule automatic, which matters more than it sounds, as the next section shows.

A single validation split has a weakness: on a small dataset, the score depends a lot on which examples happened to land in it. **Cross-validation** gives a steadier estimate. Split the training data into k **folds** (often 5), train k times while holding out a different fold each time, and average the k scores. The output above shows five fold scores from 0.880 to 0.904. That spread of about 2 points is a useful reminder of how much one split can move your number.

Cross-validation multiplies training time by k, which is fine for a model that trains in a second. Use it to choose settings like `C`. scikit-learn's `GridSearchCV` automates the sweep: give it a pipeline and a grid of values, and it cross-validates every combination. Never use cross-validation to replace the final held-out test, because once you choose settings by cross-validated score, that score is no longer an unbiased estimate either.

### Data leakage

**Data leakage** means information the model shouldn't have gets into training, and the score comes out better than it would be in real use. It's silent: nothing crashes, the numbers just look great. Common causes:

- **Duplicates across splits.** The same message appears in train and test, so the model is tested on something it memorized. Support data is full of near-identical messages. Beat the Baseline asks you to remove exact duplicates that cross splits.
- **Preprocessing fit on all the data.** Calling `fit_transform` on the whole dataset before splitting lets the test set shape the vocabulary and IDF weights. Pipelines prevent this.
- **A feature that encodes the answer.** Something in the input gives the label away in a way that won't hold up on real data.

20 Newsgroups has a famous example of the third kind. Every raw post starts with email headers like `From: jbalgley@bbn.com` and `Organization: Bolt Beranek and Newman`. Train on posts with headers and the model learns "this person always posts in graphics" instead of anything about graphics. Here's the same `C=1` pipeline scored once on the official test split, with and without the headers, footers and quoted replies removed:

| Training and test text | Test accuracy |
| --- | --- |
| Raw posts, headers included | 0.948 |
| Headers, footers and quotes removed | 0.876 |

Most of those seven points came from the headers and signatures: who was posting, not what they wrote. A new post from a new person gets none of that help. That's why the code in these lessons always passes `remove=(...)`.

Notice too that the honest test score (0.876 accuracy, and 0.876 macro-F1) is lower than the 0.899 validation score that picked `C=1`. Some of that drop is the optimism of choosing by validation score. Some is that the official test posts were written later than the training posts, so topics had drifted. Real users drift too, which is why the test set should look as much like future data as you can make it.

### Baselines come first

Before you build anything clever, build something simple and measure it. Two kinds of baseline matter:

- A **trivial baseline** needs no learning at all. Always predicting the most common class (`DummyClassifier(strategy="most_frequent")`) gives you the floor. On a dataset where 95% of messages are "not urgent," it scores 95% accuracy and 0 recall on urgent messages, which tells you immediately that accuracy is the wrong headline metric.
- A **simple baseline** is the cheapest thing that might actually work. That's often a handful of keyword rules (someone on the team probably wrote these already), or TF-IDF plus logistic regression, which takes minutes and often gets surprisingly close to the best published results on text classification.

Every system after that has to beat the baseline, and by enough to justify what it costs. An LLM classifier, or a fine-tuned model, costs more per call, adds latency and adds moving parts. If it beats TF-IDF by 1 point of macro-F1 with an interval that crosses zero, it hasn't earned its place. If it beats it by 15 points, it might have.

### Comparing against an LLM classifier

To compare two classifiers honestly, use the tools from Eval Statistics: run both on **the same cases**, report macro-F1 for each with an interval, and bootstrap the **paired difference**. Here's that comparison between a hand-written keyword baseline and the tuned model, on the 464 validation posts:

```python
# compare.py: a keyword baseline vs the tuned model, with a paired bootstrap.
# setup: uv add scikit-learn numpy
import re

import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

CATEGORIES = ["comp.graphics", "rec.autos", "sci.med", "talk.politics.guns"]
train = fetch_20newsgroups(subset="train", categories=CATEGORIES,
                           remove=("headers", "footers", "quotes"), random_state=0)
X_train, X_val, y_train, y_val = train_test_split(
    train.data, train.target, test_size=0.2, stratify=train.target, random_state=0)

# A simple baseline: hand-written keyword rules, checked in order.
RULES = [
    (3, r"\b(guns?|firearms?|weapons?|nra|amendment)\b"),
    (2, r"\b(doctor|disease|patients?|medical|pain|drugs?)\b"),
    (1, r"\b(cars?|engine|tires?|brakes?|dealer|mph)\b"),
    (0, r"\b(graphics|image|jpeg|gif|pixels?|3d|polygon)\b"),
]


def keyword_classify(text: str) -> int:
    for label, pattern in RULES:
        if re.search(pattern, text.lower()):
            return label
    return 1  # no rule fired: guess the most common class (rec.autos)


keyword_pred = np.array([keyword_classify(t) for t in X_val])
model = make_pipeline(TfidfVectorizer(min_df=2, stop_words="english"),
                      LogisticRegression(C=1, max_iter=2000)).fit(X_train, y_train)
model_pred = model.predict(X_val)
y = np.asarray(y_val)


def macro_f1(pred, idx):
    return f1_score(y[idx], pred[idx], average="macro")


# Paired bootstrap: resample the SAME validation cases for both systems each time.
rng = np.random.default_rng(seed=0)
n = len(y)
diffs, a_scores, b_scores = [], [], []
for _ in range(2000):
    idx = rng.integers(0, n, size=n)
    a, b = macro_f1(keyword_pred, idx), macro_f1(model_pred, idx)
    a_scores.append(a)
    b_scores.append(b)
    diffs.append(b - a)

everything = np.arange(n)
for name, pred, boot in [("keyword rules", keyword_pred, a_scores),
                         ("tfidf + logreg", model_pred, b_scores)]:
    low, high = np.percentile(boot, [2.5, 97.5])
    print(f"{name:15} macro-F1 {macro_f1(pred, everything):.3f}  (95% CI {low:.3f} to {high:.3f})")
low, high = np.percentile(diffs, [2.5, 97.5])
print(f"difference      {np.mean(diffs):+.3f}  (95% CI {low:+.3f} to {high:+.3f}), n = {n}")
```

```text
keyword rules   macro-F1 0.559  (95% CI 0.510 to 0.605)
tfidf + logreg  macro-F1 0.900  (95% CI 0.870 to 0.925)
difference      +0.341  (95% CI +0.295 to +0.387), n = 464
```

The keyword rules are a real baseline, and a humbling one for whoever wrote them: long posts mention "pain" or "image" in passing, and the first rule that fires wins. The trained model beats them by 34 points, with an interval far from zero. That's a clear win.

The comparison you'll make in Beat the Baseline, and again in the ML elective's fine-tuning project, swaps in an LLM as one of the systems. Nothing about the statistics changes. You collect a prediction array from each system, in the same order, and pass them to the same bootstrap. The LLM side looks like this, using the Claude API from Your First API Call and the [cheap model](#/models):

```python
# llm_classify.py: the same task as an LLM call.   setup: uv add anthropic
import os
import time

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
CATEGORIES = ["comp.graphics", "rec.autos", "sci.med", "talk.politics.guns"]
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

SYSTEM = ("Classify the forum post into exactly one of these topics. "
          "Reply with the topic name only.\n" + "\n".join(CATEGORIES))


def classify(text: str) -> tuple[int, dict]:
    """Return (label index or -1 if invalid, a small trace of cost and latency)."""
    start = time.perf_counter()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        output_config={"effort": "low"},   # a simple task: think as little as possible
        # The first 4,000 characters are plenty to tell the topic, and cap the cost.
        messages=[{"role": "user", "content": text[:4000]}],
    )
    # The response may start with a thinking block, so take the first text block.
    answer = next((b.text for b in response.content if b.type == "text"), "").strip()
    trace = {
        "seconds": time.perf_counter() - start,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    label = CATEGORIES.index(answer) if answer in CATEGORIES else -1  # invalid = wrong
    return label, trace
```

Three details make the comparison fair. An answer that isn't one of the labels becomes `-1`, which counts as wrong, so the LLM isn't flattered by ignoring its bad outputs. The trace records tokens and seconds for every call, so you can report cost per 1,000 calls and median latency next to quality. And you develop the prompt on the validation set only; the test set is run once, for every system, at the end.

Then put everything in one table: macro-F1 with its interval, cost per 1,000 messages and median latency, for the trivial baseline, the classic model and the LLM. That table is the deliverable of Beat the Baseline, and it is the kind of evidence that settles "should we use an LLM for this?" in a design review.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Overfitting module of Google's Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course/overfitting) for the core picture of generalization, with interactive plots of training and validation loss.
   - Read the pages on dividing datasets, overfitting, and [L2 regularization](https://developers.google.com/machine-learning/crash-course/overfitting/regularization), and do the interactive exercises.
1. Read the "Model selection and evaluation" material linked from [scikit-learn's Getting Started guide](https://scikit-learn.org/stable/getting_started.html), especially the section on cross-validation.
   - Pay attention to how pipelines prevent data leakage by fitting preprocessing inside each fold. The [Common pitfalls page](https://scikit-learn.org/stable/common_pitfalls.html) has a short, concrete section on data leakage that's worth reading too.
1. Skim the parameters section of [scikit-learn's LogisticRegression reference](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html).
   - Find `C`, `penalty` and `max_iter`, and note which direction of `C` means more regularization.
1. Practice: take the classifier you built in Supervised Learning and train it with `C` set to 0.01, 1 and 100. For each, print training accuracy and validation accuracy side by side. Write two sentences on which setting overfits and which underfits.
   - Then make overfitting easier to see: train on only the first 200 training posts and add `ngram_range=(1, 2)`. Does the gap at `C=100` grow?
   - Use `GridSearchCV` with `cv=5` to choose `C` and `min_df` together, and compare its choice with yours.
1. Practice the statistics behind the comparison with the [evals exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals): run `uv run pytest evals/05_confusion_matrix` and `uv run pytest evals/06_bootstrap_ci` from the `exercises/` folder if you haven't already, then adapt `compare.py` to bootstrap the difference in accuracy as well as macro-F1.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between overfitting and underfitting, and how do they relate to bias and variance?](#overfitting-and-underfitting)
- [A model scores 0.99 on training data and 0.71 on validation. What's wrong, and what would you try?](#reading-train-and-validation-scores)
- [In `LogisticRegression`, does a smaller `C` mean more or less regularization?](#regularization)
- [How does a pipeline prevent leakage during cross-validation, and why shouldn't cross-validation replace the test set?](#pipelines-and-cross-validation)
- [Name three ways data can leak into training, and explain the 20 Newsgroups header example.](#data-leakage)
- [What is the difference between a trivial baseline and a simple baseline, and why build both first?](#baselines-come-first)
- [How do you compare a classic model and an LLM classifier fairly, and what goes in the results table?](#comparing-against-an-llm-classifier)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [scikit-learn's cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html) covers the different ways to split data, including stratified and grouped folds for when examples aren't independent (for example, several messages from the same customer).
- [StatQuest's video on the bias-variance tradeoff](https://www.youtube.com/watch?v=EuBBz3bI-aA) gives a short, visual explanation of the idea behind overfitting.
