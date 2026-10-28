### Introduction

In this project you will build a classic text classifier the right way: a trivial baseline, a TF-IDF plus logistic regression model, a clean train/validation/test split, and evidence that you found and fixed overfitting. It is not glamorous, and that's the point. This classifier becomes the yardstick for Fine-Tune a Small Model later in this path, where a fine-tuned open model and a prompted frontier model have to beat it on the exact same test set.

You will practice the evaluation discipline from Overfitting and Baselines: never touch the test set until the end, fit preprocessing on training data only, and report numbers instead of impressions.

### Before you start

- Create a new repo named `mimir-beat-the-baseline` and run `uv init`, then `uv add scikit-learn datasets pandas matplotlib joblib`.
- Pick your dataset now, because you will reuse it in Fine-Tune a Small Model. The recommended choice is [Banking77](https://huggingface.co/datasets/PolyAI/banking77): about 13,000 short customer-support messages, each labeled with one of 77 intents such as `card_arrival` or `lost_or_stolen_phone`. It fits this curriculum well because intent routing is a real job that support agents do. Load it with `datasets.load_dataset("PolyAI/banking77")`.
- If you choose a different dataset, it must be a single-label text classification task with at least 2,000 labeled examples and a license that allows reuse. Record its source and license in your README.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Freeze your test set today

Banking77 comes with a train split and a test split. Carve a validation set out of the train split (for example 15%, stratified by label, with a fixed `random_state`), and save the exact IDs or rows of all three splits to files in your repo. Fine-Tune a Small Model will reuse these files unchanged. If the test set changes, the later comparison means nothing.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Write `split.py` that creates train, validation and test splits, saves them to `data/train.csv`, `data/val.csv` and `data/test.csv`, and prints the size of each split and the number of classes. Check for, and remove, exact duplicate texts that appear in more than one split.
1. Build a trivial baseline that always predicts the most common label in the training set. Report its validation accuracy. Every model after this must beat it.
1. Build a scikit-learn `Pipeline` of `TfidfVectorizer` and `LogisticRegression`. Using a pipeline guarantees the TF-IDF vocabulary is fit on the training split only.
1. Show overfitting, then fix it:
   - Train with very weak regularization (a large `C`, such as 1000) and report training accuracy and validation accuracy side by side.
   - Sweep `C` over at least five values (for example 0.01 to 1000), plus at least one other setting such as `ngram_range` or `min_df`, choosing only by validation accuracy.
   - Plot training and validation accuracy against `C` and save it as `overfitting.png`.
1. Only after you have chosen your final settings, retrain on train (or train plus validation) and evaluate once on the test set. Report:
   - Test accuracy and macro-averaged F1 (the average F1 across classes, so rare intents count as much as common ones).
   - A confusion matrix image, plus a list of the five most-confused label pairs.
   - The average time to predict one message, measured over the whole test set.
1. Save the trained pipeline with `joblib` to `model.joblib`, and write `predict.py` that loads it and classifies a message passed on the command line.
1. Write at least two pytest tests: one that checks the splits have no overlapping texts, and one that loads `model.joblib` and checks it predicts a sensible label for an obvious message.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned. Include a results table (trivial baseline, overfit model, tuned model) and the overfitting plot.

#### Extra credit

- Print the top 10 highest-weight words for three intents and comment on whether they make sense.
- Replace TF-IDF features with sentence embeddings from Similarity by Hand, keep logistic regression, and compare the scores.
- Train on 10%, 25%, 50% and 100% of the training data and plot test accuracy against training size. How much data does this task really need?

</div>

### Submitting your work

A strong submission makes the evaluation trustworthy at a glance: frozen split files in the repo, a one-command way to reproduce every number, a plot that clearly shows the train/validation gap closing as regularization increases, and a test score reported exactly once. Look at the most-confused pairs and say why they get confused (many Banking77 intents are near-duplicates). That kind of error analysis is what separates a portfolio project from a tutorial copy.
