### Introduction

In the next lesson you will turn sentences into long lists of numbers called *embeddings*, and find related sentences by comparing those lists. Before you do, it pays to understand what "comparing lists of numbers" actually means. A list of numbers is a *vector*, and a handful of simple operations on vectors (adding, scaling, the dot product, the length) explain why retrieval works, why embeddings are usually normalized, and why "close together" can mean "similar in meaning."

You will not need calculus or proofs. You already know NumPy from the Working with Data section, and that is all the tooling you need. The goal is intuition: enough to reason about embeddings, to debug a retrieval system that returns strange results, and to answer "why cosine and not Euclidean distance?" in an interview.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a vector is, both as a list of numbers and as an arrow in space.
- Vector addition and scaling, and what they mean geometrically.
- The dot product and what it measures.
- Vector length (the norm) and normalization to unit length.
- Cosine similarity, and how it relates to the dot product and Euclidean distance.
- How to find the most similar vectors in a matrix with one line of NumPy.
- Why high-dimensional spaces behave the way they do.

### What a vector is

A **vector** is an ordered list of numbers. `[3, 4]` is a vector with two entries, or two *dimensions*. You can picture it in two ways, and both are useful.

- **As a point.** `[3, 4]` is the spot three steps right and four steps up from the origin `[0, 0]`.
- **As an arrow.** It is also the arrow from the origin to that point. An arrow has a *direction* (which way it points) and a *length* (how far it goes).

An embedding from a modern model is the same thing with 384, 1,024 or 3,072 entries instead of two. You can't draw a 1,024-dimensional arrow, but every operation in this lesson works in exactly the same way whether there are two numbers or two thousand. When you're confused about something in high dimensions, draw the 2D version on paper first. It almost always gives you the right intuition.

In NumPy a vector is a one-dimensional array, and a stack of vectors (for example, one embedding per document) is a two-dimensional array, or *matrix*, with one row per vector:

```python
import numpy as np

a = np.array([3.0, 4.0])
docs = np.array([[1.0, 0.0], [0.0, 2.0], [3.0, 3.0]])  # 3 vectors, 2 dimensions each
print(docs.shape)  # (3, 2)
```

### Adding and scaling

**Adding** two vectors adds matching entries: `[1, 2] + [3, 1] = [4, 3]`. As arrows, it means "walk along the first, then along the second." **Scaling** multiplies every entry by one number: `2 × [1, 2] = [2, 4]`. The arrow gets twice as long but keeps pointing the same way. Scaling by a negative number flips it around.

Why does this matter for AI? Because of a famous result from early word embeddings: the vector for "king" minus "man" plus "woman" lands close to "queen." Directions in embedding space can carry meaning, such as "male to female" or "singular to plural." Modern sentence embeddings are messier than that tidy example, but the core idea holds: meaning is stored in *direction*, and scaling a vector changes its length without changing what it points at.

### The dot product

The **dot product** of two vectors multiplies matching entries and adds the results. For `a = [1, 2]` and `b = [3, 4]`:

```text
a · b = 1×3 + 2×4 = 11
```

The number tells you how much two arrows point the same way:

- **Large and positive** when they point in roughly the same direction.
- **Zero** when they are perpendicular (at right angles). In embedding terms: unrelated.
- **Negative** when they point in roughly opposite directions.

There's a catch. The dot product also grows with length. `[10, 20] · [3, 4]` is 110, ten times larger than before, even though the direction is identical. So a raw dot product mixes up "points the same way" with "is a long arrow." The next two sections fix that.

### Length and normalization

The **norm** of a vector is its length, written `‖a‖`. It's the square root of the vector dotted with itself, which is just Pythagoras' theorem:

```text
‖[3, 4]‖ = √(3×3 + 4×4) = √25 = 5
```

Divide a vector by its norm and you get a **unit vector**: same direction, length exactly 1. This step is called **normalization**. `[3, 4] / 5 = [0.6, 0.8]`, and you can check that `0.6² + 0.8² = 1`. Normalization throws away length and keeps only direction, which is exactly what you want when direction carries the meaning.

### Cosine similarity

**Cosine similarity** is the dot product of two vectors after both have been normalized:

```text
cos(a, b) = (a · b) / (‖a‖ × ‖b‖)
```

It's called "cosine" because the result equals the cosine of the angle between the two arrows. It always lands between -1 and 1: 1 means the same direction, 0 means perpendicular, -1 means opposite. Because it ignores length, a long document and a short tweet about the same topic can still score as very similar.

Three facts follow, and they explain a lot of what you'll see in real systems:

1. **If your vectors are already unit length, cosine similarity and the dot product are the same number.** The denominator is `1 × 1`. That's why many embedding models return normalized vectors and many vector databases simply use the dot product: it's the cheapest calculation.
1. **For unit vectors, Euclidean distance gives the same ranking too.** Euclidean distance is the straight-line distance between the two points. For unit vectors it works out to `√(2 − 2 × cos)`, so the closest vector by distance is always the most similar by cosine. When a vector database offers "cosine," "inner product" and "L2 distance," on normalized embeddings they all return the same top results in the same order.
1. **Scores are relative, not absolute.** Embedding models are trained so that texts used in similar ways point in similar directions, but each model spreads its vectors differently. A cosine of 0.6 might mean "very close" for one model and "barely related" for another. Compare rankings within one model, and never reuse a threshold you tuned for a different model.

Here is all of it in NumPy. Run it with `uv run python vectors.py` after `uv add numpy`:

```python
import numpy as np

a = np.array([1.0, 2.0, 2.0])
b = np.array([2.0, 0.0, 1.0])

dot = a @ b                                # @ is the dot product operator
norm_a = np.linalg.norm(a)                 # √(1 + 4 + 4) = 3.0
norm_b = np.linalg.norm(b)                 # √(4 + 0 + 1) ≈ 2.236
cosine = dot / (norm_a * norm_b)
print(f"dot={dot:.3f} norms=({norm_a:.3f}, {norm_b:.3f}) cosine={cosine:.3f}")

# Normalize, and the plain dot product *is* the cosine similarity.
unit_a, unit_b = a / norm_a, b / norm_b
print(f"dot of unit vectors={unit_a @ unit_b:.3f}")

# Euclidean distance between unit vectors follows from the cosine.
print(f"distance={np.linalg.norm(unit_a - unit_b):.3f} vs formula={np.sqrt(2 - 2 * cosine):.3f}")
```

It prints a cosine of about 0.596, the same number for the dot product of the unit vectors, and two matching distances. Work it out on paper too (the Assignment asks you to); seeing the same number appear by hand and in code is what makes it stick.

### Searching a whole matrix at once

Retrieval means comparing one query vector against every document vector and keeping the best few. With a loop that would be slow in Python. With NumPy, it's a single matrix multiplication: if every row of `docs` is a unit vector and `q` is a unit vector, then `docs @ q` returns one cosine similarity per document.

```python
import numpy as np


def normalize(m: np.ndarray) -> np.ndarray:
    """Scale each row (or a single vector) to length 1."""
    return m / np.linalg.norm(m, axis=-1, keepdims=True)


def top_k(query: np.ndarray, docs: np.ndarray, k: int = 3) -> list[tuple[int, float]]:
    scores = normalize(docs) @ normalize(query)   # one cosine score per row
    best = np.argsort(-scores)[:k]                # indices of the k highest scores
    return [(int(i), float(scores[i])) for i in best]


rng = np.random.default_rng(0)
docs = rng.normal(size=(10_000, 384))             # pretend: 10,000 embeddings
query = docs[42] + 0.1 * rng.normal(size=384)     # a slightly noisy copy of doc 42
print(top_k(query, docs))                         # doc 42 comes first, score near 1.0
```

This "brute-force" search compares the query against every row, and for up to a few hundred thousand vectors it's genuinely fast. That's worth remembering: you don't need a special database to start. In Chunking and Vector Databases you'll see how indexes such as HNSW speed this up for millions of vectors by skipping most of the comparisons.

### High dimensions are strange

Your 2D intuition is a good guide, with one big exception. In high-dimensional spaces, two *random* vectors are almost always nearly perpendicular. Try it:

```python
import numpy as np

rng = np.random.default_rng(1)
for dims in (2, 30, 1024):
    x = rng.normal(size=(1000, dims))
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    sims = (x @ x.T)[np.triu_indices(1000, k=1)]   # every distinct pair
    print(f"{dims:>5} dims: average |cosine| between random vectors = {np.abs(sims).mean():.3f}")
```

In 2 dimensions random pairs are all over the place (average around 0.64). In 1,024 dimensions the average falls to about 0.025: almost everything is nearly perpendicular to almost everything else. That's good news for embeddings. There is a huge amount of "room," so a model can give thousands of distinct concepts their own directions without them crowding each other. It also explains why real embedding similarities often sit in a narrow band (for example, 0.2 to 0.8) rather than spreading across the whole -1 to 1 range: meaningful similarity shows up as a small but consistent lean in the same direction.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Debugging retrieval with this lesson

When a retrieval system misbehaves, check three things first: are all vectors the same length (normalized, or all not)? Did the query and documents come from the same model? Are you sorting scores from high to low for similarity, but low to high for distance? A surprising share of "the embeddings are bad" bugs are one of these.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch the first chapters of [3Blue1Brown's Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra). This is the clearest visual introduction to vectors anywhere, and it builds the geometric picture the rest of the RAG section relies on.
   - Watch chapter 1 (vectors), chapter 2 (linear combinations, span, and basis vectors) and the chapter on dot products and duality.
   - Pause and predict what happens before each animation plays.
1. Read chapter 3 of [Mathematics for Machine Learning](https://mml-book.github.io/), a free book by Deisenroth, Faisal and Ong written specifically for ML practitioners.
   - Read sections 3.1 (norms), 3.2 (inner products) and 3.4 (angles and orthogonality). Skim the proofs; focus on the definitions and examples. If the notation feels heavy, the sections of this lesson cover everything you need, so treat the book as a second explanation rather than a hurdle.
1. Compute by hand, on paper, the dot product, the two norms and the cosine similarity of `[1, 2, 2]` and `[2, 0, 1]`. Then normalize both vectors and confirm their dot product now equals the cosine similarity you calculated. Check your answers against the first code example.
1. Practice in NumPy. If you want to warm up first, revisit the [data exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/data), which drills the array operations used here.
   - Write `cosine(a, b)` and `top_k(query, docs, k)` yourself without looking at this lesson, then check them against the examples above.
   - Take ten random vectors, scale some of them by 5, and show that their cosine rankings against a query don't change while their raw dot product rankings do.
   - Rerun the high-dimensions experiment for 2, 10, 100, 1,000 and 10,000 dimensions and plot the average with matplotlib.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the two ways to picture a vector, and which property carries the meaning of an embedding?](#what-a-vector-is)
- [Why can a raw dot product be misleading when comparing documents?](#the-dot-product)
- [What does normalizing a vector keep, and what does it throw away?](#length-and-normalization)
- [Why do cosine similarity, the dot product and Euclidean distance give the same ranking for unit vectors?](#cosine-similarity)
- [Why shouldn't you reuse a similarity threshold tuned on a different embedding model?](#cosine-similarity)
- [How do you score one query against thousands of document vectors in a single NumPy operation?](#searching-a-whole-matrix-at-once)
- [What happens to the similarity of random vectors as the number of dimensions grows?](#high-dimensions-are-strange)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [NumPy: the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html) covers arrays, the data structure you will use for vectors in every ML library.
- [scikit-learn's cosine_similarity function](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html) is a handy reference implementation to check your own code against.
- If you later take the ML Foundations elective, its Math You Need lesson and Similarity by Hand project go deeper into the linear algebra behind this lesson.
