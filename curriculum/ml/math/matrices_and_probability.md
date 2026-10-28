<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A neural network is mostly two things: matrix multiplications that transform vectors, and probability distributions that turn raw scores into predictions. When a language model picks its next token, it multiplies a vector by a big matrix to get one score per token in its vocabulary, then turns those scores into probabilities and samples one. You met the sampling side in Context Windows and Sampling. This lesson gives you the math vocabulary underneath it, intuitively, so the neural network lessons later in this path read as "more of the same" instead of a wall of symbols.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a matrix is, and matrix-vector multiplication as a transformation.
- Matrix-matrix multiplication and why shapes have to line up.
- Probability distributions, both discrete and continuous.
- Expected value, variance and the normal distribution.
- Conditional probability and Bayes' rule.
- Softmax, logits and log probabilities.

### Key ideas

- **A matrix is a grid of numbers that transforms vectors.** Multiplying a matrix by a vector produces a new vector: each output entry is the dot product of one matrix row with the input. Geometrically this rotates, stretches or squashes space. A neural network layer is exactly this, plus a small nonlinearity.
- **Shapes must line up.** A matrix with shape `(m, n)` times a vector of length `n` gives a vector of length `m`. Most real bugs in ML code are shape mismatches, so get used to writing shapes next to every variable.
- **Matrix multiplication batches many dot products at once.** Multiplying a `(1000, 384)` matrix of document embeddings by one `384`-long query vector gives 1,000 similarity scores in a single operation. GPUs are fast at exactly this.
- **A probability distribution assigns a likelihood to every possible outcome, and the likelihoods add up to 1.** A language model's output at each step is a discrete distribution over its whole vocabulary.
- **Expected value is the probability-weighted average; variance measures spread.** The normal (bell curve) distribution is defined by those two numbers and shows up everywhere, including how network weights are initialized.
- **Conditional probability, `P(A | B)`, is the probability of A given that B happened.** A language model computes `P(next token | all previous tokens)`. Bayes' rule lets you flip a conditional around and is the basis of reasoning about evidence, such as how much an eval result should change your belief that a prompt is better.
- **Softmax turns raw scores (logits) into probabilities.** It exponentiates each score and divides by the total. Temperature divides the logits before softmax: low temperature sharpens the distribution, high temperature flattens it.
- **Log probabilities avoid tiny numbers.** Multiplying many small probabilities underflows to zero, so models work with logs and add them instead. The training loss you will see later, cross-entropy, is just the average negative log probability of the right answer.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Continue [3Blue1Brown's Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra) to build the picture of matrices as transformations.
   - Watch chapter 3 (linear transformations and matrices) and chapter 4 (matrix multiplication as composition).
1. Work through the probability basics in [Khan Academy Statistics and Probability](https://www.khanacademy.org/math/statistics-probability), which has short videos and practice problems with instant feedback.
   - Do the "Probability" unit (basic probability, conditional probability) and the "Random variables" unit up through expected value. Skip hypothesis testing for now.
1. Read chapter 6 of [Mathematics for Machine Learning](https://mml-book.github.io/) for the bridge between probability and ML notation.
   - Read sections 6.1 to 6.3 and the start of 6.5 (the Gaussian distribution). Skim the formulas; focus on the worked examples.
1. In Python with NumPy, write a `softmax(logits, temperature)` function. Feed it `[2.0, 1.0, 0.1]` at temperatures 0.2, 1.0 and 2.0 and print the results. Check that each output sums to 1, and describe in one sentence what temperature did.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Seeing Theory](https://seeing-theory.brown.edu/) is a free interactive visual introduction to probability and statistics from Brown University.
