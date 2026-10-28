### Introduction

Language models only know what was in their training data and what you put in the context window. To answer questions about your own documents, you need a way to find the right passages quickly, even when the question uses different words from the document. Embeddings make that possible. They turn text into vectors so that texts with similar meanings point in similar directions, which you can measure with the cosine similarity from the last lesson.

This lesson explains what embeddings are, how to use them for semantic search (the first building block of retrieval-augmented generation, or RAG), and the practical decisions that trip people up in real projects: which model to pick, how big the vectors should be, the special prefixes some models need, and what happens when you switch models.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an embedding is, and what semantic search and RAG are.
- How to create embeddings locally with Sentence Transformers, or through an API.
- How to choose an embedding model with the MTEB leaderboard and your own data.
- How vector dimensions translate into storage cost, and how Matryoshka models let you shrink them.
- Multilingual embeddings.
- The query and document prefixes some models need.
- Why switching models means re-embedding everything.

### What an embedding is

An **embedding model** reads a piece of text and outputs a vector, typically 384 to 3,072 numbers long. That vector is the text's **embedding**. The individual numbers don't mean anything you can read; there is no "number 17 is about cats." What matters is how vectors sit relative to each other. The model was trained on huge numbers of related text pairs (a question and its answer, a title and its article) so that related texts end up pointing in similar directions. "How do I reset my password?" and "I forgot my login" land close together, even though they share no words.

That property gives you **semantic search**: search by meaning instead of by matching words. The recipe has two phases.

1. **Indexing, done once.** Embed every passage in your collection and store the vectors.
1. **Querying, done per question.** Embed the question with the same model, compute its similarity to every stored vector, and return the top few passages.

**Retrieval-augmented generation (RAG)** adds one step: put those top passages into the prompt and ask a language model to answer using them. The model answers from your documents rather than from memory. That's the whole idea behind most "chat with your docs" products, and the rest of this section fills in the details: parsing documents, chunking them, storing vectors, improving search and grounding the answer.

Semantic search has a weakness worth knowing from day one. It's good at meaning and bad at exact strings. Ask about "error E-4021" and it may happily return passages about other error codes, because they all *mean* roughly the same thing. Hybrid Search and Reranking fixes that by adding keyword search.

### Making embeddings

**Sentence Transformers** is a free Python library that runs open embedding models on your own laptop, no API key needed. The first run downloads the model (about 130 MB for the one below).

```python
# uv add sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5")   # 384 dimensions, English

docs = [
    "To reset your password, open Settings and choose 'Forgot password'.",
    "Our office is closed on public holidays.",
    "Refunds are issued to the original payment method within 5 days.",
    "You can change the email address on your account under Profile.",
]

# This model was trained with an instruction in front of *queries* (not documents).
QUERY_PROMPT = "Represent this sentence for searching relevant passages: "

doc_vecs = model.encode(docs, normalize_embeddings=True)    # shape (4, 384)


def search(query: str, k: int = 2) -> list[tuple[float, str]]:
    q = model.encode(query, prompt=QUERY_PROMPT, normalize_embeddings=True)
    scores = doc_vecs @ q                                      # cosine, since all unit length
    best = scores.argsort()[::-1][:k]
    return [(round(float(scores[i]), 3), docs[i]) for i in best]


print(search("I forgot my login"))
print(search("how do I get my money back"))
```

Notice two things you learned in Vectors and Similarity: `normalize_embeddings=True` makes every vector unit length, so a plain dot product is the cosine similarity; and the search itself is one matrix multiplication. The first query finds the password passage and the second finds the refund passage, with no shared keywords.

You can also get embeddings from a hosted API. Several providers sell them, usually for a small fraction of what text generation costs. Some model providers, including Anthropic, don't offer their own embedding model and point to partner services instead. An API saves you from running a model, while a local model is free, private and works offline. For learning, local is the easy choice.

### Choosing an embedding model

There are hundreds of embedding models. Start with the **MTEB leaderboard** (Massive Text Embedding Benchmark), which scores models across many tasks and languages. When you read it:

- **Look at the retrieval columns**, not the overall average. Clustering and classification scores don't tell you much about search.
- **Look at model size and dimensions.** A model with 7 billion parameters may top the chart, but it needs a GPU and embeds slowly. A small model a few points lower often wins in practice.
- **Check the license and languages.** Some top models forbid commercial use or only handle English.
- **Treat it as a shortlist, not a verdict.** Benchmarks are public, and some models are tuned to them. What matters is retrieval quality on *your* documents and *your* questions.

So the workflow is: pick two or three candidates from the leaderboard, embed your documents with each, write 20 questions where you know which passage is correct, and measure how often each model puts it in the top 5. That's the same evaluation habit from Measuring Quality, and you'll formalize the retrieval metrics in Hybrid Search and Reranking.

### Dimensions and storage cost

Every dimension is usually stored as a 32-bit float, which is 4 bytes. So the raw storage for your vectors is:

```text
chunks × dimensions × 4 bytes
1,000,000 chunks × 1,024 dims × 4 bytes ≈ 4.1 GB
1,000,000 chunks ×   384 dims × 4 bytes ≈ 1.5 GB
```

Search indexes (covered in Chunking and Vector Databases) add more on top, and fast search wants the index in memory. Bigger vectors also make every similarity calculation slower. More dimensions can capture finer distinctions, but past a point the gain is small. For a few thousand chunks none of this matters, but it's worth doing the arithmetic before you embed a large collection with a 3,072-dimension model. Storing vectors as 16-bit floats (pgvector calls this `halfvec`) halves the size with almost no loss in quality.

### Matryoshka embeddings

Some newer models are trained with **Matryoshka Representation Learning**, named after Russian nesting dolls. The model packs the most important information into the first dimensions, so you can cut a vector down to its first 256 or 128 numbers, re-normalize it, and still get most of the retrieval quality. Model cards say when a model supports this; `nomic-ai/nomic-embed-text-v1.5` and `mixedbread-ai/mxbai-embed-large-v1` are two examples.

Truncation is just slicing plus normalizing:

```python
import numpy as np


def truncate(vecs: np.ndarray, dims: int) -> np.ndarray:
    """Keep the first `dims` numbers of each vector, then re-normalize."""
    cut = vecs[..., :dims]
    return cut / np.linalg.norm(cut, axis=-1, keepdims=True)
```

Sentence Transformers can do it for you with `SentenceTransformer(name, truncate_dim=256)`. Truncating a model that *wasn't* trained this way works badly, so check the model card. A common trick is to search quickly with short vectors and then re-score the top results with the full ones.

### Multilingual embeddings

If your documents or users span languages, pick a **multilingual** model. These map text in different languages into one shared space, so a question in Spanish can retrieve a passage written in English. `intfloat/multilingual-e5-small` is a small free option. MTEB has per-language leaderboards; check your actual languages there, because quality varies a lot, especially for languages with less training data. An English-only model given French text won't crash. It will quietly return worse results, which is the dangerous kind of failure.

### Query and document prefixes

Many retrieval models are trained *asymmetrically*: queries are short questions and documents are long passages, so the model is taught to treat them differently using a text prefix. Examples from real model cards:

- `BAAI/bge-small-en-v1.5`: put `Represent this sentence for searching relevant passages: ` in front of queries only.
- `intfloat/multilingual-e5-small`: `query: ` in front of queries and `passage: ` in front of documents.
- `nomic-ai/nomic-embed-text-v1.5`: `search_query: ` and `search_document: `.

Forget the prefix and nothing errors. Your retrieval quality just drops, sometimes by several points. Hosted APIs often expose the same idea as an `input_type` parameter ("query" or "document"). **Always read the model card's usage section** before you embed anything, and store the exact model name and prefixes in your config so indexing and querying can't drift apart.

### Switching models means re-embedding

Vectors from different models live in different spaces. A 384-dimension vector from one model and a 384-dimension vector from another have the same shape, but comparing them is meaningless: dimension 17 means something different in each. The same goes for changing the prefix, the truncation length or even a model *version*.

So when you change any of these, you must **re-embed every document**. Plan for it from the start:

- Store the model name, version, dimensions and prefixes alongside your vectors (a column in the table, or a config value you check at startup).
- Keep the original text of every chunk, so re-embedding is a batch job and not a re-parse.
- To switch without downtime, embed into a new column or table, test the new model on your eval questions, then flip queries over and delete the old vectors.

<div class="lesson-note lesson-note--warning" markdown="1">

#### The silent mismatch

The worst embedding bug raises no error: queries embedded with one model or prefix, documents with another. Results look plausible but are mostly noise. If retrieval quality suddenly collapses after a change, check this first.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Embeddings: what they are and why they matter](https://simonwillison.net/2023/Oct/23/embeddings/) by Simon Willison.
   - Read the whole post. It is the clearest plain-language introduction available, with practical examples of related-content search.
1. Work through the [Sentence Transformers quickstart](https://sbert.net/docs/quickstart.html).
   - Install it with `uv add sentence-transformers`, run the embedding and similarity examples, and try a few sentences of your own.
1. Read the [Claude docs page on embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings) to see how a model provider thinks about choosing an embedding model.
   - Focus on the criteria for picking a model and the idea of separate query and document input types. You do not need to sign up for any service.
1. Read [Hugging Face's introduction to Matryoshka embedding models](https://huggingface.co/blog/matryoshka) for the training idea and the quality-versus-size charts. Skip the training code.
1. Practice: embed 30 short sentences on three or four different topics.
   - Write `search(query, k=3)` that returns the most similar sentences with their scores. Try queries that share no words with the right answer, and one that depends on an exact name or number. Note where semantic search does well and where it fails.
   - Compare two models from the [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) on ten queries where you know the right answer. Count how often each puts it first.
   - Rerun with the query prefix removed, and record whether results change.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the two phases of semantic search, and what does RAG add?](#what-an-embedding-is)
- [What should you look at on the MTEB leaderboard, and why isn't it the final word?](#choosing-an-embedding-model)
- [Roughly how much storage do one million 1,024-dimension float vectors need?](#dimensions-and-storage-cost)
- [What makes it safe to truncate a Matryoshka embedding, and what must you do after slicing?](#matryoshka-embeddings)
- [What happens if you forget a model's query prefix?](#query-and-document-prefixes)
- [Why must you re-embed every document when you change embedding models?](#switching-models-means-re-embedding)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Sentence Transformers documentation](https://sbert.net/) lists pretrained models and explains training your own.
- [Hugging Face's embedding quantization post](https://huggingface.co/blog/embedding-quantization) shows how to shrink vectors further with int8 and binary formats.
- [The Illustrated Word2vec](https://jalammar.github.io/illustrated-word2vec/) by Jay Alammar explains, with pictures, how the earliest word embeddings were trained.
