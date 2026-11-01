### Introduction

Welcome to the Research Track. In the [ML Foundations](#/paths/ml) path, you used vectors and matrices to compute similarities, run forward passes, and train LoRA adapters.

Graduate machine learning courses, theoretical papers, and advanced AI research laboratories assume much more mathematical maturity. Research papers express transformer layers as compositions of linear maps, analyze the rank of weight matrices to understand representation collapse, compute eigenvalues of Hessian matrices to study optimization landscapes, and apply the Singular Value Decomposition (SVD) to analyze low-rank adaptation.

This lesson takes you from "I know how to multiply matrices in NumPy" to "I can follow proofs about linear maps and understand why matrix decompositions matter."

<div class="lesson-note lesson-note--tip" markdown="1">

#### Prerequisites

This section assumes you have completed the [ML Foundations](#/paths/ml) path, particularly [Just Enough Math](#/paths/ml) and [Neural Networks & Transformers](#/paths/ml). You should already be comfortable with vectors, matrix-vector products, dot products, and basic NumPy syntax.

</div>

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Vector spaces, subspaces, linear independence, spanning sets, bases, and dimension.
- Linear maps and how matrices represent coordinate transformations across bases.
- The four fundamental subspaces of a matrix (column space, null space, row space, left null space) and the rank-nullity theorem.
- Orthogonality, projections onto subspaces, the normal equations, and least-squares optimization.
- Eigenvalues, eigenvectors, diagonalizability, and the Spectral Theorem for symmetric matrices.
- The Singular Value Decomposition (SVD) and low-rank matrix approximation via the Eckart-Young-Mirsky theorem.
- Where these mathematical structures appear directly in frontier transformer and LLM research.

### Vector spaces, subspaces, and bases

Mathematicians define a **vector space** by its algebraic rules rather than by the objects it contains.

A vector space `V` over a field (such as the real numbers `R`) is any collection of objects that is closed under two fundamental operations:
1. **Vector addition:** If `u` and `v` are in `V`, then `u + v` is in `V`.
2. **Scalar multiplication:** If `v` is in `V` and `c` is a real number, then `c * v` is in `V`.

These operations must satisfy eight standard axioms (associativity, commutativity, existence of a zero vector, additive inverses, and distributive laws). Under this definition, standard lists of numbers like `R^n` are vector spaces. But so are continuous functions, polynomials of degree at most `k`, and `m x n` matrices!

A **subspace** is a subset of a vector space that is itself a vector space. To verify that a subset `S` is a valid subspace, you only need to verify three properties:
- The zero vector `0` is in `S`.
- `S` is closed under addition: if `u, v` are in `S`, then `u + v` is in `S`.
- `S` is closed under scalar multiplication: if `v` is in `S`, then `c * v` is in `S`.

A set of vectors `{v1, v2, ..., vk}` is **linearly independent** if no vector in the set can be expressed as a linear combination of the others:

```text
c1*v1 + c2*v2 + ... + ck*vk = 0   only when   c1 = c2 = ... = ck = 0
```

If any non-zero coefficients exist that sum to zero, at least one vector is redundant.

A **basis** for a vector space `V` is a set of vectors that is both linearly independent and spans all of `V`. The number of vectors in any basis for `V` is unique and defines the **dimension** of the space:

```text
dim(V) = number of basis vectors
```

### Linear maps and change of basis

A **linear map** (or linear transformation) `T: V -> W` is a function from vector space `V` to vector space `W` that preserves linear combinations:

```text
T(c1*u + c2*v) = c1*T(u) + c2*T(v)
```

A **matrix** is simply the numerical representation of a linear map with respect to a chosen basis.

If you choose a basis `{v1, ..., vn}` for the input space `V` and a basis `{w1, ..., wm}` for the output space `W`, the `j`-th column of matrix `A` consists of the coordinates of `T(vj)` expressed in the output basis:

```text
T(x) = A @ x
```

Matrix multiplication is the algebraic equivalent of **composing** two linear maps: `(T2 ∘ T1)(x) = A2 @ (A1 @ x)`. Because function composition is associative but generally not commutative, matrix multiplication satisfies `A(BC) = (AB)C`, but `AB != BA`.

If you change the basis you use to describe vectors, the matrix representing the linear map changes through a similarity transformation:

```text
A_new = P^(-1) @ A_old @ P
```

where `P` is the change-of-basis matrix. The map `T` remains identical; only its coordinate representation has shifted.

### The four fundamental subspaces and rank-nullity

Gilbert Strang famously unified linear algebra around the **four fundamental subspaces** associated with any `m x n` matrix `A`:

![The Four Fundamental Subspaces of Linear Algebra](assets/images/four_fundamental_subspaces.svg)

1. **Column Space `C(A)`:** The span of the columns of `A`. It is a subspace of `R^m`. The equation `A @ x = b` has a solution if and only if `b` lies in `C(A)`.
2. **Null Space `N(A)`:** The set of all vectors `x` in `R^n` such that `A @ x = 0`. It measures what the matrix destroys by collapsing to zero.
3. **Row Space `C(A^T)`:** The span of the rows of `A` (or columns of `A^T`). It is a subspace of `R^n` orthogonal to `N(A)`.
4. **Left Null Space `N(A^T)`:** The set of all vectors `y` in `R^m` such that `A^T @ y = 0`. It is orthogonal to `C(A)`.

The **rank** `r` of a matrix is the dimension of its column space (which equals the dimension of its row space):

```text
rank(A) = dim(C(A)) = dim(C(A^T))
```

The fundamental **Rank-Nullity Theorem** states:

```text
dim(C(A)) + dim(N(A)) = n
rank(A) + nullity(A) = number of columns
```

Whatever information is not preserved in the column space is sent directly to the null space. When you train a model with low-rank adapters in LoRA, you are deliberately constraining the rank of weight updates, ensuring that the model modifies only a small subspace of representations.

### Orthogonality, projections, and least squares

Two vectors `u` and `v` are **orthogonal** if their inner product is zero: `u · v = 0`. A set of vectors is **orthonormal** if every vector is orthogonal to every other vector and has unit length (`norm(vi) = 1`).

When an overdetermined system `A @ x = b` has no exact solution (meaning `b` does not lie in the column space `C(A)`), what is the best possible approximation?

Geometrically, the closest vector in `C(A)` to `b` is the **orthogonal projection** of `b` onto `C(A)`, denoted `p = A @ x_hat`.

![Orthogonal Projection and Ordinary Least Squares](assets/images/orthogonal_projection.svg)

The error vector `e = b - A @ x_hat` must be perpendicular to every column in `A`:

```text
A^T @ (b - A @ x_hat) = 0
A^T @ b - A^T @ A @ x_hat = 0
A^T @ A @ x_hat = A^T @ b
```

These are the famous **normal equations**. If the columns of `A` are linearly independent, `A^T @ A` is invertible, giving the analytical least-squares solution:

```text
x_hat = (A^T @ A)^(-1) @ A^T @ b
```

The projection matrix that maps any vector `b` directly onto `C(A)` is:

```text
P = A @ (A^T @ A)^(-1) @ A^T
```

Notice that `P` satisfies `P^2 = P` (projecting twice does nothing new) and `P^T = P` (symmetric).

### Eigenvalues, eigenvectors, and the spectral theorem

For most vectors `x`, multiplying by a square matrix `A` changes both its length and its direction.

However, certain special vectors maintain their exact direction when transformed by `A`. These are **eigenvectors**, and the factor by which they are scaled is the **eigenvalue** `lambda`:

```text
A @ v = lambda * v
```

Rearranging gives `(A - lambda * I) @ v = 0`. For a non-zero eigenvector `v` to exist, the matrix `(A - lambda * I)` must have a non-trivial null space, which occurs when its determinant is zero:

```text
det(A - lambda * I) = 0
```

This polynomial equation in `lambda` is the **characteristic equation**.

If an `n x n` matrix `A` has `n` linearly independent eigenvectors, we can assemble them as the columns of an invertible matrix `V` and form a diagonal matrix `Lambda` of eigenvalues:

```text
A = V @ Lambda @ V^(-1)
```

This is **eigendecomposition** (diagonalization). Computing powers of `A` becomes trivial: `A^k = V @ (Lambda^k) @ V^(-1)`, where `Lambda^k` simply raises each diagonal eigenvalue to the power `k`.

#### The Spectral Theorem for symmetric matrices
In machine learning, the most important matrices—covariance matrices, Gram matrices, Graph Laplacians, and Hessians—are **symmetric** (`A^T = A`).

The **Spectral Theorem** guarantees two properties for any real symmetric matrix:
1. All eigenvalues are real numbers (no complex numbers).
2. There exists an orthonormal basis of eigenvectors: `V^(-1) = V^T`.

Therefore, every real symmetric matrix can be orthogonally diagonalized:

```text
A = Q @ Lambda @ Q^T
```

where `Q` is an orthogonal matrix (`Q^T @ Q = I`). Geometrically, a symmetric matrix acts by rotating space to align with its eigenvectors, scaling along each axis by `lambda_i`, and rotating back.

### Singular Value Decomposition (SVD) and low-rank approximation

Eigendecomposition only applies to square matrices. The **Singular Value Decomposition (SVD)** is the ultimate theorem of linear algebra because it applies to **every matrix**, regardless of shape or rank.

Any real `m x n` matrix `A` can be factored into:

```text
A = U @ Sigma @ V^T
```

- `U` is an `m x m` orthogonal matrix whose columns are the **left singular vectors** (the eigenvectors of `A @ A^T`).
- `Sigma` is an `m x n` diagonal matrix containing non-negative real numbers called **singular values** arranged in descending order: `sigma_1 >= sigma_2 >= ... >= sigma_r > 0`.
- `V` is an `n x n` orthogonal matrix whose columns are the **right singular vectors** (the eigenvectors of `A^T @ A`).

```text
           [   U   ]          [ Sigma ]          [   V^T   ]
          (m x m rotation)   (m x n scaling)    (n x n rotation)
```

The SVD can also be written as a sum of rank-1 outer products:

```text
A = sum_{i=1}^{r} sigma_i * (u_i @ v_i^T)
```

Each outer product `u_i @ v_i^T` is a matrix of rank 1.

#### The Eckart-Young-Mirsky Theorem
If you truncate the SVD sum to only the first `k` terms (where `k < r`):

```text
A_k = sum_{i=1}^{k} sigma_i * (u_i @ v_i^T)
```

The Eckart-Young theorem proves that `A_k` is the **optimal rank-k approximation** of matrix `A` under both the Frobenius norm and the spectral norm:

```text
min_{rank(B) = k} ||A - B||_F = ||A - A_k||_F = sqrt(sum_{j=k+1}^{r} sigma_j^2)
```

This single mathematical theorem is the theoretical foundation of Principal Component Analysis (PCA), latent semantic analysis in search, matrix compression, and low-rank representation analysis in deep learning.

### Demonstrating SVD in Python

Here is a practical Python demonstration using NumPy that verifies the SVD factorization, reconstructs a matrix using low-rank truncation, and verifies the Spectral Theorem:

```python
# svd_lab.py: Exploring SVD and the Spectral Theorem with NumPy
import numpy as np

# 1. Generate a random matrix of shape (100, 50) with rank 15
np.random.seed(42)
U_rand, _ = np.linalg.qr(np.random.randn(100, 15))
V_rand, _ = np.linalg.qr(np.random.randn(50, 15))
s_true = np.linspace(10.0, 1.0, 15)

A = U_rand @ np.diag(s_true) @ V_rand.T  # Shape: (100, 50), true rank = 15

# 2. Compute full SVD
U, s, Vt = np.linalg.svd(A, full_matrices=False)

print("Shape of U:", U.shape)        # (100, 50)
print("Shape of s:", s.shape)        # (50,)
print("Shape of Vt:", Vt.shape)      # (50, 50)
print(f"Top 5 singular values: {np.round(s[:5], 3)}")
print(f"16th singular value (should be zero): {s[15]:.2e}")

# 3. Low-rank approximation using Eckart-Young truncation (rank k = 5)
k = 5
A_k = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]
frobenius_error = np.linalg.norm(A - A_k, ord='fro')
theoretical_error = np.sqrt(np.sum(s[k:] ** 2))

print(f"Measured Frobenius error:    {frobenius_error:.5f}")
print(f"Theoretical Eckart-Young:    {theoretical_error:.5f}")
assert np.isclose(frobenius_error, theoretical_error)

# 4. Verifying the Spectral Theorem on a symmetric matrix
S = A.T @ A  # Shape: (50, 50), symmetric
eigenvalues, Q = np.linalg.eigh(S)

# Check that eigenvectors Q are orthonormal: Q^T @ Q = I
ortho_check = np.allclose(Q.T @ Q, np.eye(50))
print(f"Eigenvectors are orthonormal: {ortho_check}")
```

### Where this linear algebra appears in frontier AI research

Understanding these theorems changes how you read modern research literature:

- **Mechanistic Interpretability:** Research into transformer circuits (such as Anthropic's Transformer Circuits thread) decomposes the attention mechanism into `W_QK = W_Q^T @ W_K` and `W_OV = W_O @ W_V`. Analyzing the singular values of `W_OV` reveals whether an attention head functions as an induction head or a subspace copy mechanism.
- **LoRA and Representation Rank:** The original LoRA paper showed that the weight change matrix `ΔW` has a rapidly decaying singular value spectrum. Most adaptation capacity is concentrated in the top 4 to 16 singular vectors, which is why a rank of 8 or 16 is sufficient to fine-tune billions of parameters.
- **Hessian Eigenspectra:** In optimization research, the eigenvalues of the Hessian matrix `H = ∇^2 L` measure the curvature of the loss surface. The maximum eigenvalue `lambda_max` governs the maximum stable learning rate for gradient descent (`lr < 2 / lambda_max`).

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch 3Blue1Brown's [Essence of Linear Algebra](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) video series.
   - Rewatch the chapters on eigenvectors and eigenvalues, change of basis, and linear transformations.
1. Work through the core lectures in [MIT OCW 18.06SC Linear Algebra](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/) by Gilbert Strang.
   - Study Lecture 14 (The four fundamental subspaces), Lecture 15 (Projections onto subspaces), Lecture 21 (Eigenvalues and eigenvectors), and Lecture 29 (Singular Value Decomposition).
   - Solve at least three problem set problems from Unit II with pen and paper before consulting solutions.
1. Read Chapters 2, 3, and 4 of [Mathematics for Machine Learning](https://mml-book.github.io/) by Deisenroth, Faisal, and Ong.
   - Chapter 2: Linear systems and linear independence.
   - Chapter 3: Inner products, lengths, distances, and orthogonal projections.
   - Chapter 4: Eigendecomposition and SVD.
1. Write a standalone Python script named `svd_image_compressor.py`:
   - Load a grayscale image as a 2D NumPy array.
   - Compute its SVD using `np.linalg.svd`.
   - Reconstruct the image at rank `k = 5, 20, 50, 100`.
   - Compute and print the compression ratio (storing `k * (m + n + 1)` floats vs `m * n` floats) and the relative reconstruction error `||A - A_k|| / ||A||`.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [What is the difference between a vector space and a subspace?](#vector-spaces-subspaces-and-bases)
- [What is the relationship between a matrix's rank and the dimension of its null space?](#the-four-fundamental-subspaces-and-rank-nullity)
- [How does the geometry of orthogonal projection lead to the normal equations in least squares?](#orthogonality-projections-and-least-squares)
- [What does the Spectral Theorem guarantee about real symmetric matrices?](#eigenvalues-eigenvectors-and-the-spectral-theorem)
- [What does the Eckart-Young-Mirsky theorem state about SVD low-rank approximations?](#singular-value-decomposition-svd-and-low-rank-approximation)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Gilbert Strang's Linear Algebra Course Site](https://math.mit.edu/~gs/linearalgebra/) includes lecture notes and supplemental problem sets.
- [Linear Algebra Done Right](https://linear.axler.net/) by Sheldon Axler is an elegant, proof-focused conceptual textbook that approaches linear algebra without relying on determinants.
- [MIT 18.065: Matrix Methods in Data Analysis and Machine Learning](https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/) connects advanced matrix theory directly to modern neural networks.