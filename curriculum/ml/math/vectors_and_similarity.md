<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Back in What Embeddings Are, you turned text into long lists of numbers and compared them with something called cosine similarity. You used it as a black box. This lesson opens the box. A vector is just a list of numbers, and a handful of simple operations on vectors (adding, scaling, the dot product, the length) explain why retrieval works, why embeddings are usually normalized, and why "close in vector space" can mean "similar in meaning."

You will not need calculus or proofs here. You need enough intuition to reason about embeddings, debug a retrieval system that returns strange results, and answer "why cosine and not Euclidean distance?" in an interview.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a vector is, both as a list of numbers and as an arrow in space.
- Vector addition and scaling, and what they mean geometrically.
- The dot product and what it measures.
- Vector length (the norm) and normalization to unit length.
- Cosine similarity, and how it relates to the dot product and Euclidean distance.
- Why high-dimensional embedding spaces behave the way they do.

### Key ideas

- **A vector is an ordered list of numbers.** `[3, 4]` is a point (or arrow) in 2D space. An embedding from a modern model is the same thing with 384, 1,024 or more numbers. Every operation you learn in 2D works unchanged in 1,024 dimensions; you just can't draw it.
- **The dot product multiplies matching entries and adds them up.** For `a = [1, 2]` and `b = [3, 4]`, `a · b = 1×3 + 2×4 = 11`. It is large and positive when the vectors point the same way, near zero when they are perpendicular (unrelated), and negative when they point in opposite directions.
- **The norm is a vector's length.** It is the square root of the vector dotted with itself: `‖[3, 4]‖ = √(9 + 16) = 5`. Dividing a vector by its norm gives a unit vector of length 1 that keeps only the direction.
- **Cosine similarity is the dot product of two unit vectors.** Formally `cos(a, b) = (a · b) / (‖a‖ ‖b‖)`. It ranges from -1 to 1 and ignores length, so a long document and a short one about the same topic can still score as similar.
- **When vectors are already normalized, cosine similarity and the dot product are identical**, and ranking by Euclidean distance gives the same order too. That is why many embedding APIs return unit vectors and many vector databases just use the dot product: it is the cheapest operation.
- **Meaning lives in direction.** Embedding models are trained so that texts used in similar contexts end up pointing in similar directions. Similarity scores are relative, not absolute: 0.6 might be "very close" for one model and "unrelated" for another, so compare rankings, not raw thresholds across models.
- **High dimensions are strange.** In very high-dimensional spaces, random vectors are almost always nearly perpendicular. That is part of why embeddings can pack so many distinct concepts into one space.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch the first chapters of [3Blue1Brown's Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra). This is the clearest visual introduction to vectors anywhere, and it builds the geometric picture the rest of this path relies on.
   - Watch chapter 1 (vectors), chapter 2 (linear combinations, span, and basis vectors) and the chapter on dot products and duality.
   - Pause and predict what happens before each animation plays.
1. Read chapter 3 of [Mathematics for Machine Learning](https://mml-book.github.io/), a free book by Deisenroth, Faisal and Ong written specifically for ML practitioners.
   - Read sections 3.1 (norms), 3.2 (inner products) and 3.4 (angles and orthogonality). Skim the proofs; focus on the definitions and examples.
1. Compute by hand, on paper, the dot product, the two norms and the cosine similarity of `[1, 2, 2]` and `[2, 0, 1]`. Then normalize both vectors and confirm their dot product now equals the cosine similarity you calculated.
1. Write a short Python snippet with NumPy that takes two of the embeddings you created in What Embeddings Are and prints their dot product, their norms, and their cosine similarity. Check whether your embedding provider already returns unit-length vectors.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [NumPy: the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html) covers arrays, the data structure you will use for vectors in every ML library.
- [scikit-learn's cosine_similarity function](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html) is a handy reference implementation to check your own code against.
