### Introduction

A language model is an autoregressive probability distribution over the next token. A reinforcement learning policy is a conditional distribution over actions given states. An evaluation benchmark is a finite sample estimate with inherent statistical uncertainty.

Probability is the mathematical language of all three, and statistics is the discipline that tells you whether an improvement is genuine or merely random variance.

In [Matrices and Probability](#/paths/ml), you explored basic discrete distributions and softmax logits. In [Eval Statistics](#/paths/core), you computed bootstrap confidence intervals for classification pass rates. This lesson formalizes the full mathematical foundation required for graduate research: conditioning, linearity of expectation, joint distributions, maximum likelihood estimation, information theory (entropy, cross-entropy, and Kullback-Leibler divergence), and hypothesis testing.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Sample spaces, events, conditional probability, and avoiding the base-rate fallacy with Bayes' rule.
- Random variables, linearity of expectation, variance, and covariance.
- Core probability distributions in AI: Bernoulli, Binomial, Categorical, Gaussian, and Poisson.
- The Law of Large Numbers (LLN) and the Central Limit Theorem (CLT).
- How Maximum Likelihood Estimation (MLE) derives standard machine learning loss functions.
- Information theory: Shannon entropy, cross-entropy, and the asymmetry of KL divergence.
- Quantifying experimental uncertainty: confidence intervals, standard errors, and the non-parametric bootstrap.

### Conditioning and Bayes' rule in language models

The fundamental operation in probabilistic AI is **conditioning**: updating probabilities based on observed evidence.

For any two events `A` and `B` with `P(B) > 0`, the **conditional probability** of `A` given `B` is:

```text
P(A | B) = P(A and B) / P(B)
```

In generative AI, an autoregressive language model decomposes the joint probability of a sequence of `T` tokens using the **probability chain rule**:

```text
P(w1, w2, ..., wT) = P(w1) * P(w2 | w1) * P(w3 | w1, w2) * ... * P(wT | w1, ..., w_{T-1})
```

Each generation step evaluates the conditional probability distribution `P(w_t | w_{<t})` over the model's vocabulary.

**Bayes' rule** provides the formula for reversing conditional probabilities:

```text
P(H | D) = (P(D | H) * P(H)) / P(D)
```

- `P(H)` is the **prior probability** of hypothesis `H`.
- `P(D | H)` is the **likelihood** of observing data `D` if `H` holds.
- `P(H | D)` is the **posterior probability** of `H` given the observed data.

A common cognitive error in benchmark interpretation is the **base rate fallacy** (confusing `P(A | B)` with `P(B | A)`). If a prompt-injection vulnerability exists in only 0.1% of customer messages, a guardrail classifier with 98% accuracy and a 2% false-positive rate will produce a flagged result that is wrong more than 95% of the time. You must always multiply by the prior.

### Random variables, expectation, and variance

A **random variable** `X` is a function that maps outcomes of a random process to real numbers.

1. **Expected Value (Mean, μ):** The probability-weighted center of mass of the distribution:
```text
Discrete:    E[X] = sum(x * P(X = x))
Continuous:  E[X] = integral(x * p(x) dx)
```

The single most useful algebraic property in probability is the **Linearity of Expectation**:
> For any random variables `X` and `Y`, and any constants `a` and `b`:
> `E[a*X + b*Y] = a*E[X] + b*E[Y]`

Crucially, **linearity of expectation holds even when X and Y are dependent!** This property is used constantly in theoretical research to simplify calculations that would otherwise require intractable multi-dimensional integrals.

2. **Variance (σ^2):** Measures the expected squared deviation from the mean:
```text
Var(X) = E[(X - E[X])^2] = E[X^2] - (E[X])^2
```

Unlike expectation, variance is **not** linear. For independent random variables, `Var(X + Y) = Var(X) + Var(Y)`. For dependent variables:
```text
Var(X + Y) = Var(X) + Var(Y) + 2 * Cov(X, Y)
```
where the **covariance** `Cov(X, Y) = E[(X - E[X]) * (Y - E[Y])]` measures how the variables vary together.

### Essential probability distributions in machine learning

Every researcher should know five core distributions and their generative stories:

| Distribution | Support | Parameters | Mean | Variance | Generative Story in AI |
| --- | --- | --- | --- | --- | --- |
| **Bernoulli** | `{0, 1}` | `p` (success prob) | `p` | `p * (1 - p)` | Binary task pass/fail, coin flip |
| **Binomial** | `{0, 1, ..., n}` | `n` trials, `p` prob | `n * p` | `n * p * (1 - p)` | Number of eval tasks passed out of `n` |
| **Categorical** | `{1, ..., K}` | probabilities `p1, ..., pK` | — | — | Softmax output distribution over vocabulary tokens |
| **Gaussian (Normal)** | `(-inf, +inf)` | mean `μ`, variance `σ^2` | `μ` | `σ^2` | Measurement noise, parameter initialization |
| **Exponential** | `[0, +inf)` | rate `λ` | `1 / λ` | `1 / λ^2` | Waiting time between API request arrivals |

### The Law of Large Numbers and the Central Limit Theorem

Why can we trust empirical evaluation benchmarks?

The **Law of Large Numbers (LLN)** states that as the number of independent, identically distributed (i.i.d.) observations `n` grows, the sample mean `x_bar = (1/n) * sum(X_i)` converges to the true population mean `μ`:

```text
lim_{n -> inf} P(|x_bar - μ| < ε) = 1
```

The **Central Limit Theorem (CLT)** describes the distribution of that error. Regardless of the underlying distribution of `X` (even if `X` is skewed, bimodal, or discrete), the sum or average of a large number of independent variables approaches a Gaussian normal distribution:

```text
x_bar ≈ Normal(μ, σ^2 / n)
```

The standard deviation of the sample mean is the **Standard Error (SE)**:

```text
SE = σ / sqrt(n)
```

Notice the square root in the denominator:
- To cut your evaluation uncertainty (margin of error) in half, you must quadruple (`4x`) the number of evaluation examples.
- To reduce error by a factor of 10, you need `100x` more test cases.

### Maximum likelihood estimation as loss minimization

How do probability distributions connect to training neural networks? The bridge is **Maximum Likelihood Estimation (MLE)**.

Suppose you have observed a dataset of independent examples `D = {x1, x2, ..., xN}`, and you want to fit a parameterized probability distribution `p_θ(x)` (such as a neural network with weights `θ`).

The likelihood function is the probability of observing the entire dataset under parameter setting `θ`:

```text
L(θ) = P(D | θ) = product_{i=1}^{N} p_θ(x_i)
```

Multiplying thousands of probabilities causes numerical underflow. Because the logarithm is a monotonically increasing function, maximizing likelihood is mathematically equivalent to maximizing the log-likelihood:

```text
log L(θ) = sum_{i=1}^{N} log p_θ(x_i)
```

In optimization, algorithms minimize loss rather than maximize gain. We negate the objective to obtain the **Negative Log-Likelihood (NLL)**:

```text
Loss(θ) = -sum_{i=1}^{N} log p_θ(x_i)
```

- When `p_θ(y | x)` is a Categorical distribution parameterized by a softmax output layer, minimizing negative log-likelihood produces **cross-entropy loss** (used in next-token prediction and classification).
- When `p_θ(y | x)` is a Gaussian distribution with mean `f_θ(x)` and constant variance `σ^2`, minimizing negative log-likelihood produces **mean squared error (MSE)**.

Standard deep learning loss functions are simply maximum likelihood estimation under different distributional assumptions.

### Information theory: entropy, cross-entropy, and KL divergence

Information theory, founded by Claude Shannon in 1948, quantifies the amount of uncertainty and information in probability distributions.

![Probability, information theory, and sample size uncertainty](assets/images/probability_information_theory.svg)

1. **Shannon Entropy `H(P)`:** Measures the average surprise or uncertainty inherent in a distribution `P`:
```text
H(P) = -sum_x P(x) * log2(P(x))
```
If an event is guaranteed (`P(x) = 1`), entropy is 0 (zero uncertainty). If an outcome is uniformly random across `K` choices, entropy is maximized at `log2(K)` bits.

2. **Cross-Entropy `H(P, Q)`:** The expected number of bits needed to encode events from true distribution `P` using a code optimized for model distribution `Q`:
```text
H(P, Q) = -sum_x P(x) * log(Q(x))
```
When training a language model, `P` is the ground-truth one-hot distribution for the actual token, and `Q` is the model's softmax prediction.

3. **Kullback-Leibler (KL) Divergence `D_KL(P || Q)`:** The relative entropy measuring the information lost when approximating true distribution `P` with model distribution `Q`:
```text
D_KL(P || Q) = sum_x P(x) * log(P(x) / Q(x)) = H(P, Q) - H(P)
```

Three critical mathematical properties of KL divergence:
- **Non-negativity (Gibbs' inequality):** `D_KL(P || Q) >= 0`, with equality if and only if `P = Q` almost everywhere.
- **Asymmetry:** `D_KL(P || Q) != D_KL(Q || P)`. It is an informational distance, not a metric distance.
- **Role in RLHF and DPO:** In [RL for Language Models](#/paths/research), fine-tuning optimizes reward subject to a penalty on `D_KL(π_new || π_initial)`. This penalty acts as a probabilistic leash, preventing the model from collapsing into repetitive text or reward hacking.

### Statistical significance, confidence intervals, and the bootstrap

When comparing two models or measuring eval performance, point estimates alone ("Model A scored 82%, Model B scored 79%") are scientifically meaningless without quantifying uncertainty.

1. **Confidence Interval (CI):** An interval `[lower, upper]` computed from sample data that, under repeated hypothetical experiments, will contain the true population parameter a specified percentage of the time (typically 95%).
   - For a sample pass rate `p_hat` across `n` trials:
   ```text
   95% CI ≈ p_hat ± 1.96 * sqrt(p_hat * (1 - p_hat) / n)
   ```

2. **The Non-Parametric Bootstrap (Efron, 1979):**
When calculating confidence intervals for non-standard metrics (such as F1 score, NDCG, pass^k, or latency percentiles like p95) where analytical formulas do not exist or normality assumptions fail, use the bootstrap:
- Take your sample dataset of `n` observed test outcomes.
- Draw a sample of size `n` with replacement from your dataset.
- Compute the metric on the resampled data.
- Repeat 1,000 to 10,000 times to generate an empirical bootstrap distribution.
- The 2.5th and 97.5th percentiles of the bootstrap distribution form the **empirical 95% confidence interval**.

```python
# bootstrap_demo.py: Computing a 95% bootstrap confidence interval for pass rate
import numpy as np

np.random.seed(42)
# Simulated evaluation: 100 trials with true pass probability 75%
trials = np.random.binomial(n=1, p=0.75, size=100)
observed_pass_rate = np.mean(trials)

# Non-parametric bootstrap: 5,000 resamples
num_bootstraps = 5000
bootstrap_rates = []
for _ in range(num_bootstraps):
    resample = np.random.choice(trials, size=len(trials), replace=True)
    bootstrap_rates.append(np.mean(resample))

ci_lower = np.percentile(bootstrap_rates, 2.5)
ci_upper = np.percentile(bootstrap_rates, 97.5)

print(f"Observed pass rate: {observed_pass_rate:.1%}")
print(f"95% Bootstrap CI:   [{ci_lower:.1%}, {ci_upper:.1%}]")
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the interactive visual chapters on [Seeing Theory](https://seeing-theory.brown.edu/).
   - Complete Chapter 3 (Probability Distributions), Chapter 4 (Frequentist Inference: confidence intervals), and Chapter 5 (Bayesian Inference).
1. Watch selected lectures from Harvard's [Statistics 110: Probability](https://www.youtube.com/playlist?list=PL2SOU6wwxB0uwwH80KTQ6ht66KWxbzTIo) by Joe Blitzstein.
   - Watch Lecture 2 (Conditioning and Bayes' Rule), Lecture 6 (Monty Hall and Simpson's Paradox), Lecture 8 (Expectation and Linearity), and Lecture 21 (Covariance and Correlation).
1. Read Chapters 6 and 8 of [Mathematics for Machine Learning](https://mml-book.github.io/).
   - Chapter 6: Probability distributions and Gaussian identities.
   - Chapter 8: Empirical risk minimization and Maximum Likelihood Estimation.
1. Read the [Probability and Information Theory chapter](https://www.deeplearningbook.org/contents/prob.html) of the free *Deep Learning* book (Goodfellow et al.).
   - Pay special attention to Section 3.13 on information theory, entropy, and KL divergence.
1. Read [Adding Error Bars to Evals (Evan Miller, 2024)](https://arxiv.org/abs/2411.00640).
   - Review why reporting LLM benchmarks without error bars leads to false claims of model superiority.
1. Write a Python simulation script named `clt_simulation.py`:
   - Simulate an evaluation benchmark where the true agent accuracy is 70%.
   - Run 1,000 repeated eval experiments of sample sizes `n = 20, 100, 500`.
   - Compute the standard deviation of measured pass rates for each `n` and verify that the ratio of standard deviations matches `sqrt(500) / sqrt(100) ≈ 2.23`.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [What is the difference between conditional probability P(A | B) and posterior probability in Bayes' rule?](#conditioning-and-bayes-rule-in-language-models)
- [Why is linearity of expectation uniquely powerful when analyzing dependent random variables?](#random-variables-expectation-and-variance)
- [How does the Central Limit Theorem explain why sample uncertainty shrinks with 1 / sqrt(n)?](#the-law-of-large-numbers-and-the-central-limit-theorem)
- [How does Maximum Likelihood Estimation derive cross-entropy loss from a categorical distribution?](#maximum-likelihood-estimation-as-loss-minimization)
- [What does KL divergence measure, and why is it asymmetric?](#information-theory-entropy-cross-entropy-and-kl-divergence)
- [How does the non-parametric bootstrap construct confidence intervals without theoretical distribution formulas?](#statistical-significance-confidence-intervals-and-the-bootstrap)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [MIT OCW 18.650: Statistics for Applications](https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/) covers hypothesis testing, regression analysis, and asymptotic estimators.
- [Think Stats (Allen Downey)](https://greenteapress.com/wp/think-stats-3e/) is a free book teaching probability and statistical thinking using Python scripts and real datasets.
- [Elements of Information Theory (Cover & Thomas)](https://onlinelibrary.wiley.com/doi/book/10.1002/047174882X) is the standard definitive graduate reference on information theory and coding theorems.