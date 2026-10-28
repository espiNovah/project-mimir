<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Welcome to the Research Track. In the ML Foundations elective you used vectors and matrices to compute similarity and train small networks. Graduate courses and research papers assume much more: they write models as compositions of linear maps, reason about rank and eigenvalues, and use decompositions like the SVD without explaining them. This lesson takes you from "I can multiply matrices in NumPy" to "I can read a proof about matrices and follow it."

<div class="lesson-note" markdown="1">

#### About this track

The Research Track is optional. You do not need it to get a job building agents in industry, and the rest of the curriculum does not depend on it. It is meant for learners heading into a master's in agentic AI or machine learning, or into a research role. It pairs well with university coursework: you can take it before a program starts to arrive prepared, or alongside your courses as a second explanation. It is more mathematical than the rest of the curriculum. Expect to work problems with pen and paper, and expect some sections to take several passes.

</div>

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Vector spaces, subspaces, bases and dimension.
- Linear maps and how matrices represent them.
- The four fundamental subspaces and rank.
- Orthogonality, projections and least squares.
- Eigenvalues, eigenvectors and diagonalization.
- The singular value decomposition and low-rank approximation.
- Where these ideas show up in machine learning papers.

### Key ideas

- **A vector space is defined by its rules, not its contents.** Anything you can add and scale while satisfying a short list of axioms is a vector space: arrows, lists of numbers, polynomials, even functions. A *basis* is a minimal set of vectors that can build every vector in the space, and the number of vectors in any basis is the *dimension*.
- **A matrix is a linear map written in a chosen basis.** Multiplying by a matrix sends vectors from one space to another while preserving addition and scaling. Matrix multiplication is composition of maps, which is why it is associative but not commutative. Changing the basis changes the matrix but not the map.
- **Rank tells you how much information survives.** Every matrix has four fundamental subspaces: the column space, the null space, the row space and the left null space. The rank is the dimension of the column space. The rank-nullity theorem says rank plus the dimension of the null space equals the number of columns, so whatever the map does not preserve, it collapses to zero.
- **Projection is the geometry of least squares.** When a system has no exact solution, the best approximate solution projects the target onto the column space. The normal equations, the formula behind linear regression, come straight from requiring the error to be orthogonal to that space.
- **Eigenvectors are directions a map only stretches.** If a matrix has a full set of independent eigenvectors, it can be written as a change of basis, a diagonal scaling, and the change back. Symmetric matrices always can, with orthogonal eigenvectors and real eigenvalues (the spectral theorem). Covariance matrices and Hessians are symmetric, which is why this result shows up everywhere.
- **The SVD works for every matrix.** Any matrix factors into a rotation, a scaling by non-negative *singular values*, and another rotation. Keeping only the largest singular values gives the best low-rank approximation (the Eckart-Young theorem). PCA, LoRA's low-rank updates, and analyses of attention matrices all build on this.
- **Proofs are a skill you practice.** Master's courses grade you on whether you can show why something is true. Start by proving small facts yourself, such as "the null space is a subspace" or "eigenvectors of a symmetric matrix with distinct eigenvalues are orthogonal."

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch 3Blue1Brown's [Essence of Linear Algebra](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) series for geometric intuition before the formal treatment.
   - Watch the whole series. Pause and predict what a transformation will do before the animation shows it.
1. Work through [MIT OCW 18.06SC Linear Algebra](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/), Gilbert Strang's course with lectures, recitations, problem sets and solutions.
   - Cover Unit I (Ax = b and the four subspaces), Unit II (least squares, determinants and eigenvalues) and the SVD lecture in Unit III.
   - Do at least one problem set per unit with pen and paper before checking the solutions.
1. Read chapters 2 to 4 of [Mathematics for Machine Learning](https://mml-book.github.io/) by Deisenroth, Faisal and Ong (free PDF). It restates the same material in the notation ML papers use.
   - Chapter 2 (Linear Algebra), Chapter 3 (Analytic Geometry: inner products, orthogonal projections) and Chapter 4 (Matrix Decompositions: eigendecomposition and SVD).
   - Attempt at least five end-of-chapter exercises per chapter.
1. Practice in code: in NumPy, compute the SVD of a grayscale image (any photo converted to a 2D array), reconstruct it from the top 5, 20 and 50 singular values, and plot the reconstruction error against the rank. Then verify numerically that a random symmetric matrix has orthogonal eigenvectors.
1. Practice proofs: write short proofs (in Markdown with LaTeX math) that the null space of a matrix is a subspace, that rank(AB) is at most rank(A), and that a symmetric matrix's eigenvectors for distinct eigenvalues are orthogonal. Compare your proofs with the textbook versions.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Gilbert Strang's Linear Algebra book site](https://math.mit.edu/~gs/linearalgebra/) has the textbook's table of contents, exercises and extra material that match the 18.06 lectures.
- [Linear Algebra Done Right](https://linear.axler.net/) by Sheldon Axler is free online and teaches the subject proof-first, without determinants. Use it if your program is theory-heavy.
- [MIT 18.065 Matrix Methods in Data Analysis, Signal Processing, and Machine Learning](https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/) is Strang's follow-on course that applies these tools directly to machine learning.
