### Introduction

Vector search is good at meaning and bad at exact terms. Ask for "error E-4021" and it may happily return passages about other errors. Classic keyword search has the opposite strengths. Production RAG systems usually combine the two, a setup called *hybrid search*, and then use a second, more careful model to reorder the best candidates, which is called *reranking*. This lesson shows how both pieces fit together and why they make a big difference.

You'll build on the `chunks` table from Chunking and Vector Databases. By the end, the same Postgres database will answer a question with keyword search and vector search at once, fuse the two result lists, and hand the best candidates to a free local reranker.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Where vector search and keyword search each fail.
- How keyword search with BM25 works.
- How to run keyword search inside Postgres with full-text search.
- How to combine results with reciprocal rank fusion.
- What a reranker is and how cross-encoders differ from embedding models.
- The two-stage retrieve-then-rerank pattern.
- How to measure whether retrieval improved.

### Where each search fails

The two kinds of search fail in opposite ways, which is exactly why they work well together.

**Vector search** (also called *dense* retrieval, because every chunk gets a full vector of numbers) understands paraphrase. A user who asks "how do I get my money back" finds the chunk titled "Refund policy," even though they share no words. But an embedding captures the general meaning of a text, not its exact strings. Product codes, error numbers, people's names, acronyms and version numbers all blur together: to an embedding model, "E-4021" and "E-4012" mean nearly the same thing.

**Keyword search** (also called *sparse* retrieval, because each document is described by the few words it contains out of a huge vocabulary) is the opposite. It finds the chunk with "E-4021" in it instantly and precisely, but it has no idea that "money back" and "refund" are related. If the user's words aren't in the chunk, keyword search returns nothing.

Real users ask both kinds of question, often in the same session. Hybrid search runs both and merges the results, so each covers the other's blind spots.

### How BM25 works

**BM25** ("Best Match 25") is the standard way to rank documents for a keyword query, and it has been for decades. You don't need its formula, but you should know the three ideas inside it:

1. **Term frequency.** A chunk that mentions "refund" several times is probably more about refunds than one that mentions it once. But the benefit *saturates*: the tenth mention adds much less than the second.
1. **Rarity.** Matching a rare word counts for more than matching a common one. Almost every chunk contains "the" or "account," so they tell you little. Very few contain "E-4021," so a match on it is strong evidence. This is called *inverse document frequency* (IDF).
1. **Length.** A long chunk contains more words just by being long, so BM25 scales scores down for long chunks and up for short ones.

BM25 is fast, needs no model and no GPU, and excels at names, codes, acronyms and exact phrases. In Python, the **bm25s** library implements it efficiently. Inside Postgres, you can use the built-in full-text search instead, which is what the walkthrough below does.

### Full-text search in Postgres

Postgres has had keyword search built in for years. It works with two types:

- A **`tsvector`** is a document turned into a sorted list of *lexemes*: normalized word forms. `to_tsvector('english', 'Refunds are issued in 5 days')` gives `'5':5 'day':6 'issu':3 'refund':1`. Common *stop words* such as "are" and "in" are dropped, and the rest are *stemmed* (cut down to a root), so "refunds," "refunded" and "refund" all match each other. The numbers record word positions.
- A **`tsquery`** is a search made of lexemes joined by `&` (and), `|` (or) and `!` (not). The `@@` operator tests whether a `tsvector` matches a `tsquery`.

`websearch_to_tsquery` turns raw user text into a `tsquery` safely; it never raises a syntax error. To rank the matches, `ts_rank_cd` scores how often and how close together the query words appear. A **GIN index** (Generalized Inverted Index, a map from each lexeme to the rows that contain it) makes matching fast.

Two caveats are worth knowing. First, `websearch_to_tsquery` joins plain words with `&`, so *every* word must appear. That suits a search box, but it's too strict for full questions, so the walkthrough joins words with `or` instead. Second, Postgres's built-in ranking is **not BM25**. It doesn't weigh rare words more than common ones, so its ranking is cruder. For many document collections it's good enough, and keeping everything in one database is a real advantage. If your keyword results look poor, `bm25s` is the next step: it builds a proper BM25 index in memory from the text in your table.

### Reciprocal rank fusion

You now have two ranked lists. How do you merge them? The tempting answer is to add the scores, but that's unreliable: a `ts_rank_cd` score and a cosine similarity are on completely different scales, and their spread changes from query to query.

**Reciprocal rank fusion (RRF)** ignores the scores and uses only the *positions*. Each chunk gets `1 / (k + rank)` from every list it appears in, and those values are added up. `k` is a constant, usually 60, that stops the top position from dominating. Here's a worked example with chunk IDs:

```text
vector search:  [7, 3, 9]      keyword search:  [3, 12, 7]

chunk 3:  1/(60+2) + 1/(60+1) = 0.0161 + 0.0164 = 0.0325   ← first
chunk 7:  1/(60+1) + 1/(60+3) = 0.0164 + 0.0159 = 0.0323
chunk 12:            1/(60+2) = 0.0161
chunk 9:  1/(60+3)            = 0.0159
```

Chunks that both searches like rise to the top, and a chunk only one search found still gets a fair place. RRF needs no tuning and no training data, which is why it's the usual default.

### A hybrid search walkthrough

This script adds full-text search to the `chunks` table from the last lesson, runs both searches, and fuses them with RRF. It reuses `DB_URL` and `MODEL_NAME` from `ingest.py`.

```python
# hybrid.py — run with: uv run python hybrid.py
import re

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from ingest import DB_URL, MODEL_NAME

QUERY_PROMPT = "Represent this sentence for searching relevant passages: "
model = SentenceTransformer(MODEL_NAME)

# A generated column: Postgres computes the tsvector itself and keeps it up to date.
SETUP = """
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('english', heading || ' ' || content)) STORED;
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING gin (tsv);
"""


def keyword_search(conn, question: str, n: int = 20) -> list[int]:
    terms = " or ".join(re.findall(r"\w[\w-]*", question))   # match ANY word, not all
    rows = conn.execute(
        """SELECT id FROM chunks, websearch_to_tsquery('english', %s) AS query
           WHERE tsv @@ query ORDER BY ts_rank_cd(tsv, query) DESC LIMIT %s""",
        (terms, n),
    ).fetchall()
    return [row[0] for row in rows]


def vector_search(conn, question: str, n: int = 20) -> list[int]:
    q = model.encode(question, prompt=QUERY_PROMPT, normalize_embeddings=True)
    rows = conn.execute(
        "SELECT id FROM chunks ORDER BY embedding <=> %s LIMIT %s", (q, n)
    ).fetchall()
    return [row[0] for row in rows]


def rrf(rankings: list[list[int]], k: int = 60) -> list[tuple[int, float]]:
    """Reciprocal rank fusion: sum 1/(k + rank) over every list a chunk appears in."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def hybrid_search(conn, question: str, n: int = 20) -> list[tuple[int, float]]:
    return rrf([vector_search(conn, question, n), keyword_search(conn, question, n)])


if __name__ == "__main__":
    with psycopg.connect(DB_URL) as conn:
        register_vector(conn)
        conn.execute(SETUP)
        for chunk_id, score in hybrid_search(conn, "What does error E-4021 mean?")[:5]:
            source, heading = conn.execute(
                "SELECT source, heading FROM chunks WHERE id = %s", (chunk_id,)
            ).fetchone()
            print(f"{score:.4f}  {source} > {heading}")
```

Walk through the important lines:

- **The generated column** means you never compute `tsv` in Python. Postgres fills it in for existing rows when the column is added, and for every new row your ingestion script inserts. The heading is included so a query for "refunds" matches chunks under a "Refunds" heading.
- **`re.findall(r"\w[\w-]*", question)`** pulls out the words, keeping hyphenated codes like `E-4021` together and dropping quotes and leading dashes that `websearch_to_tsquery` would treat as operators. Joining them with `or` makes a chunk match if it contains any of the words. Stop words are removed and `ts_rank_cd` rewards chunks that contain more of the words, close together.
- **Both searches return IDs only, in rank order.** That's all RRF needs. Each search fetches 20 candidates, many more than you'll keep, so a chunk ranked 15th by one search can still win if the other likes it too.
- **`rrf` is ten lines of plain Python** with no knowledge of where the lists came from. You could add a third list (say, a second embedding model) without changing it.

You can also write RRF as a single SQL query with a `FULL OUTER JOIN`; the [pgvector-python RRF example](https://github.com/pgvector/pgvector-python/blob/master/examples/hybrid_search/rrf.py) shows how. Doing it in Python is easier to read and test, and the difference in speed is tiny for 40 rows.

### Rerankers

Hybrid search gets the right chunk into the top 20 far more often. Getting it into the top 3 is the reranker's job.

An embedding model is a **bi-encoder**: it encodes the query and each chunk *separately*, and you compare the two vectors. That's what makes vector search fast, because chunk vectors are computed once at ingestion. But the model never sees the query and the chunk together, so it can't notice that a chunk mentions refunds only to say "refunds are covered elsewhere."

A **cross-encoder** reads the query and one chunk *together*, as one input, and outputs a single relevance score. Seeing both at once lets it weigh every word of the chunk against every word of the query, so it's much more accurate. The cost: nothing can be computed ahead of time. Scoring 10,000 chunks means 10,000 model runs per question. So you only use it on a short list of candidates. Sentence Transformers runs free cross-encoders locally:

```python
# rerank.py
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")   # small and free, about 90 MB


def rerank(question: str, chunks: list[str], top: int = 5) -> list[tuple[float, str]]:
    ranked = reranker.rank(question, chunks, top_k=top)          # [{"corpus_id": 2, "score": 7.1}, ...]
    return [(r["score"], chunks[r["corpus_id"]]) for r in ranked]
```

Fetch the `content` of the 20 fused candidates, pass them to `rerank`, and keep the top 5. Hosted APIs also sell rerankers, and a language model can act as one, but a small local cross-encoder is a strong, free starting point.

### Retrieve wide, then narrow

Put it together and you get the standard two-stage pipeline:

1. **Retrieve wide.** Hybrid search pulls the top 20 to 150 candidates. It's cheap, so be generous; the goal here is *recall*, making sure the right chunk is somewhere in the pile.
1. **Narrow.** The reranker scores every candidate, and you keep the top 5 to 20 for the prompt. The goal now is *precision*, putting the best chunks first and leaving noise out of the prompt.

Each stage is tuned with its own number: how many to fetch, how many to keep. Anthropic's contextual retrieval experiments found that combining contextual embeddings, BM25 and reranking cut retrieval failures far more than any one technique alone. The gains stack.

### Measuring retrieval

Before you judge generated answers, check whether the right chunk was retrieved at all. If it wasn't, no prompt can save the answer. You need a small set of questions where you know which chunk holds the answer, and two numbers:

- **Hit rate at k**: the share of questions whose correct chunk appears in the top k results.
- **MRR** (mean reciprocal rank): for each question, score `1 / rank` of the correct chunk (1 for first place, 0.5 for second, 0 if it's missing), then average. It rewards putting the right chunk *high*, not just somewhere.

```python
def retrieval_scores(results: list[list[int]], gold: list[int], k: int = 5) -> tuple[float, float]:
    """results[i] is the ranked chunk IDs for question i; gold[i] is its correct chunk ID."""
    hits, reciprocal_ranks = 0, 0.0
    for ranked, right in zip(results, gold):
        top = ranked[:k]
        if right in top:
            hits += 1
            reciprocal_ranks += 1 / (top.index(right) + 1)
    return hits / len(gold), reciprocal_ranks / len(gold)
```

Run it for each setup (vector only, keyword only, hybrid, hybrid plus reranking) on the same questions, and you'll see which change actually helped. With only 15 or 20 questions, small differences are noise; Eval Statistics showed how to put a confidence interval on numbers like these. The Evals in Practice section builds on this with full RAG evaluation.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Pinecone's introduction to hybrid search](https://www.pinecone.io/learn/hybrid-search-intro/).
   - Read the whole article for the intuition of combining sparse (keyword) and dense (vector) retrieval. The Pinecone-specific code is optional.
1. Read [Pinecone's guide to rerankers](https://www.pinecone.io/learn/series/rag/rerankers/).
   - Focus on the explanation of why two-stage retrieval works and how cross-encoders differ from bi-encoders.
1. Return to [Introducing Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval) and read the rest of the post.
   - Pay attention to the results charts showing how each technique reduces failed retrievals.
1. Read the [Sentence Transformers cross-encoder usage guide](https://sbert.net/docs/cross_encoder/usage/usage.html) to learn how to run a free reranker locally.
1. Read the Postgres manual's page on [controlling text search](https://www.postgresql.org/docs/current/textsearch-controls.html).
   - Read "Parsing Queries" and "Ranking Search Results." Try `to_tsvector` and `websearch_to_tsquery` on a few of your own sentences in `psql`.
1. Practice: add keyword search to your ingestion project from the last lesson, using the Postgres full-text search from the walkthrough, or the [bm25s library](https://github.com/xhluca/bm25s) (fast and maintained) if you want true BM25 ranking. Implement RRF over the keyword and vector results, then rerank the top 20 with a cross-encoder.
   - Write a pytest test for your `rrf` function using the worked example in this lesson.
   - Write 15 questions with known source chunks (include some with exact names or codes) and report hit rate at 5 and MRR for vector only, keyword only, hybrid, and hybrid with reranking.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What kinds of query does vector search handle badly, and what does keyword search handle badly?](#where-each-search-fails)
- [What three ideas does BM25 combine to score a document?](#how-bm25-works)
- [What are a tsvector and a tsquery, and how does Postgres ranking differ from BM25?](#full-text-search-in-postgres)
- [Why does RRF use ranks instead of adding the raw scores together?](#reciprocal-rank-fusion)
- [Why does the walkthrough join the question's words with "or"?](#a-hybrid-search-walkthrough)
- [How does a cross-encoder differ from an embedding model, and why is it used only on a few candidates?](#rerankers)
- [What do hit rate and MRR measure, and why check retrieval before judging answers?](#measuring-retrieval)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Okapi BM25 on Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25) shows the full formula, if you want to see exactly how term frequency and document length are weighed.
- [The original reciprocal rank fusion paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) by Cormack, Clarke and Büttcher is only two pages. It introduced RRF, showed it beating more complicated fusion methods, and explains that `k = 60` was picked in a small pilot experiment.
- [The Postgres manual's page on text search tables and indexes](https://www.postgresql.org/docs/current/textsearch-tables.html) covers the generated-column pattern and GIN indexes in more detail.
