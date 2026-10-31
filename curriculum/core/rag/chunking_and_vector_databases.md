### Introduction

Real documents are long: manuals, policies, books, wikis. You cannot embed a 200-page PDF as one vector and expect to find the right paragraph. Instead you split documents into smaller pieces called *chunks*, embed each one, and store them in a database built for fast similarity search. This lesson covers both halves of that ingestion pipeline: how to chunk well, and where to put the vectors.

You'll finish with a working ingestion script that chunks a folder of Markdown files, embeds every chunk with the free local model from What Embeddings Are, and stores the results in PostgreSQL with the **pgvector** extension. Postgres is already the default database in this curriculum, and you ran it with Docker Compose in the Backend section, so there's no new service to learn.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The steps of an ingestion pipeline: load, clean, chunk, embed, store.
- Why chunk size matters and how to choose it.
- Common chunking strategies: fixed-size, recursive and structure-aware.
- Why metadata belongs with every chunk, and how contextual chunks retrieve better.
- Why every chunk needs a stable ID, and how to build one.
- What a vector database does and how approximate search works.
- How to choose between pgvector, Chroma and hosted services.
- How to write an ingestion script that stores chunks in pgvector, and query it.

### The ingestion pipeline

**Ingestion** is everything that happens before a user asks a question. It's a pipeline with five steps:

1. **Load.** Read your documents: PDF, HTML, Markdown, plain text. Document Parsing covered turning messy formats into clean text.
1. **Clean.** Remove noise that would confuse search: navigation menus, cookie banners, repeated page headers and footers, page numbers.
1. **Chunk.** Split each document into pieces small enough to embed and retrieve.
1. **Embed.** Turn each chunk into a vector with your embedding model.
1. **Store.** Save each vector together with its text and some *metadata* (facts about the chunk, such as which file it came from).

You run ingestion once up front, and again whenever documents change. If running it twice stores every chunk twice, search results fill up with duplicates. A good ingestion script is **idempotent**: running it again gives the same result as running it once.

### Why chunk size matters

Chunk size is a trade-off, and both directions fail in ways you can see.

- **Too small.** A 50-word chunk is very precise, but it loses its surroundings. A chunk that says "This must be done within 30 days" doesn't say *what* must be done. It may get retrieved, but the model can't use it.
- **Too big.** A 3,000-word chunk keeps all its context, but it blurs several topics into one vector. An embedding is a kind of average of its text's meaning, so a chunk about refunds, shipping *and* warranties matches none of those questions strongly. Big chunks also use up more of the prompt for every result you include.

There's also a hard limit. Every embedding model has a maximum input length, and most local models **silently cut off** anything longer. `BAAI/bge-small-en-v1.5` reads at most 512 tokens (a *token* is a word or a piece of a word, as you saw in the API lessons). Text after that point simply isn't in the vector.

A few hundred tokens per chunk, with a little overlap between neighbors, is a common starting point. A handy rule of thumb is that one token is about four characters of English, so 300 tokens is roughly 1,200 characters. But treat any number as a first guess. The only way to know what works for your documents is to try two or three sizes and measure how often the right passage comes back, which is exactly what the Assignment asks you to do.

### Chunking strategies

There are three common ways to decide where one chunk ends and the next begins.

- **Fixed-size.** Cut every N characters or tokens. It's simple and predictable, but it cuts sentences, lists and tables in half without noticing.
- **Recursive.** Try to split on the biggest natural boundary first (blank lines between paragraphs), and only if a piece is still too long, fall back to smaller ones (sentence ends, then spaces). Chunks end up close to the target size while mostly keeping paragraphs whole.
- **Structure-aware.** Follow the document's own structure: headings in Markdown or HTML, sections in a manual, articles in a contract. A section about "Refunds" becomes its own chunk, and you get the heading for free as metadata.

In practice you combine them: split on structure first, then split any section that is still too long into size-limited pieces. Add a small **overlap**, repeating the last sentence or two of one chunk at the start of the next, so an idea that straddles a boundary appears whole in at least one chunk.

You'll also hear about *semantic chunking*, which starts a new chunk where the meaning shifts between sentences. It costs an embedding per sentence and often isn't better than structure-aware splitting. Libraries such as LangChain's text splitters offer ready-made versions of all of these, but the core logic is short enough to write yourself once, which is the best way to understand it.

### Metadata and context

A vector on its own is useless to a person. Store these with every chunk:

- **Source**: the file name or URL, so you can cite it and link to it.
- **Title and section heading**, so you can show "From: Returns policy, Refunds."
- **Position** (chunk number, page number), so you can fetch the neighbors of a chunk or show where it sits.
- **The original text**, so you can show it, put it in the prompt and re-embed it later without re-parsing.
- **The embedding model name**, because, as you learned last lesson, vectors from different models can't be compared.

Metadata also lets you **filter**: search only this product's manual, only documents from this year, only files this user may see. In a SQL database that's just a `WHERE` clause.

Chunks also retrieve better when they carry a little context. "Revenue grew 3% over the previous quarter" is ambiguous on its own: whose revenue, which quarter? Anthropic found that prepending a short, model-written description of where a chunk came from (which company, which report) before embedding, a technique it calls **contextual retrieval**, markedly reduces failed retrievals. A free version of the same idea is to prepend the document title and heading to each chunk before you embed it, which the script below does. You still store and show the original text; only the embedded text gets the prefix.

### Stable chunk IDs

Every chunk needs an ID, and it's tempting to let the database hand one out: a `bigserial` column numbers rows 1, 2, 3 in the order they're inserted. That works until you ingest again. The delete-then-insert step that keeps ingestion idempotent gives every reinserted chunk a new number, and adding a file or rebuilding the database shuffles them all. Nothing breaks loudly, but several things outside the table remember chunk IDs:

- **Eval labels.** In Evaluating RAG and Catching Regressions you'll write test questions that record which chunks hold each answer. If the IDs change on every ingest, those labels silently point at the wrong chunks, and your retrieval scores turn into nonsense.
- **Citations and traces.** Your traces and feedback log the IDs of the chunks each answer retrieved and cited. Weeks later, you want to open exactly that chunk.
- **Caches.** Anything cached under a chunk ID, such as an embedding or a model-written context, is only valid while the ID still means the same text.

So build the ID from facts about the chunk itself, so the same input always produces the same ID. There are two common recipes:

- **Position-based:** the source file plus where the chunk sits in it, such as `refunds.md:3` (the fourth chunk of `refunds.md`, counting from 0) or `handbook.pdf:p2:0` (the first chunk on page 2). It's readable, you can find the chunk by eye, and it stays the same every time you re-ingest an unchanged file. Its weakness: an edit near the top of a file shifts the index of every later chunk in that file. Numbering chunks per page, as PDFs allow, limits the damage to one page.
- **Content hash:** a short fingerprint of the chunk's text, such as the first 12 characters of its SHA-256 hash (a *hash* turns any text into a fixed-length string, and the same text always gives the same string). It survives edits elsewhere in the file, but any change to the chunk's own text, even a fixed typo, gives it a new ID, and two identical chunks (a disclaimer repeated in every file) get the same ID.

This curriculum uses position-based IDs, built by one small function, `chunk_id`, in `chunking.py` below. Every later lesson and project uses the same function, so an ID in a trace, a citation and an eval label always means the same thing. Keep colons out of file names, since the ID uses them as separators, and remember that renaming a file renames its chunks.

One limit applies to every recipe: no chunk ID survives a change to the chunker itself. A new chunk size or overlap produces different chunks, so of course they get different IDs. Evaluating RAG and Catching Regressions shows how to keep your eval labels working when that happens.

The ingest script below uses the bare file name because all your documents sit in one folder. If they live in subfolders, use the path relative to the docs folder instead (`policies/refunds.md`, not `refunds.md`), so two files with the same name can't share IDs.

### How vector databases search fast

In Vectors and Similarity you searched by comparing the query with every stored vector. That's called **exact** or *brute-force* search, and it's fine for thousands of chunks, even a few hundred thousand. For millions, comparing against everything for every query gets slow.

A **vector database** (or a vector extension to a normal database) adds an **approximate nearest neighbor (ANN) index**: a data structure that finds *almost* the closest vectors while skipping most of the comparisons. It trades a little accuracy for a lot of speed. The share of true top results it finds is called **recall**; a well-tuned index often reaches 95% or more.

Two index types matter in pgvector:

- **HNSW** (Hierarchical Navigable Small World) builds a graph where each vector links to some of its neighbors. A search starts at a few entry points and hops toward the query, like asking for directions. It's fast and accurate, needs no training step, and can be created on an empty table. It uses more memory and builds more slowly. This is the usual default.
- **IVFFlat** groups vectors into clusters (called *lists*) and searches only the clusters nearest the query. It builds faster and uses less memory, but it should be created *after* the table has data, because the clusters are learned from it.

Both have a knob that trades speed for recall: `hnsw.ef_search` (default 40) and `ivfflat.probes`. One trap: with an approximate index, a `WHERE` filter is applied *after* the index scan, so a narrow filter can return fewer rows than your `LIMIT`. The pgvector README's "iterative index scans" fix this.

### Choosing a vector store

Pick the simplest store that fits.

- **pgvector** adds a `vector` column type, distance operators and ANN indexes to PostgreSQL. Your vectors live in the same database as your users and documents, you can combine similarity with ordinary SQL filters and joins, and you back it up like any other Postgres data. It's the default in this curriculum.
- **Chroma** runs inside your Python process with no server at all. It's great for a quick notebook experiment.
- **Hosted vector databases** (Pinecone and others) run the infrastructure for you and scale to billions of vectors, usually at a cost.

Until you have tens of millions of vectors, pgvector is plenty, and one database is easier to run than two.

### Running pgvector with Docker Compose

The official `pgvector/pgvector` Docker image is the regular Postgres image with the extension preinstalled. Here is a `compose.yaml` for local development (the password is fine for your laptop, never for a deployed database):

```yaml
services:
  db:
    image: pgvector/pgvector:pg17       # Postgres 17 with pgvector installed
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mimir
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data # keep data when the container restarts

volumes:
  pgdata:
```

Start it with `docker compose up -d`. Then add the Python packages: `uv add "psycopg[binary]" pgvector sentence-transformers`. **psycopg** is the standard PostgreSQL driver for Python (version 3), and the **pgvector** package teaches it to send and receive vectors.

### An ingestion script

Split the work into two files. First, `chunking.py` does structure-aware splitting on Markdown headings, then cuts long sections into overlapping windows that prefer to end on a paragraph break:

```python
# chunking.py
import re

MAX_CHARS = 1200   # about 300 tokens of English (roughly 4 characters per token)
OVERLAP = 200      # characters repeated between neighboring chunks


def chunk_id(source: str, index: int, page: int | None = None) -> str:
    """Stable ID from where a chunk lives: 'refunds.md:3', or 'handbook.pdf:p2:0' with a page.

    index counts chunks from 0 within the file, or within the page when there is one.
    Re-ingesting an unchanged file gives exactly the same IDs.
    """
    return f"{source}:{index}" if page is None else f"{source}:p{page}:{index}"


def split_by_headings(text: str) -> list[tuple[str, str]]:
    """Split Markdown into (heading, body) sections at #, ## and ### lines."""
    sections, heading, lines = [], "", []
    for line in text.splitlines():
        if re.match(r"#{1,3} ", line):                      # a new section starts
            sections.append((heading, "\n".join(lines).strip()))
            heading, lines = line.lstrip("#").strip(), []
        else:
            lines.append(line)
    sections.append((heading, "\n".join(lines).strip()))
    return [(h, body) for h, body in sections if body]       # drop empty sections


def split_long(body: str) -> list[str]:
    """Cut a section into windows of at most MAX_CHARS, preferring paragraph breaks."""
    chunks, start = [], 0
    while True:
        end = min(start + MAX_CHARS, len(body))
        if end < len(body):                                  # not the last window:
            cut = body.rfind("\n\n", start + MAX_CHARS // 2, end)
            if cut != -1:                                    # end on a blank line if one is
                end = cut                                    # in the second half of the window
        chunks.append(body[start:end].strip())
        if end == len(body):
            return chunks
        start = end - OVERLAP                                # step back to overlap
```

Each window ends at the last blank line in its second half, so most chunks are whole paragraphs. Because a cut never falls in the first half of a window, stepping back `OVERLAP` characters still moves `start` forward, so the loop always ends. One known weakness: a line starting with `# ` inside a fenced code block looks like a heading. You'll fix that in the Assignment. `chunk_id` is the stable ID recipe from the last section, kept here so every script that numbers chunks imports the same function.

Second, `ingest.py` creates the table, embeds every chunk and stores it:

```python
# ingest.py — run with: uv run python ingest.py
import os
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from chunking import chunk_id, split_by_headings, split_long

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mimir")
MODEL_NAME = "BAAI/bge-small-en-v1.5"   # free, local, 384 dimensions

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id        text PRIMARY KEY,        -- stable chunk_id, such as 'refunds.md:3'
    source    text NOT NULL,           -- file name, for citations and filters
    heading   text NOT NULL,           -- section heading
    position  int  NOT NULL,           -- order of the chunk inside its file
    content   text NOT NULL,           -- original text, kept so you can re-embed later
    model     text NOT NULL,           -- which model made the vector
    embedding vector(384) NOT NULL
);
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""


def main(folder: str = "docs") -> None:
    model = SentenceTransformer(MODEL_NAME)
    with psycopg.connect(DB_URL) as conn:          # commits when the block ends without error
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)                      # lets psycopg send NumPy arrays as vectors
        conn.execute(SCHEMA)                       # several statements are fine without parameters
        for path in sorted(Path(folder).glob("*.md")):
            pieces = [(h, c) for h, body in split_by_headings(path.read_text())
                      for c in split_long(body)]
            # Embed "title > heading" plus the text, so each vector carries its context.
            texts = [f"{path.stem} > {h}\n{c}" for h, c in pieces]
            vectors = model.encode(texts, normalize_embeddings=True)
            conn.execute("DELETE FROM chunks WHERE source = %s", (path.name,))  # idempotent
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO chunks (id, source, heading, position, content, model, embedding)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [(chunk_id(path.name, i), path.name, h, i, c, MODEL_NAME, v)
                     for i, ((h, c), v) in enumerate(zip(pieces, vectors))],
                )
            print(f"{path.name}: {len(pieces)} chunks")


if __name__ == "__main__":
    main()
```

Walk through it from the top:

- **`vector(384)`** is pgvector's column type. The number must match the model's dimensions, and a vector of the wrong length is rejected.
- **The HNSW index uses `vector_cosine_ops`**, so it only speeds up queries that sort by cosine distance.
- **`register_vector(conn)`** must run after `CREATE EXTENSION`, because it looks up the new `vector` type in the database.
- **The text you embed and the text you store differ.** The embedded text has the title and heading prepended; `content` keeps the original for display and prompts. Documents get no prefix, because this model only wants its instruction in front of *queries*.
- **Delete, then insert, in one transaction** makes the script idempotent. If anything fails halfway, psycopg rolls back and the old chunks stay. Because `chunk_id` builds each ID from the file name and position, the reinserted chunks get exactly the IDs they had before, and the primary key catches any bug that inserts the same chunk twice.

### Querying your chunks

pgvector adds distance operators to SQL: `<=>` is cosine distance (1 minus cosine similarity), `<->` is Euclidean distance and `<#>` is negative inner product. Sorting by `<=>` and taking the first few rows is a vector search:

```python
# search.py
import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from ingest import DB_URL, MODEL_NAME

QUERY_PROMPT = "Represent this sentence for searching relevant passages: "
model = SentenceTransformer(MODEL_NAME)


def search(conn, question: str, k: int = 5, source: str | None = None):
    q = model.encode(question, prompt=QUERY_PROMPT, normalize_embeddings=True)
    where = "WHERE source = %(source)s" if source else ""   # optional metadata filter
    sql = f"""SELECT source, heading, content, 1 - (embedding <=> %(q)s) AS similarity
              FROM chunks {where} ORDER BY embedding <=> %(q)s LIMIT %(k)s"""
    return conn.execute(sql, {"q": q, "source": source, "k": k}).fetchall()


with psycopg.connect(DB_URL) as conn:
    register_vector(conn)
    for source, heading, content, sim in search(conn, "How long do refunds take?"):
        print(f"{sim:.3f}  {source} > {heading}: {content[:80]!r}")
```

The f-string only ever inserts one of two fixed strings, never user input. The question itself always travels as a parameter (`%(q)s`), which is what keeps this safe from SQL injection, just as in SQL Fundamentals. Note the query uses the same model *and* the query prefix from the last lesson; skip either and results quietly get worse.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Check that the index is used

Put `EXPLAIN` in front of the query in `psql` (`docker compose exec db psql -U postgres mimir`). If you see `Index Scan using chunks_embedding_idx`, the HNSW index is working. On a tiny table Postgres may decide a full scan is cheaper, and that's fine.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Pinecone's chunking strategies guide](https://www.pinecone.io/learn/chunking-strategies/).
   - Read the whole article. It compares fixed-size, recursive, document-structure and semantic chunking, and how to pick a size.
1. Read [Introducing Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval) by Anthropic.
   - Read up to and including the section on contextual embeddings. You will come back for the BM25 and reranking parts in the next lesson.
1. Read the README of [pgvector](https://github.com/pgvector/pgvector) to see how vectors work inside PostgreSQL.
   - Read the "Getting Started," "Querying" and "Indexing" sections. Note the distance operators and the difference between HNSW and IVFFlat indexes. Skim "Filtering" and "Iterative Index Scans."
1. Skim the Psycopg 3 section of the [pgvector-python README](https://github.com/pgvector/pgvector-python), which shows `register_vector` and the insert and query patterns used above.
1. Practice: build the ingestion pipeline from this lesson for a folder of 5 to 10 Markdown or text documents you care about.
   - Start Postgres with the Compose file, run `ingest.py`, and run it a second time to confirm the row count and the IDs don't change (`SELECT count(*) FROM chunks` and `SELECT id FROM chunks ORDER BY id LIMIT 5`).
   - Fix the code-block weakness in `split_by_headings` so lines inside fenced code blocks are never treated as headings, and write a pytest test for it.
   - Add a second table filled with plain fixed-size chunks (no headings, no overlap). Write ten questions where you know which passage holds the answer, run each against both tables, and write down which chunking returned the right passage in the top 3 more often.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the five steps of an ingestion pipeline, and what does it mean for it to be idempotent?](#the-ingestion-pipeline)
- [What goes wrong when chunks are too small, and when they are too big?](#why-chunk-size-matters)
- [How does recursive splitting differ from fixed-size splitting, and why add overlap?](#chunking-strategies)
- [Which metadata should you store with each chunk, and why embed the title and heading with the text but store the text alone?](#metadata-and-context)
- [Why should chunk IDs stay the same when you re-ingest, and how do position-based and content-hash IDs differ?](#stable-chunk-ids)
- [How does an HNSW index differ from IVFFlat, and what does it trade away for speed?](#how-vector-databases-search-fast)
- [Which pgvector operator gives cosine distance, and why must queries use the same model and prefix as ingestion?](#querying-your-chunks)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Chroma getting started guide](https://docs.trychroma.com/docs/overview/getting-started) shows an in-process vector store with metadata filters, handy for quick notebook experiments.
