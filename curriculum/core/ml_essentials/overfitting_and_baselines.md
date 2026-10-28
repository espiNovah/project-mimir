<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A model that scores 99% on the data it was trained on can still be useless on new data. That gap is called overfitting, and spotting it is one of the most practical skills in machine learning. The cure for fooling yourself is the same one you learned in Why Evals Matter: measure on data the model has never seen, and always compare against something simple.

This lesson is about two habits that carry straight over to LLM work. First, know how to detect and reduce overfitting. Second, build a cheap baseline before anything fancy, so you know whether the fancy thing is actually worth its cost.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Overfitting and underfitting, and the bias-variance tradeoff.
- Reading train versus validation scores to diagnose a model.
- Regularization and how it limits model complexity.
- Cross-validation for small datasets.
- Data leakage and how it inflates scores.
- Trivial baselines, simple baselines, and why they come first.

### Key ideas

- **Overfitting means memorizing instead of generalizing.** The model fits noise and quirks in the training data. The telltale sign is a high training score with a much lower validation score. Underfitting is the opposite: both scores are low because the model is too simple to capture the pattern.
- **The gap between train and validation is your diagnostic.** Big gap: overfitting, so simplify, regularize or get more data. Both low: underfitting, so add features or capacity. Both high and close: you're in good shape.
- **Regularization penalizes complexity.** L2 regularization adds the size of the weights to the loss, pushing the model toward smaller, smoother weights. In scikit-learn's `LogisticRegression`, the parameter `C` is the inverse of regularization strength: smaller `C` means stronger regularization.
- **Cross-validation gives a steadier estimate on small data.** Split the training data into k folds, train k times holding out a different fold each time, and average the scores. Use it to choose settings like `C`, never to replace the final held-out test.
- **Data leakage silently inflates scores.** If test information leaks into training (duplicate examples in both splits, fitting the TF-IDF vocabulary on all data before splitting, or a feature that encodes the answer), the score is fake. Fit every preprocessing step on the training split only.
- **Always start with baselines.** A trivial baseline (always predict the most common class) tells you the floor. A simple baseline (TF-IDF plus logistic regression) takes minutes and often gets surprisingly close to state of the art on text classification. An LLM or fine-tuned model has to beat it by enough to justify its extra cost and latency.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Overfitting module of Google's Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course/overfitting) for the core picture of generalization.
   - Read the pages on dividing datasets, overfitting, and [L2 regularization](https://developers.google.com/machine-learning/crash-course/overfitting/regularization), and do the interactive exercises.
1. Read the "Model selection and evaluation" material linked from [scikit-learn's Getting Started guide](https://scikit-learn.org/stable/getting_started.html), especially the section on cross-validation.
   - Pay attention to how pipelines prevent data leakage by fitting preprocessing inside each fold.
1. Skim the parameters section of [scikit-learn's LogisticRegression reference](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html).
   - Find `C`, `penalty` and `max_iter`, and note which direction of `C` means more regularization.
1. Take the classifier you built in Supervised Learning and train it with `C` set to 0.01, 1 and 100. For each, print training accuracy and validation accuracy side by side. Write two sentences on which setting overfits and which underfits.

</div>
