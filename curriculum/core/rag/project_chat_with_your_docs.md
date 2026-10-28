### Introduction

In this project you will build a question-answering system over a set of documents you actually care about: your favorite open-source library's docs, your city's council meeting minutes, a game's rulebook, a set of course notes. It will ingest the documents, retrieve passages with hybrid search and reranking, answer with citations to the exact passages it used, and say "I don't know" when the documents do not cover the question.

This is the most common AI application in industry, and you will keep improving it: the RAG Eval Harness project measures it, and the Docs Chatbot UI project gives it a web interface. Build it as a reusable package, not a single script.

### Before you start

- Create a new GitHub repository called `mimir-chat-with-your-docs` as a `uv` project. Add `anthropic`, `sentence-transformers`, `"psycopg[binary]"` and `pgvector`, and run Postgres with the `pgvector/pgvector` image in Docker Compose, as in Chunking and Vector Databases. Add `bm25s` only if you choose it over Postgres full-text search for keyword retrieval.
- Choose a document set of at least 20 documents or 50 pages. It should be public or yours, so you can commit it or a script that downloads it. Avoid documents the model already knows by heart (such as famous novels), or you will not be able to tell retrieval from memory.
- Structure the code so the pieces can be used separately, for example: `ingest.py`, `retrieve.py`, `answer.py`, and a `cli.py` that ties them together. The next two projects import these.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Keep a question log from day one

Every time you try a question while building, write it down with whether the answer was right and which chunk should have been retrieved. By the end you will have the start of the test set you need for the RAG Eval Harness project.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Build an ingestion pipeline that loads your documents, cleans them, chunks them, embeds each chunk and stores it with metadata (source, title or heading, and position). Running it twice must not create duplicate chunks.
   - In the README, explain your chunking choice and the chunk size you used.
1. Implement hybrid retrieval: keyword search (Postgres full-text search, or BM25 with `bm25s`) and pgvector search, combined with reciprocal rank fusion (RRF), as in Hybrid Search and Reranking, followed by a cross-encoder reranker that keeps the top results.
1. Generate answers that cite their sources. Every factual claim must point to a specific retrieved passage, using either the provider's native citations feature or numbered source tags in your prompt. The output must show each cited passage's source and text.
1. Make the system say "I don't know" when the documents do not answer the question, instead of guessing from the model's general knowledge. Use a prompt instruction, a retrieval score threshold, or both.
1. Write code that verifies citations: every cited source must be one that was retrieved, and any quoted text must appear in that source. Flag answers that fail.
1. Provide a command-line interface: `uv run ask "your question"` prints the answer, its citations, and (with a `--debug` flag) the retrieved chunks with their scores.
1. Prove it works with a small check script on at least 15 questions you wrote, including at least 5 that the documents cannot answer. Report: how many answerable questions retrieved the right chunk in the top 5, how many answers were correct, and how many unanswerable questions got "I don't know."
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Add contextual retrieval: prepend a short model-generated context to each chunk before embedding and indexing, and report how retrieval hit rate changed.
- Support metadata filters, such as restricting a question to one document or section.
- Make ingestion incremental, so only new or changed documents are re-embedded.

</div>

### Submitting your work

A strong README shows a few real example questions with their cited answers (including one "I don't know"), a diagram or bullet list of the pipeline, your chunking and retrieval choices with the reasons, and the numbers from your 15-question check. Be honest about failures: one example where retrieval missed the right chunk, and why you think it did, is more convincing than a page of perfect answers.
