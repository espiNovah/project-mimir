<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Vector search is good at meaning and bad at exact terms. Ask for "error E-4021" and it may happily return passages about other errors. Classic keyword search has the opposite strengths. Production RAG systems usually combine the two, a setup called *hybrid search*, and then use a second, more careful model to reorder the best candidates, which is called *reranking*. This lesson shows how both pieces fit together and why they make a big difference.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How keyword search with BM25 works.
- Where vector search and keyword search each fail.
- How to combine results with reciprocal rank fusion.
- What a reranker is and how cross-encoders differ from embedding models.
- The two-stage retrieve-then-rerank pattern.
- How to measure whether retrieval improved.

### Key ideas

- **BM25 is the standard keyword ranking.** BM25 scores a document higher when it contains the query's words, especially rare words, and adjusts for document length. It is fast, needs no model, and excels at names, codes, acronyms and exact phrases.
- **The two searches fail differently.** Vector search finds "how do I get my money back" for a query about refunds; BM25 finds the exact SKU or error code. Combining them covers each other's blind spots.
- **Fuse ranked lists, not raw scores.** BM25 scores and cosine similarities are on different scales, so adding them is unreliable. *Reciprocal rank fusion* (RRF) gives each document a score of `1 / (k + rank)` from each list (with `k` often 60) and sums them. It is simple and works well.
- **Rerankers read query and passage together.** An embedding model encodes query and passage separately, which is fast but shallow. A *cross-encoder* reranker reads both at once and outputs a relevance score. It is more accurate but too slow to run on every chunk, so you use it only on the top candidates.
- **Retrieve wide, then narrow.** A typical pipeline retrieves the top 20 to 150 candidates with hybrid search, reranks them, and keeps the top 5 to 20 for the prompt. Anthropic's contextual retrieval experiments found that combining contextual embeddings, BM25 and reranking cut retrieval failures far more than any one technique alone.
- **Measure retrieval separately from answers.** Before judging generated answers, check whether the right chunk was retrieved at all. *Hit rate* (did the correct chunk appear in the top k?) and *MRR* (mean reciprocal rank: how high did it appear?) are easy to compute with a small set of questions where you know the right source. The Evals section builds on this.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Pinecone's introduction to hybrid search](https://www.pinecone.io/learn/hybrid-search-intro/).
   - Read the whole article for the intuition of combining sparse (keyword) and dense (vector) retrieval. The Pinecone-specific code is optional.
1. Read [Pinecone's guide to rerankers](https://www.pinecone.io/learn/series/rag/rerankers/).
   - Focus on the explanation of why two-stage retrieval works and how cross-encoders differ from bi-encoders.
1. Return to [Introducing Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval) and read the rest of the post.
   - Pay attention to the results charts showing how each technique reduces failed retrievals.
1. Read the [Sentence Transformers cross-encoder usage guide](https://sbert.net/docs/cross_encoder/usage/usage.html) to learn how to run a free reranker locally.
1. Practice: add BM25 to your ingestion project from the last lesson with the [bm25s library](https://github.com/xhluca/bm25s) (fast and maintained; Postgres full-text search, covered later, is the other common option). Implement RRF over the BM25 and vector results, then rerank the top 20 with a cross-encoder. Write 15 questions with known source chunks (include some with exact names or codes) and report hit rate at 5 for vector only, BM25 only, hybrid, and hybrid with reranking.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Okapi BM25 on Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25) shows the full formula, if you want to see exactly how term frequency and document length are weighed.
