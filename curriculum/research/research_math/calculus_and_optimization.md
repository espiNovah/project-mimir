### Introduction

Every machine learning model you have trained in this curriculum learned by following gradients. In [Backpropagation and PyTorch](#/paths/ml), you let PyTorch's `autograd` engine compute derivatives automatically.

In academic research and graduate coursework, relying entirely on black-box autodiff is not enough. You will need to derive custom objective functions by hand, check whether a new regularizer is smooth, understand why training becomes unstable when loss curvature spikes, and read research papers whose methodology sections consist of dense matrix derivatives.

This lesson covers the core optimization mathematics behind modern deep learning: multivariable calculus, matrix calculus identities, second-order Taylor approximations, convexity, the mechanics of modern adaptive optimizers (SGD, Momentum, AdamW), and constrained optimization using Lagrange multipliers.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Partial derivatives, the gradient vector, the Jacobian matrix, and the Hessian curvature matrix.
- How reverse-mode automatic differentiation computes gradients for millions of parameters in a single backward pass.
- Key matrix calculus rules for taking derivatives with respect to vectors and matrices.
- Taylor series expansions and how the maximum eigenvalue of the Hessian dictates learning rate stability.
- Convex optimization versus the non-convex empirical loss landscapes of deep neural networks.
- First-order optimization algorithms: Stochastic Gradient Descent, Momentum, RMSprop, and AdamW.
- Constrained optimization with Lagrange multipliers and their role in KL-regularized objectives (such as RLHF).

### Gradients, Jacobians, and the Hessian matrix

When a function takes multiple inputs, we measure its rates of change using partial derivatives.

Suppose a scalar function `f: R^n -> R` takes a vector of `n` parameters `x = [x1, x2, ..., xn]`. The **gradient** `∇f(x)` is the vector containing all `n` first-order partial derivatives:

```text
∇f(x) = [ ∂f/∂x1,  ∂f/∂x2,  ...,  ∂f/∂xn ]^T
```

Geometrically, the gradient vector points in the direction of **steepest ascent** (maximum rate of increase). Stepping in the opposite direction, `-∇f(x)`, moves in the direction of steepest descent.

When a function outputs a vector rather than a single number—such as a neural network layer mapping `n` inputs to `m` outputs, `f: R^n -> R^m`—its first derivatives form an `m x n` matrix called the **Jacobian** `J`:

```text
J_{i, j} = ∂f_i / ∂x_j
```

The Jacobian represents the best linear approximation of the vector-valued function near a point `x`.

To measure how the slope itself is changing, we compute second-order partial derivatives. For a scalar function `f: R^n -> R`, these form an `n x n` symmetric matrix called the **Hessian** `H`:

```text
H_{i, j} = ∂^2 f / (∂x_i ∂x_j)
```

The Hessian describes the local **curvature** of the function:
- If all eigenvalues of `H` are strictly positive (the Hessian is **positive definite**), the surface curves upward in every direction, indicating a local minimum.
- If all eigenvalues are negative (**negative definite**), the surface curves downward in every direction (a local maximum).
- If some eigenvalues are positive and others are negative (**indefinite**), the point is a **saddle point**—sloping upward along some axes and downward along others. In high-dimensional neural network loss surfaces, most critical points with zero gradient are saddle points rather than local minima.

### Matrix calculus rules for neural network layers

In deep learning papers, deriving gradients element by element using scalar calculus is tedious and error-prone. Modern research uses **matrix calculus**, treating vectors and matrices as atomic units.

The fundamental shape convention in machine learning:
> The derivative of a scalar loss `L` with respect to a matrix `W` has the exact same shape as `W`.

A few foundational matrix calculus identities appear in nearly every derivation:

1. **Linear form:** For vectors `x` and constant vector `a`:
```text
∂(a^T @ x) / ∂x = a
```

2. **Quadratic form:** For symmetric matrix `A`:
```text
∂(x^T @ A @ x) / ∂x = 2 * A @ x
```
(If `A` is not symmetric, the derivative is `(A + A^T) @ x`).

3. **Dense linear layer:** Suppose a layer computes `y = W @ x + b`, and a scalar loss `L` depends on `y`. Let `g = ∂L/∂y` be the incoming gradient vector:
```text
∂L/∂b = g
∂L/∂x = W^T @ g
∂L/∂W = g @ x^T  (outer product of incoming gradient with input)
```

Notice how dimensional shapes enforce the algebra:
- If `x` is `(d_in, 1)` and `y` is `(d_out, 1)`, then `W` is `(d_out, d_in)`.
- The incoming gradient `g = ∂L/∂y` is `(d_out, 1)`.
- To get a gradient for `W` with shape `(d_out, d_in)`, we multiply `g` of shape `(d_out, 1)` by `x^T` of shape `(1, d_in)`. The result `g @ x^T` has shape `(d_out, d_in)`.

Dimensional consistency is your strongest sanity check when verifying mathematical derivations.

### Taylor expansions and learning rate stability

Near any point `x0`, any smooth function can be approximated by its **Taylor series expansion**:

```text
f(x0 + Δx) ≈ f(x0) + ∇f(x0)^T @ Δx + (1/2) * Δx^T @ H @ Δx
```

- The first-order term `∇f(x0)^T @ Δx` is the linear tangent plane.
- The second-order term `(1/2) * Δx^T @ H @ Δx` accounts for local curvature.

In standard gradient descent, we take a step `Δx = -η * ∇f(x0)`, where `η` is the learning rate. Substituting this into the Taylor expansion gives:

```text
f(x0 - η * g) ≈ f(x0) - η * ||g||^2 + (1/2) * η^2 * (g^T @ H @ g)
```

Notice the battle between the first-order and second-order terms:
- The first-order term `-η * ||g||^2` always reduces the loss.
- But if the learning rate `η` is chosen too large, the quadratic term `(1/2) * η^2 * (g^T @ H @ g)` grows with `η^2` and dominates, causing the loss to explode!

Let `λ_max` be the largest eigenvalue of the Hessian matrix `H`. The maximum mathematically stable learning rate for gradient descent is:

```text
η < 2 / λ_max
```

If `η > 2 / λ_max`, gradient descent overshoots the valley floor and oscillates toward infinity. This is why loss spikes occur during pre-training: when a batch causes the local curvature `λ_max` to spike, a previously stable learning rate suddenly exceeds the stability threshold.

### Convexity versus non-convex loss surfaces

A set `C` is **convex** if the line segment connecting any two points in `C` lies entirely within `C`.

A function `f` is a **convex function** if its epigraph (the region above the graph) is a convex set:

```text
f(t * x + (1 - t) * y) <= t * f(x) + (1 - t) * f(y)   for all t in [0, 1]
```

For twice-differentiable functions, `f` is convex if and only if its Hessian matrix `H` is **positive semi-definite** (`x^T @ H @ x >= 0` for all `x`) everywhere.

Convex optimization is the bedrock of classical machine learning (linear regression, logistic regression, support vector machines) because:
- **Every local minimum is a global minimum.**
- Gradient descent provably converges to the optimal solution.
- Highly efficient interior-point and Newton algorithms can solve problems to machine precision.

Deep neural networks are **strictly non-convex**. Their loss surfaces contain trillions of parameters, countless saddle points, flat plateaus, and bad local valleys. While theoretical convergence guarantees do not apply to deep networks, empirical optimization works remarkably well in practice because high-dimensional saddle points almost always have escape directions with negative eigenvalues.

### Optimizers: from SGD to Momentum and AdamW

The geometry of neural network loss surfaces is notoriously ill-conditioned: ravines that are extremely steep along some dimensions and nearly flat along others.

![Optimization landscapes: SGD vs Momentum vs Adam navigating a loss valley](assets/images/gradient_descent_optimizers.svg)

1. **Standard Stochastic Gradient Descent (SGD):**
```text
θ_{t+1} = θ_t - η * g_t
```
In an elongated valley, the gradient points almost entirely across the steep walls rather than along the gentle base. Standard SGD oscillates wildly back and forth across the valley, making agonizingly slow forward progress.

2. **SGD with Momentum:**
Momentum introduces a velocity vector `v` that accumulates past gradients with an exponential decay factor `β` (typically `0.9`):
```text
v_{t+1} = β * v_t + g_t
θ_{t+1} = θ_t - η * v_{t+1}
```
Oscillating gradients across the steep walls cancel each other out in the running sum, while persistent gradients along the valley floor reinforce each other. The optimizer builds momentum and accelerates down the ravine.

3. **AdamW (Adaptive Moment Estimation with Decoupled Weight Decay):**
Adam maintains both a running average of the gradient (**first moment**, momentum `m`) and a running average of the squared gradient (**second moment**, uncentered variance `v`):
```text
m_t = β1 * m_{t-1} + (1 - β1) * g_t          (typically β1 = 0.9)
v_t = β2 * v_{t-1} + (1 - β2) * (g_t)^2       (typically β2 = 0.999)

m_hat = m_t / (1 - β1^t)                      (bias correction)
v_hat = v_t / (1 - β2^t)                      (bias correction)

θ_{t+1} = θ_t - η * (m_hat / (sqrt(v_hat) + ε)) - η * λ * θ_t
```

Dividing by `sqrt(v_hat)` automatically rescales the update: parameters with large, erratic gradients receive smaller step sizes, while parameters with infrequent or small gradients receive larger step sizes. **AdamW** decouples the weight decay regularizer `λ * θ_t` from the adaptive gradient updates, which is why it serves as the universal default optimizer for training transformers.

### Constrained optimization and Lagrange multipliers

Often, optimization problems require minimizing an objective subject to explicit constraints:

```text
minimize f(x)    subject to g(x) = 0
```

At the constrained optimum, the contour line of the objective `f` must be tangent to the constraint boundary `g(x) = 0`. That means their gradient vectors must point in the exact same (or opposite) direction:

```text
∇f(x) = -λ * ∇g(x)
```

The scalar `λ` is called the **Lagrange multiplier**. We combine the objective and constraint into a single function called the **Lagrangian**:

```text
L(x, λ) = f(x) + λ * g(x)
```

Finding the constrained minimum is converted into finding a stationary point where all partial derivatives of `L` are zero: `∂L/∂x = 0` and `∂L/∂λ = 0`.

Where does this appear in modern AI?
- **Support Vector Machines:** Maximizing margin subject to classification constraints.
- **Reinforcement Learning from Human Feedback (RLHF):** In [RL for Language Models](#/paths/research), the objective maximizes expected reward while constraining the policy from drifting too far from the initial model:
```text
maximize E[R(x, y)]   subject to   D_KL(π(y|x) || π_ref(y|x)) <= ε
```
Formulating this with Lagrange multipliers converts the hard constraint into the familiar penalized KL-divergence objective used in InstructGPT and DPO.

### Python comparison: SGD vs. Momentum vs. Adam

The script below demonstrates the performance of SGD, Momentum, and Adam on an ill-conditioned quadratic function `f(x1, x2) = 0.1*x1^2 + 2.0*x2^2` (20x steeper along `x2` than `x1`):

```python
# optimizer_comparison.py: Comparing SGD, Momentum, and Adam on an ill-conditioned surface
import numpy as np

def loss_func(x):
    # Elliptical valley: x2 is 20x steeper than x1
    return 0.1 * x[0]**2 + 2.0 * x[1]**2

def grad_func(x):
    return np.array([0.2 * x[0], 4.0 * x[1]])

def run_optimizer(opt_type, lr=0.4, steps=40):
    x = np.array([10.0, 5.0])  # Starting point
    trajectory = [x.copy()]
    
    # State variables
    v = np.zeros(2)
    m = np.zeros(2)
    s = np.zeros(2)
    
    for t in range(1, steps + 1):
        g = grad_func(x)
        if opt_type == "sgd":
            x = x - lr * g
        elif opt_type == "momentum":
            v = 0.85 * v + g
            x = x - lr * v
        elif opt_type == "adam":
            beta1, beta2, eps = 0.9, 0.999, 1e-8
            m = beta1 * m + (1 - beta1) * g
            s = beta2 * s + (1 - beta2) * (g ** 2)
            m_hat = m / (1 - beta1 ** t)
            s_hat = s / (1 - beta2 ** t)
            x = x - lr * (m_hat / (np.sqrt(s_hat) + eps))
            
        trajectory.append(x.copy())
        
    return np.array(trajectory)

traj_sgd = run_optimizer("sgd", lr=0.45, steps=30)
traj_mom = run_optimizer("momentum", lr=0.15, steps=30)
traj_adam = run_optimizer("adam", lr=1.0, steps=30)

print(f"Initial loss: {loss_func(traj_sgd[0]):.2f}")
print(f"Final loss (SGD):      {loss_func(traj_sgd[-1]):.5f}")
print(f"Final loss (Momentum): {loss_func(traj_mom[-1]):.5f}")
print(f"Final loss (Adam):     {loss_func(traj_adam[-1]):.5f}")
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the partial derivatives and gradient material in [Khan Academy's Multivariable Calculus](https://www.khanacademy.org/math/multivariable-calculus).
   - Review "Derivatives of multivariable functions" and "Applications of multivariable derivatives" (especially gradients and Lagrange multipliers).
1. Read Chapters 5 and 7 of [Mathematics for Machine Learning](https://mml-book.github.io/).
   - Chapter 5: Matrix calculus, Jacobians, and backpropagation proofs.
   - Chapter 7: Convex optimization, gradient descent convergence, and constrained optimization.
1. Read [The Matrix Calculus You Need For Deep Learning](https://explained.ai/matrix-calculus/) by Terence Parr and Jeremy Howard.
   - Work through the derivation of the gradient of mean squared error with respect to weights for a linear layer, and verify the shapes.
1. Read Chapters 2 and 3 of Boyd and Vandenberghe's [Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/).
   - Understand the definition of convex sets, convex functions, and positive semi-definite Hessians.
1. Explore the interactive visual demonstrations on [Distill: Why Momentum Really Works](https://distill.pub/2017/momentum/).
   - Interact with the sliders to observe how momentum damps oscillations and accelerates through conditioning bottlenecks.
1. Read [The Adam Paper (Kingma & Ba, 2014)](https://arxiv.org/abs/1412.6980).
   - Read Section 2 (Algorithm) and note how the bias correction terms `1 - beta^t` prevent step sizes from exploding near step `t = 1`.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [What geometric property does the gradient vector possess?](#gradients-jacobians-and-the-hessian-matrix)
- [What does the Hessian matrix measure, and how do its eigenvalues classify critical points?](#gradients-jacobians-and-the-hessian-matrix)
- [How does the maximum eigenvalue of the Hessian determine the maximum stable learning rate?](#taylor-expansions-and-learning-rate-stability)
- [Why is convex optimization easier to analyze mathematically than neural network optimization?](#convexity-versus-non-convex-loss-surfaces)
- [How does AdamW's second moment estimate prevent oscillations in ill-conditioned loss valleys?](#optimizers-from-sgd-to-momentum-and-adamw)
- [What is the core intuition behind using Lagrange multipliers for constrained optimization?](#constrained-optimization-and-lagrange-multipliers)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Stanford EE364A: Convex Optimization I (Stephen Boyd)](https://see.stanford.edu/Course/EE364A) contains the full video lecture series for the convex optimization textbook.
- [An Overview of Gradient Descent Optimization Algorithms (Sebastian Ruder)](https://ruder.io/optimizing-gradient-descent/) is a classic reference article surveying modern first-order optimizers.
- [Decoupled Weight Decay Regularization (Loshchilov & Hutter, 2019)](https://arxiv.org/abs/1711.05101) is the paper that introduced AdamW, explaining why L2 regularization breaks in standard Adam.