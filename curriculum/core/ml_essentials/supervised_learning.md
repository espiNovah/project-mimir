### Introduction

Before large language models, most useful machine learning was **supervised learning**: show a model thousands of examples with the right answer attached, and it learns to predict the answer for new examples. Spam filters, fraud detection and ticket routing all work this way, and many still do, because a small classic model is often cheaper, faster and easier to trust than an LLM call.

As an AI engineer you will regularly face the question "do we need an LLM for this at all?" You can only answer it if you know what classic ML can do. This lesson covers the vocabulary and the workflow: features, labels, training and evaluation. By the end you'll have trained a real text classifier in about 40 lines of Python, and you'll know why it can handle a million messages for less than the price of a coffee.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Features, labels and examples.
- Classification versus regression.
- What "training" a model means: a loss function and gradient descent.
- Logistic regression, the workhorse classifier.
- Turning text into features with bag-of-words and TF-IDF.
- Train, validation and test splits, and reading the results.
- Where classic ML still beats an LLM call.

### Examples, features and labels

An **example** is one row of data: one email, one support ticket, one house for sale. Each example has **features** and, in supervised learning, a **label**.

- **Features** are the inputs the model gets to look at: the words in an email, or a house's size and location.
- The **label** is the answer you want predicted: "spam" or "not spam", or the house's sale price.

"Supervised" means you have labels for your training data. Someone (often you, as in Error Analysis and Labeling) sat down and wrote the right answer next to each example. The model's job is to find a pattern that connects features to labels well enough to predict labels for examples it has never seen.

By convention, the features are called `X` (capital, because it's a table with one row per example) and the labels are called `y` (lowercase, one value per example). You'll see `X_train`, `y_test` and friends in every scikit-learn tutorial.

Notice that this is the same shape as an eval dataset: inputs paired with expected outputs. In evals you use that table to grade a system. In supervised learning you use it to *build* the system. That overlap is why the evaluation habits from the Measuring Quality section transfer straight over.

### Classification and regression

Supervised problems come in two flavors:

- **Classification** predicts a category. Routing a support ticket to one of 77 intents is classification. So is spam detection (two categories, called **binary classification**).
- **Regression** predicts a number. Predicting how many hours a ticket will take to resolve, or a house's price, is regression.

The word "regression" is confusing here, because the most popular *classifier* is called logistic regression. It's a historical accident: logistic regression predicts a number (a probability), and then you turn that number into a category. Don't let the name trip you up.

Most AI engineering problems where classic ML competes with an LLM are classification problems: routing, tagging, filtering, triage. This lesson and the Beat the Baseline project focus on those.

### What training means

A model is a function with adjustable numbers inside it, called **parameters** or **weights**. Training means finding the weights that make the model's predictions as good as possible on the training data. To do that, you need a way to score "how wrong" the predictions are.

That score is the **loss function**. For a classifier, a common choice is **log loss** (also called cross-entropy). If the right answer is "spam" and the model said "90% spam," the loss is small. If it said "1% spam," the loss is large. Confident wrong answers are punished hardest. The training loss is the average over all training examples.

**Gradient descent** is how training lowers the loss. Picture the loss as a hilly landscape, where each position is one setting of the weights and the height is the loss. You're standing somewhere on it in fog. You can feel which way the ground slopes under your feet (that slope is the **gradient**, which calculus gives you for free), so you take a small step downhill, feel again, and repeat. The size of each step is the **learning rate**. Too small and training takes forever; too large and you overshoot the valley.

You won't write gradient descent yourself in this path. scikit-learn's `fit` method does it (or a cleverer cousin) for you. But it's worth understanding, because the exact same idea, a loss plus many small downhill steps, trains every neural network, including the LLMs you call through an API. The Google course in the Assignment lets you drag the learning rate around and watch it happen.

### Logistic regression

**Logistic regression** is the workhorse classifier. For each class, it computes a weighted sum of the features: each feature value times its weight, all added up, plus a constant. Then it squashes that sum into a probability between 0 and 1 using the **sigmoid** function (or, with more than two classes, the **softmax**, which turns one score per class into probabilities that add up to 1). The class with the highest probability wins.

Three things make it the default first model for text:

- **It's fast.** Training on thousands of examples takes a second or two on a laptop, and prediction is a handful of multiplications.
- **It handles many features well.** Text produces tens of thousands of features (one per word), and logistic regression copes fine.
- **Its weights are inspectable.** Every word has a weight for every class. A big positive weight for "brakes" in the cars class means the word pushes predictions toward cars. You can print the top words and check whether the model learned something sensible or something silly. You'll do that below.

### Turning text into features

Models need numbers, so text must become features. The simplest approach is **bag-of-words**: build a vocabulary of every word in the training set, then represent each document as a row of counts, one column per vocabulary word. Word order is thrown away, which is why it's called a "bag."

Raw counts have a problem: common words such as "the" appear everywhere and tell you nothing. **TF-IDF** fixes that. It multiplies each word's **term frequency** (how often it appears in this document) by its **inverse document frequency** (a number that is large for rare words and small for words that appear in many documents). Distinctive words get high weights; filler words get low ones. scikit-learn also scales each row so that long documents don't dominate short ones.

Here are both on three tiny documents. Install scikit-learn into a fresh project first with `uv add scikit-learn`.

```python
# tfidf_demo.py: what TF-IDF does to three tiny documents.
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

docs = ["the card has not arrived",
        "the card was declined",
        "the app will not open"]

counts = CountVectorizer().fit(docs)
print(counts.get_feature_names_out())
print(counts.transform(docs).toarray())        # bag of words: raw counts

tfidf = TfidfVectorizer().fit(docs)
row = tfidf.transform(["the card was declined"]).toarray()[0]
for word, weight in zip(tfidf.get_feature_names_out(), row):
    if weight:
        print(f"{word:9} {weight:.2f}")
```

```text
['app' 'arrived' 'card' 'declined' 'has' 'not' 'open' 'the' 'was' 'will']
[[0 1 1 0 1 1 0 1 0 0]
 [0 0 1 1 0 0 0 1 1 0]
 [1 0 0 0 0 1 1 1 0 1]]
card      0.44
declined  0.58
the       0.35
was       0.58
```

Each row of the count matrix is one document, and each column is one word. In the TF-IDF version of "the card was declined", "the" (which appears in all three documents) gets the lowest weight, "card" (in two) is in the middle, and "declined" and "was" (in only one) get the highest. Real vocabularies have thousands of columns, and almost every entry is zero, so scikit-learn stores them as a **sparse matrix** that only records the non-zero values.

TF-IDF is a sparse, interpretable cousin of the dense **embeddings** you'll meet in the RAG section. An embedding captures meaning, so "card declined" and "payment refused" land close together. TF-IDF only matches exact words. That sounds like a big weakness, and sometimes it is, but on many classification tasks TF-IDF plus logistic regression is surprisingly hard to beat.

### A classifier end to end

Time for a real dataset. scikit-learn can download the classic [20 Newsgroups dataset](https://scikit-learn.org/stable/datasets/real_world.html#the-20-newsgroups-text-dataset), about 18,000 posts from old online discussion groups, each labeled with the group it was posted in. Four groups make a small, quick problem. The first run downloads about 14 MB and caches it, so later runs work offline.

```python
# classify.py: a classic text classifier, end to end.
# setup: uv add scikit-learn
import time

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

CATEGORIES = ["comp.graphics", "rec.autos", "sci.med", "talk.politics.guns"]

# 1. Load labeled examples. remove=... strips email headers and signatures,
#    which would otherwise give the answer away (more on that next lesson).
data = fetch_20newsgroups(subset="train", categories=CATEGORIES,
                          remove=("headers", "footers", "quotes"), random_state=0)
texts, labels = data.data, data.target          # features (raw text) and labels (0-3)
print(f"{len(texts)} examples, {len(CATEGORIES)} classes")

# 2. Hold out 20% as a test set the model never sees while training.
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, stratify=labels, random_state=0)

# 3. Turn text into numbers. fit_transform LEARNS the vocabulary from the
#    training set only.
vectorizer = TfidfVectorizer(stop_words="english", min_df=2)
X_train_vec = vectorizer.fit_transform(X_train)
print(f"feature matrix: {X_train_vec.shape[0]} rows x {X_train_vec.shape[1]} columns")

# 4. Train: fit finds the weights that minimize the loss on the training set.
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

# 5. Predict and score on the held-out test set.
start = time.perf_counter()
X_test_vec = vectorizer.transform(X_test)       # same vocabulary, no refitting
predicted = model.predict(X_test_vec)
per_message_ms = (time.perf_counter() - start) / len(X_test) * 1000
print(f"test accuracy: {model.score(X_test_vec, y_test):.3f}")
print(f"prediction time: {per_message_ms:.3f} ms per message\n")
print(classification_report(y_test, predicted, target_names=CATEGORIES, digits=2))
print(confusion_matrix(y_test, predicted))

# 6. Classify brand-new text.
new = ["My brakes squeal when I stop, should I replace the pads?",
       "Which file format keeps transparency, PNG or JPEG?"]
for text, label in zip(new, model.predict(vectorizer.transform(new))):
    print(f"{CATEGORIES[label]:20} <- {text}")

# 7. Look inside: the five words with the largest weight for each class.
words = vectorizer.get_feature_names_out()
for i, name in enumerate(CATEGORIES):
    top = model.coef_[i].argsort()[-5:][::-1]
    print(f"{name:20} {', '.join(words[top])}")
```

Here's the output from scikit-learn 1.9 on a laptop (your timing will differ):

```text
2318 examples, 4 classes
feature matrix: 1854 rows x 11005 columns
test accuracy: 0.899
prediction time: 0.059 ms per message

                    precision    recall  f1-score   support

     comp.graphics       0.91      0.88      0.90       117
         rec.autos       0.83      0.92      0.87       119
           sci.med       0.95      0.90      0.92       119
talk.politics.guns       0.92      0.90      0.91       109

          accuracy                           0.90       464
         macro avg       0.90      0.90      0.90       464
      weighted avg       0.90      0.90      0.90       464

[[103   9   3   2]
 [  3 109   2   5]
 [  6   5 107   1]
 [  1   9   1  98]]
rec.autos            <- My brakes squeal when I stop, should I replace the pads?
comp.graphics        <- Which file format keeps transparency, PNG or JPEG?
comp.graphics        graphics, files, image, file, program
rec.autos            car, cars, engine, oil, ford
sci.med              msg, doctor, disease, pain, medical
talk.politics.guns   gun, guns, weapons, government, fbi
```

Every scikit-learn model follows the same pattern, and it's worth memorizing:

- **`fit`** learns from training data. On the vectorizer it learns the vocabulary and the IDF weights. On the model it learns the word weights.
- **`transform`** applies what a vectorizer learned to new data, without learning anything new. `fit_transform` does both in one step, and you only ever call it on training data.
- **`predict`** returns a label for each example. `predict_proba` returns the probabilities instead.
- **`score`** predicts and returns accuracy in one call.

A few more details. `stratify=labels` keeps the same mix of classes in both splits. `random_state=0` fixes the random shuffle so you get the same split every run, which makes your numbers reproducible. `stop_words="english"` drops very common words, and `min_df=2` drops words that appear in only one training document, which are mostly typos and names. The top-weight words are the reassuring part: "car, cars, engine, oil" for autos is exactly what a human would pick. ("msg" for medicine looks odd until you search the data: 43 of the 594 medical posts mention the food additive MSG. Quirks like that are worth noticing, because they're how models learn the wrong lesson.)

### Train, validation and test splits

The script above used two splits. Real projects use three:

- The **training set** is what the model learns from.
- The **validation set** (sometimes called the dev set) is what you use to make choices: which features, which settings, which model. You'll do this in Overfitting and Baselines.
- The **test set** is touched once, at the end, to report the final score.

Why so strict? Every time you look at a score and change something to improve it, you are fitting your choices to that data. Do that against the test set, and your final score is optimistic: it measures how well you tuned to those particular examples, not how well the model works on new ones. That's the same trap as tweaking a prompt until it passes your eval cases. Once you've peeked, the test score no longer means what it says.

One more rule shows up in step 3 of the script. The vectorizer is fit on the training split only, then applied to the test split. If you fit it on all the data first, information about the test set (its vocabulary and word frequencies) leaks into training. The next lesson shows how scikit-learn's pipelines make this mistake impossible.

### Reading the results

**Accuracy alone can lie.** If 95% of emails are not spam, a model that always says "not spam" is 95% accurate and useless. You already know the cure from Eval Statistics: look at the confusion matrix and at precision and recall per class. The `classification_report` above prints exactly the table you built by hand in that lesson, and the "macro avg" row is macro-F1.

Read the confusion matrix row by row. Rows are the true labels, in the order of `CATEGORIES`, and columns are the predictions. The diagonal holds the correct answers. The second column is the interesting one: 9 graphics posts, 5 medical posts and 9 gun-politics posts were predicted as autos. That's why autos has the lowest precision (0.83) but the highest recall (0.92). The model treats "autos" as a bit of a catch-all. This is the kind of finding that tells you where to look next, which is error analysis all over again: open the misclassified posts and read them.

The test set has 464 examples, so remember to put an error bar on that 0.899. The standard-error formula from Eval Statistics gives about plus or minus 2.7 points. When you compare this model against an LLM classifier in Beat the Baseline, you'll report both with intervals.

### When classic ML beats an LLM call

You could solve the same problem by sending each post to an LLM with a prompt like "Classify this post into one of these four topics." That would take five minutes to build, need no training data, and probably score well. So why bother with scikit-learn? Three reasons: **cost, latency and volume**.

Take the support-routing task from Beat the Baseline: 2 million messages a month, 77 possible intents.

- **Cost.** A prompt that lists 77 intents with a short description of each, plus the message, might be around 600 input tokens. Two million calls is 1.2 billion input tokens. At the [cheap model's](#/models) price at the time of writing ($0.10 per million input tokens and $0.50 per million output), that's about $120 a month for input alone, plus output tokens on top. Not ruinous, but it's a bill that grows with every message, forever. The TF-IDF model's 0.06 milliseconds per message means 2 million predictions take about two minutes of CPU time on an ordinary machine. That is effectively free.
- **Latency.** An API call takes a network round trip plus generation time, typically hundreds of milliseconds and sometimes seconds. The classic model answers in well under a millisecond, with no network involved. When a classifier sits inside something interactive, or in front of another model call, that difference matters.
- **Volume and control.** At high volume you also hit rate limits, outages and model deprecations. A `model.joblib` file sitting in your repo has none of those problems, gives the same answer every time for the same input, and runs anywhere Python runs, including places where data can't leave your servers.

LLMs win in other situations: when you have little or no labeled data, when the categories change every week, when the task needs real reasoning or world knowledge, or when volume is low enough that the bill doesn't matter. Often the best answer is a combination: a cheap classic model handles the bulk, and only uncertain cases (low `predict_proba` scores) go to an LLM. The habit to build is simple: **know the classic baseline's numbers before you decide an LLM is needed.** The next lesson is about building that baseline properly.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the opening modules of [Google's Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course), a free, recently refreshed course with interactive exercises. It shows loss and gradient descent visually, which this lesson only described.
   - Do the "Linear regression" and "Logistic regression" modules, including the gradient descent and loss sections. Skip any math you find heavy; the interactive widgets carry the ideas.
1. Read the [Classification module of the Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course/classification). It connects predicted probabilities to labels, which this lesson skipped.
   - Focus on thresholds, the confusion matrix, and accuracy versus precision versus recall. Much of it reviews Eval Statistics, so move quickly through what you know.
1. Read [scikit-learn's Getting Started guide](https://scikit-learn.org/stable/getting_started.html) to see the `fit` and `predict` pattern every scikit-learn model shares.
   - Then read the "Text feature extraction" part of [scikit-learn's feature extraction guide](https://scikit-learn.org/stable/modules/feature_extraction.html), up to and including TF-IDF term weighting. It explains the options `TfidfVectorizer` takes, such as `ngram_range` and `min_df`.
1. Practice: run `classify.py` from this lesson in a new `uv` project or a notebook, then change it.
   - Swap in four different newsgroups (call `fetch_20newsgroups(subset="train").target_names` to list all 20) and pick two that are easy to confuse, such as `comp.sys.ibm.pc.hardware` and `comp.sys.mac.hardware`. How do accuracy and the confusion matrix change?
   - Print the five posts the model got most confidently wrong (use `predict_proba`), read them, and write one sentence on why each was misclassified.
   - Compute a 95% interval for your test accuracy with the standard-error formula from Eval Statistics.
1. Optional warm-up: if `numpy` array indexing still feels shaky, redo the [data exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/data), especially `02_cosine_top_k`. The `argsort` trick in step 7 of `classify.py` is the same idea.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are features and labels, and what makes learning "supervised"?](#examples-features-and-labels)
- [What is a loss function, and how does gradient descent use it?](#what-training-means)
- [Why is logistic regression a good first model for text classification?](#logistic-regression)
- [How does TF-IDF differ from raw word counts, and why does that help?](#turning-text-into-features)
- [What do `fit`, `transform` and `predict` each do, and why is `fit_transform` only called on training data?](#a-classifier-end-to-end)
- [Why should you touch the test set only once?](#train-validation-and-test-splits)
- [Give three reasons a classic classifier might beat an LLM call, and one situation where it wouldn't.](#when-classic-ml-beats-an-llm-call)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Classification of text documents using sparse features](https://scikit-learn.org/stable/auto_examples/text/plot_document_classification_20newsgroups.html), from scikit-learn's example gallery, runs the same 20 Newsgroups problem with several different classifiers and compares their accuracy and training time, including the effect of the headers you'll meet in the next lesson.
- [StatQuest's logistic regression video](https://www.youtube.com/watch?v=yIYKR4sgzI8) explains the sigmoid curve and how the model is fit, with clear pictures and no heavy math.
