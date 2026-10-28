### Introduction

Every retrieval system you have built so far ranks documents with cosine similarity, computed for you by a library or a vector database. In this project you will write it yourself, twice: first in plain Python with nothing but loops and `math.sqrt`, then in NumPy. Then you will use your own function on real embeddings to find each sentence's nearest neighbors, and prove your implementation matches the library versions.

This is a small project, but it closes the loop between the math in Vectors and Similarity and the retrieval you did in Chat With Your Docs. Being able to say "I implemented this from scratch and checked it against scikit-learn" is also a good answer to a common interview question.

### Before you start

- Create a new repo named `mimir-similarity-by-hand` and set it up with `uv init`.
- Add dependencies: `uv add numpy scikit-learn sentence-transformers`. [sentence-transformers](https://sbert.net/) runs embedding models locally and for free. The small [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model (384 dimensions) downloads in seconds and runs fine on a laptop CPU. You may use a hosted embedding API instead if you prefer; keep the key in an environment variable as you learned in API Keys and Secrets.
- Write 20 short sentences in a file called `sentences.txt`, one per line. Make them deliberately clustered: for example, five about cooking, five about football, five about programming and five about the weather. Include at least two pairs that share words but differ in meaning ("The bank raised interest rates" and "We sat on the river bank") and at least one pair that means the same thing with no shared words.

Here is the shape of the plain-Python starting point:

```python
import math


def dot(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    return sum(x * y for x, y in zip(a, b))


def norm(a: list[float]) -> float:
    return math.sqrt(dot(a, a))
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. In `similarity/pure.py`, implement `dot`, `norm`, `normalize` and `cosine_similarity` using only the Python standard library. `cosine_similarity` must raise a clear error for vectors of different lengths and for a zero-length vector (a vector of all zeros has no direction).
1. In `similarity/fast.py`, implement the same four functions with NumPy, plus `cosine_matrix(X)` that returns the full 20 by 20 similarity matrix in a single matrix multiplication (no Python loops). Hint: normalize every row first, then multiply the matrix by its own transpose.
1. Write pytest tests that prove both versions are correct:
   - Hand-checked cases: `[1, 0]` vs `[0, 1]` gives 0, a vector with itself gives 1, a vector with its negative gives -1, and `[1, 2, 2]` vs `[2, 0, 1]` matches the value you computed by hand in Vectors and Similarity.
   - Agreement: on random vectors, `pure`, `fast`, `numpy` (using `np.dot` and `np.linalg.norm`) and `sklearn.metrics.pairwise.cosine_similarity` agree to within `1e-6`.
   - Scale invariance: multiplying a vector by 10 does not change its cosine similarity with anything.
1. Embed your 20 sentences and save the vectors to `embeddings.npy` so you don't recompute them every run.
1. Write `rank.py` that, for each sentence, prints its top 3 nearest neighbors (excluding itself) with their scores, using your own `cosine_matrix`. Also print the single most similar pair and the single least similar pair in the whole set.
1. Measure and report: how long your pure-Python version takes to compute all 400 pairs versus the NumPy version. Report the speedup.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned. The README must include:
   - A short explanation, in your own words, of what cosine similarity measures and why it ignores vector length.
   - The nearest-neighbor table for at least five sentences, and a comment on whether your clusters came out as expected. Did the "bank" sentences get confused? Did the no-shared-words paraphrase pair find each other?
   - Whether the embeddings your model returned were already unit length, and how you checked.

#### Extra credit

- Repeat the ranking with Euclidean distance on raw and on normalized vectors. Show that the ordering matches cosine similarity once vectors are normalized, and explain why.
- Embed the same 20 sentences with a second model (or a hosted API) and compare the top-3 lists. Report how many neighbors the two models agree on.
- Plot the 20 by 20 similarity matrix as a heatmap with matplotlib and include the image in your README.

</div>

### Submitting your work

A strong submission is one a stranger can clone and run with `uv run pytest` and `uv run rank.py`, and see green tests and a sensible ranking within a minute. The README shows real output, not a description of output. The best READMEs point out at least one surprising result (a pair you expected to be close that wasn't, or the reverse) and offer a plausible reason for it.
