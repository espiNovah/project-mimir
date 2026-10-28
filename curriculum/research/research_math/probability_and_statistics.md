<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A language model is a probability distribution over the next token. A reinforcement learning policy is a distribution over actions. An eval result is a sample estimate with uncertainty. Probability is the language of all three, and statistics is how you decide whether a result is real. This lesson goes well beyond the intuition from Matrices and Probability: you will learn to compute expectations, derive estimators and tell signal from noise.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Sample spaces, conditional probability and Bayes' rule.
- Random variables, expectation, variance and the common distributions.
- Joint distributions, independence and covariance.
- The law of large numbers and the central limit theorem.
- Maximum likelihood estimation and how it becomes a loss function.
- Entropy, cross-entropy and KL divergence.
- Confidence intervals, hypothesis tests and the bootstrap.

### Key ideas

- **Conditioning is the core operation.** P(A | B) is the probability of A once you know B happened. Bayes' rule flips the conditioning: P(H | data) is proportional to P(data | H) times P(H). Many reasoning errors, including in LLM evals, come from confusing P(A | B) with P(B | A).
- **Expectation is linear, always.** The expected value of a sum is the sum of the expected values, even when the variables are dependent. This one fact makes many hard-looking problems easy, and it is the starting point of the policy gradient derivation you will see later in this track.
- **Know a handful of distributions well.** Bernoulli and binomial (success or failure, like an agent passing a task), categorical (a softmax over tokens), Gaussian (noise and initialization), Poisson and exponential (counts and waiting times). For each, know its mean, its variance and what story produces it.
- **Averages become predictable.** The law of large numbers says a sample mean converges to the true mean. The central limit theorem says its error is roughly Gaussian with standard deviation sigma over the square root of n. This is why you need four times as many eval examples to halve your error bar.
- **Training is maximum likelihood.** Choosing parameters that make the observed data most probable, then taking the negative log, gives the familiar losses: cross-entropy for classification and next-token prediction, squared error for regression with Gaussian noise.
- **Information theory measures surprise.** Entropy is the expected surprise of a distribution. Cross-entropy is the surprise when you code data from p using a model q. KL divergence is the gap between them. It is always non-negative and is not symmetric. KL penalties appear in RLHF, DPO and variational methods.
- **A difference is only real if it beats the noise.** A confidence interval gives a range of plausible values for a quantity. A hypothesis test asks how surprising your result would be if there were no real effect. When the math is awkward, the bootstrap (resampling your data with replacement) estimates uncertainty for almost any metric.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Explore [Seeing Theory](https://seeing-theory.brown.edu/), Brown University's interactive introduction to probability and statistics, for visual intuition.
   - Do all six chapters. Spend extra time on "Probability Distributions" (including the central limit theorem demo) and "Bayesian Inference".
1. Work through Harvard's [Statistics 110: Probability](https://www.youtube.com/playlist?list=PL2SOU6wwxB0uwwH80KTQ6ht66KWxbzTIo) lectures by Joe Blitzstein, one of the best probability courses available for free.
   - Watch lectures 1 to 24 at minimum (counting, conditional probability, random variables, expectation, the main distributions). The rest of the course covers joint distributions, the central limit theorem and Markov chains, all useful for RL.
   - The accompanying textbook, *Introduction to Probability* by Blitzstein and Hwang, is free at [probabilitybook.net](http://probabilitybook.net/). Do the starred exercises for each chapter you watch.
1. Read chapter 6 (Probability and Distributions) and chapter 8 (When Models Meet Data) of [Mathematics for Machine Learning](https://mml-book.github.io/). Chapter 8 connects maximum likelihood to the loss functions you have already used.
1. Read the [Probability and Information Theory chapter](https://www.deeplearningbook.org/contents/prob.html) of the free *Deep Learning* book by Goodfellow, Bengio and Courville for a compact treatment of entropy, cross-entropy and KL divergence.
1. Practice: simulate an eval. Create a fake agent that passes each task with probability 0.7. Run it on 20, 100 and 500 tasks, repeated 1,000 times each, and plot how the spread of measured pass rates shrinks. Then compute a 95% bootstrap confidence interval for one 100-task run and check it against the normal approximation.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [MIT 18.650 Statistics for Applications](https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/) covers estimation, hypothesis testing and regression at the level a master's statistics course expects.
- [Think Stats](https://greenteapress.com/wp/think-stats-3e/) by Allen Downey teaches statistics through Python code and is free online.
- [Adding Error Bars to Evals](https://arxiv.org/abs/2411.00640) by Evan Miller applies these statistical tools directly to language model evaluations. You will use it again in Experiment Design and Reproducibility.
