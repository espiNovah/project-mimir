<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Every model you have trained so far learned by following gradients. In Backpropagation and PyTorch you let autograd compute them. Research requires you to derive them yourself: to check that a new loss is differentiable, to work out why training diverges, or to read a paper whose method section is three pages of derivatives. This lesson covers multivariable calculus, matrix calculus, convexity and the optimizers that train modern models.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Partial derivatives, gradients, Jacobians and Hessians.
- The multivariable chain rule and why backpropagation is just the chain rule.
- Matrix calculus: taking derivatives with respect to vectors and matrices.
- Taylor expansions and what they say about step sizes.
- Convex sets, convex functions and why convexity guarantees a global minimum.
- Gradient descent, stochastic gradient descent, momentum and Adam.
- Constrained optimization with Lagrange multipliers.

### Key ideas

- **The gradient points uphill.** For a function of many variables, the gradient is the vector of partial derivatives. It points in the direction of steepest increase, so stepping against it decreases the function. The Jacobian generalizes this to vector-valued functions, and the Hessian (the matrix of second derivatives) describes curvature.
- **Backpropagation is the chain rule applied in a clever order.** A network is a composition of functions. The chain rule multiplies their Jacobians. Reverse-mode differentiation multiplies from the output backward, which costs about as much as one forward pass, no matter how many parameters there are.
- **Matrix calculus has rules worth memorizing.** Results such as the gradient of x<sup>T</sup>Ax being (A + A<sup>T</sup>)x let you derive gradients for whole layers at once. Always check shapes: the gradient of a scalar with respect to a matrix has the same shape as that matrix.
- **Taylor expansions explain learning rates.** Near a point, a smooth function looks like its first-order (linear) plus second-order (quadratic) approximation. If the step is too large for the curvature, the quadratic term dominates and the loss goes up. This is why the largest stable learning rate depends on the largest eigenvalue of the Hessian.
- **Convexity makes optimization easy to reason about.** A function is convex if the line segment between any two points on its graph lies above the graph. For convex functions every local minimum is global, and gradient descent provably converges. Logistic regression is convex. Deep networks are not, so their guarantees are weaker and their behavior is studied empirically.
- **Stochastic gradients trade accuracy for speed.** SGD estimates the gradient from a mini-batch. The estimate is unbiased but noisy. Momentum averages past gradients to smooth the path. Adam also rescales each parameter by a running estimate of its gradient's magnitude, which is why it works well with little tuning.
- **Constraints become penalties.** Lagrange multipliers turn "minimize f subject to g = 0" into finding stationary points of f plus a multiple of g. Duality, KKT conditions and support vector machines all build on this, and so does the KL-constrained objective in RLHF.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch 3Blue1Brown's [Essence of Calculus](https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr) series if single-variable derivatives, the chain rule or Taylor series feel shaky.
   - Focus on the chain rule, implicit differentiation and Taylor series videos.
1. Work through [Khan Academy's Multivariable Calculus](https://www.khanacademy.org/math/multivariable-calculus) for partial derivatives, gradients and Lagrange multipliers with practice exercises.
   - Do the "Derivatives of multivariable functions" and "Applications of multivariable derivatives" units, including the quizzes.
1. Read chapters 5 and 7 of [Mathematics for Machine Learning](https://mml-book.github.io/).
   - Chapter 5 (Vector Calculus) covers gradients of vectors and matrices and backpropagation. Chapter 7 (Continuous Optimization) covers gradient descent, constrained optimization and convexity.
1. Read [The Matrix Calculus You Need For Deep Learning](https://explained.ai/matrix-calculus/) by Terence Parr and Jeremy Howard, a practical guide to deriving gradients for whole layers.
   - Read it all, then derive the gradient of mean squared error for a linear layer yourself and check it against the article.
1. Read chapters 2, 3 and 9 of Boyd and Vandenberghe's [Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/) (free PDF on the book's Stanford page), the standard graduate text.
   - Chapter 2 (Convex sets) and chapter 3 (Convex functions) for definitions; chapter 9 (Unconstrained minimization) for gradient descent and Newton's method with convergence proofs. Skim the proofs on a first pass and return to them later.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Stanford EE364A lectures by Stephen Boyd](https://see.stanford.edu/Course/EE364A) are the free video lectures for the Convex Optimization book.
- [Why Momentum Really Works](https://distill.pub/2017/momentum/) on Distill uses interactive plots to show how momentum changes the path of gradient descent.
- [An overview of gradient descent optimization algorithms](https://ruder.io/optimizing-gradient-descent/) by Sebastian Ruder compares SGD, momentum, RMSProp, Adam and others in one place.
- [The Adam paper](https://arxiv.org/abs/1412.6980) by Kingma and Ba is short and readable once you know the ideas above.
