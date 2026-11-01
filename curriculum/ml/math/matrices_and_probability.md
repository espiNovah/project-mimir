### Introduction

A neural network is mostly two things: matrix multiplications that transform vectors, and probability distributions that turn raw scores into decisions.

When a language model predicts its next token, it takes a vector representing the text so far, multiplies it by a sequence of large weight matrices across dozens of transformer layers, and finally projects the result onto a vector of scores—one score for every token in its vocabulary. It then converts those scores into probabilities and samples one.

You met the user-facing side of sampling in [Context Windows and Sampling](#/paths/foundations) when setting temperature and top-p. This lesson opens the mathematical engine underneath. It provides the core intuition for matrices and probability distributions so that when you build backpropagation and a micro-GPT in the next section, the code reads as natural Python rather than an intimidating wall of symbols.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How a matrix functions as a geometric transformation that rotates, scales, or shears vectors.
- The fundamental shape rule of matrix multiplication, and why shape bugs are the most common error in deep learning.
- How matrix multiplication computes hundreds or thousands of dot products simultaneously on a GPU.
- Discrete versus continuous probability distributions, and what it means for probabilities to sum to 1.
- Expected value, variance, and why the Gaussian (normal) distribution governs weight initialization.
- Conditional probability and Bayes' rule: updating beliefs when new evidence arrives.
- How the softmax function converts raw logits into a valid probability distribution, and how temperature sharpens or flattens it.

### Matrices as geometric transformations

In [Vectors and Similarity](#/paths/core), you learned that a vector is an ordered list of numbers that can be viewed as an arrow pointing to a location in space. In two dimensions, `[2, 3]` means "move 2 units along the x-axis and 3 units along the y-axis."

A **matrix** is a two-dimensional grid of numbers arranged in rows and columns. While a vector represents a point or a state, a matrix represents an **action** or a **transformation**. When you multiply a matrix by a vector, the matrix transforms that vector into a new vector.

Consider a 2-by-2 matrix `A`:

```text
A = [[2, 0],
     [0, 3]]
```

If we multiply this matrix by a vector `x = [1, 1]`, each row of the matrix computes a dot product with the vector:

```text
A @ x = [2*1 + 0*1, 0*1 + 3*1] = [2, 3]
```

Notice what happened geometrically: the x-coordinate was scaled by 2, and the y-coordinate was scaled by 3. Space was stretched. Other matrices rotate space, flip it, or squash it along diagonal axes.

In a neural network, a layer with weights `W` is a matrix that takes an input vector `x` (such as a word embedding) and maps it into a new feature space:

```text
y = W @ x + b
```

The matrix `W` rotates and stretches the input vector, and the bias vector `b` shifts it. A deep neural network is simply a chain of these matrix transformations interleaved with small non-linear functions.

### Matrix multiplication and the shape rule

To work with neural networks without getting stuck, you must master the **shape rule** of matrix multiplication.

A matrix with `m` rows and `k` columns has shape `(m, k)`. You can only multiply matrix `A` by matrix `B` if the number of columns in `A` equals the number of rows in `B`:

```text
(m, k) x (k, n) -> (m, n)
```

The inner dimensions must match (`k = k`), and the outer dimensions determine the shape of the result (`(m, n)`).

```text
Matrix A (3 x 2)        Matrix B (2 x 4)         Result C (3 x 4)
[ .  . ]                [ .  .  .  . ]           [ .  .  .  . ]
[ .  . ]        x       [ .  .  .  . ]     =     [ .  .  .  . ]
[ .  . ]                                         [ .  .  .  . ]
   ^                        ^                       ^     ^
   |--- inner dims match ---|                       |-----|--- outer dims
```

Each element `C[i, j]` in the resulting matrix is the dot product of the `i`-th row of `A` with the `j`-th column of `B`:

```text
C[i, j] = sum_{r=1}^{k} A[i, r] * B[r, j]
```

Here is how you compute this in NumPy, along with checking shapes:

```python
import numpy as np

# A has shape (3, 2): 3 rows, 2 columns
A = np.array([
    [1.0, 2.0],
    [3.0, 4.0],
    [5.0, 6.0]
])

# B has shape (2, 4): 2 rows, 4 columns
B = np.array([
    [1.0, 0.0, 1.0, 0.0],
    [0.0, 2.0, 0.0, 1.0]
])

# In Python 3.5+, the @ operator performs matrix multiplication
C = A @ B

print("Shape of A:", A.shape)  # (3, 2)
print("Shape of B:", B.shape)  # (2, 4)
print("Shape of C:", C.shape)  # (3, 4)
print("Result C:\n", C)
```

If you ever attempt to multiply two matrices where the inner dimensions do not match—for example, trying `B @ A` where shapes are `(2, 4)` and `(3, 2)`—NumPy and PyTorch will immediately raise a `ValueError: matmul: Input operand 1 has a mismatch in its core dimension`. In practice, over half of all bugs encountered when writing custom models or modifying architectures are shape mismatches. Always write the shape of each tensor in a comment next to your code.

### Batching dot products on GPUs

Why do modern AI models rely so heavily on matrix multiplication? The answer is parallel computation.

Suppose you have built a retrieval system that contains 10,000 document chunks, each represented by a 384-dimensional embedding vector. When a user submits a search query, you produce a 384-dimensional query vector. To find the most relevant documents, you need the cosine similarity between the query and all 10,000 documents.

In pure Python, you could write a loop that calculates 10,000 dot products one by one. This is slow because Python loops execute sequentially on a single CPU core.

Instead, you stack all 10,000 document vectors into a single matrix `D` of shape `(10000, 384)`. If the document vectors and the query vector `q` are normalized to unit length, a single matrix-vector product computes all 10,000 similarities at once:

```text
s = D @ q
```

Here, `D` is `(10000, 384)` and `q` is `(384,)`. The result `s` is `(10000,)`, containing all 10,000 similarity scores.

```python
# 10,000 documents of dimension 384
D = np.random.randn(10000, 384)
# Normalize rows to unit length
D = D / np.linalg.norm(D, axis=1, keepdims=True)

# 1 query of dimension 384
q = np.random.randn(384)
q = q / np.linalg.norm(q)

# Compute all 10,000 similarities in one shot
similarities = D @ q
print("Top similarity score:", similarities.max())
print("Score array shape:", similarities.shape)  # (10000,)
```

Graphics Processing Units (GPUs) contain thousands of small arithmetic units designed specifically to multiply matrices at memory bandwidths exceeding terabytes per second. By expressing your operations as matrix multiplications, you allow hardware accelerators to perform trillions of calculations per second.

### Discrete and continuous probability distributions

A **probability distribution** is a mathematical function that describes the likelihood of different outcomes.

Probabilities follow two unbreakable rules:
1. Every individual probability `P(x)` must be non-negative: `P(x) >= 0`.
2. The sum (or integral) of all possible outcomes must equal exactly 1: `sum_x P(x) = 1`.

Distributions come in two forms:

- **Discrete distributions:** Outcomes are distinct categories or integers. For example, rolling a 6-sided die has six discrete outcomes, each with probability 1/6. A language model's output is a discrete distribution over a vocabulary of approximately 32,000 to 128,000 unique token IDs.
- **Continuous distributions:** Outcomes can take any real value on a continuous spectrum, such as the height of a person or the response latency of an API in milliseconds. Because there are infinite possible values, the probability of any single exact decimal (like 142.38491... ms) is zero; instead, we measure the probability of the value falling within a range using a **probability density function** (PDF).

### Expected value, variance, and the normal distribution

Two summary statistics describe the location and spread of any distribution:

1. **Expected value (Mean, μ):** The probability-weighted average of all possible values.

```text
E[X] = sum(x * P(X = x))
```

If a game pays 10 dollars with 20% probability and 0 dollars with 80% probability, the expected value is `10 * 0.20 + 0 * 0.80 = 2.00` dollars.

2. **Variance (σ^2):** A measure of how widely values spread out around the mean.

```text
Var(X) = E[(X - μ)^2]
```

The square root of variance is the **standard deviation** (`σ`). It measures typical deviation in the original units of measurement.

The most famous continuous distribution in mathematics and machine learning is the **Normal distribution** (or Gaussian bell curve), denoted `N(μ, σ^2)`. It is symmetrical and centered at `μ`, with 68% of the values falling within one standard deviation (`μ ± σ`) and 95% falling within two (`μ ± 2σ`).

```python
# Sampling from a standard normal distribution (mean=0, std=1)
samples = np.random.normal(loc=0.0, scale=1.0, size=10000)

print(f"Sample mean: {samples.mean():.4f}")        # ~0.00
print(f"Sample std:  {samples.std():.4f}")         # ~1.00
print(f"Within 1 std: {(np.abs(samples) < 1.0).mean():.1%}")  # ~68.3%
print(f"Within 2 std: {(np.abs(samples) < 2.0).mean():.1%}")  # ~95.4%
```

Why does the normal distribution matter for deep learning? When a neural network is created, its weights cannot all be zero (otherwise every neuron would compute identical values and learn identical gradients). Instead, weights are initialized by drawing random numbers from a normal distribution with mean 0 and a small, carefully chosen standard deviation (often scaled inversely by the square root of the layer's input dimension).

### Conditional probability and Bayes' rule

In applied AI, events rarely happen in a vacuum. You are almost always interested in the probability of an outcome **given** that certain background information is known.

This is **conditional probability**, written as `P(A | B)`—read "the probability of A given B":

```text
P(A | B) = P(A and B) / P(B)
```

A language model is a pure conditional probability engine. When an LLM generates text, it does not compute the unconditional probability of the word "apple"; it computes:

```text
P(next token | all previous tokens in the prompt)
```

**Bayes' rule** provides a rigorous mathematical formula for inverting conditional probabilities:

```text
P(A | B) = (P(B | A) * P(A)) / P(B)
```

- `P(A)` is the **prior**: your belief about A before seeing evidence B.
- `P(B | A)` is the **likelihood**: how likely the evidence B is if hypothesis A is true.
- `P(A | B)` is the **posterior**: your updated belief about A after observing evidence B.

In LLM evaluation, Bayes' rule explains why high test accuracy can be misleading on rare events. If an evaluation dataset has a 1% base rate of security vulnerabilities, and an automated judge has a 95% true-positive rate and a 5% false-positive rate, a flagged vulnerability only has about a 50% chance of being a real vulnerability. Understanding conditional probability prevents you from misinterpreting evaluation benchmarks.

### Softmax, logits, and temperature

When a language model processes a sequence of tokens, the final linear layer outputs raw, unconstrained real numbers called **logits** (`z`). There is one logit for each token in the vocabulary. A logit might be `4.2`, `-1.8`, or `0.05`.

To convert these raw scores into a valid probability distribution where all values are positive and sum to 1.0, models use the **softmax function**:

```text
softmax(z_i) = exp(z_i) / sum_j(exp(z_j))
```

The numerator exponentiates the score, guaranteeing that every value is strictly positive (`exp(z_i) > 0`). The denominator sums the exponentiated values across the entire vocabulary, ensuring that the total sums to 1.0.

When you sample from a model with a **temperature** parameter `T > 0`, the temperature divides the logits before the exponential is applied:

```text
P_i = exp(z_i / T) / sum_j(exp(z_j / T))
```

Let's observe what temperature does in practice:

```python
def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    scaled = logits / temperature
    # Subtracting the maximum logit prevents overflow without altering the probabilities
    shifted = scaled - np.max(scaled)
    exp_scores = np.exp(shifted)
    return exp_scores / np.sum(exp_scores)

logits = np.array([3.0, 1.0, 0.2])

print("T = 0.2 (Cold):  ", np.round(softmax(logits, temperature=0.2), 3))
print("T = 1.0 (Default):", np.round(softmax(logits, temperature=1.0), 3))
print("T = 2.0 (Warm):  ", np.round(softmax(logits, temperature=2.0), 3))
```

Output:
```text
T = 0.2 (Cold):   [1.    0.    0.   ]
T = 1.0 (Default): [0.841 0.114 0.045]
T = 2.0 (Warm):   [0.557 0.252 0.191]
```

- When `T < 1.0` (low temperature), differences between logits are magnified. The highest score dominates, and the distribution becomes sharp and confident. At the limit as `T -> 0`, it becomes greedy argmax.
- When `T = 1.0`, the distribution reflects the model's standard learned probabilities.
- When `T > 1.0` (high temperature), differences between logits are compressed toward zero. The distribution flattens out, approaching a uniform distribution where every choice is equally likely.

Understanding softmax and temperature directly connects the mathematical mechanics of vector projection to the real-world behavior of generative models.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch chapter 3 ("Linear transformations and matrices") and chapter 4 ("Matrix multiplication as composition") of [3Blue1Brown's Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra).
   - Pay attention to the visual explanation of why columns of a matrix tell you where the standard basis vectors land after transformation.
1. Work through the probability fundamentals in [Khan Academy Statistics and Probability](https://www.khanacademy.org/math/statistics-probability).
   - Complete the "Probability" unit (covering compound events and conditional probability) and the "Random variables" unit up through expected value.
1. Explore the interactive visual demonstrations on [Seeing Theory](https://seeing-theory.brown.edu/).
   - Interact with Chapter 1 (Basic Probability) and Chapter 2 (Compound Probability). Drag the sliders to see how conditional probability and Bayes' theorem update in real time.
1. Write a Python script named `matrix_lab.py` using NumPy:
   - Create a matrix `W` with shape `(4, 3)` containing random values from a normal distribution, and a vector `x` of shape `(3,)`.
   - Compute `y = W @ x` and print the shapes before and after. Verify that the output shape is `(4,)`.
   - Implement `stable_softmax(logits, temperature=1.0)` that handles numerical overflow by subtracting `np.max(logits)` before exponentiating.
   - Test your function on `logits = np.array([1000.0, 1001.0, 1002.0])` with temperature 1.0. Check that standard `np.exp(logits)` overflows to `inf`, but your stable implementation returns valid probabilities that sum to 1.0.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [What is the geometric meaning of multiplying a matrix by a vector?](#matrices-as-geometric-transformations)
- [If matrix A has shape (5, 8) and matrix B has shape (8, 3), what is the shape of A @ B?](#matrix-multiplication-and-the-shape-rule)
- [How does matrix multiplication allow GPUs to compute document similarities in parallel?](#batching-dot-products-on-gpus)
- [Why are language models described as conditional probability distributions?](#conditional-probability-and-bayes-rule)
- [How does temperature mathematically alter the output of the softmax function?](#softmax-logits-and-temperature)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Immersive Linear Algebra](https://immersivemath.com/ila/index.html) is a fully interactive digital textbook with 3D rotatable figures for matrix operations.
- [Distill.pub: Visual Information Theory](https://distill.pub/2016/misread-tsne/) provides visual explanations of probability, entropy, and high-dimensional transformations.
- [Stanford CS229 Linear Algebra Review and Reference](https://cs229.stanford.edu/summer2020/cs229-linalg.pdf) is a concise 26-page reference sheet covering matrix norms, eigenvalues, and matrix calculus notation.