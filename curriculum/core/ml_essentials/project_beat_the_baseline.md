### Introduction

In this project you will build a classic text classifier the right way: a trivial baseline, a TF-IDF plus logistic regression model, a clean train/validation/test split, and evidence that you found and fixed overfitting. Then you'll put it head to head with an LLM classifier on the same test cases and decide, with numbers, which one you'd ship. It is not glamorous, and that's the point. If you take the ML elective, this classifier also becomes the yardstick for its Fine-Tune a Small Model project, where a fine-tuned open model has to beat it on the exact same test set.

You will practice the evaluation discipline from Overfitting and Baselines: never touch the test set until the end, fit preprocessing on training data only, compare systems on the same cases, and report numbers with intervals instead of impressions.

### Before you start

- Create a new repo named `mimir-beat-the-baseline` and run `uv init`, then `uv add scikit-learn datasets pandas matplotlib joblib numpy anthropic` and `uv add --dev pytest ruff`. Make sure `ANTHROPIC_API_KEY` is set for the LLM step.
- Pick your dataset now, because the ML elective's Fine-Tune a Small Model reuses it. The recommended choice is [Banking77](https://huggingface.co/datasets/PolyAI/banking77): about 13,000 short customer-support messages, each labeled with one of 77 intents such as `card_arrival` or `lost_or_stolen_phone`. It fits this curriculum well because intent routing is a real job that support agents do. Load it with `datasets.load_dataset("PolyAI/banking77")`.
- If you choose a different dataset, it must be a single-label text classification task with at least 2,000 labeled examples and a license that allows reuse. Record its source and license in your README.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Freeze your test set today

Banking77 comes with a train split and a test split. Carve a validation set out of the train split (for example 15%, stratified by label, with a fixed `random_state`), and save the exact IDs or rows of all three splits to files in your repo. The LLM comparison below, and Fine-Tune a Small Model if you take the ML elective, reuse these files unchanged. If the test set changes, the comparison means nothing.

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
   - A 95% bootstrap confidence interval on macro-F1, with a fixed seed, as in Eval Statistics.
1. Save the trained pipeline with `joblib` to `model.joblib`, and write `predict.py` that loads it and classifies a message passed on the command line.
1. Build an LLM classifier for the same task, as in `llm_classify.py` from Overfitting and Baselines, with the [cheap model](#/models). List all the intent labels in the prompt, count any answer that isn't a valid label as wrong, and record input tokens, output tokens and seconds for every call. Develop the prompt on the validation split only.
   - Before running on the test set, estimate the bill with `count_tokens`, as in Tokens, Cost and Rate Limits. If the full test set costs more than you want to spend, draw a fixed, seeded, stratified sample of at least 500 test messages, save its IDs, and score **every** system on that same sample.
   - Save the LLM's predictions to `results/llm_predictions.csv` so the comparison can be rerun without calling the API again.
1. Write `compare.py` that loads the saved predictions of all three systems (trivial baseline, tuned TF-IDF model, LLM) on the same test cases and prints one results table: macro-F1 with its 95% bootstrap interval, cost per 1,000 messages, and median latency per message. Below the table, print a paired bootstrap of the macro-F1 difference between the LLM and the tuned model, as in Comparing against an LLM classifier. Count the TF-IDF model's cost as zero, and say so.
1. Write at least two pytest tests: one that checks the splits have no overlapping texts, and one that loads `model.joblib` and checks it predicts a sensible label for an obvious message.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned. Include the tuning table (trivial baseline, overfit model, tuned model), the overfitting plot and the comparison table, and end with a short recommendation: for 2 million messages a month, which system would you ship, and why?

#### Evidence

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. CI must not download the dataset or call the API: test the split checks on the committed split files, and either commit `model.joblib` or have the model test skip with a clear message when it's missing. (Linting, Formatting and CI)
- The comparison table from `compare.py`, in the README: macro-F1 with a 95% interval, cost per 1,000 messages and median latency for all three systems, plus the paired difference between the LLM and the tuned model with its interval and the number of test cases (n).
- The frozen split files, the LLM's saved predictions and its per-call token and latency records are committed, so `compare.py` reproduces every number without an API key.

#### Extra credit

- Print the top 10 highest-weight words for three intents and comment on whether they make sense.
- After What Embeddings Are in the RAG section, come back and replace TF-IDF features with sentence embeddings, keep logistic regression, and compare the scores on the same test set.
- Train on 10%, 25%, 50% and 100% of the training data and plot test accuracy against training size. How much data does this task really need?

</div>

### Submitting your work

A strong submission makes the evaluation trustworthy at a glance: frozen split files in the repo, a one-command way to reproduce every number, a plot that clearly shows the train/validation gap closing as regularization increases, a test score reported exactly once for every system, and a recommendation that follows from the comparison table rather than from a hunch. Look at the most-confused pairs and say why they get confused (many Banking77 intents are near-duplicates). That kind of error analysis is what separates a portfolio project from a tutorial copy.
