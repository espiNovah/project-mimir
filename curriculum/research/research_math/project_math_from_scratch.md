### Introduction

In this project you will derive the gradients of logistic regression by hand, implement gradient descent and logistic regression using only NumPy, prove to yourself that your gradients are correct with a numerical check, and show that your model matches scikit-learn. No autograd, no ML libraries in the model code.

This is the classic first exercise in many graduate ML courses, and for good reason. It forces you to connect the three lessons in this section: linear algebra to write the model in vector form, calculus to derive the gradient, and probability to see that the loss is a negative log-likelihood. Gradient checking is also a real research habit. Whenever you write a custom loss or layer, a finite-difference check is how you find the bug before it wastes a week of training.

### Before you start

- Create a new repo named `mimir-math-from-scratch`. Set it up with `uv init` and add `numpy`, `matplotlib`, `scikit-learn` and `pytest` with `uv add`. Your model code may import only NumPy and the Python standard library; scikit-learn is allowed only in the comparison script and for loading data.
- Use a small real binary classification dataset. The [breast cancer dataset bundled with scikit-learn](https://scikit-learn.org/stable/datasets/toy_dataset.html) (`load_breast_cancer`) is a good default: 569 examples, 30 numeric features, no download needed.
- Write your derivation in Markdown with LaTeX math (GitHub renders `$...$` and `$$...$$` in Markdown; see [GitHub's guide to writing mathematical expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)), or in LaTeX compiled to PDF. Either is fine. Handwritten photos are not.
- Review chapter 5 of [Mathematics for Machine Learning](https://mml-book.github.io/) and the [scikit-learn LogisticRegression reference](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) so you know which regularization and parameters the library uses by default.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Write `derivation.md` (or `derivation.pdf`) that derives, step by step:
   - The logistic regression model p(y = 1 | x) = sigma(w<sup>T</sup>x + b) and why the sigmoid's derivative is sigma(z)(1 - sigma(z)).
   - The negative log-likelihood (binary cross-entropy) loss for n examples, starting from the Bernoulli likelihood.
   - The gradient of the loss with respect to w and b, first for one example and then in matrix form for the whole dataset (it should come out as X<sup>T</sup>(p - y) / n).
   - The same gradient with an L2 penalty added.
   - A short argument (or proof) that this loss is convex in w, using the Hessian.
1. Implement, in NumPy only, a `LogisticRegression` class with `fit`, `predict_proba` and `predict` methods. Training uses batch gradient descent with your derived gradient, a configurable learning rate, number of iterations and L2 strength. Compute the sigmoid in a numerically stable way so large inputs do not overflow.
1. Implement a finite-difference gradient checker that perturbs each parameter by a small epsilon in both directions and compares the central difference with your analytic gradient. Report the relative error. Add a `pytest` test that fails if the relative error exceeds 1e-6 on random data.
1. Add mini-batch stochastic gradient descent as an option, and train with both batch and mini-batch versions.
1. Standardize the features (fit the mean and standard deviation on the training split only), split the data into train and test sets with a fixed seed, and train your model.
1. Plot the training loss against iterations for at least three learning rates on one chart, including one that is too large and diverges or oscillates. Save the plot as `loss.png`.
1. Write `compare.py` that trains scikit-learn's `LogisticRegression` on the same split with matching regularization, and reports for both models: test accuracy, test log loss, and the largest absolute difference between the learned weights. Your accuracy should be within one percentage point of scikit-learn's, and your weights should be close. If they are not, explain why (for example, different regularization scaling or stopping before convergence).
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned. The README must include the gradient check result, the loss plot, the comparison table, and a paragraph on what the learning rate experiment shows about step size and curvature.

#### Extra credit

- Implement Newton's method using the Hessian you derived, and compare the number of iterations it needs to converge with gradient descent.
- Extend the model to multiclass softmax regression, derive its gradient, gradient-check it, and test it on the scikit-learn digits dataset.
- Add momentum and Adam to your optimizer and plot all three on the same loss chart.
- Implement a two-layer neural network with manual backpropagation (no autograd) and gradient-check every layer.

</div>

### Submitting your work

A strong submission is one a skeptical reviewer can verify in two minutes. The derivation is clean, every step follows from the last, and its final formula is exactly what the code computes. The gradient check passes in CI or with one `uv run pytest` command. The comparison with scikit-learn is honest: if the weights differ, the README says by how much and why. Reviewers will look closely at the learning rate plot, so label the axes, use a log scale for the loss if it helps, and say in one sentence what each curve shows.
