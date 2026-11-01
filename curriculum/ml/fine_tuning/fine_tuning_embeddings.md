### Introduction

In [Embeddings & Retrieval (RAG)](#/paths/core), you built retrieval pipelines that indexed documents and ranked them using cosine similarity. You used pre-trained off-the-shelf embedding models like `all-MiniLM-L6-v2` or commercial API endpoints.

General-purpose embedding models are trained on hundreds of millions of broad internet pairs (Wikipedia, Reddit, web forums). On everyday English questions, they perform well. But when deployed in proprietary enterprise environments—such as searching complex financial contracts, internal API documentation, biomedical literature, or custom ERP schemas—off-the-shelf models struggle:

- They fail to recognize domain-specific acronyms and jargon.
- They cluster documents by superficial keyword overlap rather than semantic intent.
- They cannot separate queries that look similar on the surface but require different technical documents.

The solution is **fine-tuning an embedding model**.

Fine-tuning an embedding model takes under 30 minutes on a single GPU, produces a lightweight model (under 100 MB), and often boosts retrieval recall (Hit@K) by 15% to 30% on domain-specific benchmarks. This lesson covers the architecture of bi-encoders, the mathematics of contrastive learning, how to mine hard negatives using BM25, and how to train and evaluate custom embedding models using the open-source [sentence-transformers](https://sbert.net/) library.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- When fine-tuning an embedding model outperforms prompt engineering or reranking.
- The bi-encoder architecture: encoding queries and documents into a shared geometric vector space.
- The mathematics of contrastive learning and `MultipleNegativesRankingLoss` (MNRL).
- Why random negatives are insufficient, and how to mine hard negatives using lexical search (BM25).
- Generating synthetic query-document training pairs with frontier language models.
- Training a custom embedding model using the `sentence-transformers` v3 training pipeline.
- Evaluating retrieval improvements with Information Retrieval metrics: Hit@K, MRR@K, and NDCG@K.

### Why fine-tune an embedding model for RAG?

In [Fine-Tune, Prompt, or RAG?](#/paths/core), you learned that RAG and fine-tuning are not mutually exclusive. In fact, one of the most effective ways to upgrade a RAG system is to fine-tune the *retrieval model*, not the generative language model.

Consider a technical enterprise documentation search:
- **User query:** "How do I configure MTLS termination for the ingress gateway?"
- **Generic embedding behavior:** The general model places high weight on common words like "configure" and "gateway", retrieving introductory tutorials for standard web servers.
- **Domain reality:** The correct answer is an internal architecture specification titled "Service Mesh Security Policy v2: Mutual TLS at Edge".

Fine-tuning adjusts the embedding model's weight matrices so that domain-specific queries and their true target passages are pulled closer together in vector space, while unrelated technical documents are pushed apart.

### Bi-encoders, similarity geometry, and contrastive learning

Modern semantic search relies on the **bi-encoder architecture** (Sentence-BERT, Reimers & Gurevych, 2019):

```text
Query:    "How to reset auth token" ---> [ BERT Encoder ] ---> q (vector: 384)
                                                                    |
                                                            Cosine Similarity: (q · d)
                                                                    |
Document: "Navigate to User Settings..." -> [ BERT Encoder ] ---> d (vector: 384)
```

The bi-encoder passes the query and the document through a transformer encoder separately. It then applies a mean-pooling operation over the token representations to produce fixed-size dense vectors `q` and `d`.

Because documents are encoded independently of queries, you can pre-compute and store millions of document vectors in a vector database (like pgvector). At query time, you only encode the single incoming query and compute dot products.

Training a bi-encoder uses **contrastive learning**:
- Pull matching pairs (query, positive document) closer together: maximize `cosine(q, d_positive)`.
- Push non-matching pairs (query, negative document) farther apart: minimize `cosine(q, d_negative)`.

### MultipleNegativesRankingLoss and in-batch negatives

The standard loss function for training embedding models is **MultipleNegativesRankingLoss (MNRL)**, an implementation of the InfoNCE (Information Noise-Contrastive Estimation) loss.

Preparing millions of labeled negative pairs is difficult. MNRL uses an elegant trick called **in-batch negatives**:
- Suppose your training batch contains `B` pairs: `(q_1, p_1), (q_2, p_2), ..., (q_B, p_B)`.
- For query `q_1`, passage `p_1` is the positive target.
- Passages `p_2, p_3, ..., p_B` (the positive targets for all other queries in the batch) are automatically treated as negative examples for `q_1`!

![Bi-encoder architecture and in-batch negatives contrastive learning matrix](assets/images/bi_encoder_contrastive.svg)

Mathematically, for query `i`, the loss is the cross-entropy over the row:

```text
Loss_i = -log( exp(q_i · p_i / scale) / sum_j(exp(q_i · p_j / scale)) )
```

Notice that this is identical to the softmax loss you studied in [Matrices and Probability](#/paths/ml)! A batch of size `B = 64` automatically provides 1 positive pair and 63 negative pairs for every single query with zero manual negative labeling required.

### The power of hard negatives: mining with BM25

In-batch negatives are effective, but they are often "easy negatives." If query 1 is about database connection pools and passage 2 is about front-end CSS buttons, the model easily tells them apart without learning subtle distinctions.

To make an embedding model truly robust, you must feed it **hard negatives**: passages that look extremely similar to the query textually, but do *not* contain the correct answer.

The most effective and widely used method for mining hard negatives is **BM25 lexical retrieval**:
1. Take your training query: `"How do I configure MTLS termination for the ingress gateway?"`
2. Run BM25 keyword search against your full document corpus.
3. Find passages that share words like "MTLS", "ingress", or "gateway", but are *not* the true answer passage.
4. Add these mined passages as explicit negatives in your dataset: `(query, positive_passage, hard_negative_passage)`.

When trained with hard negatives, the model learns that simply matching common keywords is not enough—it must learn the deeper semantic context that distinguishes the exact answer from related documentation.

### Training with sentence-transformers

The Python library `sentence-transformers` (v3+) provides a high-level API for fine-tuning embedding models with PyTorch.

```python
# train_embeddings.py: Fine-tuning an embedding model with MultipleNegativesRankingLoss
from datasets import Dataset
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
    losses,
)
from sentence_transformers.training_args import BatchSamplers

# 1. Load a compact, fast base embedding model
model_id = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_id)

# 2. Prepare training data: tuples of (query, positive_passage, [optional hard_negative])
train_data = {
    "anchor": [
        "How do I set session timeout in the auth service?",
        "What is the maximum payload size for webhook events?",
        "How do I rotate database encryption keys without downtime?",
    ],
    "positive": [
        "In auth-config.yaml, set session.idle_timeout_seconds to the desired duration.",
        "Webhook payloads are capped at 5 MB; larger payloads return HTTP 413.",
        "Execute 'vault rekey --rotate' followed by 'service restart --rolling'.",
    ],
    "negative": [
        "User sessions are logged to CloudWatch after authentication succeeds.",
        "Webhooks deliver JSON event notifications over HTTPS with retries.",
        "Database connections use SSL certificates verified against internal CA.",
    ]
}
train_dataset = Dataset.from_dict(train_data)

# 3. Define the contrastive loss function
loss = losses.MultipleNegativesRankingLoss(model)

# 4. Configure training arguments
args = SentenceTransformerTrainingArguments(
    output_dir="./mimir-custom-embeddings",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    fp16=True,
    batch_sampler=BatchSamplers.NO_DUPLICATES,  # Ensures no duplicate anchors in batch
    logging_steps=10,
)

# 5. Initialize the trainer and train
# trainer = SentenceTransformerTrainer(
#     model=model,
#     args=args,
#     train_dataset=train_dataset,
#     loss=loss,
# )
# trainer.train()
# model.save_pretrained("./mimir-custom-embeddings")
```

### Evaluating retrieval quality

You should never deploy a fine-tuned embedding model without proving that retrieval improved on a held-out test set. Use the standard Information Retrieval evaluation metrics from [Evaluating RAG and Regressions](#/paths/core):

1. **Hit@K (Success Rate at K):** Did the true positive document appear anywhere in the top `K` retrieved results?
   - In RAG, `Hit@5` measures whether the generative LLM was provided the right context in its top 5 chunks.
2. **Mean Reciprocal Rank (MRR@K):** Evaluates how high up the ranking list the true document appeared.
   - If the correct document is at rank 1, reciprocal rank is `1/1 = 1.0`.
   - If at rank 2: `1/2 = 0.5`.
   - If at rank 4: `1/4 = 0.25`.
   - MRR is the average across all evaluation queries. Higher MRR means users (and generative models) find answers faster without digging through irrelevant context.

In `sentence-transformers`, you evaluate these metrics automatically using `InformationRetrievalEvaluator`:

```python
from sentence_transformers.evaluation import InformationRetrievalEvaluator

# queries = {"q1": "How to set session timeout?"}
# corpus = {"doc1": "In auth-config.yaml...", "doc2": "Other text..."}
# relevant_docs = {"q1": {"doc1"}}

# evaluator = InformationRetrievalEvaluator(queries, corpus, relevant_docs)
# results = evaluator(model)
# print(f"MRR@10: {results['test_cosine_mrr@10']:.4f}")
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Sentence-Transformers Training Overview](https://sbert.net/docs/sentence_transformer/training_overview.html).
   - Read the guides on dataset formats, losses, and evaluators. Note why `MultipleNegativesRankingLoss` is recommended as the default loss for retrieval.
1. Read the foundational research paper [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks (Reimers & Gurevych, 2019)](https://arxiv.org/abs/1908.10084).
   - Read Sections 1 through 3. Pay special attention to Section 3.2 explaining how mean pooling turns token embeddings into a single fixed-length sentence vector.
1. Explore the [Massive Text Embedding Benchmark (MTEB) Leaderboard](https://huggingface.co/spaces/mteb/leaderboard).
   - Look at the top-ranked models under the "Retrieval" category. Note the trade-offs between model size (e.g. 33M parameters vs 7B parameters) and retrieval performance.
1. Write a Python script named `mine_hard_negatives.py`:
   - Create a corpus of 10 short technical passages (e.g. 5 about authentication, 5 about billing).
   - For a query like `"How do I configure OAuth token renewal?"`, use `CountVectorizer` or `TfidfVectorizer` from scikit-learn to rank all 10 passages.
   - Identify the positive passage (the ground truth document), and select the highest-scoring non-ground-truth document as the mined **hard negative**.
   - Print the query, the true positive passage, and the mined hard negative side by side.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [Why do off-the-shelf embedding models often struggle in specialized enterprise RAG applications?](#why-fine-tune-an-embedding-model-for-rag)
- [How does the bi-encoder architecture allow vector databases to index millions of documents efficiently?](#bi-encoders-similarity-geometry-and-contrastive-learning)
- [How does MultipleNegativesRankingLoss create negative examples without manual labeling?](#multiplenegativesrankingloss-and-in-batch-negatives)
- [What is a hard negative and why does mining hard negatives with BM25 improve retrieval accuracy?](#the-power-of-hard-negatives-mining-with-bm25)
- [What is the difference between Hit@K and Mean Reciprocal Rank (MRR)?](#evaluating-retrieval-quality)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Hugging Face Blog: How to Train Sentence Transformers with Synthetic Data](https://huggingface.co/blog/train-sentence-transformers) provides a complete guide to generating synthetic pairs with LLMs and fine-tuning an embedding model.
- [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval](https://github.com/beir-cellar/beir) is the standard benchmark suite used by researchers to evaluate retrieval models across 15+ domains.
- [Cohere: Rerank vs Embeddings](https://cohere.com/blog/rerank) explains the architectural trade-offs between first-stage bi-encoder embedding retrieval and second-stage cross-encoder reranking.