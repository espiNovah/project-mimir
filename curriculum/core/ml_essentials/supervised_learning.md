<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Before large language models, most useful machine learning was supervised learning: show a model thousands of examples with the right answer attached, and it learns to predict the answer for new examples. Spam filters, fraud detection and ticket routing all work this way, and many still do, because a small classic model is often cheaper, faster and easier to trust than an LLM call.

As an AI engineer you will regularly face the question "do we need an LLM for this at all?" You can only answer it if you know what classic ML can do. This lesson covers the vocabulary and the workflow: features, labels, training, and evaluation.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Features, labels and examples.
- Classification versus regression.
- What "training" a model means: a loss function and gradient descent.
- Linear and logistic regression.
- Turning text into features with bag-of-words and TF-IDF.
- Train, validation and test splits.
- Accuracy, precision, recall and the confusion matrix.

### Key ideas

- **An example is a pair of features and a label.** Features are the inputs (the words in an email); the label is the answer you want predicted ("spam" or "not spam"). Supervised learning means you have labels for your training data.
- **Classification predicts a category; regression predicts a number.** Routing a support ticket to one of 77 intents is classification. Predicting how long a ticket will take to resolve is regression.
- **Training means minimizing a loss.** A loss function scores how wrong the model's predictions are. Gradient descent nudges the model's parameters, step by step, in the direction that lowers the loss. This same idea trains every neural network, including LLMs.
- **Logistic regression is the workhorse classifier.** It computes a weighted sum of features and squashes it into a probability. It is fast, works well with many features, and its weights are inspectable: you can see which words push a prediction one way.
- **Models need numbers, so text must become features.** Bag-of-words counts each word. TF-IDF (term frequency times inverse document frequency) down-weights words that appear everywhere, like "the," and up-weights distinctive ones. It is a sparse, interpretable cousin of the dense embeddings you already know.
- **Split your data three ways.** Train on the training set, tune choices on the validation set, and touch the test set once, at the end. If you peek at the test set while making decisions, your final score is optimistic and no longer means anything.
- **Accuracy alone can lie.** If 95% of emails are not spam, a model that always says "not spam" is 95% accurate and useless. Precision (of the items flagged, how many were right), recall (of the real positives, how many were found) and the confusion matrix (a table of predicted versus actual labels) show where the model actually fails.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the opening modules of [Google's Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course), a free, recently refreshed course with interactive exercises.
   - Do the "Linear regression" and "Logistic regression" modules, including the gradient descent and loss sections.
1. Read the [Classification module of the Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course/classification) for the clearest short treatment of evaluation metrics.
   - Focus on thresholds, the confusion matrix, and accuracy versus precision versus recall.
1. Read [scikit-learn's Getting Started guide](https://scikit-learn.org/stable/getting_started.html) to learn the `fit` and `predict` pattern every scikit-learn model shares.
   - Then read the "Text feature extraction" part of [scikit-learn's feature extraction guide](https://scikit-learn.org/stable/modules/feature_extraction.html), up to and including TF-IDF term weighting.
1. In a notebook or script, load any small labeled text dataset, turn it into TF-IDF features with `TfidfVectorizer`, fit a `LogisticRegression`, and print accuracy and a confusion matrix on a held-out split. You will do this properly in the next project; for now, get it running end to end.

</div>
